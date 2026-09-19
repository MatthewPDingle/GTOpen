"""Controlled 4-bet-call continuation follow-up; offline and serial."""
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

PARENT=s.OUT
OUT=PARENT/'fourbet-call'


def prices(weights,pot,stack,labels):
    counts=np.array([6 if len(h)==2 else 4 if h.endswith('s') else 12 for h in labels],dtype=float)
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    base=np.array(s.read(s.ROOT/'cache/realization_fit.json')['class_base'])
    a=eq*base[:,None]*.92;b=(1-eq)*base[None,:]*1.08
    shares=a/np.maximum(a+b,1e-12);blend=min(stack/pot/8,1)
    values=eq+blend*(shares-eq);net=pot-min(.04*pot,6)
    d=np.array(weights)*counts[None,:];d/=d.sum(axis=1)[:,None]
    oop=net*(values@d[1]);ip=net*((1-values.T)@d[0])
    means=[float(d[0]@oop),float(d[1]@ip)]
    assert abs(sum(means)-net)<1e-8
    return dict(mean_bb=means,hands=[[dict(hand=h,value_bb=float(v)) for h,v in zip(labels,vv)] for vv in (oop,ip)])


def prepare():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'manifest.json').exists(),'Preserve frozen four-bet study'
    parent=s.checked();original=s.read(PARENT/'fixtures.json');baseline,=original['cases']
    labels=[h['hand'] for h in baseline['balanced']['hands'][0]]
    # Validate independent double-precision implementation against the frozen Rust prices.
    check=prices(baseline['weights'],baseline['pot'],baseline['stack'],labels)
    error=max(abs(a['value_bb']-b['value_bb']) for aa,bb in zip(check['hands'],baseline['balanced']['hands']) for a,b in zip(aa,bb))
    assert error<.0001
    audit=s.read(PARENT/'premium-branches.json');path=[1,2,0,0,0,0,0,0,2,1]
    node=next(n for n in audit['nodes'] if n['path']==path);ex=node['export'];assert (ex['pot_bb'],ex['eff_stack_bb'])==(93.5,155)
    original_weights=[node['view']['reaches_all'][p] for p in (1,2)]
    counts=np.array([6 if len(h)==2 else 4 if h.endswith('s') else 12 for h in labels],dtype=float)
    weights=np.array(original_weights);weights/=weights.max(axis=1)[:,None]
    before=weights@counts;removed=[];added=[]
    for p in (0,1):
        drop=weights[p]<.005;removed.append(float(weights[p,drop]@counts[drop]/before[p]));weights[p,drop]=0
        extra=0.
        if p==0:
            for i,h in enumerate(labels):
                if h in original['probes'] and weights[p,i]<.001:
                    extra+=(.001-weights[p,i])*counts[i];weights[p,i]=.001
        added.append(float(extra/before[p]))
    assert max(removed)<.005 and max(added)<.005
    ranges=[','.join(f'{h}:{w:.9f}' for h,w in zip(labels,ww) if w>0) for ww in weights]
    case=dict(id='fourbet-call',path=path,pot=93.5,stack=155,weights=weights.tolist(),original_weights=original_weights,
        range_oop=ranges[0],range_ip=ranges[1],removed_mass_fraction=removed,probe_added_mass_fraction=added,
        original_balanced=prices(original_weights,93.5,155,labels),balanced=prices(weights,93.5,155,labels))
    fixtures=dict(cases=[case],probes=original['probes'],config=original['config'],iteration=1000,
        save=original['save'],canonical_flops=original['canonical_flops'],price_implementation_max_difference_bb=error)
    s.write(OUT/'fixtures.json',fixtures)
    jobs=copy.deepcopy(parent['jobs'])
    for j in jobs:
        j['case']='fourbet-call';j['config']['range_oop'],j['config']['range_ip']=ranges
        j['config']['tree']['starting_pot']=93.5;j['config']['tree']['effective_stack']=155
    inputs=[precision.BINARY,PARENT/'manifest.json',PARENT/'premium-branches.json',OUT/'fixtures.json',OUT/'PROTOCOL.md',
        s.ROOT/'tools/research/wizard_fourbet_continuation.py',s.ROOT/'cache/preflop_eq169.bin',s.ROOT/'cache/realization_fit.json']
    m=dict(parent_manifest_id=parent['id'],boards=parent['boards'],jobs=jobs,target_gap_pct=.05,max_iterations=5000,
        probe_br_gain_limit_bb=.05,inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in inputs})
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest();s.write(OUT/'manifest.json',m)


def run():
    import msvcrt
    lock=(OUT/'run.lock').open('a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    s.OUT=OUT;m=s.checked()
    assert s.read(PARENT/'floor-sensitivity/status.json')['stage']=='ready_for_review'
    env=dict(os.environ);env['PATH']=str(s.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for i,j in enumerate(m['jobs']):
        dest=OUT/'jobs'/(j['id']+'.json')
        if not dest.exists():
            while not s.idle()[0]:
                s.write(OUT/'status.json',dict(stage='waiting_for_live_app',job=j['id']));time.sleep(30)
            s.write(OUT/'status.json',dict(stage='solving',job=j['id'],completed=i,total=len(m['jobs'])))
            with (OUT/(j['id']+'.log')).open('w') as log:
                subprocess.run([str(precision.BINARY),'run',str(OUT/'manifest.json'),'1'],cwd=s.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        r=s.read(dest);s.validate(r,j,m);assert r['max_probe_br_gain_bb']<=m['probe_br_gain_limit_bb']
        print('Four-bet continuation',i+1,'/',len(m['jobs']),j['id'],flush=True)
    s.summarize();s.write(OUT/'status.json',dict(stage='ready_for_review',completed=len(m['jobs'])))


def pipeline():
    while True:
        status=PARENT/'floor-sensitivity/status.json'
        stage=s.read(status)['stage'] if status.exists() else 'waiting'
        if stage=='ready_for_review':break
        if stage=='failed':raise RuntimeError('Floor sensitivity failed; review before continuing')
        time.sleep(15)
    run()


if __name__=='__main__':
    try:{'prepare':prepare,'run':run,'pipeline':pipeline}[sys.argv[1]]()
    except Exception as error:
        if sys.argv[1] in ('run','pipeline'):s.write(OUT/'status.json',dict(stage='failed',error=str(error)))
        raise
