"""Render completed training/reconstruction/transfer results without partial rows."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def main():
    inputs = {}

    def read(path):
        path = Path(path)
        data = path.read_bytes()
        inputs[str(path.relative_to(ROOT))] = hashlib.sha256(data).hexdigest()
        return json.loads(data)

    state = read(OUT/'population-supplement-status.json')
    assert state['step'] == 'complete-awaiting-scientific-review', 'Wait for complete supplement'
    summary = read(OUT/'population-supplement-summary.json')
    assert len(summary) == 6
    assert {(r['panel'], r['source']) for r in summary} == {
        (p, s) for p in ['excluded69', 'population164', 'sourcepanel'] for s in ['ab', 'report47']}
    values = {}
    sources = [('ab', '10 training flops', '#4277aa'),
               ('report47', '47 training flops', '#d58a36')]
    for source, _, _ in sources:
        matched = read(OUT/f'sourcepanel-{source}-comparison.json')
        assert matched['preserved_preflop_and_chance'] is True
        for rel, digest in matched['inputs_sha256'].items():
            assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() == digest, rel
        for panel in ['excluded69', 'population164', 'sourcepanel']:
            reviewed = read(OUT/f'{panel}-{source}-result-review.json')
            assert reviewed['preflop_exactly_preserved'] is True and reviewed['iteration'] == 2000
            assert 0 <= reviewed['final']['postflop_gap_total'] < .01
        held = read(OUT/f'held-validation95-{source}-result-review.json')
        assert held['preflop_exactly_preserved'] is True and held['iteration'] == 2000
        assert 0 <= held['final']['postflop_gap_total'] < .01
        population = read(OUT/f'population164-{source}-result-review.json')['final']
        values[source] = [matched['original_full_gap_bb'], matched['rebuilt_full_gap_bb'],
                          held['final']['gap_total'], population['gap_total']]
    assert np.all(np.isfinite(list(values.values()))) and np.all(np.array(list(values.values())) > 0)
    output = OUT/'population-transfer-comparison'
    assert not output.with_suffix('.png').exists() and not output.with_suffix('.json').exists()
    labels = ['Original training\ngame', 'Same training boards\nrebuilt responses',
              'Independent 95\neligible sample', 'Combined 164\npopulation mixture']
    fig, ax = plt.subplots(figsize=(11, 6))
    for i, (source, label, color) in enumerate(sources):
        bars = ax.bar(np.arange(4)+(i-.5)*.32, values[source], .30, color=color, label=label)
        ax.bar_label(bars, labels=[f'{x:.4f}' for x in values[source]], padding=5, fontsize=9)
    ax.set_yscale('log')
    ax.set_ylim(min(min(v) for v in values.values())/2, max(max(v) for v in values.values())*2)
    ax.set_xticks(np.arange(4), labels)
    ax.set_ylabel('Combined deviation gain (bb at the entering decision; logarithmic scale)')
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis='y', alpha=.2)
    ax.legend(loc='upper left', framealpha=.95)
    fig.suptitle('Training accuracy and transfer to broader flop coverage', fontsize=16, y=.97)
    fig.text(.03, .09, 'Lower means less profitable deviation within the evaluated game. Each source has its own opponent policy.', fontsize=9)
    fig.text(.03, .055, 'Training panels differ by source. Combined 164 includes training boards; neither sampled panel is exact full-deck evaluation.', fontsize=9)
    fig.text(.03, .02, 'These are conditional branch diagnostics, not head-to-head win rates. All rebuilt postflop residuals are below 0.01 bb.', fontsize=9)
    fig.tight_layout(rect=(0, .13, 1, .94))
    fig.savefig(output.with_suffix('.png'), dpi=160)
    plt.close(fig)
    inputs[str(Path(__file__).relative_to(ROOT))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output.with_suffix('.json').write_text(json.dumps(dict(inputs_sha256=inputs, labels=labels,
                                                         gap_values_bb=values), indent=2, allow_nan=False)+'\n')
    print('Rendered complete population and reconstruction comparison.')


if __name__ == '__main__':
    main()
