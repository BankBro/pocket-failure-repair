# 统一评估流水线对齐计划

> 本文档记录第三方方法审计进入正式失败分布统计前, 评估流水线需要统一的输入准备, 工具适配, 分母记录, 标签生成和分析冻结要点. 它是冻结前施工图, 不是实验结果报告, 也不是正式 failure prevalence 结论.

## 背景

DiffSBDD 阶段 0 和阶段 1 已经验证:

- 第三方方法最小推理可以运行.
- `samples.jsonl`, `run_metadata.json`, `stage_attrition.json` 等元数据可以保存分母和输出.
- RDKit, PoseBusters, PLIP, Vina 等评估工具已经能被接通.
- 当前评估结果仍属于健全性接线证据, 不能解释成正式失败分布.

下一步在扩大 DiffSBDD 样本量或接入更多方法前, 需要先统一评估流水线. 否则不同工具可能使用不同 receptor 输入, 不同失败列和不同分母口径, 最终标签会难以解释.

## 目标

本计划要对齐以下内容:

- 统一 receptor preparation: 从原始 PDB 和参考配体得到清理后的 receptor.
- 统一工具输入: PoseBusters, PLIP, Vina, ProLIF, Arpeggio 等工具都从同一份 cleaned receptor 派生输入.
- 统一 PoseBusters 冻结口径: 区分配体自身检查和口袋空间检查, 不把完整报告里的所有布尔列都当成正式失败 gate.
- 统一可评价性和分母: 样本不能因为缺失 SDF, 工具超时或转换失败被静默丢掉.
- 统一输出结构和 schema: 每个项目自有 JSON / JSONL 都记录 `schema_version` 和 `schema_path`.
- 统一分析冻结 gate: 在 gate 通过前, 不声明正式失败率, 不声明 repair benchmark result.

## 非目标

本文档不覆盖:

- DiffSBDD 原论文完整复现.
- DiffLinker 或其他方法的具体执行方案.
- 正式失败率结果.
- 修复模型训练或 benchmark.
- 人工判例 adjudication 的完整 SOP.

## 总体流水线

推荐的统一评估流水线为:

```text
raw receptor PDB
+ reference ligand id, 例如 CFF A:330
-> receptor preparation
   -> cleaned receptor PDB
   -> 同名 receptor prep JSON
-> method generated ligand SDF
-> tool-specific inputs
   - PoseBusters: cleaned receptor PDB + generated ligand SDF
   - PLIP: cleaned receptor + generated ligand 合成 complex PDB
   - Vina: cleaned receptor 转 PDBQT, ligand 转 PDBQT
   - ProLIF: cleaned receptor / complex 转成可读取对象
   - Arpeggio: cleaned complex 转 mmCIF
-> evaluator tool results
-> labels.jsonl
-> label summary and prevalence summary
-> analysis-frozen gate report
```

核心原则是: receptor 清理规则只在上游定义一次, 各工具只做格式适配, 不各自重新定义口袋.

## v0.1 规则冻结决议

截至 2026-06-08, 以下规则口径已确认可作为 v0.1 冻结目标. 这里的“冻结”指评估规则口径已定, 不是说对应脚本、schema 和 `analysis-frozen` gate 已经全部实现或通过.

- 第一版主评估流水线采用 RDKit + PoseBusters + PLIP + Vina 辅助分数. ProLIF 和 Arpeggio 暂不进入第一版主 gate, 后续只作为 pilot 或交叉验证工具.
- receptor preparation 采用保守自动清理 + 可复核记录: 删除 reference ligand, 删除普通水和常见结晶添加剂, 保留明确金属和关键辅因子, 不确定 HETATM 必须记录并复核.
- 口袋附近 unknown HETATM 的复核距离固定为 `8.0 A`. 任一 unknown HETATM heavy atom 到 reference ligand heavy atom 的最小距离 `<= 8.0 A` 时, 写入 `review_required_hetero_atoms`.
- 第一版 metal / cofactor whitelist 采用小集合起步, 后续遇到新 residue 时必须进入复核流程. 只有复核决定为 `retain_and_add_to_whitelist` 时才扩展中央白名单.
- 正式分析前, `review_required_hetero_atoms` 不允许有 unresolved 项. 若仍有未复核 HETATM, `analysis-frozen` gate 必须失败.
- `receptor_prep_sensitive` 同时作为 secondary label 和 evidence flag. 若失败证据主要由保留或待复核 HETATM, 水, 金属, 辅因子, 或 receptor 清理选择触发, 不能直接归咎于生成模型.
- PoseBusters 冻结为 `posebusters_ligand_core` 和 `posebusters_pocket_core` 两层. 可以保存 `full_report=True` 原始报告, 但正式 pass/fail 只按冻结列重算, 不把完整报告里所有布尔列都当 gate.
- PoseBusters timeout 冻结为 inner `300s`, outer `420s`. timeout 只记录为 `not_evaluable_tool_failure` 或 `tool_failure.timeout`.
- PLIP 冻结输入为 cleaned receptor + generated ligand 合成的单配体 complex PDB, interaction fingerprint 使用 residue-level key.
- PLIP reference interaction recovery 在 v0.1 中只作为 reference-relative 描述性证据, 默认不单独触发 `interaction_or_contact_loss` 硬失败标签. 只有在任务级 protocol 明确冻结 `required_interactions` 清单时, 才允许升级为硬标签.
- Vina 只作为辅助 metric, 只报告 `score_only` 分数和相关准备状态, 不作为唯一 success gate, v0.1 不设置 Vina 分数阈值.
- Vina box 在正式分析中必须按 reference ligand 或 dataset/pocket 固定定义. 不允许用 generated ligand centroid 作为正式 fallback.
- `mol_pred_loaded=false` 归为 `not_evaluable_format_error`. evidence 中保留 `posebusters_mol_pred_load_failed` 或 `rdkit_parse_failed`, 但不进入可评价分子的正式分子失败率.
- `protein-ligand_maximum_distance=false` 归为 `pocket_detachment`, secondary label 使用 `ligand_outside_pocket`.
- ProLIF 不进入第一版 `analysis-frozen` gate. 待第一版主流水线稳定后作为 P1 pilot 接入, 使用单独 evaluator pilot 环境, 不污染 `pfr-eval-tools`.
- Arpeggio 暂缓接入. 后续如需要原子级 contact 复核, 再作为 P2 pilot 评估 mmCIF 转换和 ligand selection 成本.
- 分母视图冻结为 `inclusive_failure_burden`, `evaluable_only_molecular_prevalence`, `selected_output_residual_prevalence`. `samples.jsonl` 是主分母来源, 不能按 SDF 文件数倒推.

## 正式失败率禁止条件

任一条件命中时, 均禁止声明正式 failure prevalence 或正式失败分布:

- `analysis-frozen` gate 未通过.
- receptor prep policy, evaluator policy, diagnosis label config, denominator config 或 tool versions lock 未冻结, 未记录 hash, 或 hash 未传播到 run metadata / labels.
- `review_required_hetero_atoms` 存在 unresolved 项.
- `samples.jsonl` 缺少主分母行, 或 `N_budget`, `N_raw_attempt_metadata` 不能回溯到 sample metadata.
- evaluator 未使用 cleaned receptor 派生输入, 仍直接使用 raw receptor.
- PoseBusters 仍使用旧 `full_report=True` 全布尔列 `full_pass` 作为正式 gate.
- Vina box 使用 generated ligand centroid 或其他样本依赖 fallback.
- frozen evaluator sanity set 未运行或未通过.
- tool versions lock 缺少 RDKit, PoseBusters, PLIP, Vina, Meeko, OpenBabel 和 wrapper 脚本版本 / hash.
- DiffSBDD checkpoint 训练数据和测试数据重叠状态未冻结时, 禁止声明 clean generalization 或 clean-test 结论.

gate 通过后也只能声明: 在指定 method, checkpoint, dataset view, seed, sample budget, receptor prep policy, evaluator policy 和 diagnosis label config 下观察到的失败证据分布. 不能外推为 DiffSBDD 全局失败率, 官方协议完整复现, clean-test 结论或 repair benchmark result.

## 冻结产物和 hash 传播

v0.1 正式运行前, 以下配置和版本文件必须冻结, 计算 hash, 并写入 run metadata, labels, summaries 和 gate result:

| 产物 | 建议路径 | 必须记录 |
|---|---|---|
| receptor prep policy | `configs/audit/receptor_prep_policy_v0_1.yaml` | `receptor_prep_policy_version`, `receptor_prep_policy_hash` |
| evaluator policy | `configs/audit/evaluator_policy_v0_1.yaml` | `evaluator_policy_version`, `evaluator_policy_hash` |
| diagnosis label config | `configs/audit/diagnosis_label_config_v0_2.yaml` | `label_protocol_version`, `label_config_hash` |
| denominator config | `configs/audit/denominator_statistics_schema_v0_1.yaml` | `denominator_policy_version`, `denominator_policy_hash` |
| analysis-frozen gate config | `configs/audit/analysis_frozen_gate_v0_1.yaml` | `analysis_frozen_gate_version`, `analysis_frozen_gate_hash` |
| tool versions lock | `configs/audit/tool_versions.lock` | `tool_versions_lock_version`, `tool_versions_lock_hash` |

`tool_versions.lock` 必须补齐:

- RDKit Python package version.
- PoseBusters version.
- PLIP version and CLI path.
- Vina version and CLI path.
- Meeko version, `mk_prepare_ligand.py` path, `mk_prepare_receptor.py` path.
- OpenBabel CLI / Python version.
- evaluator wrapper script git commit 或 script sha256.

## Receptor Preparation 设计

### 文件组织

采用“一个 cleaned receptor PDB 跟一个同名 JSON”的结构:

```text
outputs/<experiment_id>/<method>/<run_id>/processed/receptors/
  3rfm_A_330_CFF_cleaned_receptor.pdb
  3rfm_A_330_CFF_receptor_prep.json
  receptor_prep_index.json
```

其中 `receptor_prep_index.json` 是可选轻量索引, 用于列出当前 run 下有哪些 receptor prep record. 每个样本通过 `receptor_prep_id` 引用对应 receptor prep record, 不给每个样本单独复制 receptor metadata.

### 单个 receptor prep JSON 内容

每个 `*_receptor_prep.json` 记录旁边这个 cleaned receptor PDB 的来源和处理动作:

```json
{
  "schema_version": "receptor_prep_record_v0_1",
  "schema_path": "schemas/third_party_audit/receptor/receptor_prep_record_v0_1.json",
  "receptor_prep_id": "3rfm_A_330_CFF_pfr_receptor_prep_v0_1",
  "case_id": "3rfm",
  "receptor_prep_policy_version": "pfr_receptor_prep_v0_1",
  "receptor_prep_policy_hash": "sha256:...",
  "raw_receptor_path": "third_party/diffsbdd/example/3rfm.pdb",
  "raw_receptor_sha256": "sha256:...",
  "raw_atom_count": 1234,
  "raw_hetero_group_count": 1,
  "cleaned_receptor_path": "processed/receptors/3rfm_A_330_CFF_cleaned_receptor.pdb",
  "cleaned_receptor_sha256": "sha256:...",
  "cleaned_atom_count": 1220,
  "cleaned_hetero_group_count": 0,
  "reference_ligand": {
    "residue_name": "CFF",
    "chain_id": "A",
    "residue_number": 330,
    "insertion_code": "",
    "altloc": "",
    "role": "removed_reference_ligand",
    "heavy_atom_count": 14,
    "centroid_angstrom": [1.0, 2.0, 3.0],
    "bounding_box_span_angstrom": [4.0, 5.0, 3.5],
    "source_path": "third_party/diffsbdd/example/3rfm.pdb"
  },
  "pocket_box": {
    "box_policy_version": "pfr_vina_box_v0_1",
    "box_source": "reference_ligand_heavy_atom_centroid",
    "center_angstrom": [1.0, 2.0, 3.0],
    "size_angstrom": [12.0, 13.0, 12.0],
    "padding_angstrom": 8.0,
    "minimum_size_angstrom": 12.0,
    "atom_selection": "reference_ligand_heavy_atoms",
    "generated_ligand_centroid_fallback_used": false
  },
  "removed_hetero_atoms": [],
  "retained_hetero_atoms": [],
  "review_required_hetero_atoms": [
    {
      "residue_name": "ABC",
      "chain_id": "A",
      "residue_number": 201,
      "insertion_code": "",
      "altloc": "",
      "atom_count": 12,
      "heavy_atom_count": 12,
      "elements": ["C", "N", "O"],
      "min_distance_to_reference_ligand_angstrom": 4.2,
      "classification": "unknown_hetero_near_pocket",
      "action": "review_required",
      "reason": "unknown HETATM within 8.0 A of reference ligand",
      "rule_id": "unknown_hetero_near_reference_ligand_v0_1",
      "decision_status": "unresolved",
      "decision": null,
      "decision_reason": null,
      "reviewed_by": null,
      "review_time": null,
      "action_applied": false,
      "whitelist_update": null
    }
  ],
  "unresolved_review_required_count": 1,
  "warnings": []
}
```

示例中的 `sha256:...` 和坐标只表示字段形状. 真实输出不得保留占位值, `unresolved_review_required_count` 必须为 `0` 才能进入正式分析.

### Cleaned Receptor 不变量

每个 cleaned receptor 必须满足:

- 不包含 reference ligand.
- 不包含 unresolved `review_required_hetero_atoms`.
- 记录 raw receptor 和 cleaned receptor 的 sha256, atom count, hetero group count.
- 每个 evaluator 输入必须引用 `receptor_prep_id` 和 `cleaned_receptor_path`.
- PoseBusters, PLIP, Vina 和后续 ProLIF / Arpeggio 不得直接使用 raw receptor 作为正式输入.
- `pocket_box.generated_ligand_centroid_fallback_used` 必须为 `false`.
- 如果 fixed pocket center / box 来自 dataset 而不是 reference ligand, 必须记录 `box_source`, `dataset_view_id` 和来源文件 hash.

### 清理规则

初版 receptor preparation 采用保守规则:

- 必须删除 reference ligand. 例如 3RFM 的 `CFF A:330` 是咖啡因配体, 用于定义口袋, 评估新分子时不能继续占位.
- 默认删除普通水, 例如 `HOH`, `WAT`, `DOD`, 除非某个 protocol 明确要研究桥联水.
- 默认删除常见结晶添加剂, 缓冲液, 游离小分子和离口袋很远的非蛋白组分.
- 默认保留关键金属和明确功能辅因子, 例如 `ZN`, `MG`, `FE`, `MN`, `CA`, `HEM`, `FAD`, `FMN`, `NAD`, `SAM`, `COA`.
- 第一版 metal / cofactor whitelist 采用小集合起步. 后续遇到新 residue 时, 不靠人工记忆补白名单, 而是先进入复核流程. 若复核决定为 `retain_and_add_to_whitelist`, 再扩展中央白名单.
- 对口袋附近但无法自动判断是否相关的 HETATM, 写入 `review_required_hetero_atoms`. 口袋附近阈值冻结为 `8.0 A`.
- `review_required_hetero_atoms` 必须有明确 decision, 例如 `remove`, `retain_once`, `retain_and_add_to_whitelist`, `block`. 正式分析前不能存在 unresolved 项.
- 若某个失败只由保留或待复核的 HETATM 触发, 标签应标记 `receptor_prep_sensitive`, 不能直接归咎于模型.

这里的 HETATM 不是“必须删除”的同义词. 它只是 PDB 中非标准蛋白或核酸原子记录, 可能是配体, 水, 金属, 辅因子, 缓冲液或结晶添加剂.

### HETATM 复核和白名单更新

`removed_hetero_atoms`, `retained_hetero_atoms`, `review_required_hetero_atoms` 中每个 group 至少记录:

```text
residue_name
chain_id
residue_number
insertion_code
altloc
atom_count
heavy_atom_count
elements
min_distance_to_reference_ligand_angstrom
classification
action
reason
rule_id
```

`review_required_hetero_atoms` 还必须记录:

```text
decision_status
decision
decision_reason
reviewed_by
review_time
action_applied
whitelist_update
```

允许的 `decision` 为:

```text
remove
retain_once
retain_and_add_to_whitelist
block
```

只有 `decision=retain_and_add_to_whitelist` 时才允许扩展中央白名单. 中央 receptor prep policy 至少包含 retained metals, retained cofactors, water residue names, common additive denylist, unknown HETATM review distance 和 rule ids.

## 工具适配口径

### Evaluator 输入合同

正式 evaluator 每个样本至少需要:

```text
sample_id
method
run_id
stage
sample_role
molecule_path
receptor_prep_id
cleaned_receptor_path
reference_ligand_record
pocket_box
receptor_prep_policy_version
receptor_prep_policy_hash
evaluator_policy_version
evaluator_policy_hash
label_protocol_version
label_config_hash
tool_versions_lock_hash
```

如果缺少 `molecule_path`, `receptor_prep_id`, `cleaned_receptor_path` 或 `pocket_box`, 该样本不得静默过滤, 必须进入对应 `not_evaluable_*` 或 blocking gate failure.

### RDKit

RDKit v0.1 负责生成配体的基础可读性和化学合法性检查:

- 输入为单个 generated ligand SDF 路径.
- 读取使用 `Chem.SDMolSupplier(path, sanitize=False, removeHs=False)`.
- 若文件缺失, 记录 `not_evaluable_missing_data`, primary label 为 `missing_data`.
- 若 SDF 为空, RDKit 无法 parse, 或没有任何可用 molecule, 记录 `not_evaluable_format_error`, secondary label 为 `rdkit_parse_failed`.
- 若 SDF 含多个 molecule, 第一版正式评估只接受已经拆分后的单分子 SDF. 多分子 SDF 进入 `not_evaluable_format_error`, 除非 upstream normalization 已明确生成单分子条目.
- 若 molecule 没有 3D conformer, 记录 `not_evaluable_format_error`, secondary label 为 `missing_3d_conformer`.
- parse 后显式运行 `Chem.SanitizeMol`. sanitize 失败时, evaluability 可为 `evaluable`, primary label 为 `chemical_invalid`, secondary label 为 `rdkit_sanitize_failed` 或更具体的 valence evidence.
- RDKit pass 只表示基础可读和化学 sanitize 通过, 不代表 pose 正确或 protein-ligand interaction 合理.

### PoseBusters

PoseBusters 应冻结为两层:

```text
posebusters_ligand_core
posebusters_pocket_core
```

`posebusters_ligand_core` 使用:

```text
config = mol
mol_pred = generated ligand SDF
mol_true = null
mol_cond = null
```

正式列只使用 PoseBusters `mol` 配置中的 chosen binary columns:

```text
mol_pred_loaded
sanitization
inchi_convertible
all_atoms_connected
no_radicals
bond_lengths
bond_angles
internal_steric_clash
aromatic_ring_flatness
non-aromatic_ring_non-flatness
double_bond_flatness
internal_energy
```

`posebusters_pocket_core` 使用:

```text
config = dock
mol_pred = generated ligand SDF
mol_cond = cleaned receptor PDB
mol_true = null
```

优先解释的主列:

```text
mol_pred_loaded
mol_cond_loaded
protein-ligand_maximum_distance
minimum_distance_to_protein
volume_overlap_with_protein
```

cofactor 和 water 相关列先作为 receptor preparation 敏感证据:

```text
minimum_distance_to_organic_cofactors
minimum_distance_to_inorganic_cofactors
minimum_distance_to_waters
volume_overlap_with_organic_cofactors
volume_overlap_with_inorganic_cofactors
volume_overlap_with_waters
```

PoseBusters 可以保存 `full_report=True` 的完整原始报告, 但正式 pass/fail 只看冻结列. 不应把完整报告中的所有布尔列都纳入 `full_pass`. 当前 DiffSBDD 生成任务也不应把 `redock` 的 `mol_true_loaded`, molecular identity 或 RMSD 作为主失败标签.

建议冻结运行方式:

- conda env: `pfr-eval-tools`.
- PoseBusters: `0.6.5`.
- `max_workers=0`.
- 每个样本每个 config 单独运行.
- `inner_timeout_seconds=300`.
- `outer_timeout_seconds=420`.
- timeout 记录为 `not_evaluable_tool_failure` 或 `tool_failure.timeout`, 不映射为化学或几何失败.

正式输出字段至少包括:

```text
posebusters_ligand_core_pass
posebusters_pocket_core_pass
posebusters_ligand_core_checked_columns
posebusters_pocket_core_checked_columns
posebusters_ligand_core_failed_columns
posebusters_pocket_core_failed_columns
posebusters_full_report_path
posebusters_missing_frozen_columns
posebusters_timeout_seconds
```

如果 frozen column 在工具输出中缺失, 不得默认当作 pass. 应记录 `tool_failure` 或 gate blocking failure, 并保留原始报告用于排查. 旧脚本默认 `redock`, `60s timeout` 或 `full_report` 全布尔列 `full_pass` 的输出不能进入正式 analysis-frozen.

版本化补充: 后续发现 PoseBusters `internal_energy` 可能在原始 full report 列存在但值为 `NaN`, 这不同于 frozen column 真缺失. v0.1 保持保守解释不变. v0.2 计划将 `internal_energy` 改为 conditional column, 详见 `docs/plan/20260609-01-posebusters-internal-energy-conditional-gate-plan.md`.

### PLIP

PLIP v0.1 使用同一份 cleaned receptor 与 generated ligand 组成单配体 complex PDB. 冻结输入和命令为:

```text
cleaned receptor PDB + generated ligand SDF -> complex PDB
plip -f <complex.pdb> -o <out_dir> -x -q --maxthreads 1 --name <sample_id>
```

interaction fingerprint key 冻结为 residue-level key:

```text
interaction_type|reschain|resnr|restype
```

第一版 core interaction 类型为:

```text
hydrogen_bond
salt_bridge
pi_stack
pi_cation_interaction
halogen_bond
metal_complex
```

`hydrophobic_interaction` 和 `water_bridge` 先作为辅助证据. 其中 `water_bridge` 强依赖 receptor preparation 是否保留水, 第一版不作为硬 gate.

PLIP reference interaction recovery 在 v0.1 中冻结为 reference-relative 描述性证据:

- 默认记录 recovered, lost, new interactions, recovery 和 similarity 等指标.
- 默认不因为 recovery 低于某个阈值就单独触发 `interaction_or_contact_loss`.
- 若 PLIP 显示生成分子几乎没有合理 protein-ligand contact, 可作为可疑信号写入 evidence, 但需要结合 PoseBusters pocket check, pocket distance, clash, receptor preparation 等证据再判.
- 只有当任务级 protocol 明确冻结 `required_interactions` 清单时, PLIP recovery 才能升级为硬失败标签.

这个规则适用于一般 pocket-conditioned generation 和 de novo generation. 对 fragment growing, scaffold repair 或明确要求保留关键相互作用的任务, 需要单独冻结 required interactions policy.

complex PDB 构建规则:

- `generated_complex_pdb = cleaned receptor + generated ligand`.
- `reference_complex_pdb = cleaned receptor + reference ligand`.
- 两者都必须是单配体 complex.
- generated ligand 建议使用固定 residue name, chain id 和 residue number, 例如 `LIG Z:1`, 并记录在 evaluator output.
- reference ligand 从 raw receptor 或 reference ligand record 提取, 但合成 reference complex 时必须使用 cleaned receptor, 不能使用 raw receptor.
- 如果 PLIP 自动识别出多个 ligand, 该 PLIP 结果不能进入 analysis-frozen, 必须标记为 tool/input contract failure.
- reference fingerprint 和 generated fingerprint 都使用同一套 residue-level key.

### Vina 和 Meeko

Vina 使用从 cleaned receptor 派生的 receptor PDBQT, 以及从 generated ligand SDF 派生的 ligand PDBQT.

冻结原则:

- Vina 当前只做 `score_only` 辅助 metric.
- Vina 分数不能作为唯一 success gate.
- Meeko 的 ligand / receptor preparation 参数必须记录.
- PDBQT 转换失败应区分为 tool failure, format error 或 ligand preparation failure.
- box center 使用 raw receptor 中 reference ligand 的重原子 centroid, 并在删除 reference ligand 前计算和写入 receptor prep JSON.
- box size 使用 reference ligand 重原子 bounding box, 每个维度 `max(12.0, span + 8.0)` A.
- 没有 reference ligand 时, 只能使用 dataset / pocket 提供的固定 center 和 box. 如果也没有固定 pocket 定义, 该 case 不能通过 `analysis-frozen` gate.
- generated ligand centroid + `20 A` cube 只能作为 sanity fallback, 不能进入正式冻结分析.
- Meeko `--charge_model zero` retry 可以记录为 fallback, 但对应 Vina score 应标记为 non-comparable.

正式输出字段至少包括:

```text
box_definition_source
vina_box_center_angstrom
vina_box_size_angstrom
vina_score_only_energy
vina_score_parse_status
vina_score_comparability
charge_model_retry_used
ligand_pdbqt_path
ligand_pdbqt_sha256
receptor_pdbqt_path
receptor_pdbqt_sha256
meeko_ligand_prepare_status
meeko_receptor_prepare_status
vina_command_status
```

错误分类:

- CLI 缺失, import error, wrapper nonzero, timeout, Vina score parse failure: `not_evaluable_tool_failure`, primary label `tool_failure`.
- ligand 文件缺失: `not_evaluable_missing_data`, primary label `missing_data`.
- SDF 无法 parse, 无 3D conformer, 显式氢写入失败, Meeko ligand prepare 失败: `not_evaluable_format_error`, secondary label `vina_ligand_prepare_failed` 或更具体 evidence.
- Meeko receptor prepare 失败: 若 cleaned receptor 或 HETATM 决策导致, 标记 `receptor_prep_sensitive`; 若 CLI / env 导致, 标记 `tool_failure`.
- `--charge_model zero` retry 后可以保留 score, 但 `vina_score_comparability` 必须为 `non_comparable`.

### ProLIF

ProLIF 暂不进入第一版主 gate. 待第一版 RDKit + PoseBusters + PLIP + Vina 辅助分数流水线稳定并通过 `analysis-frozen` gate 后, 可作为 P1 pilot 接入, 用于补充 PLIP 的 interaction fingerprint / contact recovery. ProLIF pilot 应使用单独 evaluator pilot 环境, 不污染 `pfr-eval-tools`. 接入前需要冻结:

- receptor / complex 输入对象构建规则.
- residue selection.
- interaction 类型.
- cutoff.
- count vector 或 bit vector.
- fingerprint similarity / recovery 口径.

ProLIF 不应替代 RDKit 或 PoseBusters 的化学和几何检查.

### Arpeggio

Arpeggio 暂不进入第一版主 gate. 当前暂缓接入. 后续如需要原子级 contact 复核, 可作为 P2 小规模 pilot, 用于更细的 interatomic contact evidence. 接入前需要确认:

- cleaned complex 到 mmCIF 的转换规则.
- ligand selection.
- altloc 和 missing density 风险.
- license 和依赖边界.

Arpeggio 不应在第一版冻结流水线中作为主 gate.

## 标签映射原则

正式标签应由冻结后的 evaluator policy 和 diagnosis label config 生成. `diagnosis_label_config_v0_2.yaml` 至少需要覆盖下表:

| 工具 / 证据 | evaluability_status | primary_label | secondary_labels / evidence |
|---|---|---|---|
| ligand 文件缺失 | `not_evaluable_missing_data` | `missing_data` | `missing_molecule_path` |
| RDKit parse 失败, 空 SDF, 多分子 SDF 未拆分, 无 3D conformer | `not_evaluable_format_error` | `unknown` | `rdkit_parse_failed`, `missing_3d_conformer` |
| RDKit sanitize 失败 | `evaluable` | `chemical_invalid` | `rdkit_sanitize_failed`, `valence_error` |
| PoseBusters import error, timeout, wrapper nonzero exit, frozen column 缺失 | `not_evaluable_tool_failure` | `tool_failure` | `tool_failure.timeout`, `posebusters_frozen_column_missing` |
| `mol_pred_loaded=false` | `not_evaluable_format_error` | `unknown` | `posebusters_mol_pred_load_failed` |
| `sanitization`, `inchi_convertible`, `all_atoms_connected`, `no_radicals` 失败 | `evaluable` | `chemical_invalid` | `rdkit_sanitize_failed`, `disconnected_graph` |
| `bond_lengths`, `bond_angles`, `internal_steric_clash`, flatness, `internal_energy` 失败 | `evaluable` | `local_geometry_failure` | `posebusters_geometry_failed`, `internal_clash` |
| `protein-ligand_maximum_distance` 失败 | `evaluable` | `pocket_detachment` | `ligand_outside_pocket` |
| `minimum_distance_to_protein`, `volume_overlap_with_protein` 失败 | `evaluable` | `protein_ligand_clash` | `protein_ligand_clash` |
| PoseBusters cofactor / water 相关失败 | `evaluable` 或 `not_evaluable_unknown` 取决于主证据 | 不直接作为模型失败 | `receptor_prep_sensitive` |
| PLIP 单配体 contract 失败或 XML 缺失 | `not_evaluable_tool_failure` | `tool_failure` | `plip_complex_contract_failed`, `plip_xml_missing` |
| PLIP reference interaction recovery 低 | `evaluable` | 不单独触发 primary label | evidence: `plip_reference_relative_recovery` |
| Vina / Meeko CLI 缺失, wrapper nonzero, timeout, score parse 失败 | `not_evaluable_tool_failure` | `tool_failure` | `vina_score_failed`, `vina_score_parse_failed` |
| Meeko ligand prepare 失败 | `not_evaluable_format_error` | `unknown` | `vina_ligand_prepare_failed` |
| Meeko receptor prepare 失败且与 receptor prep 有关 | `not_evaluable_tool_failure` 或 `evaluable` 按主证据 | 不直接作为模型失败 | `receptor_prep_sensitive`, `vina_receptor_prepare_failed` |
| `--charge_model zero` retry used | `evaluable` | 不触发 primary label | `vina_score_non_comparable` |
| receptor prep unresolved | `not_evaluable_unknown` | `unknown` 或 gate blocking failure | `receptor_prep_unresolved` |

如果某个样本缺少 required input, 工具失败或 receptor prep 未完成, 应进入 `not_evaluable_*` 状态, 而不是从分母中删除. `diagnosis_label_config_v0_2.yaml` 应统一 secondary label 命名, 推荐使用 `posebusters_geometry_failed`, 不再使用单数形式 `posebuster_geometry_failed`.

## 分母和样本记录

`samples.jsonl` 仍是 run 的主分母来源. 规则:

- 每个 generation attempt 至少有一行 sample metadata.
- 即使没有合法 SDF, 也不能丢 sample metadata 行.
- `stage_attrition.json` 的计数必须能回溯到 `samples.jsonl`.
- 每个样本应引用 `receptor_prep_id`.
- `labels.jsonl` 每一行应记录 `label_protocol_version`, `label_config_hash`, evaluator evidence 和 evaluability status.
- raw prevalence 必须有 `N_budget` 和 `N_raw_attempt_metadata`; 否则只能做 selected / final residual audit.

正式版 `samples.jsonl` 每行至少新增或显式保留:

```text
receptor_prep_id
receptor_prep_policy_version
receptor_prep_policy_hash
cleaned_receptor_path
pocket_box
evaluator_policy_version
evaluator_policy_hash
denominator_policy_version
denominator_policy_hash
```

正式版 `labels.jsonl` 每行至少新增或显式保留:

```text
receptor_prep_id
receptor_prep_policy_version
receptor_prep_policy_hash
evaluator_policy_version
evaluator_policy_hash
label_protocol_version
label_config_hash
tool_versions_lock_hash
evidence
tool_results
adjudication_status
```

`output_manifest.json` 必须登记所有项目自有输出和关键外部工具输出, 至少包括 receptor prep JSON, cleaned receptor PDB, evaluator results, raw tool outputs, labels, summaries, gate result, env_info, conda export, pip freeze, config copies 和 tables. 每个 artifact 应记录 path, sha256, artifact role, producer step, schema refs, policy hash refs.

建议 run 输出结构:

```text
outputs/<experiment_id>/<method>/<run_id>/
  run_metadata.json
  samples.jsonl
  output_manifest.json
  stage_attrition.json
  processed/
    receptors/
      *_cleaned_receptor.pdb
      *_receptor_prep.json
      receptor_prep_index.json
    normalized_samples/
  evaluator/
    evaluator_tool_results.jsonl
    raw_tool_outputs/
  labels/
    labels.jsonl
  summaries/
    label_summary.json
    prevalence_summary.json
  tables/
    failure_distribution.tsv
    failure_cooccurrence.tsv
    repairable_near_miss_candidates.tsv
```

## 需要新增或升级的配置和 schema

建议新增项目级配置:

```text
configs/audit/receptor_prep_policy_v0_1.yaml
configs/audit/evaluator_policy_v0_1.yaml
configs/audit/analysis_frozen_gate_v0_1.yaml
```

建议升级:

```text
configs/audit/diagnosis_label_config_v0_2.yaml
configs/audit/tool_versions.lock
```

建议新增 schema:

```text
schemas/configs/audit/receptor_prep_policy_config_v0_1.json
schemas/configs/audit/evaluator_policy_config_v0_1.json
schemas/configs/audit/analysis_frozen_gate_config_v0_1.json
schemas/third_party_audit/receptor/receptor_prep_record_v0_1.json
schemas/third_party_audit/receptor/receptor_prep_index_v0_1.json
schemas/third_party_audit/diagnosis/label_summary_v0_1.json
schemas/third_party_audit/diagnosis/prevalence_summary_v0_1.json
schemas/third_party_audit/diagnosis/analysis_frozen_gate_result_v0_1.json
```

新增或升级后应同步更新:

- `schemas/README.md`
- `configs/README.md`

新增配置 / schema 的最低字段要求:

| 文件 | 最低字段 |
|---|---|
| `receptor_prep_policy_v0_1.yaml` | policy version, retained metals, retained cofactors, water names, additive denylist, unknown HETATM review distance, decision enum, rule ids |
| `evaluator_policy_v0_1.yaml` | evaluator policy version, RDKit rules, PoseBusters configs and frozen columns, PLIP command and fingerprint key, Vina box policy, timeout policy, tool error mapping |
| `analysis_frozen_gate_v0_1.yaml` | blocking checks, warning checks, required artifacts, required hashes, sanity set definitions, claim boundary |
| `diagnosis_label_config_v0_2.yaml` | evaluability statuses, primary labels, secondary labels, precedence hierarchy, frozen tool evidence mapping, near-miss eligibility |
| `receptor_prep_record_v0_1.json` | receptor identity, raw/cleaned paths and hashes, atom counts, reference ligand record, pocket_box, hetero group records, unresolved count |
| `analysis_frozen_gate_result_v0_1.json` | gate status, blocking failures, warnings, checked inputs, config hashes, tool versions lock hash, sanity set results, claim boundary |

## 建议脚本拆分

建议逐步增加统一脚本:

```text
scripts/eval/prepare_receptor.py
scripts/eval/run_audit_evaluators.py
scripts/eval/build_audit_labels.py
scripts/eval/summarize_audit_labels.py
scripts/eval/check_analysis_frozen_gate.py
```

其中:

- `prepare_receptor.py` 负责生成 cleaned receptor PDB 和同名 receptor prep JSON.
- `run_audit_evaluators.py` 负责统一调度 RDKit, PoseBusters, PLIP, Vina 等工具.
- `build_audit_labels.py` 负责从工具 evidence 生成 frozen labels.
- `summarize_audit_labels.py` 负责生成 label summary, prevalence summary 和表格.
- `check_analysis_frozen_gate.py` 负责检查 schema refs, config hash, tool versions, denominator 和 sanity set.

## Analysis-Frozen Gate

进入正式失败分布统计前, gate 至少要求:

- receptor prep policy 已冻结.
- evaluator policy 已冻结.
- diagnosis label config 已冻结并计算 `label_config_hash`.
- tool versions lock 记录 PoseBusters, RDKit, PLIP, Vina, Meeko, OpenBabel 等版本和命令路径.
- PoseBusters `mol` 和 `dock` 的正式列已冻结.
- RDKit parse / sanitize 规则已冻结.
- PLIP interaction fingerprint 已冻结, 且 reference interaction recovery 默认只作为描述性证据. 若任务需要硬标签, 必须先冻结 `required_interactions` 清单.
- Vina 明确为辅助 metric.
- `samples.jsonl` 行数与 `N_raw_attempt_metadata` 一致.
- 缺失输出, 工具失败, 格式失败和 pipeline failure 不被静默过滤.
- `review_required_hetero_atoms` 没有 unresolved 项.
- 同一 receptor / pocket 下的 Vina box center 和 box size 跨样本一致.
- sanity set 覆盖 missing data, pipeline failure, tool failure, format error, original failed sample, valid final output, Meeko ligand prepare failure, Meeko receptor prepare failure 或 receptor prep sensitive, Vina pass 不能覆盖其他失败证据, 以及只有 final outputs 时自动降级为 selected/final residual view.
- gate report 明确 claim boundary.

`analysis_frozen_gate_result.json` 至少包含:

```text
schema_version
schema_path
gate_status
blocking_failures
warnings
checked_inputs
config_hashes
tool_versions_lock_hash
required_artifacts_present
sanity_set_results
claim_boundary
created_time
```

blocking checks 至少包括:

- 缺少 `receptor_prep_id` 或 `cleaned_receptor_path`.
- evaluator 输入直接使用 raw receptor.
- `review_required_hetero_atoms` 存在 unresolved 项.
- Vina box 来源为 generated ligand centroid.
- PoseBusters 仍使用旧 `full_report` 全布尔列 `full_pass` 作为正式 gate.
- tool versions lock hash 缺失或版本字段不完整.
- label config hash, evaluator policy hash, receptor prep policy hash 缺失.
- `samples.jsonl` 行数与 `N_raw_attempt_metadata` 不一致.
- output manifest 缺少 required artifacts 或 sha256.

warning checks 至少包括:

- Meeko `--charge_model zero` retry used, Vina score marked non-comparable.
- PLIP reference interaction recovery low, 但未冻结 required interactions.
- 训练数据 / 泄漏状态未知时, claim boundary 必须保持受限.

sanity set 期望输出:

| case | 输入构造 | 期望状态 | gate 检查点 |
|---|---|---|---|
| valid final output | 合法单分子 SDF + cleaned receptor | `evaluable` | RDKit, PoseBusters frozen columns, PLIP/Vina outputs 可记录 |
| missing ligand | sample metadata 存在, ligand path 缺失 | `not_evaluable_missing_data` | sample row 不丢, 分母保留 |
| broken SDF | 文件存在但 RDKit 读不出 molecule | `not_evaluable_format_error` | 不进入 evaluable-only molecular prevalence |
| pipeline failure | method run 或 sample capture 失败 | `not_evaluable_pipeline_failure` | denominator row 和 failure reason 保留 |
| tool timeout | mock 或真实工具 timeout | `not_evaluable_tool_failure` | timeout 不映射为化学/几何失败 |
| Meeko ligand prepare failure | ligand PDBQT 转换失败 | `not_evaluable_format_error` | 记录 `vina_ligand_prepare_failed` |
| Meeko receptor prepare failure | receptor PDBQT 转换失败 | tool failure 或 `receptor_prep_sensitive` | 不直接归咎模型 |
| unresolved HETATM | receptor prep JSON 有 unresolved review item | gate blocking failure | 禁止正式 prevalence |
| generated centroid Vina box | Vina box 来自 generated ligand centroid | gate blocking failure | 禁止正式 prevalence |
| Vina pass trap | Vina score 存在但 PoseBusters/PLIP 有失败证据 | 保留多工具 evidence | Vina pass 不覆盖其他失败 |
| original failed/rejected sample | sample_role 为 original_failed_sample 或 rejected_candidate | 保留行 | 不被过滤出分母 |
| final-only outputs | 只有 final outputs, 无 raw attempts | 降级为 selected/final residual view | 不声明 raw failure distribution |

## 执行顺序

建议按以下顺序落地:

1. 新增 receptor prep policy 和 receptor prep record schema.
2. 新增 evaluator policy, analysis-frozen gate config 和 diagnosis label config v0.2.
3. 补齐 tool versions lock, 计算 receptor prep policy, evaluator policy, label config, denominator config, gate config 和 tool versions lock hash.
4. 实现 `prepare_receptor.py`, 先对 3RFM 生成 cleaned receptor 和同名 JSON.
5. 将 PoseBusters, PLIP 和 Vina 输入改为统一 cleaned receptor 派生输入.
6. 用 DiffSBDD 阶段 1 的 20 个样本重跑或补算 frozen-style evaluator summary.
7. 新增 `labels.jsonl` 生成逻辑, 不直接复用旧 `diagnosis_sanity.jsonl` 作为正式标签.
8. 运行 analysis-frozen sanity set 并生成 gate result JSON.
9. 生成 `docs/report/YYYYMMDD-<num>-unified-evaluation-pipeline-alignment-report.md`, 说明已实现内容, 生成文件, sanity set 结果, gate 结果, blocker, 尚未接入工具, 以及是否允许进入更大样本 DiffSBDD audit. 该报告是人工可读的阶段报告, 不替代流水线内部的 `analysis_frozen_gate_result.json`.
10. 追加 `docs/EXPERIMENT_LOG.md`, 必要时更新 `docs/STATUS.md`.
11. gate 通过后再进入 DiffSBDD 更大样本审计.

## 完成产物

本计划执行结束后, 至少应形成以下收尾产物:

- `analysis_frozen_gate_result.json`: 机器可读的 gate 检查结果, 用于判断是否允许进入正式失败分布统计.
- `docs/report/YYYYMMDD-<num>-unified-evaluation-pipeline-alignment-report.md`: 人工可读的阶段报告, 总结本轮统一评估流水线对齐和冻结落地情况.
- `docs/EXPERIMENT_LOG.md`: 追加记录本轮实施过程, 输出位置, blocker, gate 结果和下一步.
- `docs/STATUS.md`: 仅当本轮实施改变项目当前关键状态时更新, 例如 gate 已通过, 主评估流水线已冻结, 或进入更大样本 DiffSBDD audit.

## 结论边界

在本计划落地并通过 analysis-frozen gate 前, 可以声明:

- 统一评估流水线的设计口径.
- 哪些工具已接入, 哪些工具待接入.
- 哪些冻结项尚未完成.
- 某些 sanity 样本可以证明工具接通.

不应声明:

- DiffSBDD 正式失败率.
- failure prevalence.
- repair benchmark result.
- PoseBusters 当前全列 `full_pass` 对应正式方法失败.
- PLIP, Vina 或 ProLIF 单一工具能独立证明样本成功.
- 在训练数据和测试数据重叠状态未冻结前, 不声明 clean generalization 或 clean-test 结论.
- 在官方 processed test data, split, checksum, license 和 resource gate 未冻结前, 不把 `test.py` 官方风格子集与本项目 audit protocol 扩大样本混成同一个正式结论.

## 后续实施问题

当前 v0.1 规则口径的用户拍板项已收敛. 后续实施重点是把上述规则落成配置、schema、脚本和 `analysis-frozen` gate:

- 新增或升级 receptor prep policy, evaluator policy, diagnosis label config 和 analysis-frozen gate config.
- 实现 cleaned receptor 生成和同名 receptor prep JSON.
- 将 PoseBusters, PLIP 和 Vina 输入切换到 cleaned receptor 派生输入.
- 实现 `not_evaluable_format_error`, `pocket_detachment`, `receptor_prep_sensitive` 等冻结标签映射.
- 构造并运行 analysis-frozen sanity set.
- 区分两个后续入口: `test.py` 官方风格子集 resource/data gate, 以及本项目 audit protocol 下的 DiffSBDD 扩大样本审计. 两者不能混成同一个正式结论.
