#!/usr/bin/env python3
"""Run optional official external evaluation tools for repaired molecules."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import signal
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from rdkit import Chem

try:
    from posebusters import PoseBusters
except Exception:  # pragma: no cover - exercised only in optional tool env
    PoseBusters = None  # type: ignore[assignment]


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    input_path = Path(path)
    if not input_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError(f"{input_path}:{line_number} must contain a JSON object")
            rows.append(row)
    return rows


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return output_path


def append_jsonl(path: str | Path, row: dict[str, Any]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def tool_path(name: str) -> str | None:
    resolved = shutil.which(name)
    return str(resolved) if resolved else None


def command_summary(result: subprocess.CompletedProcess[str], command: list[str]) -> dict[str, Any]:
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout_head": result.stdout[:1000],
        "stderr_head": result.stderr[:1000],
    }


def run_command(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout)


def sha256_file(path: str | Path) -> str | None:
    input_path = Path(path)
    if not input_path.exists() or not input_path.is_file():
        return None
    digest = hashlib.sha256()
    with input_path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class Timeout:
    def __init__(self, seconds: int) -> None:
        self.seconds = seconds
        self.previous: Any = None

    def __enter__(self) -> None:
        self.previous = signal.signal(signal.SIGALRM, self._handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, self.previous)

    def _handle_timeout(self, signum: int, frame: Any) -> None:
        raise TimeoutError(f"timed out after {self.seconds}s")


def ligand_centroid(path: str | Path | None) -> tuple[float, float, float] | None:
    if not path:
        return None
    supplier = Chem.SDMolSupplier(str(path), removeHs=False)
    mol = next((mol for mol in supplier if mol is not None), None)
    if mol is None or mol.GetNumConformers() == 0:
        return None
    conf = mol.GetConformer()
    coords: list[tuple[float, float, float]] = []
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 1:
            continue
        pos = conf.GetAtomPosition(atom.GetIdx())
        coords.append((float(pos.x), float(pos.y), float(pos.z)))
    if not coords:
        return None
    count = float(len(coords))
    return (
        sum(coord[0] for coord in coords) / count,
        sum(coord[1] for coord in coords) / count,
        sum(coord[2] for coord in coords) / count,
    )


def box_size_from_ligand(path: str | Path | None, padding: float = 8.0, minimum: float = 12.0) -> tuple[float, float, float]:
    if not path:
        return (20.0, 20.0, 20.0)
    supplier = Chem.SDMolSupplier(str(path), removeHs=False)
    mol = next((mol for mol in supplier if mol is not None), None)
    if mol is None or mol.GetNumConformers() == 0:
        return (20.0, 20.0, 20.0)
    conf = mol.GetConformer()
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 1:
            continue
        pos = conf.GetAtomPosition(atom.GetIdx())
        xs.append(float(pos.x))
        ys.append(float(pos.y))
        zs.append(float(pos.z))
    if not xs:
        return (20.0, 20.0, 20.0)
    return (
        max(minimum, max(xs) - min(xs) + padding),
        max(minimum, max(ys) - min(ys) + padding),
        max(minimum, max(zs) - min(zs) + padding),
    )


def pdb_serial(line: str) -> int | None:
    try:
        return int(line[6:11])
    except ValueError:
        return None


def format_pdb_serial(line: str, serial: int) -> str:
    padded = line.ljust(80)
    return f"{padded[:6]}{serial:5d}{padded[11:80]}".rstrip()


def renumber_ligand_pdb_lines(pdb_block: str, start_serial: int) -> list[str]:
    serial_map: dict[int, int] = {}
    atom_lines: list[str] = []
    conect_lines: list[str] = []
    next_serial = start_serial
    for line in pdb_block.splitlines():
        if line.startswith(("ATOM", "HETATM")):
            old_serial = pdb_serial(line)
            if old_serial is None:
                continue
            serial_map[old_serial] = next_serial
            atom_lines.append(format_pdb_serial(line, next_serial))
            next_serial += 1
        elif line.startswith("CONECT"):
            conect_lines.append(line)
    renumbered = list(atom_lines)
    for line in conect_lines:
        fields = line.split()
        if len(fields) < 2:
            continue
        try:
            mapped = [serial_map[int(field)] for field in fields[1:] if int(field) in serial_map]
        except ValueError:
            continue
        if len(mapped) < 2:
            continue
        renumbered.append("CONECT" + "".join(f"{serial:5d}" for serial in mapped))
    return renumbered


def load_ligand_for_pdb_block(path: str | Path) -> Any | None:
    input_path = Path(path)
    if input_path.suffix.lower() == ".pdb":
        return Chem.MolFromPDBFile(str(input_path), removeHs=False, sanitize=False)
    return next((mol for mol in Chem.SDMolSupplier(str(input_path), removeHs=False) if mol is not None), None)


def merge_complex_pdb(protein_path: str | Path | None, ligand_path: str | Path | None, output_path: Path) -> bool:
    if not protein_path or not ligand_path:
        return False
    protein = Path(protein_path)
    ligand = Path(ligand_path)
    if not protein.exists() or not ligand.exists():
        return False
    mol = load_ligand_for_pdb_block(ligand)
    if mol is None:
        return False
    receptor_lines: list[str] = []
    max_serial = 0
    for line in protein.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith(("ATOM", "HETATM", "TER")):
            receptor_lines.append(line)
            serial = pdb_serial(line) if line.startswith(("ATOM", "HETATM")) else None
            if serial is not None:
                max_serial = max(max_serial, serial)
    ligand_lines = renumber_ligand_pdb_lines(Chem.MolToPDBBlock(mol), max_serial + 1)
    if not receptor_lines or not ligand_lines:
        return False
    with output_path.open("w", encoding="utf-8") as handle:
        for line in receptor_lines:
            handle.write(line.rstrip() + "\n")
        if not receptor_lines[-1].startswith("TER"):
            handle.write("TER\n")
        for line in ligand_lines:
            handle.write(line.rstrip() + "\n")
        handle.write("END\n")
    return True


def run_posebusters(row: dict[str, Any], buster: Any | None, timeout: int, config: str, work_dir: Path | None = None) -> dict[str, Any]:
    if work_dir is not None:
        input_path = work_dir / "posebusters_input.jsonl"
        output_path = work_dir / "posebusters_output.jsonl"
        append_jsonl(input_path, row)
        command = [
            "python",
            "scripts/eval/eval_posebusters_one.py",
            "--repaired-candidates",
            str(input_path),
            "--index",
            "0",
            "--output",
            str(output_path),
            "--timeout",
            str(timeout),
            "--config",
            config,
        ]
        try:
            result = run_command(command, timeout=timeout + 5)
        except subprocess.TimeoutExpired as exc:
            return {
                "posebusters_available": True,
                "posebusters_error": f"subprocess_timeout_after_{timeout + 5}s",
                "posebusters_command": {"command": command, "timeout": timeout + 5, "exception": repr(exc)},
            }
        metadata = {"posebusters_command": command_summary(result, command)}
        rows = read_jsonl(output_path)
        if rows:
            rows[0].update(metadata)
            return rows[0]
        return {"posebusters_available": True, "posebusters_error": "subprocess_output_missing", **metadata}
    if buster is None:
        return {"posebusters_available": False, "posebusters_error": "posebusters_import_failed", "posebusters_config": config}
    repaired = row.get("repaired_ligand_path")
    reference = row.get("reference_ligand_path")
    protein = row.get("protein_path")
    try:
        with Timeout(timeout):
            table = buster.bust(repaired, mol_true=reference, mol_cond=protein, full_report=True)
        record = table.iloc[0].to_dict() if len(table) else {}
        bool_values = [bool(value) for value in record.values() if isinstance(value, (bool,))]
        return {
            "posebusters_available": True,
            "posebusters_config": config,
            "posebusters_full_pass": all(bool_values) if bool_values else None,
            "posebusters_num_checks": len(bool_values),
            "posebusters_num_passed": sum(bool_values),
            "posebusters_columns": list(record.keys()),
        }
    except Exception as exc:
        return {"posebusters_available": True, "posebusters_config": config, "posebusters_error": str(exc)}


PLIP_INTERACTION_TAGS = {
    "hydrophobic_interaction",
    "hydrogen_bond",
    "water_bridge",
    "salt_bridge",
    "pi_stack",
    "pi_cation_interaction",
    "halogen_bond",
    "metal_complex",
}


def xml_child_text(element: ET.Element, child_name: str) -> str | None:
    for child in element:
        if child.tag.split("}")[-1] == child_name and child.text:
            return child.text.strip()
    return None


def plip_interaction_key(element: ET.Element, interaction_type: str) -> str:
    chain = xml_child_text(element, "reschain") or ""
    resnr = xml_child_text(element, "resnr") or ""
    restype = xml_child_text(element, "restype") or ""
    return "|".join([interaction_type, chain, resnr, restype])


def parse_plip_xml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"plip_error": "xml_not_written"}
    root = ET.parse(path).getroot()
    counts: dict[str, int] = {}
    fingerprint: set[str] = set()
    for element in root.iter():
        tag = element.tag.split("}")[-1]
        if tag in PLIP_INTERACTION_TAGS:
            counts[tag] = counts.get(tag, 0) + 1
            fingerprint.add(plip_interaction_key(element, tag))
    return {
        "plip_interaction_count": sum(counts.values()),
        "plip_interaction_counts": counts,
        "plip_interaction_fingerprint": sorted(fingerprint),
        "plip_interaction_fingerprint_count": len(fingerprint),
    }


def prefix_plip_fields(parsed: dict[str, Any], label: str) -> dict[str, Any]:
    prefixed: dict[str, Any] = {}
    for key, value in parsed.items():
        if key.startswith("plip_"):
            prefixed[f"plip_{label}_{key.removeprefix('plip_')}"] = value
        else:
            prefixed[f"plip_{label}_{key}"] = value
    return prefixed


def interaction_similarity(reference: set[str], candidate: set[str]) -> dict[str, Any]:
    if not reference and not candidate:
        return {"similarity": None, "recovery": None, "recovered_count": 0}
    union = reference | candidate
    intersection = reference & candidate
    return {
        "similarity": len(intersection) / len(union) if union else None,
        "recovery": len(intersection) / len(reference) if reference else None,
        "recovered_count": len(intersection),
    }


def run_plip_for_ligand(
    row: dict[str, Any], ligand_path: str | Path | None, label: str, work_dir: Path, plip_path: str
) -> dict[str, Any]:
    if not ligand_path:
        return {f"plip_{label}_available": True, f"plip_{label}_error": "missing_ligand_path"}
    complex_path = work_dir / f"{row.get('repair_id', 'complex')}__{label}.pdb"
    if not merge_complex_pdb(row.get("protein_path"), ligand_path, complex_path):
        return {f"plip_{label}_available": True, f"plip_{label}_cli": plip_path, f"plip_{label}_error": "complex_pdb_build_failed"}
    out_dir = work_dir / f"plip_{label}"
    out_dir.mkdir(parents=True, exist_ok=True)
    command = ["plip", "-f", str(complex_path), "-o", str(out_dir), "-x", "-q"]
    result = run_command(command, timeout=120)
    metadata = {f"plip_{label}_cli": plip_path, f"plip_{label}_command": command_summary(result, command)}
    if result.returncode != 0:
        return {f"plip_{label}_available": True, f"plip_{label}_error": result.stderr.strip() or result.stdout.strip(), **metadata}
    xml_files = sorted(out_dir.glob("*.xml"))
    parsed = parse_plip_xml(xml_files[0]) if xml_files else {"plip_error": "xml_not_found"}
    prefixed = prefix_plip_fields(parsed, label)
    prefixed[f"plip_{label}_available"] = True
    prefixed.update(metadata)
    return prefixed


def run_plip(row: dict[str, Any], work_dir: Path) -> dict[str, Any]:
    plip_path = tool_path("plip")
    if plip_path is None:
        return {"plip_available": False, "plip_error": "plip_cli_missing"}
    repaired_result = run_plip_for_ligand(row, row.get("repaired_ligand_path"), "repaired", work_dir, plip_path)
    failed_result = run_plip_for_ligand(row, row.get("source_failed_ligand_path"), "failed", work_dir, plip_path)
    reference_result = run_plip_for_ligand(row, row.get("reference_ligand_path"), "reference", work_dir, plip_path)
    result: dict[str, Any] = {**repaired_result, **failed_result, **reference_result}

    result["plip_available"] = result.get("plip_repaired_available")
    if result.get("plip_repaired_error"):
        result["plip_error"] = result.get("plip_repaired_error")
    if result.get("plip_repaired_cli"):
        result["plip_cli"] = result.get("plip_repaired_cli")
    if result.get("plip_repaired_command"):
        result["plip_command"] = result.get("plip_repaired_command")
    for suffix in ["interaction_count", "interaction_counts", "interaction_fingerprint", "interaction_fingerprint_count"]:
        key = f"plip_repaired_{suffix}"
        if key in result:
            result[f"plip_{suffix}"] = result[key]

    reference_fingerprint = set(result.get("plip_reference_interaction_fingerprint") or [])
    repaired_fingerprint = set(result.get("plip_repaired_interaction_fingerprint") or [])
    failed_fingerprint = set(result.get("plip_failed_interaction_fingerprint") or [])
    repaired_metrics = interaction_similarity(reference_fingerprint, repaired_fingerprint)
    failed_metrics = interaction_similarity(reference_fingerprint, failed_fingerprint)
    result.update(
        {
            "plip_interaction_similarity": repaired_metrics["similarity"],
            "plip_interaction_recovery": repaired_metrics["recovery"],
            "plip_recovered_reference_interaction_count": repaired_metrics["recovered_count"],
            "plip_failed_interaction_similarity": failed_metrics["similarity"],
            "plip_failed_interaction_recovery": failed_metrics["recovery"],
            "plip_failed_recovered_reference_interaction_count": failed_metrics["recovered_count"],
            "plip_interaction_similarity_gain": None
            if repaired_metrics["similarity"] is None or failed_metrics["similarity"] is None
            else repaired_metrics["similarity"] - failed_metrics["similarity"],
            "plip_interaction_recovery_gain": None
            if repaired_metrics["recovery"] is None or failed_metrics["recovery"] is None
            else repaired_metrics["recovery"] - failed_metrics["recovery"],
            "plip_lost_reference_interactions": sorted(reference_fingerprint - repaired_fingerprint),
            "plip_new_repaired_interactions": sorted(repaired_fingerprint - reference_fingerprint),
        }
    )
    return result


def write_explicit_h_ligand(input_path: str | Path, output_path: Path) -> bool:
    supplier = Chem.SDMolSupplier(str(input_path), removeHs=False)
    mol = next((mol for mol in supplier if mol is not None), None)
    if mol is None:
        return False
    mol_h = Chem.AddHs(mol, addCoords=True)
    writer = Chem.SDWriter(str(output_path))
    writer.write(mol_h)
    writer.close()
    return True


def parse_vina_score(text: str) -> float | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("Estimated Free Energy of Binding"):
            parts = stripped.replace(":", " ").split()
            for token in parts:
                try:
                    return float(token)
                except ValueError:
                    continue
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].lower() == "affinity":
            try:
                return float(parts[-1])
            except ValueError:
                return None
    return None


def run_vina(row: dict[str, Any], work_dir: Path) -> dict[str, Any]:
    required = ["mk_prepare_ligand.py", "mk_prepare_receptor.py", "vina"]
    tool_paths = {name: tool_path(name) for name in required}
    missing = [name for name, path in tool_paths.items() if path is None]
    if missing:
        return {"vina_available": False, "vina_error": f"missing_cli:{','.join(missing)}", "vina_tool_paths": tool_paths}
    repaired = row.get("repaired_ligand_path")
    protein = row.get("protein_path")
    pocket_box = row.get("pocket_box") if isinstance(row.get("pocket_box"), dict) else None
    generated_fallback_used = False
    if pocket_box:
        center_values = pocket_box.get("center_angstrom")
        size_values = pocket_box.get("size_angstrom")
        center = tuple(float(value) for value in center_values) if isinstance(center_values, list) and len(center_values) == 3 else None
        size = tuple(float(value) for value in size_values) if isinstance(size_values, list) and len(size_values) == 3 else None
        box_source = str(pocket_box.get("box_source") or "pocket_box")
    else:
        center = ligand_centroid(row.get("reference_ligand_path"))
        box_source = "reference_ligand_file_centroid"
        if center is None:
            center = ligand_centroid(repaired)
            generated_fallback_used = center is not None
            box_source = "generated_ligand_centroid_fallback" if generated_fallback_used else "missing_box_center"
        size = box_size_from_ligand(row.get("reference_ligand_path"))
    if not repaired or not protein or center is None:
        return {"vina_available": True, "vina_error": "missing_input_or_box_center", "vina_tool_paths": tool_paths}
    if size is None:
        return {"vina_available": True, "vina_error": "missing_box_size", "vina_tool_paths": tool_paths}
    ligand_sdf = work_dir / "ligand_explicit_h.sdf"
    if not write_explicit_h_ligand(repaired, ligand_sdf):
        return {"vina_available": True, "vina_error": "ligand_explicit_h_failed", "vina_tool_paths": tool_paths}
    ligand_pdbqt = work_dir / "ligand.pdbqt"
    receptor_base = work_dir / "receptor"
    receptor_pdbqt = work_dir / "receptor.pdbqt"
    ligand_command = ["mk_prepare_ligand.py", "-i", str(ligand_sdf), "-o", str(ligand_pdbqt)]
    ligand_result = run_command(ligand_command, timeout=120)
    ligand_retry_command: list[str] | None = None
    ligand_retry_result: subprocess.CompletedProcess[str] | None = None
    if ligand_result.returncode != 0:
        ligand_retry_command = [
            "mk_prepare_ligand.py",
            "-i",
            str(ligand_sdf),
            "-o",
            str(ligand_pdbqt),
            "--charge_model",
            "zero",
        ]
        ligand_retry_result = run_command(ligand_retry_command, timeout=120)
        if ligand_retry_result.returncode == 0:
            ligand_command = ligand_retry_command
            ligand_result = ligand_retry_result
    if ligand_result.returncode != 0:
        error_result = {
            "vina_available": True,
            "vina_error": "ligand_prepare_failed",
            "vina_tool_paths": tool_paths,
            "vina_ligand_command": command_summary(ligand_result, ligand_command),
        }
        if ligand_retry_command is not None and ligand_retry_result is not None:
            error_result["vina_ligand_retry_command"] = command_summary(ligand_retry_result, ligand_retry_command)
        return error_result
    receptor_command = ["mk_prepare_receptor.py", "--read_pdb", str(protein), "-o", str(receptor_base), "-p", str(receptor_pdbqt), "-a"]
    receptor_result = run_command(receptor_command, timeout=180)
    receptor_retry_command: list[str] | None = None
    receptor_retry_result: subprocess.CompletedProcess[str] | None = None
    if receptor_result.returncode != 0:
        receptor_retry_command = [
            "mk_prepare_receptor.py",
            "--read_pdb",
            str(protein),
            "-o",
            str(receptor_base),
            "-p",
            str(receptor_pdbqt),
            "-a",
            "--default_altloc",
            "A",
        ]
        receptor_retry_result = run_command(receptor_retry_command, timeout=180)
        if receptor_retry_result.returncode == 0:
            receptor_command = receptor_retry_command
            receptor_result = receptor_retry_result
    if receptor_result.returncode != 0:
        error_result = {
            "vina_available": True,
            "vina_error": "receptor_prepare_failed",
            "vina_tool_paths": tool_paths,
            "vina_ligand_command": command_summary(ligand_result, ligand_command),
            "vina_receptor_command": command_summary(receptor_result, receptor_command),
        }
        if receptor_retry_command is not None and receptor_retry_result is not None:
            error_result["vina_receptor_retry_command"] = command_summary(receptor_retry_result, receptor_retry_command)
        return error_result
    vina_command = [
        "vina",
        "--receptor",
        str(receptor_pdbqt),
        "--ligand",
        str(ligand_pdbqt),
        "--score_only",
        "--center_x",
        f"{center[0]:.4f}",
        "--center_y",
        f"{center[1]:.4f}",
        "--center_z",
        f"{center[2]:.4f}",
        "--size_x",
        f"{size[0]:.4f}",
        "--size_y",
        f"{size[1]:.4f}",
        "--size_z",
        f"{size[2]:.4f}",
        "--cpu",
        "1",
    ]
    vina_result = run_command(vina_command, timeout=180)
    command_metadata = {
        "vina_tool_paths": tool_paths,
        "vina_ligand_command": command_summary(ligand_result, ligand_command),
        "vina_receptor_command": command_summary(receptor_result, receptor_command),
        "vina_score_command": command_summary(vina_result, vina_command),
        "vina_box_definition_source": box_source,
        "vina_generated_ligand_centroid_fallback_used": generated_fallback_used,
        "vina_ligand_pdbqt_path": str(ligand_pdbqt),
        "vina_ligand_pdbqt_sha256": sha256_file(ligand_pdbqt),
        "vina_receptor_pdbqt_path": str(receptor_pdbqt),
        "vina_receptor_pdbqt_sha256": sha256_file(receptor_pdbqt),
        "vina_score_comparability": "non_comparable" if ligand_retry_command is not None else "standard_score_only",
    }
    if ligand_retry_command is not None and ligand_retry_result is not None:
        command_metadata["vina_ligand_retry_command"] = command_summary(ligand_retry_result, ligand_retry_command)
    if receptor_retry_command is not None and receptor_retry_result is not None:
        command_metadata["vina_receptor_retry_command"] = command_summary(receptor_retry_result, receptor_retry_command)
    if vina_result.returncode != 0:
        return {"vina_available": True, "vina_error": "vina_score_failed", **command_metadata}
    score = parse_vina_score(vina_result.stdout)
    return {
        "vina_available": True,
        "vina_score_only_energy": score,
        "vina_box_center": center,
        "vina_box_size": size,
        "vina_box_definition_source": box_source,
        "vina_generated_ligand_centroid_fallback_used": generated_fallback_used,
        "vina_score_parse_status": "parsed" if score is not None else "not_found",
        **command_metadata,
    }


def evaluate_row(
    row: dict[str, Any],
    buster: Any | None,
    keep_work: Path | None,
    run_posebusters_flag: bool,
    run_plip_flag: bool,
    run_vina_flag: bool,
    posebusters_timeout: int,
    posebusters_config: str,
) -> dict[str, Any]:
    base = {
        "repair_id": row.get("repair_id"),
        "candidate_id": row.get("candidate_id"),
        "complex_id": row.get("complex_id"),
        "baseline": row.get("baseline"),
        "failure_type": row.get("failure_type"),
        "seed": row.get("seed"),
        "record_level_output_budget": row.get("record_level_output_budget"),
        "internal_candidate_budget": row.get("internal_candidate_budget"),
        "internal_budget_type": row.get("internal_budget_type"),
        "candidate_pool_size": row.get("candidate_pool_size"),
        "editable_offset_pool_size": row.get("editable_offset_pool_size"),
        "protein_path": row.get("protein_path"),
        "reference_ligand_path": row.get("reference_ligand_path"),
        "source_failed_ligand_path": row.get("source_failed_ligand_path"),
        "repaired_ligand_path": row.get("repaired_ligand_path"),
        "source": "official_external_eval_tools",
    }

    def run_selected(work_dir: Path) -> dict[str, Any]:
        result = dict(base)
        if run_posebusters_flag:
            result.update(run_posebusters(row, buster, posebusters_timeout, posebusters_config, work_dir))
        if run_plip_flag:
            result.update(run_plip(row, work_dir))
        if run_vina_flag:
            result.update(run_vina(row, work_dir))
        return result

    if keep_work is not None:
        work_dir = keep_work / str(row.get("repair_id", "row"))
        work_dir.mkdir(parents=True, exist_ok=True)
        return run_selected(work_dir)
    with tempfile.TemporaryDirectory(prefix="official_eval_") as tmp_name:
        return run_selected(Path(tmp_name))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repaired-candidates", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--keep-work-dir", default=None)
    parser.add_argument("--tools", default="posebusters,plip,vina")
    parser.add_argument("--posebusters-timeout", type=int, default=60)
    parser.add_argument("--posebusters-config", default="redock")
    args = parser.parse_args()

    selected_tools = {tool.strip() for tool in args.tools.split(",") if tool.strip()}
    run_posebusters_flag = "posebusters" in selected_tools
    run_plip_flag = "plip" in selected_tools
    run_vina_flag = "vina" in selected_tools

    rows = read_jsonl(args.repaired_candidates)
    if args.limit is not None:
        rows = rows[: args.limit]
    buster = PoseBusters(config=args.posebusters_config, max_workers=0) if PoseBusters is not None and run_posebusters_flag else None
    keep_work = Path(args.keep_work_dir) if args.keep_work_dir else None
    output_path = Path(args.output)
    if output_path.exists():
        output_path.unlink()
    results = []
    for index, row in enumerate(rows):
        result = evaluate_row(
            row,
            buster,
            keep_work,
            run_posebusters_flag,
            run_plip_flag,
            run_vina_flag,
            args.posebusters_timeout,
            args.posebusters_config,
        )
        result["input_index"] = index
        append_jsonl(output_path, result)
        results.append(result)
    print(f"Read {len(rows)} repaired candidate records")
    print(f"Selected tools: {','.join(sorted(selected_tools))}")
    print(f"Wrote official external eval records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
