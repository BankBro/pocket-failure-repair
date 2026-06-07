#!/usr/bin/env python3
"""Generate small Vina-docked pose candidates for smoke diagnostics."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from rdkit import Chem

from pfr.chemistry.rdkit_scaffold import load_first_molecule
from pfr.utils.io import read_jsonl, write_jsonl


def run_command(command: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout)


def tool_path(name: str) -> str | None:
    resolved = shutil.which(name)
    return str(resolved) if resolved else None


def ligand_centroid(path: str | Path) -> tuple[float, float, float] | None:
    mol = load_first_molecule(path)
    if mol is None or mol.GetNumConformers() == 0:
        return None
    conf = mol.GetConformer()
    coords = []
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 1:
            continue
        pos = conf.GetAtomPosition(atom.GetIdx())
        coords.append((float(pos.x), float(pos.y), float(pos.z)))
    if not coords:
        return None
    n = float(len(coords))
    return (sum(x for x, _, _ in coords) / n, sum(y for _, y, _ in coords) / n, sum(z for _, _, z in coords) / n)


def box_size(path: str | Path, padding: float = 8.0, minimum: float = 12.0) -> tuple[float, float, float]:
    mol = load_first_molecule(path)
    if mol is None or mol.GetNumConformers() == 0:
        return (20.0, 20.0, 20.0)
    conf = mol.GetConformer()
    xs, ys, zs = [], [], []
    for atom in mol.GetAtoms():
        if atom.GetAtomicNum() == 1:
            continue
        pos = conf.GetAtomPosition(atom.GetIdx())
        xs.append(float(pos.x)); ys.append(float(pos.y)); zs.append(float(pos.z))
    if not xs:
        return (20.0, 20.0, 20.0)
    return (max(minimum, max(xs)-min(xs)+padding), max(minimum, max(ys)-min(ys)+padding), max(minimum, max(zs)-min(zs)+padding))


def write_explicit_h_ligand(input_path: str | Path, output_path: Path) -> bool:
    mol = next((mol for mol in Chem.SDMolSupplier(str(input_path), removeHs=False) if mol is not None), None)
    if mol is None:
        return False
    mol_h = Chem.AddHs(mol, addCoords=True)
    writer = Chem.SDWriter(str(output_path))
    writer.write(mol_h)
    writer.close()
    return True


def write_pose_with_template_topology(template_path: str | Path, coordinate_path: str | Path, output_path: Path) -> str | None:
    template = next((mol for mol in Chem.SDMolSupplier(str(template_path), removeHs=False) if mol is not None), None)
    coordinate_mol = next(
        (mol for mol in Chem.SDMolSupplier(str(coordinate_path), removeHs=False, sanitize=False) if mol is not None),
        None,
    )
    if template is None:
        return "template_read_failed"
    if coordinate_mol is None or coordinate_mol.GetNumConformers() == 0:
        return "coordinate_read_failed"
    template_atoms = list(range(template.GetNumAtoms()))
    coordinate_atoms = list(range(coordinate_mol.GetNumAtoms()))
    if len(template_atoms) != len(coordinate_atoms):
        coordinate_heavy_atoms = [atom.GetIdx() for atom in coordinate_mol.GetAtoms() if atom.GetAtomicNum() > 1]
        if len(template_atoms) == len(coordinate_heavy_atoms):
            coordinate_atoms = coordinate_heavy_atoms
        else:
            template_heavy_atoms = [atom.GetIdx() for atom in template.GetAtoms() if atom.GetAtomicNum() > 1]
            if len(template_heavy_atoms) != len(coordinate_heavy_atoms):
                return f"atom_count_mismatch:{template.GetNumAtoms()}:{coordinate_mol.GetNumAtoms()}"
            template_atoms = template_heavy_atoms
            coordinate_atoms = coordinate_heavy_atoms
    coordinate_conf = coordinate_mol.GetConformer()
    repaired_pose = Chem.Mol(template)
    repaired_pose.RemoveAllConformers()
    conformer = Chem.Conformer(repaired_pose.GetNumAtoms())
    if template.GetNumConformers() > 0:
        template_conf = template.GetConformer()
        for atom_index in range(repaired_pose.GetNumAtoms()):
            conformer.SetAtomPosition(atom_index, template_conf.GetAtomPosition(atom_index))
    for template_atom, coordinate_atom in zip(template_atoms, coordinate_atoms):
        conformer.SetAtomPosition(template_atom, coordinate_conf.GetAtomPosition(coordinate_atom))
    repaired_pose.AddConformer(conformer, assignId=True)
    writer = Chem.SDWriter(str(output_path))
    writer.write(repaired_pose)
    writer.close()
    return None


def pdbqt_heavy_atom_coordinates(path: str | Path) -> list[tuple[float, float, float]]:
    allowed_atom_types = {
        "A",
        "C",
        "N",
        "NA",
        "OA",
        "S",
        "SA",
        "P",
        "F",
        "CL",
        "BR",
        "I",
        "ZN",
        "FE",
        "MG",
        "MN",
        "CA",
    }
    coords: list[tuple[float, float, float]] = []
    with Path(path).open(errors="replace") as handle:
        for line in handle:
            if not line.startswith(("ATOM", "HETATM")):
                continue
            atom_type = line.split()[-1].upper() if line.split() else ""
            if atom_type.startswith("H") or atom_type not in allowed_atom_types:
                continue
            try:
                coords.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
            except ValueError:
                parts = line.split()
                if len(parts) >= 8:
                    coords.append((float(parts[5]), float(parts[6]), float(parts[7])))
    return coords


def write_pose_with_template_topology_from_pdbqt(template_path: str | Path, pdbqt_path: str | Path, output_path: Path) -> str | None:
    template = next((mol for mol in Chem.SDMolSupplier(str(template_path), removeHs=False) if mol is not None), None)
    if template is None:
        return "template_read_failed"
    template_atoms = [atom.GetIdx() for atom in template.GetAtoms() if atom.GetAtomicNum() > 1]
    coords = pdbqt_heavy_atom_coordinates(pdbqt_path)
    if len(coords) != len(template_atoms):
        return f"pdbqt_heavy_atom_count_mismatch:{len(template_atoms)}:{len(coords)}"
    repaired_pose = Chem.Mol(template)
    repaired_pose.RemoveAllConformers()
    conformer = Chem.Conformer(repaired_pose.GetNumAtoms())
    if template.GetNumConformers() > 0:
        template_conf = template.GetConformer()
        for atom_index in range(repaired_pose.GetNumAtoms()):
            conformer.SetAtomPosition(atom_index, template_conf.GetAtomPosition(atom_index))
    for atom_index, coord in zip(template_atoms, coords):
        conformer.SetAtomPosition(atom_index, coord)
    repaired_pose.AddConformer(conformer, assignId=True)
    writer = Chem.SDWriter(str(output_path))
    writer.write(repaired_pose)
    writer.close()
    return None


def run_docking(row: dict[str, Any], output_dir: Path, exhaustiveness: int, seed: int) -> dict[str, Any]:
    required = ["mk_prepare_ligand.py", "mk_prepare_receptor.py", "vina", "obabel"]
    tools = {name: tool_path(name) for name in required}
    missing = [name for name, path in tools.items() if path is None]
    result = {
        "candidate_id": row.get("candidate_id"),
        "complex_id": row.get("complex_id"),
        "source_candidate_id": row.get("candidate_id"),
        "source": "vina_docked_pose_smoke",
        "protein_path": row.get("protein_path"),
        "ligand_path": row.get("ligand_path"),
        "scaffold_atoms": row.get("scaffold_atoms", []),
        "editable_atoms": row.get("editable_atoms", []),
        "anchor_atoms": row.get("anchor_atoms", []),
        "sample_quality": row.get("sample_quality", {}),
        "tool_paths": tools,
    }
    if missing:
        result["error"] = f"missing_cli:{','.join(missing)}"
        return result
    ligand = row.get("failed_ligand_path") or row.get("ligand_path")
    reference = row.get("ligand_path")
    protein = row.get("protein_path")
    if not ligand or not reference or not protein:
        result["error"] = "missing_input"
        return result
    center = ligand_centroid(reference)
    if center is None:
        result["error"] = "missing_box_center"
        return result
    size = box_size(reference)
    with tempfile.TemporaryDirectory(prefix="vina_docked_pose_") as tmp_name:
        tmp = Path(tmp_name)
        ligand_sdf = tmp / "ligand_h.sdf"
        if not write_explicit_h_ligand(ligand, ligand_sdf):
            result["error"] = "ligand_h_failed"
            return result
        ligand_pdbqt = tmp / "ligand.pdbqt"
        receptor_base = tmp / "receptor"
        receptor_pdbqt = tmp / "receptor.pdbqt"
        docked_pdbqt = tmp / "docked.pdbqt"
        docked_sdf = output_dir / f"{row.get('complex_id')}_vina_docked_pose_0.sdf"
        ligand_cmd = ["mk_prepare_ligand.py", "-i", str(ligand_sdf), "-o", str(ligand_pdbqt)]
        ligand_result = run_command(ligand_cmd, timeout=120)
        if ligand_result.returncode != 0:
            ligand_cmd = ["mk_prepare_ligand.py", "-i", str(ligand_sdf), "-o", str(ligand_pdbqt), "--charge_model", "zero"]
            ligand_result = run_command(ligand_cmd, timeout=120)
        if ligand_result.returncode != 0:
            result["error"] = "ligand_prepare_failed"
            result["stderr_head"] = ligand_result.stderr[:1000]
            return result
        receptor_cmd = ["mk_prepare_receptor.py", "--read_pdb", str(protein), "-o", str(receptor_base), "-p", str(receptor_pdbqt), "-a"]
        receptor_result = run_command(receptor_cmd, timeout=180)
        if receptor_result.returncode != 0:
            receptor_cmd = ["mk_prepare_receptor.py", "--read_pdb", str(protein), "-o", str(receptor_base), "-p", str(receptor_pdbqt), "-a", "--default_altloc", "A"]
            receptor_result = run_command(receptor_cmd, timeout=180)
        if receptor_result.returncode != 0:
            result["error"] = "receptor_prepare_failed"
            result["stderr_head"] = receptor_result.stderr[:1000]
            return result
        vina_cmd = [
            "vina", "--receptor", str(receptor_pdbqt), "--ligand", str(ligand_pdbqt), "--out", str(docked_pdbqt),
            "--center_x", f"{center[0]:.4f}", "--center_y", f"{center[1]:.4f}", "--center_z", f"{center[2]:.4f}",
            "--size_x", f"{size[0]:.4f}", "--size_y", f"{size[1]:.4f}", "--size_z", f"{size[2]:.4f}",
            "--exhaustiveness", str(exhaustiveness), "--num_modes", "1", "--seed", str(seed), "--cpu", "1",
        ]
        vina_result = run_command(vina_cmd, timeout=240)
        if vina_result.returncode != 0 or not docked_pdbqt.exists():
            result["error"] = "vina_dock_failed"
            result["stderr_head"] = vina_result.stderr[:1000]
            result["stdout_head"] = vina_result.stdout[:1000]
            return result
        output_dir.mkdir(parents=True, exist_ok=True)
        topology_error = write_pose_with_template_topology_from_pdbqt(ligand, docked_pdbqt, docked_sdf)
        if topology_error:
            raw_docked_sdf = tmp / "docked_raw.sdf"
            obabel_cmd = ["obabel", "-ipdbqt", str(docked_pdbqt), "-osdf", "-O", str(raw_docked_sdf)]
            obabel_result = run_command(obabel_cmd, timeout=120)
            if obabel_result.returncode != 0 or not raw_docked_sdf.exists():
                result["error"] = "obabel_convert_failed"
                result["stderr_head"] = obabel_result.stderr[:1000]
                return result
            topology_error = write_pose_with_template_topology(ligand, raw_docked_sdf, docked_sdf)
            if topology_error:
                result["error"] = f"topology_coordinate_merge_failed:{topology_error}"
                result["stderr_head"] = obabel_result.stderr[:1000]
                return result
        result.update({
            "candidate_id": f"{row.get('complex_id')}_vina_docked_pose_failure_0",
            "failure_type": "vina_docked_pose_failure",
            "failure_reason": "generated_by_vina_docking_smoke_template_topology",
            "failed_ligand_path": str(docked_sdf),
            "vina_stdout_head": vina_result.stdout[:1000],
            "error": None,
        })
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--molecules-dir", required=True)
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--exhaustiveness", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    rows = read_jsonl(args.input)[: args.limit]
    output_dir = Path(args.molecules_dir)
    results = [run_docking(row, output_dir, args.exhaustiveness, args.seed) for row in rows]
    successful = [row for row in results if not row.get("error")]
    failures = [row for row in results if row.get("error")]
    write_jsonl(args.output, successful)
    errors_path = Path(args.output).with_suffix(".errors.jsonl")
    write_jsonl(errors_path, failures)
    print(f"Read {len(rows)} input candidates")
    print(f"Wrote {len(successful)} successful Vina-docked pose records to {args.output}")
    print(f"Wrote {len(failures)} failed Vina-docked pose attempts to {errors_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
