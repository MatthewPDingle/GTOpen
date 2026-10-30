"""Orthogonal Fold/Call projection onto verified terminal payoff bounds."""
import numpy as np

ROW_ATOL_BB2=1e-8
ROW_RTOL=1e-12
VIOLATION_TOLERANCE_BB=1e-10
POLICY_TOLERANCE=1e-12


def project(scores,arity,eligible,public,scale):
    scores=np.asarray(scores,dtype=np.float64);arity=np.asarray(arity);eligible=np.asarray(eligible)
    public=np.asarray(public,dtype=np.float64)
    n=len(scores)
    if (scores.shape!=(n,4) or arity.shape!=(n,) or eligible.shape!=(n,) or public.shape!=(n,4)
        or eligible.dtype!=bool or not np.isfinite(scores).all() or not np.isfinite(scale) or scale<=0
        or np.any((arity<2)|(arity>4))):raise ValueError('Invalid projection inputs')
    p,c,r,total=public[eligible].T
    if (not np.isfinite(public[eligible]).all() or np.any(c<=0) or np.any(p<=0)
        or np.any(r<0) or np.any(r>=p+c) or np.any(p+c>total+1e-8)):
        raise ValueError('Invalid verified river geometry')
    difference=(scores[eligible,1]-scores[eligible,0])*scale
    bounded=np.clip(difference,-c,p-r)
    adjustment=(bounded-difference)/(2*scale)
    result=scores.copy()
    result[eligible,0]-=adjustment;result[eligible,1]+=adjustment
    assert np.isfinite(result).all()
    assert np.array_equal(result[~eligible],scores[~eligible])
    assert np.array_equal(result[:,2:],scores[:,2:])
    return result


def policy(scores,arity):
    scores=np.asarray(scores,dtype=np.float64);arity=np.asarray(arity)
    if scores.shape!=(len(arity),4) or not np.isfinite(scores).all() or np.any((arity<2)|(arity>4)):
        raise ValueError('Invalid policy inputs')
    legal=np.arange(4)[None,:]<arity[:,None]
    out=np.maximum(scores,0.)*legal;mass=out.sum(axis=1);positive=mass>0
    out[positive]/=mass[positive,None]
    empty=np.flatnonzero(~positive)
    chosen=np.argmax(np.where(legal,scores,-np.inf),axis=1)
    out[empty,chosen[empty]]=1.
    assert np.isfinite(out).all() and np.all(out>=0) and np.all(out[~legal]==0)
    assert np.max(np.abs(out.sum(axis=1)-1))<1e-12
    return out


def predict_numpy64(x,parameters,guard):
    outputs=[]
    for start in range(0,len(x),8192):
        guard();y=x[start:start+8192].astype(np.float64)
        for layer in range(3):
            w=parameters[f'{layer*2}.weight'];b=parameters[f'{layer*2}.bias']
            assert w.dtype==b.dtype==np.float64
            y=y@w.T+b
            if layer!=2:y=np.maximum(y,0.)
        outputs.append(y)
    result=np.concatenate(outputs);assert np.isfinite(result).all();return result


def error_checks(before,after,arity,eligible,values,scale):
    legal=np.arange(4)[None,:]<arity[:,None]
    raw_before=before*scale;raw_after=after*scale
    first=((raw_before-values)**2*legal).sum(axis=1)
    second=((raw_after-values)**2*legal).sum(axis=1)
    bound=ROW_ATOL_BB2+ROW_RTOL*first
    assert np.all(second-first<=bound),float(np.max(second-first-bound))
    target=values[:,1]-values[:,0]
    c0=((raw_before[:,1]-raw_before[:,0])-target)**2
    c1=((raw_after[:,1]-raw_after[:,0])-target)**2
    assert np.all((c1-c0)[eligible]<=ROW_ATOL_BB2+ROW_RTOL*c0[eligible])
    assert np.array_equal(before[~eligible],after[~eligible])
    return dict(maximum_action_error_increase_bb2=float(np.max(second-first)),
        maximum_contrast_error_increase_bb2=float(np.max((c1-c0)[eligible])),
        per_row_action_error_nonincrease=True,per_row_contrast_error_nonincrease=True,
        all_unaffected_rows_identical=True,absolute_tolerance_bb2=ROW_ATOL_BB2,relative_tolerance=ROW_RTOL)


def math_control():
    # Upper/lower/interior/boundary/no-op fixtures in chip units.
    raw=np.array([[-4.,8.,3.,7.],[8.,-4.,3.,7.],[1.,2.,3.,7.],[0.,5.6,3.,7.],[-4.,8.,3.,7.]])
    arity=np.array([4,3,2,3,4]);eligible=np.array([True,True,True,True,False])
    geo=np.array([[6.,2.,.4,100.]]*5)
    out=project(raw,arity,eligible,geo,1.)
    expected=np.array([[-.8,4.8,3.,7.],[3.,1.,3.,7.],[1.,2.,3.,7.],[0.,5.6,3.,7.],[-4.,8.,3.,7.]])
    assert np.allclose(out,expected,rtol=0,atol=1e-14)
    assert np.allclose(project(out,arity,eligible,geo,1.),out,rtol=0,atol=1e-14)
    assert np.allclose(out[:,:2].sum(axis=1),raw[:,:2].sum(axis=1),rtol=0,atol=1e-14)
    for bad_scale in (0.,-1.,np.nan,np.inf):
        try:project(raw,arity,eligible,geo,bad_scale)
        except ValueError:pass
        else:raise AssertionError('Bad scale accepted')
    rng=np.random.Generator(np.random.PCG64(9287701));n=2048
    p=rng.uniform(1,500,n);c=rng.uniform(.1,200,n);r=np.minimum(.05*(p+c),2.)
    geo=np.column_stack((p,c,r,p+c+500))
    scores=rng.normal(0,400,(n,4));arity=rng.integers(2,5,n);eligible=np.ones(n,dtype=bool)
    out=project(scores,arity,eligible,geo,1.)
    assert np.max(np.abs(project(out,arity,eligible,geo,1.)-out))<1e-12
    offsets=rng.uniform(-1000,1000,(n,1))
    assert np.max(np.abs(project(scores+offsets,arity,eligible,geo,1.)-(out+offsets)))<1e-12
    for factor in (.01,2.,100.):
        assert np.max(np.abs(project(scores*factor,arity,eligible,geo*factor,1.)-out*factor))<1e-9
    for scale in (.03,17.,200.):
        assert np.max(np.abs(project(scores/scale,arity,eligible,geo,scale)*scale-out))<1e-12
    weighted_maximum=0.
    for target_delta in (-c,(p+c-r)/2-c,p-r):
        targets=rng.normal(0,100,(n,4));targets[:,1]=targets[:,0]+target_delta
        targets[np.arange(4)[None,:]>=arity[:,None]]=0
        proof=error_checks(scores,out,arity,eligible,targets,1.)
        legal=np.arange(4)[None,:]<arity[:,None];weights=rng.uniform(.01,500,n)
        old=((scores-targets)**2*legal).sum(axis=1);new=((out-targets)**2*legal).sum(axis=1)
        change=float(np.dot(weights,new-old));assert change<=1e-6
        weighted_maximum=max(weighted_maximum,change)
    fixture=np.array([[2.,1.,-1.,99.],[-3.,-2.,-5.,99.],[-2.,-2.,-5.,99.],[0.,0.,0.,99.]])
    expected=np.array([[2/3,1/3,0.,0.],[0.,1.,0.,0.],[1.,0.,0.,0.],[1.,0.,0.,0.]])
    assert np.array_equal(policy(fixture,np.array([3,3,3,3])),expected)
    return dict(passed=True,hand_calculated_cases=5,random_rows=n,endpoint_target_cases=3*n,
        idempotent=True,common_offset_invariant=True,positive_unit_covariant=True,
        normalized_and_chip_formulas_agree=True,other_actions_unchanged=True,
        first_two_sum_preserved=True,invalid_scales_rejected=True,unequal_row_weights_checked=True,
        positive_regret_rule=True,negative_fallback_and_ties_checked=True,
        no_claim_of_policy_invariance=True,largest_weighted_error_increase=weighted_maximum)
