"""Prospective seven-depth K2/K8 comparison; no sampler or model selection.

Each input observation is one physical deal evaluated under eight complete
policy profiles. The sole final look is 65,536 deals at every declared depth.
The family covers all 56 player/depth contrasts, including held-out depths.
Passing arithmetic controls does not establish poker accuracy or equilibrium.
"""
import math
from statistics import NormalDist
from stack_context_matched_analysis_v1 import quantile_linear
import numpy as np

from crossed_complete_policy_comparison_v1 import crossed_profiles, differences
from sampled_evaluation_intervals_v1 import Plan, PairedEvaluation

DEPTHS = (20, 40, 60, 100, 150, 200, 400)
FIT_DEPTHS = (20, 40, 100, 200, 400)
DEALS_PER_DEPTH = 65536
ARM_ORDER = ('first-K2', 'first-K8', 'replication-K2', 'replication-K8')
PAIR_NAMES = ('K2BB-K2BTN', 'K2BB-K8BTN', 'K8BB-K2BTN', 'K8BB-K8BTN')
PROFILE_NAMES = tuple(f'{seed}:{pair}' for seed in ('first', 'replication')
                      for pair in PAIR_NAMES)
CONTRAST_NAMES = tuple(f'{seed}:{name}' for seed in ('first', 'replication')
                      for name in (
                          'K8BB-minus-K2BB-against-K2BTN',
                          'K8BB-minus-K2BB-against-K8BTN',
                          'K8BTN-minus-K2BTN-against-K2BB',
                          'K8BTN-minus-K2BTN-against-K8BB'))
FAMILY = tuple(f'{depth}bb:{name}' for depth in DEPTHS for name in CONTRAST_NAMES)


def profiles(queries, probabilities):
    """Preserve established crossing arithmetic; supply explicit K arm names."""
    result = crossed_profiles(queries, probabilities)
    for row, name in zip(result, PROFILE_NAMES):
        row['name'] = name
    return result


class SevenDepthComparison:
    def __init__(self, contexts, *, alpha=.05):
        if (not isinstance(contexts, dict) or set(contexts) != set(DEPTHS)
                or any(type(depth) is not int for depth in contexts)
                or type(alpha) not in (int, float) or not math.isfinite(alpha)
                or not 0 < alpha < 1):
            raise ValueError('Exactly seven declared depths and a finite family alpha required')
        self.alpha = float(alpha)
        self.contexts, self.series, self.next_batch = {}, {}, {}
        self.paired_rows, self.value_min, self.value_max = {}, {}, {}
        for depth in DEPTHS:
            supplied = contexts[depth]
            if (not isinstance(supplied, dict)
                    or set(supplied) != {'stack', 'dead_money', 'context_sha256'}):
                raise ValueError('Pinned stack, dead money and context identity required')
            stack, dead, identity = (supplied[k] for k in ('stack', 'dead_money', 'context_sha256'))
            if (type(stack) not in (int, float) or stack != depth
                    or type(dead) not in (int, float) or not math.isfinite(dead) or dead < 0
                    or not isinstance(identity, str) or len(identity) != 64
                    or any(c not in '0123456789abcdef' for c in identity)):
                raise ValueError('Invalid registered payoff bounds or context identity')
            self.contexts[depth] = dict(supplied)
            radius = 2 * stack + dead
            # The same full 56-series family is used at every depth. Different
            # depth-specific ranges do not change the Bonferroni allocation.
            plan = Plan(-radius, radius, FAMILY, (DEALS_PER_DEPTH,), self.alpha)
            self.series[depth] = [PairedEvaluation(plan, f'{depth}bb:{name}')
                                  for name in CONTRAST_NAMES]
            self.next_batch[depth] = 0
            self.paired_rows[depth] = []
            self.value_min[depth] = np.full((8, 2), np.inf)
            self.value_max[depth] = np.full((8, 2), -np.inf)

    def add(self, depth, values, *, context_sha256, batch_index, deal_offset):
        if type(depth) is not int or depth not in self.contexts:
            raise ValueError('Unregistered evaluation depth')
        fixed = self.contexts[depth]
        count = self.series[depth][0].count
        if (context_sha256 != fixed['context_sha256']
                or type(batch_index) is not int or batch_index != self.next_batch[depth]
                or type(deal_offset) is not int or deal_offset != count):
            raise ValueError('Changed context, duplicated/reordered batch or deal offset')
        v = np.asarray(values, dtype=np.float64)
        d = differences(v)
        if (not 1 <= len(d) <= 64 or count + len(d) > DEALS_PER_DEPTH
                or np.any(v < -fixed['stack'])
                or np.any(v > fixed['stack'] + fixed['dead_money'])):
            raise ValueError('Complete paired batch exceeds its fixed payoff/deal bounds')
        # Reject the complete input before changing even the first statistic.
        for row in d:
            for stat, value in zip(self.series[depth], row):
                stat.add_difference(float(value))
        self.next_batch[depth] += 1
        self.paired_rows[depth].append(d.copy())
        flat = v.reshape(len(v), 8, 2)
        self.value_min[depth] = np.minimum(self.value_min[depth], flat.min(0))
        self.value_max[depth] = np.maximum(self.value_max[depth], flat.max(0))

    def counts(self):
        return {depth: self.series[depth][0].count for depth in DEPTHS}

    def finish(self):
        if any(count != DEALS_PER_DEPTH for count in self.counts().values()):
            raise ValueError('All seven complete 65,536-deal budgets required; no early selection')
        rows = []
        for depth in DEPTHS:
            contrasts = []
            delta = np.concatenate(self.paired_rows[depth])
            if delta.shape != (DEALS_PER_DEPTH, 8):
                raise ValueError('Complete paired-loss records required')
            z = NormalDist().inv_cdf(1 - self.alpha / (2 * 56))
            for index, (stat, name) in enumerate(zip(self.series[depth], CONTRAST_NAMES)):
                interval = stat.interval()
                interval.update(name=name, standard_error=math.sqrt(
                    interval['sample_variance'] / interval['count']))
                loss = -delta[:, index]
                interval.update(negative_deal_fraction=float(np.mean(delta[:, index] < 0)),
                    paired_loss_95_bb=quantile_linear(loss, .95),
                    paired_loss_99_bb=quantile_linear(loss, .99),
                    worst_observed_paired_loss_bb=float(loss.max()),
                    mean_positive_paired_loss_bb=float(np.maximum(loss, 0).mean()),
                    exploratory_normal_interval=dict(lower=interval['mean']-z*interval['standard_error'],
                        upper=interval['mean']+z*interval['standard_error'], z=z, finite_sample_guarantee=False))
                contrasts.append(interval)
            rows.append(dict(depth=depth, split='fit' if depth in FIT_DEPTHS else 'heldout',
                             context_sha256=self.contexts[depth]['context_sha256'],
                             deals=DEALS_PER_DEPTH, contrasts=contrasts,
                             per_deal_value_ranges=[dict(profile=name,
                                 minimum_player_value_bb=self.value_min[depth][i].tolist(),
                                 maximum_player_value_bb=self.value_max[depth][i].tolist())
                                 for i, name in enumerate(PROFILE_NAMES)]))
        pooled = [dict(name=name,
            mean=float(np.mean([row['contrasts'][i]['mean'] / row['depth'] for row in rows])),
            lower=float(np.mean([row['contrasts'][i]['lower'] / row['depth'] for row in rows])),
            upper=float(np.mean([row['contrasts'][i]['upper'] / row['depth'] for row in rows])),
            units='starting-stack fraction per fixed entry', equal_depth_weight=1/7)
            for i, name in enumerate(CONTRAST_NAMES)]
        positive = all(row['lower'] > 0 for row in pooled)
        negative = [dict(depth=context['depth'], name=row['name'], mean_bb=row['mean'])
                    for context in rows for row in context['contrasts'] if row['mean'] < 0]
        return dict(format=1, method='seven-depth-complete-expected-policy-crossing-v2',
                    depths=rows, equal_depth_normalized_gains=pooled,
                    all_eight_pooled_lower_bounds_positive=positive,
                    negative_depth_point_estimates=negative,
                    registered_policy_improvement_criterion_met=positive and not negative,
                    arm_order=list(ARM_ORDER), profile_order=list(PROFILE_NAMES),
                    required_selection_contract=dict(completed_cycles=32, played_generations=list(range(32)),
                        excluded_unplayed_generation=32), total_deals=7 * DEALS_PER_DEPTH,
                    family_series=56, family_error_probability=self.alpha,
                    final_looks=1, interval_method='bounded empirical Bernstein; Bonferroni over all 56 contrasts',
                    units='bb per fixed HU entry',
                    tail_convention='Signed paired loss = K2 value minus K8 value; linear empirical quantiles; negative loss is a gain',
                    exploratory_normal_finite_sample_guarantee=False,
                    assumptions='Frozen played policies; IID fresh common physical deals at each depth; bounded payoffs.',
                    bounds_best_response_above=False, equilibrium_qualified=False,
                    broad_preflop_accuracy_qualified=False)
