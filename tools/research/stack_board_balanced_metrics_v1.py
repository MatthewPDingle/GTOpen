"""Detailed balanced-coverage metrics and an independent streaming CPU reference.

This is a new evaluation helper, not a training or checkpoint-selection change.
Rows are state-major, then board-major, then the 1,081 legal hero holdings.
The production summarizer uses complete arrays; reference_context independently
converts raw scores and accumulates every group state by state, retaining only
one float64 loss array for exact tail reconstruction. Neither function writes
files. CPU network inference and all scientific/provenance guards belong to the
caller; score_rows must yield exactly one complete card array per public state.
"""
import math
import numpy as np

HOLDINGS_PER_BOARD = 1081
PRICE_EDGES = np.asarray([0., .1, .2, .3, .4, .5, 1.01])
CATEGORIES = ('high_card', 'pair', 'two_pair', 'trips', 'straight', 'flush',
              'full_house', 'quads', 'straight_flush')
PROBABILITY_RULE = 'Positive-score regret matching; nonpositive rows choose the maximum legal score.'
METRIC_KEYS = ('mean_regret_bb', 'mean_regret_stack_fraction', 'p95_regret_bb',
               'p99_regret_bb', 'maximum_regret_bb',
               'mean_legal_value_squared_error_bb',
               'majority_action_error_rate', 'always_fold_regret_bb',
               'always_call_regret_bb')
COUNT_KEYS = ('rows', 'decisions_outside_indifference_band')
PARTITIONS = ('seats', 'price_bands', 'hand_groups', 'per_board')

# Fixed before any balanced-coverage scientific outputs. These are numerical
# readback tolerances, not scientific accuracy gates, and are never fitted to
# observed CPU/CUDA discrepancies. Squared value error has units bb^2 despite
# its inherited field name. A score sign/argmax crossing can violate tail or
# classification tolerances even when cash means agree; that remains a failure.
TOLERANCE_POLICY = {
    'cash_mean_absolute_bb': 1e-4,
    'cash_tail_absolute_bb': 1e-3,
    'classification_rate_absolute': 1e-5,
    'value_squared_error_absolute_bb2': 1e-4,
    'value_squared_error_stack_squared_coefficient': 1e-6,
    'counterfactual_mean_absolute_bb': 1e-9,
    'count_and_metadata': 'exact',
    'relative_tolerance': 0.,
    'near_zero_score_instability': 'Fail the fixed comparison; retain discrepancies. Do not relax tolerances.',
}


def _guard(guard):
    if guard is not None:
        guard()


def _context_inputs(equity, economics, category, stack, board_count):
    if isinstance(board_count, bool) or int(board_count) != board_count or board_count < 1:
        raise ValueError('Positive integer board_count required')
    if not math.isfinite(stack) or stack <= 0:
        raise ValueError('Positive finite starting stack required')
    nc = int(board_count) * HOLDINGS_PER_BOARD
    eq = np.asarray(equity, dtype=np.float64)
    e = np.asarray(economics, dtype=np.float64)
    cat = np.asarray(category)
    if eq.shape != (nc,) or not np.isfinite(eq).all() or np.any((eq < 0) | (eq > 1)):
        raise ValueError('Complete board-major equity array required')
    if cat.shape != (nc,) or cat.dtype.kind not in 'iu' or np.any((cat < 0) | (cat >= len(CATEGORIES))):
        raise ValueError('One integer visible hand category per holding required')
    if e.ndim != 2 or e.shape[1] != 5 or not len(e) or not np.isfinite(e).all():
        raise ValueError('Finite nonempty five-column economics array required')
    if not np.all(e[:, 0] == stack) or np.any(e[:, 1] <= 0) or np.any(e[:, 2] < 0):
        raise ValueError('Economics do not match the requested starting stack')
    if np.any((e[:, 3] != 0) & (e[:, 3] != 1)):
        raise ValueError('Only actor zero and actor one are supported')
    if np.any((e[:, 4] < PRICE_EDGES[0]) | (e[:, 4] >= PRICE_EDGES[-1])):
        raise ValueError('Public price outside the registered partition')
    return eq, e, cat, nc


def summarize_context(call, fold_score, call_score, equity, economics, category,
                      stack, board_count, detail=True, guard=None):
    """Summarize completed state-major predictions; scores are stack-normalized.

    Probability conversion is deliberately supplied by the existing evaluator.
    Extra per-board identities can be attached by the caller using board_index.
    The old empty-partition contract is retained: metadata plus rows=0 only.
    """
    _guard(guard)
    eq, e, cat, nc = _context_inputs(equity, economics, category, stack, board_count)
    shape = (len(e), nc)
    arrays = []
    for value in (call, fold_score, call_score):
        a = np.asarray(value)
        if a.size != len(e) * nc or not np.isfinite(a).all():
            raise ValueError('Finite complete state-major predictions required')
        arrays.append(a.reshape(shape))
    p, fold, called = arrays
    if np.any((p < 0) | (p > 1)):
        raise ValueError('Legal call probabilities required')
    delta = e[:, 1, None] * eq[None, :] - e[:, 2, None]
    loss = np.maximum(delta, 0.) - p * delta
    if not np.isfinite(loss).all() or np.any(loss < 0):
        raise ValueError('Invalid decision loss')
    if not detail:
        mean = float(loss.mean())
        return dict(stack=float(stack), rows=int(loss.size), mean_regret_bb=mean,
                    mean_regret_stack_fraction=mean / stack)
    value_error = ((called.astype(np.float64) * stack - delta) ** 2
                   + (fold.astype(np.float64) * stack) ** 2) / 2
    if not np.isfinite(value_error).all():
        raise ValueError('Nonfinite legal value error')

    def select(a, states, cards):
        if isinstance(states, slice):
            return a[states, cards]
        if isinstance(cards, slice):
            return a[states, cards]
        return a[np.ix_(states, cards)]

    def summary(states=slice(None), cards=slice(None)):
        _guard(guard)
        v = select(loss, states, cards).reshape(-1)
        if not v.size:
            return dict(rows=0)
        d = select(delta, states, cards).reshape(-1)
        probs = select(p, states, cards).reshape(-1)
        close = np.abs(d) > 1e-4 * stack
        mistakes = ((d > 0) != (probs >= .5)) & close
        eligible = int(close.sum())
        q95, q99 = np.quantile(v, [.95, .99], method='linear')
        mean = float(v.mean())
        return dict(rows=int(v.size), mean_regret_bb=mean,
                    mean_regret_stack_fraction=mean / stack,
                    p95_regret_bb=float(q95), p99_regret_bb=float(q99),
                    maximum_regret_bb=float(v.max()),
                    mean_legal_value_squared_error_bb=float(select(value_error, states, cards).mean()),
                    decisions_outside_indifference_band=eligible,
                    majority_action_error_rate=float(mistakes.sum() / eligible) if eligible else None,
                    always_fold_regret_bb=float(np.maximum(d, 0).mean()),
                    always_call_regret_bb=float(np.maximum(-d, 0).mean()))

    record = dict(stack=float(stack), **summary())
    bands = np.searchsorted(PRICE_EDGES, e[:, 4], side='right') - 1
    record['seats'] = [dict(actor=a, **summary(states=np.flatnonzero(e[:, 3] == a))) for a in (0, 1)]
    record['price_bands'] = [dict(minimum_equity=float(PRICE_EDGES[b]),
                                  maximum_equity=float(PRICE_EDGES[b + 1]),
                                  **summary(states=np.flatnonzero(bands == b)))
                             for b in range(len(PRICE_EDGES) - 1)]
    record['hand_groups'] = [dict(name=name, **summary(cards=np.flatnonzero(cat == j)))
                             for j, name in enumerate(CATEGORIES)]
    record['per_board'] = [dict(board_index=b, **summary(cards=slice(b * HOLDINGS_PER_BOARD,
                                                                    (b + 1) * HOLDINGS_PER_BOARD)))
                           for b in range(int(board_count))]
    for name in PARTITIONS:
        if sum(row['rows'] for row in record[name]) != loss.size:
            raise ValueError('Non-exhaustive metric partition: ' + name)
    _guard(guard)
    return record


def evaluation_summary(contexts):
    """Package nonempty context records with the inherited equal-context means."""
    if not contexts:
        raise ValueError('At least one context required')
    return dict(contexts=contexts,
                context_balanced_mean_regret_stack_fraction=float(np.mean([r['mean_regret_stack_fraction'] for r in contexts])),
                context_balanced_mean_regret_bb=float(np.mean([r['mean_regret_bb'] for r in contexts])),
                probability_rule=PROBABILITY_RULE, rows=sum(r['rows'] for r in contexts))


def evaluate(models, data, width, guard, *, detail):
    """CUDA forward pass with the old action rule plus detailed per-board rows.

    Training and validation should keep their existing evaluate implementation;
    this entry point is for the frozen final-test and separate stress datasets.
    """
    import torch
    from stack_price_learning_fit_v1 import scores, probabilities
    records = []
    models.eval()
    nc = len(data.card_np)
    if nc != data.board_count * HOLDINGS_PER_BOARD:
        raise ValueError('Incomplete legal holding coverage')
    with torch.no_grad():
        for context_id, context in enumerate(data.contexts):
            _guard(guard)
            offset = int(data.offsets[context_id])
            nstates = int(data.lengths[context_id])
            raw = np.empty((nc * nstates, 2), dtype=np.float32)
            for lo in range(0, len(raw), 8192):
                _guard(guard)
                hi = min(len(raw), lo + 8192)
                idx = torch.arange(lo, hi, device='cuda')
                x, actors, _ = data.assemble(offset + idx // nc, idx % nc, width)
                raw[lo:hi] = scores(models, x, actors)[:, :2].cpu().numpy()
            records.append(summarize_context(
                probabilities(raw), raw[:, 0], raw[:, 1], data.equity_np,
                data.economics_np[offset:offset + nstates], data.category_np,
                float(context['stack']), data.board_count, detail=detail, guard=guard))
            del raw
    return evaluation_summary(records)


def _reference_quantiles(values):
    """Independent order-statistic reconstruction of linear p95 and p99."""
    ordered = np.array(values, dtype=np.float64, copy=True).reshape(-1)
    positions = [.95 * (len(ordered) - 1), .99 * (len(ordered) - 1)]
    keys = {len(ordered) - 1}
    for position in positions:
        keys.update((math.floor(position), math.ceil(position)))
    ordered.partition(sorted(keys))
    result = []
    for position in positions:
        lo, hi = math.floor(position), math.ceil(position)
        fraction = position - lo
        result.append(float(ordered[lo] * (1 - fraction) + ordered[hi] * fraction))
    return *result, float(ordered[-1])


def reference_context(score_rows, equity, economics, category, stack, board_count,
                      detail=True, guard=None):
    """Independently reconstruct metrics from a stream of CPU raw-score rows.

    score_rows yields (board_count*1081, >=2) arrays, one per economics row.
    All reported means/denominators use streaming accumulations; exact tails use
    independent partition/interpolation on a retained float64 loss matrix.
    Peak helper allocation is bounded by approximately 3*rows*8 bytes, plus
    O(cards) working arrays (under 600 MB at 20 million rows). Caller-owned
    card features, model weights and inference buffers are additional.
    """
    _guard(guard)
    eq, e, cat, nc = _context_inputs(equity, economics, category, stack, board_count)
    nb = int(board_count)
    # Group order: whole, two seats, six price bands, nine categories, boards.
    board_start = 1 + 2 + 6 + 9
    totals = np.zeros((board_start + nb, 7), dtype=np.float64)
    losses = np.empty((len(e), nc), dtype=np.float64) if detail else None
    category_counts = np.bincount(cat, minlength=9)
    iterator = iter(score_rows)
    for state_index, state in enumerate(e):
        _guard(guard)
        try:
            raw = np.asarray(next(iterator))
        except StopIteration as exc:
            raise ValueError('Missing CPU state predictions') from exc
        if raw.ndim != 2 or raw.shape[0] != nc or raw.shape[1] < 2 or not np.isfinite(raw[:, :2]).all():
            raise ValueError('Finite complete CPU state predictions required')
        fold = raw[:, 0].astype(np.float64)
        called = raw[:, 1].astype(np.float64)
        positive_fold = np.clip(fold, 0, None)
        positive_call = np.clip(called, 0, None)
        denominator = positive_fold + positive_call
        probability = np.empty(nc, dtype=np.float64)
        active = denominator > 0
        probability[active] = positive_call[active] / denominator[active]
        # Equal nonpositive scores choose fold, matching first-index argmax.
        probability[~active] = (called[~active] > fold[~active]).astype(np.float64)
        advantage = eq * state[1] - state[2]
        row_loss = np.where(advantage > 0,
                            (1 - probability) * advantage, probability * (-advantage))
        if not np.isfinite(row_loss).all() or np.any(row_loss < 0):
            raise ValueError('Invalid reconstructed cash loss')
        if not detail:
            totals[0, 0] += nc
            totals[0, 1] += np.sum(row_loss, dtype=np.float64)
            continue
        losses[state_index] = row_loss
        squared = .5 * np.square(fold * stack) + .5 * np.square(advantage - called * stack)
        outside = np.abs(advantage) > 1e-4 * stack
        wrong = np.logical_and(outside, np.logical_xor(advantage > 0, probability >= .5))
        fold_loss = np.where(advantage > 0, advantage, 0.)
        call_loss = np.where(advantage < 0, -advantage, 0.)
        vectors = (row_loss, squared, outside, wrong, fold_loss, call_loss)
        if not all(np.isfinite(value).all() for value in vectors):
            raise ValueError('Nonfinite reconstructed metric')
        state_totals = np.asarray([nc, *(np.sum(value, dtype=np.float64) for value in vectors)])
        band = next(b for b in range(6) if PRICE_EDGES[b] <= state[4] < PRICE_EDGES[b + 1])
        for group in (0, 1 + int(state[3]), 3 + band):
            totals[group] += state_totals
        totals[9:18, 0] += category_counts
        totals[board_start:, 0] += HOLDINGS_PER_BOARD
        for column, value in enumerate(vectors, 1):
            totals[9:18, column] += np.bincount(cat, weights=value, minlength=9)
            totals[board_start:, column] += value.reshape(nb, HOLDINGS_PER_BOARD).sum(axis=1, dtype=np.float64)
    try:
        next(iterator)
    except StopIteration:
        pass
    else:
        raise ValueError('Extra CPU state predictions')
    if not detail:
        mean = float(totals[0, 1] / totals[0, 0])
        return dict(stack=float(stack), rows=int(totals[0, 0]), mean_regret_bb=mean,
                    mean_regret_stack_fraction=mean / stack)

    def finish(group, values):
        _guard(guard)
        count, regret_sum, value_sum, outside_count, errors, fold_sum, call_sum = totals[group]
        if count == 0:
            if values.size:
                raise ValueError('Unexpected reference partition values')
            return dict(rows=0)
        if values.size != count:
            raise ValueError('Reference partition count mismatch')
        p95, p99, maximum = _reference_quantiles(values)
        return dict(rows=int(count), mean_regret_bb=float(regret_sum / count),
                    mean_regret_stack_fraction=float(regret_sum / count / stack),
                    p95_regret_bb=p95, p99_regret_bb=p99, maximum_regret_bb=maximum,
                    mean_legal_value_squared_error_bb=float(value_sum / count),
                    decisions_outside_indifference_band=int(outside_count),
                    majority_action_error_rate=float(errors / outside_count) if outside_count else None,
                    always_fold_regret_bb=float(fold_sum / count),
                    always_call_regret_bb=float(call_sum / count))

    result = dict(stack=float(stack), **finish(0, losses))
    result['seats'] = [dict(actor=actor, **finish(1 + actor, losses[e[:, 3] == actor]))
                       for actor in (0, 1)]
    result['price_bands'] = []
    for band in range(6):
        mask = (e[:, 4] >= PRICE_EDGES[band]) & (e[:, 4] < PRICE_EDGES[band + 1])
        result['price_bands'].append(dict(minimum_equity=float(PRICE_EDGES[band]),
                                         maximum_equity=float(PRICE_EDGES[band + 1]),
                                         **finish(3 + band, losses[mask])))
    result['hand_groups'] = [dict(name=name, **finish(9 + category_id, losses[:, cat == category_id]))
                             for category_id, name in enumerate(CATEGORIES)]
    result['per_board'] = [dict(board_index=board, **finish(board_start + board,
                              losses[:, board * HOLDINGS_PER_BOARD:(board + 1) * HOLDINGS_PER_BOARD]))
                           for board in range(nb)]
    for partition in PARTITIONS:
        if sum(row['rows'] for row in result[partition]) != result['rows']:
            raise ValueError('Reference partition is not exhaustive')
    _guard(guard)
    return result


def metric_tolerances(stack):
    """Absolute tolerances with explicit physical units and zero relative slack."""
    return {
        'mean_regret_bb': 1e-4,
        'mean_regret_stack_fraction': 1e-4 / stack,
        'p95_regret_bb': 1e-3,
        'p99_regret_bb': 1e-3,
        'maximum_regret_bb': 1e-3,
        'mean_legal_value_squared_error_bb': 1e-4 + 1e-6 * stack ** 2,
        'majority_action_error_rate': 1e-5,
        'always_fold_regret_bb': 1e-9,
        'always_call_regret_bb': 1e-9,
    }


def compare_context(original, computed):
    """Compare every metric/count/partition identity; never hide tail failures.

    Per-board card/canonical identities added by the runner are its provenance
    responsibility. This comparator verifies the board_index and all metric
    fields, not external card manifests. It returns, rather than suppresses,
    every discrepancy so an interrupted/failed readback remains reviewable.
    """
    stack = float(original['stack'])
    if not math.isfinite(stack) or stack <= 0:
        raise ValueError('Invalid original context stack')
    tolerances = metric_tolerances(stack)
    errors, failures = {}, []
    exact_checks = 0

    def exact(path, expected, actual):
        nonlocal exact_checks
        exact_checks += 1
        if expected != actual:
            failures.append(dict(path=path, original=expected, computed=actual, kind='exact'))

    def row(path, a, b):
        exact(path + '.rows', a.get('rows'), b.get('rows'))
        if a.get('rows') == 0 or b.get('rows') == 0:
            for label, value in (('original', a), ('computed', b)):
                if value.get('rows') == 0:
                    exact(path + '.' + label + '.empty_metric_keys', [],
                          sorted(set(value) & set(METRIC_KEYS + COUNT_KEYS[1:])))
            return
        exact(path + '.decisions_outside_indifference_band',
              a.get('decisions_outside_indifference_band'), b.get('decisions_outside_indifference_band'))
        for key in METRIC_KEYS:
            location = path + '.' + key
            if key not in a or key not in b:
                failures.append(dict(path=location, kind='missing_metric'))
                continue
            av, bv = a[key], b[key]
            if av is None or bv is None:
                exact(location, av, bv)
                continue
            if not isinstance(av, (int, float)) or not isinstance(bv, (int, float)) or not math.isfinite(av) or not math.isfinite(bv):
                failures.append(dict(path=location, kind='nonfinite_or_nonnumeric'))
                continue
            error = abs(float(av) - float(bv))
            errors[location] = error
            if error > tolerances[key]:
                failures.append(dict(path=location, original=av, computed=bv,
                                     absolute_error=error, tolerance=tolerances[key], kind='numeric'))

    exact('stack', original.get('stack'), computed.get('stack'))
    row('context', original, computed)
    identities = {'seats': ('actor',), 'price_bands': ('minimum_equity', 'maximum_equity'),
                  'hand_groups': ('name',), 'per_board': ('board_index',)}
    for name in PARTITIONS:
        left, right = original.get(name), computed.get(name)
        if not isinstance(left, list) or not isinstance(right, list):
            failures.append(dict(path=name, kind='missing_partition'))
            continue
        exact(name + '.length', len(left), len(right))
        exact(name + '.original_rows_sum', original.get('rows'), sum(v.get('rows', 0) for v in left))
        exact(name + '.computed_rows_sum', computed.get('rows'), sum(v.get('rows', 0) for v in right))
        for index, (a, b) in enumerate(zip(left, right)):
            path = f'{name}[{index}]'
            for key in identities[name]:
                exact(path + '.' + key, a.get(key), b.get(key))
            row(path, a, b)
    maximum = {key: max((value for path, value in errors.items() if path.endswith('.' + key)), default=0.)
               for key in METRIC_KEYS}
    return dict(passed=not failures, stack=stack, numeric_metrics_checked=len(errors),
                exact_checks=exact_checks, absolute_errors=errors,
                maximum_absolute_error_by_metric=maximum, tolerances=tolerances,
                failures=failures)


def compare_evaluations(original, computed):
    """Verify context packaging and equally weighted means as well as slices."""
    if not original.get('contexts') or not computed.get('contexts'):
        raise ValueError('Both evaluations must contain context records')
    failures = []
    left, right = original['contexts'], computed['contexts']
    if len(left) != len(right):
        failures.append(dict(path='contexts.length', kind='exact'))
    contexts = [compare_context(a, b) for a, b in zip(left, right)]
    count = sum(row['rows'] for row in right)
    if original.get('rows') != computed.get('rows') or computed.get('rows') != count:
        failures.append(dict(path='rows', kind='exact'))
    if original.get('probability_rule') != computed.get('probability_rule'):
        failures.append(dict(path='probability_rule', kind='exact'))
    # math.fsum and explicit division provide an independent equal-context mean.
    independent = {
        'context_balanced_mean_regret_bb': math.fsum(row['mean_regret_bb'] for row in right) / len(right),
        'context_balanced_mean_regret_stack_fraction': math.fsum(row['mean_regret_stack_fraction'] for row in right) / len(right),
    }
    tolerances = {'context_balanced_mean_regret_bb': 1e-4,
                  'context_balanced_mean_regret_stack_fraction': math.fsum(1e-4 / row['stack'] for row in right) / len(right)}
    errors = {}
    for key, rebuilt in independent.items():
        for label, source, tolerance in (('original', original, tolerances[key]), ('computed', computed, 1e-12)):
            value = source.get(key)
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                failures.append(dict(path=label + '.' + key, kind='nonfinite_or_missing'))
                continue
            error = abs(value - rebuilt)
            errors[label + '.' + key] = error
            if error > tolerance:
                failures.append(dict(path=label + '.' + key, absolute_error=error, tolerance=tolerance, kind='numeric'))
    return dict(passed=not failures and all(c['passed'] for c in contexts), contexts=contexts,
                absolute_errors=errors, failures=failures, independently_rebuilt_context_means=independent,
                tolerance_policy=dict(TOLERANCE_POLICY))
