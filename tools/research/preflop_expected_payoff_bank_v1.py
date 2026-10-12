"""Frozen complete played ExpectedPolicy bank for prospective payoff evaluation.

No training, sampling, source migration or production changes. Engines are
constructed once per bank/context; their infer/prepare math is unchanged.
Only completed generations 0..31 may enter the scientific evaluation bank.
"""
import copy
import hashlib
import json
import numpy as np

from preflop_expected_policy_v1 import ExpectedPolicy, TYPE, encoded


def selected_documents(documents, *, completed_cycles, next_generation):
    if (type(completed_cycles) is not int or completed_cycles != 32
            or type(next_generation) is not int or next_generation != 32
            or not isinstance(documents, (list, tuple)) or len(documents) != 32):
        raise ValueError('Fixed completed32 and excluded unplayed32 required')
    result = []
    shared_kind = None
    for generation, value in enumerate(documents):
        if (not isinstance(value, dict) or value.get('policy_type') != TYPE
                or type(value.get('generation')) is not int
                or value['generation'] != generation):
            raise ValueError('ExpectedPolicy complete played0..31 required in order')
        kind = value['shared']['policy_type']
        if shared_kind is not None and kind != shared_kind:
            raise ValueError('Mixed shared-network representation refused')
        shared_kind = kind
        result.append(copy.deepcopy(value))
    return result


def average_engines(engines, queries, *, guard):
    """Same summation order, own-history products and zero-support fallback."""
    observations = queries['observations']
    if not observations or not engines:
        raise ValueError('Nonempty checked observations and frozen engines required')
    actors = np.asarray([o['actor'] for o in observations])
    numerator = np.zeros((len(actors), 4)); denominator = np.zeros(len(actors))
    for generation, engine in enumerate(engines):
        guard()
        if engine.generation != generation:
            raise ValueError('Engine bank generation order changed')
        prepared = engine.prepare(queries)
        p = engine.infer(prepared)
        # Every registered actor/generation weight is exactly one.
        reach = np.ones(len(actors), dtype=np.float64)
        for i, history in enumerate(prepared['own_history']):
            for parent, action in history:
                reach[i] *= p[parent, action]
        numerator += reach[:, None] * p; denominator += reach
    result = np.zeros_like(numerator); supported = denominator > 0
    result[supported] = numerator[supported] / denominator[supported, None]
    for i in np.flatnonzero(~supported):
        result[i, :observations[i]['n']] = 1. / observations[i]['n']
    if (not np.isfinite(result).all() or not np.isfinite(denominator).all()
            or np.max(abs(result.sum(1) - 1)) > 1e-12):
        raise ValueError('Invalid frozen complete played average')
    return result, denominator


class FixedExpectedBank:
    def __init__(self, documents, registry, resources, *, context_sha256,
                 completed_cycles, next_generation, device, guard):
        fixed = selected_documents(documents, completed_cycles=completed_cycles,
                                   next_generation=next_generation)
        self.context_sha256 = context_sha256
        self.context_source = registry.source(context_sha256)
        self.device = device
        self.model_identities = tuple(hashlib.sha256(encoded(value)).hexdigest() for value in fixed)
        self.engines = []
        for value in fixed:
            guard()
            self.engines.append(ExpectedPolicy(value, registry, resources=resources,
                                              context_sha256=context_sha256, device=device))
        self.engines = tuple(self.engines)

    def average(self, queries, *, guard):
        if queries.get('context_source') != self.context_source:
            raise ValueError('Bank belongs to a different registered context')
        return average_engines(self.engines, queries, guard=guard)

    def identity(self):
        return dict(policy_type=TYPE, context_sha256=self.context_sha256,
                    model_document_sha256=list(self.model_identities),
                    played_generations=list(range(32)), weights_by_player=[[1.] * 32, [1.] * 32],
                    excluded_unplayed_generation=32, device=self.device,
                    inference='unchanged ExpectedPolicy.prepare/infer; original ordered float64 own-history average')
