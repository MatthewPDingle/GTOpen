"""Separate producer byte identity from independent numerical verification.

Only seals use the original provider with its recorded two BLAS threads.
The independent policy, scalar cashflows and root updates remain the audit's
numerical reference. Different legal floating-point reductions need not hash
identically; the existing numerical tolerances are unchanged.
"""
import numpy as np
from threadpoolctl import threadpool_limits
from board_training_targets_v1 import prepare
from board_root_accumulator_v1 import digest


def verify_identity(payload, independent, evidence):
    with threadpool_limits(limits=2):
        produced = prepare(**payload)
    root_hash = digest(produced['pre'][0].tolist())
    exact_hash = digest(produced['exact'].tolist())
    if evidence['played_policy_sha256'] != root_hash or evidence['exact_terms_sha256'] != exact_hash:
        raise ValueError('Producer bytes disagree with recorded seals')
    if set(produced['pre']) != set(independent['pre']):
        raise ValueError('Independent preflop topology differs')
    maximum_policy = max(float(np.max(abs(p-independent['pre'][n]))) for n,p in produced['pre'].items())
    maximum_exact = float(np.max(abs(produced['exact']-independent['exact_scalar'])))
    if not np.isfinite(maximum_policy) or maximum_policy >= 1e-10:
        raise ValueError('Independent preflop policy differs beyond tolerance')
    if not np.isfinite(maximum_exact) or maximum_exact >= 1e-10:
        raise ValueError('Independent exact cashflows differ beyond tolerance')
    q = produced['exact'] + np.mean([d['values'] for d in evidence['draws']], axis=0)
    root = produced['pre'][0]
    delta = (payload['root_config']['physical_budget']*produced['class_mass'])[:,None]*(q-np.sum(root*q,axis=1)[:,None])
    return dict(played_policy_sha256=root_hash, exact_terms_sha256=exact_hash,
                delta_sha256=digest(delta.tolist()), maximum_policy_error=maximum_policy,
                maximum_exact_error=maximum_exact)
