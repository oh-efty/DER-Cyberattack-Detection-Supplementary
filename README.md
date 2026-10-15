# Benign-Aware ID/OOD Cyberattack Detection — Supplementary Results

Supplementary **frozen evaluation results** for the manuscript
*Benign-Aware ID/OOD Evaluation of Physics-Guided Graph-Temporal and Tree-Based Cyberattack Detection in DER-Integrated Distribution Networks*.

## Scope and provenance

The study uses a simulated IEEE 33-bus distribution feeder with DERs. Files in this repository are **frozen, read-only results and derived plotting/table scripts**; publishing them does **not** constitute a new simulation, retraining, threshold selection, or evaluation. The repository does not contain the full raw simulation dataset or trained checkpoints. Check the manuscript for scenario and metric definitions.

- Five benign scenario families and nine attack families.
- Scenario-grouped FIT/CAL/validation/ID/OOD protocol.
- Primary CAL thresholds target at most 1% benign-family endpoint FPR while maximizing attack-active recall.
- P1: attack-scenario detection; P2: benign-window FPR; P3: detector-gated nine-class Macro-F1; gated localization Top-1/Top-3.
- Paired family-stratified, scenario-cluster bootstrap with 1,000 draws; intervals are 95% percentile CIs. Neural results summarize five fixed seeds.
- Scenario-score PR/AUROC analyses are **exploratory and post-hoc**, not changes to the CAL-frozen operating points.

## Repository layout

- `frozen_archives/`: original Step-14 and Step-14A results ZIPs, byte-for-byte unchanged.
- `results/step14/`: accessible CSV results, documentation, integrity manifest (including P1/P2/P3, localization, ablation, family results, paired differences, PR/AUROC).
- `results/step14A/`: benign-window FPR and benign-scenario alarm rate CSVs plus manifest.
- `scripts/`: read-only scripts generating paper Fig. 2, Fig. 3, Fig. 4, and Tables III–IV directly from frozen ZIPs.
- `figures/`: paper-facing vector PDF figures. Fig. 3 panels (a) and (b) are stacked in one PDF.
- `tables/`: IEEE LaTeX tables (including the full-CI Table III and compact paper version).
- `SHA256SUMS.txt`: SHA-256 hashes of the included files, excluding this checksum file.

## Integrity

Expected SHA-256 hashes of **manifest JSON bytes inside source ZIPs**:

| Frozen pack | SHA-256 of embedded manifest JSON |
|---|---|
| Step-14 | `9a62c600aca150f4a334e91a21201cd50d9e87eeb4a9802b92b652ea1efd127d` |
| Step-14A | `4491141226912f5861b2cb551a7db51f1cb278850f2d8d4cd70a47ce57674d91` |

The manifest JSON inside Step-14 lists hashes under `file_sha256`, and Step-14A under `files_sha256`. Both archives and every manifest-listed member were verified before preparing this bundle. The derived scripts re-check integrity before plotting.

## Regenerate figures and tables

Use Python 3 with `numpy`, `pandas`, and `matplotlib`. The combined Fig. 3 script also needs `PyMuPDF` (imported as `fitz`). Example (from repository root):

```bash
python scripts/generate_Fig2_Attack_Family_Heatmap_READONLY.py --zip frozen_archives/stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip --outdir generated/Fig2
python scripts/generate_Fig3a_Benign_Alarm_Reliability_READONLY.py --zip frozen_archives/stage3_step14A_benign_alarm_scenario_window_FPR_READONLY_v1.zip --outdir generated/Fig3a
python scripts/generate_Fig3_Combined_READONLY.py --step14 frozen_archives/stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip --fig3a generated/Fig3a/Fig3a_OOD_Benign_Scenario_Alarms.pdf --outdir generated/Fig3
python scripts/generate_Fig4_OOD_PR_from_Step14_READONLY.py --zip frozen_archives/stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip --outdir generated/Fig4
python scripts/generate_Table_III_from_Step14_READONLY.py --zip frozen_archives/stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip --output generated/Table_III.tex
python scripts/generate_Table_IV_Ablation_from_Step14_READONLY.py --zip frozen_archives/stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip --output generated/Table_IV.tex
```

Notes: Generated plot names and appearance may differ from original plotting drafts while underlying frozen values and intervals remain fixed. Check the results manifests for the precise supported scope; this repository is not a claim of field deployment or generalization to untested feeders.

## Availability

Results and reporting scripts are provided for transparency. Raw training data, original scenario generator, and trained model checkpoints are not included in this supplementary package. No software license is asserted until the repository owner selects one.
