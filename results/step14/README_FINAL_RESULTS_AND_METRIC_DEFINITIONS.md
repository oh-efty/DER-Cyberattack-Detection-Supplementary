# Step-14 — Final Results Pack (SHA-pinned, read-only inputs)

**Status:** Produced from immutable Step-10 through Step-13 files and Step-11 saved scores. This folder is the **new reporting artifact**; source files were not written or changed.

## Data and analysis provenance

- 1,400 ID and 1,400 OOD scenarios; 14 scenario families ×100 each; 900 attack and 500 benign scenarios per split; 109 causal endpoints per scenario.
- Training and calibration were completed earlier. Here: **no training, no new inference, no model/seed selection, no threshold change, no CAL/Validation/raw-data access**.
- CIs are unadjusted percentile 95% intervals from **B=1,000 scenario-cluster draws**, stratified 14 families, seed `270325`. The same draws are used for models/seeds and paired contrasts **within each split**. ID and OOD are independent split samples.
- Neural entries: compute the metric for each of five frozen seeds, then mean metrics **within each draw**. Five-seed sample SD is a separate variability descriptor, not the scenario-bootstrap CI.
- The baseline is the **designated Combined PF+Command OR rule**, not statistically proved to be the *best* threshold baseline. It cannot be retrospectively labelled pre-outcome confirmatory after examining test results.
- Interval claims are exploratory/unadjusted where no independently verifiable pre-outcome registration exists; no adjustment for multiple comparisons.

## Explicit metric definitions (do not conflate FPR denominators)

**P1 (frozen, attack-scenario detection rate):** fraction of all ground-truth attack scenarios with ≥1 detector alarm at or after true attack onset. Pre-onset-only alarms do **not** count. Denominator = **900 attack scenarios/split** (including undetected or short-observable attacks). Higher is better.

**P2 (frozen, benign *WINDOW* FPR):** number of false-positive alarmed **benign causal endpoint windows** divided by all benign windows = 500 × 109 = **54,500 windows/split**. BESS transition and PV-cloud windows each have **100 × 109 = 10,900** denominators/split. P2 is *not* the probability of at least one false alarm in a scenario. Lower is better. Frozen ≤1% constraint was on **CAL P2 overall**, not guaranteed for held-out splits.

**P3 (detector-gated 9-class Macro-F1):** on **all ground-truth attack-active endpoint windows**, class predictions count only when the frozen detector alarms. A miss is not awarded type-class credit. Macro-F1 over the fixed nine type labels; a class with no predicted positives gets zero-division F1=0. Detection-only baselines have **N/A**, never zero.

**Localization Top-1/Top-3 (detector-gated):** denominator = all ground-truth attack-active endpoint windows (or corresponding true-label subgroup). Correct if alarm fires and true global bus index is Top-1 / within Top-3. For LightGBM, global zero-based indices `0, 13, 30` (physical buses **1, 14, 31**) were not in its native training-class support: count such test truths as incorrect, **not removed**. Both top-k metrics refer to 33 global buses.

**Threshold-free scenario AUPRC/AUROC (diagnostic):** score of each scenario is `max(score over ALL 109 causal endpoints)`, for attacks AND benign scenarios, **without using onset to select score windows**. 900 attack scenarios / 500 benign scenarios; AUPRC uses Average Precision (non-interpolated positive-step precision), AUROC uses tie-aware midrank. These are *not* the frozen P1 or P2. Curves are exploratory/descriptive, including pre-onset scores.

**Recall at matched 1% benign *SCENARIO* FPR (post-hoc diagnostic):** attack-scenario recall under an *exploratory held-out-derived* score operating point allowing at most 1% of **500 benign scenarios (≤5 scenarios)** to have a positive scenario decision. The Step-13 bootstrap recomputes that descriptive matched point per draw. No threshold is saved, applied to frozen P1, or selected as a deployment threshold. This is **not** P2's 1% benign-window constraint.

**Oracle/intersection diagnostics:** oracle measures type/localization quality over **all ground-truth attack-active endpoint windows**, without detector gating. Intersection restricts to ground-truth active endpoints detected by **both** compared models in the same-seed pairing. Reported denominators are essential; a conditional metric is not the end-to-end primary metric. Zero denominator → N/A.

## MAIN TABLE — Primary (frozen operating point)

### ID test

| Method | P1 attack scenarios (%) | P2 benign windows (%) | P3 gated Macro-F1 (%) | Loc Top1 (%) | Loc Top3 (%) | Scenario AP | Scenario AUROC | Recall@1% scenario-FPR (%) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Proposed GCN-GRU Full16 (5-seed mean) | 63.84 [62.16, 65.56] | 0.81 [0.65, 1.00] | 48.59 [47.51, 49.53] | 54.67 [53.05, 56.23] | 55.46 [53.79, 57.09] | 0.895 [0.888, 0.902] | 0.777 [0.763, 0.791] | 57.96 [56.24, 59.76] |
| GRU Full (5-seed mean) | 68.51 [66.84, 70.20] | 0.95 [0.87, 1.03] | 48.74 [47.55, 49.81] | 51.14 [49.70, 52.45] | 52.93 [51.42, 54.38] | 0.903 [0.897, 0.908] | 0.794 [0.782, 0.805] | 58.40 [56.73, 60.42] |
| LightGBM Full16 | 84.44 [82.33, 86.44] | 1.05 [0.83, 1.31] | 51.40 [50.10, 52.71] | 57.57 [55.88, 59.17] | 58.53 [56.79, 60.20] | 0.929 [0.921, 0.936] | 0.857 [0.842, 0.872] | 57.22 [54.56, 60.33] |
| Combined PF+Command (designated baseline) | 22.33 [20.00, 24.67] | 0.95 [0.87, 1.03] | N/A | N/A | N/A | N/A | N/A | N/A |

### OOD test

| Method | P1 attack scenarios (%) | P2 benign windows (%) | P3 gated Macro-F1 (%) | Loc Top1 (%) | Loc Top3 (%) | Scenario AP | Scenario AUROC | Recall@1% scenario-FPR (%) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Proposed GCN-GRU Full16 (5-seed mean) | 63.16 [61.60, 64.89] | 0.38 [0.33, 0.43] | 44.32 [43.03, 45.62] | 52.33 [50.96, 53.79] | 53.13 [51.73, 54.59] | 0.891 [0.885, 0.898] | 0.769 [0.756, 0.783] | 56.51 [54.93, 58.31] |
| GRU Full (5-seed mean) | 67.80 [66.27, 69.29] | 1.61 [1.50, 1.72] | 36.69 [34.77, 38.55] | 38.94 [37.03, 40.81] | 40.78 [38.86, 42.64] | 0.884 [0.878, 0.890] | 0.754 [0.741, 0.766] | 53.64 [51.47, 55.69] |
| LightGBM Full16 | 78.56 [76.11, 81.00] | 1.25 [1.13, 1.39] | 40.80 [39.10, 42.42] | 41.33 [39.20, 43.37] | 42.01 [39.82, 44.09] | 0.879 [0.867, 0.890] | 0.766 [0.744, 0.787] | 41.67 [39.11, 44.44] |
| Combined PF+Command (designated baseline) | 14.56 [12.55, 16.67] | 0.96 [0.87, 1.05] | N/A | N/A | N/A | N/A | N/A | N/A |

Cells display estimate [unadjusted 95% CI]. Scenario AP/AUROC and matched scenario FPR are post-hoc descriptive; their values appear identically for primary and secondary as no calibrated operating threshold is involved. Primary P2 overall/BESS/PV are separate in `step14_main_long_CI.csv`.

## Pre-specified-in-user-request paired comparisons (registration limitation noted)

Difference = Proposed − comparator (percentage points). These are **the frozen Step-12 paired intervals**, no re-sampling or cherry-picking.

### ID

| Paired contrast | Metric | Difference in pp [95% CI] |
|---|---|---:|
| proposed_vs_lightgbm_full16 | P1 | -20.60 [-22.87, -18.51] |
| proposed_vs_lightgbm_full16 | P2_overall | -0.24 [-0.57, 0.06] |
| proposed_vs_lightgbm_full16 | P3 | -2.81 [-4.25, -1.55] |
| proposed_vs_lightgbm_full16 | Loc_Top1 | -2.90 [-3.90, -1.92] |
| proposed_vs_gru | P1 | -4.67 [-5.78, -3.53] |
| proposed_vs_gru | P2_overall | -0.14 [-0.32, 0.06] |
| proposed_vs_gru | P3 | -0.15 [-1.04, 0.77] |
| proposed_vs_gru | Loc_Top1 | 3.53 [2.76, 4.31] |
| proposed_vs_designated_combined_threshold | P1 | 41.51 [38.98, 44.13] |
| proposed_vs_designated_combined_threshold | P2_overall | -0.14 [-0.33, 0.06] |
| proposed_vs_designated_combined_threshold | P3 | N/A |
| proposed_vs_designated_combined_threshold | Loc_Top1 | N/A |

### OOD

| Paired contrast | Metric | Difference in pp [95% CI] |
|---|---|---:|
| proposed_vs_lightgbm_full16 | P1 | -15.40 [-18.00, -12.80] |
| proposed_vs_lightgbm_full16 | P2_overall | -0.88 [-1.02, -0.74] |
| proposed_vs_lightgbm_full16 | P3 | 3.52 [1.76, 5.28] |
| proposed_vs_lightgbm_full16 | Loc_Top1 | 11.00 [8.99, 13.15] |
| proposed_vs_gru | P1 | -4.64 [-5.89, -3.24] |
| proposed_vs_gru | P2_overall | -1.23 [-1.35, -1.12] |
| proposed_vs_gru | P3 | 7.63 [6.14, 9.27] |
| proposed_vs_gru | Loc_Top1 | 13.39 [11.59, 15.39] |
| proposed_vs_designated_combined_threshold | P1 | 48.60 [45.98, 51.25] |
| proposed_vs_designated_combined_threshold | P2_overall | -0.59 [-0.70, -0.48] |
| proposed_vs_designated_combined_threshold | P3 | N/A |
| proposed_vs_designated_combined_threshold | Loc_Top1 | N/A |

## Ablation

`step14_ablation_all_models_CI.csv` compares LightGBM Base12/Base+PF14/Full16 and neural GCN-GRU Base12/Base+PF14/Proposed Full16 for detection, P2/BESS/PV, and available gated P3/localization. `step14_ablation_paired_difference_CI.csv` contains 95% paired scenario-cluster differences (A−B). **LightGBM Base12/PF14 are detection-only**; they have no classifier/localization head. Do not interpret an N/A as zero.

## Per-family detection and hard-benign FPR

`step14_per_family_attack_P1_CI.csv` has **9 attack families × 4 fixed methods × 2 splits = 72 rows**, denominators 100 attack scenarios per family/split. `step14_per_family_benign_window_FPR_CI.csv` separately covers **5 benign families × 4 methods × 2 splits = 40 rows**, denominator 10,900 windows per family/split. The **lowest detected families** are not validation-based method-selection criteria.

## Localization: seen/unseen, measurement/command, oracle/intersection

- `step14_localization_gated_subgroups_CI.csv` — globally gated Top1/Top3, seen/unseen buses and measurement/command attack subgroups (plus intersections), denominator counts.
- `step14_oracle_common_detection_CI_with_denominators.csv` — Pro­posed vs GRU and vs LightGBM, per comparison, split, operating point, context, and exact per-seed active-endpoint denominators.
- `step14_oracle_common_detection_paired_CI.csv` — conditional paired differences, exploratory only.
- LightGBM structurally unsupported physical buses **1, 14 and 31**. Their true test cases remain in denominators.

## ROC/PR plots and curve data

- `step14_scenario_roc_pr_empirical_per_seed_points.csv`: complete tied-score sorted empirical coordinates, **each neural seed separately**, plus LightGBM (no averaging scores).
- `step14_scenario_roc_pr_pointwise_95CI_grid.csv`: mean per-seed curves and pointwise 95% scenario-bootstrap bands on a fixed x-grid; replicates use original Step-12 draw fingerprints. Pointwise bands are not simultaneous confidence bands.
- Four ROC/PR plots (ID ROC, ID PR, OOD ROC, OOD PR), each exported as SVG+PNG; the ID→OOD degradation figure also exports as SVG+PNG. **AP/AUC must exactly match Step-13 frozen numerical statistics**; the code refuses to save if mismatched.
- Combined two-threshold OR rule has **no pre-declared scalar ranking score**, so its ROC/AUPRC/AUROC/matched scalar-score recall are honestly N/A, not synthesized.

## ID→OOD degradation

`step14_ID_to_OOD_primary_degradation_CI.csv` contains **ID minus OOD** differences for all four fixed methods, including family P1. `step14_ID_to_OOD_degradation_primary.svg/png` has P1, gated P3 and localization Top1 with 95% CIs. ID and OOD are independent sets; their CI is the frozen Step-12 independent-split bootstrap, not a spurious ID-vs-OOD scenario pairing.

## Files / reproducibility / caveats

- All numeric tables and plot data are CSV; figures are SVG/PNG. Each child file SHA is stored in `step14_final_pack_manifest.json`, with final SHA receipt `step14_final_pack_manifest.sha256`.
- Remaining thesis caveats: neural detection P1 underperforms Full16 LightGBM at the frozen primary threshold, despite OOD gated-type and localization advantages; some stealth/scaling families are difficult; 33-bus simulated network does not establish field deployment generalization.
- No prospective independent new held-out set was introduced for any post-hoc claim, and no experimental change was made after seeing Step-11 outcomes.
