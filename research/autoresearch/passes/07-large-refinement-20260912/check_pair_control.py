"""Recompute pair-control numerical and learning gates without running a solver."""
import struct
from check_joint import *


def near(a,b,tolerance=1e-9):
    require(math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tolerance*max(1,abs(a),abs(b)),
            f'Mismatch: {a} != {b}')


def verify():
    numerical=read('pair-control-variance-v1.json')
    fixtures=numerical['fixtures']
    require([(v['players'],v['family']) for v in fixtures]==[(n,f) for n in (3,4,6,8) for f in range(3)],
            'Incomplete numerical coverage')
    pooled=[0.,0.]
    for v in fixtures:
        require(v['samples']==64 and v['offsets']==1024,'Wrong particle coverage')
        require(0<v['extra_bytes']<=1024**3,'Memory cap exceeded')
        require([h['class_index'] for h in v['hands']]==list(range(169)),'Missing hand classes')
        weighted=[0.,0.]
        for h in v['hands']:
            i=h['class_index'];r,c=divmod(i,13)
            weight=struct.unpack('f',struct.pack('f',(6 if r==c else 4 if r>c else 12)/1326))[0]
            require(len(h['bias_bb'])==len(h['variance_bb2'])==2,'Wrong estimator coverage')
            require(all(math.isfinite(b) and abs(b)<=.0002 for b in h['bias_bb']),'Mean bias exceeded')
            require(all(math.isfinite(x) and x>=0 for x in h['variance_bb2']),'Invalid variance')
            for k,x in enumerate(h['variance_bb2']):weighted[k]+=weight*x
            if h['variance_bb2'][0]>1e-10:near(h['ratio'],h['variance_bb2'][1]/h['variance_bb2'][0])
            else:require(h['ratio'] is None,'Unstable variance ratio')
        for k in range(2):near(weighted[k],v['pooled_variance'][k]);pooled[k]+=weighted[k]
        near(v['ratio'],weighted[1]/weighted[0])
    ratio=pooled[1]/pooled[0];near(ratio,numerical['pooled_ratio'])
    numerical_pass=ratio<=.9 and all(v['ratio']<=1.25 for v in fixtures)
    require(numerical['passed'] is numerical_pass,'Wrong numerical gate')
    rows=[];hashes=set()
    for seed in (42,314159):
        pair=[]
        for enabled in (0,1):
            name=f'pair-control-six-{seed}-{enabled}-v1'
            d=read(name+'-result.json');p=read(name+'-exit.json')
            require(p['returncode']==0 and p['reason'] is None,'Incomplete process')
            hashes.add(p['exe_sha256'])
            require(p['environment_overrides']==({'CONVERGENCE_PAIR_CONTROL':'1'} if enabled else {}),'Wrong environment')
            require(d['samples']==64 and d['schedule']=='gamma15' and d['seed']==seed,'Wrong configuration')
            require(d['target']==.005 and d['roundtrip_exact'] and d['check_policy']=='fixed','Invalid accuracy or roundtrip')
            require(d['normalized_regret'] is False and d['research_restart'] is None
                    and d['control_variate']['refresh_interval'] is None,'Combined experiment')
            if enabled:require(0<d['pair_control_extra_bytes']<=1024**3,'Invalid allocated memory')
            else:require(d['pair_control_extra_bytes'] is None,'Control enabled correction')
            streak=0
            require([c['iteration'] for c in d['checks']]==list(range(25,d['iteration']+1,25)),'Missing accuracy checks')
            for c in d['checks']:
                require(c['full_reference_samples']==1024,'Sampled evaluation')
                require(len(c['gaps'])==len(c['evs'])==6,'Wrong seat coverage')
                require(all(math.isfinite(x) and x>=0 for x in c['gaps']),'Invalid gaps')
                require(all(math.isfinite(x) for x in c['evs']),'Invalid EV')
                near(sum(c['gaps']),c['gap'])
                streak=streak+1 if sum(c['gaps'])<=.005 else 0
                require(c['consecutive_passes']==streak,'Incorrect convergence streak')
            require(d['converged_twice'] is (streak>=2),'Incorrect convergence flag')
            require(math.isfinite(d['total_seconds']) and d['total_seconds']>0,'Invalid timing')
            pair.append(d)
        passed=all(d['converged_twice'] for d in pair) and pair[1]['total_seconds']<=1.25*pair[0]['total_seconds']
        rows.append(dict(seed=seed,passed=passed,iterations=[d['iteration'] for d in pair],
                         seconds=[d['total_seconds'] for d in pair],gaps=[d['checks'][-1]['gap'] for d in pair]))
    require(len(hashes)==1,'Controls used different binaries')
    recorded=read('pair-control-screen-v1.json')
    require([(r['seed'],r['passed']) for r in recorded]==[(r['seed'],r['passed']) for r in rows],'Incorrect speed gate')
    for r,v in zip(recorded,rows):
        near(r['baseline_seconds'],v['seconds'][0]);near(r['candidate_seconds'],v['seconds'][1])
    return dict(evidence_verified=True,numerical_pass=numerical_pass,pooled_variance_ratio=ratio,
                learning_pass=all(r['passed'] for r in rows),learning=rows)


if __name__=='__main__':
    # Exit zero means the evidence checks out, including an honestly rejected candidate.
    print(json.dumps(verify(),indent=2))
