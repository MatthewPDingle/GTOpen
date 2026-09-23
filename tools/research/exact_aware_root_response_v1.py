"""Fit a class-only root deviation using exact fold/shove conditional means.

Training may have deliberately unequal class frequencies, provided each class's
opponent cards and runouts follow its correct conditional law. Population test
draws and exact-value provenance are separate caller obligations. This module
does not load any model, draw test hands, or change downstream strategies.
"""
import re
import numpy as np
from root_residual_evaluation_v1 import policy


def sample_ids(ids):
    ids=list(ids)
    if not ids or any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=len(ids):
        raise ValueError('Distinct nonempty sample identities required')
    return ids


def fit(ids,classes,action_values,baseline,masses,fold_entries,jam_entries,*,context_sha256,minimum_training_deals):
    ids=sample_ids(ids)
    if not isinstance(context_sha256,str) or not re.fullmatch('[0-9a-f]{64}',context_sha256):
        raise ValueError('Context byte identity required')
    if type(minimum_training_deals) is not int or minimum_training_deals<1:
        raise ValueError('A positive fixed per-class support threshold is required')
    c=np.asarray(classes);q=np.asarray(action_values,dtype=np.float64);base=policy(baseline)
    if c.shape!=(len(ids),) or not np.issubdtype(c.dtype,np.integer) or np.any(c<0) or np.any(c>168) or q.shape!=(len(ids),4) or not np.isfinite(q).all():
        raise ValueError('Own hand classes and finite four-action training observations required')
    mass,fold,jam=[np.asarray(x,dtype=np.float64) for x in (masses,fold_entries,jam_entries)]
    if any(x.shape!=(169,) or not np.isfinite(x).all() for x in (mass,fold,jam)) or np.min(mass)<=0 or abs(mass.sum()-1)>1e-12:
        raise ValueError('Exact values with positive normalized population masses required')
    counts=np.bincount(c,minlength=169);sums=np.zeros((169,4));np.add.at(sums,c,q)
    means=sums/np.maximum(counts[:,None],1)
    means[:,0]=fold/mass;means[:,3]=jam/mass
    if not np.isfinite(means).all():raise ValueError('Conditional action-value overflow')
    selected=np.where(counts>=minimum_training_deals,np.argmax(means,axis=1),-1)
    rho=base.copy();supported=selected>=0;rho[supported]=np.eye(4)[selected[supported]]
    return dict(format=1,method='exact-aware-root-response-v1',context_sha256=context_sha256,
        training_ids=ids,training_counts=counts.tolist(),minimum_training_deals=minimum_training_deals,
        selected_actions=selected.tolist(),probabilities=rho.tolist(),baseline=base.tolist(),
        class_action_means=means.tolist(),class_population_masses=mass.tolist(),
        missing_or_sparse='preserve baseline',tie_rule='first maximizing legal action',
        selection_information='Own hand class only; all later policies remain frozen',
        population_test_required=True,best_response_upper_bound=False)


def frozen_policy(response,*,context_sha256):
    if response.get('format')!=1 or response.get('method')!='exact-aware-root-response-v1' or response.get('context_sha256')!=context_sha256:
        raise ValueError('Response method or context mismatch')
    ids=sample_ids(response['training_ids']);p=policy(response['probabilities']);base=policy(response['baseline'])
    counts=np.asarray(response['training_counts']);actions=np.asarray(response['selected_actions']);minimum=response['minimum_training_deals']
    if type(minimum) is not int or minimum<1 or counts.shape!=(169,) or actions.shape!=(169,) or not np.issubdtype(counts.dtype,np.integer) or not np.issubdtype(actions.dtype,np.integer):
        raise ValueError('Invalid frozen responder shape or support threshold')
    if np.any(counts<0) or counts.sum()!=len(ids) or np.any(actions<-1) or np.any(actions>3) or np.any((actions==-1)!=(counts<minimum)):
        raise ValueError('Invalid frozen responder action or support counts')
    supported=actions>=0;expected=base.copy();expected[supported]=np.eye(4)[actions[supported]]
    if not np.array_equal(p,expected):raise ValueError('Frozen response does not match declared choices and fallback')
    return p


def admit_test_ids(response,ids,*,context_sha256):
    frozen_policy(response,context_sha256=context_sha256)
    ids=sample_ids(ids)
    if set(ids)&set(response['training_ids']):raise ValueError('Training/test sample identity overlap')
    return ids
