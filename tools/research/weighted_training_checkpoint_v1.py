"""Complete typed checkpoint for stratified physical-deal training.

No nested unweighted checkpoint or model is used to carry weighted state.
"""
import json
from pathlib import Path
import uuid
import numpy as np
import sampled_visible_hybrid_checkpoint_v1 as storage
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_preflop_table_v1 import Table, build
from weighted_root_accumulator_v1 import WeightedRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from exact_btn_policy_table_v1 import document as exact_document, ExactBtnTable

POLICY_TYPE = 'class-stratified-weighted-physical-poker-v1'
FIT = 'source-deal-weighted-ordered-gradient-v1'


def require_config(config):
    storage.validate_config(config)
    if (config.get('policy_type') != POLICY_TYPE or config.get('fit_implementation') != FIT
            or config.get('device') != 'cuda'
            or config.get('current_policy_inference') != 'float64-widened-float32-weights-v1'):
        raise ValueError('Explicit weighted training configuration required')
    for k in ('deals_per_generation','deals_per_subbatch','fit_steps','chunk_size','reservoir_capacity','query_limit'):
        if type(config.get(k)) is not int or config[k] < 1: raise ValueError('Positive integer '+k+' required')
    if not 169 <= config['deals_per_generation'] <= 65536 or config['deals_per_generation'] % config['deals_per_subbatch']:
        raise ValueError('Complete evenly sliced class-stratified generation required')
    for k in ('sampler_seed','action_seed','fit_seed_base'):
        if type(config.get(k)) is not int or config[k] < 0: raise ValueError('Explicit integer seed required')
    if len(config.get('reservoir_seeds',[])) != 2 or any(type(s) is not int or s < 0 for s in config['reservoir_seeds']):
        raise ValueError('Two reservoir seeds required')
    if type(config.get('learning_rate')) not in (int,float) or not np.isfinite(config['learning_rate']) or config['learning_rate'] <= 0:
        raise ValueError('Finite positive learning rate required')


def validate_model(value, *, context_source, catalog_source, matrix_sha256, entry_mass):
    if (value.get('format') != 1 or value.get('policy_type') != POLICY_TYPE
            or value.get('context_sha256') != storage.digest(context_source)
            or value.get('catalog_sha256') != storage.digest(catalog_source)
            or value.get('matrix_sha256') != matrix_sha256 or value.get('fit_implementation') != FIT
            or value.get('representation') != storage.FEATURE_SPEC):
        raise ValueError('Wrong weighted model identity')
    storage.validate_network_pair(value)
    root = WeightedRootRegrets.restore(value['root_state'],context_sha256=storage.digest(context_source),matrix_sha256=matrix_sha256)
    exact = ExactBtnRegrets.restore(value['exact_btn_state'],context_sha256=storage.digest(context_source),entry_mass=entry_mass)
    exact_table = ExactBtnTable(exact_document(exact,context_source=context_source,catalog_source=catalog_source,
        matrix_sha256=matrix_sha256),context_source,catalog_source,matrix_sha256=matrix_sha256,entry_mass=entry_mass)
    if root.steps != value['generation'] or exact.steps != value['generation']:
        raise ValueError('Exactly one root and exact BTN update per generation required')
    tables = value['preflop_tables']
    if not isinstance(tables,list) or len(tables) != 2: raise ValueError('Two table slots required')
    if value['generation'] == 0:
        if tables != [None,None]: raise ValueError('Initial model must be uniform')
    else:
        for p,t in enumerate(tables):
            if t is None or Table(t,context_source).player != p: raise ValueError('Missing weighted player table')
            s = t['source_reservoir']
            if (s['player'] != p or s['context_sha256'] != storage.digest(context_source)
                    or s.get('method') != 'physical-visit-reservoir-with-deal-weights-v1'
                    or sum(r['count'] for r in t['rows']) > s['retained']):
                raise ValueError('Invalid weighted table source')
    return root,exact,exact_table


def write_model(directory, generation, networks, scales, tables, root, exact, **args):
    value = dict(format=1,policy_type=POLICY_TYPE,fit_implementation=FIT,representation=storage.FEATURE_SPEC,
        context_sha256=storage.digest(args['context_source']),catalog_sha256=storage.digest(args['catalog_source']),
        matrix_sha256=args['matrix_sha256'],generation=generation,networks=networks,advantage_scales=scales,
        preflop_tables=tables,root_state=root.document(),exact_btn_state=exact.document())
    validate_model(value,**args)
    return dict(storage.publish(directory,'weightedmodel',storage.encoded(value)),generation=generation)


def model_document(directory, reference, **args):
    value = json.loads(storage.read_object(directory,reference)); validate_model(value,**args)
    if type(reference['generation']) is not int or value['generation'] != reference['generation']:
        raise ValueError('Model reference generation mismatch')
    return value


def validate_state(directory, state, config, **args):
    require_config(config); completed = state['completed_iterations']
    if type(completed) is not int or completed < 0 or len(state['played_bank']) != completed:
        raise ValueError('Complete played bank required')
    for g,ref in enumerate([*state['played_bank'],state['next_model']]):
        model = model_document(directory,ref,**args)
        if model['generation'] != g or sum(model['root_state']['sample_counts']) != g*config['deals_per_generation']:
            raise ValueError('Played history or root sample budget mismatch')
    sampler = state['sampler']; reservoirs = state['reservoirs']
    if (not isinstance(sampler,ClassStratifiedDeals) or sampler.base.context_sha256 != storage.digest(args['context_source'])
            or sampler.batches != completed or sampler.base.draws != completed*config['deals_per_generation']):
        raise ValueError('Sampler is not at a complete generation boundary')
    if len(reservoirs) != 2: raise ValueError('Two weighted reservoirs required')
    for p,r in enumerate(reservoirs):
        if (not isinstance(r,WeightedPhysicalReservoir) or r.player != p
                or r.context_sha256 != storage.digest(args['context_source']) or r.capacity != config['reservoir_capacity']
                or (r.size and (int(r.iterations[:r.size].max()) > completed or completed == 0))):
            raise ValueError('Reservoir boundary, type, actor or context mismatch')
        if completed and storage.encoded(model['preflop_tables'][p]) != storage.encoded(build(r,args['context_source'])):
            raise ValueError('Current weighted table does not reproduce retained targets')
    if state['action_rng'].bit_generator.state['bit_generator'] != 'PCG64': raise ValueError('PCG64 action RNG required')
    if state['root_regret_state'].document() != model['root_state'] or state['exact_btn_state'].document() != model['exact_btn_state']:
        raise ValueError('Current model disagrees with accumulators')
    return model


def save_checkpoint(directory, state, config, **args):
    validate_state(directory,state,config,**args)
    directory = Path(directory).resolve(); refs = []
    for r in state['reservoirs']:
        temporary = directory/('.weighted-'+uuid.uuid4().hex+'.npz')
        r.save(temporary)
        refs.append(storage.publish(directory,'weightedreservoir',temporary.read_bytes(),'npz'))
        assert temporary.resolve().parent == directory
        temporary.unlink()
    value = dict(format=1,policy_type=POLICY_TYPE,config=config,
        config_sha256=storage.digest(storage.encoded(config).decode()),
        context_sha256=storage.digest(args['context_source']),catalog_sha256=storage.digest(args['catalog_source']),
        matrix_sha256=args['matrix_sha256'],completed_iterations=state['completed_iterations'],
        sampler=state['sampler'].checkpoint(),action_rng=state['action_rng'].bit_generator.state,
        reservoirs=refs,played_bank=state['played_bank'],next_model=state['next_model'],
        boundary='Both fits, weighted root sum and exact BTN update complete; final unplayed model excluded from played_bank.')
    return storage.publish(directory,'weightedcheckpoint',storage.encoded(value))


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
        reservoirs.append(WeightedPhysicalReservoir.load(Path(directory)/ref['file'],args['context_source']))
    model = model_document(directory,value['next_model'],**args)
    root,exact,_ = validate_model(model,**args)
    state = dict(completed_iterations=value['completed_iterations'],
        sampler=ClassStratifiedDeals.restore(value['sampler'],args['context_source']),action_rng=rng,
        reservoirs=reservoirs,played_bank=value['played_bank'],next_model=value['next_model'],
        root_regret_state=root,exact_btn_state=exact)
    validate_state(directory,state,config,**args)
    return state
