#!/usr/bin/env python3
"""Compute lightweight DiffSBDD-style molecular sanity metrics for stage 1."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
DIFFSBDD_ROOT = ROOT / "third_party" / "diffsbdd"
if str(DIFFSBDD_ROOT) not in sys.path:
    sys.path.insert(0, str(DIFFSBDD_ROOT))

from rdkit import Chem

from analysis.metrics import MoleculeProperties, rdmol_to_smiles


SUMMARY_SCHEMA_VERSION = "mvp_sanity_summary_v0_1"
SUMMARY_SCHEMA_PATH = "schemas/third_party_audit/diagnosis/mvp_sanity_summary_v0_1.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def summarize(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "mean": None, "std": None}
    return {"n": len(values), "mean": mean(values), "std": pstdev(values)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", required=True)
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    samples = read_jsonl(run_root / "samples.jsonl")

    parsed_mols: list[Chem.Mol] = []
    valid_mols: list[Chem.Mol] = []
    connected_mols: list[Chem.Mol] = []
    connected_smiles: list[str] = []
    parse_failures: list[dict[str, str]] = []
    sanitize_failures: list[dict[str, str]] = []

    for sample in samples:
        molecule_path = sample.get("molecule_path")
        if not molecule_path:
            parse_failures.append({"sample_id": sample["sample_id"], "reason": "missing_molecule_path"})
            continue
        path = Path(molecule_path)
        supplier = Chem.SDMolSupplier(str(path), sanitize=False, removeHs=False)
        mol = next((item for item in supplier if item is not None), None)
        if mol is None:
            parse_failures.append({"sample_id": sample["sample_id"], "reason": "rdkit_parse_returned_none"})
            continue

        parsed_mols.append(mol)
        mol_copy = Chem.Mol(mol)
        try:
            Chem.SanitizeMol(mol_copy)
        except Exception as exc:
            sanitize_failures.append({"sample_id": sample["sample_id"], "reason": repr(exc)})
            continue

        valid_mols.append(mol_copy)
        fragments = Chem.rdmolops.GetMolFrags(mol_copy, asMols=True)
        largest = max(fragments, default=mol_copy, key=lambda item: item.GetNumAtoms())
        if mol_copy.GetNumAtoms() > 0 and largest.GetNumAtoms() / mol_copy.GetNumAtoms() >= 1.0:
            connected_mols.append(largest)
            connected_smiles.append(rdmol_to_smiles(largest))

    props = MoleculeProperties()
    qed_values = [props.calculate_qed(mol) for mol in connected_mols]
    sa_values = [props.calculate_sa(mol) for mol in connected_mols]
    logp_values = [props.calculate_logp(mol) for mol in connected_mols]
    lipinski_values = [float(props.calculate_lipinski(mol)) for mol in connected_mols]
    diversity = props.calculate_diversity(connected_mols)

    n_budget = len(samples)
    n_parsed = len(parsed_mols)
    n_valid = len(valid_mols)
    n_connected = len(connected_mols)
    unique_smiles = sorted(set(connected_smiles))
    metrics = {
        "validity_over_budget": n_valid / n_budget if n_budget else None,
        "parse_success_over_budget": n_parsed / n_budget if n_budget else None,
        "connectivity_over_valid": n_connected / n_valid if n_valid else None,
        "uniqueness_over_connected": len(unique_smiles) / n_connected if n_connected else None,
        "novelty": None,
        "novelty_note": "Not computed because training SMILES / official train set provenance is not frozen in this stage.",
        "qed": summarize(qed_values),
        "sa": summarize(sa_values),
        "logp": summarize(logp_values),
        "lipinski": summarize(lipinski_values),
        "diversity": diversity,
    }

    output_path = run_root / "official_like_metrics" / "basic_molecular_metrics.json"
    payload = {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "schema_path": SUMMARY_SCHEMA_PATH,
        "run_id": samples[0]["run_id"] if samples else run_root.name,
        "method": samples[0]["method"] if samples else "DiffSBDD",
        "summary_type": "official_like_basic_molecular_metrics",
        "claim_boundary": "mvp_sanity_not_formal_prevalence",
        "counts": {
            "N_budget": n_budget,
            "N_parsed": n_parsed,
            "N_valid": n_valid,
            "N_connected": n_connected,
            "N_unique_connected_smiles": len(unique_smiles),
            "N_parse_failures": len(parse_failures),
            "N_sanitize_failures": len(sanitize_failures),
        },
        "metrics": metrics,
        "parse_failures": parse_failures,
        "sanitize_failures": sanitize_failures,
        "notes": "Lightweight stage 1 sanity metrics computed from captured README-example outputs. This is not a full original paper benchmark reproduction.",
    }
    write_json(output_path, payload)

    manifest_path = run_root / "output_manifest.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        manifest.setdefault("official_like_metrics", [])
        if str(output_path) not in manifest["official_like_metrics"]:
            manifest["official_like_metrics"].append(str(output_path))
        manifest.setdefault("sha256", {})[str(output_path)] = sha256_file(output_path)
        manifest["notes"] = "Output capture, evaluator sanity and official-like basic metric manifest. No formal labels generated."
        write_json(manifest_path, manifest)

    print(json.dumps({"output": str(output_path), "counts": payload["counts"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
