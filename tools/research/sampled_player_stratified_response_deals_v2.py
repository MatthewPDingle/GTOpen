"""Actor-specific class coverage for response training, never population testing.

Either actor can be the conditioned player, but returned physical deal columns
always remain [BB cards, BTN cards, shared board]. Separate BB and BTN training
streams avoid reusing a changed opponent mix for the other player's response.
"""
import numpy as np
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES


def private_law(context_source, *, player, seed):
    if type(player) is not int or player not in (0,1):
        raise ValueError('Explicit player 0 or 1 required')
    base = PhysicalDeals(context_source, mode='full_deck', seed=seed)
    own, opponent = base.live[0][player], base.live[0][1-player]
    card_mass = np.bincount(PAIRS.ravel(), weights=np.repeat(opponent,2), minlength=52)
    compatible = np.maximum(opponent.sum()-card_mass[PAIRS[:,0]]-card_mass[PAIRS[:,1]]+opponent,0)
    marginal = own*compatible
    if not np.isfinite(marginal).all() or marginal.sum() <= 0:
        raise ValueError('No compatible source support')
    marginal /= marginal.sum()
    return base, marginal, opponent


def sample(context_source, *, player, seed, per_class, classes, guard=lambda: None):
    if type(per_class) is not int or not 1 <= per_class <= 512:
        raise ValueError('Explicit fixed per-class count in 1..512 required')
    if (not isinstance(classes,list) or not classes
            or any(type(c) is not int or not 0 <= c < 169 for c in classes)
            or classes != sorted(set(classes))):
        raise ValueError('Explicit sorted unique supported classes required')
    base, marginal, opponent = private_law(context_source, player=player, seed=seed)
    conditionals = {}
    for c in classes:
        probabilities = marginal*(CLASSES == c)
        mass = probabilities.sum()
        if mass <= 0:
            raise ValueError(f'Player {player} class {c} has no compatible source support')
        conditionals[c] = probabilities/mass
    deals, labels = [], []
    for repeat in range(per_class):
        guard()
        for c in classes:
            i = int(base.rng.choice(len(PAIRS), p=conditionals[c]))
            conditional_opponent = opponent*((MASKS & MASKS[i]) == 0)
            conditional_opponent /= conditional_opponent.sum()
            j = int(base.rng.choice(len(PAIRS), p=conditional_opponent))
            first, second = (i,j) if player == 0 else (j,i)
            private = [int(x) for x in PAIRS[first]]+[int(x) for x in PAIRS[second]]
            remaining = [x for x in range(52) if x not in private]
            board = [int(x) for x in base.rng.choice(remaining, size=5, replace=False)]
            deal = sorted(private[:2])+sorted(private[2:])+sorted(board[:3])+board[3:]
            assert len(set(deal)) == 9 and int(CLASSES[i]) == c
            deals.append(deal); labels.append(c)
    return dict(format=2, purpose='player-stratified-response-training-only',
        conditioned_player=player, context_sha256=base.context_sha256,
        seed=seed, per_class=per_class, classes=classes, order='round-robin-class',
        physical_columns='player-0,player-1,shared-board',deals=deals,hand_classes=labels,
        original_class_masses=[float(marginal[CLASSES == c].sum()) for c in classes],
        population_evaluation=False,other_player_response_training=False)
