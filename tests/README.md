# tests 目录管理说明

`tests/` 保存项目自动化测试。测试应优先覆盖可复现的轻量逻辑、schema refs、配置路径、canonical data writer、failure generation、metrics 和 audit wiring。

## 运行方式

默认使用项目开发环境 `pfr`:

```bash
conda run -n pfr env PYTHONPATH=src pytest -q
```

常用局部测试:

```bash
conda run -n pfr env PYTHONPATH=src pytest -q tests/test_data_schema_refs.py tests/test_config_schema_refs.py tests/test_audit_schemas.py
conda run -n pfr env PYTHONPATH=src pytest -q tests/test_smoke_pipeline.py tests/test_download_smoke_complexes.py
```

## 测试边界

- 默认测试不应依赖网络、GPU、大 checkpoint、第三方仓库完整安装或不可再分发数据。
- 需要 official PLIP / Vina / PoseBusters evaluator 的测试应明确标注环境需求, 使用 `pfr-eval-tools`, 不混入默认 `pfr` 快速测试。
- 测试写文件时优先使用 `tmp_path`; 不要无意写入真实 `outputs/`, `experiments/` 或 `data/datasets/`。
- 修改 schema、config、canonical data writer 或第三方 audit metadata 时, 同步补充或更新对应测试。
- 历史 fixture 或历史 output metadata 不要为了通过新测试而静默改写; 需要迁移时应有显式 migration 记录。
