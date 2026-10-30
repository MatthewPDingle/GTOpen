"""Shared context networks plus the existing complete BB/BTN root overrides.

Research integration only: not a trainer, a checkpoint migration, or a qualified
production policy. Generation means a complete cycle over all fitting contexts.
"""
import copy
import json
import numpy as np

import stack_context_policy_v1 as base
import stack_context_relative_policy_v1 as relative
from stack_context_inputs_v1 import digest, encoded
from board_root_accumulator_v1 import BoardRootRegrets
from board_training_policy_v1 import RootTable
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from exact_btn_policy_table_v1 import document as exact_document, ExactBtnTable
from weighted_preflop_table_v1 import Table
from weighted_physical_reservoir_v1 import METHOD as RESERVOIR_METHOD
from sampled_visible_hybrid_checkpoint_v1 import publish, read_object

TYPE = 'stack-context-full-continuation-policy-v1'
ORDER = ['shared_network', 'weighted_preflop', 'exact_btn', 'board_root']
LOCAL_FIELDS = {'catalog_sha256', 'matrix_sha256', 'root_config',
                'board_root_state', 'exact_btn_state'}
RESOURCE_FIELDS = {'catalog_source', 'matrix_sha256', 'entry_mass', 'root_config'}


def interface(shared):
    kind = shared.get('policy_type')
    if kind == base.TYPE:
        return base
    if kind == relative.TYPE:
        return relative
    raise ValueError('Explicit 362-input or 387-input shared policy required')


def local_document(*, catalog_source, matrix_sha256, root_config, root, exact):
    return dict(catalog_sha256=digest(catalog_source), matrix_sha256=matrix_sha256,
                root_config=copy.deepcopy(root_config),
                board_root_state=root.document(), exact_btn_state=exact.document())


def validate(value, registry, resources):
    """Bind every fitted local state before exposing any shared-model result."""
    if (set(value) != {'format', 'policy_type', 'generation', 'shared', 'local_states', 'override_order'}
            or value['format'] != 1 or value['policy_type'] != TYPE
            or value['override_order'] != ORDER):
        raise ValueError('Explicit full continuation model contract required')
    shared = value['shared']
    interface(shared).validate(shared, registry)
    generation = value['generation']
    if type(generation) is not int or generation < 0 or generation != shared['generation']:
        raise ValueError('Shared and local generation boundary mismatch')
    if set(value['local_states']) != set(registry.fit_contexts) or set(resources) != set(registry.fit_contexts):
        raise ValueError('Exactly the fitting contexts require complete local state and resources')
    result = {}
    for key in registry.fit_contexts:
        state, args, source = value['local_states'][key], resources[key], registry.source(key)
        if set(state) != LOCAL_FIELDS or set(args) != RESOURCE_FIELDS:
            raise ValueError('Incomplete local continuation identity')
        config = args['root_config']
        if (state['catalog_sha256'] != digest(args['catalog_source'])
                or state['matrix_sha256'] != args['matrix_sha256']
                or state['root_config'] != config
                or config['context_sha256'] != key
                or config['matrix_sha256'] != args['matrix_sha256']):
            raise ValueError('Local game, catalog, matrix or root configuration changed')
        root = BoardRootRegrets.restore(state['board_root_state'], expected_config=config)
        exact = ExactBtnRegrets.restore(state['exact_btn_state'], context_sha256=key,
                                       entry_mass=args['entry_mass'])
        if (root.steps != generation or exact.steps != generation
                or root.document()['board_draws'] != generation * config['boards_per_generation']):
            raise ValueError('Only complete joint-context cycles may become a played model')
        tables = shared['preflop_tables'][key]
        if generation == 0:
            if tables != [None, None]:
                raise ValueError('Initial local tables must be empty')
        else:
            for actor, table in enumerate(tables):
                if table is None or Table(table, source).player != actor:
                    raise ValueError('Both fitted actors require their weighted preflop tables')
                origin = table['source_reservoir']
                if (origin.get('method') != RESERVOIR_METHOD or origin['player'] != actor
                        or origin['context_sha256'] != key
                        or sum(r['count'] for r in table['rows']) > origin['retained']):
                    raise ValueError('Invalid weighted preflop table provenance')
        exact_table = ExactBtnTable(exact_document(exact, context_source=source,
            catalog_source=args['catalog_source'], matrix_sha256=args['matrix_sha256']),
            source, args['catalog_source'], matrix_sha256=args['matrix_sha256'],
            entry_mass=args['entry_mass'])
        result[key] = (exact_table, RootTable(root, source, args['catalog_source']))
    return result


def model(registry, shared, local_states, resources):
    value = dict(format=1, policy_type=TYPE, generation=shared['generation'],
                 shared=copy.deepcopy(shared), local_states=copy.deepcopy(local_states),
                 override_order=list(ORDER))
    validate(value, registry, resources)
    return value


def predict(value, registry, queries, *, context_sha256, resources, device='cpu'):
    overrides = validate(value, registry, resources)
    p, prepared = interface(value['shared']).predict(value['shared'], registry, queries,
        context_sha256=context_sha256, device=device)
    exact_rows = root_rows = []
    if context_sha256 in overrides:
        exact, root = overrides[context_sha256]
        p, exact_rows = exact.apply(queries['observations'], p)
        p, root_rows = root.apply(queries['observations'], p)
    arity = np.asarray([o['n'] for o in queries['observations']])
    legal = np.arange(4)[None, :] < arity[:, None]
    if (not np.isfinite(p).all() or np.any(p < 0) or np.any(p[~legal])
            or np.max(abs(p.sum(1) - 1)) > 1e-12):
        raise ValueError('Invalid complete continuation policy')
    coverage = dict(exact_btn_rows=len(exact_rows), board_root_rows=len(root_rows),
                    learned_local_state=context_sha256 in overrides)
    return p, prepared, coverage


def average(documents, registry, queries, *, context_sha256, resources,
            weights_by_player, device, guard):
    weights = np.asarray(weights_by_player, dtype=np.float64)
    if (not documents or weights.shape != (2, len(documents))
            or not np.isfinite(weights).all() or np.any(weights <= 0)
            or not np.isfinite(weights.sum())):
        raise ValueError('Complete positive played-model weights required')
    actor = np.asarray([o['actor'] for o in queries['observations']])
    numerator = np.zeros((len(actor), 4)); denominator = np.zeros(len(actor))
    shared_kind = documents[0]['shared']['policy_type']
    for generation, value in enumerate(documents):
        guard()
        if value['generation'] != generation or value['shared']['policy_type'] != shared_kind:
            raise ValueError('Unplayed, reordered or mixed-representation model bank')
        p, prepared, _ = predict(value, registry, queries, context_sha256=context_sha256,
                                 resources=resources, device=device)
        reach = weights[actor, generation].copy()
        # Reach uses the final policy, including both exact/root overrides.
        for i, history in enumerate(prepared['own_history']):
            for parent, action in history:
                reach[i] *= p[parent, action]
        numerator += reach[:, None] * p; denominator += reach
    supported = denominator > 0
    result = np.zeros_like(numerator)
    result[supported] = numerator[supported] / denominator[supported, None]
    for i in np.flatnonzero(~supported):
        result[i, :queries['observations'][i]['n']] = 1. / queries['observations'][i]['n']
    if not np.isfinite(result).all() or np.max(abs(result.sum(1) - 1)) > 1e-12:
        raise ValueError('Invalid played continuation average')
    return result, denominator


def write_model(directory, value, registry, resources):
    validate(value, registry, resources)
    return dict(publish(directory, 'fullstackmodel', encoded(value)), generation=value['generation'])


def read_model(directory, reference, registry, resources):
    value = json.loads(read_object(directory, reference))
    validate(value, registry, resources)
    if reference['generation'] != value['generation']:
        raise ValueError('Model reference generation mismatch')
    return value
