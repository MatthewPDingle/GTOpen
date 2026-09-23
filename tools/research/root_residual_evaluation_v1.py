"""Exact root fold/shove offsets plus sampled call/raise residuals.

The optional class centre is fitted exclusively on independent training deals.
Its population expectation is added back, so it changes variance, not the
estimand. The caller must separately certify the complete class masses/values,
freeze the responder and centre, and supply independent population test draws.
"""
import math
import numpy as np


def policy(value):
    p=np.asarray(value,dtype=np.float64)
    if p.shape!=(169,4) or not np.isfinite(p).all() or np.min(p)<0 or np.max(abs(p.sum(1)-1))>1e-12:
        raise ValueError('A normalized four-action policy for all 169 classes is required')
    return p


def prepare(baseline,response,masses,fold_entries,jam_entries,*,training_classes,training_actions,centre,lower,upper):
    if type(centre) is not bool:raise ValueError('Explicit boolean centring choice required')
    baseline,response=policy(baseline),policy(response)
    mass,fold,jam=[np.asarray(x,dtype=np.float64) for x in (masses,fold_entries,jam_entries)]
    if any(x.shape!=(169,) or not np.isfinite(x).all() for x in (mass,fold,jam)) or np.min(mass)<=0 or abs(math.fsum(mass)-1)>1e-12:
        raise ValueError('Complete normalized positive class population and exact values required')
    if not math.isfinite(lower) or not math.isfinite(upper) or lower>=upper:
        raise ValueError('Fixed physical-payoff bounds required')
    ids=np.asarray(training_classes);q=np.asarray(training_actions,dtype=np.float64)
    if ids.ndim!=1 or not len(ids) or not np.issubdtype(ids.dtype,np.integer) or np.min(ids)<0 or np.max(ids)>168 or q.shape!=(len(ids),4):
        raise ValueError('Training classes and four action values required')
    if not np.isfinite(q).all() or np.min(q)<lower-1e-9 or np.max(q)>upper+1e-9:
        raise ValueError('Training values violate physical payoff bounds')
    delta=response-baseline
    residual=np.sum(delta[ids,1:3]*q[:,1:3],axis=1)
    counts=np.bincount(ids,minlength=169);means=np.zeros(169)
    if centre:
        sums=np.bincount(ids,weights=residual,minlength=169)
        means[counts>0]=sums[counts>0]/counts[counts>0]
    coefficients=delta[:,1:3]
    lo=np.sum(np.where(coefficients>=0,coefficients*lower,coefficients*upper),axis=1)-means
    hi=np.sum(np.where(coefficients>=0,coefficients*upper,coefficients*lower),axis=1)-means
    exact=math.fsum(delta[:,0]*fold+delta[:,3]*jam)
    centring=math.fsum(mass*means)
    return dict(delta=delta.tolist(),centre=means.tolist(),counts=counts.tolist(),
        exact_fold_jam_offset=exact,centre_population_offset=centring,total_offset=exact+centring,
        residual_lower=float(np.min(lo))-1e-9,residual_upper=float(np.max(hi))+1e-9,
        action_lower=lower,action_upper=upper,centred=bool(centre),
        unsupported_centre_rule='zero',scope='Estimator arithmetic only; population coverage, independent test draws and policy provenance are caller obligations.')


def residuals(prepared,classes,actions):
    ids=np.asarray(classes);q=np.asarray(actions,dtype=np.float64)
    if ids.ndim!=1 or not np.issubdtype(ids.dtype,np.integer) or np.any(ids<0) or np.any(ids>168) or q.shape!=(len(ids),4) or not np.isfinite(q).all():
        raise ValueError('Finite population test values and valid own-hand classes required')
    if len(ids) and (np.min(q)<prepared['action_lower']-1e-9 or np.max(q)>prepared['action_upper']+1e-9):
        raise ValueError('Test values violate physical payoff bounds')
    delta=np.asarray(prepared['delta']);centre=np.asarray(prepared['centre'])
    values=np.sum(delta[ids,1:3]*q[:,1:3],axis=1)-centre[ids]
    if len(values) and (np.min(values)<prepared['residual_lower'] or np.max(values)>prepared['residual_upper']):
        raise ValueError('Residual violates prospectively derived bounds')
    return values
