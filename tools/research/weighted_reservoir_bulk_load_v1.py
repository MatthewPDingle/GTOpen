"""Validate saved weighted rows in bounded NumPy batches, preserving every check."""
import json
import numpy as np
from weighted_physical_reservoir_v1 import ARRAYS, METHOD, WeightedPhysicalReservoir


def load(path,context_source,*,guard=lambda:None):
    guard()
    with np.load(path,allow_pickle=False) as data:
        if set(data.files)!=set(ARRAYS)|{'metadata'}:
            raise ValueError('Explicit weighted checkpoint arrays required')
        m=json.loads(str(data['metadata']))
        if m.get('format')!=2 or m.get('method')!=METHOD or type(m.get('seen')) is not int or not 0<=m['seen']<2**63:
            raise ValueError('Unsupported weighted checkpoint')
        result=WeightedPhysicalReservoir(m['capacity'],m['player'],0,context_source)
        if result.context_sha256!=m['context_sha256']:raise ValueError('Changed context')
        size=min(m['seen'],m['capacity'])
        for name in ARRAYS:
            guard()
            target=getattr(result,name);source=data[name]
            if source.dtype!=target.dtype or source.shape!=target[:size].shape:
                raise ValueError('Checkpoint array mismatch')
            target[:size]=source
        # uint64 key storage already enforces the checked_row key bounds.
        # The constructor checks actor/capacity; dtype/shape checks above retain
        # the exact original contract. Sorting below is a private validation
        # copy, not a change to the saved feature order.
        for start in range(0,size,16384):
            guard();stop=min(start+16384,size)
            active=result.active[start:stop]
            sorted_active=np.sort(active,axis=1)
            if np.any(active>=269) or np.any(sorted_active[:,1:]==sorted_active[:,:-1]):
                raise ValueError('Invalid visible feature row')
            arity=result.arity[start:stop]
            if np.any((arity<2)|(arity>4)):raise ValueError('Invalid legal menu')
            values=result.values[start:stop]
            illegal=np.arange(4)[None,:]>=arity[:,None]
            if not np.isfinite(values).all() or np.any(values[illegal]):
                raise ValueError('Invalid signed advantage values')
            weights=result.deal_weights[start:stop]
            if not np.isfinite(weights).all() or np.any((weights<=0)|(weights>65536)):
                raise ValueError('Positive bounded importance weight required')
            if np.any(result.iterations[start:stop]==0):raise ValueError('Missing iteration')
        result.rng.bit_generator.state=m['rng'];result.seen=m['seen']
        return result
