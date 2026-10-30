"""Frozen current-policy adapter for complete all-node expected preflop targets.

Preparation only: no worker launch, model fit, experiment admission or checkpoint
publication. The caller authenticates native executable/context identities before
and after exporting a tree. This adapter binds the received raw tree bytes, checks
complete hand order and visible observations, then emits one board contribution.
"""
import copy
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

from board_root_accumulator_v1 import digest, integer
from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets, TARGET
from sampled_physical_deals_v1 import PhysicalDeals
from stack_context_board_targets_v1 import preflop_policy
from stack_context_current_policy_v1 import CurrentPolicy
from stack_context_preflop_expected_components_v2 import PreflopExpectedComponents
from storage_strategic_common_prior_20260920 import PAIRS, CLASSES

METHOD = 'frozen-all-preflop-native-targets-v1'
SUITS = tuple(itertools.permutations(range(4)))


def text_sha(source):
    if not isinstance(source, str):
        raise ValueError('Exact UTF-8 source required')
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


def physical_class_mass(weights):
    """Original compatible pair law; no hero policy or public-board conditioning."""
    result = np.zeros((169, 169))
    for c in range(169):
        other = weights[1]*(CLASSES == c)
        counts = np.bincount(PAIRS.ravel(), weights=np.repeat(other, 2), minlength=52)
        available = np.maximum(other.sum()-counts[PAIRS[:, 0]]-counts[PAIRS[:, 1]]+other, 0.)
        result[:, c] = np.bincount(CLASSES, weights=weights[0]*available, minlength=169)
    return result, float(result.sum())


def canonical_card_keys(hands, board, actor, phase):
    """Batch equivalent of native Observation canonical_cards, prefix only."""
    integer(actor, 0, 1); integer(phase, 0, 3)
    visible = (0, 3, 4, 5)[phase]
    cards = np.full((len(hands), 7), 63, dtype=np.int64)
    cards[:, :2] = hands
    cards[:, 2:2+visible] = board[:visible]
    minimum = np.full(len(hands), np.iinfo(np.uint64).max, dtype=np.uint64)
    shifts = np.arange(0, 42, 6, dtype=np.uint64)
    for suits in SUITS:
        mapped = np.where(cards == 63, 63, 4*(cards//4)+np.asarray(suits)[cards % 4])
        mapped[:, :2].sort(1); mapped[:, 2:5].sort(1)
        lo = np.uint64(actor << 42) | np.sum(mapped.astype(np.uint64) << shifts, axis=1, dtype=np.uint64)
        np.minimum(minimum, lo, out=minimum)
    return minimum


class FrozenAllPreflopPolicy:
    """Same postflop model, complete replacement of its fitted preflop policy."""
    def __init__(self, engine, preflop, context, matrix):
        self.engine = engine
        self.context_source = engine.context_source
        self.generation = engine.generation
        self._context = copy.deepcopy(context)
        self._pre = PreflopExpectedComponents(context, matrix, preflop).preflop
        for p in self._pre.values():
            p.setflags(write=False)

    def prepare(self, queries, *, require_history=True):
        return dict(owner=self,
            base=self.engine.prepare(queries, require_history=require_history))

    def infer(self, prepared):
        if prepared.get('owner') is not self:
            raise ValueError('Rows belong to another frozen all-node policy')
        p = self.engine.infer(prepared['base']).copy()
        base = prepared['base']
        for j, (_, hi_key, lo_key) in enumerate(base['keys']):
            if int(hi_key) >= 1 << 63:
                continue
            i = int(hi_key)-1
            cards = [(int(lo_key) >> (6*k)) & 63 for k in range(2)]
            a, b = cards; hi, lo = max(a//4, b//4), min(a//4, b//4)
            c = hi*13+lo if a % 4 == b % 4 or hi == lo else lo*13+hi
            n = self._context['nodes'][i]
            if base['actors'][j] != n['actor'] or base['arity'][j] != len(n['children']):
                raise ValueError('All-node policy menu or actor mismatch')
            p[j] = 0.; p[j, :base['arity'][j]] = self._pre[i][c]
        return p

    def score_rows(self, context_source, observations):
        return self.infer(self.prepare(dict(context_source=context_source,
            observations=observations), require_history=False))


class FrozenExpectedTargets:
    def __init__(self, *, state, model_source, registry, resources,
                 physical_catalog_source, expected_physical_catalog_sha256, matrix_source):
        if not isinstance(state, PreflopExpectedRegrets):
            raise ValueError('Qualified all-node cumulative state required')
        source = registry.source(state.config['context_sha256'])
        if (state.config['context_sha256'] not in registry.fit_contexts
                or text_sha(matrix_source) != state.config['matrix_sha256']
                or text_sha(physical_catalog_source) != expected_physical_catalog_sha256):
            raise ValueError('Fitted context and pinned original matrix/catalog required')
        self._state = PreflopExpectedRegrets.restore(state.document(), context_source=source,
            matrix_source=matrix_source, expected_config=state.config)
        self._state_sha = self._state.document()['state_sha256']
        self._plan = self._state.plan()
        model = json.loads(model_source)
        if model['generation'] != self._state.steps:
            raise ValueError('Model and all-node state must share a completed generation')
        key = state.config['context_sha256']; args = resources[key]
        if (args['matrix_sha256'] != state.config['matrix_sha256']
                or not np.array_equal(np.asarray(args['entry_mass']), self._state.matrix.btn_mass)
                or not np.array_equal(np.asarray(args['root_config']['entry_mass']), self._state.matrix.bb_mass)):
            raise ValueError('Original resources and both actor entry masses must agree')
        self._base = CurrentPolicy(model, registry, context_sha256=key, resources=resources)
        fallback, suit_error = preflop_policy(json.loads(physical_catalog_source),
            self._state.context, self._base)
        self._pre = self._state.probabilities(fallback)
        self.policy = FrozenAllPreflopPolicy(self._base, self._pre, self._state.context, self._state.matrix)
        self._geometry = PreflopExpectedComponents(self._state.context, self._state.matrix, self._pre)
        self._sampler = PhysicalDeals(source, mode='full_deck', seed=0)
        raw_mass, pair_mass = physical_class_mass(self._sampler.weights)
        if (not np.isclose(pair_mass, self._sampler.masses[0], rtol=1e-13, atol=1e-10)
                or np.max(abs(raw_mass/pair_mass-self._state.matrix.mass)) > 1e-12):
            raise ValueError('Terminal matrix must use the original compatible physical entry law')
        self._exact = {i:r['q'] for i, r in self._geometry.exact().items()}
        self._recipe = dict(method=METHOD, generation=self._state.steps,
            model_sha256=text_sha(model_source), context_sha256=key,
            registry_sha256=registry.sha256, matrix_sha256=state.config['matrix_sha256'],
            physical_catalog_sha256=expected_physical_catalog_sha256,
            initial_catalog_sha256=text_sha(args['catalog_source']),
            cumulative_state_sha256=self._state_sha,
            played_preflop_sha256=digest(self._state.encoded(self._pre)),
            provider_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            entry_rule='Original PhysicalDeals weights, including inherited 1e-5 cutoff',
            private_domain='All 1081 board-legal hands per actor, including zero-weight hands',
            preflop_override='Complete all-node policy after legacy engine fallback',
            maximum_preflop_suit_difference=suit_error)

    @property
    def recipe(self):
        return copy.deepcopy(self._recipe)

    def request(self, board):
        if (not isinstance(board, list) or len(board) != 5
                or any(type(c) is not int or not 0 <= c < 52 for c in board)
                or len(set(board)) != 5 or board[:3] != sorted(board[:3])):
            raise ValueError('Canonical flop and ordered turn/river required')
        ids = np.flatnonzero(~np.isin(PAIRS, board).any(1))
        return dict(board=board.copy(), hands=[PAIRS[ids].tolist(), PAIRS[ids].tolist()]), ids

    def _policies(self, tree):
        hands = np.asarray(tree['hands'][0], dtype=np.int64)
        key_cache = {}
        result = []
        required = {'hi', 'lo', 'actor', 'phase', 'n', 'active_features'}
        for branch in tree['branches']:
            nodes = branch['nodes']; spans = []; observations = []; seen = set()
            def walk(i, history):
                if type(i) is not int or not 0 <= i < len(nodes) or i in seen:
                    raise ValueError('Complete acyclic native postflop tree required')
                seen.add(i); node = nodes[i]; kind = node['kind']
                children = node.get('children', [])
                if kind == 0:
                    actor = integer(node['actor'], 0, 1)
                    phase = integer(node['street'], 0, 2)+1
                    if not 2 <= len(children) <= 4:
                        raise ValueError('Supported native action menu required')
                    hi = str((1 << 63) | (history << 4) | branch['branch'])
                    cache_key = (actor, phase)
                    if cache_key not in key_cache:
                        key_cache[cache_key] = canonical_card_keys(hands, tree['board'], actor, phase)
                    rows = node['observations']
                    if len(rows) != len(hands):
                        raise ValueError('One native observation per ordered physical hand required')
                    for o, lo in zip(rows, key_cache[cache_key]):
                        if (set(o) != required or o['hi'] != hi or o['lo'] != str(int(lo))
                                or any(type(o[k]) is not int for k in ('actor', 'phase', 'n'))
                                or (o['actor'], o['phase'], o['n']) != (actor, phase, len(children))):
                            raise ValueError('Native row hand, actor, visible prefix, history or menu mismatch')
                    spans.append((i, len(observations), len(rows))); observations.extend(rows)
                    for a, child in enumerate(children):
                        walk(child, (history << 3) | (a+1))
                elif kind == 1:
                    if len(children) != 1:
                        raise ValueError('One fixed-board chance transition required')
                    walk(children[0], (history << 3) | 5)
                elif kind in (2, 3):
                    if children:
                        raise ValueError('Terminal node cannot have children')
                else:
                    raise ValueError('Unknown native node kind')
            walk(0, 1)
            if len(seen) != len(nodes):
                raise ValueError('Unreachable postflop nodes are refused')
            p = self.policy.score_rows(self.policy.context_source, observations)
            result.append({i:p[start:start+count, :len(nodes[i]['children'])]
                for i, start, count in spans})
        return result

    def draw_record(self, tree_source, *, expected_tree_sha256, draw_index):
        integer(draw_index, 0, len(self._plan['boards'])-1)
        if not isinstance(tree_source, bytes) or hashlib.sha256(tree_source).hexdigest() != expected_tree_sha256:
            raise ValueError('Exact received native tree bytes and identity required')
        tree = json.loads(tree_source); board = self._plan['boards'][draw_index]
        req, ids = self.request(board)
        if tree.get('format') != 1 or tree.get('board') != board or tree.get('hands') != req['hands']:
            raise ValueError('Original planned board and complete ordered private domains required')
        if (len(tree.get('ranks', [])) != 2 or any(np.asarray(r).shape != (1081,)
                or np.asarray(r).dtype.kind not in 'iu' or np.any(np.asarray(r) < 0) for r in tree['ranks'])):
            raise ValueError('Two complete nonnegative integer native rank arrays required')
        post = self._policies(tree)
        records = self._geometry.board(tree, post, [w[ids] for w in self._sampler.weights],
            [CLASSES[ids], CLASSES[ids]], self._sampler.masses[0])
        values = self._state.encoded({i:r['q'] for i, r in records.items()})
        return dict(draw_index=draw_index, board=board.copy(), model_sha256=self._recipe['model_sha256'],
            tree_sha256=expected_tree_sha256, policy_recipe_sha256=digest(self._recipe),
            values=values, values_sha256=digest(values))

    def generation_evidence(self, state, plan, records):
        if (state.document()['state_sha256'] != self._state_sha or plan != self._plan
                or len(records) != len(plan['boards'])
                or any(r['policy_recipe_sha256'] != digest(self._recipe) for r in records)):
            raise ValueError('Frozen complete generation and unchanged parent state required')
        result = dict(format=1, method=TARGET, generation=self._state.steps, plan_sha256=digest(plan),
            context_sha256=self._recipe['context_sha256'], matrix_sha256=self._recipe['matrix_sha256'],
            model_sha256=self._recipe['model_sha256'], played_policy_sha256=digest(state.encoded(self._pre)),
            exact_terms_sha256=digest(state.encoded(self._exact)), draws=copy.deepcopy(records))
        # Validate the complete transaction on a restored copy; never publish here.
        temporary = PreflopExpectedRegrets.restore(state.document(), context_source=self._state._context_source,
            matrix_source=self._state._matrix_source, expected_config=state.config)
        temporary.step(plan, result, played_policy=self._pre)
        return result

    def played_preflop(self):
        return {i:p.copy() for i, p in self._pre.items()}
