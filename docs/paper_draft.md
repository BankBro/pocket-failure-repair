# Failure-Feedback-Conditioned Repair for Pocket-Aware 3D Local Molecular Editing

> BIBM-style working draft. This draft is intentionally conservative: current evidence includes a first-round literature collision check, a validated RDKit-first smoke environment, public RCSB smoke samples, and RDKit-backed file-level pipeline outputs, but not yet a trained repair model or repaired-molecule performance evidence.

## Abstract

Pocket-aware 3D molecular generation has made progress in scaffold decoration, fragment growth, linker design, and structure-based molecule optimization. However, many workflows still rely on one-shot generation, Best-of-N sampling, reranking, or generic affinity guidance. These settings often discard information contained in a concrete failed candidate, even though the failure may reveal actionable local geometry and interaction constraints. We study failure-feedback-conditioned local repair for pocket-aware 3D molecular editing. Given a protein pocket, a fixed scaffold, an editable region, anchor atoms, a failed local candidate, and diagnostic feedback, the task is to generate a repaired candidate in the same editable region under the same generation budget. We define the task, propose a reproducible pipeline for failed-candidate construction and feedback extraction, and outline baselines including direct regeneration, Best-of-N, rerank-only, no-feedback repair, and feedback-conditioned repair. First-round literature analysis did not find a direct match that combines failed-candidate conditioning, explicit failure feedback, pocket-aware 3D local repair, and same-budget evaluation, although several adjacent pocket-aware generation and optimization methods represent important baselines. Current implementation provides a tested smoke pipeline; real molecular experiments remain future work.

## 1. Introduction

Structure-based drug design increasingly uses generative models to propose molecules conditioned on protein pockets. Existing methods can generate complete ligands, decorate scaffolds, grow fragments, optimize leads, or rerank candidates by docking or interaction scores. Yet a practical design loop often produces failed local candidates: an R-group clashes with the pocket, breaks an anchor constraint, loses a key interaction, or improves a docking score while degrading chemical plausibility.

A common response is to discard the failed candidate and sample again, or to generate many candidates and rerank them. This may be wasteful because the failed candidate contains local geometric and chemical information about what almost worked and what specifically failed. The core question of this project is whether a model can use the failed candidate and its diagnostic feedback to repair the same editable region more reliably than direct regeneration, Best-of-N, rerank-only, or generic affinity guidance under equal budget.

This draft focuses on the minimum viable setting: single R-group failed-candidate repair. The intended input is a protein pocket, original ligand, fixed scaffold, editable R-group mask, anchor atoms, failed candidate, and feedback features. The intended output is a repaired editable region or repaired local molecule.

## 2. Related Work

### 2.1 Pocket-aware generation and local molecular editing

First-round literature review identified several adjacent methods, including DiffDec, DiffLEOP, DecompDiff, DecompOpt, DecompDPO, Delete, DeepFrag, D3FG, STRIFE, SLOGEN, and BoKDiff. These methods cover scaffold decoration, lead optimization, structure-based diffusion, fragment growth, preference optimization, and Best-of-N-style selection. The current collision-risk assessment is Medium for this family because they are close to the protein-pocket local generation setting.

The first-round review did not find evidence that these methods explicitly use a concrete failed candidate and its failure diagnostics as the next-round repair condition. This remains a key point for second-round paper reading and must be rechecked before any submission claim.

### 2.2 Feedback, validation, and scoring tools

PoseBusters provides pose and molecular plausibility checks, including geometry and protein-ligand validity diagnostics. PLIP extracts protein-ligand interaction profiles such as hydrogen bonds, hydrophobic contacts, salt bridges, pi interactions, halogen bonds, and metal coordination. AutoDock Vina provides docking poses and affinity scores. In this project, these tools are treated as feedback or evaluation components, not as competing repair models.

A key methodological constraint is that Vina alone cannot establish success. Any final evaluation must include geometry validity, scaffold preservation, anchor validity, clash checks, interaction recovery, drug-likeness-related metrics, and negative results.

## 3. Task Definition

Given:

- Protein pocket `P`.
- Original ligand `L`.
- Fixed scaffold `S`.
- Editable region mask `M`.
- Anchor atoms `A`.
- Failed candidate `C_fail`.
- Feedback features `F_fail`.

Generate:

- Repaired candidate `C_repair` in the same editable region.

The central evaluation protocol is same-budget repair. For a fixed candidate budget, compare repair against direct regeneration, Best-of-N, rerank-only, no-feedback repair, global-score-only feedback, geometry-only feedback, interaction-only feedback, and full feedback.

## 4. Method Overview

The planned pipeline has four stages.

1. R-group dataset construction.
   - Load protein-ligand complexes.
   - Extract pocket context.
   - Split ligand into fixed scaffold and editable R-group.
   - Validate scaffold preservation, anchor atoms, and coordinate alignment.

2. Failed candidate generation.
   - Construct controlled failures such as clash, interaction loss, anchor invalidity, geometry invalidity, excessive flexibility, drug-likeness degradation, and score hacking.
   - Store failure type, random seed, original ligand, failed candidate, and provenance.

3. Feedback extraction.
   - Global feedback: Vina / Delta Vina, QED, SA, logP, rotatable bonds, ligand efficiency, PoseBusters pass/fail.
   - Geometry feedback: clash count, minimum protein-ligand distance, anchor distance error, editable validity.
   - Interaction feedback: PLIP interaction fingerprint and recovery of key interactions.

4. Repair and evaluation.
   - Compare direct regeneration, Best-of-N, rerank-only, no-feedback repair, and feedback-conditioned variants.
   - Aggregate metrics across seeds and splits.

The current code implements a minimal RDKit-first smoke version of this pipeline. It reads public RCSB ligand SDF files, records ligand descriptors, extracts Murcko scaffold atoms where available, derives editable atoms and anchor atoms, propagates template failure labels into feedback records, and writes auditable metrics and summary outputs. It does not yet generate repaired molecules, call PLIP/PoseBusters/Vina, or train a feedback-conditioned model.

## 5. Experimental Design

### 5.1 Data

The current smoke dataset uses public RCSB PDB entries 1A4W, 3PTB, and 1HSG. Sources and SHA256 checksums are recorded in `docs/smoke_data_manifest.md`; raw structures are excluded from git and can be reconstructed by running `scripts/data/download_smoke_complexes.py`. In the current RDKit smoke run, all three ligands are readable; 1HSG yields a Murcko scaffold and anchor atom, while 1A4W and 3PTB have no Murcko scaffold and are retained as negative data-selection examples. Full experiments should later use a larger reproducible split with leakage checks across scaffold, protein, and pocket similarity where feasible.

### 5.2 Baselines

Required baselines:

- Direct regeneration.
- Best-of-N.
- Rerank-only.
- No-feedback repair.
- Global-score-only feedback.
- Geometry-only feedback.
- Interaction-only feedback.
- Full feedback repair.

### 5.3 Metrics

Required metrics:

- Same-budget success rate.
- Scaffold preservation.
- Editable validity.
- Anchor validity.
- Protein-ligand clash.
- PoseBusters pass.
- PLIP interaction recovery / similarity.
- Vina / Delta Vina.
- Ligand efficiency.
- QED.
- SA.
- logP.
- Rotatable bonds.

At least three random seeds are required for any model claim. A single seed or toy smoke result is not sufficient evidence.

## 6. Current Implementation Status

Current reproducible artifacts:

- `environment.yml`: RDKit-first base conda environment specification.
- `configs/environment_ml_optional.yml`: optional ML environment sketch for Torch/PyG work.
- `scripts/setup/check_environment.py`: dependency and GPU visibility check.
- `configs/data/smoke_download.yaml`: public RCSB smoke data download config.
- `docs/smoke_data_manifest.md`: public smoke sample source and checksum manifest.
- `configs/data/rgroup_smoke.yaml`: smoke R-group dataset config.
- `configs/data/failed_candidate_smoke.yaml`: smoke failed-candidate config.
- `configs/feedback/smoke.yaml`: smoke feedback config.
- `configs/baselines/smoke.yaml`: smoke baseline config.
- `configs/eval_smoke_summary.yaml`: smoke summary output config.
- `scripts/setup/smoke_pipeline_dry_run.py`: dry-run pipeline plan generator.
- `scripts/data/download_smoke_complexes.py`: public RCSB smoke downloader.
- `scripts/data/build_rgroup_dataset.py`: RDKit-backed dataset builder.
- `scripts/data/generate_failed_candidates.py`: template failed-candidate record and SDF generator.
- `scripts/data/extract_feedback.py`: RDKit descriptor plus template failure feedback extractor.
- `scripts/eval/eval_baselines.py`: smoke baseline metrics writer.
- `scripts/analysis/summarize_smoke_results.py`: summary JSON, SVG figure, and case-list writer.
- `tests/test_smoke_pipeline.py`, `tests/test_metrics.py`, `tests/test_download_smoke_complexes.py`, `tests/test_rdkit_scaffold.py`: smoke and unit tests.

Validation performed:

- `conda run -n pfr python scripts/setup/check_environment.py`: required checks passed with Python 3.11.15 and RDKit 2026.03.2.
- `conda run -n pfr env PYTHONPATH=src pytest -q`: 7 passed.
- Public RCSB smoke download and file-level RDKit pipeline run completed.
- Output artifacts exist under `outputs/metrics`, `outputs/tables`, `outputs/figures`, and `outputs/molecules`.

Current limitations:

- PLIP, PoseBusters, Vina, Torch, and PyG are optional/missing in the validated base environment.
- Failed candidates are still template records, not perturbed 3D repaired or failed molecules.
- Feedback includes RDKit descriptors and scaffold/anchor state, but not PLIP/PoseBusters/Vina outputs.
- No model has been trained.
- No claim is made about repaired-molecule performance.

## 7. Preliminary Results

RDKit-backed file-level smoke results are available.

| Result type | Status | Evidence |
|---|---|---|
| Literature collision check | First round complete | `docs/literature_matrix.md` |
| Base RDKit environment | Required checks passed | `docs/optional_tool_notes.md`, `scripts/setup/check_environment.py` |
| Public smoke samples | 3 RCSB entries | `docs/smoke_data_manifest.md` |
| RDKit scaffold extraction | 3/3 readable; 1/3 with Murcko scaffold and anchor | `data/processed/rgroup_smoke.jsonl`, reproducible from scripts |
| Smoke failed molecules | 12 SDF files | `outputs/molecules/smoke_failed/`, `outputs/molecules/smoke_cases.json` |
| Smoke repair baselines | 24 SDF files | `outputs/molecules/smoke_repaired/`, `outputs/molecules/smoke_cases.json` |
| Smoke feedback records | 12 records | `data/processed/feedback_smoke.jsonl`, reproducible from scripts |
| Smoke metrics | RDKit descriptor + template-failure metrics | `outputs/metrics/baselines_smoke.json`, `outputs/tables/baselines_smoke.csv` |
| Smoke figure | Generated | `outputs/figures/smoke_success_rates.svg` |
| Smoke case file | Generated, empty molecule-level cases | `outputs/molecules/smoke_cases.json` |
| Tests | 7 passed | `conda run -n pfr env PYTHONPATH=src pytest -q` |
| Real repaired-molecule experiment | Not started | Requires perturbation/repair model and real feedback tools |
| Model comparison | Not started | Requires implemented repair model and baselines |

Current smoke metrics report same-budget success rate 0.0833, editable validity 0.5, anchor validity 0.25, and clash-free rate 0.75 across 12 template failed candidates. These values primarily reflect the template failure labels and the fact that only one smoke ligand currently has a detected scaffold/anchor; they are not model-performance results.

No claim is currently made that feedback-conditioned repair improves molecular design performance.

## 8. Discussion

The first-round literature check suggests that the proposed task is not an obvious duplicate of existing pocket-aware generation or optimization work. However, this conclusion is provisional. The strongest adjacent risks are methods for pocket-aware scaffold decoration, lead optimization, structure-based diffusion, and Best-of-N alignment. The project should therefore frame its novelty narrowly around failed-candidate-conditioned repair and same-budget evaluation, rather than broad pocket-aware generation.

The smoke pipeline is useful because it fixes file contracts and evaluation schema before heavy modeling. This reduces the risk that later experiments become ad hoc or impossible to audit. The next technical bottleneck is moving from placeholders to real chemistry-aware processing.

## 9. Limitations

- Current evidence is not sufficient for publication.
- Current failed candidates are controlled coordinate perturbations rather than failures produced by a generator or docking loop.
- The smoke dataset is tiny and includes two ligands without Murcko scaffolds.
- No trained feedback-conditioned repair model exists yet.
- PLIP, PoseBusters, Vina, Torch, and PyG are not part of the validated base environment.
- AMG and MolJO references remain ambiguous and require second-round verification.
- Vina, PLIP, and PoseBusters integration must be validated carefully to avoid overclaiming.

## 10. Reproducibility and Ethics

All conclusions must remain traceable to code, configurations, data versions, logs, raw metrics, or literature sources. Negative results and failed runs should be recorded. The project should use public datasets and avoid private or proprietary structures unless permission is explicit. Generated molecules are computational hypotheses, not validated drug candidates.

Reproducibility targets:

- Rebuild environment from `environment.yml`.
- Run dependency check with `python scripts/setup/check_environment.py`.
- Run smoke dry-run with `PYTHONPATH=src python scripts/setup/smoke_pipeline_dry_run.py`.
- Run tests with `pytest -q`.
- Preserve raw metrics, tables, figures, molecules, logs, and configs under the project structure.

## 11. Next Steps

1. Improve smoke sample selection so most ligands contain a meaningful scaffold/editable split.
2. Replace template failed-candidate records with actual RDKit 3D perturbations and saved failed molecule files.
3. Add chemistry-aware feedback beyond RDKit descriptors, starting with distance-based clash and anchor metrics.
4. Add optional PoseBusters, PLIP, and Vina integration only after installation is reproducible.
5. Implement baseline metrics for direct regeneration, Best-of-N, rerank-only, and no-feedback repair using real candidate structures.
6. Conduct second-round reading of DiffDec, DiffLEOP, DecompDPO, DecompDiff, DecompOpt, AMG, and MolJO.
7. Only after the above, start model implementation and multi-seed experiments.
