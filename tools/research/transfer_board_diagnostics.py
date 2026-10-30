"""Read-only per-board residual audit. Does not change registered panel gates.

SUBTREE MANIFEST SOURCE OUTPUT_PREFIX WORKER... (JSON or gzip workers).
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import continuation_transfer_aggregate as transfer


def summarize(combined, workers):
    by_board = {w['boards'][0]: w for w in workers}
    assert len(by_board) == len(workers) == len(combined['boards'])
    e = combined['records'][-1]['evaluation']
    rows = []
    for board, q in zip(combined['boards'], combined['board_weights']):
        w = by_board[board]
        local = w['records'][-1]['evaluation']
        weight = q * w['root_normalizer'] / combined['root_normalizer']
        residual = np.asarray(local['independent_postflop_gaps'], dtype=float)
        assert np.all(np.isfinite(residual)) and np.all(residual >= -1e-5)
        assert abs(residual.sum() - local['postflop_gap_total']) < 1e-5
        rows.append(dict(board=board, chance_weight=q, private_conditioned_weight=weight,
                         iteration=w['records'][-1]['iteration'],
                         postflop_residual_by_player_bb=residual.tolist(),
                         postflop_residual_bb=float(residual.sum()),
                         weighted_residual_contribution_bb=float(weight * residual.sum())))
    assert abs(sum(r['private_conditioned_weight'] for r in rows) - 1) < 1e-10
    weighted = sum(r['private_conditioned_weight'] * np.asarray(r['postflop_residual_by_player_bb']) for r in rows)
    assert np.max(abs(weighted - e['postflop_gaps'])) < 1e-5
    return dict(panel_postflop_residual_bb=e['postflop_gap_total'],
                reconstructed_by_player_bb=weighted.tolist(),
                largest_local_residual_bb=max(r['postflop_residual_bb'] for r in rows),
                local_boards_above_001_bb=sum(r['postflop_residual_bb'] >= .01 for r in rows),
                private_mass_above_001_bb=sum(r['private_conditioned_weight'] for r in rows if r['postflop_residual_bb'] >= .01),
                boards=sorted(rows, key=lambda r: r['weighted_residual_contribution_bb'], reverse=True),
                interpretation='Descriptive residual concentration, not a new pass/fail rule. The registered 0.01 bb gate applies to the complete weighted panel. A low aggregate does not certify every board or rare hand. Local 0.01 counts use the same numerical reference only for visibility. Weights include legal private-card normalization; simple chance-only averaging is incorrect. No claim about unseen full-deck accuracy or per-hand error bounds follows.')


def main():
    tree_path, panel_path, source_path, prefix, *worker_paths = sys.argv[1:]
    prefix = Path(prefix)
    assert not prefix.with_suffix('.json').exists() and not prefix.with_suffix('.md').exists()
    tree, panel, source = map(transfer.read, [tree_path, panel_path, source_path])
    workers = [transfer.read(p) for p in worker_paths]
    combined = transfer.aggregate(tree, panel, source, workers)
    result = summarize(combined, workers)
    paths = [tree_path, panel_path, source_path, *worker_paths, __file__, transfer.__file__]
    result['inputs_sha256'] = {str(p): hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
    prefix.with_suffix('.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    lines = ['# Residual concentration across boards', '', result['interpretation'], '',
             f'Panel residual: {result["panel_postflop_residual_bb"]:.8f} bb; '
             f'largest local residual: {result["largest_local_residual_bb"]:.8f} bb.', '',
             '| Board | Entering private-card weight | Local residual (bb) | Weighted contribution (bb) |',
             '|---|---:|---:|---:|']
    lines += [f'| {r["board"]} | {100*r["private_conditioned_weight"]:.4f}% | '
              f'{r["postflop_residual_bb"]:.8f} | {r["weighted_residual_contribution_bb"]:.8f} |' for r in result['boards']]
    prefix.with_suffix('.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ['boards', 'inputs_sha256']}))


if __name__ == '__main__':
    main()
