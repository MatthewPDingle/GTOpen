"""Read back the frozen public-input experiment and publish its full result."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import json
from pathlib import Path
import numpy as np
from board_later_fit_holdout_run_v1 import OUT, read, sha, verify
from board_prefix_publication_v1 import atomic_json


def main():
    prefix = 'board-later-public-state-fit-v1'
    result_path = OUT/(prefix+'-result.json'); registration_path = OUT/(prefix+'-registration.json')
    result = read(result_path); registration = read(registration_path)
    assert result['passed'] and result['complete'] and result['registration_sha256'] == sha(registration_path)
    assert not result['final_test_evaluated'] and not result['accuracy_qualified'] and not result['production_modified']
    verify(registration['inputs'])
    rows = []; train_changes = []; records = result['datasets']
    assert len(records) == 4
    for record in records:
        assert set(record['arms']) == {'baseline', 'public_inputs'}
        base, candidate = (record['arms'][a] for a in ('baseline', 'public_inputs'))
        assert base['baseline_reproduction']['maximum_parameter_difference'] < 1e-7
        assert base['baseline_reproduction']['maximum_validation_loss_difference'] < 1e-7
        for arm in (base, candidate):
            assert arm['step'] == 512 and sha(arm['weights']) == arm['weights_sha256']
            for key in ('all', 'postflop', 'preflop', 'flop', 'turn', 'river'):
                assert arm['validation'][key]['rows'] == base['validation'][key]['rows']
        a, b = (arm['validation']['postflop']['normalized_loss'] for arm in (base, candidate))
        rows.append(dict(dataset=record['dataset'], baseline=a, public_inputs=b, relative_change_percent=100*(b/a-1)))
        train_changes.append(100*(candidate['normalized_training_loss']/base['normalized_training_loss']-1))
    for phase, expected in result['scores'].items():
        a, b = (float(np.mean([r['arms'][arm]['validation'][phase]['normalized_loss'] for r in records]))
                for arm in ('baseline', 'public_inputs'))
        assert abs(a-expected['baseline']) < 1e-12 and abs(b-expected['public_inputs']) < 1e-12
        assert abs(100*(b/a-1)-expected['relative_change_percent']) < 1e-10
    change = result['scores']['postflop']['relative_change_percent']
    qualifies = change <= -1 and all(r['relative_change_percent'] < 0 for r in rows)
    assert qualifies == result['qualifies_for_policy_comparison']
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), layout='constrained')
    labels = ['BB / seed 1', 'BTN / seed 1', 'BB / seed 2', 'BTN / seed 2']
    def bars(ax, names, values):
        ax.bar(names, values, color=['#429066' if v < 0 else '#bd7251' for v in values])
        ax.axhline(0, color='#555555', lw=.8)
        for i, value in enumerate(values):
            ax.annotate(f'{value:+.2f}%', (i, value), xytext=(0, -13 if value < 0 else 5),
                        textcoords='offset points', ha='center', fontsize=10)
        ax.margins(y=.25); ax.grid(axis='y', alpha=.2)
    bars(axes[0], labels, [r['relative_change_percent'] for r in rows])
    axes[0].set_title('Each dataset: postflop validation error')
    axes[0].tick_params(axis='x', labelrotation=15)
    bars(axes[1], ['Flop', 'Turn', 'River'], [result['scores'][s]['relative_change_percent'] for s in ('flop', 'turn', 'river')])
    axes[1].set_title('Each street: equal-dataset mean error')
    axes[0].set_ylabel('Change from original inputs (%) — lower is better')
    fig.suptitle(f'Explicit pot / stack / price inputs: {change:+.2f}% mean validation error', fontsize=13)
    fig.supxlabel('Same retained data and 512-step fits. Reused validation split; poker strength untested.', fontsize=9)
    plot = OUT/(prefix+'.png'); assert not plot.exists(); fig.savefig(plot, dpi=170); plt.close(fig)
    headline = 'Public betting inputs qualify for a full-policy comparison' if qualifies else 'Public betting inputs did not meet the improvement threshold'
    lines = ['# '+headline, '',
        f'The 12 added public inputs changed mean postflop validation error by **{change:+.2f}%**. '
        f'{sum(r["relative_change_percent"] < 0 for r in rows)} of four datasets improved. '
        'This is a prediction diagnostic on retained training examples and a reused validation split; it is not evidence of stronger preflop play.', '',
        '| Dataset | Original loss | Public-input loss | Change |', '|---|---:|---:|---:|']
    for row in rows:
        lines.append(f'| {row["dataset"]} | {row["baseline"]:.6f} | {row["public_inputs"]:.6f} | {row["relative_change_percent"]:+.2f}% |')
    lines += ['', 'The practical threshold was at least 1% lower mean loss and improvement in every dataset. '
              + ('It was met.' if qualifies else 'It was not met.'), '', f'![Comparison]({plot.name})', '',
        '## What changed', '',
        'The original 302 inputs were retained. Twelve numerical inputs explicitly described the pot, remaining stacks, '
        'amount to call, calling price, effective stack-to-pot ratio, starting pot/stack and available action costs. '
        'The same facts were already implied by public betting history in this fixed game; the candidate made them easier to access. '
        'It also added 768 weights, so the comparison does not isolate representation from parameter count.', '',
        'Data, split, seeds, target scale, network width, learning rate and 512-step fitting budget were fixed. '
        'The additional input weights started at zero. All four original-model repeats reproduced their saved weights and validation loss '
        f'within 1e-7 (maximum parameter difference: {max(r["arms"]["baseline"]["baseline_reproduction"]["maximum_parameter_difference"] for r in records):.3g}). '
        'The CUDA training check matched ordinary training exactly on a multichunk real-data fixture spanning all streets.', '',
        '| Street | Original mean loss | Public-input mean loss | Change |', '|---|---:|---:|---:|']
    for street in ('flop', 'turn', 'river'):
        s = result['scores'][street]
        lines.append(f'| {street.capitalize()} | {s["baseline"]:.6f} | {s["public_inputs"]:.6f} | {s["relative_change_percent"]:+.2f}% |')
    lines += ['', '## Resources and limits', '',
        f'The full comparison took {result["seconds"]/60:.2f} minutes including preparation and resource checks. '
        f'Retained outputs total {result["retained_bytes"]/1e6:.2f} MB. '
        f'Peak own CUDA allocation was {max(a["timing"]["peak_allocated_bytes"] for r in records for a in r["arms"].values())/1e9:.3f} GB. '
        'Two CPU workers prepared datasets; one GPU trained the models. The light-desktop sharing guard remained enabled.', '',
        'All inputs come from two existing training runs in the same restricted 200bb BB-versus-BTN game. '
        'The four seat/seed datasets are not four independent poker environments. No new deals or final-test scores were generated. '
        'No generalization across stacks, positions, sizes or multiway play has been established. Production is unchanged.', '',
        '## Next step', '',
        ('Implement the same inputs throughout a separate, paired full-policy training trial, including checkpoint loading and policy evaluation. '
         'Require fresh-deal policy evaluation before deciding whether to adopt it.' if qualifies else
         'Keep this negative or mixed result. Do not spend a full-policy training run on this representation yet. '
         'Use the existing training data to separate predictable structure from noisy sampled targets before choosing another larger experiment.')]
    report = OUT/'BOARD-LATER-PUBLIC-STATE-FINDINGS.md'; assert not report.exists()
    report.write_text('\n'.join(lines)+'\n', encoding='utf-8')
    atomic_json(OUT/(prefix+'-analysis.json'), dict(inputs={str(p): sha(p) for p in (Path(__file__), result_path, registration_path)},
        dataset_changes=rows, all_street_training_loss_relative_changes_percent=train_changes,
        qualifies_for_policy_comparison=qualifies, independent_confirmation=False,
        plot_sha256=sha(plot), report_sha256=sha(report)))
    print(json.dumps(dict(qualifies=qualifies, change_percent=change, report=str(report))))


if __name__ == '__main__': main()
