"""Fixed coverage per BB hand class for response TRAINING only.

Conditions the existing compatible-card entry law on the first player's class.
It deliberately changes the class mix; unweighted population evaluation on this
stream would be wrong. Held-out evaluation must retain its separate sampler.
"""
import numpy as np
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS, MASKS, CLASSES


def sample(context_source, *, seed, per_class, classes, guard=lambda: None):
    if type(per_class) is not int or not 1 <= per_class <= 512:
        raise ValueError('Explicit fixed per-class count in 1..512 required')
    if (not isinstance(classes, list) or not classes
            or any(type(c) is not int or not 0 <= c < 169 for c in classes)
            or classes != sorted(set(classes))):
        raise ValueError('Explicit sorted unique supported classes required')
    base = PhysicalDeals(context_source, mode='full_deck', seed=seed)
    marginal = base.first[0]
    conditionals = {}
    for c in classes:
        probabilities = marginal*(CLASSES == c)
        mass = probabilities.sum()
        if mass <= 0:
            raise ValueError(f'Class {c} has no compatible source support')
        conditionals[c] = probabilities/mass
    deals, labels = [], []
    for repeat in range(per_class):
        guard()
        for c in classes:
            i = int(base.rng.choice(len(PAIRS), p=conditionals[c]))
            second = base.live[0][1]*((MASKS & MASKS[i]) == 0)
            second /= second.sum()
            j = int(base.rng.choice(len(PAIRS), p=second))
            private = [int(x) for x in PAIRS[i]]+[int(x) for x in PAIRS[j]]
            remaining = [x for x in range(52) if x not in private]
            board = [int(x) for x in base.rng.choice(remaining, size=5, replace=False)]
            deal = sorted(private[:2])+sorted(private[2:])+sorted(board[:3])+board[3:]
            assert len(set(deal)) == 9 and int(CLASSES[i]) == c
            deals.append(deal); labels.append(c)
    return dict(format=1, purpose='stratified-response-training-only',
        context_sha256=base.context_sha256, seed=seed, per_class=per_class,
        classes=classes, order='round-robin-class', deals=deals, hand_classes=labels,
        original_class_masses=[float(marginal[CLASSES == c].sum()) for c in classes],
        population_evaluation=False)
