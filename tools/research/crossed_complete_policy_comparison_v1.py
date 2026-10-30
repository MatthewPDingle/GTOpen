"""Fixed complete-policy crossings and paired finite-sample comparison.

No sampling, fitting, policy selection, root forcing, or production access.
Each observation is one common physical deal evaluated under eight profiles.
"""
import math
import numpy as np
from sampled_batch_protocol_v2 import policy_document
from sampled_evaluation_intervals_v1 import Plan, PairedEvaluation

SEEDS = ('first', 'replication')
PAIRS = ((0, 0), (0, 1), (1, 0), (1, 1))
PAIR_NAMES = ('oldBB-oldBTN', 'oldBB-newBTN', 'newBB-oldBTN', 'newBB-newBTN')
PROFILE_NAMES = tuple(f'{seed}:{pair}' for seed in SEEDS for pair in PAIR_NAMES)
CONTRAST_NAMES = tuple(f'{seed}:{name}' for seed in SEEDS for name in (
    'newBB-v-oldBB-against-oldBTN', 'newBB-v-oldBB-against-newBTN',
    'newBTN-v-oldBTN-against-oldBB', 'newBTN-v-oldBTN-against-newBB'))


def crossed_profiles(queries, policies):
    """Policies ordered first-old, first-new, replication-old, replication-new."""
    obs = queries['observations']
    if not obs or any(type(o['actor']) is not int or o['actor'] not in (0, 1)
                      or type(o['n']) is not int or not 1 <= o['n'] <= 4 for o in obs):
        raise ValueError('Valid two-player legal-action queries required')
    p = np.asarray(policies, dtype=np.float64)
    if p.shape != (4, len(obs), 4) or not np.isfinite(p).all() or np.any(p < 0):
        raise ValueError('Four finite nonnegative complete policies required')
    arities = np.array([o['n'] for o in obs])
    illegal = np.arange(4)[None, :] >= arities[:, None]
    if np.any(p[:, illegal] != 0) or np.any(abs(p.sum(axis=2) - 1) > 1e-10):
        raise ValueError('Policies must be normalized over legal actions')
    actors = np.array([o['actor'] for o in obs])
    result = []
    for seed in range(2):
        for bb, btn in PAIRS:
            mixed = np.where((actors == 0)[:, None], p[2*seed+bb], p[2*seed+btn])
            result.append(dict(name=PROFILE_NAMES[len(result)],
                               policies=policy_document(queries, mixed)['policies']))
    return result


def differences(values):
    """n x seed x pairing x player -> n x eight registered player gains."""
    v = np.asarray(values, dtype=np.float64)
    if v.ndim != 4 or v.shape[1:] != (2, 4, 2) or not np.isfinite(v).all():
        raise ValueError('Expected finite paired values with shape (deals,2,4,2)')
    rows = []
    for s in range(2):
        rows.extend((v[:, s, 2, 0]-v[:, s, 0, 0], v[:, s, 3, 0]-v[:, s, 1, 0],
                     v[:, s, 1, 1]-v[:, s, 0, 1], v[:, s, 3, 1]-v[:, s, 2, 1]))
    return np.stack(rows, axis=1)


class CompletePolicyComparison:
    def __init__(self, *, stack, dead_money, deals, alpha=.05):
        if not (math.isfinite(stack) and stack > 0 and math.isfinite(dead_money) and dead_money >= 0):
            raise ValueError('Fixed valid payoff bounds required')
        self.stack, self.dead_money = stack, dead_money
        self.radius_bound = 2*stack + dead_money
        self.plan = Plan(-self.radius_bound, self.radius_bound, CONTRAST_NAMES, (deals,), alpha)
        self.series = [PairedEvaluation(self.plan, name) for name in CONTRAST_NAMES]

    def add(self, values):
        v = np.asarray(values, dtype=np.float64)
        d = differences(v)
        # Validate the complete batch before mutating any statistic.
        if (np.any(v < -self.stack) or np.any(v > self.stack+self.dead_money)
                or np.any(abs(d) > self.radius_bound)):
            raise ValueError('Values violate the prospectively fixed payoff bounds')
        if self.series[0].count + len(d) > self.plan.looks[-1]:
            raise ValueError('Registered common-deal budget exhausted')
        for row in d:
            for statistic, value in zip(self.series, row):
                statistic.add_difference(float(value))

    def finish(self):
        results = []
        for statistic in self.series:
            interval = statistic.interval()
            interval.update(name=statistic.series,
                standard_error=math.sqrt(interval['sample_variance']/interval['count']))
            results.append(interval)
        return dict(deals=self.plan.looks[-1], profile_order=list(PROFILE_NAMES),
            contrasts=results, family_error_probability=self.plan.alpha,
            interval_method='two-sided bounded empirical Bernstein; Bonferroni over eight contrasts and one final look',
            assumptions='Frozen policies; independent common physical deals from the registered entry distribution; bounded payoffs. Correlation between contrasts is allowed.',
            units='bb per entry', positive_gain='Improvement for the player being replaced against the stated fixed opponent',
            bounds_best_response_above=False, accuracy_qualified=False)
