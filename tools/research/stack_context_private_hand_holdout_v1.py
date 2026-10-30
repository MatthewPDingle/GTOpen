"""Explicit own-hand holdout and source routing for a future prediction study.

No scientific namespace, ratio, seed, source identity or budget is supplied by
default. Held own-hand classes are excluded from predictor fitting on ALL streets.
"""
from collections import Counter
import hashlib
import itertools
from stack_context_flop_partition_v1 import canonical_flop, encoded, visible_partition, validate as validate_flops

TYPE = 'own-169-hand-class-holdout-v1'
SOURCE_TYPE = 'disjoint-prediction-source-routing-v1'


def own_class(hand):
    if (not isinstance(hand, (list, tuple)) or len(hand) != 2
            or any(type(c) is not int or not 0 <= c < 52 for c in hand) or hand[0] == hand[1]):
        raise ValueError('Exactly two distinct visible own cards required')
    a, b = hand;lo, hi = sorted((a//4, b//4))
    return hi*13+lo if a%4 == b%4 or hi == lo else lo*13+hi


def config(*, namespace, buckets, test_buckets):
    if type(namespace) is not str or not 0 < len(namespace) <= 256:
        raise ValueError('Explicit bounded private-hand namespace required')
    if type(buckets) is not int or not 2 <= buckets <= 65536:
        raise ValueError('Explicit finite bucket count required')
    if (not isinstance(test_buckets, (list, tuple)) or not 0 < len(test_buckets) < buckets
            or any(type(b) is not int or not 0 <= b < buckets for b in test_buckets)
            or len(set(test_buckets)) != len(test_buckets)):
        raise ValueError('Distinct nonempty test and fit buckets required')
    result = dict(format=1, holdout_type=TYPE, namespace=namespace, buckets=buckets,
        test_buckets=sorted(test_buckets), unit='Acting player own 169 rank/suitedness hand class',
        exclusion='Held own-hand classes excluded from predictor fitting on every street, actor and depth',
        opponent_cards_used=False, board_cards_used=False, actor_used_in_assignment=False,
        depth_used_in_assignment=False, scientific_admission=False)
    result['sha256'] = hashlib.sha256(encoded(result)).hexdigest()
    return result


def validate(document):
    if type(document) is not dict:raise ValueError('Explicit private-hand holdout contract required')
    expected = config(namespace=document['namespace'], buckets=document['buckets'], test_buckets=document['test_buckets'])
    if document != expected:raise ValueError('Changed private-hand holdout contract')


def assignment(hand, document):
    validate(document);c = own_class(hand)
    raw = hashlib.sha256(encoded([TYPE, document['sha256'], c])).digest()
    bucket = int.from_bytes(raw, 'big') % document['buckets']
    return 'test' if bucket in document['test_buckets'] else 'fit'


def catalogue(document):
    validate(document);counts = Counter();representatives = {}
    for pair in itertools.combinations(range(52), 2):
        c = own_class(pair);counts[c] += 1;representatives.setdefault(c, list(pair))
    if len(counts) != 169 or sum(counts.values()) != 1326:raise ValueError('Incomplete physical own-hand catalogue')
    rows = [dict(hand_class=c, representative=representatives[c], physical_combos=counts[c],
        split=assignment(representatives[c], document)) for c in range(169)]
    totals = {s:sum(r['physical_combos'] for r in rows if r['split'] == s) for s in ('fit', 'test')}
    if min(totals.values()) <= 0:raise ValueError('Hand holdout must support both physical sides')
    result = dict(format=1, config=document, hand_classes=169, physical_combos=1326,
        combo_multiplicities=dict(sorted(Counter(counts.values()).items())), rows=rows,
        physical_combos_by_split=totals,
        weighting='Combinatorial catalogue only; actual entry/blocker/action source weights are separate',
        scientific_deals_sampled=False, scientific_admission=False)
    result['sha256'] = hashlib.sha256(encoded(result)).hexdigest()
    return result


def identity(value):
    if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('Explicit source SHA256 identity required')
    return value


def source_config(*, fit_source_identity, test_source_identity):
    fit, test = identity(fit_source_identity), identity(test_source_identity)
    if fit == test:raise ValueError('Fit and evaluation sources must be prospectively distinct')
    result = dict(format=1, source_type=SOURCE_TYPE, fit_source_identity=fit, test_source_identity=test,
        rule='A source can emit only its own side; no training rows taken from evaluation parent draws',
        independence_is_registration_requirement=True, scientific_admission=False)
    result['sha256'] = hashlib.sha256(encoded(result)).hexdigest()
    return result


def validate_sources(document):
    if type(document) is not dict:raise ValueError('Explicit source routing contract required')
    expected = source_config(fit_source_identity=document['fit_source_identity'], test_source_identity=document['test_source_identity'])
    if expected != document:raise ValueError('Changed immutable source routing')


def cluster_identity(source_identity, draw_index):
    identity(source_identity)
    if type(draw_index) is not int or not 0 <= draw_index < 2**63:
        raise ValueError('Original nonnegative parent draw index required')
    return hashlib.sha256(encoded([SOURCE_TYPE, source_identity, draw_index])).hexdigest()


def route(*, hand, board, phase, actor, depth_split, hand_document, flop_document,
          sources_document, source_side, draw_index):
    """Classify current visible information; future/opponent cards have no slot.

    Preflop assignment ignores future flops. All later descendants keep their
    initial public-flop split. Source-side masking prevents parent reuse across
    predictor fitting and evaluation, including the other actor's fit-like rows.
    """
    if type(phase) is not int or not 0 <= phase <= 3 or type(actor) is not int or actor not in (0, 1):
        raise ValueError('Explicit visible native street and actor required')
    if depth_split not in ('fit', 'heldout') or source_side not in ('fit', 'test'):
        raise ValueError('Registered context and source sides required')
    c = own_class(hand)
    if (not isinstance(board, (list, tuple)) or len(board) != (0, 3, 4, 5)[phase]
            or any(type(v) is not int or not 0 <= v < 52 for v in board)
            or len(set([*hand, *board])) != 2+len(board)):
        raise ValueError('Only complete distinct currently visible public cards allowed')
    validate_sources(sources_document);validate_flops(flop_document)
    own = assignment(hand, hand_document)
    public = visible_partition(board, phase=phase, document=flop_document) if phase else None
    axes = []
    if depth_split == 'heldout':axes.append('depth')
    if own == 'test':axes.append('own-hand')
    if public == 'test':axes.append('public-flop')
    label_side = 'test' if axes else 'fit'
    source = sources_document[source_side+'_source_identity']
    result = dict(format=1, phase=phase, actor=actor, hand_class=c, own_hand_split=own,
        public_flop_split=public, depth_split=depth_split, holdout_axes=axes,
        label_side=label_side, source_side=source_side, label_generation_allowed=label_side == source_side,
        source_identity=source, parent_draw_index=draw_index,
        source_cluster_identity=cluster_identity(source, draw_index),
        private_hand_config_sha256=hand_document['sha256'], public_flop_config_sha256=flop_document['sha256'],
        source_config_sha256=sources_document['sha256'], unseen_own_hand_excluded_from_all_fitting=True,
        preflop_future_board_used=False, opponent_cards_used=False,
        partition_is_metadata_not_model_input=True, scientific_admission=False)
    if phase:result['canonical_public_flop'] = list(canonical_flop(board[:3]))
    result['sha256'] = hashlib.sha256(encoded(result)).hexdigest()
    return result
