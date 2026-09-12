"""Validate the lower-particle GPU screen, including failures; no live access."""
from check_pair_control import near,struct
from check_joint import *


def verify():
    for name in ('tests','cyclic','build'):
        p=read(f'pair-budget-{name}-v2-exit.json')
        require(p['returncode']==0 and p['reason'] is None,'Incomplete prerequisite')
    records=[]
    for line in (RAW/'pair-budget-tests-v2.log').read_text().splitlines():
        if 'PAIR_VARIANCE ' in line:records.append(json.loads(line.split('PAIR_VARIANCE ',1)[1]))
    require(sorted((r['samples'],r['players'],r['family']) for r in records)==
            [(s,n,f) for s in (32,64) for n in (3,4,6,8) for f in range(3)],'Incomplete numerical coverage')
    fixtures={}
    for r in records:
        require(r['offsets']==1024 and 0<r['extra_bytes']<=1024**3,'Invalid numerical configuration')
        require([h['class_index'] for h in r['hands']]==list(range(169)),'Missing hands')
        pooled=[0.,0.]
        for h in r['hands']:
            a,b=divmod(h['class_index'],13)
            weight=struct.unpack('f',struct.pack('f',(6 if a==b else 4 if a>b else 12)/1326))[0]
            require(len(h['bias_bb'])==len(h['variance_bb2'])==2,'Missing estimators')
            require(all(math.isfinite(x) and abs(x)<.0002 for x in h['bias_bb']),'Biased cyclic estimator')
            require(all(math.isfinite(x) and x>=0 for x in h['variance_bb2']),'Invalid variance')
            for i in range(2):pooled[i]+=weight*h['variance_bb2'][i]
            if h['variance_bb2'][0]>1e-10:near(h['ratio'],h['variance_bb2'][1]/h['variance_bb2'][0])
            else:require(h['ratio'] is None,'Unstable hand ratio')
        for i in range(2):near(pooled[i],r['pooled_variance'][i])
        near(r['ratio'],pooled[1]/pooled[0])
        fixtures[r['samples'],r['players'],r['family']]=r
    variance=[]
    for n in (3,4,6,8):
        for f in range(3):
            a=fixtures[64,n,f];b=fixtures[32,n,f]
            variance.append(dict(players=n,family=f,corrected32_over_native64=b['pooled_variance'][1]/a['pooled_variance'][0]))
    rows=[];hashes=set()
    for seed in (42,314159):
        pair=[]
        for enabled,samples in ((0,64),(1,32)):
            name=f'pair-budget-six-{seed}-{enabled}-v2'
            p=read(name+'-exit.json');r=read(name+'-result.json')
            require(p['returncode']==0 and p['reason'] is None,'Incomplete solve')
            hashes.add(p['exe_sha256'])
            require(p['environment_overrides']==({'CONVERGENCE_PAIR_CONTROL':'1'} if enabled else {}),'Wrong controls')
            require(r['seed']==seed and r['samples']==samples and r['schedule']=='gamma15','Wrong experiment')
            require(r['check_policy']=='fixed' and r['target']==.005 and r['roundtrip_exact'],'Changed accuracy')
            require(not r['normalized_regret'] and r['research_restart'] is None and
                    r['control_variate']['refresh_interval'] is None,'Combined experiment')
            if enabled:require(0<r['pair_control_extra_bytes']<=1024**3,'Invalid memory')
            else:require(r['pair_control_extra_bytes'] is None,'Corrected control')
            require([c['iteration'] for c in r['checks']]==list(range(25,r['iteration']+1,25)),'Missing checks')
            streak=0
            for c in r['checks']:
                require(c['full_reference_samples']==1024 and len(c['gaps'])==len(c['evs'])==6,'Wrong evaluation scope')
                require(all(math.isfinite(x) and x>=0 for x in c['gaps']),'Invalid gaps')
                require(all(math.isfinite(x) for x in c['evs']),'Invalid EV')
                near(sum(c['gaps']),c['gap'])
                streak=streak+1 if sum(c['gaps'])<=.005 else 0
                require(c['consecutive_passes']==streak,'Wrong streak')
            require(r['converged_twice'] is (streak>=2),'Wrong convergence')
            require(math.isfinite(r['total_seconds']) and r['total_seconds']>0,'Invalid time')
            pair.append(r)
        rows.append(dict(seed=seed,passed=all(r['converged_twice'] for r in pair) and pair[1]['total_seconds']<pair[0]['total_seconds'],
                         iterations=[r['iteration'] for r in pair],seconds=[r['total_seconds'] for r in pair],
                         gaps=[r['checks'][-1]['gap'] for r in pair]))
    require(len(hashes)==1,'Executable mismatch')
    require(rows==read('pair-budget-screen-v2.json'),'Wrong recorded decision')
    return dict(evidence_verified=True,learning_pass=all(r['passed'] for r in rows),learning=rows,variance=variance)


if __name__=='__main__':print(json.dumps(verify(),indent=2))
