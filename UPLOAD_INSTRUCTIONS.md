# Publish the frozen supplementary results

This repository is the intended public location for the manuscript’s supplementary data. The frozen data and reproducibility package has been prepared and SHA-256-checked locally, but the full binary/CSV package must be pushed from the research PC.

## Windows PowerShell instructions

1. Download `DER-Cyberattack-Detection-Supplementary_UPLOAD_READY.zip` from the related ChatGPT session and extract all files into one folder.
2. Confirm that `README.md`, `SHA256SUMS.txt`, `publish_to_github.ps1`, and the `results/`, `figures/`, `tables/`, `scripts/`, and `frozen_archives/` folders are present.
3. Install Git for Windows if needed, and authenticate to GitHub with your account.
4. Open PowerShell in the extracted folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\publish_to_github.ps1
```

5. The script checks SHA-256 hashes of all packaged files, clones this repository, stages the supplementary files, shows a file list, and pauses. Type `PUBLISH` to authorize the GitHub commit and push.
6. Check the public repo for `results/step14/`, `results/step14A/`, `figures/`, and `tables/`, and confirm all uploads completed.

## Scientific scope

- Supplementary artifacts are **frozen Step-14 and Step-14A results** and scripts for derived tables and plots, not new simulations.
- Full CI CSVs are included; the manuscript’s compact Tables III–IV and Figures 2–4 have matching supporting artifacts.
- Scenario-score AUROC/PR summaries are post-hoc diagnostics, not recalibrated operating-point results.
- Raw scenario generation data, trained neural checkpoints, and the training pipeline are **not included** in this results-only package.

**Do not claim the full supplementary package is online until the final push has been checked.**