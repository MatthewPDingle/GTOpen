"""All-node preflop counterfactual components under a supplied frozen policy.

No sampling, inference, fitting, regret update, or scientific admission occurs.
Exact terminal matrices and a complete fixed-board postflop tree are supplied by
the caller, which must authenticate their population/context and visible-only
policy provenance. A board result is one importance-weighted chance contribution,
not a complete action EV. Own past reach is excluded; opponent past reach is not
renormalized. This preserves the reach scale needed for counterfactual regrets.
"""
import copy
import itertools
import math

import numpy as np

from board_fixed_policy_values_v1 import evaluate
from stack_context_board_components_v1 import routes


def _class(hand):
    a, b = hand
    hi, lo = max(a // 4, b // 4), min(a // 4, b // 4)
    return hi * 13 + lo if a % 4 == b % 4 or hi == lo else lo * 13 + hi


class PreflopExpectedComponents:
    def __init__(self, context, matrix, preflop):
        self.context = copy.deepcopy(context)
        self.routes = routes(self.context)
        self.nodes = self.context['nodes']
        self.decisions = {i for i, n in enumerate(self.nodes) if n['children']}
        if set(preflop) != self.decisions:
            raise ValueError('Exactly one frozen policy per preflop decision required')
        self.preflop = {}
        for i in self.decisions:
            n = self.nodes[i]
            p = np.asarray(preflop[i], dtype=np.float64)
            if (type(n['actor']) is not int or n['actor'] not in (0, 1)
                    or len(n['actions']) != len(n['children'])
                    or p.shape != (169, len(n['children']))
                    or not np.isfinite(p).all() or np.any(p < 0)
                    or np.max(abs(p.sum(1) - 1)) > 1e-12):
                raise ValueError('Finite class-constant normalized policy required')
            self.preflop[i] = p.copy()
            self.preflop[i].flags.writeable = False
        self.mass = np.asarray(matrix.mass, dtype=np.float64).copy()
        self.showdown = [np.asarray(matrix.bb, dtype=np.float64).copy(),
                         np.asarray(matrix.btn, dtype=np.float64).copy()]
        if (any(x.shape != (169, 169) or not np.isfinite(x).all()
                for x in [self.mass, *self.showdown])
                or np.any(self.mass < 0) or abs(self.mass.sum() - 1) > 1e-12):
            raise ValueError('Original normalized class-pair terminal matrices required')
        if any(np.any(x[self.mass == 0] != 0) for x in self.showdown):
            raise ValueError('No payoff mass outside original private-pair support')
        called = self.nodes[self.nodes[self.nodes[0]['children'][3]]['children'][1]]
        rake = called['pot'] * self.context['rake_fraction']
        if self.context['rake_cap'] > 0:
            rake = min(rake, self.context['rake_cap'])
        conserved = called['pot'] - sum(called['invested']) - rake
        if np.max(abs(self.showdown[0] + self.showdown[1] - self.mass*conserved)) > 1e-11:
            raise ValueError('Original all-in cashflow conservation required')
        low, high = -self.context['config']['stack'], self.context['config']['stack'] + self.context['dead_money']
        if any(np.any(v < self.mass*low-1e-11) or np.any(v > self.mass*high+1e-11)
               for v in self.showdown):
            raise ValueError('All-in values exceed original chip bounds')
        self.class_mass = [self.mass.sum(1), self.mass.sum(0)]
        if (not np.array_equal(self.class_mass[0], matrix.bb_mass)
                or not np.array_equal(self.class_mass[1], matrix.btn_mass)):
            raise ValueError('Terminal matrices and initial class masses disagree')
        self.reach = {}
        self.postorder = []

        def visit(i, reach):
            self.reach[i] = [r.copy() for r in reach]
            n = self.nodes[i]
            for a, child in enumerate(n['children']):
                nxt = [r.copy() for r in reach]
                nxt[n['actor']] *= self.preflop[i][:, a]
                visit(child, nxt)
            self.postorder.append(i)

        visit(0, [np.ones(169), np.ones(169)])

    def _normalize(self, value, hero):
        return np.divide(value, self.class_mass[hero],
                         out=np.zeros(169), where=self.class_mass[hero] > 0)

    def _project(self, leaves, component):
        value = {}
        records = {}
        for i in self.postorder:
            n = self.nodes[i]
            if not n['children']:
                value[i] = leaves.get(i, np.zeros((2, 169)))
                continue
            child = np.stack([value[j] for j in n['children']], axis=2)
            actor = n['actor']
            # Opponent probabilities are already in terminal prefix reach.
            value[i] = child.sum(2)
            q = child[actor]
            value[i][actor] = (q * self.preflop[i]).sum(1)
            entries = self.mass if actor == 0 else self.mass.T
            opponent_history = self._normalize(entries @ self.reach[i][1-actor], actor)
            supported = (self.class_mass[actor] > 0) & (opponent_history > 0)
            records[i] = dict(actor=actor, component=component, q=q.copy(),
                advantages=q - value[i][actor, :, None],
                incoming_class_supported=self.class_mass[actor] > 0,
                counterfactual_supported=supported,
                own_history_probability=self.reach[i][actor].copy(),
                opponent_history_probability=opponent_history)
        if any(not np.isfinite(r[k]).all() for r in records.values()
               for k in ('q', 'advantages', 'opponent_history_probability')):
            raise ValueError('Nonfinite counterfactual component')
        return records

    def exact(self):
        """Fold/all-in contributions integrated over original entry pairs."""
        leaves = {}
        for route in self.routes:
            i, kind = route['node'], route['kind']
            if kind == 'postflop':
                continue
            v = []
            for hero in (0, 1):
                opponent = self.reach[i][1-hero]
                if kind == 'fold':
                    matrix = self.mass if hero == 0 else self.mass.T
                    numerator = matrix @ opponent * self.nodes[i]['leaf']['utilities'][hero]
                else:
                    matrix = self.showdown[hero] if hero == 0 else self.showdown[hero].T
                    numerator = matrix @ opponent
                v.append(self._normalize(numerator, hero))
            leaves[i] = np.asarray(v)
        return self._project(leaves, 'exact-fold-allin')

    def board(self, tree, policies, weights, classes, total_pair_mass):
        """One unconditional 52-card board draw; compatible private pairs exact.

        Both actor vectors are reused from each postflop branch evaluation. The
        class reduction uses original hero entry weights, NEVER hero past reach.
        Zero source-entry classes return zero with an explicit unsupported mask.
        """
        board = tree.get('board')
        if (tree.get('format') != 1 or not isinstance(board, list) or len(board) != 5
                or any(type(c) is not int or not 0 <= c < 52 for c in board)
                or len(set(board)) != 5 or board[:3] != sorted(board[:3])):
            raise ValueError('Canonical physical five-card board required')
        expected = list(itertools.combinations([c for c in range(52) if c not in board], 2))
        if (len(tree.get('hands', [])) != 2
                or any(h != [list(pair) for pair in expected] for h in tree['hands'])
                or len(weights) != 2 or len(classes) != 2
                or type(total_pair_mass) not in (float, int)
                or not math.isfinite(total_pair_mass) or total_pair_mass <= 0):
            raise ValueError('Complete board-legal physical hands and original pair mass required')
        weights = [np.asarray(w, dtype=np.float64) for w in weights]
        raw_classes = [np.asarray(c) for c in classes]
        native_classes = np.asarray([_class(h) for h in expected], dtype=np.int64)
        if (any(c.dtype.kind not in 'iu' or not np.array_equal(c, native_classes)
                for c in raw_classes)
                or any(w.shape != (len(expected),) or not np.isfinite(w).all()
                       or np.any(w < 0) for w in weights)):
            raise ValueError('Original nonnegative entry weights and physical hand classes required')
        classes = [c.astype(np.int64) for c in raw_classes]
        if any(np.any(w[self.class_mass[p][c] == 0] != 0)
               for p, (w, c) in enumerate(zip(weights, classes))):
            raise ValueError('No board weights on absent original entry classes')
        paths = {r['node'] for r in self.routes if r['kind'] == 'postflop'}
        branches = tree.get('branches', [])
        if (len(branches) != len(policies) or len(branches) != len(paths)
                or any(type(b.get('branch')) is not int for b in branches)
                or {b['branch'] for b in branches} != paths):
            raise ValueError('Exactly one complete policy map per postflop branch required')
        leaves = {}
        factor = math.comb(52, 5) / math.comb(48, 5) / total_pair_mass
        for branch, policy in zip(branches, policies):
            i = branch['branch']
            self._validate_postflop(branch, policy, len(expected))
            # Each hero sees the OTHER player's preflop prefix reach here.
            reached = [weights[p] * self.reach[i][p][classes[p]] for p in (0, 1)]
            v = evaluate(tree, branch, policy, reached)
            leaves[i] = np.asarray([self._normalize(
                np.bincount(classes[h], weights=weights[h]*v[h], minlength=169)*factor, h)
                for h in (0, 1)])
        return self._project(leaves, 'one-unconditional-board-draw')

    def _validate_postflop(self, branch, policies, private_count):
        leaf = self.nodes[branch['branch']]['leaf']
        if (branch.get('offsets') != leaf['value_offsets']
                or branch.get('starting_pot') != leaf['starting_pot']):
            raise ValueError('Original postflop branch cashflow offsets required')
        nodes = branch.get('nodes')
        if not isinstance(nodes, list) or not nodes:
            raise ValueError('Complete nonempty native postflop tree required')
        seen, decisions = set(), set()
        def walk(i):
            if type(i) is not int or not 0 <= i < len(nodes) or i in seen:
                raise ValueError('Unique acyclic complete postflop nodes required')
            seen.add(i)
            node = nodes[i]
            kind, children = node.get('kind'), node.get('children', [])
            if type(kind) is not int or kind not in (0, 1, 2, 3) or not isinstance(children, list):
                raise ValueError('Recognized native postflop node required')
            if kind == 0:
                if (type(node.get('actor')) is not int or node['actor'] not in (0, 1)
                        or not 2 <= len(children) <= 4):
                    raise ValueError('Supported postflop decision required')
                decisions.add(i)
                p = np.asarray(policies[i], dtype=np.float64)
                if (p.shape != (private_count, len(children)) or not np.isfinite(p).all()
                        or np.any(p < 0) or np.max(abs(p.sum(1)-1)) > 1e-12):
                    raise ValueError('Complete finite normalized postflop policy required')
            elif kind == 1:
                if len(children) != 1:
                    raise ValueError('Fixed-board chronological chance child required')
            else:
                payouts = np.asarray(node.get('payouts'), dtype=np.float64)
                if (children or type(node.get('actor')) is not int
                        or node['actor'] not in (0, 1) or payouts.shape != (3,)
                        or not np.isfinite(payouts).all()):
                    raise ValueError('Finite native terminal payouts required')
            for child in children:
                walk(child)
        walk(0)
        if len(seen) != len(nodes) or set(policies) != decisions:
            raise ValueError('No missing or extra postflop nodes/policies')
