"""Validated adapter for the isolated fixed-board float64 terminal prototype."""
import numpy as np
from board_sorted_terminal_v1 import checked, masses as unchecked_masses, values


def masses(hero_hands, hero_ranks, opponent_hands, opponent_ranks, opponent_reach):
    h, hr = checked(hero_hands, hero_ranks)
    o, ranks = checked(opponent_hands, opponent_ranks)
    if np.any(hr < 0) or np.any(ranks < 0):
        raise ValueError('Nonnegative hand strengths required')
    lookup = dict(zip((o[:, 0] * 52 + o[:, 1]).tolist(), ranks.tolist()))
    for key, rank in zip(h[:, 0] * 52 + h[:, 1], hr):
        if key in lookup and lookup[key] != rank:
            raise ValueError('Identical holdings must have identical strength on one board')
    return unchecked_masses(h, hr, o, ranks, opponent_reach)
