"""Chance-only sampling diagnostics; no solver policy or action-value input."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import collections
import hashlib
import json
import math
import numpy as np
import integrated_coverage as c

OUT=c.OUT
def write(p,d):p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n',encoding='utf8')
def read(p):return json.loads(p.read_text())
def run():
    paths=[c.s.ROOT/'tools/research/integrated_panel_sampling.py',OUT/'SAMPLING-PROTOCOL.md',
        c.s.OUT/'fixtures.json',c.s.OUT.parent/'conditional-hu-20260919/subtree.json']
    freeze=OUT/'sampling-freeze.json'
    assert not freeze.exists(),'Preserve the registered diagnostic.'
    write(freeze,{'inputs':{p.relative_to(c.s.ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}})
    d=read(paths[-1]);weights=np.array(d['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES]
    weights/=weights.max(1)[:,None];weights[weights<1e-5]=0
    indices=[np.flatnonzero(w) for w in weights]
    masks=[c.MASKS[i] for i in indices];classes=[c.CLASSES[i] for i in indices]
    unique=[np.unique(x) for x in classes];n0,n1=map(len,unique)
    cls=[np.searchsorted(u,cs) for u,cs in zip(unique,classes)]
    class_pair=(cls[0][:,None]*n1+cls[1][None,:]).ravel()
    pairs=weights[0,indices[0]][:,None]*weights[1,indices[1]][None,:]*((masks[0][:,None]&masks[1][None,:])==0)
    aggregate=lambda p:np.bincount(class_pair,weights=p.ravel(),minlength=n0*n1).reshape(n0,n1)
    full=aggregate(pairs);mass=full.sum();full/=mass
    boards=read(c.s.OUT/'fixtures.json')['canonical_flops'];table=[];strata=[collections.defaultdict(list) for _ in range(2)]
    for i,(b,iso) in enumerate(boards):
        cards=c.cards(b);mask=np.uint64(sum(1<<x for x in cards));ranks=len({x//4 for x in cards});suits=len({x%4 for x in cards})
        legal=[(m&mask)==0 for m in masks];table.append(aggregate(pairs*legal[0][:,None]*legal[1][None,:])*iso)
        key=('paired' if ranks<3 else 'unpaired')+'/'+str(suits)
        strata[0][key].append(i);strata[1]['trips' if ranks==1 else key].append(i)
    table=np.array(table);all_mass=table.sum(0)
    normalizer_error=abs(all_mass.sum()/(mass*math.comb(48,3))-1)
    prior_error=float(abs(all_mass/all_mass.sum()-full).max())
    assert normalizer_error<1e-12 and prior_error<1e-12,(normalizer_error,prior_error)
    def error(est):
        est=est/est.sum()
        return [float(abs(est-full).sum()/2),float(abs(est.sum(1)-full.sum(1)).sum()/2),float(abs(est.sum(0)-full.sum(0)).sum()/2)]
    rows=[]
    for design,groups in enumerate(strata):
        for k in [1,2,4,8,16,32]:
            rng=np.random.default_rng(9026191940+1000*design+k);errors=[]
            for _ in range(1000):
                est=np.zeros_like(full)
                for members in groups.values():
                    n=min(k,len(members));selection=rng.choice(members,n,replace=False)
                    est+=table[selection].sum(0)*len(members)/n
                errors.append(error(est))
            rows.append(dict(strata=len(groups),per_stratum=k,boards=sum(min(k,len(m)) for m in groups.values()),
                tv_quantiles_05_50_95=np.quantile(errors,[.05,.5,.95],axis=0).tolist()))
    actual={};lookup={b:i for i,(b,_) in enumerate(boards)}
    for name in ['panel-a','panel-b','panel-ab']:
        manifest=read(OUT/(name+'.json'));est=np.zeros_like(full)
        for b in manifest['boards']:
            idx=lookup[b['board']];est+=table[idx]*b['weight']/boards[idx][1]
        actual[name]=error(est)
    result=dict(normalizer_relative_error=normalizer_error,full_class_prior_max_error=prior_error,
        classes=[u.tolist() for u in unique],strata_sizes=[{k:len(v) for k,v in g.items()} for g in strata],
        metric_order=['joint_hand_class_tv','UTG_class_tv','LJ_class_tv'],repeats=1000,designs=rows,actual_panels=actual,
        note='Chance-only class prior distortion. Not strategy error, not suit-combo joint TV, and not held-out poker accuracy.')
    write(OUT/'sampling-audit.json',result);print(json.dumps(result,indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4))
    for design,color in [(5,'#bd714e'),(6,'#386b58')]:
        selected=[r for r in rows if r['strata']==design];x=[r['boards'] for r in selected]
        q=np.array([r['tv_quantiles_05_50_95'] for r in selected])*100
        ax.plot(x,q[:,1,0],marker='o',label=f'{design} strata',color=color)
        ax.fill_between(x,q[:,0,0],q[:,2,0],alpha=.12,color=color)
    ax.set(xscale='log',xlabel='Canonical flops in a sample',ylabel='Joint hand-class prior distance (TV %)',title='Board-sampling distortion before considering action values')
    ax.grid(alpha=.2);ax.legend();fig.text(.12,.01,'Lines: median. Bands: 5th–95th percentiles across 1,000 samples; not strategy error.',fontsize=8)
    fig.tight_layout(rect=(0,.045,1,1));fig.savefig(OUT/'sampling.png',dpi=160);plt.close(fig)

if __name__=='__main__':run()
