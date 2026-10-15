# STEP-14A — Frozen benign scenario alarms vs window FPR

**Provenance:** Step-10 frozen detection thresholds; Step-11 saved ID/OOD predictions only; Step-12 original 1,000 paired whole-scenario family-stratified bootstrap resamples, seed 270325. No raw dataset access, no training, no model selection or calibration.

**Benign SCENARIO alarm rate:** fraction of benign scenarios with at least one frozen-threshold alarm among 109 causal endpoint windows. Overall n=500 benign scenarios per split; each family n=100. This is not Step-11 P2 nor the post-hoc matched 1% scenario FPR.

**Benign WINDOW FPR:** number of alarmed benign causal endpoint windows / benign endpoint windows; overall n=54,500 windows and per family n=10,900 per split. CIs resample whole scenarios, NEVER independent windows.

**Neural 5-seed mean:** compute rate per seed within each bootstrap resample, then average five rates. All 30 neural seed-specific methods are also present in the full CSV.

**Confidence intervals:** unadjusted percentile 95%, 1,000 resamples, frozen seed 270325. Identical scenario weights across all methods and seeds within a split.

## Scenario alarm rate — four primary methods

### id_test — estimate [95% CI], %

| Benign group | Proposed | GRU_FULL | LightGBM Full16 | Combined PF+Command |
|---|---:|---:|---:|---:|
| OVERALL_BENIGN | 21.96 [20.00, 23.84] | 33.88 [32.00, 35.84] | 45.60 [41.20, 50.00] | 22.00 [20.80, 23.20] |
| BESS_TRANSITION | 44.60 [39.79, 49.80] | 49.80 [45.60, 54.20] | 37.00 [28.00, 47.00] | 100.00 [100.00, 100.00] |
| LOAD_RAMP | 13.00 [9.60, 16.80] | 29.40 [25.80, 33.60] | 60.00 [51.00, 69.00] | 1.00 [0.00, 3.00] |
| LOAD_STEP | 14.40 [10.60, 18.40] | 28.60 [24.60, 33.00] | 63.00 [53.00, 72.00] | 3.00 [0.00, 7.00] |
| PV_CLOUD | 13.40 [10.00, 17.40] | 23.40 [19.40, 27.40] | 24.00 [16.00, 33.00] | 1.00 [0.00, 3.00] |
| PV_CONTROL_CHANGE | 24.40 [19.20, 29.20] | 38.20 [32.80, 43.20] | 44.00 [34.00, 54.00] | 5.00 [1.00, 9.00] |

### ood_test — estimate [95% CI], %

| Benign group | Proposed | GRU_FULL | LightGBM Full16 | Combined PF+Command |
|---|---:|---:|---:|---:|
| OVERALL_BENIGN | 23.60 [21.68, 25.40] | 46.32 [44.36, 48.20] | 62.60 [58.39, 66.60] | 20.40 [20.00, 21.00] |
| BESS_TRANSITION | 44.20 [38.20, 49.40] | 54.20 [50.20, 58.00] | 58.00 [49.00, 68.00] | 100.00 [100.00, 100.00] |
| LOAD_RAMP | 16.00 [12.20, 19.40] | 41.20 [36.59, 45.60] | 82.00 [74.00, 90.00] | 1.00 [0.00, 3.00] |
| LOAD_STEP | 15.20 [12.00, 18.80] | 45.60 [41.40, 49.60] | 75.00 [66.97, 83.00] | 0.00 [0.00, 0.00] |
| PV_CLOUD | 12.80 [9.20, 16.40] | 32.40 [28.20, 36.60] | 37.00 [28.00, 47.00] | 1.00 [0.00, 3.00] |
| PV_CONTROL_CHANGE | 29.80 [24.00, 34.80] | 58.20 [53.40, 63.00] | 61.00 [51.00, 70.00] | 0.00 [0.00, 0.00] |

## Window FPR — frozen Step-14 primary method table (parity checked)

### id_test — estimate [95% CI], %

| Benign family | Proposed | GRU_FULL | LightGBM Full16 | Combined PF+Command |
|---|---:|---:|---:|---:|
| BESS_TRANSITION | 0.95 [0.67, 1.32] | 1.21 [1.07, 1.35] | 0.47 [0.33, 0.63] | 4.65 [4.26, 5.07] |
| LOAD_RAMP | 0.74 [0.39, 1.16] | 0.88 [0.72, 1.07] | 2.18 [1.35, 3.19] | 0.01 [0.00, 0.03] |
| LOAD_STEP | 0.93 [0.50, 1.48] | 1.07 [0.85, 1.30] | 1.66 [1.02, 2.55] | 0.03 [0.00, 0.06] |
| PV_CLOUD | 0.71 [0.40, 1.09] | 0.65 [0.49, 0.81] | 0.28 [0.17, 0.39] | 0.01 [0.00, 0.03] |
| PV_CONTROL_CHANGE | 0.72 [0.45, 1.10] | 0.94 [0.79, 1.09] | 0.65 [0.46, 0.87] | 0.05 [0.01, 0.08] |

### ood_test — estimate [95% CI], %

| Benign family | Proposed | GRU_FULL | LightGBM Full16 | Combined PF+Command |
|---|---:|---:|---:|---:|
| BESS_TRANSITION | 0.59 [0.49, 0.67] | 1.80 [1.56, 2.03] | 1.04 [0.81, 1.28] | 4.79 [4.34, 5.23] |
| LOAD_RAMP | 0.24 [0.17, 0.32] | 1.62 [1.38, 1.90] | 1.72 [1.44, 2.00] | 0.01 [0.00, 0.03] |
| LOAD_STEP | 0.23 [0.17, 0.30] | 1.69 [1.46, 1.96] | 1.64 [1.36, 1.96] | 0.00 [0.00, 0.00] |
| PV_CLOUD | 0.44 [0.24, 0.67] | 1.06 [0.87, 1.25] | 0.49 [0.34, 0.63] | 0.01 [0.00, 0.03] |
| PV_CONTROL_CHANGE | 0.38 [0.30, 0.45] | 1.87 [1.65, 2.11] | 1.39 [1.02, 1.79] | 0.00 [0.00, 0.00] |

## All configurations

Full primary and secondary reports for **all 36 frozen model/seed configurations**, plus six separate five-seed architecture averages, are in the attached CSV files.

**Interpretation guard:** 1% CAL constraint applied to benign *window* FPR, not scenario alarm rate; one alarm in 109 windows causes a positive scenario. The Combined PF+Command baseline is design-designated, not empirically proven “best”.
