# Notes

2026-06-04:

- Generated a unique source-to-target migration manifest for 89 migration-era processed JSONL files.
- Kept `rgroup_smoke.jsonl` and `rgroup_smoke_plus.jsonl` as canonical reusable dataset entries, now represented under `data/datasets/<dataset_id>/entries/index.jsonl`.
- Copied 87 derived JSONL artifacts into experiment-scoped `outputs/<experiment_id>/processed/` directories.
- Retargeted repository references from derived migration-era processed JSONL paths to the new `outputs/<experiment_id>/processed/` paths.
- Validation found zero remaining non-canonical migration-era processed JSONL references outside the migration manifest.
- Source files were intentionally left in place for a later `.gitignore` / git tracking cleanup stage.
