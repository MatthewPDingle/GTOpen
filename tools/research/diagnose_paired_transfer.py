"""Development-only capacity/transfer diagnostic; no candidate selection or test labels."""
import numpy as np
import paired_continuation_study as study


def design(c, encoder):
    if encoder=='compact18':return study.model.features(c)
    x=c['x'].copy()
    x-= (x*c['mass'][...,None]).sum(axis=(0,1))/2
    spr=c['case']['stack']/c['case']['pot']
    return x*spr/(1+spr)


def action_design(p,encoder):
    result=None
    for c in p['contexts']:
        case=c['case'];term=p['terms'][case['node']]
        sign=1 if term['action']==2 else -1
        x=sign*term['coefficient'][:,None]*case['pot']*design(c,encoder)[0]
        result=x if result is None else result+x
    return result


def fit(p,encoder,penalty,action_weight):
    xs=[];ys=[];ws=[]
    for c in p['contexts']:
        x=design(c,encoder);w=c['mass']*c['qualified'];w/=w.sum()
        xs.append(x.reshape(-1,x.shape[-1]));ys.append((c['corrected']-c['base']).ravel());ws.append(w.ravel()/len(p['contexts']))
    w=p['mass']*p['qualified'];w/=w.sum()
    xs.append(action_design(p,encoder)/5);ys.append((p['reference_delta']['corrected']-p['base_delta'])/5);ws.append(action_weight*w)
    x=np.concatenate(xs);y=np.concatenate(ys);w=np.concatenate(ws)
    return np.linalg.solve(x.T@(w[:,None]*x)+penalty*np.eye(x.shape[1]),x.T@(w*y))


def score(p,encoder,coef):
    delta=p['base_delta'].copy();conservation=0
    for c in p['contexts']:
        b=c['base'];d=design(c,encoder)@coef;spr=c['case']['stack']/c['case']['pot']
        bounds=np.where(d>0,(1+spr-b)/np.maximum(d,1e-100),(b+spr)/np.maximum(-d,1e-100))
        d*=max(0,min(1,float(bounds.min())))
        conservation=max(conservation,abs(((b+d)*c['mass']).sum()-1))
        term=p['terms'][c['case']['node']];sign=1 if term['action']==2 else -1
        delta+=sign*term['coefficient']*c['case']['pot']*d[0]
    assert conservation<1e-8
    w=p['mass']*p['qualified'];w/=w.sum()
    return {key:float(w@abs(delta-truth)) for key,truth in p['reference_delta'].items()}


def main():
    families,inputs=study.training();rows=[]
    choices=[(.1,0),(.1,4),(.001,100),(.00001,1000)]
    for encoder in ['compact18','range54']:
        for name,p in families:
            for penalty,weight in choices:
                coef=fit(p,encoder,penalty,weight)
                rows.append(dict(encoder=encoder,trained_on=name,penalty=penalty,action_weight=weight,
                                 action_mae_bb={nm:score(q,encoder,coef) for nm,q in families}))
    baseline={name:study.model.score(p,dict(coefficients=[0.]*18))['action_mae_bb'] for name,p in families}
    study.write(study.OUT/'transfer-diagnostic.json',dict(checked_at=study.now(),inputs=inputs,baseline=baseline,rows=rows,
        interpretation='Exploratory capacity diagnostic on development families only. Same-family fit is not validation; richer features and extra weights are not retroactive changes to the frozen candidate or protocol.',production_enabled=False))
    for row in rows:print(row,flush=True)


if __name__=='__main__':main()
