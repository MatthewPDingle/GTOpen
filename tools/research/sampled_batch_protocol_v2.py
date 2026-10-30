"""Transport exact input identity without a JSON-number round trip."""
import numpy as np


def policy_document(queries, probabilities):
    if queries.get('format')!=2 or not isinstance(queries.get('context_source'),str) or not isinstance(queries.get('batch_source'),str):
        raise ValueError('Original context and batch source identities required')
    if np.asarray(probabilities).shape!=(len(queries['observations']),4):
        raise ValueError('Policy rows do not match the exported query count')
    return dict(format=2,context_source=queries['context_source'],batch_source=queries['batch_source'],policies=[
        dict(hi=o['hi'],lo=o['lo'],actor=o['actor'],n=o['n'],probabilities=list(map(float,p)))
        for o,p in zip(queries['observations'],probabilities)])
