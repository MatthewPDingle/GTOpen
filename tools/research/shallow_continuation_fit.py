"""Small zero-sum low-SPR correction; selection sees synthetic training only."""
import numpy as np
import shallow_continuation_audit as study


def context(case):
    counts, eq = study.pilot.matrices()
    c = study.pilot.context(case, counts, eq)
    w = np.array(case['weights']); base = np.array(study.read(study.ROOT/'cache/realization_fit.json')['class_base'])
    spr = case['stack']/case['pot']; balanced = []
    for p,pos in enumerate([.92, 1.08]):
        opp = counts*w[1-p][None, :]
        a = eq*base[:, None]*pos; b = (1-eq)*base[None, :]*(2-pos)
        adjusted = (opp*a/(a+b)).sum(axis=1)/opp.sum(axis=1)
        balanced.append(c['raw'][p]+min(spr/8,1)*(adjusted-c['raw'][p]))
    c.update(case=case, balanced=np.array(balanced))
    assert abs((c['mass']*c['raw']).sum()-1) < 1e-10
    assert abs((c['mass']*c['balanced']).sum()-1) < 1e-10
    return c


def features(c):
    q = c['raw']-.5; spr = c['case']['stack']/c['case']['pot']
    pos = np.broadcast_to(np.array([-1.,1.])[:,None], q.shape)
    pair = np.broadcast_to(np.array([float(a==b) for a,b,s in study.pilot.PARTS]), q.shape)
    suited = np.broadcast_to(np.array([float(s) for a,b,s in study.pilot.PARTS]), q.shape)
    base = np.stack([q,q*q,q*q*q,pos,pos*q,pair,suited,pair*q,suited*q],axis=-1)
    # Smooth in stack depth and exactly raw-equity in the zero-stack limit.
    x = np.concatenate([base,base*np.log1p(spr)],axis=-1)*spr/(1+spr)
    x -= (x*c['mass'][...,None]).sum(axis=(0,1))/2
    return x


def arrays(case, rows):
    shape = (len(rows),2,169)
    mass = np.zeros(shape); ev = mass.copy(); residual = mass.copy(); gain = mass.copy()
    for i,row in enumerate(rows):
        factor = row['job']['iso_weight']/row['job']['inclusion_probability']
        for p in range(2):
            for h in row['hands'][p]:
                k = study.pilot.INDEX[h['hand']]; w = factor*h['pair_mass']
                mass[i,p,k] = w; ev[i,p,k] = w*h['ev_bb']/case['pot']
                residual[i,p,k] = w*(h['ev_bb']/case['pot']-h['equity'])
                gain[i,p,k] = w*max(0,h['br_ev_bb']-h['ev_bb'])/case['pot']
    return mass,ev,residual,gain


def aggregate(case, rows):
    c = context(case); mass,ev,residual,gain = arrays(case,rows); den = mass.sum(axis=0)
    assert (den>0).all()
    c.update(direct=ev.sum(axis=0)/den, corrected=c['raw']+residual.sum(axis=0)/den,
             gain=gain.sum(axis=0)/den)
    c['qualified'] = c['gain'] <= .005
    return c


def fit(cases, penalty):
    xs=[]; ys=[]; ws=[]
    for c in cases:
        w = c['mass']*c['qualified']; w /= w.sum()
        xs.append(features(c).reshape(-1,18)); ys.append((c['corrected']-c['raw']).ravel()); ws.append(w.ravel()/len(cases))
    x=np.concatenate(xs); y=np.concatenate(ys); w=np.concatenate(ws)
    coef = np.linalg.solve(x.T@(w[:,None]*x)+penalty*np.eye(18), x.T@(w*y))
    return dict(coefficients=coef.tolist(), penalty=penalty, production_enabled=False)


def predict(c, model):
    residual = features(c)@np.array(model['coefficients']); raw=c['raw']; spr=c['case']['stack']/c['case']['pot']
    # One shared multiplier preserves zero-sum accounting and legal payoff bounds.
    limits=np.where(residual>0,(1+spr-raw)/np.maximum(residual,1e-100),
                    (raw+spr)/np.maximum(-residual,1e-100))
    scale=min(1.,float(limits.min())); value=raw+scale*residual
    assert abs((value*c['mass']).sum()-1)<1e-9
    assert value.min()>=-spr-1e-9 and value.max()<=1+spr+1e-9
    return value


def score(c, value, key='corrected'):
    w=c['mass']*c['qualified']; return float((w*abs(value-c[key])).sum()/w.sum())


def train():
    m=study.checked(); cases=[]
    assert not (study.OUT/'candidate.json').exists(), 'Preserve the frozen candidate'
    for c in m['cases']:
        if c['partition']!='train': continue
        rows=[]
        for j in m['jobs']:
            if j['case']==c['id']:
                row=study.read(study.OUT/'jobs'/(j['id']+'.json')); study.old.validate(row,j,m); rows.append(row)
        cases.append(aggregate(c,rows))
    scores=[]; families=sorted({c['case']['family'] for c in cases})
    for penalty in [.0001,.001,.01,.1]:
        fold=[]
        for family in families:
            model=fit([c for c in cases if c['case']['family']!=family],penalty)
            for c in cases:
                if c['case']['family']==family:
                    fold.append(dict(case=c['case']['id'], candidate=score(c,predict(c,model)),
                                     balanced=score(c,c['balanced']), raw=score(c,c['raw'])))
        scores.append(dict(penalty=penalty, cases=fold, mean=float(np.mean([r['candidate'] for r in fold]))))
    best=min(scores,key=lambda r:r['mean']); model=fit(cases,best['penalty'])
    model.update(frozen_at=study.now(), training_cases=[c['case']['id'] for c in cases],
                 selection='leave one synthetic range-pair family out; heldout ranges excluded',
                 supported_research_spr=[.2,.75], input_manifest=m['id'])
    study.write(study.OUT/'training-screen.json',dict(scores=scores,selected_penalty=best['penalty']))
    study.write(study.OUT/'candidate.json',model)
    study.write(study.OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(study.OUT/'candidate.json'), frozen_at=study.now()))
    print('Frozen candidate, penalty',best['penalty'],flush=True)


if __name__=='__main__': train()
