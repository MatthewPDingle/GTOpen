"""Complete joint-context checkpoints; never publish a partial collection cycle.

Each context owns its physical/action/reservoir random state and root updates.
The shared networks are fitted once per actor after collecting every context
against the same frozen played model. Adam is fresh per fit, not persistent.
"""
import copy
import json
from pathlib import Path
import re
import uuid
import numpy as np
import sampled_visible_hybrid_checkpoint_v1 as storage
import stack_context_full_policy_v1 as full
import stack_context_policy_v1 as base
import stack_context_relative_policy_v1 as relative
from stack_context_training_fit_v1 import RUNTIME,INITIALIZATION,OPTIMIZER
from stack_context_fit_rows_v1 import METHOD
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_preflop_table_v1 import build
from board_root_accumulator_v1 import BoardRootRegrets,CHANCE
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets

TYPE='complete-joint-context-training-checkpoint-v1'
SCALE='advantage_bb / context_starting_stack'


def hash_document(value):
    return storage.digest(storage.encoded(value).decode())


def require_config(config,registry,resources):
    required={'format','checkpoint_type','registry_sha256','representation','target_units','fit_runtime',
              'objective_method','initialization','optimizer','device','current_policy_inference',
              'fit_steps','chunk_size','learning_rate','fit_seed_base','context_order','context_weights',
              'contexts','source_identities'}
    if (set(config)!=required or config['format']!=1 or config['checkpoint_type']!=TYPE
            or config['registry_sha256']!=registry.sha256 or config['representation']!=registry.manifest['representation']
            or config['target_units']!=SCALE or config['fit_runtime']!=RUNTIME or config['objective_method']!=METHOD
            or config['initialization']!=INITIALIZATION or config['optimizer']!=OPTIMIZER
            or config['device']!='cuda' or config['current_policy_inference']!='float64-widened-float32-weights-v1'):
        raise ValueError('Explicit complete context-training configuration required')
    expected=set(registry.fit_contexts)
    if (config['context_order']!=list(registry.fit_contexts) or set(config['contexts'])!=expected
            or set(config['context_weights'])!=expected or set(resources)!=expected):
        raise ValueError('All fitting contexts, fixed order and resource identities required')
    weights=np.asarray([config['context_weights'][k] for k in registry.fit_contexts],dtype=float)
    if not np.isfinite(weights).all() or np.any(weights<=0) or abs(float(weights.sum())-1)>1e-12:
        raise ValueError('Fixed positive normalized context weights required')
    for name in ('fit_steps','chunk_size'):
        if type(config[name]) is not int or config[name]<1:raise ValueError('Positive '+name+' required')
    if type(config['fit_seed_base']) is not int or not 0<=config['fit_seed_base']<2**63:
        raise ValueError('Bounded explicit fit seed required')
    if type(config['learning_rate']) not in (int,float) or not np.isfinite(config['learning_rate']) or config['learning_rate']<=0:
        raise ValueError('Finite positive learning rate required')
    sources=config['source_identities']
    if not isinstance(sources,dict) or not sources or any(not isinstance(k,str) or not k or not isinstance(v,str)
            or re.fullmatch('[0-9a-f]{64}',v) is None for k,v in sources.items()):
        raise ValueError('Registered immutable source identities required')
    for key in registry.fit_contexts:
        c=config['contexts'][key]
        if set(c)!={'sampler_seed','action_seed','reservoir_seeds','reservoir_capacity','deals_per_generation',
                    'deals_per_subbatch','query_limit','board_root','allin_cache_sha256','river_targets'}:
            raise ValueError('Complete local sampling and target configuration required')
        for name in ('sampler_seed','action_seed'):
            if type(c[name]) is not int or not 0<=c[name]<2**63:raise ValueError('Explicit local RNG seed required')
        if len(c['reservoir_seeds'])!=2 or any(type(s) is not int or not 0<=s<2**63 for s in c['reservoir_seeds']):
            raise ValueError('Two explicit local reservoir seeds required')
        for name in ('reservoir_capacity','deals_per_generation','deals_per_subbatch','query_limit'):
            if type(c[name]) is not int or c[name]<1:raise ValueError('Positive local '+name+' required')
        if not 169<=c['deals_per_generation']<=65536 or c['deals_per_generation']%c['deals_per_subbatch']:
            raise ValueError('Complete sliced stratified generation required')
        if not isinstance(c['allin_cache_sha256'],str) or re.fullmatch('[0-9a-f]{64}',c['allin_cache_sha256']) is None:
            raise ValueError('Exact all-in cache identity required')
        from river_weighted_overlay_ingest_v1 import METHOD as RIVER
        if c['river_targets']!={'method':RIVER,'K':64}:raise ValueError('Explicit posterior64 continuation targets required')
        root=dict(c['board_root'])
        if root.pop('chance',None)!=CHANCE or c['board_root']!=resources[key]['root_config']:
            raise ValueError('Wrong board-root algorithm or context configuration')
        BoardRootRegrets(**root)
        if (root['physical_budget']!=c['deals_per_generation'] or root['context_sha256']!=key
                or root['matrix_sha256']!=resources[key]['matrix_sha256']):
            raise ValueError('Local board and physical budgets/identities disagree')


def local_document(state,args):
    return full.local_document(catalog_source=args['catalog_source'],matrix_sha256=args['matrix_sha256'],
        root_config=args['root_config'],root=state['root_regret_state'],exact=state['exact_btn_state'])


def initialize(directory,config,registry,resources):
    require_config(config,registry,resources);local={}
    for key in registry.fit_contexts:
        c=config['contexts'][key];source=registry.source(key);root=dict(c['board_root']);root.pop('chance')
        local[key]=dict(sampler=ClassStratifiedDeals(source,seed=c['sampler_seed']),
            action_rng=np.random.Generator(np.random.PCG64(c['action_seed'])),
            reservoirs=[WeightedPhysicalReservoir(c['reservoir_capacity'],p,c['reservoir_seeds'][p],source) for p in (0,1)],
            root_regret_state=BoardRootRegrets(**root),exact_btn_state=ExactBtnRegrets(key,resources[key]['entry_mass']))
    api=relative if registry.manifest['representation']['input_width']==387 else base
    value=full.model(registry,api.initial(registry),{k:local_document(s,resources[k]) for k,s in local.items()},resources)
    reference=full.write_model(directory,value,registry,resources)
    return dict(completed_cycles=0,contexts=local,played_bank=[],next_model=reference)


def validate_state(directory,state,config,registry,resources):
    require_config(config,registry,resources)
    if set(state)!={'completed_cycles','contexts','played_bank','next_model'}:
        raise ValueError('Only complete joint-cycle state is checkpointable')
    completed=state['completed_cycles']
    if type(completed) is not int or completed<0 or len(state['played_bank'])!=completed:
        raise ValueError('Complete played bank excludes the final unplayed model')
    if set(state['contexts'])!=set(registry.fit_contexts):raise ValueError('Missing or extra context state')
    for generation,reference in enumerate([*state['played_bank'],state['next_model']]):
        model=full.read_model(directory,reference,registry,resources)
        if model['generation']!=generation:raise ValueError('Reordered, missing or unplayed generation')
    for key,local in state['contexts'].items():
        if set(local)!={'sampler','action_rng','reservoirs','root_regret_state','exact_btn_state'}:
            raise ValueError('Complete local state required')
        c=config['contexts'][key];sampler=local['sampler']
        if (not isinstance(sampler,ClassStratifiedDeals) or sampler.base.context_sha256!=key
                or sampler.batches!=completed or sampler.base.draws!=completed*c['deals_per_generation']):
            raise ValueError('All samplers must be at the same completed joint cycle')
        if not isinstance(local['action_rng'],np.random.Generator) or local['action_rng'].bit_generator.state['bit_generator']!='PCG64':
            raise ValueError('Local PCG64 action state required')
        if len(local['reservoirs'])!=2:raise ValueError('Both actor reservoirs required')
        for actor,r in enumerate(local['reservoirs']):
            if (not isinstance(r,WeightedPhysicalReservoir) or r.context_sha256!=key or r.player!=actor
                    or r.capacity!=c['reservoir_capacity'] or r.rng.bit_generator.state['bit_generator']!='PCG64'
                    or (completed==0 and r.seen!=0) or (completed>0 and r.size==0)
                    or (r.size and (np.any(r.iterations[:r.size]<1) or np.any(r.iterations[:r.size]>completed)))):
                raise ValueError('Wrong local reservoir context, actor, RNG or cycle')
            if completed and storage.encoded(build(r,registry.source(key)))!=storage.encoded(model['shared']['preflop_tables'][key][actor]):
                raise ValueError('Published local table differs from retained targets')
        if local_document(local,resources[key])!=model['local_states'][key]:
            raise ValueError('Published model and local root/exact states differ')
    return model


def save_checkpoint(directory,state,config,registry,resources):
    validate_state(directory,state,config,registry,resources)
    directory=Path(directory).resolve();contexts={}
    for key in registry.fit_contexts:
        local=state['contexts'][key];refs=[]
        for reservoir in local['reservoirs']:
            temporary=directory/('.contextreservoir-'+uuid.uuid4().hex+'.npz')
            reservoir.save(temporary)
            refs.append(storage.publish(directory,'contextreservoir',temporary.read_bytes(),'npz'))
            assert temporary.resolve().parent==directory
            temporary.unlink()
        contexts[key]=dict(sampler=local['sampler'].checkpoint(),action_rng=local['action_rng'].bit_generator.state,reservoirs=refs)
    value=dict(format=1,checkpoint_type=TYPE,config=config,config_sha256=hash_document(config),
        registry=registry.manifest,registry_sha256=registry.sha256,completed_cycles=state['completed_cycles'],
        contexts=contexts,played_bank=state['played_bank'],next_model=state['next_model'],
        boundary='All contexts collected against one frozen played model; both shared fits and all local updates complete.')
    return storage.publish(directory,'jointcontextcheckpoint',storage.encoded(value))


def restore_checkpoint(directory,reference,config,registry,resources):
    require_config(config,registry,resources);value=json.loads(storage.read_object(directory,reference))
    if (value.get('format')!=1 or value.get('checkpoint_type')!=TYPE or value.get('config_sha256')!=hash_document(config)
            or storage.encoded(value.get('config'))!=storage.encoded(config) or value.get('registry')!=registry.manifest
            or value.get('registry_sha256')!=registry.sha256 or set(value['contexts'])!=set(registry.fit_contexts)):
        raise ValueError('Wrong context-training checkpoint identity or configuration')
    model=full.read_model(directory,value['next_model'],registry,resources);contexts={}
    for key in registry.fit_contexts:
        record=value['contexts'][key];rng=np.random.Generator(np.random.PCG64(0));rng.bit_generator.state=record['action_rng']
        reservoirs=[]
        for ref in record['reservoirs']:
            storage.read_object(directory,ref)
            reservoirs.append(WeightedPhysicalReservoir.load(Path(directory)/ref['file'],registry.source(key)))
        local=model['local_states'][key]
        contexts[key]=dict(sampler=ClassStratifiedDeals.restore(record['sampler'],registry.source(key)),action_rng=rng,
            reservoirs=reservoirs,root_regret_state=BoardRootRegrets.restore(local['board_root_state'],expected_config=resources[key]['root_config']),
            exact_btn_state=ExactBtnRegrets.restore(local['exact_btn_state'],context_sha256=key,entry_mass=resources[key]['entry_mass']))
    state=dict(completed_cycles=value['completed_cycles'],contexts=contexts,played_bank=value['played_bank'],next_model=value['next_model'])
    validate_state(directory,state,config,registry,resources)
    return state


def complete_cycle(directory,previous,staged,config,registry,resources,*,networks,on_stage=lambda stage:None):
    """Return a published complete state; never mutate the caller's live state.

Collectors must record the actual shared model identity per context. The
worker integration must additionally verify its native target provenance.
Immutable orphan objects after an interruption are not resume checkpoints.
"""
    validate_state(directory,previous,config,registry,resources)
    if set(staged)!={'contexts','collected_against'} or set(staged['contexts'])!=set(registry.fit_contexts):
        raise ValueError('Every fitting context must be collected before fitting/publication')
    expected={k:previous['next_model']['sha256'] for k in registry.fit_contexts}
    if staged['collected_against']!=expected:
        raise ValueError('All contexts must use the same frozen played model')
    local=copy.deepcopy(staged['contexts']);generation=previous['completed_cycles']+1
    api=relative if registry.manifest['representation']['input_width']==387 else base
    shared=api.model(registry,generation=generation,networks=networks,
        preflop_tables={k:[build(r,registry.source(k)) for r in s['reservoirs']] for k,s in local.items()})
    model=full.model(registry,shared,{k:local_document(s,resources[k]) for k,s in local.items()},resources)
    on_stage('before-model-publication')
    reference=full.write_model(directory,model,registry,resources)
    candidate=dict(completed_cycles=generation,contexts=local,played_bank=[*previous['played_bank'],previous['next_model']],next_model=reference)
    validate_state(directory,candidate,config,registry,resources)
    on_stage('before-checkpoint-publication')
    checkpoint=save_checkpoint(directory,candidate,config,registry,resources)
    on_stage('checkpoint-published')
    return candidate,checkpoint
