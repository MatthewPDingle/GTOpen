"""Bounded four-family development screen; reserved test labels are not read."""
import collections
import numpy as np
import paired_continuation_expansion as expansion
import diagnose_paired_transfer as diagnostic

study=expansion.pilot
OUT=expansion.OUT


def families():
    result,inputs=study.training();m=expansion.checked();rows=collections.defaultdict(list)
    for j in m['jobs']:
        path=OUT/'jobs'/(j['id']+'.json');row=study.read(path)
        study.native.previous.old.validate(row,j,m);rows[j['case']].append(row)
        inputs[path.relative_to(study.ROOT).as_posix()]=study.pilot.sha(path)
    for family,path in m['trees'].items():
        cases=[c for c in m['cases'] if c['family']==family]
        result.append((family,study.model.pack(study.read(study.ROOT/path),cases,rows)))
    return result,inputs


def fit(packs,encoder,penalty,weight):
    xs=[];ys=[];ws=[]
    for p in packs:
        for c in p['contexts']:
            x=diagnostic.design(c,encoder);w=c['mass']*c['qualified'];w/=w.sum()
            xs.append(x.reshape(-1,x.shape[-1]));ys.append((c['corrected']-c['base']).ravel());ws.append(w.ravel()/len(p['contexts'])/len(packs))
        w=p['mass']*p['qualified'];assert w.sum()>0;w/=w.sum()
        xs.append(diagnostic.action_design(p,encoder)/5);ys.append((p['reference_delta']['corrected']-p['base_delta'])/5);ws.append(weight*w/len(packs))
    x=np.concatenate(xs);y=np.concatenate(ys);w=np.concatenate(ws)
    return np.linalg.solve(x.T@(w[:,None]*x)+penalty*np.eye(x.shape[1]),x.T@(w*y))


def prediction(c,model):
    d=diagnostic.design(c,model['encoder'])@np.array(model['coefficients']);b=c['base']
    spr=c['case']['stack']/c['case']['pot']
    bounds=np.where(d>0,(1+spr-b)/np.maximum(d,1e-100),(b+spr)/np.maximum(-d,1e-100))
    d*=max(0,min(1,float(bounds.min())))
    v=b+d
    assert abs((v*c['mass']).sum()-1)<1e-8
    assert v.min()>=-spr-1e-8 and v.max()<=1+spr+1e-8
    return v


def score(p,model):
    delta=p['base_delta'].copy();leaves=[]
    for c in p['contexts']:
        pred=prediction(c,model);w=c['mass']*c['qualified'];w/=w.sum()
        case=c['case'];term=p['terms'][case['node']];sign=1 if term['action']==2 else -1
        delta+=sign*term['coefficient']*case['pot']*(pred[0]-c['base'][0])
        leaves.append(dict(case=case['id'],qualified_mass=float((c['mass']*c['qualified']).sum()/2),
            candidate={key:float((w*abs(pred-c[key])).sum()) for key in ['direct','corrected']},
            baseline={key:float((w*abs(c['base']-c[key])).sum()) for key in ['direct','corrected']}))
    w=p['mass']*p['qualified'];w/=w.sum()
    return dict(action_mae_bb={key:float(w@abs(delta-truth)) for key,truth in p['reference_delta'].items()},
        baseline_action_mae_bb={key:float(w@abs(p['base_delta']-truth)) for key,truth in p['reference_delta'].items()},
        qualified_mass=float(p['mass']@p['qualified']),qualified_classes=int(p['qualified'].sum()),leaves=leaves)


def screen():
    assert not (OUT/'training-screen.json').exists(),'Preserve the completed screen'
    fs,inputs=families();rows=[]
    for encoder in ['compact18','range54']:
        for penalty in [.001,.01,.1,1.]:
            for weight in [0.,4.,100.]:
                fits={held:fit([p for name,p in fs if name!=held],encoder,penalty,weight) for held,_ in fs}
                for shrink in [.25,.5,1.]:
                    folds=[dict(family=name,**score(p,dict(encoder=encoder,coefficients=shrink*fits[name]))) for name,p in fs]
                    mean=float(np.mean([r['action_mae_bb']['corrected'] for r in folds]));base=float(np.mean([r['baseline_action_mae_bb']['corrected'] for r in folds]))
                    worst=max(r['action_mae_bb']['corrected']/r['baseline_action_mae_bb']['corrected'] for r in folds)
                    leaf_ok=all(np.mean([c['candidate'][key] for c in r['leaves']])<=1.05*np.mean([c['baseline'][key] for c in r['leaves']]) for r in folds for key in ['direct','corrected'])
                    rows.append(dict(encoder=encoder,penalty=penalty,action_weight=weight,shrink=shrink,folds=folds,
                        mean_action_mae_bb=mean,baseline_mean_action_mae_bb=base,improvement=1-mean/base,
                        worst_family_ratio=float(worst),leaf_guard_passed=bool(leaf_ok),eligible=bool(mean<=.95*base and worst<=1.05 and leaf_ok)))
                print('Screened',encoder,penalty,weight,flush=True)
    eligible=[r for r in rows if r['eligible']]
    winner=min(eligible,key=lambda r:r['mean_action_mae_bb']) if eligible else None
    study.write(OUT/'training-screen.json',dict(completed_at=study.now(),families=[n for n,_ in fs],inputs=inputs,
        choices=len(rows),scores=rows,selected=winner,production_enabled=False))
    if winner:
        coef=winner['shrink']*fit([p for _,p in fs],winner['encoder'],winner['penalty'],winner['action_weight'])
        model=dict(encoder=winner['encoder'],coefficients=coef.tolist(),penalty=winner['penalty'],action_weight=winner['action_weight'],
                   shrink=winner['shrink'],frozen_at=study.now(),screen_sha256=study.pilot.sha(OUT/'training-screen.json'),production_enabled=False)
        study.write(OUT/'candidate.json',model)
        study.write(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.now()))
    print('Winner:',None if winner is None else {k:v for k,v in winner.items() if k!='folds'},flush=True)


if __name__=='__main__':screen()
