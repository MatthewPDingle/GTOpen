"""Experimental BB root state for complete public-board estimates.

This is not an admitted training model. No physical-deal visits are invented.
Chance is keyed by seed and generation, so preparing/rejecting a transaction
does not advance a mutable RNG. External native evidence still needs readback.
"""
import copy
import hashlib
import json
import re
import numpy as np

METHOD = 'board-integrated-bb-root-regrets-v1'
TARGET = 'board-integrated-bb-root-targets-v1'
CHANCE = 'numpy-pcg64-seedsequence-seed-generation-v1'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def identity(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('SHA-256 identity required')
    return value


def integer(value, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError('Bounded integer required')
    return value


def matrix(value):
    x = np.asarray(value, dtype=np.float64)
    if x.shape != (169, 4) or not np.isfinite(x).all():
        raise ValueError('169 by 4 finite matrix required')
    return x.copy()


def policy(value):
    x = matrix(value)
    if np.any(x < 0) or np.max(abs(x.sum(1) - 1)) > 1e-12:
        raise ValueError('Normalized nonnegative played policy required')
    return x


class BoardRootRegrets:
    def __init__(self, *, context_sha256, matrix_sha256, entry_mass,
                 physical_budget, boards_per_generation, board_seed):
        mass = np.asarray(entry_mass, dtype=np.float64)
        if (mass.shape != (169,) or not np.isfinite(mass).all()
                or np.any(mass <= 0) or abs(mass.sum() - 1) > 1e-12):
            raise ValueError('Original normalized positive entry-class mass required')
        self.config = dict(context_sha256=identity(context_sha256),
            matrix_sha256=identity(matrix_sha256), entry_mass=mass.tolist(),
            physical_budget=integer(physical_budget, 1, 65536),
            boards_per_generation=integer(boards_per_generation, 1, 4096),
            board_seed=integer(board_seed, 0, 2**63-1), chance=CHANCE)
        self.steps = 0
        self.regrets = np.zeros((169, 4), dtype=np.float64)
        self.history = []

    def document(self):
        result = dict(format=1, method=METHOD, config=copy.deepcopy(self.config),
            completed_updates=self.steps,
            board_draws=self.steps*self.config['boards_per_generation'],
            regret_sums=self.regrets.tolist(), history=copy.deepcopy(self.history))
        result['state_sha256'] = digest(result)
        return result

    def plan(self):
        generation = self.steps
        rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(
            [self.config['board_seed'], generation])))
        boards = []
        for _ in range(self.config['boards_per_generation']):
            board = rng.choice(52, size=5, replace=False).tolist()
            board[:3] = sorted(board[:3])
            boards.append(board)
        return dict(format=1, method=TARGET, generation=generation,
            parent_state_sha256=self.document()['state_sha256'],
            config_sha256=digest(self.config), boards=boards)

    def step(self, plan, evidence, *, played_policy, exact_terms):
        # All checks and arithmetic precede the single publication below.
        if plan != self.plan():
            raise ValueError('Stale, detached or modified board plan')
        p, exact = policy(played_policy), matrix(exact_terms)
        required = dict(format=1, method=TARGET, generation=self.steps,
            plan_sha256=digest(plan), context_sha256=self.config['context_sha256'],
            matrix_sha256=self.config['matrix_sha256'],
            played_policy_sha256=digest(p.tolist()), exact_terms_sha256=digest(exact.tolist()))
        if any(evidence.get(k) != v for k, v in required.items()):
            raise ValueError('Wrong generation target identity')
        model = identity(evidence['model_sha256'])
        draws = evidence['draws']
        if len(draws) != len(plan['boards']):
            raise ValueError('Complete board generation required')
        values = []
        for i, (draw, board) in enumerate(zip(draws, plan['boards'])):
            if (type(draw['draw_index']) is not int or draw['draw_index'] != i
                    or draw['board'] != board or draw['model_sha256'] != model):
                raise ValueError('Repeated, reordered or detached draw')
            identity(draw['tree_sha256']); identity(draw['policy_recipe_sha256'])
            x = matrix(draw['values'])
            if digest(x.tolist()) != draw['values_sha256'] or np.any(x[:, (0, 3)] != 0):
                raise ValueError('Changed values or non-variable fold/jam contribution')
            values.append(x)
        # Distinct draw indices may legitimately contain the same board.
        # Rejecting chance collisions would silently change the sampling law.
        q = exact + np.mean(values, axis=0)
        advantages = q - np.sum(p*q, axis=1)[:, None]
        delta = (self.config['physical_budget'] * np.asarray(self.config['entry_mass']))[:, None] * advantages
        regrets = self.regrets + delta
        if not np.isfinite(regrets).all():
            raise ValueError('Root regret overflow')
        entry = dict(generation=self.steps, plan_sha256=digest(plan),
            evidence_sha256=digest(evidence), model_sha256=model,
            played_policy_sha256=required['played_policy_sha256'],
            exact_terms_sha256=required['exact_terms_sha256'],
            delta_sha256=digest(delta.tolist()))
        self.regrets, self.history, self.steps = regrets, [*self.history, entry], self.steps+1
        return delta.copy()

    def probabilities(self, fallback):
        p = policy(fallback)
        if not self.steps:
            return p
        positive = np.maximum(self.regrets, 0)
        mass = positive.sum(1)
        live = mass > 0
        p[live] = positive[live]/mass[live, None]
        zero = np.flatnonzero(~live)
        p[zero] = np.eye(4)[np.argmax(self.regrets[zero], axis=1)]
        return p

    @classmethod
    def restore(cls, document, *, expected_config):
        document = copy.deepcopy(document)
        seal = document.pop('state_sha256', None)
        if (seal != digest(document) or document.get('format') != 1
                or document.get('method') != METHOD or document.get('config') != expected_config
                or expected_config.get('chance') != CHANCE):
            raise ValueError('Unknown board root state or changed configuration')
        config = dict(expected_config); del config['chance']
        result = cls(**config)
        steps = integer(document['completed_updates'], 0, 1000000)
        regrets = matrix(document['regret_sums']); history = document['history']
        if (document['board_draws'] != steps*config['boards_per_generation']
                or len(history) != steps or (steps == 0 and np.any(regrets != 0))):
            raise ValueError('Incomplete root history or wrong board count')
        for generation, row in enumerate(history):
            if type(row['generation']) is not int or row['generation'] != generation:
                raise ValueError('Nonsequential root history')
            for key in ('plan_sha256', 'evidence_sha256', 'model_sha256',
                        'played_policy_sha256', 'exact_terms_sha256', 'delta_sha256'):
                identity(row[key])
        result.steps, result.regrets, result.history = steps, regrets, copy.deepcopy(history)
        return result
