"""Original full checkpoint checks with the qualified batched reservoir loader."""
import json
from pathlib import Path
import numpy as np
import weighted_training_checkpoint_v1 as base
from weighted_reservoir_bulk_load_v1 import load


def restore_checkpoint(directory,reference,config,*,guard=lambda:None,**args):
    guard();base.require_config(config)
    value=json.loads(base.storage.read_object(directory,reference))
    if (value.get('format')!=1 or value.get('policy_type')!=base.POLICY_TYPE
            or value.get('config_sha256')!=base.storage.digest(base.storage.encoded(config).decode())
            or base.storage.encoded(value['config'])!=base.storage.encoded(config)
            or value.get('context_sha256')!=base.storage.digest(args['context_source'])
            or value.get('catalog_sha256')!=base.storage.digest(args['catalog_source'])
            or value.get('matrix_sha256')!=args['matrix_sha256']):
        raise ValueError('Weighted checkpoint identity changed')
    rng=np.random.Generator(np.random.PCG64(0));rng.bit_generator.state=value['action_rng']
    reservoirs=[]
    for ref in value['reservoirs']:
        guard();base.storage.read_object(directory,ref)
        reservoirs.append(load(Path(directory)/ref['file'],args['context_source'],guard=guard))
    guard();model=base.model_document(directory,value['next_model'],**args)
    root,exact,_=base.validate_model(model,**args)
    state=dict(completed_iterations=value['completed_iterations'],
        sampler=base.ClassStratifiedDeals.restore(value['sampler'],args['context_source']),action_rng=rng,
        reservoirs=reservoirs,played_bank=value['played_bank'],next_model=value['next_model'],
        root_regret_state=root,exact_btn_state=exact)
    # Retain full historical model validation and reconstruction of the current
    # weighted tables. No cached assertion or metadata substitutes for these.
    guard();base.validate_state(directory,state,config,**args);guard()
    return state
