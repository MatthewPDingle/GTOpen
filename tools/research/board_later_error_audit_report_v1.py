"""Descriptive accounting report for frozen baseline fits; no model selection."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import numpy as np
from board_later_fit_holdout_run_v1 import OUT, read, sha, verify
from board_prefix_publication_v1 import atomic_json


def main():
    prefix = 'board-later-error-audit-v1'
    rp = OUT/(prefix+'-registration.json'); result_path = OUT/(prefix+'-result.json')
    registration, result = read(rp), read(result_path)
    assert result['passed'] and result['complete'] and result['registration_sha256'] == sha(rp)
    assert not result['final_test_evaluated'] and not result['cuda_initialized'] and not result['accuracy_qualified']
    verify(registration['inputs']); records = result['datasets']; assert len(records) == 4
    error = max(e for r in records for e in r['baseline_reproduction_absolute_errors'].values()); assert error < 1e-6
    keys = ('row_share', 'source_weight_share', 'error_share', 'target_energy_share')
    pots = []
    for i in range(5):
        label = records[0]['validation_pots'][i]['label']
        assert all(r['validation_pots'][i]['label'] == label for r in records)
        pots.append(dict(label=label, **{key: float(np.mean([r['validation_pots'][i][key] for r in records])) for key in keys}))
    for key in keys: assert abs(sum(p[key] for p in pots)-1) < 1e-12
    concentration = {street: float(np.mean([r['largest_error_one_percent'][street]['weighted_error_share'] for r in records]))
                     for street in ('flop', 'turn', 'river', 'postflop')}
    repeated = {}
    for phase in ('preflop', 'flop', 'turn', 'river', 'postflop'):
        repeated[phase] = {}
        for grouping in ('across_iterations', 'within_iteration'):
            items = [r['training_repetition'][phase][grouping] for r in records]
            repeated[phase][grouping] = dict(rows=sum(r['rows'] for r in items), repeated_rows=sum(r['repeated_rows'] for r in items),
                repeated_groups=sum(r['repeated_groups'] for r in items),
                repeated_row_fraction=sum(r['repeated_rows'] for r in items)/sum(r['rows'] for r in items),
                mean_source_weight_fraction=float(np.mean([r['repeated_source_weight_fraction'] for r in items])),
                effective_count_medians=[r['repeated_effective_count_median'] for r in items],
                observed_disagreement_mse=[r['observed_disagreement_mse'] for r in items])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), layout='constrained')
    x = np.arange(5)
    axes[0].bar(x-.18, [p['source_weight_share']*100 for p in pots], .36, color='#718ea5', label='Source weight')
    axes[0].bar(x+.18, [p['error_share']*100 for p in pots], .36, color='#bf7654', label='Squared error')
    axes[0].set_xticks(x, ['<10', '10–50', '50–100', '100–200', '200+'])
    axes[0].set_xlabel('Current pot (bb)'); axes[0].set_ylabel('Share of postflop total (%)')
    axes[0].set_title('Where held-out prediction error occurs'); axes[0].legend(fontsize=9)
    values = [100*concentration[k] for k in ('flop', 'turn', 'river')]
    axes[1].bar(['Flop', 'Turn', 'River'], values, color='#668c70')
    for i, value in enumerate(values): axes[1].annotate(f'{value:.1f}%', (i, value), xytext=(0, 6), textcoords='offset points', ha='center')
    axes[1].set_ylabel('Share of street squared error (%)'); axes[1].set_title('Error in the largest-error 1% of rows')
    for ax in axes: ax.grid(axis='y', alpha=.2); ax.margins(y=.2)
    fig.supxlabel('Equal-dataset means. Existing validation data; descriptive, not a noise floor or poker-strength test.', fontsize=9)
    plot = OUT/(prefix+'.png'); assert not plot.exists(); fig.savefig(plot, dpi=170); plt.close(fig)
    lines = ['# Prediction-error readback', '',
        'This CPU-only audit reconstructs all four saved 512-step baseline validation results and locates their errors. '
        'It uses existing data; no model was trained, no new deals were generated, and the final test stayed closed.', '',
        f'Maximum absolute difference from the saved GPU validation losses: **{error:.3g}** '
        '(declared tolerance 1e-6). Disjoint bucket totals reproduce the full weighted error, target energy and source mass.', '',
        '## Pot-size concentration', '',
        'The percentages below are equal-dataset means. Pot refers to the current public pot, reconstructed from the native state catalog.', '',
        '| Current pot | Rows | Source weight | Squared error | Target energy |', '|---|---:|---:|---:|---:|']
    for p in pots: lines.append(f'| {p["label"]} | {100*p["row_share"]:.2f}% | {100*p["source_weight_share"]:.2f}% | {100*p["error_share"]:.2f}% | {100*p["target_energy_share"]:.2f}% |')
    lines += ['', f'![Error concentration]({plot.name})', '',
        'Large errors in large pots are not automatically a training defect: the objective is expressed in chip value, '
        'and costly mistakes deserve weight. These totals motivate controlled comparisons, not deleting examples or silently changing the loss.', '',
        '## Repeated training inputs', '',
        'Repeats have identical visible inputs and legal menus. The within-iteration column additionally requires the same training iteration. '
        'These counts combine rows from all four datasets; percentages are row-weighted, not equal-dataset means.', '',
        '| Street | Training rows | Repeated rows across iterations | Repeated rows within iteration |', '|---|---:|---:|---:|']
    for phase in ('preflop', 'flop', 'turn', 'river', 'postflop'):
        a, b = repeated[phase]['across_iterations'], repeated[phase]['within_iteration']
        lines.append(f'| {phase.capitalize()} | {a["rows"]:,} | {a["repeated_rows"]:,} ({100*a["repeated_row_fraction"]:.3f}%) | {b["repeated_rows"]:,} ({100*b["repeated_row_fraction"]:.3f}%) |')
    lines += ['', 'The saved JSON includes every dataset/street, repeat-group effective counts, and observed target disagreement. '
        'An empirical mean fitted to two repeated examples understates predictive uncertainty. Singleton rows supply no repeat-based evidence. '
        'Policy drift, hidden-card variation, correlated samples and stochastic action rollouts may all contribute. '
        'This audit does not identify an irreducible noise floor.', '',
        '## Largest-error rows', '',
        '| Street | Squared error in largest-error 1% of rows |', '|---|---:|']
    for phase, fraction in concentration.items(): lines.append(f'| {phase.capitalize()} | {100*fraction:.2f}% |')
    lines += ['', 'Rows are ranked by their weighted squared error; the selected row count rounds upward. '
        'The metric describes concentration in this sample, not a confidence interval or a rule for excluding difficult examples.', '',
        '## Runtime and scope', '',
        f'Elapsed time including storage admission: {result["seconds"]:.1f} seconds. Four CPU workers, one numerical thread each; '
        f'maximum reported worker resident memory: {max(r["process_rss_bytes"] for r in records)/1e9:.2f} GB. '
        'CUDA was never initialized. Original weights and input files remained unchanged.', '',
        'These are two existing runs and two player datasets per run in one restricted 200bb BB-versus-BTN game. '
        'The result does not validate ranges across other stacks, positions, sizes or multiway situations. Production remains unchanged.']
    report = OUT/'BOARD-LATER-ERROR-AUDIT-FINDINGS.md'; assert not report.exists()
    report.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    atomic_json(OUT/(prefix+'-analysis.json'), dict(inputs={str(p): sha(p) for p in (Path(__file__), rp, result_path)},
        pot_equal_dataset_mean_shares=pots, concentration_equal_dataset_means=concentration,
        repeated_training_inputs=repeated, maximum_baseline_validation_difference=error,
        report_sha256=sha(report), plot_sha256=sha(plot), independent_confirmation=False))
    print(json.dumps(dict(pot_shares=pots, repeat_postflop=repeated['postflop'], report=str(report))))


if __name__ == '__main__': main()
