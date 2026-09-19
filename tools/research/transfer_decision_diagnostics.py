"""Read-only root decision values for a completed frozen-policy transfer.

SUBTREE MANIFEST SOURCE OUTPUT_PREFIX WORKER... (JSON or gzip workers).
The complete panel is audited first. Future own actions stay fixed here:
this measures changing only the entering decision, not a full best response.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import continuation_transfer_aggregate as transfer
import integrated_coverage as coverage


def root_values(nodes, policy, leaves):
    """Action-major root CFVs, after hidden chance has been averaged."""
    assert nodes[0]['kind'] == 0 and nodes[0]['actor'] == 0

    def walk(index):
        node = nodes[index]
        if node['kind'] != 0:
            return leaves[index]
        children = np.array([walk(c) for c in node['children']])
        if node['actor'] != 0:
            return children.sum(0)  # opponent actions are already in leaf reach
        return (children * np.asarray(policy[index])).sum(0)

    return np.array([walk(c) for c in nodes[0]['children']])


def diagnose(tree, manifest, source, workers):
    combined = transfer.aggregate(tree, manifest, source, workers)
    evaluation = combined['records'][-1]['evaluation']
    policy = evaluation['preflop_policy']
    chance = np.array(combined['board_weights'])
    by_board = {w['boards'][0]: w for w in workers}
    leaves = np.zeros((len(tree['nodes']), 1326))
    mass = np.zeros(1326)
    for board, weight in zip(combined['boards'], chance):
        terminal = by_board[board]['terminal_values']
        mass += weight * np.asarray(terminal['root_opponent_mass'])
        for i, node in enumerate(tree['nodes']):
            if node['kind'] != 0:
                leaves[i] += weight * np.asarray(terminal['values'][0][i])
    q = root_values(tree['nodes'], policy, leaves)
    sigma = np.asarray(policy[0])
    own = np.asarray(tree['incoming_class_mass'][0])[coverage.CLASSES] / coverage.COUNTS[coverage.CLASSES]
    own /= own.max()
    own[own < 1e-5] = 0
    z = combined['root_normalizer']
    prior = own * mass / z
    actual = (q * sigma).sum(0)
    best = q.max(0)
    gain = float((best - actual) @ own / z)
    assert abs(actual @ own / z - evaluation['ev'][0]) < 1e-8
    assert gain >= -1e-5 and gain <= evaluation['gaps'][0] + 1e-5
    assert abs(prior.sum() - 1) < 1e-10
    rows = []
    for cls in range(169):
        mask = coverage.CLASSES == cls
        denominator = float(mass[mask] @ own[mask])
        if denominator <= 0:
            continue
        action_ev = q[:, mask] @ own[mask] / denominator
        current_ev = float(actual[mask] @ own[mask] / denominator)
        class_gain = float((best[mask] - actual[mask]) @ own[mask] / denominator)
        frequency = sigma[:, mask] @ prior[mask] / prior[mask].sum()
        # These are class-average action values. Best-over-combos is retained
        # separately, so suit-dependent choices are not erased by averaging.
        order = np.sort(action_ev)
        rows.append(dict(hand=evaluation['hands'][cls]['hand'], prior=float(prior[mask].sum()),
                         action_ev=action_ev.tolist(), frequency=frequency.tolist(),
                         current_ev=current_ev, call_minus_fold=float(action_ev[1]-action_ev[0]),
                         top_two_class_margin=float(order[-1]-order[-2]),
                         root_only_gain=class_gain,
                         gain_contribution=float((best[mask]-actual[mask]) @ own[mask] / z)))
    assert abs(sum(r['gain_contribution'] for r in rows) - gain) < 1e-9
    return dict(iteration=combined['records'][-1]['iteration'],
                actions=['Fold', 'Call', '4-bet', 'Jam'], root_only_gain_bb=gain,
                full_oop_deviation_bb=evaluation['gaps'][0],
                postflop_residual_bb=evaluation['postflop_gap_total'],
                accounting=combined['independent_accounting'], hands=rows,
                interpretation='Values condition on this sampled panel and frozen opponent. Only the root action changes; later own actions stay fixed. Hidden chance is averaged before maximizing. Class-average action margins are descriptive, not confidence intervals. Off-path continuations may be poorly determined. These are not full-deck values or proof that one source is a stronger player.')


def main():
    tree_path, panel_path, source_path, prefix, *worker_paths = sys.argv[1:]
    prefix = Path(prefix)
    assert not prefix.with_suffix('.json').exists() and not prefix.with_suffix('.md').exists()
    result = diagnose(*[transfer.read(p) for p in [tree_path, panel_path, source_path]],
                      [transfer.read(p) for p in worker_paths])
    paths = [tree_path, panel_path, source_path, *worker_paths, __file__, transfer.__file__]
    result['inputs_sha256'] = {str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
    prefix.with_suffix('.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    lines = ['# Entering decision diagnostics', '', result['interpretation'], '',
             f'Changing only the entering decision gains **{result["root_only_gain_bb"]:.6f} bb**.',
             f'Full OOP deviation: {result["full_oop_deviation_bb"]:.6f} bb; '
             f'postflop numerical residual: {result["postflop_residual_bb"]:.6f} bb.', '',
             'All values below are bb per occurrence of the hand in the evaluated entering distribution. '
             'The contribution column weights the decision gain by how often that hand arrives.', '',
             '| Hand | Entering share | Call frequency | Call minus fold | Top-two action margin | Root-only gain | Weighted contribution |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for row in sorted(result['hands'], key=lambda r: r['gain_contribution'], reverse=True):
        lines.append(f'| {row["hand"]} | {row["prior"]*100:.2f}% | {row["frequency"][1]*100:.2f}% | '
                     f'{row["call_minus_fold"]:.5f} | {row["top_two_class_margin"]:.5f} | '
                     f'{row["root_only_gain"]:.5f} | {row["gain_contribution"]:.6f} |')
    prefix.with_suffix('.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['root_only_gain_bb', 'full_oop_deviation_bb', 'postflop_residual_bb']}))


if __name__ == '__main__':
    main()
