"""Additional paired development labels; distinct from the reserved test protocol."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import numpy as np
import paired_continuation_study as pilot

ROOT=pilot.ROOT; OUT=pilot.OUT/'development-expansion'
read,write,now=pilot.read,pilot.write,pilot.now


def policy_tree(family):
    t=copy.deepcopy(read(pilot.prior.OUT/'shallow/tree.json'))
    counts,eq=pilot.pilot.matrices()
    # Rank against a uniform compatible opponent; this orders a synthetic policy,
    # and is not treated as a solved strategy or the reference value target.
    strength=(counts*eq).sum(axis=1)/counts.sum(axis=1)
    for n in t['nodes']:
        if n['kind']!=0:continue
        weights=[]
        for action in n['actions']:
            label=action['label'].lower()
            facing=len(n['path'])>1
            strong=1/(1+np.exp(-18*(strength-(.55 if not facing else .61))))
            if 'fold' in label:w=1-strong
            elif 'all-in' in label:w=.015+.12*strong**5
            elif 'raise' in label or 'bet' in label:
                if family=='linear':w=.04+1.4*strong**2
                else:w=.03+1.2*strong**3+.18*np.exp(-((strength-.42)/.06)**2)
            else:
                w=(.08+.75*strong*(1-.65*strong)) if family=='linear' else (.06+.95*strong*(1-.8*strong))
            weights.append(w)
        s=np.array(weights);s/=s.sum(axis=0)
        n['sigma']=s.ravel().tolist()
    _,_,reaches=pilot.native.tree_values(t)
    for n in t['nodes']:n['reaches']=reaches[n['id']].tolist()
    t.update(research_perturbation='synthetic-'+family,read_only=True)
    return t


def prepare():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'manifest.json').exists()
    boards=pilot.native.previous.panel('paired-development-expansion-v1',2)
    template=read(pilot.prior.OUT/'manifest.json')['jobs'][0]['config']['tree']
    cases=[];jobs=[];trees={}
    for family in ['linear','polar']:
        t=policy_tree(family);path=OUT/(family+'-tree.json');write(path,t);trees[family]=path.relative_to(ROOT).as_posix()
        for branch,ident in zip(pilot.native.previous.old.PATHS,pilot.native.previous.old.CASE_IDS):
            node=next(n for n in t['nodes'] if n['path']==branch)
            w=np.array(node['reaches'])[[1,0]]/(pilot.pilot.COMBOS/1326)
            texts=[','.join(f'{pilot.pilot.LABELS[k]}:{v:.17g}' for k,v in enumerate(row)) for row in w]
            c=dict(id=family+'-'+ident,family=family,branch=ident,node=node['id'],path=branch,pot=node['pot'],
                   stack=min(t['config']['stack']-v for v in node['invested']),weights=w.tolist(),range_oop=texts[0],range_ip=texts[1])
            cases.append(c);config=dict(template,starting_pot=c['pot'],effective_stack=c['stack'])
            for b in boards:jobs.append(dict(**b,id=c['id']+'-'+b['board'],case=c['id'],config=dict(board=b['board'],range_oop=texts[0],range_ip=texts[1],tree=config)))
    import sys
    paths=[Path(__file__),OUT/'PROTOCOL.md',pilot.native.previous.prior.REFERENCE]+[ROOT/p for p in trees.values()]
    paths += [Path(mod.__file__) for mod in list(sys.modules.values()) if getattr(mod,'__file__',None) and Path(mod.__file__).parent==ROOT/'tools/research']
    m=dict(registered_at=now(),cases=cases,jobs=jobs,boards=boards,trees=trees,partition='development',target_gap_pct=.1,
           max_iterations=2000,inputs={p.relative_to(ROOT).as_posix():pilot.pilot.sha(p) for p in paths},production_enabled=False)
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    write(OUT/'preflight.json',dict(live=pilot.native.previous.prior.idle(),references=len(jobs),checked_at=now()))
    write(OUT/'manifest.json',m);print('Registered development references:',len(jobs),flush=True)


def checked():
    m=read(OUT/'manifest.json')
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k!='id'},sort_keys=True).encode()).hexdigest()==m['id']
    for p,h in m['inputs'].items():assert pilot.pilot.sha(ROOT/p)==h,p
    return m


def run():
    m=checked();start=time.perf_counter();env=dict(os.environ)
    env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for i,j in enumerate(m['jobs']):
        path=OUT/'jobs'/(j['id']+'.json')
        if not path.exists():
            pilot.native.previous.prior.idle()
            write(OUT/'status.json',dict(stage='references',completed=i,total=len(m['jobs']),active=j['id'],updated=now()))
            with (OUT/(j['id']+'.log')).open('w',encoding='utf-8',newline='\n') as log:
                subprocess.run([str(pilot.native.previous.prior.REFERENCE),str(OUT/'manifest.json'),'1'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        pilot.native.previous.old.validate(read(path),j,m)
        print(i+1,'/',len(m['jobs']),j['id'],'seconds',round(time.perf_counter()-start),flush=True)
    checked();write(OUT/'status.json',dict(stage='references_complete',completed=len(m['jobs']),total=len(m['jobs']),updated=now()))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','run'])
    {'prepare':prepare,'run':run}[p.parse_args().command]()
