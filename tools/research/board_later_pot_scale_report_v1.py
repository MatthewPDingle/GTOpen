"""Read back the predeclared pot-scaling comparison without further fitting."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import json
from pathlib import Path
import numpy as np
from board_later_fit_holdout_run_v1 import OUT, read, sha, verify
from board_prefix_publication_v1 import atomic_json

ARMS = ('original', 'zero_output', 'pot_scaled')


def main():
    prefix = 'board-later-pot-scale-v1'
    rp = OUT/(prefix+'-registration.json'); result_path = OUT/(prefix+'-result.json')
    registration, result = read(rp), read(result_path)
    assert result['passed'] and result['complete'] and result['registration_sha256'] == sha(rp)
    assert not result['final_test_evaluated'] and not result['production_modified'] and not result['accuracy_qualified']
    verify(registration['inputs']); records = result['datasets']; assert len(records) == 4
    for record in records:
        assert set(record['arms']) == set(ARMS)
        reproduction = record['arms']['original']['baseline_reproduction']
        assert reproduction['maximum_parameter_difference'] < 1e-7 and reproduction['maximum_validation_loss_difference'] < 1e-7
        for arm in ARMS:
            point = record['arms'][arm]; assert point['step'] == 512 and sha(point['weights']) == point['weights_sha256']
            # Reconstruct pooled small-pot loss; do not average bucket means.
            first = point['pots'][:2]
            assert abs(sum(p['squared_error'] for p in first)/sum(p['legal_target_mass'] for p in first)-point['under_50bb']['normalized_loss']) < 1e-12
            post = point['validation']['postflop']
            assert abs(sum(p['squared_error'] for p in point['pots'])/sum(p['legal_target_mass'] for p in point['pots'])-post['normalized_loss']) < 1e-12
    means = {arm: float(np.mean([r['arms'][arm]['validation']['postflop']['normalized_loss'] for r in records])) for arm in ARMS}
    for arm in ARMS: assert abs(means[arm]-result['scores']['postflop'][arm]) < 1e-12
    comparisons = {}
    for baseline in ('original', 'zero_output'):
        change = 100*(means['pot_scaled']/means[baseline]-1)
        all_lower = all(r['arms']['pot_scaled']['validation']['postflop']['normalized_loss'] < r['arms'][baseline]['validation']['postflop']['normalized_loss'] for r in records)
        small_safe = all(r['arms']['pot_scaled']['under_50bb']['normalized_loss'] <= r['arms'][baseline]['under_50bb']['normalized_loss'] for r in records)
        comparisons[baseline] = dict(mean_postflop_change_percent=change, all_four_lower=all_lower, no_under_50bb_regression=small_safe)
        assert comparisons[baseline] == result['comparisons'][baseline]
    qualifies = all(v['mean_postflop_change_percent'] <= -1 and v['all_four_lower'] and v['no_under_50bb_regression'] for v in comparisons.values())
    assert qualifies == result['qualifies_for_policy_comparison']
    buckets = []
    for i in range(5):
        label = records[0]['arms']['original']['pots'][i]['label']
        assert all(r['arms'][a]['pots'][i]['label'] == label for r in records for a in ARMS)
        losses = {a: float(np.mean([r['arms'][a]['pots'][i]['normalized_loss'] for r in records])) for a in ARMS}
        vs_zero = {a: float(np.mean([r['arms'][a]['pots'][i]['loss_relative_to_zero'] for r in records])) for a in ARMS}
        buckets.append(dict(label=label, losses=losses, loss_relative_to_predicting_zero=vs_zero,
            change_from_original_percent=100*(losses['pot_scaled']/losses['original']-1),
            change_from_zero_output_percent=100*(losses['pot_scaled']/losses['zero_output']-1)))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), layout='constrained')
    x = np.arange(4)
    for arm, offset, color, label in [('zero_output', -.18, '#839cad', 'Zero-output start'), ('pot_scaled', .18, '#528b67', 'Pot-scaled + zero start')]:
        values = [100*(r['arms'][arm]['validation']['postflop']['normalized_loss']/r['arms']['original']['validation']['postflop']['normalized_loss']-1) for r in records]
        axes[0].bar(x+offset, values, .36, color=color, label=label)
    axes[0].set_xticks(x, ['BB / seed 1', 'BTN / seed 1', 'BB / seed 2', 'BTN / seed 2'], rotation=15)
    axes[0].set_title('Postflop prediction error vs original start')
    axes[0].set_ylabel('Change in validation error (%)'); axes[0].legend(fontsize=9)
    x = np.arange(5)
    axes[1].bar(x-.18, [p['change_from_original_percent'] for p in buckets], .36, color='#718ea5', label='vs original')
    axes[1].bar(x+.18, [p['change_from_zero_output_percent'] for p in buckets], .36, color='#be7b55', label='vs zero-output start')
    axes[1].set_xticks(x, ['<10', '10–50', '50–100', '100–200', '200+'])
    axes[1].set_xlabel('Current pot (bb)'); axes[1].set_title('Pot-scaled prediction error by pot size')
    axes[1].set_ylabel('Change in validation error (%)'); axes[1].legend(fontsize=9)
    for ax in axes: ax.axhline(0, color='#444444', lw=.8); ax.grid(axis='y', alpha=.2); ax.margins(y=.18)
    fig.supxlabel('Lower is better. Same chip-error objective and 512 steps; reused validation data, not a poker-strength test.', fontsize=9)
    plot = OUT/(prefix+'.png'); assert not plot.exists(); fig.savefig(plot, dpi=170); plt.close(fig)
    headline = 'Pot scaling passes the practical follow-up gate' if qualifies else 'Pot scaling does not pass the practical follow-up gate'
    lines = ['# '+headline, '',
        f'Pot-scaled outputs changed mean postflop validation error by **{comparisons["original"]["mean_postflop_change_percent"]:+.2f}% versus the original model** '
        f'and **{comparisons["zero_output"]["mean_postflop_change_percent"]:+.2f}% versus the same zero-output initialization without scaling**. '
        'These are prediction results on reused validation data, not proof of more accurate or stronger poker ranges.', '',
        '| Dataset | Original loss | Zero-output loss | Pot-scaled loss | Pot vs original | Pot vs zero-output |',
        '|---|---:|---:|---:|---:|---:|']
    for r in records:
        a, b, c = [r['arms'][arm]['validation']['postflop']['normalized_loss'] for arm in ARMS]
        lines.append(f'| {r["dataset"]} | {a:.6f} | {b:.6f} | {c:.6f} | {100*(c/a-1):+.2f}% | {100*(c/b-1):+.2f}% |')
    lines += [f'| Equal-dataset mean | {means["original"]:.6f} | {means["zero_output"]:.6f} | {means["pot_scaled"]:.6f} | {comparisons["original"]["mean_postflop_change_percent"]:+.2f}% | {comparisons["zero_output"]["mean_postflop_change_percent"]:+.2f}% |', '',
        f'![Pot-scaling comparison]({plot.name})', '',
        '## Predeclared decision', '',
        'The gate required at least 1% lower mean loss than both baselines, lower loss in every dataset than both, '
        'and no under-50-bb loss increase in any dataset versus either baseline.', '',
        '| Reference | At least 1% lower mean | Lower in all four | No under-50-bb regression |', '|---|---|---|---|']
    for reference, v in comparisons.items():
        lines.append(f'| {reference} | {v["mean_postflop_change_percent"] <= -1} | {v["all_four_lower"]} | {v["no_under_50bb_regression"]} |')
    lines += ['', '## Pot-size results', '',
        'Each loss is an equal-dataset mean in the original normalized chip units. All input examples and source weights were retained.', '',
        '| Current pot | Original loss | Zero-output loss | Pot-scaled loss | Pot vs original | Pot vs zero-output |', '|---|---:|---:|---:|---:|---:|']
    for p in buckets:
        a, b, c = (p['losses'][arm] for arm in ARMS)
        lines.append(f'| {p["label"]} | {a:.6f} | {b:.6f} | {c:.6f} | {p["change_from_original_percent"]:+.2f}% | {p["change_from_zero_output_percent"]:+.2f}% |')
    lines += ['', '## Why the calculation remains comparable', '',
        'The candidate predicts `g*f`, where g is the current public pot divided by 10 postflop and one preflop. '
        'Training targets divide by g while weights multiply by g squared, preserving the original chip-error loss and denominator. '
        'No difficult examples were removed, and errors were restored to original units before evaluation.', '',
        'Both comparison arms start with zero outputs by zeroing only their last layer. Hidden-layer seeds and all other fitting settings match. '
        'The original initialization is retained as a third arm to separate initialization from scaling. '
        'All four original-arm repeats reproduced the saved weights and validation losses within 1e-7. '
        'Captured/eager training and factor-one controls matched exactly; direct gradient and scoring controls passed.', '',
        '## Runtime and limits', '',
        f'Total time including preparation/storage admission: {result["seconds"]/60:.2f} minutes. '
        f'Retained output size: {result["retained_bytes"]/1e6:.2f} MB. '
        f'Peak own CUDA allocation: {max(a["timing"]["peak_allocated_bytes"] for r in records for a in r["arms"].values())/1e9:.3f} GB. '
        'Four CPU workers prepared inputs, and a single GPU trained the models with the desktop-sharing guard enabled.', '',
        'The experiment reused four datasets from two existing runs of one restricted 200bb BB-versus-BTN game. '
        'No new deals or final-test scores were generated. It does not establish robustness across positions, stacks, sizes or multiway play. '
        'Production is unchanged.', '',
        '## Next action', '',
        ('Qualify this representation through complete policy training and fresh-deal evaluation before adopting it.' if qualifies else
         'Preserve the full mixed/negative result. Do not promote pot scaling on this evidence. Inspect the separate initialization result and remaining data/policy uncertainty before another large training trial.')]
    report = OUT/'BOARD-LATER-POT-SCALE-FINDINGS.md'; assert not report.exists(); report.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    atomic_json(OUT/(prefix+'-analysis.json'), dict(inputs={str(p): sha(p) for p in (Path(__file__), rp, result_path)},
        postflop_means=means, comparisons=comparisons, pot_buckets=buckets, qualifies_for_policy_comparison=qualifies,
        report_sha256=sha(report), plot_sha256=sha(plot), independent_confirmation=False))
    print(json.dumps(dict(qualifies=qualifies, means=means, comparisons=comparisons, report=str(report))))


if __name__ == '__main__': main()
