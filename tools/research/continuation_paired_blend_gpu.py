"""N35 fixed 25% learned blend, isolated correctness and settling experiment."""
import datetime as dt
import math
from pathlib import Path
import sys
import continuation_chance_control as control
import continuation_policy_stability as stability

study=control.study
BASE=control.BASE
OUT=BASE/'paired-blend-gpu-20260916'
SOURCE=BASE/'chance-control-20260916/500/policy.gtop'
ORACLE_SOURCE=BASE/'policy-stability-20260916/candidate/1500/policy.gtop'
OLD=control.KERNEL
NEW=OUT/'interface.cu'
runtime=control.transfer.original.runtime

def prepare():
    assert study.read(BASE/'paired-blend-20260916/training-screen.json')['selected_alpha']==.25
    OUT.mkdir(parents=True,exist_ok=True)
    original=OLD.read_bytes()
    before=b'for(int h=threadIdx.x;h<169;h+=blockDim.x){double pred=qraw[side*169+h]+correction[side*169+h]-center;'
    after=b'''for(int h=threadIdx.x;h<169;h+=blockDim.x){double pred=qraw[side*169+h]+correction[side*169+h]-center;
  double pair_raw=0.,pair_balanced=0.;
  for(int j=0;j<169;j++){double w=compatible(h,j)/combos(h)/combos(j)*d[(1-side)*169+j];
   pair_raw+=w*eq[j*169+h];pair_balanced+=w*eq[(side?2:1)*169*169+j*169+h];}
  double legal_mass=legal(h,d+(1-side)*169,rankmass+(1-side)*13);
  double realization_blend=fmin(1.,fabs((double)rw[(size_t)nd*np+p]-1.)/.08);
  double baseline=(pair_raw+realization_blend*(pair_balanced-pair_raw))/legal_mass;
  pred=.75*baseline+.25*pred;'''
    assert original.count(before)==1
    changed=original.replace(before,after)
    if NEW.exists():assert NEW.read_bytes()==changed
    else:NEW.write_bytes(changed)
    inputs=dict(study.read(control.FULL/'manifest.json')['files'])
    for p in [Path(__file__),OUT/'README.md',OLD,NEW,SOURCE,ORACLE_SOURCE,
              BASE/'paired-blend-20260916/training-screen.json',BASE/'paired-blend-20260916/protocol-freeze.json']:
        inputs[str(p.resolve().relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(p)
    for p,h in inputs.items():assert study.pilot.sha(study.ROOT/p)==h,p
    freeze=OUT/'protocol-freeze.json'
    if freeze.exists():assert study.read(freeze)['inputs']==inputs
    else:study.freeze(freeze,dict(registered_at=study.night.now(),inputs=inputs,alpha=.25,start_iteration=500,checkpoints=[750,1000],production_enabled=False))

def state(stage,**fields):
    study.night.dump(OUT/'status.json',dict(stage=stage,updated=study.night.now(),production_enabled=False,**fields));print(stage,fields,flush=True)

def remaining():return (control.transfer.original.bridge.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()

def idle():
    control.idle()
    assert study.read(BASE/'zero-fallback-20260916/status.json')['stage']=='complete','Wait for N32 to finish'

def linearity(a,b,c):
    assert a['iteration']==b['iteration']==c['iteration']
    assert len(a['rows'])==len(b['rows'])==len(c['rows'])>0
    maximum=0.;count=0
    for x,y,z in zip(a['rows'],b['rows'],c['rows']):
        assert x['node']==y['node']==z['node'] and x['actions']==y['actions']==z['actions']
        assert len(x['hands'])==len(y['hands'])==len(z['hands'])
        for h,j,k in zip(x['hands'],y['hands'],z['hands']):
            assert h['class_index']==j['class_index']==k['class_index']
            assert h['actor_reach']==j['actor_reach']==k['actor_reach']
            for av,bv,cv in zip(h['action_values_counterfactual_bb'],j['action_values_counterfactual_bb'],k['action_values_counterfactual_bb']):
                assert all(math.isfinite(v) for v in [av,bv,cv])
                maximum=max(maximum,abs(cv-(.75*av+.25*bv)));count+=1
    assert count>0
    return dict(maximum_difference_bb=maximum,values=count,passed=maximum<=2e-6)

def run():
    idle();prepare();assert remaining()>=1800
    assert not (OUT/'result.json').exists()
    oracle=OUT/'oracle';oracle.mkdir(exist_ok=True);state('oracle')
    for name,model,kernel in [('balanced','balanced',OLD),('learned','candidate',OLD),('blend','candidate',NEW)]:
        output=oracle/f'{name}.json';assert not output.exists()
        runtime.command(['evaluate',ORACLE_SOURCE,output,model,kernel],oracle/f'{name}.log',optimized=True,warm=0)
    parity=linearity(*[study.read(oracle/f'{name}.json') for name in ['balanced','learned','blend']])
    study.freeze(OUT/'oracle-linearity.json',parity);assert parity['passed'],parity
    for n in [2,3,8]:
        output=oracle/f'zero-{n}.json'
        runtime.command(['oracle',output,NEW,'candidate',n,'zeros'],oracle/f'zero-{n}.log',optimized=True,warm=0)
        s=study.read(output)
        assert all(math.isfinite(x) for x in s['gaps']+s['evs']) and abs(sum(s['evs']))<.0002
        for row in s['frontier']['rows']:
            for h in row['hands']:assert all(math.isfinite(x) for x in h['action_values_counterfactual_bb'])
    sources={a:SOURCE for a in ['control','blend']};snapshots={a:[] for a in sources}
    for iteration,order in [(750,['control','blend']),(1000,['blend','control'])]:
        for arm in order:
            idle();assert remaining()>450,'Insufficient time for bounded 250-step arm'
            state('learning',arm=arm,iteration=iteration)
            folder=OUT/arm/str(iteration);folder.mkdir(parents=True,exist_ok=True)
            model='balanced' if arm=='control' else 'candidate';kernel=OLD if arm=='control' else NEW
            assert not (folder/'policy.gtop').exists()
            runtime.command(['solve',sources[arm],folder,model,250,kernel,'resume'],folder/'run.log',optimized=True,warm=0)
            s=study.read(folder/f'iteration-{iteration}.json')
            assert s['iteration']==iteration and s['start_iteration']==iteration-250 and s['warmup_iterations']==0
            assert all(math.isfinite(x) for x in s['gaps']+s['evs']) and abs(sum(s['evs']))<.0002
            snapshots[arm].append(s);sources[arm]=folder/'policy.gtop'
    prepare()
    changes={a:stability.changes(*s) for a,s in snapshots.items()}
    times={a:sum(s['learning_seconds'] for s in ss) for a,ss in snapshots.items()}
    hashes={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in OUT.glob('*/*/iteration-*.json')}
    result=dict(changes=changes,learning_seconds=times,learning_time_ratio=times['blend']/times['control'],snapshot_hashes=hashes,
        desired_time_ratio_met=times['blend']<=1.1*times['control'],production_enabled=False,
        caveat='One ordered warm-start comparison, not repeated timing, cold-start time to target, fresh accuracy validation or full-game convergence.')
    study.freeze(OUT/'result.json',result);state('complete',settling_signal=changes['blend']['signal_passed'],learning_time_ratio=result['learning_time_ratio'])

if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
