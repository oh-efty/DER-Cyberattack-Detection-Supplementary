"""Read-only Fig. 3(a): OOD benign-scenario alarms, frozen primary thresholds.

Notebook example:
%run "D:\\Google COLAB\\generate_Fig3a_Benign_Alarm_Reliability_READONLY.py" --zip "D:\\ICREST_Cybersecurity\\stage3_step14A_benign_alarm_scenario_window_FPR_READONLY_v1.zip" --outdir "D:\\Google COLAB\\Fig3_Output"

Source: STEP14A frozen benign scenario/window report. Primary operating point
only; error bars are scenario-cluster bootstrap percentile 95% CIs.
No retraining, recalibration, resampling or new simulations.
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

FROZEN_MANIFEST_SHA = '4491141226912f5861b2cb551a7db51f1cb278850f2d8d4cd70a47ce57674d91'
FROZEN_STEP14_MANIFEST_SHA = '9a62c600aca150f4a334e91a21201cd50d9e87eeb4a9802b92b652ea1efd127d'
METHODS = [
    ('PROPOSED_GCN_GRU_FULL__five_seed_mean', 'Proposed'),
    ('GRU_FULL__five_seed_mean', 'GRU'),
    ('LightGBM_FULL16', 'LightGBM'),
    ('COMBINED_PF_COMMAND_THRESHOLD', 'Combined'),
]
GROUPS = [
    ('OVERALL_BENIGN', 'All benign'),
    ('BESS_TRANSITION', 'BESS transition'),
    ('PV_CLOUD', 'PV cloud'),
]

def sha256(blob):
    return hashlib.sha256(blob).hexdigest()

def read_exact(zf, filename):
    paths = [name for name in zf.namelist()
             if name == filename or name.endswith('/' + filename)]
    if len(paths) != 1:
        raise RuntimeError('STOP: expected exactly one %s, found %d' % (filename, len(paths)))
    return zf.read(paths[0])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zip', type=Path, required=True, help='Frozen Step14A benign scenario/window ZIP (NOT the Step14 main ZIP)')
    ap.add_argument('--outdir', type=Path, required=True)
    args = ap.parse_args()
    with ZipFile(args.zip) as zf:
        mb = read_exact(zf, 'step14A_final_report_manifest.json')
        if sha256(mb) != FROZEN_MANIFEST_SHA:
            raise RuntimeError('STOP: Step14A approved manifest SHA-256 mismatch')
        meta = json.loads(mb)
        if meta.get('source_step14_sha256') != FROZEN_STEP14_MANIFEST_SHA:
            raise RuntimeError('STOP: inconsistent Step14 provenance')
        if meta.get('bootstrap_replicates') != 1000 or meta.get('scenario_denominator_overall') != 500 or meta.get('scenario_denominator_per_family') != 100:
            raise RuntimeError('STOP: frozen bootstrap or denominator mismatch')
        for fn, sha in meta['files_sha256'].items():
            if sha256(read_exact(zf, fn)) != sha:
                raise RuntimeError('STOP: packed file hash mismatch: ' + fn)
        scenario = pd.read_csv(io.BytesIO(read_exact(zf, 'step14A_all36_scenario_alarm_primary_secondary_CI.csv')))
        windows = pd.read_csv(io.BytesIO(read_exact(zf, 'step14A_all36_benign_window_FPR_primary_secondary_CI.csv')))
    required_scenario = {'split','operating_point','method','family','n_benign_scenarios','estimate_pct','ci95_lower_pct','ci95_upper_pct','bootstrap_replicates','aggregation'}
    required_window = {'split','operating_point','method','family','n_benign_windows','estimate_pct','bootstrap_replicates'}
    if not required_scenario.issubset(scenario.columns) or not required_window.issubset(windows.columns):
        raise RuntimeError('STOP: report CSV schema mismatch')
    if len(scenario) != 1008 or len(windows) != 1008:
        raise RuntimeError('STOP: expected 1008 frozen report rows per CSV')
    keys=['split','operating_point','method','family']
    if scenario.duplicated(keys).any() or windows.duplicated(keys).any():
        raise RuntimeError('STOP: duplicate report keys')
    ss=scenario[(scenario.split=='ood_test')&(scenario.operating_point=='primary')].set_index(['family','method'])
    ww=windows[(windows.split=='ood_test')&(windows.operating_point=='primary')].set_index(['family','method'])
    y=np.zeros((len(GROUPS),len(METHODS)))
    low=np.zeros_like(y); high=np.zeros_like(y)
    for gi,(group, _) in enumerate(GROUPS):
        for mi,(method, _) in enumerate(METHODS):
            if (group,method) not in ss.index or (group,method) not in ww.index:
                raise RuntimeError('STOP: absent source report row: %s / %s' % (group,method))
            r=ss.loc[(group,method)]; w=ww.loc[(group,method)]
            expected_n = 500 if group=='OVERALL_BENIGN' else 100
            expected_w = 54500 if group=='OVERALL_BENIGN' else 10900
            if int(r['n_benign_scenarios'])!=expected_n or int(w['n_benign_windows'])!=expected_w or int(r['bootstrap_replicates'])!=1000 or int(w['bootstrap_replicates'])!=1000:
                raise RuntimeError('STOP: inconsistent scenario/window counts or bootstrap')
            if method.endswith('__five_seed_mean') and r['aggregation'] != 'mean_over_5_seed_metrics_per_draw':
                raise RuntimeError('STOP: unexpected neural aggregation')
            point=float(r['estimate_pct']); lo=float(r['ci95_lower_pct']); hi=float(r['ci95_upper_pct'])
            if not (0 <= lo <= point <= hi <= 100):
                raise RuntimeError('STOP: invalid CI bounds')
            y[gi,mi],low[gi,mi],high[gi,mi]=point,lo,hi

    fig,ax=plt.subplots(figsize=(3.48,2.15))
    x=np.arange(len(GROUPS)); width=.19
    hatch=['', '///', '...', 'xx']
    for j,(_,label) in enumerate(METHODS):
        xpos=x+(j-1.5)*width
        bars=ax.bar(xpos, y[:,j], width=.175, label=label,
                    linewidth=.4, edgecolor='black', hatch=hatch[j], zorder=2)
        ax.errorbar(xpos, y[:,j], yerr=[y[:,j]-low[:,j],high[:,j]-y[:,j]],
                    fmt='none', ecolor='black', elinewidth=.7, capsize=1.5, capthick=.7, zorder=3)
    ax.set_ylim(0,111)
    ax.set_ylabel('Benign scenarios with alarm (%)',fontsize=7.3)
    ax.set_xticks(x, [name for _,name in GROUPS],fontsize=7)
    ax.tick_params(axis='y',labelsize=7,length=2)
    ax.tick_params(axis='x',length=0,pad=3)
    ax.yaxis.grid(True, linewidth=.35, alpha=.4, zorder=0)
    ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='upper center',ncol=4,bbox_to_anchor=(.5,1.17),
              fontsize=6.4,frameon=False, columnspacing=.75,handlelength=1.4,handletextpad=.25)
    fig.subplots_adjust(left=.17,right=.985,bottom=.16,top=.81)
    args.outdir.mkdir(parents=True,exist_ok=True)
    pdf=args.outdir/'Fig3a_OOD_Benign_Scenario_Alarms.pdf'
    png=args.outdir/'Fig3a_OOD_Benign_Scenario_Alarms.png'
    fig.savefig(pdf,bbox_inches='tight',pad_inches=.025)
    fig.savefig(png,dpi=350,bbox_inches='tight',pad_inches=.025)
    plt.close(fig)
    print('PASS: Step14A frozen manifest, all source SHA-256, frozen Step14 linkage')
    print('PASS: 12 OOD primary benign-scenario alarm estimates and paired-draw bootstrap CI bounds')
    print('NOTE: error bars are individual-method 95% CIs, not paired method-difference CIs')
    print('NOTE: window FPR is a different metric; see Table III / frozen Step14A CSV')
    print('PDF:', pdf)
    print('PNG:', png)
    for gi,(fam,_) in enumerate(GROUPS):
        print(fam+': '+', '.join(f'{label} {y[gi,j]:.2f} [{low[gi,j]:.2f},{high[gi,j]:.2f}]' for j,(_,label) in enumerate(METHODS)))

if __name__=='__main__':
    main()
