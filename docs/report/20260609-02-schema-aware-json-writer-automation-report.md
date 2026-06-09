# 基于 schema 的 JSON 自动填充落地报告

日期: 2026-06-09

对应计划: `docs/plan/20260609-02-schema-aware-json-writer-automation-plan.md`

## 概要

本轮完成 schema-aware writer 的第一版落地, 并把统一评估流水线中低风险的单行或单 payload 输出迁移到该 writer. 新写出的项目自有 JSON / JSONL 会从 JSON Schema 的 `const` 自动注入 `schema_version` 和 `schema_path`, 而不是在多个脚本中手写双常量.

## 已完成内容

- 新增 `src/pfr/utils/schema_io.py`, 提供 `load_schema_ref`, `with_schema_ref`, `write_json_with_schema`, `write_jsonl_with_schema` 和轻量 required/const 校验.
- `scripts/eval/audit_common.py` re-export schema-aware writer, 并新增 `finalize_output_manifest()` 用于最终刷新 `output_manifest.json` 的 artifact sha256 和 canonical `metadata_schemas`.
- 新增 `schemas/configs/audit/manual_decisions_v0_1.json`, 用于后续约束人工拍板 YAML. 本轮未在 `configs/audit/` 放空模板, 以遵守 `configs/README.md` 的目录规范.
- 已迁移到 schema-aware writer 的输出:
  - `evaluator/raw_tool_outputs/posebusters_*.json`
  - `evaluator/evaluator_input.jsonl`
  - `evaluator/evaluator_tool_results.jsonl`
  - `labels.jsonl`
  - `summaries/label_summary.json`
  - `summaries/prevalence_summary.json`
  - `summaries/analysis_frozen_gate_result.json`
- 暂缓迁移:
  - `run_metadata.json`, `samples.jsonl`, `stage_attrition.json`, `output_manifest.json` 的初始 writer. 这些文件跨阶段语义不同或需要最终 manifest finalizer 统一处理.

## 重要边界

- writer 只负责格式来源字段和轻量结构校验, 不自动决定 `primary_label`, `gate_status`, `claim_boundary`, `training_data_status` 等科学语义字段.
- 人工判断后续应进入 schema-covered `manual_decisions.yaml`, 并作为单次实验 resolved config 保存到 `experiments/<experiment_id>/configs/resolved/audit/`.
- 输出 JSON / JSONL 只记录 manual decisions 的路径、hash、version 和相关 decision ids, 不嵌入整份 YAML.
- 历史 outputs 没有被自动重写.

## 验证

已运行:

```bash
conda run -n pfr env PYTHONPATH=src pytest -q
```

结果:

```text
51 passed in 0.79s
```

## 下一步

- 在下一次真实 evaluator run 中验证 `finalize_output_manifest()` 刷新后的 sha256 是否覆盖所有最终 artifact.
- 需要人工拍板时, 为具体实验新增 resolved `manual_decisions.yaml`, 并把 manual decision provenance 接入 `run_metadata.json`, `labels.jsonl` 和 gate result.
- 后续再评估是否引入完整 JSON Schema validator; 当前第一版只做轻量校验.
