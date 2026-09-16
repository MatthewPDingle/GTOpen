"""Fresh continuation references for the frozen interface experiment; no fitting."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import collections,hashlib,json,pathlib,subprocess,sys
import numpy as np
import learned_interface as study
import range_value_pilot as pilot
import continuation_overnight as night
import continuation_overnight_fit as fit
from continuation_checkpoint import same_job
OUT=study.OUT/'references'
ROOT=pilot.ROOT

def checked():
    study.freeze()
    m=json.loads((OUT/'manifest.json').read_text())
    payload={k:v for k,v in m.items() if k!='id'}
    assert hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()==m['id']
    assert pilot.sha(ROOT/m['binary_path'])==m['binary_sha256']
    assert pilot.sha(night.OUT/'candidate.json')==m['model_sha256']
    assert pilot.sha(study.OUT/'candidate/iteration-250.json')==m['source_sha256']
    return m

def prepare():
    study.freeze();OUT.mkdir(exist_ok=True)
    source=study.OUT/'candidate/iteration-250.json'
    result=json.loads(source.read_text());cases=[]
    for leaf in result['leaves']:
        assert 1<=leaf['stack']/leaf['pot']<=20
        w,removed,added=night.clean_weights(leaf['weights'])
        text=lambda p:','.join(f'{pilot.LABELS[h]}:{v:.9f}' for h,v in enumerate(w[p]) if v>0)
        cases.append(dict(leaf,weights=w.tolist(),range_oop=text(0),range_ip=text(1),
                          removed_mass_fraction=removed,probe_added_mass_fraction=added))
    assert len(cases)==2
    old=json.loads((night.OUT/'manifest.json').read_text())
    excluded={j['board'] for j in old['jobs']}
    for directory in [pilot.OUT,pilot.AUDIT,pilot.AUDIT/'extension']:
        excluded.update(b['board'] for b in json.loads((directory/'manifest.json').read_text())['boards'])
    groups=collections.defaultdict(list)
    for board,iso in json.loads((pilot.AUDIT/'fixtures.json').read_text())['canonical_flops']:
        if board in excluded:continue
        cards=[board[i:i+2] for i in range(0,6,2)]
        key=('paired' if len({c[0] for c in cards})<3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    boards=[]
    for key,rows in sorted(groups.items()):
        rows.sort(key=lambda x:hashlib.sha256(('anchored-interface-20260916'+x[0]).encode()).digest())
        for board,iso in rows[:4]:boards.append(dict(board=board,iso_weight=iso,stratum=key,inclusion_probability=4/len(rows)))
    assert len(boards)==20
    jobs=[]
    for b in boards:
        for c in cases:
            size={'bet':[{'PotPct':50}],'raise':[{'PotPct':100}],'donk':[{'PotPct':50}]}
            config=dict(board=b['board'],range_oop=c['range_oop'],range_ip=c['range_ip'],tree=dict(
                starting_pot=c['pot'],effective_stack=c['stack'],rake_pct=0,rake_cap=0,
                oop=[size]*3,ip=[size]*3,max_raises=1,add_allin=False,allin_threshold=.85))
            jobs.append(dict(**b,case=c['id'],id=c['id']+'-'+b['board'],config=config))
    binary=ROOT/old['binary_path'];assert pilot.sha(binary)==old['binary_sha256']
    m=dict(cases=cases,boards=boards,jobs=jobs,binary_path=old['binary_path'],binary_sha256=old['binary_sha256'],
        source_sha256=pilot.sha(source),model_sha256=pilot.sha(night.OUT/'candidate.json'),
        target_gap_pct=.1,max_iterations=2000,
        protocol='Two candidate-250 blind-call branches; 20 previously unused stratified flops each. Frozen predictor, no fitting. Screen for at least 15% lower weighted MAE than original Balanced in EACH case; exploratory bootstrap uncertainty. These ranges are new but the source scenario family is not independent of training. This is not a deployment or convergence test.')
    m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
    path=OUT/'manifest.json'
    if path.exists():assert json.loads(path.read_text())==m
    else:study.write(path,m)
    print('Frozen 40 new postflop references.',flush=True)

def run():
    m=checked();binary=ROOT/m['binary_path']
    env=dict(os.environ);env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for batch in range(10):
        assert not night.live_busy(),'Live application is busy; research deferred'
        with (OUT/f'batch-{batch}.log').open('a') as log:
            subprocess.run([str(binary),str(OUT/'manifest.json'),'4'],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
        print('Reference batch',batch+1,'of 10 complete',flush=True)

def analyze():
    m=checked();counts,eq=pilot.matrices()
    model=json.loads((night.OUT/'candidate.json').read_text());reports=[]
    K=counts/pilot.COMBOS[:,None]/pilot.COMBOS[None,:]
    base=np.array(json.loads((ROOT/'cache/realization_fit.json').read_text())['class_base'])
    for case in m['cases']:
        rows=[]
        for job in m['jobs']:
            if job['case']!=case['id']:continue
            row=json.loads((OUT/'jobs'/f"{job['id']}.json").read_text())
            assert row['manifest_id']==m['id'] and same_job(row['job'],job) and row['target_met']
            rows.append(row)
        ctx=pilot.context(case,counts,eq);ctx.update(base_x=ctx['x'].copy(),base_names=ctx['names'],case=case)
        residual,observed,uncorrected=pilot.aggregate(case,rows);target=ctx['raw']+residual
        d=np.array(case['weights'])*pilot.COMBOS;d/=d.sum(axis=1,keepdims=True)
        paired=[]
        for side,pos in enumerate([.92,1.08]):
            a=eq*base[:,None]*pos;b=(1-eq)*base[None,:]*(2-pos)
            rel=(K*(a/(a+b)))@d[1-side]/(K@d[1-side])
            paired.append(ctx['raw'][side]+min(case['stack']/case['pot']/8,1)*(rel-ctx['raw'][side]))
        predictions=dict(original=ctx['balanced'],paired=np.array(paired),candidate=fit.predict(ctx,model),raw=ctx['raw'])
        weight=ctx['mass']*(observed>0);weight/=weight.sum()
        metric=lambda y:{name:float((abs(pred-y)*weight).sum()) for name,pred in predictions.items()}
        errors=metric(target);improvement=1-errors['candidate']/errors['original']
        probe_index=[pilot.INDEX[h] for h in night.PROBES]
        assert (observed[:,probe_index]>0).all(),'Probe lacks a reference observation'
        probe_errors={name:float(abs(pred[:,probe_index]-target[:,probe_index]).mean()) for name,pred in predictions.items()}
        rng=np.random.default_rng(20260916);bygroup=collections.defaultdict(list)
        for row in rows:bygroup[row['job']['stratum']].append(row)
        improvements=[]
        for _ in range(300):
            sample=[group[i] for group in bygroup.values() for i in rng.integers(0,len(group),len(group))]
            res,_,_=pilot.aggregate(case,sample);e=metric(ctx['raw']+res);improvements.append(1-e['candidate']/e['original'])
        hands=[]
        for side in range(2):
            for h in range(169):
                if observed[side,h]<=0:continue
                hands.append(dict(position=case['positions'][side],hand=pilot.LABELS[h],mass=float(ctx['mass'][side,h]),
                    reference=float(target[side,h]),**{name:float(pred[side,h]) for name,pred in predictions.items()},
                    deterioration=float(abs(predictions['candidate'][side,h]-target[side,h])-abs(predictions['original'][side,h]-target[side,h]))))
        reports.append(dict(case=case['id'],positions=case['positions'],spr=case['stack']/case['pot'],
            weighted_mae_pot=errors,improvement=improvement,bootstrap_90_improvement=np.quantile(improvements,[.05,.95]).tolist(),
            uniform_probe_mae_pot=probe_errors,
            negative_candidate_predictions=[dict(position=case['positions'][p],hand=pilot.LABELS[h],value=float(predictions['candidate'][p,h]),mass=float(ctx['mass'][p,h])) for p,h in zip(*np.where(predictions['candidate']<0))],
            screening_pass=improvement>=.15,max_reference_gap_pct=max(r['gap_pct'] for r in rows),
            probes=[h for h in hands if h['hand'] in night.PROBES],
            worst_mass_weighted_regressions=sorted(hands,key=lambda h:h['deterioration']*h['mass'],reverse=True)[:12],
            worst_regressions=sorted(hands,key=lambda h:h['deterioration'],reverse=True)[:12]))
    study.write(OUT/'comparison.json',dict(cases=reports,all_screening_pass=all(c['screening_pass'] for c in reports),
        caveat='Small 20-flop samples exclude earlier boards; control-variate conditional labels and bootstrap intervals are approximate. Model family/scenario transfer, not fully independent generalization. No refitting.'))
    print(json.dumps([{k:v for k,v in r.items() if k not in ['probes','worst_regressions','worst_mass_weighted_regressions']} for r in reports],indent=2))

if __name__=='__main__':{'prepare':prepare,'run':run,'analyze':analyze}[sys.argv[1]]()
