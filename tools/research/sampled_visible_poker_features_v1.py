"""Redundant visible-card summaries for a future representation experiment.

No equity, opponent cards, future cards, policy targets or Wizard data. Preserve
the original 269 lossless inputs and append these summaries; do not substitute
them for the original observation. This module is not used by an active trial.
"""
from collections import Counter
import numpy as np


CATEGORIES = ('high_card','pair','two_pair','trips','straight','flush',
              'full_house','quads','straight_flush')
FEATURE_NAMES = (
    *('made_'+x for x in CATEGORIES),
    *(f'tiebreak_{i}' for i in range(5)),
    *(f'board_rank_multiplicity_{i}' for i in range(3)),
    *(f'suit_{i}_{kind}' for i in range(4) for kind in ('board_count','hole_count')),
    'combined_straight_rank_coverage','board_straight_rank_coverage',
    'hole_overcards','hole_cards_matching_board_rank',
    'hole_pair','hole_suited','board_distinct_ranks','board_high_rank',
)
WIDTH = len(FEATURE_NAMES)
STRAIGHTS = [frozenset(range(hi-4,hi+1)) for hi in range(4,13)] + [frozenset((12,0,1,2,3))]


def _straight_high(ranks):
    for hi in range(12,3,-1):
        if all(r in ranks for r in range(hi-4,hi+1)): return hi
    return 3 if {12,0,1,2,3} <= ranks else -1


def best_visible_rank(cards):
    """Exact best-five rank of five, six or seven visible cards; higher wins."""
    cards = list(cards)
    if not 5 <= len(cards) <= 7 or any(type(c) is not int or not 0 <= c < 52 for c in cards) or len(set(cards)) != len(cards):
        raise ValueError('Five to seven distinct visible cards required')
    counts = Counter(c//4 for c in cards)
    ranks = set(counts)
    suits = [[c//4 for c in cards if c%4 == suit] for suit in range(4)]
    flush = next((sorted(rs,reverse=True) for rs in suits if len(rs)>=5),None)
    if flush is not None:
        high = _straight_high(set(flush))
        if high >= 0: return (8,high)
    quads = sorted((r for r,n in counts.items() if n==4),reverse=True)
    if quads: return (7,quads[0],max(ranks-{quads[0]}))
    trips = sorted((r for r,n in counts.items() if n>=3),reverse=True)
    if trips:
        pairs = [r for r,n in counts.items() if n>=2 and r!=trips[0]]
        if pairs: return (6,trips[0],max(pairs))
    if flush is not None: return (5,*flush[:5])
    high = _straight_high(ranks)
    if high >= 0: return (4,high)
    if trips: return (3,trips[0],*sorted(ranks-{trips[0]},reverse=True)[:2])
    pairs = sorted((r for r,n in counts.items() if n>=2),reverse=True)
    if len(pairs)>=2: return (2,*pairs[:2],max(ranks-set(pairs[:2])))
    if pairs: return (1,pairs[0],*sorted(ranks-{pairs[0]},reverse=True)[:3])
    return (0,*sorted(ranks,reverse=True)[:5])


def visible_summaries(hole, board):
    """33 suit/order-invariant summaries. Preflop additions are all zero.

    Straight coverage is a rank-pattern count, not an estimate of equity or
    clean outs. Made-hand rank includes a possible board-only hand on the river.
    Suit groups are sorted by (board count, hole count), not suit identity.
    """
    hole,board = list(hole),list(board)
    cards = hole+board
    if (len(hole)!=2 or len(board) not in (0,3,4,5)
        or any(type(c) is not int or not 0<=c<52 for c in cards)
        or len(set(cards))!=len(cards)):
        raise ValueError('Exactly two private cards and a legal visible board required')
    if not board: return np.zeros(WIDTH,dtype=np.float32)
    rank = best_visible_rank(cards)
    x = [float(i==rank[0]) for i in range(9)]
    x += [(r+1)/13 for r in rank[1:]] + [0.]*(6-len(rank))
    board_ranks = Counter(c//4 for c in board)
    multiplicities = sorted(board_ranks.values(),reverse=True)
    x += [n/4 for n in multiplicities[:3]] + [0.]*(3-min(3,len(multiplicities)))
    suit_groups = sorted(((sum(c%4==s for c in board),sum(c%4==s for c in hole)) for s in range(4)),reverse=True)
    for b,h in suit_groups: x += [b/5,h/2]
    all_ranks = {c//4 for c in cards}
    x += [max(len(all_ranks&s) for s in STRAIGHTS)/5,
          max(len(set(board_ranks)&s) for s in STRAIGHTS)/5,
          sum(c//4>max(board_ranks) for c in hole)/2,
          sum(c//4 in board_ranks for c in hole)/2,
          float(hole[0]//4==hole[1]//4),float(hole[0]%4==hole[1]%4),
          len(board_ranks)/5,(max(board_ranks)+1)/13]
    result=np.asarray(x,dtype=np.float32)
    assert result.shape==(WIDTH,) and np.isfinite(result).all() and np.all((result>=0)&(result<=1))
    return result


def from_active_features(active):
    """Decode only the existing visible input row, with no access to a deal."""
    if len(active)!=36 or len(set(active))!=36 or any(type(a) is not int or not 0<=a<269 for a in active):
        raise ValueError('Invalid original feature row')
    active=set(active)
    def one(start,width):
        selected=[a-start for a in active if start<=a<start+width]
        if len(selected)!=1: raise ValueError('Invalid one-hot group')
        return selected[0]
    cards=[]
    for i in range(7):
        rank,suit=one(i*19,14),one(i*19+14,5)
        if (rank==13)!=(suit==4): raise ValueError('Mismatched missing card')
        cards.append(None if rank==13 else rank*4+suit)
    one(133,2);phase=one(135,4);one(139,16)
    history=[one(155+i*6,6) for i in range(19)]
    end=next((i for i,h in enumerate(history) if h==0),19)
    if any(history[end:]): raise ValueError('Noncontiguous public history')
    count=(0,3,4,5)[phase]
    if any(c is None for c in cards[:2+count]) or any(c is not None for c in cards[2+count:]):
        raise ValueError('Future-card leakage or incomplete visible board')
    return visible_summaries(cards[:2],cards[2:2+count])
