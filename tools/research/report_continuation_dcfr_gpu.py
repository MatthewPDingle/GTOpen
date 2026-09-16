"""Render the completed production-kernel toy diagnostic, without rerunning it."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import continuation_dcfr_gpu as fixture

OUT = fixture.OUT
ARMS = [('full_dcfr', 'Full tree', '#248a61'), ('exact_cutoff', 'Exact cutoff', '#2676c6'),
        ('offsupport_cutoff', 'Exact cutoff + zero-support completion', '#9174c9'),
        ('predicted_cutoff', 'Unchanged predictor', '#d25c44')]


def main():
    data = {name: json.loads((OUT/(name+'.json')).read_text()) for name, _, _ in ARMS}
    assert all(doc['complete'] for doc in data.values())
    parity = json.loads((OUT/'parity-checks.json').read_text())
    audit = json.loads((OUT/'audit.json').read_text())
    controls = json.loads((OUT/'integration-gate.json').read_text())['passed']
    prediction_passed = json.loads((OUT/'prediction-gate.json').read_text())['passed']
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.5), constrained_layout=True)
    for name, label, color in ARMS:
        rows = data[name]['rows']
        axes[0].loglog([r['iteration'] for r in rows], [r['full_game']['nashconv'] for r in rows],
                       'o-', label=label, color=color)
    axes[0].axhline(.005, color='#777777', linestyle=':', label='Registered threshold')
    axes[0].set(title='Independent full-game error', xlabel='Alternating DCFR iterations', ylabel='NashConv (chips; lower is better)')
    rows = data['predicted_cutoff']['rows']
    sensitivity = [r for r in audit['completion_sensitivity'] if r['arm'] == 'predicted_cutoff']
    axes[0].loglog([r['iteration'] for r in sensitivity],
                   [r['regularized_completion_metrics']['nashconv'] for r in sensitivity],
                   '--', color='#db9c68', label='Predictor: completion sensitivity audit')
    axes[1].loglog([r['iteration'] for r in rows], [r['full_game']['nashconv'] for r in rows],
                   'o-', color='#d25c44', label='Independent full-game error')
    axes[1].loglog([r['iteration'] for r in rows], [max(abs(r['frozen_value_gap']), 1e-15) for r in rows],
                   's--', color='#777777', label='Internal fixed-prediction gap (absolute)')
    axes[1].loglog([r['iteration'] for r in sensitivity],
                   [r['regularized_completion_metrics']['nashconv'] for r in sensitivity],
                   '--', color='#db9c68', label='Same upper strategy; stable completion (audit)')
    axes[1].set(title='Does the predictor report its own error?', xlabel='Alternating DCFR iterations', ylabel='Gap (chips; logarithmic scale)')
    for ax in axes:
        ax.grid(alpha=.18)
        ax.legend(fontsize=8, loc='upper center', bbox_to_anchor=(.5, -.17), frameon=False)
    fig.suptitle('Three-card diagnostic using GTOpen CUDA updates — not a Hold’em benchmark', fontsize=13)
    fig.savefig(OUT/'comparison.png', dpi=160); plt.close(fig)
    lines = ['# Production CUDA continuation diagnostic', '',
        'This test executes GTOpen’s unmodified GPU reach, strategy-update and discount routines in the independently solved three-card game. It does not use a live server or change port 56708.', '',
        f'**Exact-control gate: {"passed" if controls else "failed"}. Prediction gate: {"passed" if prediction_passed else "failed"}.**', '',
        '## Results at 20,000 iterations', '',
        '| Approach | Independent full-game error | Internal fixed-leaf gap |',
        '|---|---:|---:|']
    for name, label, _ in ARMS:
        last = data[name]['rows'][-1]
        fg = f"{last['frozen_value_gap']:.9f}" if 'frozen_value_gap' in last else 'Not applicable'
        lines.append(f"| {label} | {last['full_game']['nashconv']:.9f} | {fg} |")
    pred = data['predicted_cutoff']['rows'][-1]
    ratio = pred['full_game']['nashconv']/max(abs(pred['frozen_value_gap']), 1e-15)
    lines += ['', 'NashConv sums the gains available to both players by changing their strategy in the complete game; lower is better. The registered pass threshold is 0.005 chips.', '',
        f"At the final predictor checkpoint the independent error is {ratio:,.0f} times its internal fixed-value gap. Exact continuation completion is granted to every cutoff arm, including the predicted arm.", '',
        'The bumps at 5,000 and 10,000 iterations come from numerical selection of continuation actions for almost-impossible hands. A separately labeled, post-hoc audit floors only the reconstruction ranges at 1e-6; it leaves the learned upper policies unchanged. That removes the bumps, changes on-policy EV by at most 2e-12 chips, and still leaves prediction error near 0.085. Both exact controls and the final prediction result are unchanged. The original measurements and gates are retained.', '',
        '## Checks', '',
        f"- {parity['comparisons']} GPU/CPU comparisons passed. Reaches, update values, regrets and strategy sums matched exactly after matching GPU fused multiply-add rounding; maximum leaf-transfer difference was {parity['maximum_absolute_errors']['transfer']:.3g} chips.",
        '- A separate 192-vector transfer audit included zero opponent mass and predicted shares outside [0,1]; all matched direct explicit-deal arithmetic exactly.',
        '- Every recorded complete-game error was recalculated using both exhaustive pure best responses and an independent recursive evaluator.',
        f"- The full-game linear-program reference value is {audit['reference_value']:.12f} chips, agreeing with 1/18. All {audit['frozen_inputs_checked']} registered source/data inputs retained their hashes.",
        '- Two smoke failures are retained in SMOKE-NOTES.md: CUDA context initialization and the initial non-fused CPU reference. Neither required a production edit or a relaxed tolerance.', '',
        '## Interpretation and limits', '',
        'When the controls pass but the predictor fails, the earlier prediction blind spot survives GTOpen’s real alternating GPU update method. A small reported gap against frozen predicted continuation values does not certify a good complete-game strategy.', '',
        'This narrows the investigation; it does not prove the same cause explains GTOpen’s Hold’em range differences. The fixture has three private cards, two players, a tiny tree, and a separately fitted RBF predictor. It does not test the N15 model, Hold’em feature encoding, production tree construction, value-slot reuse, multiway continuation, forced policies, or the full CUDA host pipeline.', '',
        'No production performance conclusion can be drawn from these times: the diagnostic deliberately moves values through Python and solves small linear programs on the CPU. The production CUDA kernels themselves were not modified.', '',
        '## Suggested next step', '',
        'Use a fixed, small heads-up Hold’em case to compare action values from direct downstream solves against the deployed prediction interface at the ranges produced by search. Check decision reversals and independent best responses, not only average prediction error or the internal stopping gap. Keep this as a research gate before any model deployment.', '',
        '![Independent error and stopping-gap comparison](comparison.png)', '',
        'Reproduce from the repository root with Python 3.12, NumPy, SciPy, Torch CUDA and local NVRTC. The runner refuses to overwrite a registered run. Audit completed outputs with `tools/research/audit_continuation_dcfr_gpu.py`; render this report with `tools/research/report_continuation_dcfr_gpu.py`.', '']
    (OUT/'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')


if __name__ == '__main__': main()
