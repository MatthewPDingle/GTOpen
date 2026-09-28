"""Separate checkpoint restore with only the reservoir loader substituted."""
import json
from pathlib import Path
import numpy as np
from board_training_checkpoint_v1 import (
    require_config, storage, model_document, validate_model, validate_state, ClassStratifiedDeals, POLICY_TYPE)
from weighted_reservoir_load_vector_v1 import load as load_reservoir


def restore_checkpoint(directory, reference, config, **args):
    require_config(config); value = json.loads(storage.read_object(directory,reference))
    if (value.get('format') != 1 or value.get('policy_type') != POLICY_TYPE
            or value.get('config_sha256') != storage.digest(storage.encoded(config).decode())
            or storage.encoded(value['config']) != storage.encoded(config)
            or value.get('context_sha256') != storage.digest(args['context_source'])
            or value.get('catalog_sha256') != storage.digest(args['catalog_source'])
            or value.get('matrix_sha256') != args['matrix_sha256']):
        raise ValueError('Weighted checkpoint identity changed')
    rng = np.random.Generator(np.random.PCG64(0)); rng.bit_generator.state = value['action_rng']
    reservoirs = []
    for ref in value['reservoirs']:
        storage.read_object(directory,ref)
        reservoirs.append(load_reservoir(Path(directory)/ref['file'],args['context_source']))
    model = model_document(directory,value['next_model'],**args)
    root,exact,_ = validate_model(model,**args)
    state = dict(completed_iterations=value['completed_iterations'],
        sampler=ClassStratifiedDeals.restore(value['sampler'],args['context_source']),action_rng=rng,
        reservoirs=reservoirs,played_bank=value['played_bank'],next_model=value['next_model'],
        root_regret_state=root,exact_btn_state=exact)
    validate_state(directory,state,config,**args)
    return state
