"""A independently certifiable Bayesian two-player push/fold research game."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import time
import numpy as np
from scipy.optimize import linprog
import wizard_continuation_study as s

OUT=s.OUT.parent/'card-compatible-hu-20260919'


def card_pairs():
    pairs=[(a,b) for a in range(52) for b in range(a+1,52)]
    masks=np.array([(1<<a)|(1<<b) for a,b in pairs],dtype=np.uint64)
    classes=np.array([max(a//4,b//4)*13+min(a//4,b//4) if a%4==b%4 or a//4==b//4 else min(a//4,b//4)*13+max(a//4,b//4) for a,b in pairs])
    left,right=np.where((masks[:,None]&masks[None,:])==0)
    counts=np.zeros((169,169));np.add.at(counts,(classes[left],classes[right]),1)
    combos=np.bincount(classes,minlength=169)
    assert np.array_equal(counts,counts.T)
    assert np.array_equal(counts.sum(1),combos*1225)
    assert counts[168,168]==6 and counts[168,154]==36
    assert counts[168,167]==12 and counts[167,167]==12
    return counts,combos,classes[left],classes[right]


def game(weights,counts,eq,pot,hero_add,opp_add):
    chance=counts*weights[0][:,None]*weights[1][None,:]
    assert chance.sum()>0;chance/=chance.sum()
    called=(pot+hero_add+opp_add)*eq-hero_add
    return chance,pot*chance.sum(1),chance*(called-pot),called


def gap_value(a,b,x,y):
    hi=np.maximum(a+b@y,0).sum()
    lo=a@x+np.minimum(b.T@x,0).sum()
    value=a@x+x@b@y
    assert lo-1e-8<=value<=hi+1e-8
    return float(hi-lo),float(value)


def exact(a,b):
    n=len(a);settings=dict(primal_feasibility_tolerance=1e-9,dual_feasibility_tolerance=1e-9)
    upper=linprog(np.r_[np.zeros(n),np.ones(n)],A_ub=np.c_[b,-np.eye(n)],b_ub=-a,
        bounds=[(0,1)]*n+[(0,None)]*n,method='highs',options=settings)
    lower=linprog(np.r_[-a,-np.ones(n)],A_ub=np.c_[-b.T,np.eye(n)],b_ub=np.zeros(n),
        bounds=[(0,1)]*n+[(None,0)]*n,method='highs',options=settings)
    assert upper.success and lower.success,(upper.message,lower.message)
    x,y=lower.x[:n],upper.x[:n];gap,value=gap_value(a,b,x,y)
    assert abs(upper.fun+lower.fun)<1e-6 and gap<1e-6
    return x,y,dict(value_bb=value,primal_dual_gap_bb=float(upper.fun+lower.fun),response_gap_bb=gap)


def cfr(a,b,limit=50000):
    n=len(a);rx=np.zeros((2,n));ry=rx.copy();sx=np.zeros(n);sy=sx.copy();total=0.;trace=[]
    def policy(r):
        den=r.sum(0)
        return np.divide(r[1],den,out=np.full(n,.5),where=den>0)
    start=time.monotonic()
    for t in range(1,limit+1):
        x,y=policy(rx),policy(ry)
        u=a+b@y
        rx=np.maximum(rx+np.array([-x*u,(1-x)*u]),0)
        x=policy(rx);u=-b.T@x
        ry=np.maximum(ry+np.array([-y*u,(1-y)*u]),0)
        y=policy(ry)
        sx+=t*x;sy+=t*y;total+=t
        if t%1000==0:
            gap,value=gap_value(a,b,sx/total,sy/total)
            trace.append(dict(iteration=t,gap_bb=gap,value_bb=value))
            if gap<=.001:break
    x,y=sx/total,sy/total;gap,value=gap_value(a,b,x,y)
    return x,y,dict(iterations=t,gap_bb=gap,value_bb=value,elapsed_seconds=time.monotonic()-start,trace=trace)


def run():
    assert not (OUT/'results.json').exists(),'Preserve completed experiment'
    counts,combos,left,right=card_pairs()
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    audit=s.read(s.OUT/'premium-branches.json');root=next(n for n in audit['nodes'] if len(n['path'])==8)
    saved=np.array([root['view']['reaches_all'][p] for p in [1,2]])
    premium=np.zeros((2,169));premium[:,[168,154,167,142,140]]=[[1,1,.5,.3,.2],[1,.7,1,.5,.2]]
    fixtures=[('uniform10',np.ones((2,169)),3.,9.,8.),('saved200_zero_rake',saved,27.5,194.,182.),('overlapping_premiums',premium,3.,49.,48.)]
    rows=[];rng=np.random.default_rng(19092026)
    for name,weights,pot,own,other in fixtures:
        chance,a,b,called=game(weights,counts,eq,pot,own,other)
        maximum_error=0.
        for _ in range(3):
            x,y=rng.random(169),rng.random(169)
            p=weights[0,left]*weights[1,right];p/=p.sum()
            u=x[left]*((1-y[right])*pot+y[right]*called[left,right])
            v=(1-x[left])*pot+x[left]*y[right]*(pot-called[left,right])
            assert abs(p@(u+v)-pot)<1e-10
            error=abs(p@u-(a@x+x@b@y));maximum_error=max(maximum_error,error)
            assert error<1e-10
        xlp,ylp,lp=exact(a,b);xc,yc,cf=cfr(a,b)
        assert cf['gap_bb']<=.001
        assert abs(cf['value_bb']-lp['value_bb'])<=cf['gap_bb']+1e-8
        _,ai,bi,_=game(weights,combos[:,None]*combos[None,:],eq,pot,own,other)
        xi,yi,li=exact(ai,bi);cross_gap,cross_value=gap_value(a,b,xi,yi)
        row=dict(name=name,weights=weights.tolist(),pot=pot,hero_add=own,opponent_add=other,
            physical_pair_payoff_max_error_bb=float(maximum_error),exact=lp,cfr=cf,
            independent_exact=li,independent_policy_compatible_gap_bb=cross_gap,independent_policy_compatible_value_bb=cross_value,
            compatible_policies=dict(hero_jam=xc.tolist(),opponent_call=yc.tolist()),
            exact_policies=dict(hero_jam=xlp.tolist(),opponent_call=ylp.tolist()),
            independent_policies=dict(hero_jam=xi.tolist(),opponent_call=yi.tolist()))
        rows.append(row);print(name,lp,cf['iterations'],cf['gap_bb'],'independent cross gap',cross_gap,flush=True)
    s.write(OUT/'results.json',dict(results=rows,
        inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in [OUT/'PROTOCOL.md',s.ROOT/'tools/research/card_compatible_hu.py',s.OUT/'premium-branches.json',s.ROOT/'cache/preflop_eq169.bin']},
        note='Zero-rake two-player push/fold class abstraction, fixed sampled equities. Exact compatible physical hole-card counts. Not a full preflop or postflop solution; no GPU integration.'))


if __name__=='__main__':run()
