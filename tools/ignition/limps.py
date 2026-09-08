"""Role/legal-action/limper-count refinement; retrospective chronological evaluation.

The late period has already been inspected in responses.py, so it is NOT a
fresh untouched test. Fix this candidate family before scoring that period;
select smoothing on the earlier tuning sessions. Publish by decision type.
"""
import collections, importlib.util, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('responses',Path(__file__).with_name('responses.py'))
resp=importlib.util.module_from_spec(spec);spec.loader.exec_module(resp)
ROLES=resp.opening.ROLES

def arrays(sessions,kind):
    out=collections.defaultdict(lambda:np.zeros((169,3)))
    for s in sessions:
        for k,v in s['limp_cells'].items():
            prefix,act=k.split('|');n,pos,group,count,h=prefix.split('/')
            if group==kind:out[(int(n),ROLES[pos],min(3,int(count)))][int(h),['fold','call','raise'].index(act)]+=v
    return dict(out)

def train(cs,kind,alpha,beta,gamma):
    total=sum(cs.values(),np.zeros((169,3)))
    prior=total.sum(0)+np.array([0 if kind=='free' else .5,.5,.5]);prior/=prior.sum()
    hand=(total+beta*prior)/(total.sum(1)[:,None]+beta)
    positions=collections.defaultdict(lambda:np.zeros((169,3)))
    for (n,r,l),c in cs.items():positions[(n,r)]+=c
    parent={k:(c+gamma*hand)/(c.sum(1)[:,None]+gamma) for k,c in positions.items()}
    return {k:(c+alpha*parent[k[:2]])/(c.sum(1)[:,None]+alpha) for k,c in cs.items()}

def closest(policies,n,r,l):
    return min(policies,key=lambda k:(abs(k[1]-r),abs(k[0]-n),abs(k[2]-l),-k[0]))

def benchmark(cs,kind,mix):
    # Use the existing ranked comparator, with each limper count a separate
    # pseudo-context. Enforce no fold probability in free-check situations.
    sessions=[]
    for (n,r,l),c in cs.items():
        pos=next(k for k,v in ROLES.items() if v==r)
        cells={f'{n*10+l}/{pos}/{h}|{a}':int(c[h,i]) for h in range(169) for i,a in enumerate(['fold','call','raise']) if c[h,i]}
        sessions.append(dict(cells=cells))
    policies,_,_=resp.benchmark(sessions,mix,'limps')
    out={}
    for (encoded,r),p in policies.items():
        p=p.copy()
        if kind=='free':p[:,1]+=p[:,0];p[:,0]=0
        out[(encoded//10,r,encoded%10)]=p
    return out

def score(sessions,kind,model):
    rows=[]
    for s in sessions:
        loss=den=0.
        for k,c in arrays([s],kind).items():
            p=model[closest(model,*k)];loss-=float((c*np.log(np.maximum(p,1e-12))).sum());den+=c.sum()
        if den:rows.append((loss,den))
    return rows

def evaluate(sessions,splits,kind):
    tr=[s for s in sessions if s['last']<splits['tune_from']]
    tune=[s for s in sessions if s['first']>=splits['tune_from'] and s['last']<splits['test_from']]
    test=[s for s in sessions if s['first']>=splits['test_from']]
    cs=arrays(tr,kind);val=[]
    refs=[dict(mix=m,loss=resp.opening.loss(score(tune,kind,benchmark(cs,kind,m)))) for m in [.05,.1,.2,.35,.5,.75,1.]]
    ref=min(refs,key=lambda x:x['loss']);base=benchmark(cs,kind,ref['mix'])
    for alpha in [10,30,100]:
        for beta in [5,20,100]:
            for gamma in [10,50,200]:
                fitted=train(cs,kind,alpha,beta,gamma)
                for blend in [.5,1.]:
                    model={k:blend*p+(1-blend)*base[k] for k,p in fitted.items()}
                    val.append(dict(alpha=alpha,beta=beta,gamma=gamma,blend=blend,loss=resp.opening.loss(score(tune,kind,model))))
    best=min(val,key=lambda x:x['loss'])
    def fit(ss):
        c=arrays(ss,kind);learned=train(c,kind,best['alpha'],best['beta'],best['gamma']);base=benchmark(c,kind,ref['mix'])
        return {k:best['blend']*p+(1-best['blend'])*base[k] for k,p in learned.items()},base
    model,baseline=fit(tr+tune)
    learned=score(test,kind,model);reference=score(test,kind,baseline);ci=resp.gain_ci(learned,reference)
    observed=arrays(sessions,kind)
    evidence=dict(selected=best,reference_selected=ref,candidates=val,reference_candidates=refs,
        opportunities=int(sum(c.sum() for c in observed.values())),test_opportunities=int(sum(n for l,n in learned)),test_sessions=len(learned),
        learned_log_loss=resp.opening.loss(learned),reference_log_loss=resp.opening.loss(reference),gain_ci=ci,published=ci[0]>0 and len(learned)>=30,
        contexts=[dict(players=n,role=r,limpers=l,opportunities=int(c.sum()),classes=int((c.sum(1)>0).sum())) for (n,r,l),c in sorted(observed.items())])
    return fit(sessions)[0],evidence

def run(source,out):
    d=json.loads(Path(source).read_text(encoding='utf-8'));out=Path(out)
    if d.get('schema',0)<3:raise ValueError('Rerun analysis for detailed limping contexts')
    report=json.loads((out/'NL10.json').read_text(encoding='utf-8'));assert report['audit']==d['audit']
    fitted={};validation={}
    for kind in ['free','complete','field']:
        fitted[kind],validation[kind]=evaluate(d['sessions'],report['splits'],kind)
        v=validation[kind];print(kind,{k:v[k] for k in ['opportunities','test_opportunities','learned_log_loss','reference_log_loss','gain_ci','published','selected']},flush=True)
    model=report['model'];data=model['stats']['dataset']
    # Replacing this extension is idempotent and leaves other responses exact.
    for row in data['rows']:
        row['responses']={k:v for k,v in row['responses'].items() if not k.startswith('limps')}
    used=sorted({v for row in data['rows'] for v in row['responses'].values()})
    remap={old:new for new,old in enumerate(used)}
    pool=[data['response_policies'][i] for i in used];data['response_policies']=pool;lookup={}
    for row in data['rows']:row['responses']={k:remap[v] for k,v in row['responses'].items()}
    data['scope']=data['scope'].split(' Vs limps separates')[0]
    model['note']=model['note'].split(' Vs limps includes')[0]
    def index(kind,n,r,l):
        key=closest(fitted[kind],n,r,l);cache=(kind,key)
        if cache not in lookup:
            p=fitted[kind][key];call=np.round(p[:,1],6);raised=np.minimum(np.round(p[:,2],6),1-call)
            if kind=='free':call=1-raised
            lookup[cache]=len(pool);pool.append(dict(call=call.tolist(),raise_=raised.tolist(),jam=[0.]*169,raise_size='max'));pool[-1]['raise']=pool[-1].pop('raise_')
        return lookup[cache]
    for row in data['rows']:
        kind='complete' if row['role']==-1 else 'field'
        for free in [False,True]:
            group='free' if free else kind
            if not validation[group]['published']:continue
            for l in [1,2,3]:row['responses'][f'limps_{"free" if free else "paid"}_{l}']=index(group,row['players'],row['role'],l)
        default='free' if row['role']==-2 else 'paid'
        key=f'limps_{default}_1'
        if key in row['responses']:row['responses']['limps']=row['responses'][key]
    notes=[]
    for kind,label in [('free','BB free checks'),('complete','SB completions'),('field','other positions')]:
        v=validation[kind];method=('learned/reference blend' if v['selected']['blend']<1 else 'learned') if v['published'] else 'inferred fallback'
        notes.append(f"{label}: {method} ({v['opportunities']:,} decisions)")
    data['response_notes']['limps']='; '.join(notes)+'. Select 1, 2, or 3+ limpers; sparse situations borrow related observations.'
    data['scope']+=' Vs limps separates free checks, SB completions, and paid entries; conditions on 1, 2, or 3+ limpers. Equal-blind SB free checks borrow BB observations.'
    model['source']['version']='2026-09-08-v3'
    model['note']+=' Vs limps includes separately validated legal-action and limper-count contexts. The refinement reuses the historical evaluation period; new-period validation is still needed.'
    report['limp_validation']=dict(retrospective=True,groups=validation)
    for name,value in [('NL10.json',report),('models.json',[model])]:
        (out/name).write_text(json.dumps(value,indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.input,a.out)
