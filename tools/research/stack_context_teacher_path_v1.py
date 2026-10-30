"""Visible path binding and fixed-policy intervention for action-value labels.

This is transport plumbing, not a target sampler or an admitted experiment.
Infer the teacher BEFORE forcing the path. Pass the returned profile to the
existing root evaluator on the same physical deal; aggregate conditional hidden
cards and future boards separately. Never feed label-only deals to a network.
"""
import copy
import hashlib
import itertools
import json
import math
import numpy as np

SUITS = tuple(itertools.permutations(range(4)))


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def integer(value, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError('Explicit bounded integer required')
    return value


def public_key(value):
    if not isinstance(value, str) or not value.isdecimal() or str(int(value)) != value:
        raise ValueError('Canonical serialized public key required')
    hi = int(value)
    if not 0 < hi < 2**64:raise ValueError('Public key out of range')
    if hi < 2**63:
        if hi > 16:raise ValueError('Invalid preflop node')
        return hi-1, 0, ()
    branch, h, tokens = hi & 15, (hi & (2**63-1)) >> 4, []
    while h > 1:
        token = h & 7
        if not 1 <= token <= 5:raise ValueError('Invalid public action token')
        tokens.append(token);h >>= 3
    if h != 1 or len(tokens) > 19:raise ValueError('Invalid public history root')
    tokens.reverse();phase = 1+tokens.count(5)
    if phase > 3:raise ValueError('Too many board transitions')
    return branch, phase, tuple(tokens)


def card_key(hand, board, actor):
    integer(actor, 0, 1)
    if len(hand) != 2 or len(board) not in (0, 3, 4, 5):
        raise ValueError('Only complete visible streets are allowed')
    cards = [*hand, *board]
    for card in cards:integer(card, 0, 51)
    if len(set(cards)) != len(cards):raise ValueError('Distinct visible cards required')
    padded = cards+[63]*(7-len(cards));best = None
    for suits in SUITS:
        current = [63 if c == 63 else 4*(c//4)+suits[c%4] for c in padded]
        current[:2] = sorted(current[:2]);current[2:5] = sorted(current[2:5])
        lo = (actor << 42)+sum(c << (6*i) for i, c in enumerate(current))
        best = lo if best is None else min(best, lo)
    return str(best)


def visible_cards(row):
    lo = row['lo']
    if not isinstance(lo, str) or not lo.isdecimal() or str(int(lo)) != lo or not 0 <= int(lo) < 2**43:
        raise ValueError('Canonical serialized card key required')
    cards = [(int(lo) >> (6*i)) & 63 for i in range(7)]
    actor = (int(lo) >> 42) & 1
    phase = row['phase'];integer(phase, 0, 3)
    nvisible = (2, 5, 6, 7)[phase]
    if (actor != row['actor'] or any(c >= 52 for c in cards[:nvisible])
            or any(c != 63 for c in cards[nvisible:])):
        raise ValueError('Actor, visible street or future-card padding mismatch')
    if lo != card_key(cards[:2], cards[2:nvisible], actor):
        raise ValueError('Noncanonical or duplicate visible cards')
    return cards[:2], cards[2:nvisible]


class Binding:
    """Bind chronological BOTH-player paths to a retained native query batch."""
    def __init__(self, queries):
        self.queries = copy.deepcopy(queries)
        source = self.queries['context_source'];context = json.loads(source)
        if context.get('schema') != 'hu-context-v1' or context.get('positions') != ['BB', 'BTN']:
            raise ValueError('Explicit heads-up BB/BTN context required')
        nodes = context['nodes']
        if not 1 <= len(nodes) <= 16:raise ValueError('Unsupported native context')
        parents = {};self.pre = {};self.nodes = nodes
        for node, row in enumerate(nodes):
            integer(row['kind'], 0, 2)
            if row['kind'] == 0:
                integer(row['actor'], 0, 1);n = len(row['children'])
                if not 2 <= n <= 4 or n != len(row['actions']):raise ValueError('Invalid preflop menu')
                self.pre[str(node+1)] = dict(actor=row['actor'], phase=0, n=n)
                for action, child in enumerate(row['children']):
                    integer(child, 0, len(nodes)-1)
                    if child in parents:raise ValueError('Context must be a tree')
                    parents[child] = (node, action)
            elif row['kind'] not in (1, 2) or row['children'] or row['actions']:
                raise ValueError('Invalid terminal or postflop context node')
        if 0 in parents or set(parents) != set(range(1, len(nodes))):
            raise ValueError('Every context node must descend from root zero')
        self.prepaths = {}
        for node in range(len(nodes)):
            path = [];seen = set();current = node
            while current:
                if current in seen:raise ValueError('Cyclic context')
                seen.add(current);parent, action = parents[current]
                path.append((str(parent+1), action));current = parent
            self.prepaths[node] = tuple(reversed(path))
        rows = self.queries['observations']
        if not rows:raise ValueError('Nonempty native batch required')
        self.public = dict(self.pre);self.lookup = {};self.cards = [];self.paths = {}
        for index, row in enumerate(rows):
            integer(row['actor'], 0, 1);integer(row['n'], 2, 4)
            if (not isinstance(row['own_history'], list) or any(not isinstance(item, list) or len(item) != 3
                    or any(type(v) is not int for v in item) for item in row['own_history'])
                    or any(type(v) is not int for v in row['active_features'])):
                raise ValueError('Native links and feature indices require explicit integers')
            branch, phase, history = public_key(row['hi'])
            if phase != row['phase'] or branch >= len(nodes):raise ValueError('Public street or branch mismatch')
            if phase and (nodes[branch]['kind'] != 2 or nodes[branch]['leaf']['type'] != 'postflop'):
                raise ValueError('Postflop history must start from an actual postflop branch')
            geometry = dict(actor=row['actor'], phase=phase, n=row['n'])
            if row['hi'] in self.public and self.public[row['hi']] != geometry:
                raise ValueError('Conflicting public geometry')
            if not phase and row['hi'] not in self.pre:raise ValueError('Not a preflop decision')
            self.public[row['hi']] = geometry
            key = (row['hi'], row['lo'])
            if key in self.lookup:raise ValueError('Duplicate canonical query')
            self.lookup[key] = index;hand, board = visible_cards(row);self.cards.append((hand, board))
            # Independently reconstruct the original 269-input one-hot groups.
            cards = [*hand, *board]+[63]*(7-len(hand)-len(board));active = []
            for i, card in enumerate(cards):
                active.extend((19*i+(13 if card == 63 else card//4),
                    19*i+14+(4 if card == 63 else card%4)))
            active.extend((133+row['actor'], 135+phase, 139+branch))
            active.extend(155+6*i+(history[i] if i < len(history) else 0) for i in range(19))
            if row['active_features'] != active:raise ValueError('Native visible features do not bind the key')
        for hi in self.public:self.paths[hi] = self._path(hi)
        for index, row in enumerate(rows):
            hand, board = self.cards[index];expected = []
            for hi, action in self.paths[row['hi']]:
                ancestor = self.public[hi]
                if ancestor['actor'] != row['actor']:continue
                count = (0, 3, 4, 5)[ancestor['phase']]
                prior = self._index(hi, hand, board[:count])
                expected.append([prior, action, ancestor['n']])
            if row['own_history'] != expected:raise ValueError('Native own history is incomplete or out of order')
        self.identity = hashlib.sha256(encoded(self.queries)).hexdigest()

    def _path(self, hi):
        branch, phase, tokens = public_key(hi);path = list(self.prepaths[branch])
        if not phase:return tuple(path)
        prefix = 1;current_phase = 1
        for token in tokens:
            previous = str(2**63+(prefix << 4)+branch)
            if token == 5:
                if previous in self.public:raise ValueError('Board transition at a decision')
                current_phase += 1
                if str(2**63+(((prefix << 3)|5) << 4)+branch) not in self.public:
                    raise ValueError('Missing decision after board transition')
            else:
                if previous not in self.public:raise ValueError('Missing previous public decision')
                row = self.public[previous]
                if row['phase'] != current_phase or token > row['n']:
                    raise ValueError('Illegal chronological action')
                path.append((previous, token-1))
            prefix = (prefix << 3)|token
        if current_phase != phase:raise ValueError('Public board transition mismatch')
        return tuple(path)

    def _index(self, hi, hand, board):
        key = (hi, card_key(hand, board, self.public[hi]['actor']))
        if key not in self.lookup:raise ValueError('Missing physical visible query')
        return self.lookup[key]

    def trace(self, deal, target_hi):
        """Deal is LABEL-ONLY. Query keys use only own cards and visible prefix."""
        if len(deal) != 9:raise ValueError('A full conditional evaluator deal is required')
        for card in deal:integer(card, 0, 51)
        if len(set(deal)) != 9:raise ValueError('Distinct physical deal required')
        if target_hi not in self.paths:raise ValueError('Unknown target decision')
        result = []
        for hi, action in self.paths[target_hi]:
            row = self.public[hi];actor = row['actor'];count = (0, 3, 4, 5)[row['phase']]
            result.append([self._index(hi, deal[2*actor:2*actor+2], deal[4:4+count]), action, row['n']])
        row = self.public[target_hi];actor = row['actor'];count = (0, 3, 4, 5)[row['phase']]
        target = self._index(target_hi, deal[2*actor:2*actor+2], deal[4:4+count])
        if target in {i for i, _, _ in result}:raise ValueError('Target cannot occur in its past')
        return target, result

    def freeze(self, probabilities):return FrozenTeacher(self, probabilities)


class FrozenTeacher:
    def __init__(self, binding, probabilities):
        p = np.asarray(probabilities, dtype=np.float64).copy()
        rows = binding.queries['observations'];legal = np.arange(4)[None, :] < np.array([r['n'] for r in rows])[:, None]
        if (p.shape != legal.shape or not np.isfinite(p).all() or np.any(p < 0)
                or np.any(p[~legal]) or np.max(abs(p.sum(1)-1)) > 1e-12):
            raise ValueError('Complete normalized fixed-teacher policy required')
        p.flags.writeable = False;self.p = p;self.binding = binding
        self.identity = hashlib.sha256(binding.identity.encode()+p.tobytes()).hexdigest()

    def intervene(self, deal, target_hi, action):
        """Force BOTH players' entire past and one target action; freeze future."""
        target, path = self.binding.trace(deal, target_hi);rows = self.binding.queries['observations']
        integer(action, 0, rows[target]['n']-1)
        profile = self.p.copy();likelihood = [1., 1.]
        for index, previous, _ in path:
            likelihood[rows[index]['actor']] *= float(self.p[index, previous])
            profile[index] = 0.;profile[index, previous] = 1.
        profile[target] = 0.;profile[target, action] = 1.;profile.flags.writeable = False
        return dict(probabilities=profile, target_index=target, path=path,
            original_sigma=self.p[target].copy(), original_path_likelihood_by_actor=likelihood,
            frozen_teacher_sha256=self.identity,
            scope='label-only path intervention; conditional hidden cards and future boards not integrated')


def advantage(action_values, sigma, *, starting_stack):
    """Same fixed teacher's Q minus its baseline, normalized by original stack."""
    q, p = np.asarray(action_values, dtype=np.float64), np.asarray(sigma, dtype=np.float64)
    if (q.ndim != 1 or len(q) not in (2, 3, 4) or p.shape != q.shape or not np.isfinite(q).all()
            or not np.isfinite(p).all() or np.any(p < 0) or abs(math.fsum(p)-1) > 1e-12
            or type(starting_stack) not in (float, int) or not math.isfinite(starting_stack) or starting_stack <= 0):
        raise ValueError('Finite legal action values, original teacher sigma and positive stack required')
    baseline = math.fsum(float(x*y) for x, y in zip(q, p))
    return dict(action_values=q.copy(), value=baseline, advantage=(q-baseline)/starting_stack)
