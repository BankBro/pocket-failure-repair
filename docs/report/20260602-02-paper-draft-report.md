# Failure-Feedback-Conditioned Repair for Pocket-Aware 3D Local Molecular Editing

> BIBM-style working draft. This draft is conservative: it reports a reproducible diagnostic protocol, three-seed contact-degraded local-edit experiments, official PLIP/Vina checks, budget-fair tables, shuffled-feedback ablations, and a representative case study. It does not claim a benchmark-scale trained generative model.

## Abstract

Pocket-aware molecular generation often relies on one-shot generation, Best-of-N sampling, reranking, or generic scoring guidance. These workflows can discard information contained in a concrete failed local edit, even when the failure reveals actionable geometric or interaction constraints. We study failure-feedback-conditioned repair for pocket-aware 3D local molecular editing. Given a protein pocket, fixed scaffold, editable region, anchor atoms, a failed local candidate, and diagnostic feedback, the task is to repair the same editable region under an auditable generation budget. We introduce a reproducible diagnostic protocol for constructing contact-degraded, anchor-preserved local-edit failures from public protein-ligand complexes, extracting repair feedback, and comparing feedback-conditioned repair against no-feedback, rerank-only, Best-of-N, direct regeneration, and ablated feedback policies. On a three-seed contact-degraded diagnostic set with 53 failed candidates, official PLIP/Vina evaluation completes for 477 key-baseline records with zero PLIP/Vina errors. Feedback-conditioned editable-contact repair achieves positive official PLIP interaction recovery gain, while no-feedback/rerank-only remain at zero and Best-of-N/direct regeneration are negative. Shuffled-feedback ablations reduce the learned-policy recovery gains toward zero or below, supporting the role of diagnostic feedback content. The learned policies remain weak compared with an editable-search fallback, so the contribution is best interpreted as a reproducible diagnostic repair protocol and mechanism-level evidence rather than a final publication-level generative model.

## 1. Introduction

Structure-based molecular design increasingly uses generative models conditioned on protein pockets. These systems can decorate scaffolds, grow fragments, optimize leads, or rank candidates by docking or interaction scores. In practical design loops, however, local candidates often fail in structured ways: an editable R-group may lose contacts while preserving the anchor, introduce pocket clashes, drift from anchor atoms, or improve a score while weakening interpretable interactions.

A common response is to discard the failed candidate and sample again, or to produce many candidates and rerank them. This may be inefficient because the failed candidate contains information about what almost worked and what specifically failed. We therefore ask whether explicit failure feedback can guide repair in the same editable region more reliably than no-feedback repair, rerank-only, Best-of-N, direct regeneration, or generic score-based guidance under an auditable budget.

This work focuses on the minimum viable setting: single R-group failed-candidate repair. We do not claim to solve general pocket-aware molecular generation. Instead, we define and evaluate a failed-candidate-conditioned diagnostic local repair protocol.

Our current contributions are:

1. A reproducible file-level pipeline for public protein-ligand complexes, fixed scaffold/editable-region records, failed candidate construction, feedback extraction, repair baselines, and unified evaluation.
2. A contact-degraded anchor-preserved local-edit diagnostic set designed to test interaction recovery rather than trivial validity preservation.
3. Same-record and internal-budget auditing, with budget=1, budget=10, and higher-budget references reported separately.
4. Official PLIP/Vina evaluation of key baselines with explicit error accounting, plus shuffled-feedback ablations showing that feedback content affects interaction recovery.
5. A conservative paper-ready set of tables and a representative case study, while preserving negative results and limitations.

## 2. Related Work

### 2.1 Pocket-aware generation and local editing

Adjacent methods include DiffDec, DiffLEOP/Diffleop, DecompDiff, DecompOpt, DecompDPO, Delete, D3FG, MolJO, BoKDiff, AMG, CBGBench, and related pocket-conditioned scaffold decoration or lead optimization methods. These works are close to the broader setting of structure-based molecular generation and optimization. The current literature matrix in `docs/report/20260601-02-literature-matrix-report.md` tracks these methods and their collision risk.

The current positioning is narrow: failed-candidate-conditioned local repair with explicit diagnostics, fixed scaffold/editable region, and same-budget recovery evaluation. The closest adjacent families solve scaffold decoration, lead optimization, molecule editing, preference/guidance alignment, or benchmark construction, but current evidence has not found the full combination of a concrete failed candidate, explicit failure diagnostics, same editable region repair, and same-budget recovery evaluation. We do not claim novelty for pocket-aware generation, R-group optimization, docking, PLIP/PoseBusters evaluation, or Best-of-N selection.

### 2.2 Feedback and validation tools

PLIP extracts protein-ligand interaction fingerprints such as hydrogen bonds, hydrophobic interactions, salt bridges, pi interactions, halogen bonds, and metal coordination. AutoDock Vina provides docking and score-only energies. PoseBusters provides pose and molecular plausibility diagnostics. In this project, these tools are evaluators or diagnostic components, not repair models.

A core evaluation constraint is that Vina score-only is not a repair success criterion. Interaction recovery must be reported as gain relative to the failed candidate, and no-feedback/identity/rerank outputs cannot be counted as successful repair without recovery gain.

## 3. Task Definition

Given:

- Protein pocket `P`.
- Original ligand `L`.
- Fixed scaffold atoms `S`.
- Editable region atoms `M`.
- Anchor atoms `A`.
- Failed local candidate `C_fail`.
- Diagnostic feedback `F_fail`.

Generate a repaired candidate `C_repair` that modifies only the editable local region while preserving the scaffold/anchor context.

The key evaluation target is repair gain relative to `C_fail`, not absolute validity alone. For each method, we track one final repaired record per failed candidate, plus internal candidate budget metadata.

## 4. Method

### 4.1 Data and local-edit records

The current smoke-plus data use 12 public RCSB entries: 1A4W, 3PTB, 1HSG, 1HVR, 2BR1, 3ERT, 1M17, 2HYY, 3G0E, 4DLI, 4ERW, and 5P21. Source and checksum details are recorded in `docs/report/20260602-01-smoke-plus-data-manifest-report.md`. Ligands are parsed with RDKit where possible, scaffold atoms and editable atoms are derived, and anchor atoms are stored in JSONL records.

### 4.2 Failed candidate construction

The broader pipeline supports several failure types, including clash, interaction loss, anchor invalidity, geometry invalidity, linker flexibility, drug-likeness drop, score hacking, local proposal failures, and docking-like failures. The strongest current diagnostic chain is contact-degraded anchor-preserved local editing. It selects local edits that keep basic validity and anchor preservation but reduce contact recovery, making interaction repair gain measurable.

For the expanded diagnostic run, seeds 0/1/2 produce 19, 17, and 17 failed candidates, respectively, for 53 total candidates.

### 4.3 Feedback extraction

Feedback records include:

- Geometry diagnostics: anchor distance error, clash count, minimum protein-ligand distance, editable-region validity, editable atom count.
- Global descriptors: molecular weight, QED, logP, rotatable bonds, TPSA, optional Vina/PoseBusters fields.
- Interaction placeholders and official PLIP-derived interaction recovery in downstream evaluation.
- Contact-degradation fields for the local-edit diagnostic subset, including contact recovery loss and contact similarity.

### 4.4 Repair policies

Compared policies include:

- No-feedback repair and identity/rerank-only controls.
- Direct regeneration and Best-of-N candidate-pool references.
- Geometry/global/interaction/full editable-search policies.
- Learned editable-contact policy based on leave-one-complex nearest-neighbor offsets.
- Ridge editable-contact policy.
- Budgeted learned editable-contact policy.
- Classified editable-contact policy that predicts one of 10 fixed editable offsets from oracle-free diagnostic features.
- Shuffled-feedback controls for learned, ridge, and budgeted learned policies.

### 4.5 Budget accounting

Record-level output budget is one repaired record per failed candidate per baseline. Internal candidate budget is tracked separately:

- budget=1: no-feedback, rerank-only, learned, ridge, classified.
- budget=10: budgeted learned, editable-contact/full search.
- budget≈16.1: Best-of-N and direct regeneration references.

Strict internal budget equality across all baselines is false, so final tables must be budget-stratified.

## 5. Experimental Setup

### 5.1 Environment

The base `pfr` conda environment supports RDKit-first data generation, repair, fallback metrics, and summaries. Official external evaluation uses the isolated `pfr-eval-tools` environment with PLIP, Vina, Meeko, OpenBabel, and PoseBusters. The environment caveats and command pattern are recorded in `docs/report/20260601-03-optional-tool-notes-report.md`.

Official outputs are not trusted by row count alone; `plip_error` and `vina_error` are checked for every official run.

### 5.2 Metrics

Main metrics include:

- repair gain / gain success relative to the failed candidate.
- scaffold/editable/anchor validity.
- clash and geometry diagnostics.
- contact recovery and contact fingerprint similarity gain.
- official PLIP interaction recovery and similarity gain.
- Vina score-only energy as a supplemental column.
- QED, logP, rotatable bonds, and related descriptor fields where available.

### 5.3 Reproducibility artifacts

Key artifacts include:

- `scripts/eval/run_contact_degraded_multiseed.py`.
- `scripts/eval/repair_baselines.py`.
- `scripts/eval/eval_repaired.py`.
- `scripts/eval/eval_official_tools.py`.
- `scripts/eval/summarize_official_eval.py`.
- `scripts/eval/audit_same_budget.py`.
- `scripts/analysis/write_paper_tables.py`.

## 6. Results

### 6.1 Main contact-degraded official results

The paper-ready main table is generated from raw summaries at `outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_main_results.md`.

Generated SVG figures:

- Main result figure: `outputs/20260602-03-paper-ready-contact-degraded-reporting/figures/paper_contact_degraded_main_results.svg`.
- Feedback ablation figure: `outputs/20260602-03-paper-ready-contact-degraded-reporting/figures/paper_contact_degraded_feedback_ablation.svg`.
- Case-study interaction-count figure: `outputs/20260602-03-paper-ready-contact-degraded-reporting/figures/paper_case_contact_degraded_3ert_seed2_interactions.svg`.


| Method | Internal budget | PLIP recovery gain | PLIP similarity gain | Vina score-only | PLIP errors | Vina errors |
|---|---|---|---|---|---|---|
| No-feedback | 1 | 0.0000 | 0.0000 | -6.9855 | 0 | 0 |
| Rerank-only | 1 | 0.0000 | 0.0000 | -6.9855 | 0 | 0 |
| Classified feedback | 1 | 0.0090 | -0.0108 | -6.5498 | 0 | 0 |
| Budgeted learned feedback | 10 | 0.0099 | -0.0083 | -6.9294 | 0 | 0 |
| Editable-contact search | 10 | 0.0301 | -0.0071 | -6.9934 | 0 | 0 |
| Best-of-N | 16.1 ref | -0.0591 | -0.0553 | -6.8985 | 0 | 0 |
| Direct regeneration | 16.1 ref | -0.1441 | -0.1900 | -4.7090 | 0 | 0 |

Interpretation: feedback-conditioned local repair yields positive PLIP recovery gain on this diagnostic subset, while no-feedback/rerank remain at zero and Best-of-N/direct regeneration are negative. The strongest method remains editable-contact search, not the learned policy.

### 6.2 Feedback ablation

The feedback ablation table is generated at `outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_contact_degraded_feedback_ablation.md`.

| Method | Budget | PLIP recovery gain | PLIP similarity gain | Vina score-only |
|---|---|---|---|---|
| No-feedback | 1 | 0.0000 | 0.0000 | -6.9855 |
| Shuffled learned | 1 | 0.0007 | -0.0188 | -6.9422 |
| Shuffled ridge | 1 | -0.0053 | -0.0251 | -6.8626 |
| Learned feedback | 1 | 0.0065 | -0.0119 | -6.5991 |
| Ridge feedback | 1 | 0.0076 | 0.0083 | -6.5593 |
| Classified feedback | 1 | 0.0090 | -0.0108 | -6.5498 |
| Shuffled budgeted learned | 10 | -0.0012 | -0.0205 | -6.9473 |
| Budgeted learned feedback | 10 | 0.0099 | -0.0083 | -6.9294 |
| Editable-contact search | 10 | 0.0301 | -0.0071 | -6.9934 |

Interpretation: shuffled feedback reduces official recovery gains toward zero or below, supporting the claim that feedback content matters. However, absolute gains are small.

### 6.3 Learned policy improvement attempt

The classified editable-contact policy predicts one of 10 fixed offsets from diagnostic features. It improves budget=1 official PLIP recovery gain to +0.0090, above learned (+0.0065) and ridge (+0.0076), but it does not close the gap to budget=10 editable-contact search (+0.0301). It is therefore an incremental learned baseline, not a final model.

## 7. Case Study

A representative case is `3ert_contact_degraded_local_edit_6_0`, seed 2. The case table is generated at `outputs/20260602-03-paper-ready-contact-degraded-reporting/tables/paper_case_contact_degraded_3ert_seed2.md`, with machine-readable details in `outputs/20260602-03-paper-ready-contact-degraded-reporting/metrics/paper_case_contact_degraded_3ert_seed2.json`.

The failed candidate has 10 reference PLIP interactions and 8 failed interactions. No-feedback and rerank-only preserve 8 interactions and have zero recovery gain. Classified feedback, learned feedback, budgeted learned feedback, and editable-contact search recover 9 interactions, reaching PLIP recovery gain +0.1250. This illustrates the intended repair behavior, but it is a single case and does not replace aggregate statistics.

## 8. Discussion

The current evidence supports a narrow mechanism-level conclusion: diagnostic failure feedback can improve interaction recovery in a controlled local-edit repair task. The shuffled-feedback results strengthen this claim because mismatched feedback removes most of the official recovery gain.

The evidence does not support a broad claim that the current learned model is publication-level or that the approach outperforms all pocket-aware generation methods. Editable-search fallback remains stronger than learned policies, and the dataset is still a diagnostic subset rather than a large benchmark.

## 9. Limitations

- The diagnostic contact-degraded set has only 53 failed candidates over three seeds.
- The public smoke-plus set has 12 complexes and is not a leakage-controlled community benchmark.
- Many failed candidates are constructed or selected diagnostics, not failures from a modern pocket-aware generator.
- The learned policies are lightweight nearest-neighbor/ridge/classification baselines, not neural generative repair models.
- Strict internal candidate budget equality across all baselines is false; tables must be budget-stratified.
- Vina score-only is supplemental and cannot establish repair success.
- PoseBusters remains bounded/diagnostic because full-batch pass rates and timeouts are not yet stable for this local-edit task.
- Official tool runs require `pfr-eval-tools`; outputs must be checked for error fields.

## 10. Ethics and Reproducibility

All data used in the current pipeline come from public structural resources. Generated molecules are computational hypotheses and should not be interpreted as validated therapeutics. Negative results, failed tool runs, and environment pitfalls are recorded in `docs/EXPERIMENT_LOG.md` and `docs/report/20260601-03-optional-tool-notes-report.md`.

Reproducibility principles:

- Rebuild base environment from `environment.yml`.
- Use `pfr` for RDKit-first pipeline steps and summaries.
- Use `pfr-eval-tools` for official PLIP/Vina/PoseBusters evaluation.
- Preserve raw JSONL outputs, summaries, tables, and case files.
- Report repair gain relative to the failed candidate.
- Do not report Vina-only improvements as repair success.

## 11. Conclusion

We introduced a reproducible diagnostic protocol for failure-feedback-conditioned pocket-aware 3D local repair. On a contact-degraded local-edit subset, feedback-conditioned policies show positive official PLIP recovery gain, while no-feedback/rerank are zero and direct regeneration/Best-of-N are negative. Shuffled-feedback ablations indicate that diagnostic feedback content contributes to recovery. The current learned policies remain weak relative to editable-search fallback, so the present result is best viewed as a reproducible, auditable mechanism-level foundation for a future stronger repair model.

## 12. Next Steps

1. Improve the oracle-free learned repair policy using richer pocket/contact directional features or top-k classified offset selection.
2. Add failures from a generator, docking loop, or stronger local edit proposal mechanism.
3. Expand beyond the 12-complex smoke-plus split toward protein/scaffold/pocket leakage checks.
4. Add figures for aggregate results and the 3ERT case study.
5. Continue updating the literature matrix and narrowing claims against adjacent work.
6. Convert this working draft into a final BIBM submission only after stronger learned-model evidence or a clearly scoped diagnostic-method paper framing is complete.
