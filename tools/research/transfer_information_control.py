"""Synthetic hidden-chance control for the frozen-policy CFV aggregator.

Reuse valid physical-card reaches, but deliberately replace utilities with
a known two-outcome test game. These are NOT additional poker observations.
At preflop, one action wins on outcome A and loses on B; another does the
reverse. A player unable to see the future outcome has zero deviation gain.
Maximizing separately before chance averaging would incorrectly add 1 bb.
"""
import copy
import hashlib
import json
from pathlib import Path
import numpy as np
import continuation_transfer_aggregate as aggregate

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def main():
    subtree_path = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
    source_path = OUT/'transfer-control-fold.json'
    worker_path = OUT/'transfer-v2-streamed-fold-result.json'
    tree, source, original = [aggregate.read(p) for p in [subtree_path, source_path, worker_path]]
    # Two named outcomes share the same physical-card prior. Card order is
    # immaterial to that prior; utility signs distinguish the test outcomes.
    boards = ['KhQd9d2c7s', '9dKhQd2c7s']
    manifest = dict(suit_orbits=True, bet_menu='50', boards=[dict(board=b, weight=1) for b in boards])
    mass = np.array(original['terminal_values']['root_opponent_mass'])
    workers = []
    for board, sign in zip(boards, [1., -1.]):
        worker = copy.deepcopy(original)
        worker['boards'] = [board]
        worker['manifest'] = {**manifest, 'boards': [dict(board=board, weight=1)]}
        # P0's opponent always calls at the two response nodes. Other opponent
        # branches have zero reach. P0's frozen root folds with probability 1.
        for mode in [0, 1]:  # same synthetic continuation for average and BR
            for i, node in enumerate(tree['nodes']):
                if node['kind'] != 0:
                    worker['terminal_values']['values'][mode][i] = [0.]*1326
            for i in [1, 2, 5, 11]:
                utility = -6. + (sign if i == 2 else -sign if i == 11 else 0.)
                worker['terminal_values']['values'][mode][i] = (mass*utility).tolist()
        last = worker['records'][-1]['evaluation']
        last['best_response'][0] = -5.
        last['gaps'][0] = -5.-last['ev'][0]
        last['gap_total'] = sum(last['gaps'])
        workers.append(worker)
    combined = aggregate.aggregate(tree, manifest, source, workers)
    evaluation = combined['records'][-1]['evaluation']
    correct = evaluation['gaps'][0]
    # In each observed outcome, the artificially favored preflop action gains
    # exactly 1 bb. This is the known WRONG answer for a hidden future outcome.
    clairvoyant = np.mean([w['records'][-1]['evaluation']['gaps'][0] for w in workers])
    assert abs(correct) < 1e-7, correct
    assert abs(clairvoyant-1.) < 1e-7, clairvoyant
    assert abs(evaluation['postflop_gap_total']) < 1e-7
    output = OUT/'transfer-information-control.json'
    assert not output.exists()
    result = dict(passed=True, hidden_chance_deviation_bb=correct,
                  deliberately_invalid_clairvoyant_deviation_bb=float(clairvoyant),
                  accounting=combined['independent_accounting'],
                  inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in [Path(__file__), Path(aggregate.__file__), subtree_path, source_path, worker_path]},
                  note='Synthetic utilities, not a poker strategy result. Tests that leaf aggregation precedes preflop maximization.')
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
