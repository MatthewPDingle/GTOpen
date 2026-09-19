"""AA call/jam sensitivity with adapting all-in and postflop responses."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import copy
import hashlib
import json
import subprocess
import sys
import time
import numpy as np
import conditional_hu_audit as conditional
import wizard_continuation_study as s
import wizard_continuation_precision as precision

OUT=s.OUT.parent/'aa-joint-response-20260919'
FRACTIONS=[0.,1.,.5,.25,.75]


def prepare():
    assert not (OUT/'manifest.json').exists(),'Preserve registration'
    conditional.frozen()
    parent=s.read(s.OUT/'manifest.json');fixture=s.read(s.OUT/'fixtures.json')
    labels=[h['hand'] for h in fixture['cases'][0]['balanced']['hands'][0]]
    counts=np.array([6 if len(h)==2 else 4 if h.endswith('s') else 12 for h in labels])
    aa=labels.index('AA');assert aa==168
    data=s.read(conditional.OUT/'subtree.json');game=conditional.Game(data,True)
    result=s.read(conditional.OUT/'compatible_fresh.json')
    baseline={int(i):np.array(v) for i,v in result['records'][-1]['policy'].items()}
    assert result['records'][-1]['iteration']==50000
    initial=np.array(data['incoming_class_mass'])/counts[None,:]
    initial/=initial.max(1)[:,None]
    jobs=[];cases=[]
    for q in FRACTIONS:
        name=f'q{int(q*100):03d}';policy={i:v.copy() for i,v in baseline.items()}
        policy[0][:,aa]=[0.,q,0.,1-q]
        # At the final jam response there are two actions and no continuation
        # decisions. Values below include the compatible opponent reach mass;
        # the positive common normalizer cancels when choosing fold/call.
        opponent=policy[0][3]
        vals=np.array([game.values(policy,1,c,opponent) for c in game.nodes[9]['children']])
        choose=vals.argmax(0);reply=np.zeros_like(policy[9]);reply[choose,np.arange(169)]=1
        policy[9]=reply
        actions={};game.values(policy,0,actions=actions)
        jam_value=float(actions[0][3,aa]+6.)
        weights=initial.copy();weights[0]*=policy[0][1]
        weights/=weights.max(1)[:,None]
        original=weights.copy();before=weights@counts;removed=[];added=[]
        for p in [0,1]:
            trim=weights[p]<.005;removed.append(float(weights[p,trim]@counts[trim]/before[p]));weights[p,trim]=0
            extra=0.
            if p==0:
                for h,label in enumerate(labels):
                    if label in fixture['probes'] and weights[p,h]<.001:
                        extra+=(.001-weights[p,h])*counts[h];weights[p,h]=.001
            added.append(float(extra/before[p]))
        assert max(removed)<.005 and max(added)<.005,(removed,added)
        ranges=[','.join(f'{h}:{w:.9f}' for h,w in zip(labels,ww) if w>0) for ww in weights]
        cases.append(dict(id=name,q=q,jam_value_bb=jam_value,lj_jam_call=reply[1].tolist(),
            aa_call_combo_mass_fraction=float(weights[0,aa]*6/(weights[0]@counts)),
            removed_mass_fraction=removed,added_mass_fraction=added,weights=weights.tolist(),
            original_weights=original.tolist(),range_oop=ranges[0],range_ip=ranges[1]))
        for old in parent['jobs']:
            j=copy.deepcopy(old);j['id']=name+'-'+j['id'];j['case']=name
            j['config']['range_oop'],j['config']['range_ip']=ranges
            jobs.append(j)
        print(name,'AA jam value',jam_value,'AA call range share',cases[-1]['aa_call_combo_mass_fraction'])
    s.write(OUT/'fixtures.json',dict(cases=cases,labels=labels,probes=fixture['probes']))
    paths=[OUT/'PROTOCOL.md',OUT/'fixtures.json',precision.BINARY,
        s.ROOT/'crates/solver/examples/wizard_continuation_precision.rs',
        s.ROOT/'tools/research/aa_joint_response_study.py',
        s.ROOT/'tools/research/conditional_hu_audit.py',s.ROOT/'tools/research/wizard_continuation_study.py',
        conditional.OUT/'subtree.json',conditional.OUT/'compatible_fresh.json',
        s.OUT/'manifest.json',s.ROOT/'cache/preflop_eq169.bin',s.SAVE]
    m=dict(jobs=jobs,boards=parent['boards'],target_gap_pct=.05,max_iterations=5000,
        probe_br_gain_limit_bb=.05,inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in paths})
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
    m=checked();env=dict(os.environ)
    env['PATH']=str(s.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for i,j in enumerate(m['jobs']):
        dest=OUT/'jobs'/(j['id']+'.json')
        if dest.exists():validate(s.read(dest),j,m);continue
        while not s.idle()[0]:
            s.write(OUT/'status.json',dict(stage='waiting_for_live_app',completed=i,total=len(m['jobs'])))
            time.sleep(30)
        s.write(OUT/'status.json',dict(stage='solving',job=j['id'],completed=i,total=len(m['jobs'])))
        with (OUT/(j['id']+'.log')).open('w') as log:
            subprocess.run([str(precision.BINARY),'run',str(OUT/'manifest.json'),'1'],cwd=s.ROOT,
                env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        validate(s.read(dest),j,m)
        print('Completed',i+1,'/',len(m['jobs']),j['id'],flush=True)
        if (i+1)%80==0:summarize()
    summarize();s.write(OUT/'status.json',dict(stage='ready_for_review',completed=len(m['jobs'])))


def summarize():
    m=checked();fixtures=s.read(OUT/'fixtures.json');boards=m['boards'];index={b['board']:i for i,b in enumerate(boards)}
    rng=np.random.default_rng(19092026);draws=np.zeros((5000,len(boards)))
    for group in sorted({b['stratum'] for b in boards}):
        indices=[i for i,b in enumerate(boards) if b['stratum']==group]
        for row in draws:np.add.at(row,rng.choice(indices,len(indices)),1)
    results=[]
    for case in fixtures['cases']:
        jobs=[j for j in m['jobs'] if j['case']==case['id']]
        if not all((OUT/'jobs'/(j['id']+'.json')).exists() for j in jobs):continue
        for menu in ['half','large']:
            mass=np.zeros(len(boards));total=mass.copy();gains=[]
            for j in jobs:
                if j['menu']!=menu:continue
                r=s.read(OUT/'jobs'/(j['id']+'.json'));validate(r,j,m)
                h=next(h for h in r['hands'][0] if h['hand']=='AA')
                i=index[j['board']];mass[i]=j['iso_weight']/j['inclusion_probability']*h['pair_mass']
                total[i]=mass[i]*h['ev_bb'];gains.append(h['br_ev_bb']-h['ev_bb'])
            gross=float(total.sum()/mass.sum());sample=draws@total/(draws@mass)-12.
            call=gross-12.;difference=call-case['jam_value_bb']
            results.append(dict(q=case['q'],menu=menu,call_value_bb=call,jam_value_bb=case['jam_value_bb'],
                call_minus_jam_bb=difference,call_ci95_bb=np.quantile(sample,[.025,.975]).tolist(),
                difference_ci95_bb=np.quantile(sample-case['jam_value_bb'],[.025,.975]).tolist(),
                max_aa_br_gain_bb=max(gains),aa_call_range_mass=case['aa_call_combo_mass_fraction']))
    s.write(OUT/'summary.json',dict(completed_cases=len(results)//2,results=results,
        note='Restricted AA call/jam feedback with adapting LJ jam response and both postflop policies. Board-sampling intervals only; not a full-game equilibrium.'))


if __name__=='__main__':
    try:{'prepare':prepare,'run':run,'summarize':summarize}[sys.argv[1]]()
    except Exception as error:
        if sys.argv[1]=='run':s.write(OUT/'status.json',dict(stage='failed',error=str(error)))
        raise
