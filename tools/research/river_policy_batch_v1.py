"""Research batch preparation, with one explicitly bound CPU current policy."""
import copy
import numpy as np
from board_training_checkpoint_v1 import validate_model
from board_training_policy_v1 import RootTable
from weighted_preflop_table_v1 import Table
from river_query_preparation_vector_v1 import prepare
from board_river_bounds_math_v1 import policy


class CPUCurrentPolicy:
    def __init__(self,model,context_source,**args):
        root,_,exact=validate_model(model,context_source=context_source,**args)
        self.context_source=context_source
        self.tables=[Table(t,context_source) for t in model['preflop_tables'] if t is not None]
        self.tables.extend([exact,RootTable(root,context_source,args['catalog_source'])])
        self.weights=[]
        for net in model['networks']:
            self.weights.append([(np.asarray(net[f'w{i}'],np.float32).astype(np.float64).reshape(shape),
                                  np.asarray(net[f'b{i}'],np.float32).astype(np.float64))
                                 for i,shape in enumerate(((64,302),(64,64),(4,64)))])

    def prepare(self,queries):return prepare(self,queries)

    def infer(self,prepared):
        a=prepared['arrays'];scores=np.zeros((len(a.actors),4))
        for actor in (0,1):
            ids=np.flatnonzero(a.actors==actor)
            if not len(ids):continue
            y=a.features[ids]
            for i,(w,b) in enumerate(self.weights[actor]):
                y=y@w.T+b
                if i<2:y=np.maximum(y,0.)
            scores[ids]=y
        p=policy(scores,prepared['arity']);mask=prepared['mask'];p[mask]=prepared['table'][mask]
        assert np.isfinite(p).all() and np.all(p>=0) and np.max(abs(p.sum(1)-1))<1e-12 and not np.any(p[~a.legal])
        return p


def merge_queries(documents,context_source):
    """Deduplicate visible keys and remap actual own histories without changing them."""
    keys={};rows=[];mappings=[]
    for query in documents:
        if query['context_source']!=context_source:raise ValueError('Context mismatch')
        mapping=[]
        for o in query['observations']:
            key=(o['hi'],o['lo'])
            if key not in keys:keys[key]=len(rows);rows.append(None)
            mapping.append(keys[key])
        mappings.append(np.asarray(mapping,dtype=np.int64))
    for query,mapping in zip(documents,mappings):
        for i,o in enumerate(query['observations']):
            row=copy.deepcopy(o);row['own_history']=[[int(mapping[j]),a,n] for j,a,n in o['own_history']]
            at=int(mapping[i])
            if rows[at] is None:rows[at]=row
            elif rows[at]!=row:raise ValueError('Duplicate key has different visible features, legality or own history')
    if not rows or any(o is None for o in rows):raise ValueError('Incomplete union')
    return dict(format=2,context_source=context_source,batch_source='river-visible-query-union-v1',observations=rows),mappings
