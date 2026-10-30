"""CPU-only checks of root-only decision diagnostics; no new poker solves."""
import hashlib
import json
from pathlib import Path
import numpy as np
import transfer_decision_diagnostics as diagnostics
import continuation_transfer_aggregate as transfer

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
DEV = ROOT/'research/preflop-evolution/integrated-coverage-20260919'


def main():
    tree_path = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
    tree = transfer.read(tree_path)
    source_path = OUT/'transfer-control-fold.json'
    policy = transfer.read(source_path)['records'][-1]['evaluation']['preflop_policy']
    policy[6] = np.tile([[.25], [.75]], (1, 1326)).tolist()
    values = np.zeros((len(tree['nodes']), 1326))
    for i, value in {1: 1, 2: 2, 4: .5, 5: .7, 7: 2, 8: 4, 10: 1, 11: 3}.items():
        values[i] = value
    q = diagnostics.root_values(tree['nodes'], policy, values)
    assert np.max(abs(q - np.tile([[1], [2], [4.7], [4]], (1, 1326)))) < 1e-12
    # Choosing the better continuation at node 6 would yield 5.2, not 4.7.
    # This checks that only the root decision can change.
    inverse = -values
    hidden = diagnostics.root_values(tree['nodes'], policy, (values + inverse)/2)
    assert np.max(abs(hidden)) == 0
    paths = [Path(__file__), Path(diagnostics.__file__), Path(transfer.__file__), tree_path]
    physical = []
    for kind in ['fold', 'call', 'fourbet', 'jam']:
        source_path = OUT/f'transfer-control-{kind}.json'
        panel_path = DEV/'orbit-river.json'
        worker_path = OUT/f'transfer-v3-streamed-{kind}-result.json'
        result = diagnostics.diagnose(tree, transfer.read(panel_path), transfer.read(source_path),
                                      [transfer.read(worker_path)])
        physical.append(dict(control=kind, root_only_gain_bb=result['root_only_gain_bb'],
                             full_oop_deviation_bb=result['full_oop_deviation_bb'],
                             supported_hand_classes=len(result['hands']), accounting=result['accounting']))
        paths.extend([source_path, panel_path, worker_path])
    output = OUT/'transfer-decision-controls.json'
    assert not output.exists()
    result = dict(passed=True, synthetic_root_values=[1, 2, 4.7, 4],
                  synthetic_hidden_chance_values=[0, 0, 0, 0], physical_controls=physical,
                  inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                  note='Diagnostic verification only. Existing deterministic river controls and artificial utilities; no reserved strategy outcomes accessed.')
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
