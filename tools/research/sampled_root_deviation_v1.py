"""Fit a root-only class response on training deals; score it on disjoint deals.

All downstream behavior stays frozen. The fitted action can depend only on the
acting player's own hand class, not the opponent cards or future board. This is
a tested deviation, never a best-response upper bound or a new equilibrium.
"""
import numpy as np


def observations(ids, classes, action_values, baseline_values):
    ids=tuple(ids);classes=np.asarray(classes);values=np.asarray(action_values,dtype=float)
    baseline=np.asarray(baseline_values,dtype=float)
    if (not ids or any(not isinstance(x,str) or not x for x in ids)
            or len(set(ids))!=len(ids)):
        raise ValueError('Distinct complete-deal sample IDs required')
    if (classes.shape!=(len(ids),) or not np.issubdtype(classes.dtype,np.integer)
            or np.any(classes<0) or np.any(classes>=169)):
        raise ValueError('Only the acting player hand class may select a root action')
    if (values.ndim!=2 or values.shape[0]!=len(ids) or not 2<=values.shape[1]<=4
            or baseline.shape!=(len(ids),) or not np.isfinite(values).all()
            or not np.isfinite(baseline).all()):
        raise ValueError('Finite per-deal root-action and baseline values required')
    return ids,classes.astype(np.int64),values,baseline


def learn(ids,classes,action_values,baseline_values,*,minimum_training_deals):
    ids,classes,values,baseline=observations(ids,classes,action_values,baseline_values)
    if type(minimum_training_deals) is not int or minimum_training_deals<1:
        raise ValueError('Positive predeclared class-support threshold required')
    counts=np.bincount(classes,minlength=169);sums=np.zeros((169,values.shape[1]))
    np.add.at(sums,classes,values)
    actions=np.full(169,-1,dtype=np.int64)
    supported=counts>=minimum_training_deals
    actions[supported]=sums[supported].argmax(axis=1)
    # Missing/sparse training classes keep the complete baseline strategy. The
    # choice among sufficiently sampled classes is fixed before evaluation.
    return dict(format=1,training_ids=list(ids),actions=actions.tolist(),
                training_counts=counts.tolist(),action_count=values.shape[1],
                minimum_training_deals=minimum_training_deals,
                fallback='unchanged baseline',tie_rule='first maximizing legal action')


def differences(response,ids,classes,action_values,baseline_values):
    ids,classes,values,baseline=observations(ids,classes,action_values,baseline_values)
    if response.get('format')!=1 or response.get('action_count')!=values.shape[1]:
        raise ValueError('Response format/menu mismatch')
    training=response.get('training_ids')
    if not isinstance(training,list) or not training or len(set(training))!=len(training):
        raise ValueError('Invalid training provenance')
    if set(ids)&set(training):raise ValueError('Training and evaluation samples overlap')
    actions=np.asarray(response.get('actions'))
    counts=np.asarray(response.get('training_counts'))
    threshold=response.get('minimum_training_deals')
    if (actions.shape!=(169,) or counts.shape!=(169,) or not np.issubdtype(actions.dtype,np.integer)
            or not np.issubdtype(counts.dtype,np.integer) or np.any(counts<0)
            or type(threshold) is not int or threshold<1
            or np.any(actions < -1) or np.any(actions>=values.shape[1])
            or np.any((actions==-1)!=(counts<threshold)) or counts.sum()!=len(training)):
        raise ValueError('Invalid frozen class response')
    selected=actions[classes];result=np.zeros(len(ids));changed=selected>=0
    result[changed]=values[np.flatnonzero(changed),selected[changed]]-baseline[changed]
    return result
