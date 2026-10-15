"""Read-only, SHA-gated single-column IEEE Table IV generator.

Use in notebook:
%run "D:\\Google COLAB\\generate_Table_IV_Ablation_from_Step14_READONLY.py" --zip "D:\\ICREST_Cybersecurity\\stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip" --output "D:\\Google COLAB\\Table_IV_Output\\Table_IV_Physics_Feature_Ablation_REVIEW.tex"

NO training, inference, threshold adjustment, or input writes.
Source: frozen Step-14 step14_ablation_paired_difference_CI.csv, OOD, primary.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

EXPECTED_MANIFEST_SHA256 = '9a62c600aca150f4a334e91a21201cd50d9e87eeb4a9802b92b652ea1efd127d'
CONTRASTS = [
    ('lgb_pf_vs_base', r'LGBM: +PF'),
    ('neural_pf_vs_base', r'GCN--GRU: +PF'),
    ('lgb_full_vs_pf', r'LGBM: +Cmd'),
    ('neural_proposed_vs_pf', r'GCN--GRU: +Cmd'),
]
METRICS = ('P1','P3','Loc_Top1')


def hash256(data):
    return hashlib.sha256(data).hexdigest()


def fetch_one(z, name):
    names = [n for n in z.namelist() if n.rsplit('/', 1)[-1] == name]
    if len(names) != 1:
        raise ValueError(f'Expected one {name}; found {len(names)}')
    return z.read(names[0])


def metric_cell(row):
    n = int(row['valid_replicates'])
    if n == 0:
        if row['estimate'].strip().lower() not in ('','nan','n/a'):
            raise ValueError('Inconsistent N/A in ablation file')
        return r'--'
    if n != 1000:
        raise ValueError(f'Expected 1000 bootstrap draws, got {n}')
    est, lo, hi = (float(row[k]) for k in ('estimate','ci95_lower','ci95_upper'))
    if not lo <= est <= hi:
        raise ValueError('Estimate is outside reported confidence interval')
    # Two-line layout avoids reducing entire table below IEEE scriptsize.
    return r'\shortstack{' + f'{est:+.1f}' + r'\\{' + f'[{lo:+.1f},{hi:+.1f}]' + '}}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with ZipFile(args.zip) as z:
        mraw = fetch_one(z, 'step14_final_pack_manifest.json')
        if hash256(mraw) != EXPECTED_MANIFEST_SHA256:
            raise RuntimeError('STOP: frozen manifest SHA mismatch')
        manifest = json.loads(mraw)
        for name, want in manifest['file_sha256'].items():
            actual = hash256(fetch_one(z,name))
            if actual != want:
                raise RuntimeError(f'STOP: SHA mismatch: {name}')
        src = fetch_one(z,'step14_ablation_paired_difference_CI.csv')
    srcrows = list(csv.DictReader(io.StringIO(src.decode('utf-8-sig'))))
    desired = {(c,m) for c,_ in CONTRASTS for m in METRICS}
    subset = [r for r in srcrows if r['split']=='ood_test' and r['operating_point']=='primary' and (r['comparison'],r['metric']) in desired]
    rows = {(r['comparison'],r['metric']):r for r in subset}
    if len(subset)!=len(desired) or set(rows)!=desired:
        raise RuntimeError('STOP: OOD ablation row mismatch or duplicates')
    for r in rows.values():
        if r['analysis_status']!='exploratory_ablation' or r['difference_units']!='percentage_points':
            raise RuntimeError('STOP: unexpected ablation metadata')
    latex = [
        r'% REVIEW ONLY, pending user approval; source is SHA-verified frozen Step-14 OOD paired differences.',
        r'% Requires \usepackage{booktabs}; single-column IEEE table.',
        r'\begin{table}[!t]',
        r'\caption{OOD feature-ablation changes (percentage points)}',
        r'\label{tab:feature_ablation}',
        r'\centering',
        r'\scriptsize',
        r'\setlength{\tabcolsep}{3.0pt}',
        r'\renewcommand{\arraystretch}{1.05}',
        r'\begin{tabular}{@{}lccc@{}}',
        r'\toprule',
        r'\textbf{Addition} & \textbf{$\Delta$P1} & \textbf{$\Delta$P3} & \textbf{$\Delta$Top-1} \\',
        r'\midrule'
    ]
    for i,(name,label) in enumerate(CONTRASTS):
        cells=[metric_cell(rows[(name,m)]) for m in METRICS]
        latex.append(label + ' & ' + ' & '.join(cells) + r' \\')
        if i==1:
            latex.append(r'\addlinespace[2pt]\midrule')
    latex += [
        r'\bottomrule',
        r'\end{tabular}',
        r'\vspace{2pt}',
        r'\par\vspace{2pt}',
        r'\begin{minipage}{0.98\columnwidth}',
        r'\fontsize{6.7}{7.6}\selectfont',
        r'Values are paired differences [95\% CI] at frozen primary thresholds.',
        r'+PF: Base12 $\to$ PF14; +Cmd: PF14 $\to$ Full16.',
        r'LGBM Base12/PF14 are detection-only (--: not applicable).',
        r'Exploratory ablations; intervals are unadjusted.',
        r'\end{minipage}',
        r'\end{table}',
        ''
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(latex),encoding='utf-8')
    print('PASS: frozen Step-14 manifest and all source SHAs verified')
    print(f'PASS: {len(rows)} contrast × metric records verified (OOD primary)')
    print('OUTPUT:',args.output)
    print('TABLE SHA-256:',hash256(args.output.read_bytes()))

if __name__=='__main__':
    main()
