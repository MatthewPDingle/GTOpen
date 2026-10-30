"""Development and synthetic controls for descriptive board residual reports."""
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
import continuation_transfer_aggregate as transfer
import transfer_board_diagnostics as diagnostic

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def main():
    paths = [ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json',
             ROOT/'research/preflop-evolution/integrated-coverage-20260919/old-two-orbits-result.json',
             OUT/'transfer-v3-streamed-two-0-result.json', OUT/'transfer-v3-streamed-two-1-result.json']
    tree, source, *workers = map(transfer.read, paths)
    panel = dict(suit_orbits=True, bet_menu='50', boards=[dict(board=w['boards'][0], weight=q) for w,q in zip(workers,[1,3])])
    combined = transfer.aggregate(tree, panel, source, workers)
    actual = diagnostic.summarize(combined, workers)
    assert diagnostic.summarize(combined, workers[::-1]) == actual
    assert abs(sum(r['weighted_residual_contribution_bb'] for r in actual['boards']) - actual['panel_postflop_residual_bb']) < 1e-5

    # A passing weighted panel can contain an unresolved low-probability board.
    toy_workers = [dict(boards=[name], root_normalizer=1., records=[dict(iteration=2000,
                    evaluation=dict(independent_postflop_gaps=[g/2,g/2], postflop_gap_total=g))])
                   for name,g in [('rare',1.),('common',0.)]]
    toy_combined = dict(boards=['rare','common'], board_weights=[.001,.999], root_normalizer=1.,
                       records=[dict(evaluation=dict(postflop_gaps=[.0005,.0005], postflop_gap_total=.001))])
    rare = diagnostic.summarize(toy_combined, toy_workers)
    assert rare['panel_postflop_residual_bb'] < .01
    assert rare['largest_local_residual_bb'] == 1.
    assert rare['local_boards_above_001_bb'] == 1 and rare['private_mass_above_001_bb'] == .001
    rejected = []
    for label, value in [('nan',float('nan')), ('negative',-.1)]:
        bad = copy.deepcopy(toy_workers)
        bad[0]['records'][-1]['evaluation']['independent_postflop_gaps'][0] = value
        try:
            diagnostic.summarize(toy_combined, bad)
        except AssertionError:
            rejected.append(label)
        else:
            raise AssertionError('Invalid residual accepted: '+label)
    inputs = [Path(__file__), Path(diagnostic.__file__), Path(transfer.__file__), *paths]
    result = dict(passed=True, development=actual, rare_board_control=rare, rejected=rejected,
                  worker_order_invariant=True, reserved_outcomes_accessed=False,
                  inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    output = OUT/'board-residual-controls.json'
    assert not output.exists()
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(passed=True, panel=actual['panel_postflop_residual_bb'],
                         max_board=actual['largest_local_residual_bb'], synthetic_rare_board_detected=True)))


if __name__ == '__main__':
    main()
