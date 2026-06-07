# Notes

2026-06-04:

- Migrated legacy `experiments/20260531-01-smoke-file-pipeline/metadata/pipeline_plan.json` into dated experiment metadata.
- Migrated `experiments/smoke*/multiseed_repaired/` generated artifacts into corresponding `outputs/<experiment_id>/processed/multiseed_repaired/` directories.
- Moved generated `outputs/<experiment_id>/raw/` cases/failed molecule artifacts to `processed/cases/` and `processed/failed_molecules/`.
- Moved generated `outputs/<experiment_id>/normalized/` repaired molecule artifacts to `processed/repaired_molecules/`.
- Moved canonical split files under `data/datasets/<dataset_id>/splits/`.
- Moved raw dataset manifests under `data/datasets/<dataset_id>/raw/`.
- Did not modify `.gitignore`.
