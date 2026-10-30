"""Persistent all-node preflop regrets from complete fixed-policy generations.

Isolated preparation only. This component never infers a model, executes native
code, admits science, or edits a training checkpoint. The caller authenticates
native board targets. Chance draws are counted separately from hand-history
visits; dispersion across changing policies is not a confidence interval.
"""
import copy
import hashlib
import json

import numpy as np

from board_root_accumulator_v1 import digest, identity, integer, CHANCE
from preflop_allin_matrix_v1 import AllinMatrix
from stack_context_preflop_expected_components_v2 import PreflopExpectedComponents

METHOD = 'board-integrated-all-preflop-regrets-v1'
TARGET = 'complete-all-preflop-board-generation-v1'


class PreflopExpectedRegrets:
    def __init__(self, *, context_source, matrix_source, generation_scale,
                 boards_per_generation, board_seed):
        if not isinstance(context_source, str) or not isinstance(matrix_source, str):
            raise ValueError('Exact immutable context and terminal matrix sources required')
        self._context_source, self._matrix_source = context_source, matrix_source
        self.context = json.loads(context_source)
        self.matrix = AllinMatrix(json.loads(matrix_source), context_source)
        uniform = {i:np.full((169, len(n['children'])), 1/len(n['children']))
                   for i, n in enumerate(self.context['nodes']) if n['children']}
        geometry = PreflopExpectedComponents(self.context, self.matrix, uniform)
        self.nodes = sorted(geometry.decisions)
        self.mass = [self.matrix.bb_mass.copy(), self.matrix.btn_mass.copy()]
        self.specs = {i:dict(actor=self.context['nodes'][i]['actor'],
                            arity=len(self.context['nodes'][i]['children'])) for i in self.nodes}
        self.post_slots = {}
        def has_post(i):
            n = self.context['nodes'][i]
            return (any(has_post(j) for j in n['children']) if n['children']
                    else n['leaf']['type'] == 'postflop')
        for i in self.nodes:
            self.post_slots[i] = np.asarray([has_post(j) for j in self.context['nodes'][i]['children']])
        self.config = dict(context_sha256=hashlib.sha256(context_source.encode()).hexdigest(),
            matrix_sha256=hashlib.sha256(matrix_source.encode()).hexdigest(),
            generation_scale=integer(generation_scale, 1, 65536),
            boards_per_generation=integer(boards_per_generation, 1, 4096),
            board_seed=integer(board_seed, 0, 2**63-1), chance=CHANCE,
            numpy_version=np.__version__, specs={str(i):s for i, s in self.specs.items()},
            class_mass=[m.tolist() for m in self.mass], units='bb-counterfactual-values',
            method=METHOD)
        self.steps = 0
        self.regrets = {i:np.zeros((169, s['arity'])) for i, s in self.specs.items()}
        self.board_sums = {i:np.zeros_like(v) for i, v in self.regrets.items()}
        self.board_squared_sums = {i:np.zeros_like(v) for i, v in self.regrets.items()}
        self.supported_generations = {i:np.zeros(169, dtype=np.int64) for i in self.nodes}
        self.history = []

    def _arrays(self, values):
        if not isinstance(values, dict) or set(values) != set(map(str, self.nodes)):
            raise ValueError('Every preflop decision required exactly once')
        result = {}
        for i in self.nodes:
            x = np.asarray(values[str(i)], dtype=np.float64)
            if x.shape != self.regrets[i].shape or not np.isfinite(x).all():
                raise ValueError('Complete finite node/class/action values required')
            result[i] = x.copy()
        return result

    @staticmethod
    def encoded(values):
        return {str(i):v.tolist() for i, v in sorted(values.items())}

    def document(self):
        result = dict(format=1, method=METHOD, config=copy.deepcopy(self.config),
            completed_updates=self.steps,
            board_draws=self.steps*self.config['boards_per_generation'],
            sampled_hand_visits=0, regret_sums=self.encoded(self.regrets),
            board_target_sums=self.encoded(self.board_sums),
            board_target_squared_sums=self.encoded(self.board_squared_sums),
            supported_generations=self.encoded(self.supported_generations),
            history=copy.deepcopy(self.history))
        result['state_sha256'] = digest(result)
        return result

    def plan(self):
        rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(
            [self.config['board_seed'], self.steps])))
        boards = []
        for _ in range(self.config['boards_per_generation']):
            board = rng.choice(52, size=5, replace=False).tolist()
            board[:3] = sorted(board[:3])
            boards.append(board)
        return dict(format=1, method=TARGET, generation=self.steps,
            parent_state_sha256=self.document()['state_sha256'],
            config_sha256=digest(self.config), boards=boards)

    def step(self, plan, evidence, *, played_policy):
        """Validate and reduce a whole generation before publishing any state."""
        if plan != self.plan():
            raise ValueError('Stale or detached all-node generation plan')
        geometry = PreflopExpectedComponents(self.context, self.matrix, played_policy)
        exact_records = geometry.exact()
        exact = {i:r['q'] for i, r in exact_records.items()}
        p = geometry.preflop
        required = dict(format=1, method=TARGET, generation=self.steps,
            plan_sha256=digest(plan), context_sha256=self.config['context_sha256'],
            matrix_sha256=self.config['matrix_sha256'],
            played_policy_sha256=digest(self.encoded(p)),
            exact_terms_sha256=digest(self.encoded(exact)))
        if (not isinstance(evidence, dict) or set(evidence) != set(required)|{'model_sha256', 'draws'}
                or any(evidence[k] != v for k, v in required.items())):
            raise ValueError('Complete matching model/policy/generation evidence required')
        model = identity(evidence['model_sha256'])
        draws = evidence['draws']
        if not isinstance(draws, list) or len(draws) != len(plan['boards']):
            raise ValueError('Every declared board contribution required')
        board_sums = {i:np.zeros_like(x) for i, x in self.regrets.items()}
        board_squares = {i:np.zeros_like(x) for i, x in self.regrets.items()}
        try:
            with np.errstate(over='raise', invalid='raise'):
                for j, (draw, board) in enumerate(zip(draws, plan['boards'])):
                    if (set(draw) != {'draw_index', 'board', 'model_sha256', 'tree_sha256',
                                     'policy_recipe_sha256', 'values', 'values_sha256'}
                            or type(draw['draw_index']) is not int or draw['draw_index'] != j
                            or draw['board'] != board or draw['model_sha256'] != model):
                        raise ValueError('Missing, reordered or detached native board target')
                    identity(draw['tree_sha256']); identity(draw['policy_recipe_sha256'])
                    values = self._arrays(draw['values'])
                    if digest(draw['values']) != draw['values_sha256']:
                        raise ValueError('Changed board target values')
                    for i, x in values.items():
                        unsupported = ~exact_records[i]['counterfactual_supported']
                        if np.any(abs(x[unsupported]) > 1e-12) or np.any(x[:, ~self.post_slots[i]] != 0):
                            raise ValueError('Board mass outside counterfactual/postflop support')
                        board_sums[i] += x
                        board_squares[i] += x*x
                delta, regrets, total_sums, total_squares, counts = {}, {}, {}, {}, {}
                for i in self.nodes:
                    q = exact[i] + board_sums[i]/len(draws)
                    advantage = q - np.sum(p[i]*q, axis=1)[:, None]
                    weight = self.config['generation_scale']*self.mass[self.specs[i]['actor']]
                    delta[i] = weight[:, None]*advantage
                    regrets[i] = self.regrets[i]+delta[i]
                    total_sums[i] = self.board_sums[i]+board_sums[i]
                    total_squares[i] = self.board_squared_sums[i]+board_squares[i]
                    counts[i] = self.supported_generations[i]+exact_records[i]['counterfactual_supported']
                if any(not np.isfinite(x).all() for group in (regrets, total_sums, total_squares)
                       for x in group.values()):
                    raise ValueError('Persistent target state overflow')
        except FloatingPointError as error:
            raise ValueError('Persistent target arithmetic overflow') from error
        entry = dict(generation=self.steps, plan_sha256=digest(plan),
            evidence_sha256=digest(evidence), model_sha256=model,
            played_policy_sha256=required['played_policy_sha256'],
            exact_terms_sha256=required['exact_terms_sha256'],
            delta_sha256=digest(self.encoded(delta)),
            board_sum_delta_sha256=digest(self.encoded(board_sums)),
            board_squared_sum_delta_sha256=digest(self.encoded(board_squares)))
        self.regrets, self.board_sums, self.board_squared_sums, self.supported_generations, self.history, self.steps = (
            regrets, total_sums, total_squares, counts, [*self.history, entry], self.steps+1)
        return {i:x.copy() for i, x in delta.items()}

    def probabilities(self, fallback):
        p = PreflopExpectedComponents(self.context, self.matrix, fallback).preflop
        result = {i:x.copy() for i, x in p.items()}
        if not self.steps:
            return result
        for i, regret in self.regrets.items():
            supported = self.supported_generations[i] > 0
            positive = np.maximum(regret, 0)
            total = positive.sum(1)
            live = supported & (total > 0)
            result[i][live] = positive[live]/total[live, None]
            zero = np.flatnonzero(supported & ~live)
            result[i][zero] = np.eye(self.specs[i]['arity'])[np.argmax(regret[zero], axis=1)]
        return result

    @classmethod
    def restore(cls, document, *, context_source, matrix_source, expected_config):
        d = copy.deepcopy(document)
        seal = d.pop('state_sha256', None)
        required = {'format', 'method', 'config', 'completed_updates', 'board_draws',
                    'sampled_hand_visits', 'regret_sums', 'board_target_sums',
                    'board_target_squared_sums', 'supported_generations', 'history'}
        if (set(d) != required or seal != digest(d) or d['format'] != 1 or d['method'] != METHOD
                or d['config'] != expected_config or d['sampled_hand_visits'] != 0):
            raise ValueError('Unknown, changed or unsupported cumulative checkpoint')
        result = cls(context_source=context_source, matrix_source=matrix_source,
            generation_scale=expected_config['generation_scale'],
            boards_per_generation=expected_config['boards_per_generation'], board_seed=expected_config['board_seed'])
        if result.config != expected_config:
            raise ValueError('Context/matrix/runtime/configuration changed across restoration')
        steps = integer(d['completed_updates'], 0, 1_000_000)
        history = d['history']
        if (d['board_draws'] != steps*expected_config['boards_per_generation']
                or not isinstance(history, list) or len(history) != steps):
            raise ValueError('Incomplete cumulative generation history')
        arrays = [result._arrays(d[k]) for k in
                  ('regret_sums', 'board_target_sums', 'board_target_squared_sums')]
        counts = d['supported_generations']
        if not isinstance(counts, dict) or set(counts) != set(map(str, result.nodes)):
            raise ValueError('Every node requires support generation counts')
        checked_counts = {}
        for i in result.nodes:
            c = np.asarray(counts[str(i)])
            if c.shape != (169,) or c.dtype.kind not in 'iu' or np.any(c < 0) or np.any(c > steps):
                raise ValueError('Bounded integer support generation counts required')
            absent = result.mass[result.specs[i]['actor']] == 0
            if np.any(c[absent] != 0) or any(np.any(a[i][absent] != 0) for a in arrays):
                raise ValueError('Checkpoint contains absent source-entry mass')
            if (np.any(arrays[2][i] < 0) or (not steps and
                    (np.any(c) or any(np.any(a[i] != 0) for a in arrays)))):
                raise ValueError('Invalid target moments or nonempty initial checkpoint')
            checked_counts[i] = c.astype(np.int64)
        history_keys = {'generation', 'plan_sha256', 'evidence_sha256', 'model_sha256',
                        'played_policy_sha256', 'exact_terms_sha256', 'delta_sha256',
                        'board_sum_delta_sha256', 'board_squared_sum_delta_sha256'}
        for generation, row in enumerate(history):
            if (set(row) != history_keys or type(row['generation']) is not int
                    or row['generation'] != generation):
                raise ValueError('Complete sequential generation identities required')
            for k in history_keys-{'generation'}: identity(row[k])
        result.regrets, result.board_sums, result.board_squared_sums = arrays
        result.supported_generations, result.history, result.steps = checked_counts, history, steps
        if result.document() != document:
            raise ValueError('Noncanonical cumulative checkpoint')
        return result
