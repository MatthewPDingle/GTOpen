"""Candidate all-nonpositive fallback; not yet qualified by self-play.

Brown et al. ICML 2019, section 2, equation 4 discussion: choose the highest
estimated regret rather than uniform when no positive regret is predicted.
"""
import numpy as np
from hu_sampled_neural_control_20260922 import regret_policy


def highest_regret_fallback(values, mask):
    values=np.asarray(values,dtype=float);mask=np.asarray(mask,dtype=bool)
    assert values.shape==mask.shape and np.isfinite(values).all() and mask.any(axis=1).all()
    result=regret_policy(values,mask)
    no_positive=(np.maximum(values,0)*mask).sum(axis=1)==0
    rows=np.flatnonzero(no_positive)
    chosen=np.where(mask,values,-np.inf).argmax(axis=1)
    result[rows]=0
    result[rows,chosen[rows]]=1
    return result


def check():
    values=np.array([[-1.,-.01,-.5],[2.,1.,-3.],[-2.,-1.,100.],[0.,0.,0.],[-3.,-3.,-4.]])
    mask=np.array([[1,1,1],[1,1,1],[1,1,0],[1,1,0],[1,1,1]],dtype=bool)
    expected=np.array([[0,1,0],[2/3,1/3,0],[0,1,0],[1,0,0],[1,0,0]])
    actual=highest_regret_fallback(values,mask)
    assert np.allclose(actual,expected,rtol=0,atol=1e-15)
    assert np.all(actual[~mask]==0) and np.allclose(actual.sum(axis=1),1)
    return dict(passed=True,legal_action_mask=True,positive_regret_policy_unchanged=True,
                ties='first legal maximizing action',cases=len(values),self_play_qualified=False)
