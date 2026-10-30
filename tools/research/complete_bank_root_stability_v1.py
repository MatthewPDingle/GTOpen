"""Descriptive two-seed BB-root stability, separate from policy effectiveness."""
import numpy as np


def summarize(policies, masses):
    p=np.asarray(policies,dtype=np.float64);m=np.asarray(masses,dtype=np.float64)
    if (p.shape!=(4,169,4) or m.shape!=(169,) or not np.isfinite(p).all()
            or not np.isfinite(m).all() or np.any(p<0) or np.any(m<=0)
            or abs(m.sum()-1)>1e-12 or np.max(abs(p.sum(2)-1))>1e-10):
        raise ValueError('Four normalized complete root policies and compatible entry masses required')
    comparisons={}
    for name,a,b in [('baseline_cross_seed',0,2),('candidate_cross_seed',1,3),
                     ('first_matched_change',0,1),('replication_matched_change',2,3)]:
        tv=.5*np.abs(p[a]-p[b]).sum(1)
        comparisons[name]=dict(entry_weighted_total_variation=float(m@tv),
            class_total_variation=tv.tolist(),
            classes_with_different_most_frequent_action=int(np.sum(p[a].argmax(1)!=p[b].argmax(1))))
    return dict(policy_order=['first-old','first-new','replication-old','replication-new'],
        action_order=['fold','call','raise','jam'],root_probabilities=p.tolist(),
        entry_masses=m.tolist(),aggregate_action_frequencies=np.einsum('c,bca->ba',m,p).tolist(),
        comparisons=comparisons,
        candidate_minus_baseline_variation=(comparisons['candidate_cross_seed']['entry_weighted_total_variation']
            -comparisons['baseline_cross_seed']['entry_weighted_total_variation']),
        units='probability; multiply by 100 for percentage points',accuracy_qualified=False,
        scope='Two fixed seeds; descriptive consistency, not a confidence interval or proof of accurate play.')
