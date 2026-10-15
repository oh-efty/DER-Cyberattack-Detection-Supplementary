"""Generate IEEE Table III from an immutable frozen Step-14 results ZIP.

No training, evaluation, threshold changes, or writes to the source pack.

Example (run from a Jupyter cell using %run):
%run generate_Table_III_from_Step14_READONLY.py --zip r"D:\\YOUR_FOLDER\\stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip" --output r"D:\\YOUR_FOLDER\\Table_III_Primary_Results_REVIEW.tex"
"""
import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from zipfile import ZipFile

MANIFEST_SHA = "9a62c600aca150f4a334e91a21201cd50d9e87eeb4a9802b92b652ea1efd127d"
METHODS = [
    ("PROPOSED_GCN_GRU_FULL", r"Proposed GCN--GRU"),
    ("GRU_FULL", "GRU Full16"),
    ("LightGBM_FULL16", "LightGBM Full16"),
    ("COMBINED_PF_COMMAND_THRESHOLD", "Combined threshold"),
]
SPLITS = [("id_test", "ID"), ("ood_test", "OOD")]
METRICS = [("P1", 1), ("P2_overall", 2), ("P3", 1), ("Loc_Top1", 1), ("Loc_Top3", 1)]
VAL_RE = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*\[\s*([-+]?\d+(?:\.\d+)?)\s*,\s*([-+]?\d+(?:\.\d+)?)\s*\]\s*$")


def file_in_zip(zf, name):
    matches = [p for p in zf.namelist() if p.endswith('/' + name) or p == name]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {name} in ZIP, got {matches}")
    return zf.read(matches[0])


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def fmt(value, decimals):
    if not value or value.strip().lower() in ('nan', 'n/a'):
        return r"\textemdash"
    m = VAL_RE.fullmatch(value)
    if not m:
        raise ValueError(f"Unexpected CI format: {value!r}")
    n, lo, hi = map(float, m.groups())
    return f"{n:.{decimals}f} [{lo:.{decimals}f},{hi:.{decimals}f}]"


def main():
    pa = argparse.ArgumentParser()
    pa.add_argument('--zip', required=True, type=Path, help='Original frozen Step-14 results ZIP')
    pa.add_argument('--output', required=True, type=Path, help='Destination review .tex')
    args = pa.parse_args()
    with ZipFile(args.zip) as zf:
        mdata = file_in_zip(zf, 'step14_final_pack_manifest.json')
        if sha_bytes(mdata) != MANIFEST_SHA:
            raise RuntimeError('STOP: Step-14 manifest SHA does not match frozen expected SHA')
        manifest = json.loads(mdata)
        for fname, expected_sha in manifest['file_sha256'].items():
            raw = file_in_zip(zf, fname)
            if sha_bytes(raw) != expected_sha:
                raise RuntimeError(f'STOP: SHA mismatch in {fname}')
        source_data = file_in_zip(zf, 'step14_main_primary_and_secondary_wide.csv')
    rows = list(csv.DictReader(io.StringIO(source_data.decode('utf-8-sig'))))
    rows = {(r['split'], r['method']): r for r in rows if r['operating_point']=='primary'}
    expected = {(s,m) for s,_ in SPLITS for m,_ in METHODS}
    if set(rows) != expected:
        raise RuntimeError(f'STOP: unexpected primary rows: missing {expected-set(rows)}, extra {set(rows)-expected}')
    out = [
        r'\begin{table*}[!t]',
        r'\caption{Frozen-threshold ID/OOD performance with unadjusted 95\% scenario-cluster bootstrap confidence intervals}',
        r'\label{tab:results}',
        r'\centering',
        r'\scriptsize',
        r'\setlength{\tabcolsep}{2.1pt}',
        r'\renewcommand{\arraystretch}{1.13}',
        r'\resizebox{\textwidth}{!}{%',
        r'\begin{tabular}{llccccc}',
        r'\toprule',
        r'\textbf{Method} & \textbf{Set} & \textbf{P1 (\%)} & \textbf{P2 (\%)} & \textbf{P3 (\%)} & \textbf{Top-1 (\%)} & \textbf{Top-3 (\%)} \\',
        r'\midrule',
    ]
    for index, (model, label) in enumerate(METHODS):
        for spl, spllabel in SPLITS:
            r=rows[(spl,model)]
            fields=[fmt(r[metric], nd) for metric, nd in METRICS]
            out.append(f"{label} & {spllabel} & " + ' & '.join(fields) + r' \\')
        if index != len(METHODS)-1:
            out.append(r'\addlinespace[2pt]')
    out.extend([
        r'\bottomrule',
        r'\end{tabular}}',
        r'\vspace{0.5mm}',
        r'\begin{minipage}{0.98\textwidth}',
        r'\scriptsize',
        r'Entries show estimate [95\% CI]. P1: attack-scenario detection; P2: benign-window FPR; P3: detector-gated nine-class Macro-F1; Top-$k$: detector-gated bus localization. Neural entries are five-seed means; dashes mean the metric is inapplicable to the detection-only comparator. All results use CAL-frozen primary thresholds.',
        r'\end{minipage}',
        r'\end{table*}',
        '',
    ])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(out), encoding='utf-8')
    print('PASS: manifest and all source CSV/file SHAs verified')
    print('PASS: 8 primary method/split rows verified')
    print('OUTPUT:', args.output)
    print('TABLE SHA-256:', sha_bytes(args.output.read_bytes()))

if __name__=='__main__':
    main()
