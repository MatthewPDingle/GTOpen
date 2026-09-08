"""Hand-aware response smoothing: no hand-independent action mixture.

This is retrospective evaluation on previously inspected chronological data.
Select parameters on earlier tuning sessions; report subgroup diagnostics as
well as overall loss. Published opening/position policies are never changed.
"""
import collections,importlib.util,json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import softmax
spec=importlib.util.spec_from_file_location('limps',Path(__file__).with_name('limps.py'))
limps=importlib.util.module_from_spec(spec);spec.loader.exec_module(limps)
resp=limps.resp
BUCKETS=['limps_free','limps_complete','limps_field','raise','squeeze','reraise','cold_reraise',*resp.BANDS]
HI=np.maximum(np.arange(169)//13,np.arange(169)%13)
LO=np.minimum(np.arange(169)//13,np.arange(169)%13)
TYPE=np.where(HI==LO,0,np.where(np.arange(169)//13>np.arange(169)%13,1,2))
PREMIUM=(HI==12)&((LO==12)|(LO==11))|((HI==LO)&(HI>=10))
GROUPS={'premiums':PREMIUM,'other_pairs':(TYPE==0)&~PREMIUM,'other_suited':(TYPE==1)&~PREMIUM,'other_offsuit':(TYPE==2)&~PREMIUM}

def collect(sessions,bucket):
    if bucket.startswith('limps_'):return [limps.arrays([s],bucket[6:]) for s in sessions]
    return [resp.opening.arrays([s]) for s in resp.subset(sessions,bucket)]

def merge(rows):
    cs=collections.defaultdict(lambda:np.zeros((169,3)))
    for row in rows:
        for k,c in row.items():cs[k]+=c
    return dict(cs)

def kernel(width):
    # Same hand family; adjacent ranks borrow most. Pairs never borrow the
    # population fold rate of unrelated offsuit trash. Own-hand observations
    # are handled separately in the next hierarchy level.
    distance=(HI[:,None]-HI)**2+(LO[:,None]-LO)**2
    k=np.exp(-distance/(2*width**2))*(TYPE[:,None]==TYPE)
    np.fill_diagonal(k,0)
    return k

def related_prior(total,aux,width):
    base=sum(aux.values(),np.zeros((169,3)))
    nearby=kernel(width)@base+.001
    nearby/=nearby.sum(1)[:,None]
    base=(base+2*nearby)/(base.sum(1)[:,None]+2)
    logits=np.log(np.maximum(base,1e-15))
    def objective(v):
        offset=np.column_stack([np.zeros(3),v.reshape(3,2)])[TYPE]
        p=softmax(logits+offset,axis=1)
        err=p*total.sum(1)[:,None]-total
        grad=np.stack([err[TYPE==g,1:].sum(0) for g in range(3)])+2*v.reshape(3,2)
        return -float((total*np.log(np.maximum(p,1e-15))).sum())+float(np.square(v).sum()),grad.ravel()
    opt=minimize(objective,np.zeros(6),jac=True,method='L-BFGS-B')
    if not opt.success:raise RuntimeError(opt.message)
    return softmax(logits+np.column_stack([np.zeros(3),opt.x.reshape(3,2)])[TYPE],axis=1)

def fit(cs,alpha,beta,width,free=False,aux=None,transfer=0):
    total=sum(cs.values(),np.zeros((169,3)))
    neighbor=kernel(width)@total
    # A tiny numerical prior prevents exact empirical zeroes; unlike the old
    # population mixture it is not a common percentage floor for every hand.
    tiny=np.array([0 if free else .001,.001,.001])
    neighbor+=tiny;neighbor/=neighbor.sum(1)[:,None]
    if aux is not None and transfer:
        neighbor=(1-transfer)*neighbor+transfer*related_prior(total,aux,width)
    hand=(total+beta*neighbor)/(total.sum(1)[:,None]+beta)
    if len(next(iter(cs)))==3:
        parent=collections.defaultdict(lambda:np.zeros((169,3)))
        for k,c in cs.items():parent[k[:2]]+=c
        parent={k:(c+30*hand)/(c.sum(1)[:,None]+30) for k,c in parent.items()}
        out={k:(c+alpha*parent[k[:2]])/(c.sum(1)[:,None]+alpha) for k,c in cs.items()}
    else:out={k:(c+alpha*hand)/(c.sum(1)[:,None]+alpha) for k,c in cs.items()}
    if free:
        for p in out.values():p[:,0]=0;p/=p.sum(1)[:,None]
    return out

def closest(model,key):
    return limps.closest(model,*key) if len(key)==3 else resp.opening.closest(model,*key)

def score(rows,model,mask=None):
    out=[]
    for row in rows:
        loss=den=predfold=obsfold=0.
        for k,c in row.items():
            p=model[closest(model,k)]
            if mask is not None:c=c[mask];p=p[mask]
            loss-=float((c*np.log(np.maximum(p,1e-15))).sum());den+=c.sum()
            predfold+=float((c.sum(1)*p[:,0]).sum());obsfold+=float(c[:,0].sum())
        if den:out.append((loss,float(den),predfold,obsfold))
    return out

def loss(rows):return sum(x[0] for x in rows)/sum(x[1] for x in rows)

def ci(new,old):
    assert len(new)==len(old)
    rows=np.array([[b[0]-a[0],a[1]] for a,b in zip(new,old)]);rng=np.random.default_rng(20260909);out=[]
    for _ in range(1000):
        x=rows[rng.integers(0,len(rows),len(rows))];out.append(x[:,0].sum()/x[:,1].sum())
    return np.quantile(out,[.025,.975]).tolist()

def old_fit(sessions,report,bucket):
    if bucket.startswith('limps_'):
        kind=bucket[6:];e=report['limp_validation']['groups'][kind];b=e['selected'];cs=limps.arrays(sessions,kind)
        learned=limps.train(cs,kind,b['alpha'],b['beta'],b['gamma']);ref=limps.benchmark(cs,kind,e['reference_selected']['mix'])
        return {k:b['blend']*p+(1-b['blend'])*ref[k] for k,p in learned.items()}
    e=report['response_validation'][bucket]
    return resp.opening.train(resp.subset(sessions,bucket),e['selected']['alpha'],e['selected']['beta'])[0]

def evaluate(sessions,report,bucket):
    s=report['splits'];tr=[x for x in sessions if x['last']<s['tune_from']];tu=[x for x in sessions if x['first']>=s['tune_from'] and x['last']<s['test_from']];te=[x for x in sessions if x['first']>=s['test_from']]
    train=merge(collect(tr,bucket));tune=collect(tu,bucket);test=collect(te,bucket);free=bucket=='limps_free'
    candidates=[];aux_train=merge(collect(tr,'raise')) if bucket=='squeeze' else None
    for alpha in [3,10,30,100,300]:
        for beta in [.5,2,10,30,100]:
            for width in [.5,1.,2.]:
                for transfer in ([0,.5,1.] if aux_train else [0]):
                    model=fit(train,alpha,beta,width,free,aux_train,transfer)
                    overall=loss(score(tune,model));group=[loss(x) for mask in GROUPS.values() if (x:=score(tune,model,mask))]
                    candidates.append(dict(alpha=alpha,beta=beta,width=width,transfer=transfer,loss=overall,selection_score=.75*overall+.25*np.mean(group)))
    best=min(candidates,key=lambda c:c['selection_score'])
    def fitted(ss):return fit(merge(collect(ss,bucket)),best['alpha'],best['beta'],best['width'],free,merge(collect(ss,'raise')) if aux_train else None,best['transfer'])
    model=fitted(tr+tu);old=old_fit(tr+tu,report,bucket)
    newrows=score(test,model);oldrows=score(test,old);groups={}
    for name,mask in GROUPS.items():
        a=score(test,model,mask);b=score(test,old,mask)
        if a:groups[name]=dict(decisions=int(sum(x[1] for x in a)),old_loss=loss(b),new_loss=loss(a),gain_ci=ci(a,b),predicted_fold=sum(x[2] for x in a)/sum(x[1] for x in a),observed_fold=sum(x[3] for x in a)/sum(x[1] for x in a))
    interval=ci(newrows,oldrows)
    # Do not publish a candidate with statistically clear subgroup harm.
    passed=loss(newrows)<loss(oldrows) and all(v['gain_ci'][1]>=0 for v in groups.values() if v['decisions']>=30)
    evidence=dict(selected=best,candidates=candidates,decisions=int(sum(x[1] for x in newrows)),sessions=len(newrows),old_loss=loss(oldrows),new_loss=loss(newrows),gain_ci=interval,groups=groups,published=passed)
    print(bucket,json.dumps({k:evidence[k] for k in ['old_loss','new_loss','gain_ci','published','selected']}),flush=True)
    for name,g in groups.items():print(' ',name,g,flush=True)
    final=fitted(sessions)
    return final,evidence

def publish(report,models,evidence,out,sessions):
    data=report['model']['stats']['dataset'];pool=data['response_policies'];lookup={}
    def index(bucket,key):
        near=closest(models[bucket],key);cache=(bucket,near)
        if cache not in lookup:
            p=models[bucket][near];call=np.round(p[:,1],6);raised=np.minimum(np.round(p[:,2],6),1-call)
            if bucket=='limps_free':call=1-raised
            lookup[cache]=len(pool);pool.append(dict(call=call.tolist(),raise_=raised.tolist(),jam=[0.]*169,raise_size=report['model']['stats']['raise_size']))
            pool[-1]['raise']=pool[-1].pop('raise_')
        return lookup[cache]
    for row in data['rows']:
        n,r=row['players'],row['role']
        for b,e in evidence.items():
            if e['published'] and not b.startswith('limps_'):row['responses'][b]=index(b,(n,r))
        for free in [False,True]:
            b='limps_free' if free else 'limps_complete' if r==-1 else 'limps_field'
            if evidence[b]['published']:
                for count in [1,2,3]:row['responses'][f'limps_{"free" if free else "paid"}_{count}']=index(b,(n,r,count))
        row['responses']['limps']=row['responses'][f'limps_{"free" if r==-2 else "paid"}_1']
    used=sorted({i for r in data['rows'] for i in r['responses'].values()});remap={old:new for new,old in enumerate(used)}
    data['response_policies']=[pool[i] for i in used]
    for row in data['rows']:row['responses']={k:remap[i] for k,i in row['responses'].items()}
    for b,e in evidence.items():
        if b.startswith('limps_'):continue
        data['response_notes'][b]=('Hand-aware smoothing of known-card observations; same hands and nearby ranks within pairs/suited/offsuit families.' if e['published'] else 'Existing learned policy retained: the alternative smoothing did not improve overall validation.')
        if b=='squeeze' and e['published'] and e['selected']['transfer']:
            data['response_notes'][b]+=' Also borrows the same hands from cold raise responses, adjusted to squeeze tendencies.'
    if all(evidence[b]['published'] for b in ['limps_free','limps_complete','limps_field']):
        data['response_notes']['limps']='Hand-aware smoothing: free checks, SB completions and other paid entries remain separate, with 1 / 2 / 3+ limpers. No hand-independent fold mixture; sparse hands borrow same-hand and neighboring-rank observations.'
    model=report['model'];model['source']['version']='2026-09-08-v5'
    model['source']['hand_composition']='known-card preflop probabilities with hand-aware response smoothing'
    model['note']=model['note'].split(' Response smoothing:')[0]+' Response smoothing: same and similar hands replace population-wide action priors where validation supports the change; see per-bucket notes.'
    old=old_fit(sessions,report,'limps_complete');key=closest(old,(8,-1,3));new=models['limps_complete'][closest(models['limps_complete'],(8,-1,3))]
    examples=[dict(hand=name,old_fold=float(old[key][h,0]),new_fold=float(new[h,0])) for name,h in [('AA',168),('KK',154),('QQ',140),('AKs',167),('AKo',155)]]
    report['smoothing_validation']=dict(retrospective=True,baseline='v4 pre-smoothing response models',selection='75% overall tuning log loss + 25% mean hand-group tuning log loss',
        publication_rule='Lower retrospective mean loss and no clear 95% bootstrap subgroup harm among groups with at least 30 decisions. This is not proof of noninferiority.',
        development='Neighbor-only initial family, expanded smoothing strengths, then same-hand cold-raise transfer for squeeze were explored after inspecting historical evaluation results. No fresh untouched test remains.',
        buckets=evidence,sb_three_plus_example=examples)
    for name,value in [('NL10.json',report),('models.json',[model])]:
        (Path(out)/name).write_text(json.dumps(value,indent=1,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')

def run(source,out,do_publish=False):
    d=json.loads(Path(source).read_text(encoding='utf-8'));report=json.loads((Path(out)/'NL10.json').read_text(encoding='utf-8'));assert d['audit']==report['audit']
    models={};evidence={}
    for bucket in BUCKETS:models[bucket],evidence[bucket]=evaluate(d['sessions'],report,bucket)
    Path('output/smoothing-evidence.json').write_text(json.dumps(evidence,indent=1,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    packed={b:[dict(key=list(k),probabilities=p.tolist()) for k,p in m.items()] for b,m in models.items()}
    Path('output/smoothing-policies.json').write_text(json.dumps(packed,allow_nan=False),encoding='utf-8')
    if do_publish:publish(report,models,evidence,out,d['sessions'])

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--publish',action='store_true');a=p.parse_args();run(a.input,a.out,a.publish)
