"""Training-only rank-event control-variate diagnostic; frozen labels untouched."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import collections
import numpy as np
import continuation_label_precision as precision

study=precision.study
OUT=study.ROOT/'research/preflop-evolution/continuation/rank-controls-20260916'


def choose2(x):return x*(x-1)/2
def choose3(x):return x*(x-1)*(x-2)/6


def expected_concrete(ranks,hi,lo):
    """Remaining rank counts, after both concrete private hands are removed."""
    ranks=np.asarray(ranks,dtype=float);n=ranks.sum();den=choose3(n)
    def events(k):return [1-choose3(n-k)/den,(choose2(k)*(n-k)+choose3(k))/den]
    high=events(ranks[hi]);low=events(ranks[lo]) if hi!=lo else [0.,0.]
    over=events(ranks[hi+1:].sum())
    distinct=(n**3-3*n*(ranks*ranks).sum()+2*(ranks**3).sum())/6
    return np.array(high+low+over+[1-distinct/den,choose3(ranks).sum()/den])


def board_features(board,hi,lo):
    ranks=np.asarray(board);a=int((ranks==hi).sum());b=int((ranks==lo).sum());over=int((ranks>hi).sum())
    unique=len(set(map(int,ranks)))
    return np.array([a>=1,a>=2,b>=1 and hi!=lo,b>=2 and hi!=lo,over>=1,over>=2,unique<3,unique==1],dtype=float)


def moments():
    result=np.empty((169,169,8))
    for h,(hi,lo,_) in enumerate(study.pilot.PARTS):
        for k,(a,b,_) in enumerate(study.pilot.PARTS):
            ranks=np.full(13,4.)
            for r in [hi,lo,a,b]:ranks[r]-=1
            result[h,k]=expected_concrete(ranks,hi,lo)
    return result


def context(c,pair_moments,counts):
    num,den,strata=precision.arrays(c)
    features=np.array([[board_features([study.pilot.RANKS.index(row['job']['board'][i]) for i in [0,2,4]],hi,lo)
        for hi,lo,_ in study.pilot.PARTS] for row in c['rows']])
    means=[]
    for p in range(2):
        compatible=counts*np.array(c['case']['weights'][1-p])[None,:]
        means.append(np.einsum('hk,hkf->hf',compatible,pair_moments)/compatible.sum(axis=1)[:,None])
    return dict(c=c,num=num,den=den,strata=strata,features=features,means=np.array(means))


def group(h):
    hi,lo,suited=study.pilot.PARTS[h]
    return 0 if hi==lo else 1 if suited else 2


def fit(contexts):
    cov=np.zeros((2,3,8,8));rhs=np.zeros((2,3,8))
    for item in contexts:
        c=item['c'];den=item['den'];num=item['num'];feature=item['features']
        total=den.sum(axis=0)
        for p in range(2):
            for h in range(169):
                if total[p,h]<=0 or c['mass'][p,h]<=0:continue
                w=den[:,p,h]/total[p,h]
                x=feature[:,h];x=x-(x*w[:,None]).sum(axis=0)
                y=np.divide(num[:,p,h],den[:,p,h],out=np.zeros(len(w)),where=den[:,p,h]>0)
                y-=num[:,p,h].sum()/total[p,h]
                w*=c['mass'][p,h]/(2*len(contexts))
                g=group(h);cov[p,g]+=x.T@(w[:,None]*x);rhs[p,g]+=x.T@(w*y)
    slopes=np.zeros((2,3,8))
    for p in range(2):
        for g in range(3):
            penalty=.01*np.trace(cov[p,g])/8
            if penalty>0:slopes[p,g]=np.linalg.solve(cov[p,g]+penalty*np.eye(8),rhs[p,g])
    return slopes


def compare(item,slopes,boards):
    c=item['c'];num=item['num'];den=item['den']
    beta=np.array([[slopes[p,group(h)] for h in range(169)] for p in range(2)])
    control=((item['features'][:,None,:,:]-item['means'][None,:,:,:])*beta[None,:,:,:]).sum(axis=-1)
    adjusted=num-den*control
    rng=np.random.default_rng(20260916+boards);draws=np.zeros((200,len(c['rows'])))
    for b in range(200):
        for ids in item['strata'].values():draws[b,rng.choice(ids,boards//5,replace=False)]=1
    sample_den=np.einsum('bi,iph->bph',draws,den)
    w=(sample_den>0)*c['mass'];w/=w.sum(axis=(1,2),keepdims=True)
    totals=den.sum(axis=0);estimates={};targets={}
    for key,values in [('ordinary',num),('rank_control',adjusted)]:
        targets[key]=np.divide(values.sum(axis=0),totals,out=np.zeros_like(totals),where=totals>0)
        sample_num=np.einsum('bi,iph->bph',draws,values)
        labels=np.divide(sample_num,sample_den,out=np.zeros_like(sample_num),where=sample_den>0)
        deviations=(abs(labels-targets[key])*w).sum(axis=(1,2))*100
        estimates[key]=dict(mean=float(deviations.mean()),central_90=np.quantile(deviations,[.05,.95]).tolist())
    return dict(boards=boards,deviation_pct_pot=estimates,
        improvement=1-estimates['rank_control']['mean']/estimates['ordinary']['mean'],
        full_label_shift_mae_pct_pot=float((abs(targets['rank_control']-targets['ordinary'])*c['mass']).sum()*50),
        full_pot_sum_pct={k:float(((c['raw']+v)*c['mass']).sum()*100) for k,v in targets.items()},
        largest_missing_mass_fraction=float(((sample_den==0)*c['mass']).sum(axis=(1,2)).max()/2))


def main():
    sources=['tools/research/continuation_rank_controls.py','tools/research/continuation_label_precision.py',
        'research/preflop-evolution/continuation/rank-controls-20260916/README.md']
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={p:study.pilot.sha(study.ROOT/p) for p in sources},production_enabled=False))
    cases=study.fit.load_cases('train')+study.contexts('development')
    assert len(cases)==26 and all(c['case']['partition']=='train' for c in cases)
    counts,_=study.pilot.matrices();pair_moments=moments()
    items=[context(c,pair_moments,counts) for c in cases];rows=[];coefficients=[]
    families=sorted({c['case']['family'] for c in cases})
    for family in families:
        slopes=fit([item for item in items if item['c']['case']['family']!=family])
        coefficients.append(dict(excluded_family=family,slopes=slopes.tolist()))
        for item in items:
            c=item['c']
            if c['case']['family']==family:
                rows.append(dict(case=c['case']['id'],family=family,subsamples=[compare(item,slopes,n) for n in [20,50]]))
    summaries=[]
    for family in families:
        for n in [20,50]:
            selected=[next(s for s in r['subsamples'] if s['boards']==n) for r in rows if r['family']==family]
            means={k:float(np.mean([s['deviation_pct_pot'][k]['mean'] for s in selected])) for k in ['ordinary','rank_control']}
            summaries.append(dict(family=family,boards=n,mean_deviation_pct_pot=means,improvement=1-means['rank_control']/means['ordinary']))
    passed=all(s['improvement']>=.2 for s in summaries)
    study.freeze(OUT/'diagnostic.json',dict(cases=rows,summaries=summaries,coefficients=coefficients,promising=passed,
        production_enabled=False,caveat='Historical finite-population subset dispersion, not new-board accuracy. No reference label or model is replaced.'))
    print(summaries);print('Promising:',passed)


if __name__=='__main__':main()
