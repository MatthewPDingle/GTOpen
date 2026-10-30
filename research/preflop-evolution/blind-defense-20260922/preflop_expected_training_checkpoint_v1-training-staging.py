"""Complete all-node preflop/shared-postflop training-cycle transactions.

New-format research checkpoints only; original comparison/checkpoints untouched.
Board targets are replay-checked against the same frozen played model. Both fits,
all cumulative states and sampler/action/reservoir RNGs publish together. This
module does not authenticate an external native worker or execute fitting.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import uuid

import numpy as np

import preflop_expected_policy_v1 as policy
from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets
from preflop_expected_native_targets_v2 import FrozenExpectedTargets
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir, ARRAYS, checked_weight
from sampled_physical_reservoir_v1 import checked_row
from river_weighted_overlay_ingest_v1 import METHOD as RIVER_METHOD
import sampled_visible_hybrid_checkpoint_v1 as storage
from board_root_accumulator_v1 import integer, identity
from stack_context_full_policy_v1 import interface

TYPE = 'complete-all-node-context-training-checkpoint-v1'
FIT_METHOD = 'dense-cumulative-preflop-and-sampled-postflop-objective-v1'
RUNTIME = 'dense-preflop-postflop-ordered-cuda-gradient-v1'
INITIALIZATION = 'seeded-visible-base-zero-public-and-relative-columns-v1'
OPTIMIZER = dict(name='Adam', betas=[.9, .999], eps=1e-8, weight_decay=0.,
    amsgrad=False, foreach=False, fused=False,
    lifecycle='fresh seeded network and optimizer for each player fit')
DENSE_RECIPE = dict(method='class-complete-cumulative-preflop-targets-v1',
    target='regret / (generation_scale * source_class_mass * completed_updates * starting_stack)',
    support='positive source class mass and at least one supported counterfactual generation',
    loss_weight='source_class_mass per supported node/class/legal-action')
SCALE = 'advantage_bb / context_starting_stack'
LOCAL_FIELDS = {'sampler', 'action_rng', 'reservoirs', 'preflop_state'}
BOUNDARY = 'All fitted contexts, both networks, every cumulative node and sampling/retention stream complete'


def hash_document(value):
    return hashlib.sha256(storage.encoded(value)).hexdigest()


def require_config(config, registry, resources):
    required = {'format', 'checkpoint_type', 'execution_mode', 'registry_sha256', 'representation',
        'target_units', 'fit_runtime', 'objective_method', 'preflop_fit_recipe', 'preflop_fraction',
        'initialization', 'optimizer', 'device', 'current_policy_inference', 'fit_steps', 'chunk_size',
        'learning_rate', 'fit_seed_base', 'context_order', 'context_weights', 'contexts', 'source_identities'}
    if (not isinstance(config, dict) or set(config) != required
            or type(config['format']) is not int or config['format'] != 1
            or config['checkpoint_type'] != TYPE or config['execution_mode'] not in ('study', 'software-control')
            or config['registry_sha256'] != registry.sha256
            or config['representation'] != registry.manifest['representation']
            or config['target_units'] != SCALE or config['fit_runtime'] != RUNTIME
            or config['objective_method'] != FIT_METHOD or config['preflop_fit_recipe'] != DENSE_RECIPE
            or config['initialization'] != INITIALIZATION or config['optimizer'] != OPTIMIZER
            or config['device'] != 'cuda'
            or config['current_policy_inference'] != 'float64-widened-float32-weights-v1'):
        raise ValueError('Explicit new all-node training configuration required')
    keys = set(registry.fit_contexts)
    if (config['context_order'] != list(registry.fit_contexts) or set(config['contexts']) != keys
            or set(config['context_weights']) != keys or set(resources) != keys):
        raise ValueError('Exactly all fitted contexts and fixed collection order required')
    weights = np.array([config['context_weights'][k] for k in registry.fit_contexts])
    if not np.isfinite(weights).all() or np.any(weights <= 0) or abs(float(weights.sum())-1) > 1e-12:
        raise ValueError('Fixed positive normalized context weights required')
    if (type(config['preflop_fraction']) not in (int, float)
            or not np.isfinite(config['preflop_fraction']) or not 0 < config['preflop_fraction'] < 1):
        raise ValueError('Explicit fixed positive preflop/postflop mixture required')
    integer(config['fit_steps'], 1, 1_000_000); integer(config['chunk_size'], 1, 1_000_000)
    integer(config['fit_seed_base'], 0, 2**63-1)
    if (type(config['learning_rate']) not in (int, float)
            or not np.isfinite(config['learning_rate']) or config['learning_rate'] <= 0):
        raise ValueError('Finite positive learning rate required')
    sources = config['source_identities']
    if not isinstance(sources, dict) or not sources or any(not isinstance(k, str) or not k
            or not isinstance(v, str) or re.fullmatch('[0-9a-f]{64}', v) is None for k, v in sources.items()):
        raise ValueError('Immutable source identities required')
    for key in registry.fit_contexts:
        c, args = config['contexts'][key], resources[key]
        if set(c) != {'sampler_seed', 'action_seed', 'reservoir_seeds', 'reservoir_capacity',
                'deals_per_generation', 'deals_per_subbatch', 'query_limit', 'expected_preflop',
                'allin_cache_sha256', 'river_targets'}:
            raise ValueError('Explicit local sampler, postflop and cumulative budgets required')
        if set(args) != policy.RESOURCE_FIELDS or c['expected_preflop'] != args['expected_config']:
            raise ValueError('Resource/configuration mismatch')
        integer(c['sampler_seed'], 0, 2**63-1); integer(c['action_seed'], 0, 2**63-1)
        if type(c['reservoir_seeds']) is not list or len(c['reservoir_seeds']) != 2:
            raise ValueError('Two postflop retention RNG streams required')
        for seed in c['reservoir_seeds']: integer(seed, 0, 2**63-1)
        integer(c['reservoir_capacity'], 1, 2**24)
        integer(c['deals_per_generation'], 169, 65536)
        integer(c['deals_per_subbatch'], 1, c['deals_per_generation']); integer(c['query_limit'], 1, 10_000_000)
        if c['deals_per_generation'] % c['deals_per_subbatch']:
            raise ValueError('Complete sliced source-deal generations required')
        identity(c['allin_cache_sha256'])
        if c['river_targets'] != {'method': RIVER_METHOD, 'K':64}:
            raise ValueError('Explicit existing posterior-64 river target contract required')
        expected = PreflopExpectedRegrets(context_source=registry.source(key), matrix_source=args['matrix_source'],
            generation_scale=c['expected_preflop']['generation_scale'],
            boards_per_generation=c['expected_preflop']['boards_per_generation'],
            board_seed=c['expected_preflop']['board_seed'])
        if expected.config != c['expected_preflop']:
            raise ValueError('Unqualified cumulative context/matrix/runtime configuration')


def local_fit_identity(local):
    """Identity of the actual cumulative targets and all retained postflop data."""
    h = hashlib.sha256(storage.encoded(local['preflop_state'].document()))
    for r in local['reservoirs']:
        h.update(storage.encoded(dict(player=r.player, context_sha256=r.context_sha256,
            capacity=r.capacity, seen=r.seen, rng=r.rng.bit_generator.state)))
        for name in ARRAYS:
            a = getattr(r, name)[:r.size]
            h.update(name.encode()); h.update(str(a.dtype).encode()); h.update(storage.encoded(list(a.shape)))
            h.update(a.tobytes(order='C'))
    return h.hexdigest()


def initialize(directory, config, registry, resources):
    require_config(config, registry, resources)
    local = {}
    for key in registry.fit_contexts:
        c = config['contexts'][key]; source = registry.source(key); p = c['expected_preflop']
        local[key] = dict(sampler=ClassStratifiedDeals(source, seed=c['sampler_seed']),
            action_rng=np.random.Generator(np.random.PCG64(c['action_seed'])),
            reservoirs=[WeightedPhysicalReservoir(c['reservoir_capacity'], actor, c['reservoir_seeds'][actor], source)
                        for actor in (0, 1)],
            preflop_state=PreflopExpectedRegrets(context_source=source, matrix_source=resources[key]['matrix_source'],
                generation_scale=p['generation_scale'], boards_per_generation=p['boards_per_generation'], board_seed=p['board_seed']))
    import stack_context_policy_v1 as base
    import stack_context_relative_policy_v1 as relative
    api = relative if registry.manifest['representation']['input_width'] == 387 else base
    value = policy.model(registry, api.initial(registry), {k:s['preflop_state'] for k, s in local.items()}, resources)
    ref = policy.write_model(directory, value, registry, resources)
    return dict(completed_cycles=0, contexts=local, played_bank=[], next_model=ref)


def validate_local(local, completed, config, registry, resources, model):
    if set(local) != set(registry.fit_contexts): raise ValueError('Every fitting context required')
    states = policy.validate(model, registry, resources)
    for key, s in local.items():
        if set(s) != LOCAL_FIELDS: raise ValueError('Complete new-format local state required')
        c = config['contexts'][key]; source = registry.source(key); sampler = s['sampler']
        if (not isinstance(sampler, ClassStratifiedDeals) or sampler.base.context_sha256 != key
                or sampler.batches != completed or sampler.base.draws != completed*c['deals_per_generation']):
            raise ValueError('Every sampler must reach the same completed cycle')
        if (not isinstance(s['preflop_state'], PreflopExpectedRegrets)
                or s['preflop_state'].document() != states[key].document()):
            raise ValueError('Played model and all cumulative targets differ')
        if (not isinstance(s['action_rng'], np.random.Generator)
                or s['action_rng'].bit_generator.state['bit_generator'] != 'PCG64'):
            raise ValueError('Explicit PCG64 action stream required')
        if len(s['reservoirs']) != 2: raise ValueError('Both actor postflop reservoirs required')
        for actor, r in enumerate(s['reservoirs']):
            if (not isinstance(r, WeightedPhysicalReservoir) or r.player != actor or r.context_sha256 != key
                    or r.capacity != c['reservoir_capacity'] or r.rng.bit_generator.state['bit_generator'] != 'PCG64'
                    or type(r.seen) is not int or not 0 <= r.seen < 2**63
                    or (completed == 0 and r.seen != 0) or (completed > 0 and r.size == 0)
                    or (r.size and (np.any(r.iterations[:r.size] < 1) or np.any(r.iterations[:r.size] > completed)))
                    or np.any(r.keys[:r.size, 0] < 1 << 63)):
                raise ValueError('Matching postflop-only retained visits and bounded iteration labels required')
            geometry = dict(keys=(np.dtype('uint64'), (r.capacity, 2)),
                active=(np.dtype('uint16'), (r.capacity, 36)), arity=(np.dtype('uint8'), (r.capacity,)),
                values=(np.dtype('float64'), (r.capacity, 4)), iterations=(np.dtype('uint64'), (r.capacity,)),
                deal_weights=(np.dtype('float64'), (r.capacity,)))
            for name, (dtype, shape) in geometry.items():
                a = getattr(r, name)
                if not isinstance(a, np.ndarray) or a.dtype != dtype or a.shape != shape or np.any(a[r.size:]):
                    raise ValueError('Canonical reservoir allocation, dtype and unused tail required')
            if r.size:
                observations = []
                for j in range(r.size):
                    active = r.active[j].astype(int).tolist()
                    phase = [v-135 for v in active if 135 <= v < 139]
                    if len(phase) != 1 or phase[0] not in (1, 2, 3):
                        raise ValueError('Retained row needs a real postflop phase')
                    observations.append(dict(hi=str(int(r.keys[j, 0])), lo=str(int(r.keys[j, 1])),
                        actor=actor, phase=phase[0], n=int(r.arity[j]), active_features=active))
                    checked_row(observations[-1], r.values[j]); checked_weight(r.deal_weights[j])
                # State/catalog/model authentication already occurred above. Only
                # checked visible inputs are needed here; do not infer all preflop
                # policies just to validate a postflop row's public geometry.
                from preflop_expected_training_fit_v1 import visible_inputs
                visible_inputs(registry, key, observations)
        if completed == 0:
            if (sampler.checkpoint() != ClassStratifiedDeals(source, seed=c['sampler_seed']).checkpoint()
                    or s['action_rng'].bit_generator.state != np.random.PCG64(c['action_seed']).state
                    or any(r.rng.bit_generator.state != np.random.PCG64(c['reservoir_seeds'][actor]).state
                           for actor, r in enumerate(s['reservoirs']))):
                raise ValueError('Initial independent RNG streams must match their registered seeds')


def validate_state(directory, state, config, registry, resources):
    require_config(config, registry, resources)
    if set(state) != {'completed_cycles', 'contexts', 'played_bank', 'next_model'}:
        raise ValueError('Only complete new-format cycles are checkpointable')
    completed = integer(state['completed_cycles'], 0, 1_000_000)
    if len(state['played_bank']) != completed:
        raise ValueError('Played prefix must exclude final unplayed model')
    value = None; histories = {k:[] for k in registry.fit_contexts}
    for generation, ref in enumerate([*state['played_bank'], state['next_model']]):
        value = policy.read_model(directory, ref, registry, resources)
        if value['generation'] != generation: raise ValueError('Reordered or incomplete model bank')
        for key in registry.fit_contexts:
            history = value['local_states'][key]['cumulative_state']['history']
            if generation and (history[:-1] != histories[key]
                    or history[-1]['model_sha256'] != state['played_bank'][generation-1]['sha256']):
                raise ValueError('Cumulative history must extend the actual previous played model')
            histories[key] = history
    validate_local(state['contexts'], completed, config, registry, resources, value)
    return value


def save_checkpoint(directory, state, config, registry, resources):
    validate_state(directory, state, config, registry, resources)
    directory = Path(directory).resolve(); contexts = {}
    for key in registry.fit_contexts:
        s = state['contexts'][key]; refs = []
        for r in s['reservoirs']:
            temporary = directory/('.postflop-reservoir-'+uuid.uuid4().hex+'.npz')
            r.save(temporary)
            refs.append(storage.publish(directory, 'postflopreservoir', temporary.read_bytes(), 'npz'))
            assert temporary.resolve().parent == directory
            temporary.unlink()
        contexts[key] = dict(sampler=s['sampler'].checkpoint(),
            action_rng=copy.deepcopy(s['action_rng'].bit_generator.state), reservoirs=refs)
    value = dict(format=1, checkpoint_type=TYPE, config=copy.deepcopy(config), config_sha256=hash_document(config),
        registry=registry.manifest, registry_sha256=registry.sha256, completed_cycles=state['completed_cycles'],
        contexts=contexts, played_bank=copy.deepcopy(state['played_bank']), next_model=copy.deepcopy(state['next_model']),
        boundary=BOUNDARY)
    return storage.publish(directory, 'expectedcontextcheckpoint', storage.encoded(value))


def restore_checkpoint(directory, reference, config, registry, resources):
    require_config(config, registry, resources)
    value = json.loads(storage.read_object(directory, reference))
    if (set(value) != {'format', 'checkpoint_type', 'config', 'config_sha256', 'registry', 'registry_sha256',
                'completed_cycles', 'contexts', 'played_bank', 'next_model', 'boundary'}
            or type(value['format']) is not int or value['format'] != 1 or value['checkpoint_type'] != TYPE
            or value['boundary'] != BOUNDARY
            or value['config_sha256'] != hash_document(config) or value['config'] != config
            or value['registry'] != registry.manifest or value['registry_sha256'] != registry.sha256
            or set(value['contexts']) != set(registry.fit_contexts)):
        raise ValueError('Changed registry, objective, budgets, runtime or checkpoint contract')
    model = policy.read_model(directory, value['next_model'], registry, resources)
    expected = policy.validate(model, registry, resources); local = {}
    for key in registry.fit_contexts:
        record = value['contexts'][key]
        if set(record) != {'sampler', 'action_rng', 'reservoirs'} or len(record['reservoirs']) != 2:
            raise ValueError('Complete local checkpoint references required')
        rng = np.random.Generator(np.random.PCG64(0)); rng.bit_generator.state = record['action_rng']
        reservoirs = []
        for ref in record['reservoirs']:
            storage.read_object(directory, ref)
            reservoirs.append(WeightedPhysicalReservoir.load(Path(directory)/ref['file'], registry.source(key)))
        local[key] = dict(sampler=ClassStratifiedDeals.restore(record['sampler'], registry.source(key)),
            action_rng=rng, reservoirs=reservoirs, preflop_state=expected[key])
    state = dict(completed_cycles=value['completed_cycles'], contexts=local,
        played_bank=value['played_bank'], next_model=value['next_model'])
    validate_state(directory, state, config, registry, resources)
    return state


def require_fits(receipts, networks, staged, previous, config, registry, resources):
    from preflop_expected_training_fit_v1 import prepare
    generation = previous['completed_cycles']+1
    if type(receipts) is not list or len(receipts) != 2 or type(networks) is not list or len(networks) != 2:
        raise ValueError('Both complete actor fits required')
    target_ids = {k:local_fit_identity(staged['contexts'][k]) for k in registry.fit_contexts}
    for actor, (receipt, net) in enumerate(zip(receipts, networks)):
        expected = dict(execution_mode=config['execution_mode'], player=actor, generation=generation,
            collected_against=previous['next_model']['sha256'], registry_sha256=registry.sha256,
            local_fit_identities=target_ids, network_sha256=hash_document(net), objective_method=FIT_METHOD,
            fit_runtime=RUNTIME, target_units=SCALE, preflop_fit_recipe=DENSE_RECIPE,
            preflop_fraction=config['preflop_fraction'], context_weights=config['context_weights'],
            seed=config['fit_seed_base']+generation*200003+actor, steps=config['fit_steps'],
            learning_rate=config['learning_rate'], chunk_size=config['chunk_size'],
            initialization=INITIALIZATION, optimizer=OPTIMIZER, device='cuda')
        if not isinstance(receipt, dict) or set(receipt) != set(expected)|{'objective_sha256'}:
            raise ValueError('Explicit complete fit identity required')
        if any(receipt[k] != v for k, v in expected.items()):
            raise ValueError('Fits must use the actual joint collected targets and registered recipe')
        objective = prepare(registry, staged['contexts'], resources, player=actor,
            context_weights=config['context_weights'], preflop_fraction=config['preflop_fraction'])
        if receipt['objective_sha256'] != objective['objective_sha256']:
            raise ValueError('Fit objective differs from the complete dense/sampled target calculation')


def complete_cycle(directory, previous, staged, config, registry, resources, *, networks, fit_receipts,
                   on_stage=lambda stage:None):
    """Immutable model then complete checkpoint; never mutate live caller state.

The runner publishes its resume pointer after its complete collection/fit result
exists. Immutable orphan objects are retained but are not restart boundaries.
Native worker provenance must additionally be authenticated by that runner.
"""
    prior = validate_state(directory, previous, config, registry, resources)
    if (set(staged) != {'contexts', 'collected_against', 'board_targets'}
            or set(staged['contexts']) != set(registry.fit_contexts)
            or set(staged['board_targets']) != set(registry.fit_contexts)
            or staged['collected_against'] != {k:previous['next_model']['sha256'] for k in registry.fit_contexts}):
        raise ValueError('Complete collection against one frozen played model required')
    # Independently replay each complete target generation from the prior state.
    for key in registry.fit_contexts:
        target = staged['board_targets'][key]
        if set(target) != {'plan', 'evidence', 'recipe'}:
            raise ValueError('Complete frozen target recipe and evidence required')
        provider = FrozenExpectedTargets(state=previous['contexts'][key]['preflop_state'],
            model_source=storage.read_object(directory, previous['next_model']).decode(), registry=registry, resources=resources)
        if (target['recipe'] != provider.recipe
                or target['evidence'] != provider.generation_evidence(previous['contexts'][key]['preflop_state'],
                    target['plan'], target['evidence']['draws'])):
            raise ValueError('Board evidence detached from actual frozen model/recipe')
        replay = copy.deepcopy(previous['contexts'][key]['preflop_state'])
        replay.step(target['plan'], target['evidence'], played_policy=provider.played_preflop())
        if replay.document() != staged['contexts'][key]['preflop_state'].document():
            raise ValueError('Staged cumulative update differs from replayed complete evidence')
    local = copy.deepcopy(staged['contexts']); generation = previous['completed_cycles']+1
    api = interface(prior['shared'])
    shared = api.model(registry, generation=generation, networks=networks,
                       preflop_tables={k:[None, None] for k in registry.fit_contexts})
    value = policy.model(registry, shared, {k:s['preflop_state'] for k, s in local.items()}, resources)
    validate_local(local, generation, config, registry, resources, value)
    require_fits(fit_receipts, networks, staged, previous, config, registry, resources)
    on_stage('before-model-publication')
    ref = policy.write_model(directory, value, registry, resources)
    candidate = dict(completed_cycles=generation, contexts=local,
        played_bank=[*previous['played_bank'], previous['next_model']], next_model=ref)
    on_stage('before-checkpoint-publication')
    checkpoint = save_checkpoint(directory, candidate, config, registry, resources)
    on_stage('checkpoint-published')
    return candidate, checkpoint
