"""Compare two completed root policies under one exact full-deck entry prior.

SOURCE_A SOURCE_B OUTPUT_PREFIX LABEL_A LABEL_B. Never claims the source
finite games are full-deck equilibria; only the comparison prior is exact.
"""
import json
import hashlib
from pathlib import Path
import sys
import numpy as np
import integrated_coverage as coverage
import integrated_coverage_review as review


def compare(a, b):
    assert a['suit_orbits'] is True and b['suit_orbits'] is True
    assert a['entry_cutoff'] == b['entry_cutoff'] == 1e-5
    assert a['manifest']['bet_menu'] == b['manifest']['bet_menu']
    assert a['records'][-1]['iteration'] == b['records'][-1]['iteration'] == 2000
    audits = [review.audit_result(r) for r in [a, b]]
    tree = json.loads((coverage.s.OUT.parent/'conditional-hu-20260919/subtree.json').read_text())
    weights = np.array(tree['incoming_class_mass'])[:, coverage.CLASSES]/coverage.COUNTS[coverage.CLASSES]
    weights /= weights.max(1)[:, None]
    weights[weights < 1e-5] = 0
    compatible = (coverage.MASKS[:, None] & coverage.MASKS[None, :]) == 0
    joint = weights[0, :, None]*weights[1, None, :]*compatible
    prior = joint.sum(1)/joint.sum()
    e = [r['records'][-1]['evaluation'] for r in [a, b]]
    sigma = np.array([x['preflop_policy'][0] for x in e])
    tv = abs(sigma[1]-sigma[0]).sum(0)/2
    rows = []
    for cls in range(169):
        mask = coverage.CLASSES == cls
        mass = prior[mask].sum()
        action = sigma[:, :, mask] @ prior[mask]/mass if mass else np.zeros((2, 4))
        rows.append(dict(hand=e[0]['hands'][cls]['hand'], prior=float(mass),
                         source_a=action[0].tolist(), source_b=action[1].tolist(),
                         policy_tv=float(tv[mask] @ prior[mask]/mass) if mass else 0.,
                         weighted_tv=float(tv[mask] @ prior[mask])))
    return dict(common_prior='Exact compatible two-player entry prior over the full deck; same 1e-5 support cutoff. Earlier folds omitted.',
                prior_weighted_policy_tv=float(tv @ prior),
                standardized_frequencies=[(s @ prior).tolist() for s in sigma],
                native_frequencies=[x['root_frequencies'] for x in e],
                source_gaps=[x['gap_total'] for x in e], hand_comparison=rows, audits=audits,
                note='Policy sensitivity, not error against poker ground truth. The source strategies still come from different finite flop games.')


def main():
    path_a, path_b, output_prefix, label_a, label_b = sys.argv[1:]
    prefix = Path(output_prefix)
    assert not prefix.with_suffix('.json').exists()
    a, b = [json.loads(Path(p).read_text()) for p in [path_a, path_b]]
    result = compare(a, b)
    result['sources'] = [dict(label=label, path=path, sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())
                         for label, path in [(label_a, path_a), (label_b, path_b)]]
    prefix.with_suffix('.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), gridspec_kw=dict(width_ratios=[1, 2]))
    bottom = np.zeros(2)
    for i, (label, color) in enumerate(zip(['Fold', 'Call', '4-bet', 'Jam'], ['#597ab9', '#75a66a', '#d04f54', '#824c9e'])):
        vals = np.array(result['standardized_frequencies'])[:, i]*100
        axes[0].bar([0, 1], vals, bottom=bottom, label=label, color=color)
        bottom += vals
    axes[0].set(xticks=[0, 1], xticklabels=[label_a, label_b], ylim=(0, 100), ylabel='Action frequency (%)', title='One common entering prior')
    axes[0].legend(fontsize=8)
    rows = sorted(result['hand_comparison'], key=lambda r:r['weighted_tv'], reverse=True)[:12][::-1]
    axes[1].barh([r['hand'] for r in rows], [r['weighted_tv']*100 for r in rows], color='#4f9877')
    axes[1].set(xlabel='Contribution to total policy variation (percentage points)', title='Largest contributions by hand')
    axes[1].grid(axis='x', alpha=.2)
    fig.text(.08, .015, 'Different finite board games. Differences do not identify which policy is more accurate.', fontsize=9)
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(prefix.with_suffix('.png'), dpi=160);plt.close(fig)
    lines = ['# Root policy comparison', '',
             f'{label_a} versus {label_b}, using the same entering private-card distribution.', '',
             f'Total prior-weighted policy variation: **{result["prior_weighted_policy_tv"]*100:.2f}%**. '
             'This measures redistributed action probability, not the percentage of hands that changed.', '',
             '| Source | Fold | Call | 4-bet | Jam | Training-game gap (bb) |',
             '|---|---:|---:|---:|---:|---:|']
    for label, f, gap in zip([label_a, label_b], result['standardized_frequencies'], result['source_gaps']):
        lines.append(f'| {label} | {f[0]*100:.2f}% | {f[1]*100:.2f}% | {f[2]*100:.2f}% | {f[3]*100:.3f}% | {gap:.6f} |')
    lines += ['', f'![Common-prior comparison]({prefix.name}.png)', '',
              'The source strategies solve different finite flop games. A lower training gap is not proof '
              'of greater poker accuracy. Use the independently reserved transfer results to assess robustness.', '',
              '| Hand | Common prior | Call: first source | Call: second source | Policy variation |',
              '|---|---:|---:|---:|---:|']
    for r in rows[::-1]:
        lines.append(f'| {r["hand"]} | {r["prior"]*100:.2f}% | {r["source_a"][1]*100:.2f}% | '
                     f'{r["source_b"][1]*100:.2f}% | {r["policy_tv"]*100:.2f}% |')
    prefix.with_suffix('.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['prior_weighted_policy_tv','standardized_frequencies','source_gaps']}, indent=2))


if __name__ == '__main__':
    main()
