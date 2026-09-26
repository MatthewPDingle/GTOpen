"""Publish only the completed, separately audited archived-deal diagnostic."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import time

import psutil
from hu_frozen_root_precision_20260926 import OUT, ROOT, read, sha
from frozen_root_precision_audit_20260926 import NAMES, CONTRASTS

PREFIX='frozen-root-precision-study-v1'


def label(i):
    row,col=divmod(i,13); ranks='23456789TJQKA'
    return ranks[row]+ranks[col] if row==col else ranks[max(row,col)]+ranks[min(row,col)]+('s' if row>col else 'o')


def publish():
    rp=OUT/f'{PREFIX}-registration.json'; sp=OUT/f'{PREFIX}-result.json'
    qp=OUT/f'{PREFIX}-aggregate-audit.json'; vp=OUT/f'{PREFIX}-readback.json'
    reg=read(rp); result=read(sp); audit=read(qp); review=read(vp)
    assert read(OUT/f'{PREFIX}-status.json')['state']=='complete'
    assert result['passed'] and not result['control_only'] and not result['fresh_deals']
    assert result['registration_sha256']==sha(rp)
    assert audit['passed'] and audit['source_result_sha256']==sha(sp)
    assert audit['source_readback_sha256']==sha(vp) and review['passed']
    assert audit['reviewer_sha256']==sha(ROOT/'tools/research/frozen_root_precision_audit_20260926.py')
    ap=Path(reg['store'])/'analysis.json'; assert sha(ap)==result['analysis_sha256']==audit['analysis_sha256']
    analysis=read(ap); assert analysis['deals']==65536 and len(result['jobs'])==2048
    assert [x['source'] for x in result['jobs']]==[f'test-{i:06d}' for i in range(0,65536,32)]
    counts=[x['count'] for x in analysis['banks'][0]['classes']]
    assert min(counts)>1 and sum(counts)==65536
    # This publication retains native ordering, not display-grid ordering.
    assert [label(i) for i in (0,168,167,155)]==['22','AA','AKs','AKo']
    catalog=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    assert sha(catalog)=='57834fc6b59173f22b5027bcec1f32e649060463fd275bc80fb7a58a4cfc6629'
    checked=set()
    for row in read(catalog)['native_observations']:
        if row['player']!=0:continue
        key=int(row['observation']['lo']);a=key&63;b=(key>>6)&63
        hi,lo=sorted((a//4,b//4),reverse=True);ranks='23456789TJQKA'
        actual=ranks[hi]+ranks[lo]+('' if hi==lo else 's' if a%4==b%4 else 'o')
        assert label(row['hand_class'])==actual
        checked.add(row['hand_class'])
    assert checked==set(range(169))
    target=OUT/'frozen-root-precision-final-analysis.json'
    with target.open('xb') as f:f.write(ap.read_bytes())
    with (OUT/'frozen-root-precision-class-values.csv').open('x',newline='') as f:
        w=csv.writer(f)
        w.writerow(['bank','native_class','hand','count','entry_mass']+[f'{k}_{s}' for k in CONTRASTS for s in ('mean_bb','descriptive_se_bb')]+['even_preferred_nonjam','odd_preferred_nonjam'])
        for b,bank in enumerate(analysis['banks']):
            for row in bank['classes']:
                w.writerow([NAMES[b],row['hand_class'],label(row['hand_class']),row['count'],row['entry_mass']]+[z for k in range(3) for z in (row['contrast_means'][k],row['descriptive_standard_errors'][k])]+[h['maximizing_non_jam_action'] for h in row['halves']])
    with (OUT/'frozen-root-precision-paired-bank-values.csv').open('x',newline='') as f:
        w=csv.writer(f);w.writerow(['bank_difference','native_class','hand','entry_mass','contrast','count','mean_bb','paired_descriptive_se_bb'])
        for pair in audit['paired_banks']:
            for row in pair['classes']:
                for k,m in enumerate(row['contrasts']):
                    w.writerow([pair['direction'],row['hand_class'],label(row['hand_class']),row['entry_mass'],CONTRASTS[k],m['count'],m['mean'],m['standard_error']])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
    x=np.arange(4)
    for k,title in enumerate(('Call - fold','Raise - fold','Raise - call')):
        axes[0].bar(x+(k-1)*.24,[b['rms_class_standard_error_on_covered_mass'][k] for b in analysis['banks']],width=.24,label=title)
    axes[0].set_xticks(x,NAMES,rotation=15);axes[0].set_ylabel('Weighted RMS class standard error (bb)');axes[0].legend()
    disagreements=[100*b['half_maximizer_disagreement_entry_mass'] for b in analysis['banks']]
    axes[1].bar(x,disagreements,color='#377aa6');axes[1].set_xticks(x,NAMES,rotation=15)
    axes[1].set_ylabel('Entry mass with different preferred action (%)')
    for i,y in enumerate(disagreements):axes[1].text(i,y,f'{y:.1f}%',ha='center',va='bottom')
    axes[1].set_ylim(0,max(5,max(disagreements)*1.2))
    fig.suptitle('Fixed continuations: uncertainty across saved physical deals\nDescriptive only; fold/call/raise comparisons exclude jam')
    fig.savefig(OUT/'frozen-root-precision-summary.png',dpi=150);plt.close(fig)
    table='\n'.join('| '+NAMES[i]+' | '+' | '.join(f'{v:.3f}' for v in b['rms_class_standard_error_on_covered_mass'])+f" | {100*b['half_maximizer_disagreement_entry_mass']:.1f}% |" for i,b in enumerate(analysis['banks']))
    archive_bytes=sum(j['compressed_bytes'] for j in result['jobs'])
    content=f'''# Frozen-continuation root precision

This exploratory diagnostic measures uncertainty in action values while continuation policies remain fixed. It does not establish more accurate preflop ranges or select a model for deployment. The earlier confirmatory study and its inconclusive intervals remain unchanged.

## Method

Reused all 65,536 already-inspected deals, in original order, for four frozen self-play policy pairs. BB's first action was forced to fold, call, raise or jam while every later policy row remained unchanged. Each original payoff was reproduced and recovered by mixing the four forced-action values. Both players' cashflows and rake were checked. No new cards, training, GPU inference or production modifications were involved.

Every class has {min(counts)}–{max(counts)} observations. Even and odd global deal indices define the halves. Standard errors describe fixed-policy sample precision, not simultaneous confidence bounds. Incoming hand-class masses weight the RMS summaries below. Preferred actions compare fold, call and raise only; a disagreement between halves is not a percentage of hands played incorrectly.

| Bank | Call - fold SE (bb) | Raise - fold SE (bb) | Raise - call SE (bb) | Half-sample disagreement mass |
| --- | ---: | ---: | ---: | ---: |
{table}

![Precision and split-sample stability](frozen-root-precision-summary.png)

## Evidence and limits

The separate scalar audit recomputed means, paired standard errors, class coverage, weighted aggregate errors and split-sample preferred actions. Maximum discrepancy: {audit['maximum_scalar_error']:.3g}. The parallel control also reproduced the qualified serial native outputs byte for byte. Full batch processing and first analysis took {result['seconds']/60:.1f} minutes, excluding storage admission and separate readbacks. Compressed batch evidence occupies {archive_bytes/1e6:.1f} MB.

[All class values](frozen-root-precision-class-values.csv) and [all six paired bank comparisons](frozen-root-precision-paired-bank-values.csv) are retained. The paired comparisons use common deals, but both players' continuations change between self-play banks; they are not unilateral gains or proof of treatment benefit. Action numbers in the class export are 0=fold, 1=call, 2=raise.

These forced values can enter branches with weak fallback continuation play. Their maximizing action is not a best response to a fully solved game. Jam is excluded from the precision summaries because this native per-deal estimator differs from the exact private-hand integration used for training jam targets. This spot remains BB versus BTN, 200bb, 2bb open, 0.5bb dead money, 5% rake capped at 2bb; it does not qualify other stacks or positions.

The result separates fixed-policy sampling variation from the moving-policy behavior already documented. It does not alone apportion the original training instability or justify extrapolating a required training budget. The next experiment should address whichever uncertainty remains visible here, alongside the existing evidence of sparse per-class coverage and policy movement.
'''
    with (OUT/'FROZEN-ROOT-PRECISION-FINDINGS.md').open('x',encoding='utf-8') as f:f.write(content)
    print(json.dumps(dict(published=True,banks=[{k:v for k,v in b.items() if k!='classes'} for b in analysis['banks']],counts=[min(counts),max(counts)],archive_bytes=archive_bytes)))


def wait_and_finish(pid):
    process=psutil.Process(pid)
    assert any('hu_frozen_root_precision_20260926.py' in x for x in process.cmdline())
    assert '--study' in process.cmdline()
    born=process.create_time(); started=time.monotonic()
    while process.is_running():
        assert process.create_time()==born and time.monotonic()-started<14400
        time.sleep(5)
    assert read(OUT/f'{PREFIX}-status.json')['state']=='complete'
    cp=subprocess.run([sys.executable,str(ROOT/'tools/research/frozen_root_precision_audit_20260926.py'),PREFIX],cwd=ROOT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW)
    assert cp.returncode==0
    publish()


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--wait':wait_and_finish(int(sys.argv[2]))
    else:
        assert sys.argv[1:]==['--publish']
        publish()
