"""Generate Fig. 4 from frozen Step-14 PR grid and AUPRC CSV.

No simulation, training, threshold selection, or writes to the source ZIP.

Notebook example:
    %run "D:\\Google COLAB\\generate_Fig4_OOD_PR_from_Step14_READONLY.py" --zip "D:\\ICREST_Cybersecurity\\stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip" --outdir "D:\\Google COLAB\\Fig4_Output"
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

EXPECTED_MANIFEST_SHA = '9a62c600aca150f4a334e91a21201cd50d9e87eeb4a9802b92b652ea1efd127d'
METHODS = [
    ('PROPOSED_GCN_GRU_FULL', 'Proposed GCN--GRU'),
    ('GRU_FULL', 'GRU Full16'),
    ('LightGBM_FULL16', 'LightGBM Full16'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def get_file(zf, basename):
    matches = [n for n in zf.namelist() if n == basename or n.endswith('/' + basename)]
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one {basename}, found {len(matches)}')
    return zf.read(matches[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zip', type=Path, required=True)
    ap.add_argument('--outdir', type=Path, required=True)
    args = ap.parse_args()

    with ZipFile(args.zip) as zf:
        mbytes = get_file(zf, 'step14_final_pack_manifest.json')
        if sha(mbytes) != EXPECTED_MANIFEST_SHA:
            raise RuntimeError('STOP: frozen manifest SHA mismatch')
        manifest = json.loads(mbytes)
        for fn, expected in manifest['file_sha256'].items():
            if sha(get_file(zf, fn)) != expected:
                raise RuntimeError(f'STOP: source-file SHA mismatch: {fn}')
        grid = pd.read_csv(io.BytesIO(get_file(zf, 'step14_scenario_roc_pr_pointwise_95CI_grid.csv')))
        summary = pd.read_csv(io.BytesIO(get_file(zf, 'step14_scenario_AUPRC_AUROC_matched_FPR_and_CI.csv')))

    grid = grid[(grid['split'] == 'ood_test') & (grid['curve_type'] == 'PR')]
    summary = summary[(summary['split'] == 'ood_test') & (summary['metric'] == 'scenario_AUPRC')]
    if len(grid) != 303:
        raise RuntimeError(f'Unexpected PR grid length: {len(grid)}, expected 303')

    fig, ax = plt.subplots(figsize=(3.46, 2.75))
    for method, name in METHODS:
        g = grid[grid['method'] == method].sort_values('x')
        s = summary[summary['method'] == method]
        if len(g) != 101 or len(s) != 1:
            raise RuntimeError(f'Unexpected row count for {method}: PR={len(g)}, AP={len(s)}')
        if not g['band_type'].eq('pointwise_95pct_not_simultaneous').all():
            raise RuntimeError('Unexpected bootstrap band definition')
        ap_value = float(s.iloc[0]['estimate'])
        line, = ax.plot(g['x'], g['mean_y'], linewidth=1.5,
                        label=f'{name} (AP={ap_value:.3f})')
        ax.fill_between(g['x'], g['ci95_lower_y'], g['ci95_upper_y'],
                        color=line.get_color(), alpha=0.10, linewidth=0)

    ax.set_xlabel('Scenario-level recall', fontsize=8)
    ax.set_ylabel('Precision', fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0.60, 1.01)  # zoomed precision axis: disclose in plot
    ax.tick_params(labelsize=7)
    ax.grid(alpha=0.16)
    ax.legend(loc='lower left', fontsize=6.8, frameon=True)
    fig.tight_layout(pad=0.55)

    args.outdir.mkdir(parents=True, exist_ok=True)
    pdf = args.outdir / 'Fig4_OOD_PR.pdf'
    png = args.outdir / 'Fig4_OOD_PR.png'
    fig.savefig(pdf, bbox_inches='tight')
    fig.savefig(png, dpi=350, bbox_inches='tight')
    plt.close(fig)
    print('PASS: frozen manifest and all source-file SHA checks')
    print('PASS: 303 OOD PR-grid rows and three frozen AUPRC values')
    print('PDF:', pdf)
    print('PNG:', png)
    print('NOTE: precision axis intentionally zoomed to 0.60--1.01')


if __name__ == '__main__':
    main()
