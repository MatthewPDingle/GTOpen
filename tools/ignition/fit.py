"""Learn anonymous NL10 opening policies with untouched chronological test sessions."""
import collections, json, math, sys, re
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'coinpoker'))
from fit import make_model,merge,n as count
from context import ROLES
COMBOS=np.array([6 if h//13==h%13 else 4 if h//13>h%13 else 12 for h in range(169)])

def reference_model(sessions,mix):
    repo=Path(__file__).resolve().parents[2]
    text=(repo/'crates/solver/src/preflop/reference.rs').read_text()
    scores=np.array([float(x) for x in re.findall(r'^\s*([\d.]+),',text.split('pub const OPEN_SCORE:')[1].split('];')[0],re.M)])
    equity=np.frombuffer((repo/'cache/preflop_eq169.bin').read_bytes(),dtype='<f4',offset=4).reshape(169,169)
    strength=equity@(COMBOS/1326)
    order=np.argsort(-(scores+1e-6*strength),kind='stable')
    contexts=arrays(sessions);pool=sum(contexts.values(),np.zeros((169,3))).sum(0)
    pool=(pool+.5)/(pool.sum()+1.5);policies={}
    for k,c in contexts.items():
        p=(c.sum(0)+100*pool)/(c.sum()+100)
        def fill(target):
            v=np.zeros(169);remaining=target*1326
            for h in order:
                take=min(remaining,COMBOS[h]);v[h]=take/COMBOS[h];remaining-=take
                if remaining<=0:break
            return v
        cont=fill(p[1]+p[2]);raise_=fill(p[2]);matrix=np.column_stack([1-cont,cont-raise_,raise_])
        policies[k]=(1-mix)*matrix+mix*p
    return policies,np.tile(pool,(169,1)),pool

def arrays(sessions):
    out=collections.defaultdict(lambda:np.zeros((169,3)))
    for s in sessions:
        for key,v in s['cells'].items():
            prefix,act=key.split('|');n,pos,h=prefix.split('/')
            out[(int(n),ROLES[pos])][int(h),['fold','call','raise'].index(act)]+=v
    return dict(out)

def train(sessions,alpha,beta):
    counts=arrays(sessions);allhands=sum(counts.values(),np.zeros((169,3)))
    prior=(allhands.sum(0)+.5)/(allhands.sum()+1.5)
    hand=(allhands+beta*prior)/(allhands.sum(1)[:,None]+beta)
    policies={k:(c+alpha*hand)/(c.sum(1)[:,None]+alpha) for k,c in counts.items()}
    return policies,hand,prior

def closest(policies,n,r):
    # Unsupported contexts borrow an observed neighbor; no invented labels.
    candidates=[k for k in policies if k[1]==r]
    if not candidates:
        candidates=[k for k in policies if (k[1]>=0)==(r>=0)] or list(policies)
    return min(candidates,key=lambda k:(abs(k[1]-r),abs(k[0]-n),-k[0]))

def score(sessions,model,handblind=False):
    policies,hand,prior=model;rows=[]
    for session in sessions:
        loss=den=0.
        for (n,r),c in arrays([session]).items():
            p=policies[closest(policies,n,r)]
            if handblind:
                # Learn aggregate rates from training probabilities, never test actions.
                p=np.tile((p*COMBOS[:,None]).sum(0)/1326,(169,1))
            loss-=float((c*np.log(np.maximum(p,1e-12))).sum());den+=c.sum()
        if den:rows.append((loss,den))
    return rows

def loss(rows):return sum(v for v,n in rows)/sum(n for v,n in rows)

def fit(source,out):
    d=json.loads(Path(source).read_text());sessions=d['sessions']
    if d['audit'].get('duplicate_variants'):raise ValueError('Resolve duplicate conflicts')
    dates=sorted(set(s['last'] for s in sessions));cut1=dates[int(len(dates)*.6)];cut2=dates[int(len(dates)*.8)]
    tr=[s for s in sessions if s['last']<cut1]
    tune=[s for s in sessions if s['first']>=cut1 and s['last']<cut2]
    test=[s for s in sessions if s['first']>=cut2]
    excluded=[s for s in sessions if s not in tr+tune+test]
    if min(len(tr),len(tune),len(test))<15:raise ValueError('Too few independent sessions')
    candidates=[]
    for alpha in [10,30,100,300,1000]:
        for beta in [1,5,20,100]:
            model=train(tr,alpha,beta)
            candidates.append(dict(alpha=alpha,beta=beta,validation_log_loss=loss(score(tune,model))))
    best=min(candidates,key=lambda c:c['validation_log_loss'])
    ref_candidates=[dict(mix=v,validation_log_loss=loss(score(tune,reference_model(tr,v)))) for v in [.01,.05,.1,.2,.35,.5,.75,1.]]
    ref_best=min(ref_candidates,key=lambda c:c['validation_log_loss'])
    model=train(tr+tune,best['alpha'],best['beta'])
    learned=score(test,model);blind=score(test,model,True)
    reference=score(test,reference_model(tr+tune,ref_best['mix']))
    rows=np.array([(b[0]-a[0],a[1]) for a,b in zip(learned,blind)])
    rng=np.random.default_rng(20260908);gains=[]
    for _ in range(1000):
        x=rows[rng.integers(0,len(rows),len(rows))];gains.append(x[:,0].sum()/x[:,1].sum())
    ci=np.quantile(gains,[.025,.975]).tolist()
    if ci[0]<=0:raise ValueError('No reliable held-out benefit from learned hand composition')
    ref_rows=np.array([(b[0]-a[0],a[1]) for a,b in zip(learned,reference)])
    ref_gains=[]
    for _ in range(1000):
        x=ref_rows[rng.integers(0,len(ref_rows),len(ref_rows))];ref_gains.append(x[:,0].sum()/x[:,1].sum())
    ref_ci=np.quantile(ref_gains,[.025,.975]).tolist()
    if ref_ci[0]<=0:raise ValueError('No reliable improvement over smoothed reference-ordered ranges')
    final=train(sessions,best['alpha'],best['beta'])
    pool=merge(s['counts'] for s in sessions)
    sourceinfo=dict(site='Ignition',stakes='NL10 regular',date_from=min(s['first'] for s in sessions),date_to=max(s['last'] for s in sessions),players=0,
                    sessions=len(sessions),unique_hands=d['audit']['accepted'],version='2026-09-08-v1')
    m=make_model('NL10 regular','Pool',pool,pool,sourceinfo)
    m['name']='Data · Ignition · NL10 regular · Pool'
    # Other buckets/postflop are measured aggregate frequencies with inferred cards.
    iso=m['stats']['iso_raise'];limp=m['stats']['limp_behind']
    combos=COMBOS
    datasetrows=[];contextcoverage=[]
    observed=arrays(sessions)
    for n in range(2,10):
        for role in [-2,-1,*range(n-2)]:
            near=closest(final[0],n,role);p=final[0][near]
            if role==-2:
                # BB has no first-in decision after folds; free check remains legal.
                p=np.tile([0.,1.,0.],(169,1))
            avg=(p*combos[:,None]).sum(0)/1326
            datasetrows.append(dict(players=n,role=role,open_raise=float(avg[2]*100),open_limp=float(avg[1]*100),iso_raise=iso,limp_behind=limp,
                                    opening=dict(call=p[:,1].tolist(),raise_=p[:,2].tolist(),jam=[0.]*169,raise_size=m['stats']['raise_size'])))
            datasetrows[-1]['opening']['raise']=datasetrows[-1]['opening'].pop('raise_')
    for (n,r),c in sorted(observed.items()):
        contextcoverage.append(dict(players=n,role=r,opportunities=int(c.sum()),hands_seen=int((c.sum(1)>0).sum()),median_per_class=float(np.median(c.sum(1)))))
    m['stats']['dataset']=dict(site='Ignition NL10 regular',min_players=3,max_players=6,ante=False,small_blind_bb=.5,empirical_opening=True,
        scope='Anonymous opponent pool, hero excluded; stacks pooled. Sparse hands borrow pooled estimates. Unsupported contexts borrow the nearest observed position/table size. Other action buckets use aggregate frequencies and inferred hands.',rows=datasetrows)
    m['source'].update(dict(type='anonymous_pool',players=None,hand_composition='known-card first-in probabilities',
                            assumptions=['Anonymous seats are not persistent players.','Stacks pooled; sparse cells smoothed.','Other preflop and postflop card composition inferred.','Outside 3–6 players borrows the nearest observed context; site/ante/stack transfer unvalidated.','Configured smallest/largest sizes approximate the observed distribution.']))
    m['note']=(f"Ignition NL10 regular · anonymous opponent pool, excluding your hands. {sourceinfo['date_from']}–{sourceinfo['date_to']}; "
               f"{sourceinfo['unique_hands']:,} validated hands, {len(sessions)} sessions. Opening hand probabilities learned from known cards including folds, smoothed by position/player count. "
               "3–6 players, no ante, stacks pooled. Other ranges inferred from measured frequencies. Outside source contexts uses nearest observed context. Validation: docs/ignition_models.md.")
    report=dict(source=sourceinfo,audit=d['audit'],splits=dict(tune_from=cut1,test_from=cut2,train_sessions=len(tr),tune_sessions=len(tune),test_sessions=len(test),cross_boundary_sessions_excluded=len(excluded)),
                validation=dict(candidates=candidates,selected=best,test_log_loss=loss(learned),handblind_test_log_loss=loss(blind),test_opportunities=int(sum(n for l,n in learned)),session_bootstrap_gain_ci=ci,
                                reference_candidates=ref_candidates,reference_selected=ref_best,reference_test_log_loss=loss(reference),reference_gain_ci=ref_ci),
                contexts=contextcoverage,pool_counts=pool,model=m)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'NL10.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    (out/'models.json').write_text(json.dumps([m],indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(splits=report['splits'],validation=report['validation']),indent=2))

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--out',required=True);a=ap.parse_args();fit(a.input,a.out)
