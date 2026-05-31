#!/usr/bin/env python3
"""Extract lightweight RDKit-backed feedback records for smoke testing."""

from __future__ import annotations

import argparse
from typing import Any

from pfr.utils.io import load_yaml, read_jsonl, write_jsonl


FAILURE_DEFAULTS = {
    "clash": {"clash_count": 1, "anchor_distance_error": 0.0, "editable_region_validity": True},
    "interaction_loss": {"clash_count": 0, "anchor_distance_error": 0.0, "editable_region_validity": True},
    "anchor_invalid": {"clash_count": 0, "anchor_distance_error": 2.0, "editable_region_validity": False},
    "geometry_invalid": {"clash_count": 0, "anchor_distance_error": 0.0, "editable_region_validity": False},
}


def has_editable_region(candidate: dict[str, Any]) -> bool:
    return bool(candidate.get("editable_atoms"))


def has_anchor(candidate: dict[str, Any]) -> bool:
    return bool(candidate.get("anchor_atoms"))


def build_feedback(candidate: dict[str, Any]) -> dict[str, Any]:
    failure_type = str(candidate.get("failure_type", "unknown_failure"))
    defaults = FAILURE_DEFAULTS.get(
        failure_type,
        {"clash_count": 0, "anchor_distance_error": 0.0, "editable_region_validity": True},
    )
    descriptors = candidate.get("descriptors", {}) or {}
    scaffold_present = bool(candidate.get("scaffold_atoms"))
    anchor_present = has_anchor(candidate)
    editable_present = has_editable_region(candidate)
    editable_valid = bool(defaults["editable_region_validity"] and editable_present)
    anchor_distance_error = float(defaults["anchor_distance_error"])
    if not anchor_present:
        anchor_distance_error = max(anchor_distance_error, 2.0)
    return {
        "candidate_id": candidate.get("candidate_id"),
        "complex_id": candidate.get("complex_id"),
        "failure_type": failure_type,
        "global": {
            "qed": descriptors.get("qed"),
            "sa": None,
            "logp": descriptors.get("logp"),
            "rotatable_bonds": descriptors.get("rotatable_bonds"),
            "molecular_weight": descriptors.get("molecular_weight"),
            "tpsa": descriptors.get("tpsa"),
            "vina_score": None,
            "posebusters_pass": None,
        },
        "geometry": {
            "clash_count": defaults["clash_count"],
            "min_protein_ligand_distance": None,
            "anchor_distance_error": anchor_distance_error,
            "editable_region_validity": editable_valid,
            "scaffold_present": scaffold_present,
            "anchor_present": anchor_present,
            "editable_atom_count": len(candidate.get("editable_atoms", [])),
            "scaffold_atom_count": len(candidate.get("scaffold_atoms", [])),
        },
        "interaction": {
            "plip_hbond_count": None,
            "plip_hydrophobic_count": None,
            "plip_salt_bridge_count": None,
            "interaction_fingerprint_similarity": None,
        },
        "source": "smoke_rdkit_descriptors_plus_failure_template",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    config = load_yaml(args.config)
    input_path = config["input"]["candidates_path"]
    output_path = config["output"]["feedback_path"]
    candidates = read_jsonl(input_path)
    rows = [build_feedback(candidate) for candidate in candidates]

    write_jsonl(output_path, rows)
    print(f"Read {len(candidates)} candidates from {input_path}")
    print(f"Wrote {len(rows)} feedback records to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
