# Failure-Feedback-Conditioned Repair for Pocket-Aware 3D Local Molecular Editing

> BIBM-style working draft. This draft is intentionally conservative: current evidence includes a first-round literature collision check and a runnable smoke pipeline, but not yet real molecular experiments.

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

The current code implements a minimal smoke version of this pipeline with placeholder chemistry logic. It validates interfaces and output schemas but does not yet perform RDKit-based R-group splitting or real protein-ligand feedback extraction.

## 5. Experimental Design

### 5.1 Data

The final dataset should use public protein-ligand complexes. The immediate next step is a small smoke set of 1-3 public complexes under `data/raw/smoke_complexes`. Full experiments should later use a reproducible split with leakage checks across scaffold, protein, and pocket similarity where feasible.

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

- `environment.yml`: target conda environment specification.
- `scripts/setup/check_environment.py`: dependency and GPU visibility check.
- `configs/data/rgroup_smoke.yaml`: smoke R-group dataset config.
- `configs/data/failed_candidate_smoke.yaml`: smoke failed-candidate config.
- `configs/feedback/smoke.yaml`: smoke feedback config.
- `configs/baselines/smoke.yaml`: smoke baseline config.
- `scripts/setup/smoke_pipeline_dry_run.py`: dry-run pipeline plan generator.
- `scripts/data/build_rgroup_dataset.py`: minimal dataset metadata builder.
- `scripts/data/generate_failed_candidates.py`: minimal failed-candidate record generator.
- `scripts/data/extract_feedback.py`: minimal feedback record generator.
- `scripts/eval/eval_baselines.py`: placeholder baseline metrics writer.
- `tests/test_smoke_pipeline.py`: toy end-to-end test.

Validation performed:

- Empty-input smoke pipeline runs end-to-end.
- Toy-input pytest passes: `pytest -q` reports `1 passed`.

Current limitations:

- The active shell environment lacks RDKit.
- Real protein-ligand complexes have not yet been downloaded or processed.
- R-group splitting, conformer handling, PLIP, PoseBusters, and Vina integration are not yet implemented.
- No model has been trained.
- No real molecular metrics or figures have been produced.

## 7. Preliminary Results

Only engineering smoke results are available.

| Result type | Status | Evidence |
|---|---|---|
| Literature collision check | First round complete | `docs/literature_matrix.md` |
| Environment specification | Complete draft | `environment.yml` |
| Dependency check script | Implemented | `scripts/setup/check_environment.py` |
| Empty-input smoke run | Passed | `docs/EXPERIMENT_LOG.md` |
| Toy pipeline test | Passed | `tests/test_smoke_pipeline.py`, `pytest -q` |
| Real molecular experiment | Not started | Requires RDKit environment and public complex data |
| Model comparison | Not started | Requires implemented repair model and baselines |

No claim is currently made that feedback-conditioned repair improves molecular design performance.

## 8. Discussion

The first-round literature check suggests that the proposed task is not an obvious duplicate of existing pocket-aware generation or optimization work. However, this conclusion is provisional. The strongest adjacent risks are methods for pocket-aware scaffold decoration, lead optimization, structure-based diffusion, and Best-of-N alignment. The project should therefore frame its novelty narrowly around failed-candidate-conditioned repair and same-budget evaluation, rather than broad pocket-aware generation.

The smoke pipeline is useful because it fixes file contracts and evaluation schema before heavy modeling. This reduces the risk that later experiments become ad hoc or impossible to audit. The next technical bottleneck is moving from placeholders to real chemistry-aware processing.

## 9. Limitations

- Current evidence is not sufficient for publication.
- Current pipeline uses placeholders and toy metadata.
- No real protein-ligand data have been processed.
- No trained feedback-conditioned repair model exists yet.
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

1. Create and activate the `pfr` conda environment.
2. Re-run `python scripts/setup/check_environment.py` until RDKit and required tools are available.
3. Prepare 1-3 public protein-ligand complexes for smoke testing.
4. Replace placeholder dataset construction with RDKit-based scaffold / R-group / anchor extraction.
5. Add real failed-candidate perturbations and feedback extraction.
6. Implement baseline metrics for direct regeneration, Best-of-N, rerank-only, and no-feedback repair.
7. Conduct second-round reading of DiffDec, DiffLEOP, DecompDPO, DecompDiff, DecompOpt, AMG, and MolJO.
8. Only after the above, start model implementation and multi-seed experiments.
