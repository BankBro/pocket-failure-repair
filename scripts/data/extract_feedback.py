#!/usr/bin/env python3
"""Extract lightweight feedback records for smoke testing."""

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


def build_feedback(candidate: dict[str, Any]) -> dict[str, Any]:
    failure_type = str(candidate.get("failure_type", "unknown_failure"))
    defaults = FAILURE_DEFAULTS.get(
        failure_type,
        {"clash_count": 0, "anchor_distance_error": 0.0, "editable_region_validity": True},
    )
    return {
        "candidate_id": candidate.get("candidate_id"),
        "complex_id": candidate.get("complex_id"),
        "failure_type": failure_type,
        "global": {
            "qed": None,
            "sa": None,
            "logp": None,
            "rotatable_bonds": None,
            "vina_score": None,
            "posebusters_pass": None,
        },
        "geometry": {
            "clash_count": defaults["clash_count"],
            "min_protein_ligand_distance": None,
            "anchor_distance_error": defaults["anchor_distance_error"],
            "editable_region_validity": defaults["editable_region_validity"],
        },
        "interaction": {
            "plip_hbond_count": None,
            "plip_hydrophobic_count": None,
            "plip_salt_bridge_count": None,
            "interaction_fingerprint_similarity": None,
        },
        "source": "smoke_placeholder",
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
