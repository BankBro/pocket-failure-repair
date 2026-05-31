# Optional Tool Notes

## PLIP

PLIP is useful for protein-ligand interaction feedback, but installing `plip` from pip can build Open Babel and may fail without system-level Open Babel, SWIG, and pkg-config. The core `pfr` environment therefore does not require PLIP for smoke reproducibility.

Recommended handling:

- Treat PLIP as optional until the base RDKit pipeline is stable.
- Prefer a conda/Open Babel based installation or a containerized PLIP workflow.
- Record exact installation command, Open Babel version, and failure logs before using PLIP metrics in any paper claim.

## Torch / PyG

The base smoke pipeline does not require Torch or PyG. Model training should use a separate environment, e.g. `configs/environment_ml_optional.yml`, after data and feedback extraction are validated.

## Current validated base environment

`conda run -n pfr python scripts/setup/check_environment.py` passed required checks with:

- Python 3.11.15.
- RDKit 2026.03.2.
- Required checks passed.
- Optional tools missing: torch, torch_geometric, pytorch_lightning, vina, posebusters, plip, meeko.

This is sufficient for RDKit-first data and smoke development, but not for final Vina / PLIP / PoseBusters / model experiments.
