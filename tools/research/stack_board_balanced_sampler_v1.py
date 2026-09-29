"""Deterministic visible-card board sampler; no labels, fitting, or I/O.

Cell = descending rank multiplicities and maximum suit occupancy.  Feasible
cells are ordered lexicographically by the multiplicity tuple, then numerically
by suit occupancy.  Equal allocation gives the first remainder cells one extra.

Random candidates use random.sample(range(52), 5): uniform ordered physical
deals.  Structured candidates choose ordered distinct rank slots uniformly,
then choose uniformly among *all* suit-subset assignments for that cell, then
uniformly shuffle the five cards.  Each physical unordered board has the same
product of factorials of repeated multiplicities representations.  This proves
uniform physical-board probability within a cell before exclusion.  Rejection
of already-used suit-equivalence groups preserves this conditional physical
distribution, but does NOT make canonical groups uniform.  Equal cell quotas
deliberately change the natural distribution.  Turn and river positions remain
random; the board list is not sorted after selection.

Every new split excludes the supplied historical union and all earlier retained
groups, including across different cells/splits.  The caller owns and hashes
that historical union and the reused original 512 fitting boards.  This module
does not discover manifests or silently add/recover historical boards.

Bound: at most 100,000 candidates overall, 10,000 per random split or structured
cell bucket, and at most 200,000 exclusion entries.  A bound failure raises and
returns no partial selection.  No silent retry, reseeding, or quota relaxation.
Exact replay requires the same Python random implementation/version, source,
seed, and exclusion union; freeze those and the returned board list externally.
"""

from collections import Counter
from collections.abc import Collection
from functools import lru_cache
from itertools import combinations, product
import random

from stack_price_reference_v1 import board_group

METHOD = "stack_board_balanced_sampler_v1"
SPLIT_SIZES = (
    ("fit_random", 512),
    ("fit_structured", 512),
    ("validation", 128),
    ("test", 128),
    ("stress", 64),
)
STRUCTURED_SPLITS = frozenset(("fit_structured", "stress"))
MAX_CANDIDATES = 100_000
MAX_CANDIDATES_PER_BUCKET = 10_000
MAX_EXCLUDED_GROUPS = 200_000
RANK_MULTIPLICITIES = (
    (1, 1, 1, 1, 1), (2, 1, 1, 1), (2, 2, 1),
    (3, 1, 1), (3, 2), (4, 1),
)


class SelectionExhausted(RuntimeError):
    """A deterministic draw budget was exhausted; no result is admitted."""


def _validate_board(board):
    if (not isinstance(board, (list, tuple)) or len(board) != 5
            or any(type(card) is not int or not 0 <= card < 52 for card in board)
            or len(set(board)) != 5):
        raise ValueError("Five distinct integer cards in [0, 52) required")


def _cell_name(multiplicities, max_suit):
    return "-".join(map(str, multiplicities)) + "|s" + str(max_suit)


def board_cell(board):
    """Return the visible-card cell; invalid boards fail before computation."""
    _validate_board(board)
    multiplicities = tuple(sorted(Counter(card // 4 for card in board).values(), reverse=True))
    max_suit = max(Counter(card % 4 for card in board).values())
    return _cell_name(multiplicities, max_suit)


@lru_cache(maxsize=1)
def _catalog():
    """Immutable exact suit-subset catalog; only 1,644 templates in total."""
    rows = []
    for multiplicities in RANK_MULTIPLICITIES:
        by_max_suit = {}
        choices = [tuple(combinations(range(4), n)) for n in multiplicities]
        for suit_subsets in product(*choices):
            max_suit = max(Counter(suit for subset in suit_subsets for suit in subset).values())
            by_max_suit.setdefault(max_suit, []).append(suit_subsets)
        for max_suit, templates in sorted(by_max_suit.items()):
            rows.append((_cell_name(multiplicities, max_suit), multiplicities, tuple(templates)))
    return tuple(rows)


def feasible_cells():
    """Return a fresh list in the frozen allocation order."""
    return [cell for cell, _, _ in _catalog()]


def allocation(count):
    """Exact equal-cell quota with deterministic first-cell remainder."""
    if type(count) is not int or not 0 <= count <= 1_000_000:
        raise ValueError("Allocation requires an integer count in [0, 1000000]")
    cells = feasible_cells()
    base, remainder = divmod(count, len(cells))
    return {cell: base + (index < remainder) for index, cell in enumerate(cells)}


def _validated_exclusions(excluded_groups):
    if (not isinstance(excluded_groups, Collection)
            or isinstance(excluded_groups, (str, bytes, dict))
            or len(excluded_groups) > MAX_EXCLUDED_GROUPS):
        raise ValueError("A bounded collection of canonical 5-card groups is required")
    groups = set()
    for group in excluded_groups:
        _validate_board(group)
        group = tuple(group)
        if group != board_group(group):
            raise ValueError("Exclusions must be canonical board_group outputs")
        groups.add(group)
    return groups


def _validate_seed(seed):
    if type(seed) is not int or not 0 <= seed < 2**64:
        raise ValueError("Seed must be an integer in [0, 2**64)")


def _structured_candidate(rng, multiplicities, templates):
    ranks = rng.sample(range(13), len(multiplicities))
    suit_subsets = templates[rng.randrange(len(templates))]
    board = [4 * rank + suit for rank, suits in zip(ranks, suit_subsets) for suit in suits]
    rng.shuffle(board)
    return board


def _select(seed, excluded_groups, split_sizes, *, max_candidates, max_bucket_candidates):
    """Shared bounded engine; nonstandard sizes are solely for CPU fixtures."""
    _validate_seed(seed)
    if (type(max_candidates) is not int or max_candidates < 1
            or type(max_bucket_candidates) is not int or max_bucket_candidates < 1):
        raise ValueError("Positive integer candidate budgets required")
    if tuple(name for name, _ in split_sizes) != tuple(name for name, _ in SPLIT_SIZES):
        raise ValueError("All five split names in frozen order required")
    if any(type(count) is not int or not 0 <= count <= 1024 for _, count in split_sizes):
        raise ValueError("Each split count must be an integer in [0, 1024]")
    used = _validated_exclusions(excluded_groups)
    rng = random.Random(seed)
    catalog = {cell: (multiplicities, templates) for cell, multiplicities, templates in _catalog()}
    records = []
    attempts = 0
    for split, count in split_sizes:
        buckets = allocation(count).items() if split in STRUCTURED_SPLITS else ((None, count),)
        index = 0
        for cell, quota in buckets:
            accepted = 0
            bucket_attempts = 0
            while accepted < quota:
                if attempts >= max_candidates or bucket_attempts >= max_bucket_candidates:
                    raise SelectionExhausted(
                        f"Candidate budget exhausted: split={split}, cell={cell}, "
                        f"accepted={accepted}/{quota}, attempts={attempts}, "
                        f"bucket_attempts={bucket_attempts}; no result admitted")
                attempts += 1
                bucket_attempts += 1
                board = (rng.sample(range(52), 5) if cell is None else
                         _structured_candidate(rng, *catalog[cell]))
                group = board_group(board)
                if group in used:
                    continue
                actual_cell = board_cell(board)
                if cell is not None and actual_cell != cell:
                    raise RuntimeError("Internal constructed-cell mismatch")
                used.add(group)
                records.append(dict(split=split, index=index, board=board,
                                    canonical_group=list(group), cell=actual_cell))
                index += 1
                accepted += 1
    return records


def select_boards(seed, excluded_groups, *, counts=None):
    """Select 1,344 mutually suit-disjoint new boards in the five fixed splits.

    ``excluded_groups`` is a list/tuple/set/frozenset (or other finite Collection)
    of canonical five-integer tuples/lists returned by the reference board_group.
    Inputs are not mutated.  Records contain split, index, board, canonical_group,
    and cell; both board and canonical_group are JSON-compatible integer lists.
    ``counts=None`` fixes the scientific split sizes.  For bounded controls only,
    counts may be a dict containing all five split names, each integer value
    between zero and that split's frozen scientific size.  A reduced-count result
    is a fixture, not a scientific board list.  Dict insertion order is ignored.
    This function performs no I/O and evaluates no poker hands or equity labels.
    """
    sizes = SPLIT_SIZES
    if counts is not None:
        if (not isinstance(counts, dict) or set(counts) != {name for name, _ in SPLIT_SIZES}
                or any(type(counts[name]) is not int or not 0 <= counts[name] <= maximum
                       for name, maximum in SPLIT_SIZES)):
            raise ValueError("Control counts require every split name and integer values within frozen sizes")
        sizes = tuple((name, counts[name]) for name, _ in SPLIT_SIZES)
    return _select(seed, excluded_groups, sizes, max_candidates=MAX_CANDIDATES,
                   max_bucket_candidates=MAX_CANDIDATES_PER_BUCKET)
