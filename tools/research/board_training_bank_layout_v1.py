"""CPU preparation of typed board-root histories for the shared bank evaluator."""
from types import SimpleNamespace
import numpy as np
from board_training_checkpoint_v1 import validate_model
from board_training_policy_v1 import RootTable
from weighted_preflop_table_v1 import Table

SHAPES={'w0':(64,302),'b0':(64,),'w1':(64,64),'b1':(64,),'w2':(4,64),'b2':(4,)}


def prepare_layout(documents,weights_by_player,*,completed_iterations,context_source,
                   catalog_source,matrix_sha256,entry_mass,root_config,guard):
    models=list(documents)
    if type(completed_iterations) is not int or completed_iterations<1 or len(models)!=completed_iterations:
        raise ValueError('Complete ordered played model bank required')
    weights=np.asarray(weights_by_player,dtype=np.float64)
    if (weights.shape!=(2,completed_iterations) or not np.isfinite(weights).all()
            or np.any(weights<=0) or not np.isfinite(weights.sum())):
        raise ValueError('Two positive finite weight sequences required')
    tables=[];parameters={name:[] for name in SHAPES};exact_geometry=None
    for generation,model in enumerate(models):
        guard()
        root,_,exact=validate_model(model,context_source=context_source,catalog_source=catalog_source,
            matrix_sha256=matrix_sha256,entry_mass=entry_mass,root_config=root_config)
        if model['generation']!=generation:raise ValueError('Reordered or unplayed board-root model')
        pair=[None if value is None else Table(value,context_source) for value in model['preflop_tables']]
        override=RootTable(root,context_source,catalog_source)
        rows={} if pair[0] is None else dict(pair[0].rows)
        rows.update(override.rows)
        pair[0]=SimpleNamespace(player=0,context=override.context,rows=rows)
        pair[1]=exact.compose(pair[1]);tables.append(pair);exact_geometry=exact
        for name,shape in SHAPES.items():
            value=np.asarray([net[name] for net in model['networks']],dtype=np.float32)
            if value.size!=2*int(np.prod(shape)) or not np.isfinite(value).all():raise ValueError('Invalid parameters')
            parameters[name].append(value.reshape(2,*shape))
    return dict(context_source=context_source,tables=tables,exact_geometry=exact_geometry,count=completed_iterations,
        weights=weights.copy(),parameters={name:np.stack(values).astype(np.float64) for name,values in parameters.items()})


def validate_queries(layout,queries):
    if queries['context_source']!=layout['context_source']:raise ValueError('Query context mismatch')
    observations=queries['observations']
    if not observations:raise ValueError('Nonempty observations required')
    for o in observations:
        if int(o['hi'])==1 and (o['actor']!=0 or o['own_history']!=[]):
            raise ValueError('Root must have no own-action ancestors')
    layout['exact_geometry'].validate_queries(observations)
