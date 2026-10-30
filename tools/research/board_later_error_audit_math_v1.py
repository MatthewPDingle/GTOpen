"""Descriptive error accounting; repeated samples are not a noise-floor estimate."""
import math
import numpy as np


def row_totals(prediction, values, arity, weights, scale):
    prediction = np.asarray(prediction, dtype=np.float64)
    target = np.asarray(values, dtype=np.float64)/scale
    arity = np.asarray(arity); weights = np.asarray(weights, dtype=np.float64)
    assert prediction.shape == target.shape == (len(weights), 4)
    assert scale > 0 and np.isfinite(scale) and np.all(weights > 0)
    assert np.all((arity >= 2) & (arity <= 4))
    assert np.isfinite(prediction).all() and np.isfinite(target).all() and np.isfinite(weights).all()
    legal = np.arange(4)[None, :] < arity[:, None]
    assert not np.any(target[~legal])
    return dict(error=((prediction-target)**2*legal*weights[:, None]).sum(axis=1),
                energy=(target**2*legal*weights[:, None]).sum(axis=1),
                mass=weights*arity, weight=weights)


def totals(rows, mask):
    count = int(np.count_nonzero(mask))
    error, energy, mass, weight = (float(rows[k][mask].sum()) for k in ('error', 'energy', 'mass', 'weight'))
    return dict(rows=count, squared_error=error, target_energy=energy, legal_target_mass=mass,
                source_weight=weight, normalized_loss=error/mass if mass else None,
                loss_relative_to_zero=error/energy if energy else None)


def partition(rows, parent, bins):
    """Bins are disjoint masks exhausting parent; include empty cells explicitly."""
    reference = totals(rows, parent); covered = np.zeros(len(parent), dtype=int); result = []
    for label, mask in bins:
        assert np.all(~mask | parent)
        covered += mask.astype(int)
        value = totals(rows, mask)
        value.update(label=str(label), row_share=value['rows']/reference['rows'],
            source_weight_share=value['source_weight']/reference['source_weight'],
            error_share=value['squared_error']/reference['squared_error'] if reference['squared_error'] else 0.,
            target_energy_share=value['target_energy']/reference['target_energy'] if reference['target_energy'] else 0.)
        result.append(value)
    assert np.array_equal(covered, parent.astype(int))
    for key in ('rows', 'squared_error', 'target_energy', 'legal_target_mass', 'source_weight'):
        assert np.isclose(sum(v[key] for v in result), reference[key], rtol=1e-12, atol=1e-10), key
    return result


def concentration(rows, mask):
    indices = np.flatnonzero(mask); count = max(1, math.ceil(len(indices)*.01))
    selected = indices[np.argsort(rows['error'][indices], kind='stable')[-count:]]
    top = np.zeros(len(mask), dtype=bool); top[selected] = True
    total = totals(rows, mask); value = totals(rows, top)
    return dict(selected_rows=count, eligible_rows=len(indices), row_fraction=count/len(indices),
                weighted_error_share=value['squared_error']/total['squared_error'] if total['squared_error'] else 0.,
                source_weight_share=value['source_weight']/total['source_weight'])


def repetition(active, arity, values, weights, iterations, scale, *, within_iteration):
    """Empirical disagreement in covered duplicate groups; no singleton estimate."""
    values = np.asarray(values, dtype=np.float64); weights = np.asarray(weights, dtype=np.float64)
    keys = np.column_stack((active, arity, iterations)) if within_iteration else np.column_stack((active, arity))
    _, inverse, counts = np.unique(keys, axis=0, return_inverse=True, return_counts=True)
    mass = np.bincount(inverse, weights=weights); square_mass = np.bincount(inverse, weights=weights**2)
    target = values/scale; means = np.zeros((len(counts), 4), dtype=np.float64)
    np.add.at(means, inverse, target*weights[:, None]); means /= mass[:, None]
    repeated = counts[inverse] > 1; repeated_groups = counts > 1
    legal = np.arange(4)[None, :] < arity[:, None]
    residual = ((target-means[inverse])**2*legal*weights[:, None]).sum(axis=1)
    energy = (target**2*legal*weights[:, None]).sum(axis=1)
    error = float(residual[repeated].sum()); den = float((weights*arity)[repeated].sum())
    repeat_energy = float(energy[repeated].sum())
    effective = mass[repeated_groups]**2/square_mass[repeated_groups]
    return dict(rows=len(active), groups=len(counts), repeated_groups=int(repeated_groups.sum()),
        repeated_rows=int(repeated.sum()), repeated_row_fraction=float(repeated.mean()),
        repeated_source_weight_fraction=float(weights[repeated].sum()/weights.sum()),
        maximum_group_rows=int(counts.max()), observed_disagreement_sse=error,
        observed_disagreement_mse=error/den if den else None,
        disagreement_fraction_of_repeated_target_energy=error/repeat_energy if repeat_energy else None,
        repeated_effective_count_min=float(effective.min()) if len(effective) else None,
        repeated_effective_count_median=float(np.median(effective)) if len(effective) else None,
        within_iteration=within_iteration)


def public_amounts(active, arity, catalog):
    """Join exact native chip values; do not reconstruct chips from float features."""
    table = {(r['public_id'], r['actor'], r['phase'], tuple(r['history'])): r for r in catalog['rows']}
    assert len(table) == catalog['decision_templates']
    unique, inverse = np.unique(np.column_stack((active[:, 14:], arity)), axis=0, return_inverse=True)
    pot = np.full(len(unique), np.nan); starting = pot.copy()
    for i, row in enumerate(unique):
        actor = int(row[0])-133; phase = int(row[1])-135; public = int(row[2])-139
        assert actor in (0, 1) and phase in range(4)
        history = [int(x)-(155+6*j) for j, x in enumerate(row[3:22])]
        assert all(0 <= x <= 5 for x in history)
        end = next((j for j, value in enumerate(history) if value == 0), len(history))
        assert not any(history[end:])
        if phase == 0:
            assert end == 0; continue
        native = table[(public, actor, phase, tuple(history[:end]))]
        assert int(row[-1]) == native['legal_actions']
        pot[i] = native['pot']; starting[i] = native['starting_pot']
        assert pot[i] >= starting[i] > 0
    return pot[inverse], starting[inverse]


def control():
    active = np.array([[0], [0], [1]])
    arity = np.array([2, 2, 2]); weights = np.array([1., 3., 2.]); iterations = np.array([1, 2, 1])
    values = np.array([[1., 3., 0., 0.], [3., 1., 0., 0.], [2., 4., 0., 0.]])
    rows = row_totals(np.ones((3, 4)), values, arity, weights, 1.)
    assert np.array_equal(rows['error'], [4., 12., 20.]) and np.array_equal(rows['energy'], [10., 30., 40.])
    all_rows = np.ones(3, dtype=bool); value = totals(rows, all_rows)
    assert value['squared_error'] == 36 and value['target_energy'] == 80 and value['normalized_loss'] == 3
    result = partition(rows, all_rows, [('a', np.array([True, True, False])), ('b', np.array([False, False, True]))])
    assert result[0]['normalized_loss'] == 2 and result[1]['normalized_loss'] == 5
    repeat = repetition(active, arity, values, weights, iterations, 1., within_iteration=False)
    assert repeat['observed_disagreement_sse'] == 6 and repeat['observed_disagreement_mse'] == .75
    assert repeat['repeated_effective_count_median'] == 1.6 and repeat['repeated_source_weight_fraction'] == 2/3
    assert repetition(active, arity, values, weights, iterations, 1., within_iteration=True)['repeated_rows'] == 0
    assert concentration(rows, all_rows)['weighted_error_share'] == 20/36
    order = np.array([2, 0, 1])
    assert repeat == repetition(active[order], arity[order], values[order], weights[order], iterations[order], 1., within_iteration=False)
    return dict(passed=True, hand_calculated_weighted_totals=True, partition_identity=True,
                repeated_target_disagreement=True, effective_count=True, iteration_grouping=True,
                row_order_independent=True, largest_error_concentration=True)
