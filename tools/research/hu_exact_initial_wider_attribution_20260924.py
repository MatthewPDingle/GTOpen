"""Exploratory attribution of a completed holdout; no fitting or new deals."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from reboot_research_idle_v1 import idle

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
SOURCE=Path('T:/GTOpen-research/exact-initial-wider-study-v1/evaluation')
PREFIX='exact-initial-wider-attribution-v1'
ACTION=['fold','call','raise','jam']


def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
    with p.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(d,f,separators=(',',':'),allow_nan=False);f.write('\n')


def label(c):
    a,b=divmod(c,13);lo,hi=sorted((a,b));r='23456789TJQKA'
    return r[hi]+r[lo]+('' if a==b else 's' if a>b else 'o')


def family(c):
    a,b=divmod(c,13);lo,hi=sorted((a,b))
    if a==b:return 'Pocket pairs'
    if a>b:
        if lo>=8:return 'Suited broadways'
        if hi==12:return 'Other suited aces'
        if hi-lo==1:return 'Other suited connectors'
        return 'Other suited hands'
    return 'Offsuit broadways' if lo>=8 else 'Other offsuit hands'


def main():
    start=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    def guard():
        assert time.monotonic()-start<600 and idle()
        assert psutil.virtual_memory().available>20_000_000_000
    guard()
    paths={s:OUT/f'exact-initial-wider-study-v1-{s}.json' for s in
           ('registration','result','evaluation','independent-review')}
    reg,finished,evaluation,audit=[read(paths[s]) for s in
           ('registration','result','evaluation','independent-review')]
    assert finished['passed'] and audit['passed'] and evaluation['complete']
    assert finished['registration_sha256']==audit['registration_sha256']==evaluation['registration_sha256']==sha(paths['registration'])
    assert audit['evaluation_sha256']==sha(paths['evaluation'])
    detail=read(SOURCE/'result.json')
    assert sha(SOURCE/'result.json')==evaluation['result_sha256']==audit['result_sha256']
    response=read(SOURCE/'response.json');preparation=read(SOURCE/'residual-preparation.json')
    assert sha(SOURCE/'response.json')==detail['response_sha256']
    assert sha(SOURCE/'residual-preparation.json')==detail['preparation_sha256']
    inputs={str(p):sha(p) for p in [*paths.values(),SOURCE/'result.json',SOURCE/'response.json',
        SOURCE/'prior-response.json',SOURCE/'residual-preparation.json',Path(__file__)]}
    rp=OUT/(PREFIX+'-registration.json')
    save(rp,dict(inputs=inputs,source=str(SOURCE),test_deals=detail['test_deals'],
        groups='Exhaustive rank families and frozen responder action; report every group and all 169 classes.',
        scope='Post-hoc decomposition of an already reported holdout, not new independent evidence or a policy.',
        gpu_used=False,production_modified=False))
    exact=reg['exact'];mass=np.asarray(exact['masses']);base=np.asarray(exact['baseline'])
    fold=np.asarray(exact['fold_entries']);jam=np.asarray(exact['jam_entries'])
    assert np.max(abs(base-np.asarray(response['baseline'])))<1e-12
    assert np.max(abs(mass-np.asarray(response['class_population_masses'])))<1e-12
    selected=np.asarray(response['selected_actions'])
    assert np.array_equal(selected,np.argmax(response['class_action_means'],axis=1))
    series=['trained-response','previous-response']
    counts=np.zeros(169,dtype=np.int64)
    sums={s:np.zeros(169) for s in series};qsum=np.zeros((169,4))
    maximum_residual_error=0.;number=0
    for name,h in sorted(detail['batch_summary_hashes'].items()):
        if not name.startswith('test-'):continue
        guard();p=SOURCE/name/'summary.json';assert sha(p)==h
        d=read(p);cs=np.asarray(d['classes']);q=np.asarray(d['action_values'])
        assert q.shape==(len(cs),4) and np.min(cs)>=0 and np.max(cs)<169
        assert np.max(abs(np.asarray(d['root_probabilities'])-base[cs]))<1e-10
        stored=read(SOURCE/name/'residuals.json')
        assert stored['response_sha256']==detail['response_sha256'] and stored['preparation_sha256']==detail['preparation_sha256']
        for s in series:
            p=preparation[s];delta=np.asarray(p['delta']);centre=np.asarray(p['centre'])
            # Independently reconstruct the two sampled action contributions.
            values=np.array([delta[c,1]*x[1]+delta[c,2]*x[2]-centre[c]
                             for c,x in zip(cs,q)])
            error=float(np.max(abs(values-np.asarray(stored['values'][s]))))
            assert error<1e-10;maximum_residual_error=max(maximum_residual_error,error)
            np.add.at(sums[s],cs,values)
        np.add.at(qsum,cs,q);counts+=np.bincount(cs,minlength=169);number+=1
    n=int(counts.sum());assert n==131072==detail['test_deals']
    assert counts.tolist()==detail['test_counts'] and number==2048 and min(counts)>0
    contributions={};offsets={}
    for s in series:
        p=preparation[s];delta=np.asarray(p['delta'])
        offsets[s]=delta[:,0]*fold+delta[:,3]*jam+mass*np.asarray(p['centre'])
        assert abs(math.fsum(offsets[s])-p['total_offset'])<1e-12
        contributions[s]=offsets[s]+sums[s]/n
        assert abs(math.fsum(contributions[s])-detail['intervals'][s]['mean'])<1e-12
    prior=read(SOURCE/'prior-response.json');assert sha(SOURCE/'prior-response.json')==detail['prior_response_sha256']
    prior_rho=np.asarray(prior['probabilities']);rho=np.asarray(response['probabilities'])
    assert np.max(abs((rho-base)-np.asarray(preparation['trained-response']['delta'])))<1e-12
    assert np.max(abs((prior_rho-base)-np.asarray(preparation['previous-response']['delta'])))<1e-12
    rows=[]
    for c in range(169):
        rows.append(dict(hand=label(c),hand_class=c,family=family(c),mass=float(mass[c]),test_count=int(counts[c]),
            baseline=base[c].tolist(),trained_action=ACTION[selected[c]],prior_action=ACTION[prior['selected_actions'][c]],
            train_action_values=response['class_action_means'][c],sample_test_action_values=(qsum[c]/counts[c]).tolist(),
            contribution_bb_per_entry={s:float(contributions[s][c]) for s in series}))
    groups={}
    for grouping in ['family','trained_action']:
        grouped=[]
        for value in sorted({r[grouping] for r in rows}):
            ids=[r['hand_class'] for r in rows if r[grouping]==value];m=float(mass[ids].sum())
            grouped.append(dict(group=value,classes=len(ids),mass=m,test_count=int(counts[ids].sum()),
                baseline_mix=(np.sum(base[ids]*mass[ids,None],axis=0)/m).tolist(),
                response_mix=(np.sum(rho[ids]*mass[ids,None],axis=0)/m).tolist(),
                contribution_bb_per_entry={s:math.fsum(contributions[s][ids]) for s in series}))
        for s in series:assert abs(math.fsum(r['contribution_bb_per_entry'][s] for r in grouped)-detail['intervals'][s]['mean'])<1e-12
        groups[grouping]=grouped
    for p,h in inputs.items():assert sha(Path(p))==h
    result=dict(passed=True,registration_sha256=sha(rp),test_deals=n,batches=number,rows=rows,groups=groups,
        totals={s:math.fsum(contributions[s]) for s in series},maximum_residual_error_bb=maximum_residual_error,
        seconds=time.monotonic()-start,exploratory_only=True,gpu_used=False,production_modified=False,
        caveat='Groups and class rankings are descriptive post-hoc estimates; no new per-group confidence claim. Contributions sum to the original estimator. Sampled per-class action values include runout noise; exact fold/jam offsets remain authoritative.')
    save(OUT/(PREFIX+'-result.json'),result)
    print(json.dumps({k:result[k] for k in ['passed','test_deals','totals','groups','seconds']}),flush=True)


if __name__=='__main__':main()
