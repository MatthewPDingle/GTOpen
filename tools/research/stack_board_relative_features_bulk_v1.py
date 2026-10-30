"""Batched, semantically identical 25-column visible river representation.

Research implementation candidate. No opponent cards, policy or equity input.
"""
import numpy as np
from stack_board_relative_features_v1 import WIDTH
from visible_summaries_vector_v1 import summaries


def rank_columns(cards):
    """The first fourteen qualified summary columns encode exact made-hand rank."""
    padded = np.full((len(cards), 7), 52, dtype=np.int16)
    padded[:, :cards.shape[1]] = cards
    return summaries(padded)[:, :14]


def relative_features_bulk(cards):
    """[N,7] distinct integers: two private cards followed by five river cards."""
    cards = np.asarray(cards)
    if cards.ndim != 2 or cards.shape[1] != 7 or cards.dtype.kind not in 'iu':
        raise ValueError('Seven integer visible cards required per row')
    if np.any(cards < 0) or np.any(cards >= 52):
        raise ValueError('Only visible deck cards are allowed')
    ordered = np.sort(cards, axis=1)
    if np.any(ordered[:, 1:] == ordered[:, :-1]):
        raise ValueError('Seven distinct visible cards required')
    n = len(cards)
    result = np.zeros((n, WIDTH), dtype=np.float32)
    if not n:
        return result
    board = cards[:, 2:]
    unique_boards, inverse = np.unique(np.sort(board, axis=1), axis=0, return_inverse=True)
    public = rank_columns(unique_boards)[inverse]
    full = rank_columns(cards)
    same_category = np.argmax(public[:, :9], axis=1) == np.argmax(full[:, :9], axis=1)
    plays_board = np.all(full == public, axis=1)
    relation = np.where(plays_board, 0, np.where(same_category, 1, 2))
    one_private = np.zeros(n, dtype=bool)
    for index in (0, 1):
        rank = rank_columns(np.column_stack((board, cards[:, index])))
        one_private |= np.all(rank == full, axis=1)
    minimum = np.where(plays_board, 0, np.where(one_private, 1, 2))
    result[:, :14] = public
    result[np.arange(n), 14 + relation] = 1
    result[same_category, 17:22] = full[same_category, 9:14] - public[same_category, 9:14]
    result[np.arange(n), 22 + minimum] = 1
    if not np.isfinite(result).all() or np.max(abs(result)) > 1:
        raise ValueError('Invalid relative feature values')
    return result
