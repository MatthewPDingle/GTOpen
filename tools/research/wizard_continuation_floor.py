"""Paired range-floor sensitivity; waits for the convergence refinement."""
import copy
import hashlib
import json
import os
import subprocess
import sys
import time
import numpy as np
import wizard_continuation_study as s
import wizard_continuation_precision as precision

OUT=s.OUT/'floor-sensitivity'


def prepare():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'manifest.json').exists(), 'Preserve frozen sensitivity manifest'
    parent=s.checked(); fixtures=s.read(s.OUT/'fixtures.json'); case,=fixtures['cases']
    weights=list(case['weights'][0]); labels=[h['hand'] for h in case['balanced']['hands'][0]]
    counts=np.array([6 if len(h)==2 else 4 if h.endswith('s') else 12 for h in labels])
    before=np.array(weights)
    for i,h in enumerate(labels):
        if h in fixtures['probes']:weights[i]=max(weights[i],.01)
    fraction=float(np.sum((np.array(weights)-before)*counts)/np.sum(before*counts))
    assert fraction<.005
    range_oop=','.join(f'{h}:{w:.9f}' for h,w in zip(labels,weights) if w>0)
    jobs=copy.deepcopy(parent['jobs'])
    for j in jobs:j['config']['range_oop']=range_oop
    inputs=[precision.BINARY,s.OUT/'manifest.json',s.OUT/'fixtures.json',OUT/'PROTOCOL.md',
            s.ROOT/'tools/research/wizard_continuation_floor.py']
    m=dict(parent_manifest_id=parent['id'],jobs=jobs,target_gap_pct=.05,max_iterations=5000,
        probe_br_gain_limit_bb=.05,probe_floor=.01,added_mass_fraction=fraction,
        inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in inputs})
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    s.write(OUT/'manifest.json',m)


def checked():
    m=s.read(OUT/'manifest.json')
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k!='id'},sort_keys=True).encode()).hexdigest()==m['id']
    for path,digest in m['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    return m


def validate(r,j,m):
    s.validate(r,j,m)
    assert r['max_probe_br_gain_bb']<=m['probe_br_gain_limit_bb']


def run():
    import msvcrt
    lock=(OUT/'run.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    m=checked()
    assert s.read(precision.OUT/'status.json')['stage']=='ready_for_review'
    env=dict(os.environ);env['PATH']=str(s.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for i,j in enumerate(m['jobs']):
        dest=OUT/'jobs'/(j['id']+'.json')
        if dest.exists():validate(s.read(dest),j,m);continue
        while not s.idle()[0]:
            s.write(OUT/'status.json',dict(stage='waiting_for_live_app',job=j['id']));time.sleep(30)
        s.write(OUT/'status.json',dict(stage='solving',job=j['id'],completed=i,total=len(m['jobs'])))
        with (OUT/(j['id']+'.log')).open('w') as log:
            subprocess.run([str(precision.BINARY),'run',str(OUT/'manifest.json'),'1'],cwd=s.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        validate(s.read(dest),j,m)
        print('Floor sensitivity',i+1,'/',len(m['jobs']),j['id'],flush=True)
    summarize()
    s.write(OUT/'status.json',dict(stage='ready_for_review',completed=len(m['jobs'])))


def summarize():
    m=checked(); parent=s.read(s.OUT/'manifest.json'); pm=s.read(precision.OUT/'manifest.json')
    refined={j['id'] for j in pm['jobs']}; probes=s.read(s.OUT/'fixtures.json')['probes']
    pairs=[]
    for j in m['jobs']:
        new=s.read(OUT/'jobs'/(j['id']+'.json'));validate(new,j,m)
        original_job=next(p for p in parent['jobs'] if p['id']==j['id'])
        old=s.read(s.OUT/('precision/jobs' if j['id'] in refined else 'jobs')/(j['id']+'.json'))
        s.validate(old,original_job,pm if j['id'] in refined else parent)
        pairs.append((old,new))
    boards=parent['boards'];index={b['board']:i for i,b in enumerate(boards)}
    rng=np.random.default_rng(19092026); draws=np.zeros((5000,len(boards)))
    for group in sorted({b['stratum'] for b in boards}):
        indices=[i for i,b in enumerate(boards) if b['stratum']==group]
        for row in draws:np.add.at(row,rng.choice(indices,len(indices)),1)
    results=[]
    for menu in ('half','large'):
        for hand in probes:
            mass=np.zeros((2,len(boards)));total=mass.copy();gains=[]
            for pair in pairs:
                if pair[0]['job']['menu']!=menu:continue
                for k,r in enumerate(pair):
                    h=next((h for h in r['hands'][0] if h['hand']==hand),None)
                    if h is None:continue
                    i=index[r['job']['board']]
                    mass[k,i]=r['job']['iso_weight']/r['job']['inclusion_probability']*h['pair_mass']
                    total[k,i]=mass[k,i]*h['ev_bb']
                    if k:gains.append(h['br_ev_bb']-h['ev_bb'])
            values=total.sum(axis=1)/mass.sum(axis=1)
            sampled=[draws@total[k]/(draws@mass[k]) for k in range(2)]
            delta=sampled[1]-sampled[0]
            results.append(dict(menu=menu,hand=hand,original_bb=float(values[0]),higher_floor_bb=float(values[1]),
                change_bb=float(values[1]-values[0]),paired_change_ci95_bb=np.quantile(delta,[.025,.975]).tolist(),
                max_probe_gain_bb=max(gains)))
    s.write(OUT/'summary.json',dict(results=results,added_mass_fraction=m['added_mass_fraction'],
        note='Paired direct estimates under 0.001 versus 0.01 OOP probe floors. No new fast-model prices were calculated.'))


def pipeline():
    while True:
        status=precision.OUT/'status.json'
        stage=s.read(status)['stage'] if status.exists() else 'waiting'
        if stage=='ready_for_review':break
        if stage=='failed':raise RuntimeError('Precision study failed; review before continuing')
        time.sleep(15)
    run()


if __name__=='__main__':
    try:{'prepare':prepare,'run':run,'summarize':summarize,'pipeline':pipeline}[sys.argv[1]]()
    except Exception as error:
        if sys.argv[1] in ('run','pipeline'):s.write(OUT/'status.json',dict(stage='failed',error=str(error)))
        raise
