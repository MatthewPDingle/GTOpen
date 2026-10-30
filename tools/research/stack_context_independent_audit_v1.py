"""Read-only numerical audit of the frozen matched-stack result.

Uses NumPy reductions instead of the evaluator's streaming statistics, and
physical private holdings instead of its class-pair range propagation. No
imports from the analysis, export, model, sampler or native evaluator modules.
This audits supplied evidence; it does not authenticate files or prove that
the supplied policies were produced by the selected models. The final reader
must establish those identities separately.
"""
import itertools
import math
from statistics import NormalDist
import numpy as np

DEPTHS = (20, 40, 60, 100, 150, 200, 400)
N = 4096
ALPHA = .05
CONTRASTS = tuple(f'{seed}:{name}' for seed in ('first', 'replication') for name in (
    'newBB-v-oldBB-against-oldBTN', 'newBB-v-oldBB-against-newBTN',
    'newBTN-v-oldBTN-against-oldBB', 'newBTN-v-oldBTN-against-newBB'))
PROFILES = tuple(f'{seed}:{pair}' for seed in ('first', 'replication') for pair in (
    'oldBB-oldBTN', 'oldBB-newBTN', 'newBB-oldBTN', 'newBB-newBTN'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(actual, expected, label, *, atol=1e-10, rtol=2e-11):
    a, b = np.asarray(actual, dtype=float), np.asarray(expected, dtype=float)
    require(a.shape == b.shape and np.isfinite(a).all() and np.isfinite(b).all(),
            label + ': nonfinite or wrong shape')
    require(np.all(np.abs(a-b) <= atol + rtol*np.abs(b)), label + ': differs from independent calculation')
    return float(np.max(np.abs(a-b))) if a.size else 0.


def exact(actual, expected, label):
    require(type(actual) is type(expected) and actual == expected, label + ': changed field')


def numerical_context(values, depth):
    """All primary statistics recomputed without the streaming implementation."""
    require(type(depth) is int and depth in DEPTHS, 'Unregistered depth')
    values = np.asarray(values, dtype=float)
    require(values.shape == (N, 2, 4, 2) and np.isfinite(values).all(), 'Complete finite final sample required')
    require(np.all(values >= -depth) and np.all(values <= depth+.5), 'Physical payoff bounds violated')
    # Explicit coefficient tensors avoid reusing the evaluator's differences().
    coefficients = np.zeros((8, 2, 4, 2))
    for seed in range(2):
        for offset, (actor, plus, minus) in enumerate(((0, 2, 0), (0, 3, 1), (1, 1, 0), (1, 3, 2))):
            coefficients[4*seed+offset, seed, plus, actor] = 1
            coefficients[4*seed+offset, seed, minus, actor] = -1
    delta = values.reshape(N, 16) @ coefficients.reshape(8, 16).T
    mean = delta.mean(axis=0)
    variance = delta.var(axis=0, ddof=1)
    se = np.sqrt(variance/N)
    bound = 2*depth+.5
    log_factor = math.log(4*56/ALPHA)  # 56 simultaneous two-sided contrasts, one look.
    radius = np.sqrt(2*variance*log_factor/N) + 14*bound*log_factor/(3*(N-1))
    z = NormalDist().inv_cdf(1-ALPHA/(2*56))
    tails = np.quantile(-delta, [.95, .99], axis=0, method='linear')
    result = []
    for index, name in enumerate(CONTRASTS):
        result.append(dict(name=name, count=N, mean=float(mean[index]), sample_variance=float(variance[index]),
            radius=float(radius[index]), lower=float(max(-bound, mean[index]-radius[index])),
            upper=float(min(bound, mean[index]+radius[index])), standard_error=float(se[index]),
            family_error_probability=ALPHA/7, bounds_best_response_above=False,
            negative_deal_fraction=float(np.count_nonzero(delta[:, index] < 0)/N),
            paired_loss_95_bb=float(tails[0, index]), paired_loss_99_bb=float(tails[1, index]),
            worst_observed_paired_loss_bb=float(np.max(-delta[:, index])),
            mean_positive_paired_loss_bb=float(np.clip(-delta[:, index], 0, None).mean()),
            exploratory_normal_interval=dict(lower=float(mean[index]-z*se[index]),
                upper=float(mean[index]+z*se[index]), z=z, finite_sample_guarantee=False)))
    flat = values.reshape(N, 8, 2)
    return dict(depth=depth, contrasts=result, per_deal_value_ranges=[dict(profile=name,
        minimum_player_value_bb=flat[:, i].min(axis=0).tolist(),
        maximum_player_value_bb=flat[:, i].max(axis=0).tolist()) for i, name in enumerate(PROFILES)])


def audit_comparison(comparison, values_by_depth):
    """Verify every reported numeric statistic, selection-independent gate and scope flag."""
    require(set(values_by_depth) == set(DEPTHS), 'Seven complete independent test contexts required')
    exact(comparison['format'], 1, 'format')
    exact(comparison['simultaneous_family_alpha'], ALPHA, 'family alpha')
    for key, flag in (('fixed_policy_evaluation_complete', True), ('preflop_accuracy_qualified', False),
                      ('production_promotion', False)):
        exact(comparison[key], flag, key)
    contexts = comparison['contexts']
    require(isinstance(contexts, list) and len(contexts) == 7 and
            tuple(row['depth'] for row in contexts) == DEPTHS, 'Changed context order or count')
    independent = []
    max_error = 0.
    for depth, context in zip(DEPTHS, contexts):
        reference = numerical_context(values_by_depth[depth], depth)
        independent.append(reference)
        for key, wanted in (('deals', N), ('family_error_probability', ALPHA/7), ('dead_money', .5),
                ('profile_order', list(PROFILES)), ('split', 'heldout' if depth in (60, 150) else 'fit'),
                ('bounds_best_response_above', False), ('accuracy_qualified', False),
                ('exploratory_normal_family_size', 56), ('exploratory_normal_finite_sample_guarantee', False)):
            exact(context[key], wanted, f'{depth}/{key}')
        require(len(context['contrasts']) == 8, 'Wrong contrast count')
        for actual, wanted in zip(context['contrasts'], reference['contrasts']):
            require(set(actual) == set(wanted), 'Missing or unexpected contrast fields')
            for key, value in wanted.items():
                label = f'{depth}/{wanted["name"]}/{key}'
                if key == 'exploratory_normal_interval':
                    require(set(actual[key]) == set(value), 'Changed exploratory interval fields')
                    exact(actual[key]['finite_sample_guarantee'], False, label)
                    for part in ('lower', 'upper', 'z'):
                        max_error = max(max_error, close(actual[key][part], value[part], label+'/'+part))
                elif key in ('name', 'count', 'bounds_best_response_above', 'family_error_probability'):
                    exact(actual[key], value, label)
                else:
                    max_error = max(max_error, close(actual[key], value, label))
        require(len(context['per_deal_value_ranges']) == 8, 'Wrong payoff range count')
        for actual, wanted in zip(context['per_deal_value_ranges'], reference['per_deal_value_ranges']):
            exact(actual['profile'], wanted['profile'], 'Payoff range profile order')
            for key in ('minimum_player_value_bb', 'maximum_player_value_bb'):
                max_error = max(max_error, close(actual[key], wanted[key], key, atol=0, rtol=0))
    pooled = []
    for i, name in enumerate(CONTRASTS):
        pooled.append(dict(name=name, **{key:math.fsum(r['contrasts'][i][key]/r['depth'] for r in independent)/7
            for key in ('mean', 'lower', 'upper')}))
    require(len(comparison['equal_depth_normalized_gains']) == 8, 'Wrong pooled comparison count')
    for actual, wanted in zip(comparison['equal_depth_normalized_gains'], pooled):
        exact(actual['name'], wanted['name'], 'Pooled contrast order')
        exact(actual['units'], 'starting-stack fraction per entry', 'Pooled units')
        exact(actual['equal_depth_weight'], 1/7, 'Pooled depth weight')
        for key in ('mean', 'lower', 'upper'):
            max_error = max(max_error, close(actual[key], wanted[key], 'Pooled '+key))
    negatives = [dict(depth=r['depth'], name=c['name'], mean_bb=c['mean'])
                 for r in independent for c in r['contrasts'] if c['mean'] < 0]
    actual_negative = comparison['negative_depth_point_estimates']
    require(len(actual_negative) == len(negatives), 'Negative depth list differs')
    for actual, wanted in zip(actual_negative, negatives):
        exact(actual['depth'], wanted['depth'], 'Negative depth')
        exact(actual['name'], wanted['name'], 'Negative contrast')
        close(actual['mean_bb'], wanted['mean_bb'], 'Negative mean')
    positive = all(r['lower'] > 0 for r in pooled)
    exact(comparison['all_eight_pooled_lower_bounds_positive'], positive, 'Bound gate')
    exact(comparison['registered_policy_improvement_criterion_met'], positive and not negatives, 'Primary gate')
    return dict(passed=True, depths=7, contrasts=56, deals_per_depth=N, maximum_numeric_error=max_error,
        independent_primary_gate=positive and not negatives, negative_depth_contrasts=len(negatives),
        calculation='NumPy vector reductions and quantiles; separately encoded contrasts and bounded interval formula',
        authenticated_files=False, policy_identity_verified=False, scientific_accuracy_qualified=False)


def physical_population(context):
    """Reconstruct compatible physical holdings without sampler/class-matrix imports."""
    cards = np.asarray(list(itertools.combinations(range(52), 2)), dtype=int)
    ranks = cards//4
    suited = cards[:, 0] % 4 == cards[:, 1] % 4
    classes = np.where(suited, ranks[:, 1]*13+ranks[:, 0], ranks[:, 0]*13+ranks[:, 1])
    counts = np.bincount(classes, minlength=169)
    incoming = np.asarray(context['incoming_class_mass'], dtype=float)
    require(incoming.shape == (2, 169) and np.isfinite(incoming).all() and np.all(incoming >= 0)
            and np.all(incoming.sum(axis=1) > 0), 'Invalid original entry population')
    weights = incoming[:, classes]/counts[classes]
    weights /= weights.max(axis=1)[:, None]
    weights[weights < 1e-5] = 0  # Preserve the registered cutoff, never reselect support.
    a, b = cards[:, 0], cards[:, 1]
    compatible = ((a[:, None] != a[None, :]) & (a[:, None] != b[None, :]) &
                  (b[:, None] != a[None, :]) & (b[:, None] != b[None, :]))
    pairs = weights[0, :, None]*weights[1, None, :]*compatible
    require(float(pairs.sum()) > 0, 'No compatible entry mass')
    pairs /= pairs.sum()
    return cards, classes, pairs


def audit_ranges(context, result, *, guard):
    """Recompute node ranges from 1,326 physical holdings and both players' paths.

The exported probabilities are inputs here, not independently established
model outputs. A separate policy replay must authenticate those probabilities.
The own-support identity uses telescoping perfect-recall behavioral averages.
"""
    exact(result['format'], 1, 'Range format')
    exact(result['accuracy_qualified'], False, 'Range accuracy scope')
    cards, classes, joint = physical_population(context)
    tree = context['nodes']; rows = result['nodes']
    require(isinstance(rows, list), 'Expected exported node list')
    bynode = {row['node']:row for row in rows}
    require(len(bynode) == len(rows), 'Repeated exported decision')
    visited = set(); decisions = set(); leaves = []; zero = 0; errors = []
    todo = [(0, [], np.ones((2, len(cards))))]
    while todo:
        guard()
        node, path, reach = todo.pop()
        require(type(node) is int and 0 <= node < len(tree) and node not in visited,
                'Invalid, shared or cyclic native topology')
        visited.add(node); native = tree[node]
        actor = native['actor']; children = native['children']
        if not children:
            leaves.append(float(reach[0] @ (joint @ reach[1])))
            continue
        require(actor in (0, 1) and 1 <= len(children) <= 4 and len(native['actions']) == len(children),
                'Invalid native decision')
        decisions.add(node)
        require(node in bynode, 'Missing exported decision')
        row = bynode[node]
        exact(row['actor'], actor, 'Actor')
        exact(row['actions'], native['actions'], 'Action identity')
        exact(row['path'], path, 'Ancestor action identity')
        p = np.asarray(row['action_probabilities_by_class'], dtype=float)
        require(p.shape == (169, len(children)) and np.isfinite(p).all() and np.all(p >= 0), 'Invalid exported action matrix')
        close(p.sum(axis=1), np.ones(169), 'Action normalization', atol=1e-12, rtol=0)
        # Dense physical marginalization is independent of the export's 169x169 recursion.
        physical_mass = reach[actor]*((joint if actor == 0 else joint.T) @ reach[1-actor])
        total = float(physical_mass.sum())
        class_mass = np.bincount(classes, weights=physical_mass, minlength=169)
        errors.append(close(row['probability_of_reaching_node'], total, 'Node probability', atol=1e-12))
        errors.append(close(row['entry_mass_by_class'], class_mass, 'Entry class mass', atol=1e-12))
        exact(row['zero_node_reach'], total == 0, 'Zero arrival node')
        exact(row['in_arriving_range'], (class_mass > 0).tolist(), 'Zero arrival hands')
        support = np.asarray(row['own_history_weighted_model_support_by_class'], dtype=float)
        require(support.shape == (169,) and np.isfinite(support).all() and np.all(support >= 0), 'Invalid model support')
        # Sum 1..64 = 2080. Same actor's earlier behavioral probabilities
        # telescope to the weighted model own-reach sum at this decision.
        errors.append(close(support[classes], 2080*reach[actor], 'Perfect-recall weighted model support', atol=1e-8))
        if total:
            errors.append(close(row['conditional_range_by_class'], class_mass/total, 'Arriving range', atol=1e-12))
            action_mass = np.sum(physical_mass[:, None]*p[classes], axis=0)
            errors.append(close(row['conditional_action_frequencies'], action_mass/total, 'Conditional action frequency', atol=1e-12))
        else:
            zero += 1
            exact(row['conditional_range_by_class'], None, 'Unavailable arriving range')
            exact(row['conditional_action_frequencies'], None, 'Unavailable action frequency')
        for action, child in reversed(list(enumerate(children))):
            next_reach = reach.copy()
            next_reach[actor] *= p[classes, action]
            todo.append((child, path+[[node, action]], next_reach))
    require(visited == set(range(len(tree))) and decisions == set(bynode), 'Incomplete native or exported topology')
    close(math.fsum(leaves), 1., 'Physical terminal mass', atol=1e-11, rtol=0)
    close(result['terminal_entry_mass'], math.fsum(leaves), 'Reported terminal mass', atol=1e-11, rtol=0)
    for key, limit in (('maximum_preflop_suit_policy_error', 1e-12), ('maximum_preflop_suit_support_error', 1e-10)):
        value = result[key]
        require(type(value) in (float, int) and math.isfinite(value) and 0 <= value <= limit, 'Reported suit invariance failed')
    return dict(passed=True, decision_nodes=len(decisions), zero_arrival_nodes=zero,
        terminal_nodes=len(leaves), physical_holdings=len(cards), maximum_numeric_error=max(errors, default=0),
        terminal_entry_mass=math.fsum(leaves), perfect_recall_weight_sum=2080,
        policy_identity_verified=False, scope='Physical-card range and own-reach consistency, conditional on authenticated exported policies')
