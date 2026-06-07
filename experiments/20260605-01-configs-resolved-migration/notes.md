# Notes

- `configs/baselines/`, `configs/feedback/`, `configs/data/failed_candidate_*.yaml` 和顶层 eval summary 配置已按 owner experiment 迁到 `experiments/<experiment_id>/configs/resolved/`。
- `configs/data/smoke*_download.yaml` 的完整当前版本已保存为实验 resolved snapshot; 项目级版本改为 `configs/data/download_templates/` 下的 canonical dataset download template。
- DiffSBDD / DiffLinker audit protocol 的完整 MVP trial 版本已保存到 `experiments/20260603-01-third-party-failure-audit-mvp/configs/resolved/third_party/`; 项目级版本保留为带 `{experiment_id}` / `{run_id}` placeholder 的 protocol template。
