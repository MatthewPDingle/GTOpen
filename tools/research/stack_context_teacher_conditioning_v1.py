"""Conditional history, opponent posterior and future-board sampling plumbing.

No teacher is selected, diagnostic is admitted, label is computed, or network
is fitted here. A caller must bind a prospectively declared teacher and budget.
Query rows contain own cards/public prefixes; hidden hypotheses stay separate.
"""
import copy
import hashlib
import itertools
import json
import math
import numpy as np
from stack_context_teacher_path_v1 import Binding, card_key, public_key, integer, encoded, advantage
from storage_strategic_common_prior_20260920 import PAIRS, CLASSES, COUNTS

TYPE = 'fixed-teacher-conditional-history-v1'
SAMPLE_TYPE = 'fixed-teacher-conditional-future-sample-v1'
ENTRY_RULE = 'PhysicalDeals v1: class mass per combo / max, inherited cutoff 1e-5'


def target_cards(hand, board, phase):
    integer(phase, 0, 3)
    # The native physical deal convention sorts the two private cards and the
    # initial flop, while retaining the chronological turn and river positions.
    card_key(hand, board, 0)
    if len(board) != (0, 3, 4, 5)[phase]:raise ValueError('Visible street length mismatch')
    return sorted(hand), [*sorted(board[:3]), *board[3:]]


def hypotheses(hand, board, phase):
    hand, board = target_cards(hand, board, phase)
    pairs = list(itertools.combinations([c for c in range(52) if c not in hand+board], 2))
    if len(pairs) != (1225, 1081, 1035, 990)[phase]:raise ValueError('Incomplete hidden domain')
    return pairs


def observation(geometry, hi, hand, board):
    row = geometry.public[hi];branch, phase, history = public_key(hi)
    lo = card_key(hand, board[:(0, 3, 4, 5)[phase]], row['actor'])
    cards = [(int(lo) >> (6*i)) & 63 for i in range(7)];active = []
    for i, card in enumerate(cards):
        active.extend((19*i+(13 if card == 63 else card//4), 19*i+14+(4 if card == 63 else card%4)))
    active.extend((133+row['actor'], 135+phase, 139+branch))
    active.extend(155+6*i+(history[i] if i < len(history) else 0) for i in range(19))
    return dict(hi=hi, lo=lo, actor=row['actor'], phase=phase, n=row['n'], active_features=active, own_history=[])


def history_queries(geometry, *, target_hi, actor, hand, board):
    """Enumerate compatible hidden hands, exporting ONLY visible policy rows."""
    if not isinstance(geometry, Binding):raise ValueError('Qualified bound public geometry required')
    integer(actor, 0, 1)
    if target_hi not in geometry.public or geometry.public[target_hi]['actor'] != actor:
        raise ValueError('Target actor/public state mismatch')
    phase = geometry.public[target_hi]['phase'];hand, board = target_cards(hand, board, phase)
    pairs = hypotheses(hand, board, phase);rows = [];lookup = {};raw = set();plans = []
    def add(hi, private):
        row = observation(geometry, hi, private, board);key = (hi, row['lo'])
        # Counting raw keys does not expose them in the model observations.
        state = geometry.public[hi];visible = board[:(0, 3, 4, 5)[state['phase']]]
        cards = [*sorted(private), *sorted(visible[:3]), *visible[3:]]+[63]*(7-2-len(visible))
        raw.add((hi, (state['actor'] << 42)+sum(c << (6*i) for i, c in enumerate(cards))))
        if key not in lookup:lookup[key] = len(rows);rows.append(row)
        return lookup[key]
    for pair in pairs:
        private = [hand, list(pair)] if actor == 0 else [list(pair), hand];path = []
        for hi, action in geometry.paths[target_hi]:
            state = geometry.public[hi];path.append([add(hi, private[state['actor']]), action, state['n']])
        plans.append(dict(cards=list(pair), path=path, target_index=add(target_hi, hand)))
    # Own ancestry is reconstructed from the CURRENT row's canonical private
    # hand/public board. It does not inspect the hidden hypothesis or future.
    for row in rows:
        cards = [(int(row['lo']) >> (6*i)) & 63 for i in range(7)]
        for hi, action in geometry.paths[row['hi']]:
            state = geometry.public[hi]
            if state['actor'] == row['actor']:
                prior = observation(geometry, hi, cards[:2], cards[2:2+(0, 3, 4, 5)[row['phase']]])
                key = (hi, prior['lo'])
                if key not in lookup:raise ValueError('Incomplete genuine own-history closure')
                row['own_history'].append([lookup[key], action, state['n']])
    target = observation(geometry, target_hi, hand, board)
    meta = dict(format=1, generator=TYPE, context_sha256=hashlib.sha256(geometry.queries['context_source'].encode()).hexdigest(),
        geometry_query_sha256=geometry.identity, target_hi=target_hi, actor=actor, hand=hand, board=board,
        phase=phase, rule='Complete compatible pair domain; chronological public actions; no hidden/future inputs')
    query = dict(format=2, context_source=geometry.queries['context_source'], batch_source=encoded(meta).decode(),
        observations=rows, raw_queries=len(raw))
    binding = Binding(query)
    index = binding.lookup[(target['hi'], target['lo'])]
    if any(p['target_index'] != index for p in plans):raise ValueError('Teacher target depends on hidden hand')
    return dict(format=1, conditioning_type=TYPE, queries=query,
        target=dict(hi=target_hi, lo=target['lo'], actor=actor, phase=phase, n=target['n'], hand=hand, board=board,
            query_index=index), hypotheses=plans, scientific_admission=False)


def entry_weights(context_source):
    """Exact inherited PhysicalDeals convention, including its existing cutoff."""
    context = json.loads(context_source);mass = np.asarray(context['incoming_class_mass'], dtype=np.float64)
    if mass.shape != (2, 169) or not np.isfinite(mass).all() or np.any(mass < 0) or np.any(mass.sum(1) <= 0):
        raise ValueError('Two nonempty finite entry ranges required')
    weights = mass[:, CLASSES]/COUNTS[CLASSES];weights /= weights.max(1)[:, None]
    weights[weights < 1e-5] = 0
    return [{tuple(map(int, pair)):float(w) for pair, w in zip(PAIRS, player)} for player in weights]


def posterior(history, frozen):
    if (history['format'] != 1 or history['conditioning_type'] != TYPE or history['scientific_admission'] is not False
            or encoded(history['queries']) != encoded(frozen.binding.queries)):
        raise ValueError('Exact frozen teacher/query binding required')
    t = history['target'];hand, board = target_cards(t['hand'], t['board'], t['phase']);hero = t['actor']
    expected = hypotheses(hand, board, t['phase'])
    if [tuple(p['cards']) for p in history['hypotheses']] != expected:
        raise ValueError('Complete ordered compatible hidden hypotheses required')
    source = history['queries']['context_source'];context = json.loads(source);entry = entry_weights(source)
    p = frozen.p;rows = frozen.binding.queries['observations'];mass = [];own = []
    for pair in history['hypotheses']:
        private = [*hand, *pair['cards']] if hero == 0 else [*pair['cards'], *hand]
        known = private+board;available = [c for c in range(52) if c not in known]
        # Filler is used ONLY to bind already-visible history keys. No future
        # query is exported, inferred, or conditioned on these arbitrary cards.
        deal = known+available[:5-len(board)]
        index, path = frozen.binding.trace(deal, t['hi'])
        if index != t['query_index'] or index != pair['target_index'] or path != pair['path']:
            raise ValueError('Changed target or chronological hidden-hand path')
        w = entry[1-hero][tuple(pair['cards'])];my = 1.
        for i, a, _ in path:
            if rows[i]['actor'] == hero:my *= float(p[i, a])
            else:w *= float(p[i, a])
        mass.append(w);own.append(my)
    if max(own)-min(own) > 1e-12:raise ValueError('Own history depends on opponent cards')
    total = math.fsum(mass)
    if not math.isfinite(total) or total <= 0:raise ValueError('Unsupported opponent posterior')
    probability = np.asarray(mass, dtype=np.float64)/total
    sigma = p[t['query_index'], :t['n']].copy()
    result = dict(format=1, posterior_type=TYPE, target=copy.deepcopy(t), probabilities=probability.tolist(),
        opponent_mass=total, own_history_likelihood=own[0], hero_entry_mass=entry[hero][tuple(hand)],
        teacher_state_supported=bool(own[0] > 0 and entry[hero][tuple(hand)] > 0), original_sigma=sigma.tolist(),
        context_source=source, frozen_teacher_probability_sha256=frozen.identity,
        entry_rule=ENTRY_RULE,
        fixed_teacher_scientifically_admitted=False)
    result['sha256'] = hashlib.sha256(encoded(result)).hexdigest()
    return result


def validate_posterior(document):
    if (set(document) != {'format', 'posterior_type', 'target', 'probabilities', 'opponent_mass',
            'own_history_likelihood', 'hero_entry_mass', 'teacher_state_supported', 'original_sigma',
            'context_source', 'frozen_teacher_probability_sha256', 'entry_rule',
            'fixed_teacher_scientifically_admitted', 'sha256'}
            or document.get('format') != 1 or document.get('posterior_type') != TYPE):
        raise ValueError('Explicit conditional posterior required')
    raw = dict(document);identity = raw.pop('sha256')
    if hashlib.sha256(encoded(raw)).hexdigest() != identity:raise ValueError('Changed conditional posterior')
    t = document['target']
    if set(t) != {'hi', 'lo', 'actor', 'phase', 'n', 'hand', 'board', 'query_index'}:
        raise ValueError('Explicit visible target contract required')
    integer(t['actor'], 0, 1);integer(t['n'], 2, 4);integer(t['query_index'], 0, 1_000_000)
    hand, board = target_cards(t['hand'], t['board'], t['phase'])
    branch, phase, _ = public_key(t['hi'])
    if phase != t['phase'] or t['lo'] != card_key(hand, board, t['actor']):
        raise ValueError('Visible target key mismatch')
    pairs = hypotheses(hand, board, t['phase']);p = np.asarray(document['probabilities'], dtype=np.float64)
    if p.shape != (len(pairs),) or not np.isfinite(p).all() or np.any(p < 0) or abs(math.fsum(p)-1) > 1e-12:
        raise ValueError('Normalized complete posterior required')
    sigma = np.asarray(document['original_sigma'], dtype=np.float64)
    if sigma.shape != (t['n'],) or not np.isfinite(sigma).all() or np.any(sigma < 0) or abs(math.fsum(sigma)-1) > 1e-12:
        raise ValueError('Original target sigma required')
    context = json.loads(document['context_source'])
    if context.get('schema') != 'hu-context-v1' or context.get('positions') != ['BB', 'BTN']:
        raise ValueError('Same heads-up context required')
    if branch >= len(context['nodes']):raise ValueError('Unknown target branch')
    node = context['nodes'][branch]
    if (not phase and (node['kind'] != 0 or node['actor'] != t['actor'] or len(node['actions']) != t['n'])
            or phase and (node['kind'] != 2 or node['leaf']['type'] != 'postflop')):
        raise ValueError('Target differs from context geometry')
    for field in ('opponent_mass', 'own_history_likelihood', 'hero_entry_mass'):
        v = document[field]
        if type(v) not in (float, int) or not math.isfinite(v) or v < 0:
            raise ValueError('Invalid teacher likelihood/mass')
    if (document['opponent_mass'] <= 0 or document['own_history_likelihood'] > 1 or document['hero_entry_mass'] > 1
            or type(document['teacher_state_supported']) is not bool
            or document['teacher_state_supported'] != (document['own_history_likelihood'] > 0 and document['hero_entry_mass'] > 0)
            or document['entry_rule'] != ENTRY_RULE or document['fixed_teacher_scientifically_admitted'] is not False):
        raise ValueError('Inconsistent conditional scope or inherited entry convention')
    identity = document['frozen_teacher_probability_sha256']
    if not isinstance(identity, str) or len(identity) != 64 or any(c not in '0123456789abcdef' for c in identity):
        raise ValueError('Frozen teacher probability identity required')
    for field in ('stack',):
        v = context['config'][field]
        if type(v) not in (float, int) or not math.isfinite(v) or v <= 0:raise ValueError('Positive original stack required')
    dead = context['dead_money']
    if type(dead) not in (float, int) or not math.isfinite(dead) or dead < 0:raise ValueError('Finite dead money required')
    return pairs, p


def future_domain(hand, pair, board, phase):
    hand, board = target_cards(hand, board, phase)
    if (len(pair) != 2 or any(type(c) is not int or not 0 <= c < 52 for c in pair)
            or pair[0] >= pair[1] or any(c in hand+board for c in pair)):
        raise ValueError('Compatible sorted hidden pair required')
    remaining = [c for c in range(52) if c not in [*hand, *pair, *board]]
    count = (math.comb(48, 3)*45*44, 45*44, 44, 1)[phase]
    return dict(remaining=remaining, unknown_cards=5-len(board), distinct_runouts=count,
        rule='Uniform physical flop set then ordered turn/river; no split conditioning')


class ConditionalSampler:
    """Explicit local RNG; reproducible plans shared across every legal action."""
    def __init__(self, document, *, seed):
        if type(seed) is not int or seed < 0:raise ValueError('Explicit nonnegative stream seed required')
        self.pairs, self.probability = validate_posterior(document);self.document = copy.deepcopy(document)
        self.rng = np.random.Generator(np.random.PCG64(seed));self.draws = 0

    def sample(self, count):
        integer(count, 0, 65536);start = self.checkpoint();t = self.document['target'];plans = [];indices = []
        for _ in range(count):
            index = int(self.rng.choice(len(self.pairs), p=self.probability));pair = self.pairs[index]
            domain = future_domain(t['hand'], pair, t['board'], t['phase'])
            future = [int(c) for c in self.rng.choice(domain['remaining'], size=domain['unknown_cards'], replace=False)]
            private = [*t['hand'], *pair] if t['actor'] == 0 else [*pair, *t['hand']]
            board = [*t['board'], *future];board[:3] = sorted(board[:3])
            plans.append(private+board);indices.append(index)
        self.draws += count
        return dict(format=1, sample_type=SAMPLE_TYPE, posterior_sha256=self.document['sha256'],
            draw_count=count, opponent_pair_indices=indices, deals=plans,
            start_state_sha256=hashlib.sha256(encoded(start)).hexdigest(),
            end_state_sha256=hashlib.sha256(encoded(self.checkpoint())).hexdigest(),
            reduction='Arithmetic mean; do not multiply source/posterior weights again')

    def checkpoint(self):
        return dict(format=1, sample_type=SAMPLE_TYPE, posterior_sha256=self.document['sha256'],
            numpy_version=np.__version__, draws=self.draws, rng=copy.deepcopy(self.rng.bit_generator.state))

    @classmethod
    def restore(cls, state, document):
        if (set(state) != {'format', 'sample_type', 'posterior_sha256', 'numpy_version', 'draws', 'rng'}
                or state['format'] != 1 or state['sample_type'] != SAMPLE_TYPE or state['numpy_version'] != np.__version__
                or state['posterior_sha256'] != document['sha256']):
            raise ValueError('Changed conditional stream identity/runtime')
        if type(state['draws']) is not int or state['draws'] < 0:raise ValueError('Invalid draw counter')
        result = cls(document, seed=0);result.draws = state['draws'];result.rng.bit_generator.state = copy.deepcopy(state['rng'])
        return result


def audit_plan(document, plan, start_state):
    if (set(plan) != {'format', 'sample_type', 'posterior_sha256', 'draw_count', 'opponent_pair_indices', 'deals',
            'start_state_sha256', 'end_state_sha256', 'reduction'}
            or plan['start_state_sha256'] != hashlib.sha256(encoded(start_state)).hexdigest()):
        raise ValueError('Original conditional chance checkpoint required')
    regenerated = ConditionalSampler.restore(start_state, document).sample(plan['draw_count'])
    if encoded(regenerated) != encoded(plan):raise ValueError('Changed conditional chance stream or plan')


def sampled_advantage(document, plan, values, *, start_state):
    audit_plan(document, plan, start_state)
    pairs, _ = validate_posterior(document);t = document['target']
    if (plan.get('format') != 1 or plan.get('sample_type') != SAMPLE_TYPE or plan.get('posterior_sha256') != document['sha256']
            or type(plan.get('draw_count')) is not int or not 1 <= plan['draw_count'] <= 65536
            or len(plan['deals']) != plan['draw_count'] or len(plan['opponent_pair_indices']) != plan['draw_count']):
        raise ValueError('Complete matching conditional sample plan required')
    for deal, index in zip(plan['deals'], plan['opponent_pair_indices']):
        integer(index, 0, len(pairs)-1)
        if document['probabilities'][index] <= 0:raise ValueError('Sampled unsupported hidden hand')
        if (len(deal) != 9 or any(type(c) is not int or not 0 <= c < 52 for c in deal) or len(set(deal)) != 9
                or deal[2*t['actor']:2*t['actor']+2] != t['hand']
                or tuple(deal[2*(1-t['actor']):2*(1-t['actor'])+2]) != pairs[index]
                or deal[4:4+len(t['board'])] != t['board'] or deal[4:7] != sorted(deal[4:7])):
            raise ValueError('Sample physical deal, visible information or hidden pair changed')
    q = np.asarray(values, dtype=np.float64);context = json.loads(document['context_source'])
    stack, dead = context['config']['stack'], context['dead_money']
    if (q.shape != (plan['draw_count'], t['n']) or not np.isfinite(q).all()
            or np.any(q < -stack-1e-9) or np.any(q > stack+dead+1e-9)):
        raise ValueError('Finite legal action values within original chip bounds required')
    # Repeated draws retain multiplicity. These draws ALREADY follow the
    # conditional law; no additional posterior, entry or arrival weight applies.
    mean = np.asarray([math.fsum(q[:, a])/plan['draw_count'] for a in range(t['n'])])
    return advantage(mean, document['original_sigma'], starting_stack=stack)
