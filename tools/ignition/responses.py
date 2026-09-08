"""Validate and publish known-card response policies, independently by bucket.

Run after fit.py. The opening fit and its evaluation are retained unchanged.
Only aggregate policies/evidence are published; session observations stay local.
"""
import collections, importlib.util, json, re
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('ignition_openings',Path(__file__).with_name('fit.py'))
opening=importlib.util.module_from_spec(spec);spec.loader.exec_module(opening)
BUCKETS=['limps','raise','squeeze','reraise','cold_reraise','limp_defense']
BANDS=['raise_2.5','raise_3.5','raise_5','raise_999']
LABELS=dict(limps='Vs limps',raise_='Vs raise',squeeze='Squeeze',reraise='Vs 3-bet+ after entering',cold_reraise='Cold vs 3-bet+',limp_defense='After limping/calling')
LABELS['raise']=LABELS.pop('raise_')

def subset(sessions,bucket):
    return [dict(s,cells={k.split('/',1)[1]:v for k,v in s['policy_cells'].items() if k.startswith(bucket+'/')}) for s in sessions]

def benchmark(sessions,mix,bucket):
    """Reference-ranked comparator with train-only context targets/reach.

    Match the generator's zero-naivety continue/raise ranking, including its
    half-strength blend. Conditional buckets use observed reaching hand mass.
    Tune probability smoothing separately; this is not an equilibrium solve.
    """
    text=(ROOT/'crates/solver/src/preflop/reference.rs').read_text(encoding='utf-8')
    scores={name:np.array([float(x) for x in re.findall(r'^\s*([\d.]+),',text.split(f'pub const {name}_SCORE:')[1].split('];')[0],re.M)]) for name in ['OPEN','CALL','THREEBET']}
    eq=np.frombuffer((ROOT/'cache/preflop_eq169.bin').read_bytes(),dtype='<f4',offset=4).reshape(169,169)
    strength=eq@(opening.COMBOS/1326)
    rank=lambda v:np.argsort(np.argsort(-v,kind='stable'),kind='stable')
    deep=bucket in ['reraise','cold_reraise']
    cont_score=scores['OPEN'] if bucket=='limps' else scores['CALL']+scores['THREEBET']
    raise_score=scores['OPEN'] if bucket=='limps' else scores['THREEBET']
    cont_order=np.argsort(-strength if deep else -(cont_score+1e-6*strength),kind='stable')
    raise_order=np.argsort(rank(strength) if deep else .5*rank(raise_score+1e-6*strength)+.5*rank(strength),kind='stable')
    cs=opening.arrays(sessions);pooled=sum(cs.values(),np.zeros((169,3)))
    prior=(pooled.sum(0)+.5)/(pooled.sum()+1.5)
    policies={}
    for k,c in cs.items():
        p=(c.sum(0)+100*prior)/(c.sum()+100)
        # Actual training reach avoids treating limpers/raisers as a full deck.
        weight=c.sum(1)+30*(pooled.sum(1)+1)/(pooled.sum()+169)
        def fill(target,capacity,order):
            v=np.zeros(169);remaining=target*weight.sum()
            for h in order:
                take=min(remaining,weight[h]*capacity[h]);v[h]=take/weight[h];remaining-=take
                if remaining<=0:break
            return v
        cont=fill(p[1]+p[2],np.ones(169),cont_order)
        raised=fill(p[2],cont,raise_order)
        policies[k]=(1-mix)*np.column_stack([1-cont,cont-raised,raised])+mix*p
    return policies,np.tile(prior,(169,1)),prior

def gain_ci(learned,reference):
    assert len(learned)==len(reference)
    rows=np.array([(b[0]-a[0],a[1]) for a,b in zip(learned,reference)])
    rng=np.random.default_rng(20260908);gains=[]
    for _ in range(1000):
        x=rows[rng.integers(0,len(rows),len(rows))];gains.append(x[:,0].sum()/x[:,1].sum())
    return np.quantile(gains,[.025,.975]).tolist()

def evaluate(sessions,splits,bucket):
    ss=subset(sessions,bucket)
    tr=[s for s in ss if s['last']<splits['tune_from']]
    tune=[s for s in ss if s['first']>=splits['tune_from'] and s['last']<splits['test_from']]
    test=[s for s in ss if s['first']>=splits['test_from']]
    candidates=[]
    for alpha in [10,30,100,300,1000]:
        for beta in [1,5,20,100]:
            candidates.append(dict(alpha=alpha,beta=beta,loss=opening.loss(opening.score(tune,opening.train(tr,alpha,beta)))))
    best=min(candidates,key=lambda c:c['loss'])
    refs=[dict(mix=m,loss=opening.loss(opening.score(tune,benchmark(tr,m,bucket)))) for m in [.01,.05,.1,.2,.35,.5,.75,1.]]
    ref=min(refs,key=lambda c:c['loss'])
    learned=opening.score(test,opening.train(tr+tune,best['alpha'],best['beta']))
    reference=opening.score(test,benchmark(tr+tune,ref['mix'],bucket))
    ci=gain_ci(learned,reference)
    observed=opening.arrays(ss)
    evidence=dict(opportunities=int(sum(c.sum() for c in observed.values())),test_opportunities=int(sum(n for l,n in learned)),test_sessions=len(learned),
        selected=best,reference_selected=ref,learned_log_loss=opening.loss(learned),reference_log_loss=opening.loss(reference),gain_ci=ci,
        published=ci[0]>0 and len(learned)>=30,candidates=candidates,reference_candidates=refs,
        contexts=[dict(players=n,role=r,opportunities=int(c.sum()),classes=int((c.sum(1)>0).sum())) for (n,r),c in sorted(observed.items())])
    return opening.train(ss,best['alpha'],best['beta']),evidence

def run(source,out):
    d=json.loads(Path(source).read_text(encoding='utf-8'));out=Path(out)
    if d.get('schema')!=2:raise ValueError('Rerun analyze.py to collect response opportunities')
    report=json.loads((out/'NL10.json').read_text(encoding='utf-8'))
    assert d['audit']==report['audit'],'Opening and response source audits differ'
    model=report['model'];dataset=model['stats']['dataset']
    pool=[];pool_ids={};validation={};models={}
    for bucket in BUCKETS+BANDS:
        fitted,evidence=evaluate(d['sessions'],report['splits'],bucket)
        models[bucket]=fitted;validation[bucket]=evidence
        print(f"{bucket}: {evidence['opportunities']} decisions, test {evidence['test_opportunities']}, loss {evidence['reference_log_loss']:.4f} -> {evidence['learned_log_loss']:.4f}, CI {evidence['gain_ci']}, publish {evidence['published']}",flush=True)
    def index(bucket,n,r):
        fitted=models[bucket];near=opening.closest(fitted[0],n,r);key=(bucket,near)
        if key not in pool_ids:
            p=fitted[0][near]
            # Six decimals retain probabilities while keeping saved tables small.
            call=np.round(p[:,1],6);raised=np.minimum(np.round(p[:,2],6),1-call)
            pool_ids[key]=len(pool)
            pool.append(dict(call=call.tolist(),raise_=raised.tolist(),jam=[0.]*169,raise_size=model['stats']['raise_size']))
            pool[-1]['raise']=pool[-1].pop('raise_')
        return pool_ids[key]
    for row in dataset['rows']:
        row['responses']={b:index(b,row['players'],row['role']) for b in BUCKETS+BANDS if validation[b]['published']}
        # If a size-specific estimate fails validation, use the learned pooled
        # response, explicitly labeled as pooled. Never reintroduce hard cutoffs.
        if validation['raise']['published']:
            for b in BANDS:row['responses'].setdefault(b,index('raise',row['players'],row['role']))
    dataset['response_policies']=pool
    dataset['response_notes']={b:(f"Known-card probabilities · {v['opportunities']:,} observed decisions; sparse hands smoothed." if v['published'] else 'Insufficient validation benefit; inferred fallback.') for b,v in validation.items()}
    dataset['scope']='Anonymous opponents, hero excluded; sparse hands smoothed. Position/player count fitted separately in each situation. Unsupported contexts borrow nearby observed positions. Stacks, opponent positions and re-raise depths pooled; postflop hand composition inferred.'
    model['note']=model['note'].split('Opening hand probabilities')[0]+'Known-card preflop policies, including folds, learned separately by situation and position/player count. Sparse cells smoothed; source 3–6 players, no ante, stacks pooled. See docs/ignition_models.md for per-situation validation and limitations.'
    model['source']['version']='2026-09-08-v2'
    model['source']['hand_composition']='known-card preflop probabilities by decision bucket'
    model['source']['assumptions']=['Anonymous seats are not persistent players.','Sparse cells smoothed; unsupported table positions borrow the nearest observed context.','Stacks, aggressor positions and re-raise depths pooled.','Postflop hand composition remains inferred.','Raise/jam sizing uses the configured menu, not a learned sizing distribution.','Source 3–6 players, no ante, SB 0.5bb; other formats unvalidated.']
    report['response_validation']=validation
    for name,value in [('NL10.json',report),('models.json',[model])]:
        (out/name).write_text(json.dumps(value,indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();run(a.input,a.out)
