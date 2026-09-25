"""Unqualified crossed-batch candidate using one shared query preparation.

The original transport, native evaluator, validation and output format remain
in use. Only its four bank calls are adapted; their timing includes preparation.
"""
from crossed_complete_policy_batch_v1 import evaluate_batch as original_evaluate_batch
from sampled_visible_hybrid_gpu_bank_shared_v1 import prepare_cuda_queries


class _SharedPreparation:
    def __init__(self, guard):
        self.guard = guard
        self.query = None
        self.prepared = None
        self.calls = 0

    def get(self, queries):
        if self.query is not queries:
            if self.query is not None:
                raise ValueError('A crossed batch must use one common query object')
            self.prepared = prepare_cuda_queries(queries, guard=self.guard)
            self.query = queries
            self.calls += 1
        return self.prepared


class _BankAdapter:
    def __init__(self, bank, shared):
        self.bank = bank
        self.shared = shared

    def average(self, queries, *, guard):
        return self.bank.average_prepared(self.shared.get(queries), guard=guard)


def evaluate_batch(*, banks, guard, **kwargs):
    if len(banks) != 4 or any(not callable(getattr(bank, 'average_prepared', None)) for bank in banks):
        raise ValueError('Four shared-query model banks required')
    shared = _SharedPreparation(guard)
    result = original_evaluate_batch(banks=[_BankAdapter(bank, shared) for bank in banks],
                                    guard=guard, **kwargs)
    if shared.calls != 1:
        raise ValueError('Shared query preparation count changed')
    return result
