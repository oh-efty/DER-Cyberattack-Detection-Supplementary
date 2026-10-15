"""Read-only IEEE single-column Fig. 3: user-supplied panel (a) + frozen Step14 OOD localization panel (b).

Usage in Jupyter notebook:
%run "D:\\Google COLAB\\generate_Fig3_Combined_READONLY.py" --step14 "D:\\ICREST_Cybersecurity\\stage3_step14_final_results_pack_from_frozen_STEP11_12_13_v1.zip" --fig3a "D:\\Google COLAB\\Fig3_Output\\Fig3a_OOD_Benign_Scenario_Alarms.pdf" --outdir "D:\\Google COLAB\\Fig3_Output"

Requires: pandas numpy matplotlib pymupdf (fitz). No new simulation, model fit,
threshold optimization or resampling; uses frozen 1000-draw percentile bounds.
"""
from __future__ import annotations
import argparse, hashlib, io, json
from pathlib import Path
from zipfile import ZipFile

import fitz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FROZEN_STEP14_MANIFEST_SHA = '9a62c600aca150f4a334e91a21201cd50d9e87eeb4a9802b92b652ea1efd127d'
METHODS=[('PROPOSED_GCN_GRU_FULL','Proposed','#1f77b4',''),
         ('GRU_FULL','GRU','#ff7f0e','///'),
         ('LightGBM_FULL16','LightGBM','#2ca02c','...')]
GROUPS=[('command_attack','Command'),('measurement_attack','Measurement'),('unseen_bus','Unseen bus')]

def sha256(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def get(z:ZipFile, name:str)->bytes:
    found=[k for k in z.namelist() if k==name or k.endswith('/'+name)]
    if len(found)!=1: raise RuntimeError('STOP: expected exactly one '+name+', found '+str(len(found)))
    return z.read(found[0])

def load_frozen(zipfile_path:Path):
    with ZipFile(zipfile_path) as z:
        manifest_bytes=get(z,'step14_final_pack_manifest.json')
        actual=sha256(manifest_bytes)
        if actual!=FROZEN_STEP14_MANIFEST_SHA:
            raise RuntimeError(f'STOP: wrong frozen Step14 manifest {actual}')
        manifest=json.loads(manifest_bytes)
        # Verify frozen ZIP member hashes listed in source manifest.
        integrity=manifest.get('file_sha256')
        if not isinstance(integrity,dict):
            raise RuntimeError('STOP: missing manifest files_sha256')
        for name,expected in integrity.items():
            if sha256(get(z,name))!=expected:
                raise RuntimeError('STOP: ZIP source hash mismatch '+name)
        df=pd.read_csv(io.BytesIO(get(z,'step14_localization_gated_subgroups_CI.csv')))
    required={'split','operating_point','method','group','metric','denominator_active_endpoints','context','estimate','ci95_lower','ci95_upper','valid_replicates'}
    if not required.issubset(df.columns):raise RuntimeError('STOP: subgroup schema mismatch')
    if df.duplicated(['split','operating_point','method','group','metric']).any():
        raise RuntimeError('STOP: duplicate subgroup metric rows')
    d=df[(df.split=='ood_test')&(df.operating_point=='primary')&(df.metric=='Top1')]
    rows=[]
    for group,group_display in GROUPS:
        group_rows=[]
        for method,method_display,color,hatch in METHODS:
            chosen=d[(d.group==group)&(d.method==method)]
            if len(chosen)!=1:raise RuntimeError('STOP: missing/duplicate subgroup '+str((group,method)))
            r=chosen.iloc[0]
            if r.context!='detector_gated_end_to_end' or int(r.valid_replicates)!=1000:
                raise RuntimeError('STOP: not primary detector-gated 1000-bootstrap subgroup')
            if int(r.denominator_active_endpoints)!={'command_attack':9437,'measurement_attack':10647,'unseen_bus':2233}[group]:
                raise RuntimeError('STOP: unexpected denominator '+group)
            est,lo,hi=(float(r[k]) for k in ('estimate','ci95_lower','ci95_upper'))
            if not 0<=lo<=est<=hi<=100:raise RuntimeError('STOP: invalid bounds')
            group_rows.append((est,lo,hi))
        rows.append(group_rows)
    return np.array(rows)

def make_panel_b(vals:np.ndarray, filepath:Path):
    # Match panel (a) method hues and hatched style. 'Combined' does not support localization.
    fig,ax=plt.subplots(figsize=(3.48,1.96))
    x=np.arange(3)
    for j,(_,label,color,hatch) in enumerate(METHODS):
        xx=x+(j-1)*.24
        y=vals[:,j,0];lo=vals[:,j,1];hi=vals[:,j,2]
        ax.bar(xx,y,width=.215,color=color,label=label,hatch=hatch,
               edgecolor='black',linewidth=.42,zorder=3)
        ax.errorbar(xx,y,yerr=[y-lo,hi-y],fmt='none',ecolor='black',
                    elinewidth=.72,capsize=1.4,capthick=.72,zorder=4)
    ax.set_ylim(0,108)
    ax.set_ylabel('Gated Top-1 localization (%)',fontsize=7.1)
    ax.set_xticks(x,[lab for _,lab in GROUPS],fontsize=7)
    ax.tick_params(axis='y',labelsize=7,length=2)
    ax.tick_params(axis='x',length=0,pad=3)
    ax.yaxis.grid(True,linewidth=.35,alpha=.4,zorder=0)
    ax.spines[['top','right']].set_visible(False)
    fig.subplots_adjust(left=.165,right=.987,bottom=.17,top=.96)
    fig.savefig(filepath,format='pdf',bbox_inches='tight',pad_inches=.028)
    plt.close(fig)

def assemble(panel_a:Path,panel_b:Path,outfile:Path):
    # Embed both source PDF pages as vector content on ONE PDF page (not PDF concatenation).
    with fitz.open(panel_a) as a,fitz.open(panel_b) as b:
        if a.page_count!=1 or b.page_count!=1:raise RuntimeError('STOP: both panels must have one PDF page')
        aw,ah=a[0].rect.width,a[0].rect.height
        bw,bh=b[0].rect.width,b[0].rect.height
        pagewidth=247.0
        margin=3.0
        usable=pagewidth-2*margin
        ah_scaled=ah*usable/aw
        bh_scaled=bh*usable/bw
        labelheight=13.0
        spacing=7.0
        bottom=5.0
        pageheight=labelheight+ah_scaled+spacing+labelheight+bh_scaled+bottom
        out=fitz.open();p=out.new_page(width=pagewidth,height=pageheight)
        center=pagewidth/2
        p.insert_text((center-69,9.2),'(a) Benign-scenario alarm reliability',fontsize=7.3,fontname='hebo')
        ya=labelheight
        p.show_pdf_page(fitz.Rect(margin,ya,margin+usable,ya+ah_scaled),a,0,keep_proportion=True)
        yb=ya+ah_scaled+spacing
        p.insert_text((center-70,yb+9.2),'(b) OOD gated Top-1 localization',fontsize=7.3,fontname='hebo')
        yplot=yb+labelheight
        p.show_pdf_page(fitz.Rect(margin,yplot,margin+usable,yplot+bh_scaled),b,0,keep_proportion=True)
        out.save(outfile,garbage=4,deflate=True)
        out.close()
    with fitz.open(outfile) as check:
        if check.page_count!=1:raise RuntimeError('STOP: combined output was not one-page PDF')
        print('Single combined PDF: %.2f x %.2f pt' % (check[0].rect.width,check[0].rect.height))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--step14',type=Path,required=True)
    p.add_argument('--fig3a',type=Path,required=True)
    p.add_argument('--outdir',type=Path,required=True)
    args=p.parse_args()
    if not args.fig3a.is_file():raise FileNotFoundError('Fig3a PDF not found: '+str(args.fig3a))
    vals=load_frozen(args.step14)
    args.outdir.mkdir(parents=True,exist_ok=True)
    panel_b=args.outdir/'Fig3b_OOD_Gated_Localization.pdf'
    combined=args.outdir/'Fig3_Benign_Alarms_and_OOD_Localization.pdf'
    make_panel_b(vals,panel_b)
    assemble(args.fig3a,panel_b,combined)
    print('PASS: frozen Step14 manifest and all source-file SHA-256')
    print('PASS: 9 OOD primary subgroup Top-1 values and 95% bootstrap intervals')
    print('Panel (a): user-supplied original PDF, embedded unchanged as vectors')
    print('Panel (b): 3 subgroup x 3 method localization from frozen results')
    for i,(_,label) in enumerate(GROUPS):
        print(label+': '+', '.join('%s %.2f [%.2f,%.2f]' % (METHODS[j][1],*vals[i,j]) for j in range(3)))
    print('COMBINED:',combined)
    print('PANEL B:',panel_b)
    print('SHA256:',sha256(combined.read_bytes()))

if __name__=='__main__':main()
