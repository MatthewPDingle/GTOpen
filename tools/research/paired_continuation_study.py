"""Offline paired-context pilot; frozen training then prospective new-range labels."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import numpy as np
import paired_continuation_model as model

prior=model.prior; native=model.native; pilot=model.pilot
ROOT=prior.ROOT; OUT=native.previous.prior.BASE/'paired-continuation-20260917'
read,write,now=prior.read,prior.write,prior.now


def training():
    """Two completed audits become development data, never the new test set."""
    families=[]; inputs={}
    for name,folder in [('original',native.previous.old.OUT),('shallow',prior.OUT)]:
        m=read(folder/'manifest.json'); cases=m['cases']; rows={}; tree_path=folder/'tree.json' if name=='original' else folder/'shallow/tree.json'
        for case in cases:
            source=folder; manifest=m
            if name=='original' and case['id']=='call':
                source=native.previous.prior.OUT; manifest=read(source/'manifest.json')
            jobs=[j for j in manifest['jobs'] if name=='original' and case['id']=='call' or j['case']==case['id']]
            rr=[]
            for j in jobs:
                path=source/'jobs'/(j['id']+'.json'); row=read(path)
                native.previous.old.validate(row,j,manifest); rr.append(row)
                inputs[path.relative_to(ROOT).as_posix()]=pilot.sha(path)
            rows[case['id']]=rr
            inputs[(source/'manifest.json').relative_to(ROOT).as_posix()]=pilot.sha(source/'manifest.json')
        inputs[tree_path.relative_to(ROOT).as_posix()]=pilot.sha(tree_path)
        families.append((name,model.pack(read(tree_path),cases,rows)))
    return families,inputs


def train():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'candidate.json').exists(),'Preserve frozen candidate'
    prior.checked(); families,inputs=training(); scores=[]
    for penalty in [.0001,.001,.01,.1]:
        for weight in [0.,1.,4.]:
            folds=[]
            for held,p in families:
                fit=model.fit([q for name,q in families if name!=held],penalty,weight)
                folds.append(dict(family=held,**model.score(p,fit)))
            # Validation is on the other entire range family, not randomly split hands.
            action=float(np.mean([r['action_mae_bb']['corrected'] for r in folds]))
            leaf_ok=all(np.mean([c['candidate'][key] for c in r['leaves']]) <= 1.05*np.mean([c['baseline'][key] for c in r['leaves']]) for r in folds for key in ['direct','corrected'])
            scores.append(dict(penalty=penalty,action_weight=weight,folds=folds,mean_action_mae_bb=action,leaf_guard_passed=bool(leaf_ok)))
    eligible=[r for r in scores if r['leaf_guard_passed']]
    write(OUT/'training-screen.json',dict(scores=scores,eligible=len(eligible)))
    assert eligible,'No candidate passed development leaf guards'
    best=min(eligible,key=lambda r:(r['mean_action_mae_bb'],-r['penalty'],r['action_weight']))
    result=model.fit([p for _,p in families],best['penalty'],best['action_weight'])
    result.update(frozen_at=now(),selection='leave one completed policy family out; minimize adjusted action MAE subject to <=5% mean leaf regression per family and estimator',
                  development_families=[name for name,_ in families],development_inputs=inputs,
                  scope='40bb HU paired-context pilot only; no production or arbitrary-stack claim')
    write(OUT/'candidate.json',result)
    write(OUT/'candidate-freeze.json',dict(sha256=pilot.sha(OUT/'candidate.json'),frozen_at=now()))
    print('Frozen',best['penalty'],best['action_weight'],'CV action MAE',best['mean_action_mae_bb'],flush=True)


def perturb(tree, family):
    t=copy.deepcopy(tree)
    strength=np.array([((hi+lo)/24 + float(hi==lo)*.35 + float(suited)*.08) for hi,lo,suited in pilot.PARTS])
    strength-=strength.mean()
    for node in t['nodes']:
        if node['kind']!=0:continue
        s=np.array(node['sigma']).reshape(-1,169)
        # No action added or removed. Temper support and tilt ordinary calls/raises.
        s=np.maximum(s,1e-7)**(.8 if family=='tempered' else .9)
        if family=='tilted':
            for a,action in enumerate(node['actions']):
                label=action['label'].lower()
                tilt=.3 if 'call' in label or 'limp' in label else -.25 if 'raise' in label or 'bet' in label else 0.
                s[a]*=np.exp(tilt*strength)
        s/=s.sum(axis=0)
        node['sigma']=s.ravel().tolist()
    _,_,reaches=native.tree_values(t)
    for n in t['nodes']:n['reaches']=reaches[n['id']].tolist()
    t['research_perturbation']=family
    t['read_only']=True
    return t


def prepare():
    assert not (OUT/'manifest.json').exists(),'Preserve registered study'
    assert pilot.sha(OUT/'candidate.json')==read(OUT/'candidate-freeze.json')['sha256']
    old=prior.checked(); cases=[]; jobs=[]; trees={}
    # New board panel across the full canonical population; incidental old overlap allowed.
    boards=native.previous.panel('paired-continuation-test-v1',4)
    template=old['jobs'][0]['config']['tree']
    for family,path in [('tempered',native.previous.old.OUT/'tree.json'),('tilted',prior.OUT/'shallow/tree.json')]:
        tree=perturb(read(path),family); tree_path=OUT/(family+'-tree.json'); write(tree_path,tree); trees[family]=tree_path.relative_to(ROOT).as_posix()
        for branch,ident in zip(native.previous.old.PATHS,native.previous.old.CASE_IDS):
            node=next(n for n in tree['nodes'] if n['path']==branch)
            w=np.array(node['reaches'])[[1,0]]/(pilot.COMBOS/1326)
            texts=[','.join(f'{pilot.LABELS[k]}:{v:.17g}' for k,v in enumerate(row)) for row in w]
            case=dict(id=family+'-'+ident,family=family,branch=ident,node=node['id'],path=branch,
                      pot=node['pot'],stack=min(tree['config']['stack']-v for v in node['invested']),
                      weights=w.tolist(),range_oop=texts[0],range_ip=texts[1])
            cases.append(case); config=dict(template,starting_pot=case['pot'],effective_stack=case['stack'])
            for b in boards:
                jobs.append(dict(**b,id=case['id']+'-'+b['board'],case=case['id'],config=dict(board=b['board'],range_oop=texts[0],range_ip=texts[1],tree=config)))
    paths=[Path(__file__),ROOT/'tools/research/paired_continuation_model.py',ROOT/'tools/research/evaluate_paired_continuation.py',OUT/'PROTOCOL.md',OUT/'candidate.json',OUT/'candidate-freeze.json',native.previous.prior.REFERENCE]
    paths += [ROOT/p for p in trees.values()]
    # Capture all imported research helpers so changes cannot silently alter the test.
    import sys
    paths += [Path(mod.__file__) for mod in list(sys.modules.values()) if getattr(mod,'__file__',None) and Path(mod.__file__).parent==ROOT/'tools/research']
    m=dict(registered_at=now(),cases=cases,jobs=jobs,boards=boards,trees=trees,target_gap_pct=.1,max_iterations=2000,
           inputs={p.relative_to(ROOT).as_posix():pilot.sha(p) for p in paths},bootstrap_seed=2026091705,bootstrap_replicates=5000,production_enabled=False)
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    write(OUT/'preflight.json',dict(live=native.previous.prior.idle(),references=len(jobs),checked_at=now()))
    write(OUT/'manifest.json',m);print('Registered',len(jobs),'new references',flush=True)


def checked():
    m=read(OUT/'manifest.json')
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k!='id'},sort_keys=True).encode()).hexdigest()==m['id']
    for p,h in m['inputs'].items():assert pilot.sha(ROOT/p)==h,p
    for p,h in read(OUT/'candidate.json')['development_inputs'].items():assert pilot.sha(ROOT/p)==h,p
    return m


def run():
    m=checked();start=time.perf_counter();env=dict(os.environ)
    env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for i,j in enumerate(m['jobs']):
        path=OUT/'jobs'/(j['id']+'.json')
        if not path.exists():
            native.previous.prior.idle()
            write(OUT/'status.json',dict(stage='references',completed=i,total=len(m['jobs']),active=j['id'],updated=now()))
            with (OUT/(j['id']+'.log')).open('w',encoding='utf-8',newline='\n') as log:
                subprocess.run([str(native.previous.prior.REFERENCE),str(OUT/'manifest.json'),'1'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        native.previous.old.validate(read(path),j,m)
        print(i+1,'/',len(m['jobs']),j['id'],'seconds',round(time.perf_counter()-start),flush=True)
    checked();write(OUT/'status.json',dict(stage='references_complete',completed=len(m['jobs']),total=len(m['jobs']),updated=now()))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['train','prepare','run'])
    {'train':train,'prepare':prepare,'run':run}[parser.parse_args().command]()
