"""25 redundant visible-only river features; no opponent range or equity input."""
import numpy as np
from sampled_visible_poker_features_v1 import best_visible_rank,CATEGORIES

NAMES=(*('board_'+c for c in CATEGORIES),*(f'board_tiebreak_{i}' for i in range(5)),
    'plays_board','same_category_better_kickers','improves_category',
    *(f'same_category_tiebreak_delta_{i}' for i in range(5)),
    'minimum_private_cards_0','minimum_private_cards_1','minimum_private_cards_2')
WIDTH=len(NAMES)
assert WIDTH==25

def relative_features(hole,board):
    hole,board=list(hole),list(board);cards=hole+board
    if len(hole)!=2 or len(board)!=5 or any(type(c) is not int or not 0<=c<52 for c in cards) or len(set(cards))!=7:
        raise ValueError('Two private cards and five distinct visible river cards required')
    public=best_visible_rank(board);full=best_visible_rank(cards)
    assert full>=public
    relation=0 if full==public else 1 if full[0]==public[0] else 2
    public_kickers=np.asarray([(r+1)/13 for r in public[1:]]+[0.]*(6-len(public)),dtype=np.float32)
    full_kickers=np.asarray([(r+1)/13 for r in full[1:]]+[0.]*(6-len(full)),dtype=np.float32)
    minimum=0 if relation==0 else 1 if any(best_visible_rank(board+[c])==full for c in hole) else 2
    x=np.zeros(WIDTH,dtype=np.float32)
    x[public[0]]=1;x[9:14]=public_kickers;x[14+relation]=1
    if full[0]==public[0]:x[17:22]=full_kickers-public_kickers
    x[22+minimum]=1
    assert np.isfinite(x).all() and np.max(abs(x))<=1
    return x
