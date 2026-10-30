"""Unqualified GPU candidate using the CPU-qualified JSON-native snapshot.

Same tensors, shared-query type, four frozen banks and native batch evaluator.
Not connected to the running evaluation. Full GPU/cashflow control required.
"""
from native_query_snapshot_v1 import snapshot
from shared_visible_query_arrays_v1 import prepare
from sampled_visible_hybrid_gpu_bank_shared_v1 import PreparedCudaQueries
from crossed_complete_policy_batch_shared_v1 import _BankAdapter
from crossed_complete_policy_batch_v1 import evaluate_batch as original_evaluate_batch


def prepare_cuda_queries(queries, *, guard):
    import torch
    guard()
    isolated=snapshot(queries)
    arrays=prepare(isolated)
    tensors={name:torch.tensor(getattr(arrays,name),device='cuda')
             for name in ('features','actors','legal','prior','action','valid')}
    ids=tuple(torch.nonzero(tensors['actors']==p).flatten() for p in (0,1))
    guard()
    return PreparedCudaQueries(isolated,**tensors,ids=ids)


class SharedPreparation:
    def __init__(self,guard):
        self.guard=guard; self.query=None; self.prepared=None; self.calls=0

    def get(self,queries):
        if self.query is not queries:
            if self.query is not None: raise ValueError('A crossed batch must use one common query object')
            self.prepared=prepare_cuda_queries(queries,guard=self.guard)
            self.query=queries;self.calls+=1
        return self.prepared


def evaluate_batch(*,banks,guard,**kwargs):
    if len(banks)!=4 or any(not callable(getattr(bank,'average_prepared',None)) for bank in banks):
        raise ValueError('Four shared-query model banks required')
    shared=SharedPreparation(guard)
    result=original_evaluate_batch(banks=[_BankAdapter(bank,shared) for bank in banks],guard=guard,**kwargs)
    if shared.calls!=1:raise ValueError('Shared query preparation count changed')
    return result
