"""Entry frequencies: fit table geometry separately from player-type intercepts.

Only aggregate opportunity counters are exported. Hand composition is inferred.
"""
import collections, math
import numpy as np
from scipy.optimize import minimize
from sklearn.linear_model import LogisticRegression

ROLES={'BTN':0,'CO':1,'HJ':2,'LJ':3,'UTG':4,'SB':-1,'BB':-2}
ACTIONS=['fold','call','raise']

def observations(c,situation):
    out=[]
    for key,value in c.items():
        if not key.startswith('context/') or not value: continue
        prefix,action=key.split('|'); _,n,pos,sit=prefix.split('/')
        if sit==situation and action in ACTIONS and pos in ROLES:
            out.append((int(n),ROLES[pos],ACTIONS.index(action),value))
    return out

def design(n,role,occupancy=True):
    return [max(role,0),float(role==-1),float(role==-2)]+([n-6] if occupancy else [])

def fit(c,sit,occupancy=True):
    obs=observations(c,sit)
    model=LogisticRegression(C=.01,max_iter=500,tol=1e-9)
    model.fit([design(n,r,occupancy) for n,r,a,k in obs], [a for n,r,a,k in obs],sample_weight=[k for n,r,a,k in obs])
    return model

def predict(model,n,role,occupancy=True):
    # Extrapolate the learned linear log odds beyond 5–7; disclose in UI.
    return model.predict_proba([design(n,role,occupancy)])[0]

def score(c,sit,model,occupancy=True):
    obs=observations(c,sit)
    if not obs: return 0.,0
    probs=model.predict_proba([design(n,r,occupancy) for n,r,a,k in obs])
    return sum(-k*math.log(max(p[a],1e-12)) for p,(n,r,a,k) in zip(probs,obs)),sum(k for n,r,a,k in obs)

def legacy_score(c,sit,prior):
    vals=[prior.get('pre/'+sit+'|'+a,0)+.5 for a in ACTIONS]
    probs=np.array(vals)/sum(vals); loss=den=0
    for n,r,a,k in observations(c,sit):
        refs=[11,12.5,14,16,19.5,26,42][-(n-2):]+[35]
        value=35 if r==-1 else 1 if r==-2 else [42,26,19.5,16,14,12.5,11][r]
        factor=1 if r==-2 else value/np.mean(refs)
        if sit=='limps': factor=math.sqrt(factor)
        cont=min(1.,(probs[1]+probs[2])*factor); raised=min(cont,probs[2]*factor)
        p=[1-cont,cont-raised,raised]
        loss-=k*math.log(max(p[a],1e-6));den+=k
    return loss,den

def select(players):
    train=collections.Counter();held=[]
    for pid,cs in players.items():
        if int(pid[:8],16)%5: train.update(cs[0])
        elif sum(v for k,v in cs[0].items() if k.startswith('vpip|'))>=100: held.append(cs[1])
    result={}
    for sit in ['open','limps']:
        candidates=[]
        for occ in [False,True]:
            model=fit(train,sit,occ)
            scores=[score(c,sit,model,occ) for c in held]
            loss=sum(x for x,n in scores)/sum(n for x,n in scores)
            candidates.append(dict(occupancy=occ,log_loss=loss))
        best=min(r['log_loss'] for r in candidates)
        chosen=next(r for r in candidates if r['log_loss']<=best+.0001)
        legacy=[legacy_score(c,sit,train) for c in held]
        model=fit(train,sit,chosen['occupancy'])
        rows=np.array([(l-score(c,sit,model,chosen['occupancy'])[0],n) for c,(l,n) in zip(held,legacy) if n])
        rng=np.random.default_rng(20260908)
        gains=[]
        for _ in range(500):
            b=rows[rng.integers(0,len(rows),len(rows))];gains.append(b[:,0].sum()/b[:,1].sum())
        result[sit]=dict(candidates=candidates,selected_occupancy=chosen['occupancy'],
                        legacy_log_loss=sum(l for l,n in legacy)/sum(n for l,n in legacy),
                        selected_log_loss=chosen['log_loss'],validation_opportunities=sum(n for l,n in legacy),
                        player_bootstrap_gain_ci=np.quantile(gains,[.025,.975]).tolist())
        if result[sit]['player_bootstrap_gain_ci'][0]<=0:
            raise ValueError(f'{sit}: contextual model has no reliable improvement over existing position prior')
    return result

def export(c,pool,validation):
    models={sit:fit(pool,sit,validation[sit]['selected_occupancy']) for sit in ['open','limps']}
    shifts={}
    for sit in models:
        obs=observations(c,sit); occ=validation[sit]['selected_occupancy']
        x=np.array([np.log(np.maximum(predict(models[sit],n,r,occ),1e-12)) for n,r,a,k in obs])
        y=np.array([a for n,r,a,k in obs]);w=np.array([k for n,r,a,k in obs])
        def objective(z):
            logits=x+np.array([0,z[0],z[1]])
            norm=np.logaddexp.reduce(logits,axis=1)
            return float(np.sum(w*(norm-logits[np.arange(len(y)),y]))+100*np.square(z).sum())
        res=minimize(objective,[0.,0.],method='BFGS',tol=1e-6)
        if not np.all(np.isfinite(res.x)): raise ValueError('Invalid type intercept')
        shifts[sit]=[0.,*res.x]
    rows=[]
    for n in range(2,10):
        for role in [-2,-1,*range(n-2)]:
            vals={}
            for sit in models:
                logits=np.log(np.maximum(predict(models[sit],n,role,validation[sit]['selected_occupancy']),1e-12))+shifts[sit]
                prob=np.exp(logits-np.logaddexp.reduce(logits))
                vals[sit]=prob
            rows.append(dict(players=n,role=role,open_raise=float(vals['open'][2]*100),open_limp=float(vals['open'][1]*100),
                             iso_raise=float(vals['limps'][2]*100),limp_behind=float(vals['limps'][1]*100)))
    return dict(site='CoinPoker',min_players=5,max_players=7,ante=True,empirical_opening=False,
                scope='2025 ante sample; stacks pooled. Entry frequencies fitted by position and player count; hand composition inferred.',rows=rows)
