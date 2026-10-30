"""Suit-invariant public-flop partitions, independent of all private cards.

No default scientific split, seed, sampling or outcome selection is provided.
Every descendant keeps the initial flop's partition. Preflop needs its own
prospectively declared holdout; a hidden future flop cannot stand in for one.
"""
from collections import Counter
import hashlib
import itertools
import json

TYPE = 'public-canonical-flop-partition-v1'
SUITS = tuple(itertools.permutations(range(4)))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def checked_cards(cards, count):
    require(type(cards) in (list, tuple) and len(cards) == count,
        'Exactly the visible public cards for this street are required')
    require(all(type(c) is int and 0 <= c < 52 for c in cards)
        and len(set(cards)) == count, 'Distinct physical card integers required')
    return tuple(cards)


def canonical_flop(cards):
    flop = checked_cards(cards, 3)
    return min(tuple(sorted(4*(c//4)+permutation[c%4] for c in flop)) for permutation in SUITS)


def config(*, namespace, buckets, test_buckets):
    require(type(namespace) is str and 0 < len(namespace) <= 256,
        'Explicit bounded partition namespace required')
    require(type(buckets) is int and 2 <= buckets <= 65536,
        'Explicit finite bucket count required')
    require(type(test_buckets) in (list, tuple) and 0 < len(test_buckets) < buckets
        and all(type(b) is int and 0 <= b < buckets for b in test_buckets)
        and len(set(test_buckets)) == len(test_buckets), 'Nonempty distinct test and fit buckets required')
    document = dict(format=1, partition_type=TYPE, namespace=namespace, buckets=buckets,
        test_buckets=sorted(test_buckets), unit='Public initial flop modulo all 24 suit permutations',
        private_cards_used=False, future_cards_used=False, preflop_partition_defined=False)
    document['sha256'] = hashlib.sha256(encoded(document)).hexdigest()
    return document


def validate(document):
    require(type(document) is dict and set(document) == {'format', 'partition_type', 'namespace', 'buckets',
        'test_buckets', 'unit', 'private_cards_used', 'future_cards_used', 'preflop_partition_defined', 'sha256'},
        'Unexpected partition contract')
    expected = config(namespace=document['namespace'], buckets=document['buckets'], test_buckets=document['test_buckets'])
    require(document == expected, 'Changed partition configuration or identity')


def assignment(canonical, document):
    key = checked_cards(canonical, 3)
    require(key == canonical_flop(key), 'Canonical public flop key required')
    validate(document)
    identity = hashlib.sha256(encoded([TYPE, document['sha256'], list(key)])).digest()
    bucket = int.from_bytes(identity, 'big') % document['buckets']
    return 'test' if bucket in document['test_buckets'] else 'fit'


def visible_partition(board, *, phase, document):
    require(type(phase) is int and phase in (1, 2, 3),
        'Postflop only; preflop requires a separate declared holdout')
    public = checked_cards(board, (3, 4, 5)[phase-1])
    return assignment(canonical_flop(public[:3]), document)


def population(document):
    """Exhaustive public geometry, not a sampled scientific hand population."""
    validate(document)
    multiplicity = Counter(canonical_flop(flop) for flop in itertools.combinations(range(52), 3))
    rows = [dict(canonical_flop=list(key), physical_flops=count, split=assignment(key, document))
        for key, count in sorted(multiplicity.items())]
    totals = {split:sum(row['physical_flops'] for row in rows if row['split'] == split) for split in ('fit', 'test')}
    require(all(count > 0 for count in totals.values()), 'Physical fit and test populations must both be supported')
    require(len(rows) == 1755 and sum(totals.values()) == 22100, 'Incomplete exhaustive flop geometry')
    result = dict(format=1, config=document, canonical_flops=len(rows), physical_flops=22100,
        canonical_orbit_multiplicities=dict(sorted(Counter(multiplicity.values()).items())),
        physical_population_by_split=totals, rows=rows,
        weighting='Conditional full-deck flop frequency within each partition; canonical rows are not uniformly weighted',
        no_scientific_deals_sampled=True, no_private_cards_used=True)
    result['sha256'] = hashlib.sha256(encoded(result)).hexdigest()
    return result
