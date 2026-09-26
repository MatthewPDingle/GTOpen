"""Publish the completed, independently checked fixed-budget study; no new deals."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'later-action-compact-evaluation-study-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    result_path = OUT / f'{PREFIX}-result.json'
    result = json.loads(result_path.read_text())
    review_path = OUT / f'{PREFIX}-independent-review.json'
    review = json.loads(review_path.read_text())
    assert result['passed'] and result['complete'] and result['deals'] == 65536
    assert review['passed'] and review['source_result_sha256'] == digest(result_path)
    assert result['registration_sha256'] == digest(OUT / f'{PREFIX}-registration.json')
    store = Path(result['store'])
    for name, key in [('analysis.json', 'analysis_sha256'), ('root-stability.json', 'root_stability_sha256')]:
        assert digest(store / name) == result[key]
    analysis = json.loads((store / 'analysis.json').read_text())
    roots = json.loads((store / 'root-stability.json').read_text())
    for source, target in [('analysis.json', 'later-action-final-analysis.json'),
                           ('root-stability.json', 'later-action-final-root-stability.json')]:
        (OUT / target).write_bytes((store / source).read_bytes())
    assert len(analysis['contrasts']) == 8 and all(x['lower'] < 0 < x['upper'] for x in analysis['contrasts'])
    columns = ['hand', 'entry_mass'] + [f'{p}_{a}' for p in roots['policy_order'] for a in roots['action_order']]
    columns += [f'{c}_TV' for c in roots['comparisons']]
    ranks = 'AKQJT98765432'
    with (OUT / 'later-action-final-root-ranges.csv').open('w', newline='') as stream:
        writer = csv.writer(stream); writer.writerow(columns)
        for i in range(169):
            row, col = divmod(i, 13)
            name = ranks[row] + ranks[col] if row == col else ranks[min(row,col)] + ranks[max(row,col)] + ('s' if row < col else 'o')
            writer.writerow([name, roots['entry_masses'][i]] + [v for p in roots['root_probabilities'] for v in p[i]] + [c['class_total_variation'][i] for c in roots['comparisons'].values()])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 5.6), layout='constrained')
    labels = []
    for i, row in enumerate(analysis['contrasts']):
        seed, desc = row['name'].split(':')
        player, opponent = desc.split('-against-')
        labels.append(f"{'Run 1' if seed == 'first' else 'Run 2'}: new {player[3:6].split('-')[0]} vs {opponent}")
        ax.errorbar(row['mean'], i, xerr=[[row['mean']-row['lower']], [row['upper']-row['mean']]], fmt='o', capsize=4, color='#246e9e' if i < 4 else '#c46b26')
    ax.axvline(0, color='#555555', linewidth=1)
    ax.set_yticks(range(8), labels); ax.invert_yaxis()
    ax.set_xlabel('Gain from replacing one player (bb per entry; positive favors new)')
    ax.set_title('Later-action integration: no contrast resolves above or below zero\n65,536 shared deals; simultaneous 95% bounded intervals')
    ax.grid(axis='x', alpha=.2)
    fig.savefig(OUT / 'later-action-final-gains.png', dpi=150)
    plt.close(fig)
    rows = '\n'.join(f"| {x['name']} | {x['mean']:+.4f} | {x['standard_error']:.4f} | [{x['lower']:+.4f}, {x['upper']:+.4f}] |" for x in analysis['contrasts'])
    freq = '\n'.join('| ' + p + ' | ' + ' | '.join(f'{100*v:.2f}%' for v in f) + ' |' for p, f in zip(roots['policy_order'], roots['aggregate_action_frequencies']))
    text = f'''# Later-action training study: completed findings

The fixed-budget experiment does not establish better preflop ranges. Do not promote this candidate. The two training runs still produce very different hand assignments, and all eight preregistered payoff intervals include both gains and losses. This is an inconclusive effectiveness result, not proof of equivalence or proof that action integration cannot help with a different training budget.

## What was compared

The same BB-versus-BTN-open context, 200bb stack, 2bb open, 0.5bb dead money, 5% rake capped at 2bb, and the same restricted action tree. Each candidate matches its baseline's seeds, 78 updates, 512 deals per update, network size, reservoir and fitting budget. Both already integrate BB root actions and retain exact initial all-in targets. The new treatment additionally integrates later postflop actions into training targets. Complete played banks use generations 0–77 with weights 1–78; generation 78 is excluded.

After freezing and auditing all four banks, the registered final evaluation used 65,536 fresh common physical deals and eight crossed profiles. There was one final look, no sample extension and no checkpoint selection. These results concern complete policies against fixed tested opponents, not a best-response bound or a comparison with GTO Wizard.

## Reproducibility of the hand ranges

Incoming-mass-weighted disagreement between training seeds barely changed: **47.03% to 46.48% total variation**, a reduction of **0.55 percentage points**. The most frequent action still differs in **89 of 169 hand classes**, versus 90 for the baseline. This metric measures how much probability must move to reconcile two policies; it is not the percentage of hands played incorrectly. There are only two seeds, so this is descriptive, not a statistical stability guarantee.

| Complete bank | Fold | Call | Raise | Jam |
| --- | ---: | ---: | ---: | ---: |
{freq}

Aggregate frequencies conceal substantial per-hand differences. The treatment changes roughly 40% of root action probability within each matched run, yet leaves almost all the cross-seed disagreement. The first run calls more; the second calls less. The [169-class export](later-action-final-root-ranges.csv) records every root policy, exact incoming mass and per-class comparison; probabilities are stored on a 0–1 scale.

## Effectiveness on fresh deals

Positive means replacing that player with the new policy improved its own payoff against the named fixed opponent. Units are **bb per entry into this particular spot**, not bb/100 dealt hands. The intervals use the registered two-sided bounded empirical Bernstein construction with Bonferroni coverage over all eight contrasts, at one final look. They include the effect of rare large pots and are wider than ordinary normal-approximation intervals. We do not change methods after observing the outcomes.

| Replacement and fixed opponent | Mean gain | Paired standard error | Simultaneous 95% interval |
| --- | ---: | ---: | ---: |
{rows}

![All eight paired gains and simultaneous intervals](later-action-final-gains.png)

All four point estimates are positive in run 1. Three are negative in run 2. All eight intervals include zero. Neither averaging away the contradictory seeds nor selecting the attractive first run would establish the intended improvement. More test deals could narrow evaluation uncertainty, but would not repair these already-frozen, inconsistent ranges.

## Verification and runtime

Both full 78-update training audits passed. The separate CPU evaluation reader then reconstructed the registered deal stream and checked all 2,048 archived batches, 29,771,619 policy observations, policy transport, payoff accounting, root aggregation and paired intervals. Maximum statistical recomputation discrepancy was {review['maximum_statistical_error']:.3g}. This reader does not repeat neural inference or independently solve poker; integrity checks are not accuracy claims.

The evaluation controller took 3h 10m; the independent reader took 23m 39s. The complete supervised evaluation and review took 3h 34m. The final evaluation archive uses 6.50GB. Port 56708 and production code were not modified by this study. These local jobs completed through the conversation's connection interruption.

## What to do next

1. Keep the candidate experimental and retain the complete baseline and candidate evidence. Do not make the displayed ranges look smoother to hide instability.
2. Diagnose the remaining card/runout noise and learning drift using existing training evidence, before another expensive training pair. Use fixed-policy comparisons to separate noisy payoff estimates from changing opponents and network fitting. These are exploratory diagnostics; register any subsequent confirmatory experiment separately.
3. Qualify the already prepared shared-query GPU optimization on previously inspected control deals. Its CPU preparation check passed, but there is no GPU or whole-batch speed claim yet. The September 26 launch refused before registration because production port 56708 was offline; the activity safeguard remains intact.
4. If the next diagnostic supports a change, test a bounded pilot with unchanged baselines and matched budgets before expanding to both full seeds. Broader positions, stack depths, sizes and multiway play remain necessary for the larger preflop goal; this one context does not cover them.

## Evidence identities

- Study registration: `{result['registration_sha256']}`
- Completed result: `{digest(result_path)}`
- Independent review: `{digest(review_path)}`
- Final analysis: `{result['analysis_sha256']}`
- Full root policies and stability: `{result['root_stability_sha256']}`

The source artifacts retain all per-deal summaries and archive identities. This report is generated by `tools/research/later_action_final_findings_20260926.py` from those authenticated, completed outputs.
'''
    (OUT / 'LATER-ACTION-MATCHED-FINAL-FINDINGS.md').write_text(text, encoding='utf-8')
    print('Published completed findings, all 169 hand classes and the eight-contrast graph.')


if __name__ == '__main__':
    main()
