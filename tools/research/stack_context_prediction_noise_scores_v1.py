"""Bounded, legal-action, paired-label prediction and decision diagnostics.

Caller must prospectively freeze predictions, independent label streams and
IID cluster sampling. This module cannot admit data or prove those conditions.
"""
import hashlib
import math
from sampled_evaluation_intervals_v1 import Plan, PairedEvaluation
from stack_context_teacher_path_v1 import encoded

METRICS = ('observed_mse_A', 'observed_mse_B', 'label_noise',
           'corrected_mse_A', 'corrected_mse_B', 'prediction_gain_B', 'decision_gain_B')


def scalar(x):
    if type(x) not in (int, float) or not math.isfinite(x):raise ValueError('Finite real scalar required')
    return float(x)


def vector(values, n):
    if not isinstance(values, (list, tuple)) or len(values) != n:raise ValueError('Exact legal-action vector required')
    return [scalar(x) for x in values]


def bounds(stack, dead):
    stack, dead = scalar(stack), scalar(dead)
    if stack <= 0 or dead < 0:raise ValueError('Original positive stack and nonnegative dead money required')
    return 2+dead/stack


def prediction(raw, n, span):
    if type(n) is not int or not 2 <= n <= 4 or not isinstance(raw, (list, tuple)) or len(raw) != 4:
        raise ValueError('Four-slot prediction and legal menu required')
    # Illegal outputs are deliberately ignored, including NaN padding. Neither
    # their values nor their count enter the legal loss or decision rule.
    legal = [scalar(x) for x in raw[:n]]
    clipped = [min(span, max(-span, x)) for x in legal]
    best = max(clipped);winners = [i for i, v in enumerate(clipped) if v == best]
    policy = [float(i in winners)/len(winners) for i in range(n)]
    return clipped, policy, sum(a != b for a, b in zip(legal, clipped))


def label(q, sigma, stack, dead):
    n = len(sigma);q = vector(q, n);sigma = vector(sigma, n)
    if not 2 <= n <= 4 or any(p < 0 for p in sigma) or abs(math.fsum(sigma)-1) > 1e-12:
        raise ValueError('Original normalized teacher strategy required')
    span = bounds(stack, dead)
    if any(v < -stack-1e-10 or v > stack+dead+1e-10 for v in q):
        raise ValueError('Conditional Q outside original chip ledger bounds')
    baseline = math.fsum(p*v for p, v in zip(sigma, q))
    y = [(v-baseline)/stack for v in q]
    if any(abs(v) > span+1e-12 for v in y):raise ValueError('Normalized advantage exceeds ledger range')
    return y


def paired_scores(*, q_first, q_second, sigma, starting_stack, dead_money,
                  prediction_A, prediction_B):
    """Two equal-budget independent label means for the SAME information state.

    Observed MSE minus half the squared replicate difference equals the
    cross-residual estimator. The latter may be negative; never clamp it.
    Decision policies use only clipped predictions with uniform exact ties.
    """
    stack, dead = scalar(starting_stack), scalar(dead_money);span = bounds(stack, dead)
    first = label(q_first, sigma, stack, dead);second = label(q_second, sigma, stack, dead);n = len(sigma)
    a, pa, ca = prediction(prediction_A, n, span);b, pb, cb = prediction(prediction_B, n, span)
    def loss(p):
        observed = math.fsum(((v-y)**2+(v-z)**2)/2 for v, y, z in zip(p, first, second))/n
        corrected = math.fsum((v-y)*(v-z) for v, y, z in zip(p, first, second))/n
        return observed, corrected
    observed_a, cross_a = loss(a);observed_b, cross_b = loss(b)
    noise = math.fsum((y-z)**2/2 for y, z in zip(first, second))/n
    if abs(observed_a-noise-cross_a) > 1e-10 or abs(observed_b-noise-cross_b) > 1e-10:
        raise ValueError('Paired-label identity failed')
    # Q is in chips: use its paired mean directly. Because policy differences
    # sum to zero, this equals the corresponding advantage difference.
    q = [(x+y)/2 for x, y in zip(q_first, q_second)]
    decision = math.fsum((p-r)*v/stack for p, r, v in zip(pb, pa, q))
    gains = dict(observed_mse_A=observed_a, observed_mse_B=observed_b, label_noise=noise,
        corrected_mse_A=cross_a, corrected_mse_B=cross_b,
        prediction_gain_B=cross_a-cross_b, decision_gain_B=decision)
    return dict(scores=gains, advantage_span=span, legal_actions=n,
        clipped_legal_outputs_A=ca, clipped_legal_outputs_B=cb,
        decision_policy_A=pa, decision_policy_B=pb,
        scoring='Mean over legal actions only; clipped prediction; equal-budget independent label means',
        policy_rule='Argmax clipped legal prediction, uniform exact ties',
        corrected_score_may_be_negative=True, scientific_admission=False)


def metric_bounds(name, span):
    if name in ('observed_mse_A', 'observed_mse_B'):return 0., 4*span*span
    if name == 'label_noise':return 0., 2*span*span
    if name in ('corrected_mse_A', 'corrected_mse_B'):return -span*span, 4*span*span
    if name == 'prediction_gain_B':return -4*span*span, 4*span*span
    if name == 'decision_gain_B':return -span, span
    raise ValueError('Unknown registered prediction metric')


class ClusterEvaluation:
    """One convex row average per independent registered source cluster.

    Cluster identifiers represent the declared parent draw/board units, not
    generated action rows. Every dependent descendant belongs to its parent.
    IID parent draws, fixed row weighting, independent label streams and frozen
    predictors are caller requirements, not facts inferred from identifiers.
    """
    def __init__(self, *, strata, stratum, looks, alpha, maximum_advantage_span):
        span = scalar(maximum_advantage_span)
        if span < 2:raise ValueError('Conservative original ledger span required')
        if (not isinstance(strata, tuple) or not strata or len(set(strata)) != len(strata)
                or any(type(s) is not str or not s or '/' in s for s in strata) or stratum not in strata):
            raise ValueError('Explicit distinct prospective strata required')
        family = tuple(s+'/'+metric for s in strata for metric in METRICS)
        self.config = dict(strata=strata, stratum=stratum, looks=looks, alpha=alpha, maximum_advantage_span=span)
        self.identity = hashlib.sha256(encoded(self.config)).hexdigest()
        self.span = span;self.seen = set();self.rows = 0;self.evaluations = {}
        for metric in METRICS:
            lo, hi = metric_bounds(metric, span)
            p = Plan(lo, hi, family, looks, alpha)
            self.evaluations[metric] = PairedEvaluation(p, stratum+'/'+metric)

    def add_cluster(self, identity, rows, weights):
        if type(identity) is not str or not identity or identity in self.seen:
            raise ValueError('Distinct complete source-cluster identity required')
        if not isinstance(rows, list) or not rows or len(rows) != len(weights):
            raise ValueError('One complete weighted source-cluster block required')
        w = [scalar(v) for v in weights];total = math.fsum(w)
        if any(v < 0 for v in w) or total <= 0:raise ValueError('Nonnegative nonempty prospective row weighting required')
        normalized = [v/total for v in w]
        values = {}
        for row in rows:
            span = scalar(row['advantage_span']);n = row['legal_actions']
            if (set(row['scores']) != set(METRICS) or not 2 <= span <= self.span+1e-12
                    or type(n) is not int or not 2 <= n <= 4
                    or row.get('scientific_admission') is not False):
                raise ValueError('Changed metric contract or ledger span')
            for metric in METRICS:
                v = scalar(row['scores'][metric]);lo, hi = metric_bounds(metric, span)
                if not lo-1e-10 <= v <= hi+1e-10:raise ValueError('Out-of-bounds row score')
            s = row['scores']
            if (abs(s['observed_mse_A']-s['label_noise']-s['corrected_mse_A']) > 1e-10
                    or abs(s['observed_mse_B']-s['label_noise']-s['corrected_mse_B']) > 1e-10
                    or abs(s['corrected_mse_A']-s['corrected_mse_B']-s['prediction_gain_B']) > 1e-10):
                raise ValueError('Changed paired-score identities')
        for metric, evaluation in self.evaluations.items():
            v = math.fsum(weight*row['scores'][metric] for weight, row in zip(normalized, rows))
            # Validate every metric before any accumulator mutation.
            if not evaluation.plan.lower <= v <= evaluation.plan.upper:raise ValueError('Cluster bound exceeded')
            if evaluation.count >= evaluation.plan.looks[-1]:raise ValueError('Cluster budget exhausted')
            values[metric] = v
        for metric, v in values.items():self.evaluations[metric].add_difference(v)
        self.seen.add(identity);self.rows += len(rows)

    def merge(self, other):
        if other is self or self.identity != other.identity or self.seen.intersection(other.seen):
            raise ValueError('Incompatible or overlapping source-cluster batches')
        if len(self.seen)+len(other.seen) > next(iter(self.evaluations.values())).plan.looks[-1]:
            raise ValueError('Registered source-cluster budget exhausted')
        for metric in METRICS:self.evaluations[metric].merge(other.evaluations[metric])
        self.seen.update(other.seen);self.rows += other.rows

    def interval(self):
        return dict(clusters=len(self.seen), dependent_rows=self.rows, registered_config=self.config,
            intervals={metric:evaluation.interval() for metric, evaluation in self.evaluations.items()},
            equal_weight_per_source_cluster=True, conditional_IID_source_assumption_required=True,
            frozen_predictions_and_independent_replicates_required=True,
            canonical_flop_train_test_split_is_separate=True, scientific_admission=False,
            equilibrium_or_best_response_certificate=False)
