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

## Official evaluation environment pitfalls

Official PLIP/Vina evaluation must be run in the isolated `pfr-eval-tools` conda environment, not the base `pfr` environment. The `pfr` environment is validated for RDKit-first data generation, repair, fallback metrics, and summary scripts, but it intentionally does not include the official external CLIs.

Use this split:

```bash
PATH=/home/lyj/miniconda3/envs/pfr-eval-tools/bin:$PATH \
PYTHONPATH=src \
/home/lyj/miniconda3/envs/pfr-eval-tools/bin/python scripts/eval/eval_official_tools.py \
  --repaired-candidates <input.jsonl> \
  --output <official_eval.jsonl> \
  --tools plip,vina \
  --keep-work-dir <work-dir>
conda run -n pfr env PYTHONPATH=src python scripts/eval/summarize_official_eval.py \
  --input <official_eval.jsonl> \
  --output-json <summary.json> \
  --output-csv <summary.csv>
```

Important: using the `pfr-eval-tools` Python interpreter is not always enough. The official CLI tools (`plip`, `mk_prepare_ligand.py`, `mk_prepare_receptor.py`, `vina`) are discovered through `PATH`. If the environment's `bin` directory is not on `PATH`, `eval_official_tools.py` can still write one row per input while every row contains `plip_cli_missing` or `missing_cli:mk_prepare_ligand.py,mk_prepare_receptor.py,vina`. For direct interpreter calls, prefix the command with `PATH=/home/lyj/miniconda3/envs/pfr-eval-tools/bin:$PATH`. `conda run -n pfr-eval-tools ...` usually handles this, but still verify the error counters after every official run.

Before trusting official outputs, check both row count and error fields:

```bash
python - <<'PY'
import json
from collections import Counter
from pathlib import Path
rows = [json.loads(line) for line in Path('<official_eval.jsonl>').open()]
print('rows', len(rows))
print('plip_error', Counter(row.get('plip_error') for row in rows).most_common())
print('vina_error', Counter(row.get('vina_error') for row in rows).most_common())
PY
```

A JSONL with the expected number of rows is not sufficient. If `plip_error=plip_cli_missing` or `vina_error=missing_cli:mk_prepare_ligand.py,mk_prepare_receptor.py,vina`, the run used the wrong environment and must not be reported as an official result. Preserve this failed run in `docs/EXPERIMENT_LOG.md` as a negative/blocked attempt if it affected the research trail.

## Claude tool-use pitfall

When reading normal text files with Claude's `Read` tool, do not pass `pages: ""`. The `pages` argument is only for PDFs and must be omitted for Markdown, JSON, Python, YAML, and other text files. Passing an empty `pages` string causes `Invalid pages parameter` errors and wastes the turn.

