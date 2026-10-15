"""Generate IEEE one-column Fig. 2 from SHA-pinned, frozen Step-14 family-P1 CSV.

Run in Jupyter Notebook (no re-training or recalibration):
%run "D:\\Google COLAB\\generate_Fig2_Attack_Family_Heatmap_READONLY.py" --zip "D:\\ICREST_Cybersecurity\\stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip" --outdir "D:\\Google COLAB\\Fig2_Output"

The plot contains OOD family P1 point estimates. CI values remain in the source CSV
and selected intervals are reported in the manuscript text; this is NOT a CI plot.
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
import numpy as np
import pandas as pd

EXPECTED_MANIFEST_SHA = '9a62c600aca150f4a334e91a21201cd50d9e87eeb4a9802b92b652ea1efd127d'
FAMILIES = [
    ('CMD_BESS_OFFSET', 'BESS offset'),
    ('CMD_BESS_SIGN_FLIP', 'BESS sign flip'),
    ('CMD_PV_CURTAILMENT', 'PV curtailment'),
    ('CMD_PV_Q_SHIFT', 'PV Q shift'),
    ('MEAS_BIAS', 'Meas. bias'),
    ('MEAS_PULSE', 'Meas. pulse'),
    ('MEAS_RAMP', 'Meas. ramp'),
    ('MEAS_SCALING', 'Meas. scaling'),
    ('MEAS_STEALTH_AC', 'Meas. stealth AC'),
]
METHODS = [
    ('PROPOSED_GCN_GRU_FULL', 'Proposed'),
    ('GRU_FULL', 'GRU'),
    ('LightGBM_FULL16', 'LightGBM'),
    ('COMBINED_PF_COMMAND_THRESHOLD', 'Combined'),
]

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def exact_file(zf, filename):
    hits = [name for name in zf.namelist()
            if name == filename or name.endswith('/' + filename)]
    if len(hits) != 1:
        raise RuntimeError(f'STOP: expected exactly one {filename}, got {len(hits)}')
    return zf.read(hits[0])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--outdir', type=Path, required=True)
    args = parser.parse_args()

    with ZipFile(args.zip) as zf:
        manifest_bytes = exact_file(zf, 'step14_final_pack_manifest.json')
        if sha256(manifest_bytes) != EXPECTED_MANIFEST_SHA:
            raise RuntimeError('STOP: frozen manifest SHA-256 differs from approved version')
        manifest = json.loads(manifest_bytes)
        for filename, expected_hash in manifest['file_sha256'].items():
            if sha256(exact_file(zf, filename)) != expected_hash:
                raise RuntimeError(f'STOP: frozen source SHA-256 mismatch: {filename}')
        data = pd.read_csv(io.BytesIO(exact_file(zf, 'step14_per_family_attack_P1_CI.csv')))

    required_cols = {'split','method','family','n_attack_scenarios',
                     'estimate','ci95_lower','ci95_upper','valid_replicates'}
    if not required_cols.issubset(data.columns) or len(data) != 72:
        raise RuntimeError('STOP: unexpected frozen family table schema/row count')
    if data.duplicated(['split', 'method', 'family']).any():
        raise RuntimeError('STOP: duplicate method-family rows')
    selected = data[data['split'] == 'ood_test'].set_index(['family','method'])
    if len(selected) != 36:
        raise RuntimeError('STOP: expected exactly 36 OOD family/method entries')
    records = []
    for f, _ in FAMILIES:
        row = []
        for m, _ in METHODS:
            if (f, m) not in selected.index:
                raise RuntimeError(f'STOP: missing {f}/{m}')
            r = selected.loc[(f, m)]
            if int(r['n_attack_scenarios']) != 100 or int(r['valid_replicates']) != 1000:
                raise RuntimeError(f'STOP: unexpected denominator/bootstrap for {f}/{m}')
            estimate = float(r['estimate'])
            if not (0 <= estimate <= 100):
                raise RuntimeError('STOP: out-of-range P1')
            row.append(estimate)
        records.append(row)
    matrix = np.asarray(records)

    fig, ax = plt.subplots(figsize=(3.47, 2.88))
    plot = ax.imshow(matrix, vmin=0, vmax=100, aspect='auto', interpolation='nearest')
    ax.set_xticks(range(4), [name for _, name in METHODS], fontsize=6.6)
    ax.set_yticks(range(9), [name for _, name in FAMILIES], fontsize=6.8)
    ax.tick_params(axis='both', length=0, pad=2)
    ax.axhline(3.5, color='white', linewidth=1.8)
    # Label the cell values; background brightness controls contrast.
    for i in range(9):
        for j in range(4):
            v = matrix[i, j]
            label = f'{v:.0f}' if abs(v-round(v)) < 1e-8 else f'{v:.1f}'
            rgba = plot.cmap(plot.norm(v))
            luma = 0.2126*rgba[0] + 0.7152*rgba[1] + 0.0722*rgba[2]
            ax.text(j, i, label, ha='center', va='center', fontsize=6.6,
                    color='black' if luma > 0.49 else 'white')
    for spine in ax.spines.values():
        spine.set_visible(False)
    cb = fig.colorbar(plot, ax=ax, fraction=0.045, pad=0.025, ticks=[0, 50, 100])
    cb.ax.tick_params(labelsize=6, length=2, pad=1)
    cb.set_label('P1 (%)', fontsize=6.5, labelpad=1)
    fig.subplots_adjust(left=.34, right=.935, bottom=.105, top=.99)

    args.outdir.mkdir(parents=True, exist_ok=True)
    pdf = args.outdir/'Fig2_OOD_Attack_Family_Heatmap.pdf'
    png = args.outdir/'Fig2_OOD_Attack_Family_Heatmap.png'
    fig.savefig(pdf, bbox_inches='tight', pad_inches=.025)
    fig.savefig(png, dpi=350, bbox_inches='tight', pad_inches=.025)
    plt.close(fig)

    print('PASS: approved manifest SHA and every packed source-file SHA verified')
    print('PASS: 36 OOD family-P1 values, 100 attack scenarios/family, 1,000 CI resamples')
    print('NOTE: plot annotates estimates; 95% CIs are in frozen CSV, not plotted')
    print('PDF:', pdf)
    print('PNG:', png)

if __name__ == '__main__':
    main()
