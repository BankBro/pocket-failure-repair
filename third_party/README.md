# third_party workspace

This directory is reserved for official third-party method repositories used in the failure audit.

Repositories cloned here are treated as external artifacts. Do not commit large checkpoints, datasets, generated outputs, or modified upstream source trees. Record upstream URL, commit, license, resource status, and run notes in the audit manifests under `docs/report/` and `configs/third_party/`.

## Patch and instrumentation placement

- Long-lived reusable patches for a third-party method should be stored under `third_party/patches/<method>/` and referenced from the relevant audit config or report.
- One-off patches for a specific experiment should be stored under `experiments/<experiment_id>/patches/`, alongside that experiment's resolved configs and command records.
- Wrapper or instrumentation code that does not need to modify upstream source should live under `scripts/third_party/`.
- Avoid editing cloned upstream source trees in place. If a source change is unavoidable, record whether it changes the algorithm; algorithm-changing patches must be reported as an adapted baseline rather than an original protocol reproduction.
