# Audit Tool Coverage 小报告

日期: 2026-06-04
状态: `tool_coverage_review_completed`, `MVP_sufficient`, `formal_audit_not_yet_analysis_frozen`

## 1. 核心结论

按照 `docs/report/20260603-01-failure-taxonomy-research-report.md` 的调研结论和当前项目配置, 现有外部工具对第一阶段 MVP **基本足够**, 但对正式 third-party failure prevalence audit 和 `analysis-frozen` 结论 **还不够**。

简要判断:

| 阶段 | 是否足够 | 说明 |
|---|---|---|
| 第一阶段 MVP / sanity wiring | 足够 | 已覆盖 parse/sanitize、格式转换、interaction report、Vina 辅助 score 和基础 tool failure 记录 |
| 小规模 output-capture trial | 基本足够 | 可先用于 DiffSBDD / DiffLinker 输出后的诊断链路 sanity |
| formal failure prevalence audit | 不足 | 需要冻结 PoseBusters、RDKit、PLIP、Vina 的规则、输出字段、阈值、wrapper 和 hash |
| repair benchmark / 论文主结果 | 不足 | 还需要 scaffold/anchor preservation、contact-loss、labeling pipeline 和 sanity set |

## 2. 当前已具备的外部工具

当前主要评估环境为:

```text
conda env: pfr-eval-tools
path: /home/lyj/miniconda3/envs/pfr-eval-tools/
```

当前已确认工具覆盖:

| 工具 | 当前用途 | MVP 覆盖度 | 主要限制 |
|---|---|---|---|
| RDKit | 分子解析、sanitize、validity、基础 scaffold/anchor 检查入口 | 高 | sanitize/aromaticity/valence、substructure/atom mapping 规则未冻结 |
| OpenBabel | 分子格式转换 | 高 | 需记录转换失败和输入/输出格式边界 |
| Meeko | Vina ligand/receptor preparation | 中 | 主要服务 Vina, 不单独定义 failure label |
| PLIP | protein-ligand interaction report | 中高 | 还缺 XML/TXT parser、key interaction/contact-loss 规则和阈值冻结 |
| AutoDock Vina | docking / score-only 辅助指标 | 中 | 只能作为辅助 metric, 不能作为 success gate |
| PoseBusters | 3D geometry / pose plausibility / clash 检查 | 理论覆盖高, 当前工程冻结不足 | 已安装但未在 `tool_versions.lock` 中完整锁定 config、columns、阈值和 wrapper |

## 3. 与 failure taxonomy 调研的对应关系

调研报告指出, 本项目第一阶段最相关的 failure 类型包括:

- chemical invalidity / sanitization failure。
- local 3D geometry failure。
- protein-ligand clash / volume overlap。
- scaffold / anchor preservation failure。
- key interaction / contact loss。
- docking 或 evaluation tool failure。

当前工具对应关系:

| failure 维度 | 当前工具 | 当前状态 |
|---|---|---|
| chemical validity | RDKit, PoseBusters | RDKit 可用; PoseBusters 需冻结配置 |
| local geometry | PoseBusters, RDKit geometry scripts | PoseBusters 是关键缺口, RDKit 自定义脚本仍需实现 |
| clash / pocket overlap | PoseBusters, 可选 Arpeggio / MolProbity | MVP 可先用 PoseBusters; 交叉验证工具可后补 |
| interaction/contact loss | PLIP, 可选 ProLIF | PLIP 可用; contact-loss parser 和规则未冻结 |
| scaffold/anchor preservation | RDKit + 项目自定义脚本 | 外部工具只提供基础能力, 核心规则需项目内实现 |
| docking / score | Vina, Meeko, OpenBabel | 只能辅助, 不能单独证明修复成功 |
| tool/pipeline failure | 所有 wrapper 的 error fields | 需要统一 wrapper 和 not_evaluable 记录 |

## 4. 正式 audit 前的主要缺口

### 4.1 PoseBusters 未完成冻结

PoseBusters 是当前最大工具缺口。它适合覆盖:

- ligand chemical/geometric consistency。
- bond length / angle。
- ring / alkene flatness。
- internal clash。
- protein/cofactor/water overlap。
- protein-ligand distance / pocket plausibility。

但当前仍缺:

- 在 `configs/audit/tool_versions.lock` 中记录 PoseBusters 版本。
- 冻结使用 `mol`, `dock` 还是 `redock` config。
- 冻结输出 columns 到本项目 labels 的映射。
- 批量 wrapper 和 timeout/error 处理。
- sanity set 验证。

### 4.2 PLIP 还缺结构化 contact-loss 规则

PLIP 已适合做 interaction report, 但 formal audit 前需要:

- PLIP XML/TXT parser。
- reference/key interaction 的定义。
- contact count drop 或 IFP similarity 阈值。
- protonation / ligand ID / cofactor / water 处理规则。
- `plip_error` 和 not_evaluable 处理。

### 4.3 RDKit 规则需要冻结

RDKit 已足够作为基础 chemical gate, 但需要固定:

- `SanitizeMol` flags / catchErrors。
- aromaticity / valence edge case 规则。
- disconnected graph 判定。
- scaffold match / atom mapping / tautomer/protonation 容忍度。
- anchor distance 阈值。

### 4.4 还缺统一 labeling pipeline

正式 audit 前需要把工具输出转成统一结构:

```text
raw/tool outputs
→ structured tool result
→ evaluability_status
→ primary_label / secondary_labels
→ stage_attrition / prevalence summary
```

当前已有 schema/config, 但正式 labeling 脚本尚未完成。

## 5. 优先补充顺序

建议按以下顺序推进:

1. **PoseBusters**: 写入 `tool_versions.lock`, 冻结 config/columns/thresholds, 实现 batch wrapper。
2. **RDKit audit wrapper**: 固定 parse/sanitize/scaffold/anchor/anchor-distance 规则。
3. **PLIP parser**: 把 PLIP 输出转为 interaction/contact-loss labels。
4. **Vina/OpenBabel/Meeko wrapper**: 只作为辅助 metric, 重点记录 prep/docking error。
5. **统一 labeling 脚本**: 输出 `labels.jsonl` 和 `label_summary.json`。
6. **sanity set**: 验证 missing_data, tool_failure, pipeline_failure, not_evaluable, original_failed_sample 不被静默删除。

可选第二层交叉验证工具:

- ProLIF: interaction fingerprint / contact recovery。
- Arpeggio / MolProbity / Probe: clash/contact 交叉验证。

这些不是第一阶段 MVP 阻塞项。

## 6. 当前可允许的表述

允许表述:

> 当前工具栈足够支撑第一阶段 MVP 的 evaluator wiring 和小规模 output-capture sanity, 但尚未达到 formal third-party failure prevalence audit 的 analysis-frozen 要求。

不应表述:

> 当前工具已经足够完成正式 failure prevalence audit。

不应表述:

> Vina score 或单个工具结果可以单独定义 repair success。

## 7. 参考来源

项目内来源:

- `docs/report/20260603-01-failure-taxonomy-research-report.md`
- `configs/audit/tool_versions.lock`
- `configs/audit/diagnosis_label_config_v0_1.yaml`
- `configs/audit/README.md`

外部来源:

- RDKit documentation: https://www.rdkit.org/docs/RDKit_Book.html
- PLIP GitHub: https://github.com/pharmai/plip
- PLIP paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC4489249/
- AutoDock Vina GitHub: https://github.com/ccsb-scripps/AutoDock-Vina
- PoseBusters paper: https://pubs.rsc.org/en/content/articlelanding/2024/sc/d3sc04185a
- PoseBusters GitHub: https://github.com/maabuu/posebusters
- PoseBusters config examples: https://raw.githubusercontent.com/maabuu/posebusters/main/posebusters/config/dock.yml, https://raw.githubusercontent.com/maabuu/posebusters/main/posebusters/config/redock.yml
