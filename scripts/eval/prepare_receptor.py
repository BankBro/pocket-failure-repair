#!/usr/bin/env python3
"""Prepare a cleaned receptor PDB and receptor-prep metadata for audit evaluators."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.audit_common import load_yaml, normalized_config_hash, sha256_file, write_json


SCHEMA_VERSION = "receptor_prep_record_v0_1"
SCHEMA_PATH = "schemas/third_party_audit/receptor/receptor_prep_record_v0_1.json"
INDEX_SCHEMA_VERSION = "receptor_prep_index_v0_1"
INDEX_SCHEMA_PATH = "schemas/third_party_audit/receptor/receptor_prep_index_v0_1.json"


def parse_atom_line(line: str) -> dict[str, Any]:
    element = line[76:78].strip() if len(line) >= 78 else ""
    atom_name = line[12:16].strip()
    if not element:
        element = "".join(ch for ch in atom_name if ch.isalpha())[:2].strip().upper()
    return {
        "record": line[:6].strip(),
        "serial": int(line[6:11]),
        "atom_name": atom_name,
        "altloc": line[16:17].strip(),
        "residue_name": line[17:20].strip(),
        "chain_id": line[21:22].strip(),
        "residue_number": int(line[22:26]),
        "insertion_code": line[26:27].strip(),
        "x": float(line[30:38]),
        "y": float(line[38:46]),
        "z": float(line[46:54]),
        "element": element.upper(),
        "line": line.rstrip("\n"),
    }


def group_key(atom: dict[str, Any]) -> tuple[str, str, int, str, str]:
    return (
        atom["residue_name"],
        atom["chain_id"],
        atom["residue_number"],
        atom["insertion_code"],
        atom["altloc"],
    )


def parse_reference_spec(value: str) -> tuple[str, int, str | None]:
    parts = value.split(":")
    if len(parts) < 2:
        raise ValueError("--reference-ligand must look like A:330 or A:330:CFF")
    chain_id = parts[0]
    residue_number = int(parts[1])
    residue_name = parts[2].upper() if len(parts) >= 3 and parts[2] else None
    return chain_id, residue_number, residue_name


def heavy_atoms(atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [atom for atom in atoms if atom["element"].upper() not in {"H", "D"}]


def centroid(atoms: list[dict[str, Any]]) -> list[float]:
    if not atoms:
        return [0.0, 0.0, 0.0]
    return [
        round(sum(float(atom[axis]) for atom in atoms) / len(atoms), 4)
        for axis in ["x", "y", "z"]
    ]


def bounding_span(atoms: list[dict[str, Any]]) -> list[float]:
    if not atoms:
        return [0.0, 0.0, 0.0]
    spans = []
    for axis in ["x", "y", "z"]:
        values = [float(atom[axis]) for atom in atoms]
        spans.append(round(max(values) - min(values), 4))
    return spans


def distance(a: dict[str, Any], b: dict[str, Any]) -> float:
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2 + (a["z"] - b["z"]) ** 2)


def minimum_distance(atoms: list[dict[str, Any]], reference_atoms: list[dict[str, Any]]) -> float | None:
    if not atoms or not reference_atoms:
        return None
    return round(min(distance(atom, ref) for atom in atoms for ref in reference_atoms), 4)


def hetero_record(
    atoms: list[dict[str, Any]],
    classification: str,
    action: str,
    reason: str,
    rule_id: str,
    reference_atoms: list[dict[str, Any]],
) -> dict[str, Any]:
    first = atoms[0]
    atom_elements = sorted({atom["element"] for atom in atoms if atom["element"]})
    heavy = heavy_atoms(atoms)
    return {
        "residue_name": first["residue_name"],
        "chain_id": first["chain_id"],
        "residue_number": first["residue_number"],
        "insertion_code": first["insertion_code"],
        "altloc": first["altloc"],
        "atom_count": len(atoms),
        "heavy_atom_count": len(heavy),
        "elements": atom_elements,
        "min_distance_to_reference_ligand_angstrom": minimum_distance(heavy, reference_atoms),
        "classification": classification,
        "action": action,
        "reason": reason,
        "rule_id": rule_id,
    }


def classify_group(
    atoms: list[dict[str, Any]],
    reference_key: tuple[str, str, int, str, str],
    policy: dict[str, Any],
    reference_atoms: list[dict[str, Any]],
) -> tuple[str, str, str, str]:
    rules = policy["hetero_atom_rules"]
    residue_name = atoms[0]["residue_name"].upper()
    key = group_key(atoms[0])
    if key == reference_key:
        return (
            "reference_ligand",
            "remove_reference_ligand",
            "reference ligand removed from cleaned receptor",
            "remove_reference_ligand_v0_1",
        )
    if residue_name in set(rules.get("ordinary_water_residue_names", [])):
        return ("ordinary_water", "remove_water", "ordinary water removed", "remove_ordinary_water_v0_1")
    if residue_name in set(rules.get("crystallization_additive_residue_names", [])):
        return (
            "crystallization_additive",
            "remove_crystallization_additive",
            "common crystallization additive removed",
            "remove_crystallization_additive_v0_1",
        )
    if residue_name in set(rules.get("retained_metal_or_ion_residue_names", [])):
        return ("retained_metal_or_ion", "retain", "known metal or ion retained", "retain_metal_or_ion_v0_1")
    if residue_name in set(rules.get("retained_key_cofactor_residue_names", [])):
        return ("retained_key_cofactor", "retain", "known key cofactor retained", "retain_key_cofactor_v0_1")
    min_dist = minimum_distance(heavy_atoms(atoms), reference_atoms)
    review_distance = float(rules.get("unknown_review_distance_angstrom", 8.0))
    if min_dist is not None and min_dist <= review_distance:
        return (
            "unknown_hetero_near_pocket",
            "review_required",
            f"unknown HETATM within {review_distance:.1f} A of reference ligand",
            "unknown_hetero_near_reference_ligand_v0_1",
        )
    return (
        "unknown_hetero_far_from_pocket",
        "remove_as_unrelated_hetero",
        "unknown HETATM outside review distance removed as unrelated",
        "remove_unknown_hetero_far_from_reference_ligand_v0_1",
    )


def atom_counts(lines: list[str]) -> tuple[int, int]:
    atom_count = 0
    hetero_groups: set[tuple[str, str, str, str, str]] = set()
    for line in lines:
        if line.startswith(("ATOM", "HETATM")):
            atom_count += 1
        if line.startswith("HETATM"):
            atom = parse_atom_line(line)
            hetero_groups.add(group_key(atom))
    return atom_count, len(hetero_groups)


def should_remove_metadata_line(line: str, removed_residue_names: set[str]) -> bool:
    record = line[:6].strip()
    tokens = set(line.split())
    if record in {"HETNAM", "HETSYN", "FORMUL"} and removed_residue_names & tokens:
        return True
    if record == "HET":
        residue_name = line[7:10].strip()
        return residue_name in removed_residue_names
    return False


def conect_references_removed_serial(line: str, removed_serials: set[int]) -> bool:
    if not line.startswith("CONECT"):
        return False
    for token in line.split()[1:]:
        try:
            if int(token) in removed_serials:
                return True
        except ValueError:
            continue
    return False


def write_cleaned_pdb(raw_lines: list[str], output_path: Path, removed_serials: set[int], removed_residue_names: set[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for line in raw_lines:
            stripped = line.rstrip("\n")
            if stripped.startswith("HETATM"):
                atom = parse_atom_line(stripped)
                if atom["serial"] in removed_serials:
                    continue
            if conect_references_removed_serial(stripped, removed_serials):
                continue
            if should_remove_metadata_line(stripped, removed_residue_names):
                continue
            if stripped.startswith("MASTER"):
                continue
            handle.write(stripped + "\n")
        if raw_lines and not raw_lines[-1].startswith("END"):
            handle.write("END\n")


def write_reference_ligand_pdb(atoms: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for atom in atoms:
            handle.write(atom["line"] + "\n")
        handle.write("END\n")


def build_record(args: argparse.Namespace) -> dict[str, Any]:
    raw_receptor = Path(args.raw_receptor).resolve()
    policy_path = Path(args.policy).resolve()
    policy = load_yaml(policy_path)
    raw_lines = raw_receptor.read_text(encoding="utf-8", errors="ignore").splitlines()

    hetero_groups: dict[tuple[str, str, int, str, str], list[dict[str, Any]]] = {}
    for line in raw_lines:
        if line.startswith("HETATM"):
            atom = parse_atom_line(line)
            hetero_groups.setdefault(group_key(atom), []).append(atom)

    ref_chain, ref_number, ref_resname = parse_reference_spec(args.reference_ligand)
    reference_candidates = [
        (key, atoms)
        for key, atoms in hetero_groups.items()
        if key[1] == ref_chain and key[2] == ref_number and (ref_resname is None or key[0].upper() == ref_resname)
    ]
    if not reference_candidates:
        raise ValueError(f"reference ligand {args.reference_ligand} was not found as HETATM in {raw_receptor}")
    reference_key, reference_atoms_all = reference_candidates[0]
    reference_atoms = heavy_atoms(reference_atoms_all)
    reference_residue_name = reference_key[0]

    output_dir = Path(args.output_dir).resolve()
    output_prefix = args.output_prefix or f"{args.case_id}_{ref_chain}_{ref_number}_{reference_residue_name}"
    cleaned_receptor_path = output_dir / f"{output_prefix}_cleaned_receptor.pdb"
    reference_ligand_path = output_dir / f"{output_prefix}_reference_ligand.pdb"
    receptor_prep_path = output_dir / f"{output_prefix}_receptor_prep.json"

    removed: list[dict[str, Any]] = []
    retained: list[dict[str, Any]] = []
    review_required: list[dict[str, Any]] = []
    removed_serials: set[int] = set()
    removed_residue_names: set[str] = set()

    for key, atoms in sorted(hetero_groups.items()):
        classification, action, reason, rule_id = classify_group(atoms, reference_key, policy, reference_atoms)
        record = hetero_record(atoms, classification, action, reason, rule_id, reference_atoms)
        if action.startswith("remove"):
            removed.append(record)
            removed_serials.update(atom["serial"] for atom in atoms)
            removed_residue_names.add(atoms[0]["residue_name"])
        elif action == "review_required":
            record.update(
                {
                    "decision_status": "unresolved",
                    "decision": None,
                    "decision_reason": None,
                    "reviewed_by": None,
                    "review_time": None,
                    "action_applied": False,
                    "whitelist_update": None,
                }
            )
            review_required.append(record)
        else:
            retained.append(record)

    write_reference_ligand_pdb(reference_atoms_all, reference_ligand_path)
    write_cleaned_pdb(raw_lines, cleaned_receptor_path, removed_serials, removed_residue_names)
    raw_atom_count, raw_hetero_group_count = atom_counts(raw_lines)
    cleaned_atom_count, cleaned_hetero_group_count = atom_counts(cleaned_receptor_path.read_text(encoding="utf-8").splitlines())

    center = centroid(reference_atoms)
    span = bounding_span(reference_atoms)
    pocket_policy = policy.get("pocket_box_policy", {})
    padding = float(pocket_policy.get("padding_angstrom", 8.0))
    minimum = float(pocket_policy.get("minimum_size_angstrom", 12.0))
    size = [round(max(minimum, value + padding), 4) for value in span]
    receptor_prep_id = f"{args.case_id}_{ref_chain}_{ref_number}_{reference_residue_name}_pfr_receptor_prep_v0_1".lower()

    payload = {
        "schema_version": SCHEMA_VERSION,
        "schema_path": SCHEMA_PATH,
        "receptor_prep_id": receptor_prep_id,
        "case_id": args.case_id,
        "receptor_prep_policy_version": policy["receptor_prep_policy_version"],
        "receptor_prep_policy_hash": normalized_config_hash(policy_path),
        "raw_receptor_path": str(raw_receptor),
        "raw_receptor_sha256": sha256_file(raw_receptor),
        "raw_atom_count": raw_atom_count,
        "raw_hetero_group_count": raw_hetero_group_count,
        "cleaned_receptor_path": str(cleaned_receptor_path),
        "cleaned_receptor_sha256": sha256_file(cleaned_receptor_path),
        "cleaned_atom_count": cleaned_atom_count,
        "cleaned_hetero_group_count": cleaned_hetero_group_count,
        "reference_ligand_path": str(reference_ligand_path),
        "reference_ligand_sha256": sha256_file(reference_ligand_path),
        "reference_ligand": {
            "residue_name": reference_residue_name,
            "chain_id": ref_chain,
            "residue_number": ref_number,
            "insertion_code": reference_key[3],
            "altloc": reference_key[4],
            "role": "removed_reference_ligand",
            "heavy_atom_count": len(reference_atoms),
            "centroid_angstrom": center,
            "bounding_box_span_angstrom": span,
            "source_path": str(raw_receptor),
        },
        "pocket_box": {
            "box_policy_version": pocket_policy.get("box_policy_version", "pfr_vina_box_v0_1"),
            "box_source": "reference_ligand_heavy_atom_centroid",
            "center_angstrom": center,
            "size_angstrom": size,
            "padding_angstrom": padding,
            "minimum_size_angstrom": minimum,
            "atom_selection": "reference_ligand_heavy_atoms",
            "generated_ligand_centroid_fallback_used": False,
        },
        "removed_hetero_atoms": removed,
        "retained_hetero_atoms": retained,
        "review_required_hetero_atoms": review_required,
        "unresolved_review_required_count": sum(1 for item in review_required if item.get("decision_status") == "unresolved"),
        "warnings": [],
    }
    write_json(receptor_prep_path, payload)

    if args.index:
        index_path = Path(args.index).resolve()
        index_payload = {
            "schema_version": INDEX_SCHEMA_VERSION,
            "schema_path": INDEX_SCHEMA_PATH,
            "run_id": args.run_id or "unknown_run",
            "receptor_preps": [
                {
                    "receptor_prep_id": receptor_prep_id,
                    "case_id": args.case_id,
                    "receptor_prep_record_path": str(receptor_prep_path),
                    "cleaned_receptor_path": str(cleaned_receptor_path),
                    "reference_ligand_path": str(reference_ligand_path),
                    "unresolved_review_required_count": payload["unresolved_review_required_count"],
                }
            ],
        }
        write_json(index_path, index_payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-receptor", required=True)
    parser.add_argument("--reference-ligand", required=True, help="Reference ligand spec such as A:330 or A:330:CFF")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--policy", default="configs/audit/receptor_prep_policy_v0_1.yaml")
    parser.add_argument("--output-prefix", default=None)
    parser.add_argument("--index", default=None)
    parser.add_argument("--run-id", default=None)
    args = parser.parse_args()
    payload = build_record(args)
    print(
        {
            "receptor_prep_id": payload["receptor_prep_id"],
            "cleaned_receptor_path": payload["cleaned_receptor_path"],
            "unresolved_review_required_count": payload["unresolved_review_required_count"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
