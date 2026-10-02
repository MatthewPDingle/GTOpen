"""Typed policy using complete cumulative preflop state and shared postflop nets.

This is a new research model contract, never a migration of the old comparison.
All fitted preflop decisions use the new state. Sparse retained tables and legacy
root/BTN overlays are refused. Held-out contexts use the shared network only.
No training, scientific admission, worker execution, or production mutation.
"""
import copy
import json
from collections import OrderedDict

import numpy as np

from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets
from stack_context_current_policy_v1 import CurrentPolicy
from stack_context_board_targets_v1 import preflop_policy
from stack_context_full_policy_v1 import interface
from stack_context_inputs_v1 import digest as text_sha, encoded
from sampled_visible_hybrid_checkpoint_v1 import publish, read_object

TYPE = 'stack-context-all-node-expected-continuation-policy-v1'
ORDER = ['shared_network', 'all_preflop_expected']
RESOURCE_FIELDS = {'physical_catalog_source', 'physical_catalog_sha256',
                   'matrix_source', 'expected_config'}


def local_document(state, resources):
    return dict(physical_catalog_sha256=resources['physical_catalog_sha256'],
                cumulative_state=state.document())


def validate(value, registry, resources):
    if (not isinstance(value, dict)
            or set(value) != {'format', 'policy_type', 'generation', 'shared', 'local_states', 'override_order'}
            or type(value['format']) is not int or value['format'] != 1
            or value['policy_type'] != TYPE or value['override_order'] != ORDER):
        raise ValueError('Explicit all-node cumulative policy contract required')
    shared = value['shared']
    interface(shared).validate(shared, registry)
    generation = value['generation']
    if (type(generation) is not int or generation < 0
            or generation != shared['generation']):
        raise ValueError('Shared network and cumulative states need one completed generation')
    if any(pair != [None, None] for pair in shared['preflop_tables'].values()):
        raise ValueError('Sparse retained preflop tables are not part of this policy')
    if (set(value['local_states']) != set(registry.fit_contexts)
            or set(resources) != set(registry.fit_contexts)):
        raise ValueError('Exactly the fitting contexts require all-node local states')
    result = {}
    for key in registry.fit_contexts:
        local, args = value['local_states'][key], resources[key]
        if (set(local) != {'physical_catalog_sha256', 'cumulative_state'}
                or set(args) != RESOURCE_FIELDS
                or not isinstance(args['physical_catalog_source'], str)
                or local['physical_catalog_sha256'] != args['physical_catalog_sha256']
                or text_sha(args['physical_catalog_source']) != args['physical_catalog_sha256']):
            raise ValueError('Pinned complete physical catalog and all-node resources required')
        catalog = json.loads(args['physical_catalog_source'])
        source = registry.source(key)
        if catalog['context_source'] != source:
            raise ValueError('Physical catalog belongs to another context')
        state = PreflopExpectedRegrets.restore(local['cumulative_state'],
            context_source=source, matrix_source=args['matrix_source'],
            expected_config=args['expected_config'])
        if state.steps != generation or state.config['context_sha256'] != key:
            raise ValueError('Every local cumulative state must finish the complete cycle')
        result[key] = state
    return result


def model(registry, shared, states, resources):
    if set(states) != set(registry.fit_contexts):
        raise ValueError('All fitting states required before model publication')
    value = dict(format=1, policy_type=TYPE, generation=shared['generation'],
        shared=copy.deepcopy(shared),
        local_states={k:local_document(states[k], resources[k]) for k in registry.fit_contexts},
        override_order=list(ORDER))
    validate(value, registry, resources)
    return value


class ExpectedPolicy(CurrentPolicy):
    """Reuse qualified visible-row math, with the new model's own policy state.

The initializer deliberately does not construct a legacy full-policy document.
Inherited prepare/infer check visible inputs, public menus and ancestor links;
our complete preflop rows replace the shared result at every fitted node.
"""
    def __init__(self, value, registry, *, context_sha256, resources, device='cpu'):
        if device not in ('cpu', 'cuda'):
            raise ValueError('Explicit CPU/CUDA inference required')
        states = validate(value, registry, resources)
        self.context_sha256 = context_sha256
        self.context_source = registry.source(context_sha256)
        self.entry = copy.deepcopy(registry._get(context_sha256))
        self.width = registry.manifest['representation']['input_width']
        self.generation = value['generation']
        self.device = device
        self.relative_cache = OrderedDict()
        self.tables = []
        self._pre = None
        self.weights = []
        if device == 'cuda':
            import torch
            if torch.backends.cuda.matmul.allow_tf32 or torch.backends.cudnn.allow_tf32:
                raise ValueError('Disable TF32')
        for net in value['shared']['networks']:
            layers = []
            for layer, shape in enumerate(((64, self.width), (64, 64), (4, 64))):
                w = np.asarray(net[f'w{layer}'], np.float32).astype(np.float64).reshape(shape)
                b = np.asarray(net[f'b{layer}'], np.float32).astype(np.float64)
                if device == 'cuda':
                    w, b = torch.tensor(w, device='cuda'), torch.tensor(b, device='cuda')
                else:
                    w.setflags(write=False); b.setflags(write=False)
                layers.append((w, b))
            self.weights.append(layers)
        self._state = states.get(context_sha256)
        if self._state is not None:
            fallback, self.maximum_preflop_suit_difference = preflop_policy(
                json.loads(resources[context_sha256]['physical_catalog_source']),
                self._state.context, self)
            self._pre = self._state.probabilities(fallback)
            for p in self._pre.values(): p.setflags(write=False)
        else:
            self.maximum_preflop_suit_difference = None

    def prepare(self, queries, *, require_history=True):
        prepared = super().prepare(queries, require_history=require_history)
        if self._pre is not None:
            for j, (_, hi_key, lo_key) in enumerate(prepared['keys']):
                if int(hi_key) >= 1 << 63: continue
                node = int(hi_key)-1
                a, b = [(int(lo_key) >> (6*k)) & 63 for k in range(2)]
                hi, lo = max(a//4, b//4), min(a//4, b//4)
                c = hi*13+lo if a % 4 == b % 4 or hi == lo else lo*13+hi
                n = self._state.context['nodes'][node]
                if (prepared['actors'][j] != n['actor']
                        or prepared['arity'][j] != len(n['children'])):
                    raise ValueError('Cumulative preflop row actor/menu mismatch')
                prepared['table'][j] = 0.
                prepared['table'][j, :prepared['arity'][j]] = self._pre[node][c]
                prepared['mask'][j] = True
        return prepared

    def played_preflop(self):
        if self._pre is None:
            raise ValueError('Held-out contexts have no fitted cumulative state')
        return {i:p.copy() for i, p in self._pre.items()}


def predict(value, registry, queries, *, context_sha256, resources, device='cpu'):
    engine = ExpectedPolicy(value, registry, context_sha256=context_sha256,
                            resources=resources, device=device)
    prepared = engine.prepare(queries)
    return engine.infer(prepared), prepared


def average(documents, registry, queries, *, context_sha256, resources,
            completed_cycles, weights_by_player, device='cpu', guard=lambda:None):
    """Own-history-weighted average of the complete played prefix only.

The checkpoint supplies completed_cycles; the final unplayed generation must
not be included. No opponent reach or sampled visit count replaces own reach.
"""
    weights = np.asarray(weights_by_player, dtype=np.float64)
    if (type(completed_cycles) is not int or completed_cycles < 1
            or len(documents) != completed_cycles
            or weights.shape != (2, completed_cycles) or not np.isfinite(weights).all()
            or np.any(weights <= 0) or not np.isfinite(weights.sum())):
        raise ValueError('Complete played prefix and positive actor weights required')
    actors = np.asarray([o['actor'] for o in queries['observations']])
    numerator = np.zeros((len(actors), 4)); denominator = np.zeros(len(actors))
    kind = documents[0]['shared']['policy_type']
    for generation, value in enumerate(documents):
        guard()
        if value['generation'] != generation or value['shared']['policy_type'] != kind:
            raise ValueError('Reordered, unplayed or mixed-representation model bank')
        p, prepared = predict(value, registry, queries, context_sha256=context_sha256,
                              resources=resources, device=device)
        reach = weights[prepared['actors'], generation].copy()
        for i, history in enumerate(prepared['own_history']):
            for parent, action in history: reach[i] *= p[parent, action]
        numerator += reach[:, None]*p; denominator += reach
    result = np.zeros_like(numerator); supported = denominator > 0
    result[supported] = numerator[supported]/denominator[supported, None]
    for i in np.flatnonzero(~supported):
        result[i, :queries['observations'][i]['n']] = 1./queries['observations'][i]['n']
    if not np.isfinite(result).all() or np.max(abs(result.sum(1)-1)) > 1e-12:
        raise ValueError('Invalid complete played average')
    return result, denominator


def write_model(directory, value, registry, resources):
    validate(value, registry, resources)
    return dict(publish(directory, 'expectedstackmodel', encoded(value)), generation=value['generation'])


def read_model(directory, reference, registry, resources):
    value = json.loads(read_object(directory, reference))
    validate(value, registry, resources)
    if type(reference['generation']) is not int or reference['generation'] != value['generation']:
        raise ValueError('All-node model reference generation mismatch')
    return value
