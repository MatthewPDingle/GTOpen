"""Cheap fixed synthetic controls; no saved corpus, model, or experiment output.

The scalar oracle enumerates every fixture state/holding with Python arithmetic
and sorting. It does not invoke either summarizer or NumPy quantiles. Controls
also inject metric corruption and a near-zero score perturbation that passes
the cash mean tolerance while failing tail/classification readback tolerances.
"""
import copy
import json
import math
import numpy as np
import stack_board_balanced_metrics_v1 as metrics


def scalar_oracle(raw, equity, economics, category, stack, board_count):
    rows = []
    for state_index, state in enumerate(economics.tolist()):
        for card, eq in enumerate(equity.tolist()):
            fold, call_score = map(float, raw[state_index, card, :2])
            positive_fold, positive_call = max(0., fold), max(0., call_score)
            total = positive_fold + positive_call
            probability = positive_call / total if total > 0 else float(call_score > fold)
            delta = state[1] * eq - state[2]
            outside = abs(delta) > stack * .0001
            rows.append(dict(actor=int(state[3]), price=state[4], category=int(category[card]),
                             board=card // 1081, regret=max(delta, 0.) - probability * delta,
                             squared=((call_score * stack - delta) ** 2 + (fold * stack) ** 2) / 2,
                             outside=outside, mistake=outside and ((delta > 0) != (probability >= .5)),
                             fold=max(delta, 0.), call=max(-delta, 0.)))

    def summarize(chosen):
        if not chosen:
            return {'rows': 0}
        n = len(chosen)
        losses = sorted(r['regret'] for r in chosen)
        def quantile(q):
            place = q * (n - 1)
            lo, hi = math.floor(place), math.ceil(place)
            return losses[lo] + (losses[hi] - losses[lo]) * (place - lo)
        mean = math.fsum(losses) / n
        outside = sum(r['outside'] for r in chosen)
        return dict(rows=n, mean_regret_bb=mean, mean_regret_stack_fraction=mean / stack,
                    p95_regret_bb=quantile(.95), p99_regret_bb=quantile(.99),
                    maximum_regret_bb=losses[-1],
                    mean_legal_value_squared_error_bb=math.fsum(r['squared'] for r in chosen) / n,
                    decisions_outside_indifference_band=outside,
                    majority_action_error_rate=sum(r['mistake'] for r in chosen) / outside if outside else None,
                    always_fold_regret_bb=math.fsum(r['fold'] for r in chosen) / n,
                    always_call_regret_bb=math.fsum(r['call'] for r in chosen) / n)
    result = dict(stack=stack, **summarize(rows))
    result['seats'] = [dict(actor=a, **summarize([r for r in rows if r['actor'] == a])) for a in (0, 1)]
    edges = [0., .1, .2, .3, .4, .5, 1.01]
    result['price_bands'] = [dict(minimum_equity=lo, maximum_equity=hi,
                                 **summarize([r for r in rows if lo <= r['price'] < hi]))
                            for lo, hi in zip(edges[:-1], edges[1:])]
    names = ('high_card', 'pair', 'two_pair', 'trips', 'straight', 'flush', 'full_house', 'quads', 'straight_flush')
    result['hand_groups'] = [dict(name=name, **summarize([r for r in rows if r['category'] == i]))
                            for i, name in enumerate(names)]
    result['per_board'] = [dict(board_index=b, **summarize([r for r in rows if r['board'] == b]))
                          for b in range(board_count)]
    return result


def probabilities(raw):
    # Fixture adapter only; no import from an executed experiment helper.
    p = []
    for fold, called in np.asarray(raw).reshape(-1, 2).tolist():
        den = max(fold, 0.) + max(called, 0.)
        p.append(max(called, 0.) / den if den else float(called > fold))
    return np.asarray(p)


def assert_nested_close(a, b, path='root'):
    if isinstance(a, dict):
        assert a.keys() == b.keys(), path
        for key in a:
            assert_nested_close(a[key], b[key], path + '.' + key)
    elif isinstance(a, list):
        assert len(a) == len(b), path
        for i, (left, right) in enumerate(zip(a, b)):
            assert_nested_close(left, right, path + f'[{i}]')
    elif isinstance(a, float):
        assert math.isclose(a, b, rel_tol=2e-13, abs_tol=2e-12), (path, a, b)
    else:
        assert a == b, (path, a, b)


def reject(action):
    try:
        action()
    except (ValueError, TypeError):
        return
    raise AssertionError('Malformed input was accepted')


def run():
    stack, boards = 20., 2
    nc = boards * 1081
    equity = (np.arange(nc) % 991) / 990
    equity[:5] = [0., .5, .5001, .4999, 1.]
    category = np.arange(nc, dtype=np.int64) % 7  # Two unsupported hand groups.
    economics = np.asarray([[20, 12, 1.2, 0, .1], [20, 10, 0, 1, 0],
                            [20, 10, 5, 1, .5], [20, 7, 2.1, 0, .3]], dtype=float)
    index = np.arange(len(economics) * nc, dtype=np.float64).reshape(len(economics), nc)
    raw = np.stack((.2 * np.sin(index * .173), .15 * np.cos(index * .137)), axis=2)
    raw.reshape(-1, 2)[:6] = [[0., 0.], [-.1, -.1], [-.2, -.1], [-.1, -.2], [.1, .1], [.2, 0.]]
    guards = [0]
    def guard():
        guards[0] += 1
    production = metrics.summarize_context(probabilities(raw), raw[:, :, 0], raw[:, :, 1],
                                         equity, economics, category, stack, boards, guard=guard)
    reference = metrics.reference_context(iter(raw), equity, economics, category, stack, boards, guard=guard)
    oracle = scalar_oracle(raw, equity, economics, category, stack, boards)
    assert_nested_close(production, oracle)
    assert_nested_close(reference, oracle)
    comparison = metrics.compare_context(production, reference)
    assert comparison['passed'], comparison['failures']
    assert guards[0] > 30
    assert production['hand_groups'][7] == dict(name='quads', rows=0)
    assert production['price_bands'][2] == dict(minimum_equity=.2, maximum_equity=.3, rows=0)
    for detail in (False,):
        p = metrics.summarize_context(probabilities(raw), raw[:, :, 0], raw[:, :, 1],
                                      equity, economics, category, stack, boards, detail=detail)
        r = metrics.reference_context(iter(raw), equity, economics, category, stack, boards, detail=detail)
        assert_nested_close(p, r)
        assert p['rows'] == len(economics) * nc
    root = metrics.evaluation_summary([production])
    rebuilt = metrics.evaluation_summary([reference])
    assert metrics.compare_evaluations(root, rebuilt)['passed']
    broken = copy.deepcopy(root)
    broken['context_balanced_mean_regret_bb'] += .01
    assert not metrics.compare_evaluations(broken, rebuilt)['passed']

    # Every reported metric class, plus metadata and denominators, is checked.
    corrupted_fields = 0
    for key in metrics.METRIC_KEYS:
        broken = copy.deepcopy(production)
        broken['per_board'][0][key] += 10 * metrics.metric_tolerances(stack)[key]
        assert not metrics.compare_context(broken, reference)['passed'], key
        corrupted_fields += 1
    for field in ('rows', 'decisions_outside_indifference_band', 'board_index'):
        broken = copy.deepcopy(production)
        broken['per_board'][0][field] += 1
        assert not metrics.compare_context(broken, reference)['passed'], field
        corrupted_fields += 1

    # All indifferent rows preserve a zero denominator and None, including the
    # unsupported seat and all but one price band/category.
    tied_equity = np.full(1081, .5)
    tied_economics = np.asarray([[20., 10., 5., 0., .5]])
    tied_category = np.zeros(1081, dtype=np.int64)
    tied_raw = np.zeros((1, 1081, 2))
    tied = metrics.reference_context(tied_raw, tied_equity, tied_economics, tied_category, 20., 1)
    assert tied['decisions_outside_indifference_band'] == 0
    assert tied['majority_action_error_rate'] is None
    assert_nested_close(tied, scalar_oracle(tied_raw, tied_equity, tied_economics, tied_category, 20., 1))

    # A 2e-8 score perturbation affects only one of 1,081 rows, with a 0.05bb
    # payoff. Whole-context mean shift is <1e-4bb but maximum and decision rate
    # exceed preregistered tolerances. The honest result is a failed readback.
    boundary_eq = np.full(1081, .5)
    boundary_eq[0] = .505
    boundary_raw = np.zeros((1, 1081, 2))
    boundary_raw[:, :, 0] = -1e-8
    boundary_raw[:, :, 1] = -2e-8
    changed_raw = boundary_raw.copy()
    changed_raw[0, 0, 1] = 0.
    before = metrics.summarize_context(probabilities(boundary_raw), boundary_raw[:, :, 0], boundary_raw[:, :, 1],
                                       boundary_eq, tied_economics, tied_category, 20., 1)
    after = metrics.reference_context(changed_raw, boundary_eq, tied_economics, tied_category, 20., 1)
    boundary = metrics.compare_context(before, after)
    assert boundary['absolute_errors']['context.mean_regret_bb'] < 1e-4
    assert not boundary['passed']
    assert any(v['path'] == 'context.maximum_regret_bb' for v in boundary['failures'])
    assert any(v['path'] == 'context.majority_action_error_rate' for v in boundary['failures'])

    percentile_boundaries = []
    for affected, payoff, key in ((12, .006, 'p99_regret_bb'), (55, .0015, 'p95_regret_bb')):
        percentile_eq = np.full(1081, .5)
        percentile_eq[:affected] = (5 + payoff) / 10
        percentile_changed = boundary_raw.copy()
        percentile_changed[0, :affected, 1] = 0.
        left = metrics.summarize_context(probabilities(boundary_raw), boundary_raw[:, :, 0], boundary_raw[:, :, 1],
                                         percentile_eq, tied_economics, tied_category, 20., 1)
        right = metrics.reference_context(percentile_changed, percentile_eq, tied_economics, tied_category, 20., 1)
        check = metrics.compare_context(left, right)
        assert check['absolute_errors']['context.mean_regret_bb'] < 1e-4
        assert not check['passed']
        assert any(f['path'] == 'context.' + key for f in check['failures'])
        percentile_boundaries.append(dict(metric=key, affected_rows=affected,
                                           cash_mean_error_bb=check['absolute_errors']['context.mean_regret_bb'],
                                           percentile_error_bb=check['absolute_errors']['context.' + key],
                                           rejected=True))

    # Same finite near-zero values without a sign/argmax crossing remain valid;
    # the tolerance policy is never changed by the preceding rejection.
    stable_raw = raw.copy()
    stable_raw *= 1 + 1e-9
    stable = metrics.reference_context(stable_raw, equity, economics, category, stack, boards)
    assert metrics.compare_context(production, stable)['passed']
    reject(lambda: metrics.reference_context(raw[:-1], equity, economics, category, stack, boards))
    reject(lambda: metrics.reference_context(list(raw) + [raw[0]], equity, economics, category, stack, boards))
    bad_raw = raw.copy()
    bad_raw[0, 0, 0] = np.nan
    reject(lambda: metrics.reference_context(bad_raw, equity, economics, category, stack, boards))
    reject(lambda: metrics.summarize_context(np.full(raw.shape[:2], 2.), raw[:, :, 0], raw[:, :, 1],
                                             equity, economics, category, stack, boards))
    bad_economics = economics.copy()
    bad_economics[0, 4] = 1.01
    reject(lambda: metrics.reference_context(raw, equity, bad_economics, category, stack, boards))
    print(json.dumps(dict(passed=True, synthetic_only=True, scalar_oracle_rows=len(economics) * nc,
                          metric_values_checked=comparison['numeric_metrics_checked'],
                          corrupted_fields_rejected=corrupted_fields,
                          maximum_same_fixture_error=max(comparison['absolute_errors'].values()),
                          near_zero_boundary_mean_error_bb=boundary['absolute_errors']['context.mean_regret_bb'],
                          near_zero_boundary_maximum_error_bb=boundary['absolute_errors']['context.maximum_regret_bb'],
                          near_zero_boundary_readback_failed_as_required=not boundary['passed'],
                          near_zero_percentile_boundaries=percentile_boundaries,
                          guard_calls=guards[0], tolerance_policy=metrics.TOLERANCE_POLICY,
                          files_written=False, gpu_used=False, new_training=False, new_test_data=False)), flush=True)


if __name__ == '__main__':
    run()
