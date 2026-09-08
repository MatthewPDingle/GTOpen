"""Conservative opening-position transport, tested by hiding larger tables.

Candidate family is fixed before evaluation. Historical late sessions have
already been inspected in earlier work: these are retrospective checks.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import softmax
spec=importlib.util.spec_from_file_location('opening',Path(__file__).with_name('fit.py'))
opening=importlib.util.module_from_spec(spec);spec.loader.exec_module(opening)
GROUP=np.array([0 if h//13==h%13 else 1 if h//13>h%13 else 2 for h in range(169)])
FOLDS=[(4,5,2),(4,6,3),(5,6,3)]

def subset(sessions,max_players):
    return [dict(s,cells={k:v for k,v in s['cells'].items() if int(k.split('/')[0])<=max_players}) for s in sessions]

def trend(sessions,penalty):
    counts=opening.arrays(sessions);keys=[k for k in counts if k[1]>=0]
    counts=np.stack([counts[k] for k in keys]);n=np.array([k[0]-3 for k in keys]);r=np.array([k[1] for k in keys])
    pooled=counts.sum(0)+.5;initial=np.log(pooled[:,1:]/pooled[:,:1])
    # Per-hand intercept, a shared positional slope, three shrunk hand-type
    # deviations, and observed table-size nuisance effects. Only position is
    # transported: unseen occupancy effects are never extended beyond data.
    def unpack(v):return v[:338].reshape(169,2),v[338:340],v[340:346].reshape(3,2),v[346:].reshape(4,2)
    def objective(v):
        hand,shared,dev,occ=unpack(v)
        logits=hand[None,:,:]+r[:,None,None]*(shared+dev[GROUP])[None,:,:]+occ[n,None,:]
        full=np.concatenate([np.zeros((*logits.shape[:2],1)),logits],2);p=softmax(full,axis=2)
        loss=-np.sum(counts*np.log(np.maximum(p,1e-15)))
        err=(p*counts.sum(2)[:,:,None]-counts)[:,:,1:]
        dh=err.sum(0)+.5*(hand-initial);ds=(err*r[:,None,None]).sum((0,1))+2*shared
        dd=np.stack([(err[:,GROUP==g,:]*r[:,None,None]).sum((0,1)) for g in range(3)])+penalty*dev
        dn=np.stack([err[n==g].sum((0,1)) for g in range(4)])+50*occ
        loss+=.25*np.square(hand-initial).sum()+np.square(shared).sum()+penalty/2*np.square(dev).sum()+25*np.square(occ).sum()
        return loss,np.concatenate([dh.ravel(),ds,dd.ravel(),dn.ravel()])
    v=np.concatenate([initial.ravel(),np.zeros(16)])
    result=minimize(objective,v,jac=True,method='L-BFGS-B',options=dict(maxiter=1000,ftol=1e-10,gtol=1e-5))
    if not result.success:raise RuntimeError(result.message)
    hand,shared,dev,occ=unpack(result.x)
    # Conservative structural assumption: extra players do not increase
    # entry-versus-fold odds. Cap each action's adjustment per added seat.
    return np.clip(shared+dev,-.75,0)

def transport(p,slopes,distance,blend):
    odds=np.log(np.maximum(p[:,1:],1e-12)/np.maximum(p[:,:1],1e-12))
    odds+=slopes[GROUP]*min(distance,2)*blend
    return softmax(np.column_stack([np.zeros(169),odds]),axis=1)

def losses(sessions,target,model,slopes,blend):
    n,r=target;key=opening.closest(model[0],n,r);p=model[0][key]
    q=transport(p,slopes,r-key[1],blend);result=[]
    for s in sessions:
        c=opening.arrays([s]).get((n,r))
        if c is not None and c.sum():result.append((s['id'],float(-(c*np.log(p)).sum()),float(-(c*np.log(q)).sum()),float(c.sum())))
    return result

def loss(rows,column):return sum(x[column] for x in rows)/sum(x[3] for x in rows)

def interval(rows):
    rng=np.random.default_rng(20260909);samples=np.array([[a-b,n] for _,a,b,n in rows]);out=[]
    for _ in range(2000):
        x=samples[rng.integers(0,len(samples),len(samples))];out.append(x[:,0].sum()/x[:,1].sum())
    return np.quantile(out,[.025,.975]).tolist()

def run(source,out,publish=False):
    out=Path(out);d=json.loads(Path(source).read_text(encoding='utf-8'));report=json.loads((out/'NL10.json').read_text(encoding='utf-8'))
    assert report['audit']==d['audit']
    ss=d['sessions'];cuts=report['splits'];params=report['validation']['selected']
    tr=[s for s in ss if s['last']<cuts['tune_from']]
    tune=[s for s in ss if s['first']>=cuts['tune_from'] and s['last']<cuts['test_from']]
    test=[s for s in ss if s['first']>=cuts['test_from']]
    candidates=[]
    for penalty in [10,100,1000]:
        fits={m:(opening.train(subset(tr,m),params['alpha'],params['beta']),trend(subset(tr,m),penalty)) for m in [4,5]}
        for blend in [.25,.5,1.]:
            rows=[x for m,n,r in FOLDS for x in losses(tune,(n,r),*fits[m],blend)]
            candidates.append(dict(penalty=penalty,blend=blend,loss=loss(rows,2)))
    best=min(candidates,key=lambda x:x['loss']);print('Selected',best,flush=True)
    fits={m:(opening.train(subset(tr+tune,m),params['alpha'],params['beta']),trend(subset(tr+tune,m),best['penalty'])) for m in [4,5]}
    evaluations=[]
    for m,n,r in FOLDS:
        rows=losses(test,(n,r),*fits[m],best['blend']);ci=interval(rows)
        e=dict(source_max_players=m,target_players=n,target_role=r,extra_positions=n-m,opportunities=int(sum(x[3] for x in rows)),sessions=len(rows),nearest_loss=loss(rows,1),adjusted_loss=loss(rows,2),gain_ci=ci)
        evaluations.append(e);print(e,flush=True)
    passed=all(e['gain_ci'][0]>0 and e['sessions']>=30 for e in evaluations)
    result=dict(retrospective=True,candidates=candidates,selected=best,evaluations=evaluations,published=passed,
        assumption='Nonpositive entry-versus-fold log-odds slopes capped at 0.75 per added position. Maximum two positions of adjustment; no extrapolated occupancy effect.')
    if passed:
        slopes=trend(ss,best['penalty']);result['slopes']=slopes.tolist();print('Slopes',slopes.tolist(),flush=True)
        data=report['model']['stats']['dataset'];base=opening.train(ss,params['alpha'],params['beta'])
        updated=[]
        for row in data['rows']:
            n,r=row['players'],row['role'];key=opening.closest(base[0],n,r)
            if r==-2:
                row['opening_note']='No first-in BB decision after folds; the unraised free-check action remains legal.'
                continue
            if r>key[1]:
                p=transport(base[0][key],slopes,r-key[1],best['blend'])
                row['opening']['call']=p[:,1].tolist();row['opening']['raise']=p[:,2].tolist()
                avg=(p*opening.COMBOS[:,None]).sum(0)/1326;row['open_raise']=float(avg[2]*100);row['open_limp']=float(avg[1]*100)
                row['opening_note']=f"Position-adjusted estimate: {min(r-key[1],2)} extra player{'' if r-key[1]==1 else 's'} to act relative to the measured {key[0]}-player early position."+(' Adjustment capped at two positions; farther transfer is unvalidated.' if r-key[1]>2 else ' Extrapolation, not directly observed hands at this position.')
                updated.append(dict(players=n,role=r,raise_pct=row['open_raise'],limp_pct=row['open_limp']))
            elif (n,r) in base[0]:row['opening_note']='Measured position: known-card opening probabilities, with smoothing.'
            else:row['opening_note']=f'Borrowed table size: measured {key[0]}-player position with the same number of players left to act; target occupancy unvalidated.'
        result['updated_rows']=updated
        # Existing servers preserve this extensible metadata dictionary, so
        # publishing ranges and their provenance does not require a restart.
        for row in data['rows']:
            note=row.pop('opening_note',None)
            if note:data['response_notes'][f"open_{row['players']}_{row['role']}"]=note
        model=report['model']
        data['scope']=data['scope'].replace('Unsupported contexts borrow nearby observed positions.',
            'Unsupported early opening positions use a conservative positional adjustment; other unsupported contexts borrow observed neighbors.')
        model['source']['version']='2026-09-08-v4'
        model['source']['assumptions']=[s for s in model['source']['assumptions'] if not s.startswith('Opening extrapolation:')]
        model['source']['assumptions'].append('Opening extrapolation: measured hand probabilities adjusted by learned positional log-odds, up to two extra early positions; retrospective validation only.')
        model['note']=model['note'].split(' Early opening positions')[0]+' Early opening positions beyond six-handed coverage are position-adjusted estimates, not direct observations.'
    report['position_validation']=result
    # Exploration emits evidence only. Publishing is explicit after review.
    Path('output/position-candidate.json').write_text(json.dumps(report,indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    if publish:
        if not passed:raise ValueError('Hidden-position validation failed; model unchanged')
        for name,value in [('NL10.json',report),('models.json',[report['model']])]:
            (out/name).write_text(json.dumps(value,indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print('Publish eligible:',passed,flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--publish',action='store_true');a=p.parse_args();run(a.input,a.out,a.publish)
