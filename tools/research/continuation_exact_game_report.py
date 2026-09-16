"""Generate the miniature-game handoff and scientific plot from completed results."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'research/preflop-evolution/continuation'
OUT = BASE/'exact-game-extension-20260917'


def read(path):
    return json.loads(path.read_text())


def main():
    names = {'full_cfr': 'Full game', 'exact_cutoff': 'Exact continuations',
             'offsupport_cutoff': 'Exact + zero-hand completion',
             'predicted_cutoff': 'Predicted values; exact completion'}
    data = {key: read(OUT/(key+'.json')) for key in names}
    assert all(x['complete'] for x in data.values())
    errors = read(OUT/'prediction-errors.json')
    gate = read(OUT/'prediction-gate.json')
    audit = read(OUT/'audit.json')
    lines = ['# Exact-game diagnostic: results','',
        'This is a deliberately tiny two-round, three-card poker game. It has every legal deal '
        'enumerated and a full-game equilibrium reference. It does not run GTOpen\'s GPU kernel '
        'or establish Hold\'em accuracy. Production on port 56708 was not changed.','',
        '## What the controlled comparison found','',
        'Both versions of the exact continuation interface pass the original 0.005-chip full-game '
        'error threshold with more iterations. The original 5,000-iteration failures remain failures '
        'at that budget. The basic split design can work in this game; the short-run outcome '
        'also depends on the equilibrium selected by the continuation solver.','',
        '| Approach | Full-game NashConv at 5,000 | At 20,000 | Frozen-value gap at 20,000 | Elapsed seconds at 20,000 |',
        '|---|---:|---:|---:|---:|']
    for key, label in names.items():
        rows = data[key]['rows']; first = next(r for r in rows if r['iteration']==5000); last=rows[-1]
        frozen = f"{last['frozen_value_gap']:.6f}" if 'frozen_value_gap' in last else 'n/a'
        lines.append(f"| {label} | {first['full_game']['nashconv']:.6f} | {last['full_game']['nashconv']:.6f} | {frozen} | {last['elapsed_seconds']:.1f} |")
    pred_last=data['predicted_cutoff']['rows'][-1]
    exact_last=data['exact_cutoff']['rows'][-1]
    lines += ['', 'NashConv is the sum of the gains available to both opponents by changing their '
        'entire strategy. Lower is better; the normal-form LP reference is within 1e-8 of zero. '
        'These are chips in this miniature game, not big blinds or the overnight experiment\'s '
        'frozen-value gaps. Timings include checkpoint work and are not repeated production benchmarks.', '',
        '**The clearest finding is false confidence from the stopping measure.** With predicted values, '
        f"the frozen-value gap reaches {pred_last['frozen_value_gap']:.8f}, while true full-game error "
        f"remains {pred_last['full_game']['nashconv']:.6f}. The weakest card bets "
        f"{100*pred_last['root_bet_by_hand'][0]:.1f}% instead of about "
        f"{100*exact_last['root_bet_by_hand'][0]:.1f}% with exact values. More iterations settle "
        'the approximate game without repairing this strategy error. This is a counterexample in '
        'the miniature harness, not proof that the same cause explains the overnight Hold\'em result.', '',
        'The predicted arm supplies only upper-tree hand values. For independent full-game evaluation, '
        'its final upper ranges are completed by fresh exact continuation solves. Therefore it is '
        'an oracle-completed policy, not a complete learned agent.','',
        f"The fixed surrogate's registered practical screen **{'passed' if gate['passed'] else 'failed'}**. "
        f"On 256 independent held-out range contexts, corrected hand-value MAE is "
        f"**{errors['corrected']['mae_chips']:.4f} chips**, 95th-percentile absolute error "
        f"**{errors['corrected']['p95_absolute_error']:.4f}**, and maximum "
        f"**{errors['corrected']['max_absolute_error']:.4f}**. Raw MAE before physical projection "
        f"is {errors['raw']['mae_chips']:.4f}. No model settings were selected using these results.", '',
        '## Why averaging and absent hands need separate treatment','',
        'In the initial LP-backend run, averaging all intermediate exact continuation policies '
        'produced full-game NashConv 0.21334 at 5,000 steps, while completing the averaged upper ranges '
        'with a fresh exact solve gave 0.00387. The robust backend produced a different outcome. '
        'This is evidence that blindly stitching intermediate strategies can be misleading; it '
        'does not show that GTOpen currently makes that particular error. A separate rerun reproduced '
        'both outcomes and verified their full policies by tree and normal-form best responses. '
        '[Averaging audit](averaging-audit.json).', '',
        'The follow-up completed actions only for hands with exactly zero own probability. '
        'Their actions are unconstrained by the continuation equilibrium objective, yet their '
        'values can affect earlier decisions. The change preserved the continuation\'s expected '
        'payoff on its input distribution. Its effect is shown separately; this is not the same '
        'as replacing an entirely empty range with a prior.', '',
        '## What to do next','',
        'Use this miniature game as a permanent correctness fixture. Next match GTOpen\'s alternating '
        'discounted update schedule and actual value-transfer code, then add a richer exact game. '
        'The present independent harness uses simultaneous vanilla CFR. A passing toy test does '
        'not clear the production integration or solve the multiway approximation problem.', '',
        'Before further large training runs, inspect prediction errors at the sparse range contexts '
        'actually reached during search and compare the frozen-value stopping number with true '
        'full-game error. Avoid concluding that lower average prediction error guarantees faster '
        'or more accurate complete-game solving.', '',
        '## Reproducibility and failures','',
        'Default LP precision and then tighter tolerances alone each failed the 1e-8 continuation '
        'duality check before model fitting. Their completed controls and freezes are retained. '
        'An explicit interior-point backend without presolve passed all fixed label checks. '
        'The original 5,000-step experiment, the zero-hand follow-up and the longer extension each '
        'have separate preregistered inputs; none silently replaces a failed run.', '',
        f"The final audit verified {audit['frozen_inputs_checked_including_repeats']} frozen-input entries, "
        f"{len(audit['result_files'])} result files, every stored full-game value and best response "
        'against both normal-form enumeration and a separate tree traversal, repeated upper policies, '
        'no exact training/test overlap, prediction error reproduction and physical projection.', '',
        '[Protocol](PROTOCOL.md) Â· [Audit](audit.json) Â· [Graph](comparison.png)', '']
    (OUT/'RESULTS.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    fig, ax=plt.subplots(figsize=(10,6.5),layout='constrained')
    colors=['#377eb8','#4daf4a','#984ea3','#e07c24']
    for (key,label),color in zip(names.items(),colors):
        rows=data[key]['rows']; xx=[r['iteration'] for r in rows]
        ax.plot(xx,[r['full_game']['nashconv'] for r in rows],'-o',label=label,color=color,markersize=4)
    pred=data['predicted_cutoff']['rows']
    ax.plot([r['iteration'] for r in pred],[max(r['frozen_value_gap'],1e-10) for r in pred],
            '--',label='Prediction: frozen-value gap',color=colors[-1],alpha=.8)
    ax.axhline(.005,ls=':',color='#666666',label='Fixed full-game target: 0.005')
    ax.set(xscale='log',yscale='log',xlabel='Iterations',ylabel='Error (chips; lower is better)',
           title='Small exact game: full-game error versus a frozen-value stopping measure')
    ax.grid(alpha=.2); ax.legend(fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.16),ncol=2,frameon=False)
    fig.suptitle('Independent design diagnostic â€” not a GTOpen GPU performance benchmark',fontsize=10)
    fig.savefig(OUT/'comparison.png',dpi=170)
    plt.close(fig)
    print(OUT/'RESULTS.md')


if __name__=='__main__':
    main()
