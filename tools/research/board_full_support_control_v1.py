"""Full supported private ranges on one fixed board; CPU-only propagation check."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from board_fixed_policy_control_v1 import ROOT, OUT, read, save, sha, policy_rows, forward
from board_fixed_policy_values_v1 import evaluate
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS

PREFIX = 'board-full-support-control-v1'


def main():
    began = time.monotonic()
    assert psutil.virtual_memory().available > 20 * 2**30
    assert psutil.disk_usage('S:/').free > 40 * 2**30
    prior_path = OUT / 'board-fixed-policy-control-v1-result.json'; prior = read(prior_path)
    assert prior['passed'] and len(prior['rows']) == 12
    for path, digest in prior['inputs'].items(): assert sha(path) == digest, path
    model_paths = [Path(p) for p in prior['inputs'] if '/objects/' in p.replace('\\','/')]
    assert len(model_paths) == 1
    model = read(model_paths[0]); cp = OUT / 'bb-context-candidate.json'; context = read(cp)
    sampler = PhysicalDeals(cp.read_text(), mode='full_deck', seed=0)
    board = [0,5,10,15,20]; legal = ~np.isin(PAIRS, board).any(1)
    ids = [np.flatnonzero(legal & (sampler.weights[p] > 0)) for p in (0,1)]
    hands = [PAIRS[x].tolist() for x in ids]
    weights = [sampler.weights[p,x] for p,x in enumerate(ids)]
    folder = Path('S:/GTOpen-research') / PREFIX; folder.mkdir(exist_ok=False)
    request = folder / 'request.json'; save(request, dict(board=board, hands=hands))
    exe = ROOT / 'target/release/examples/hu_fixed_board_tree_v1.exe'
    tree_path = folder / 'tree.json'; started = time.monotonic()
    with tree_path.open('xb') as f:
        subprocess.run([str(exe), str(cp), str(request)], stdout=f, check=True, timeout=180,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    native_seconds = time.monotonic() - started
    tree = read(tree_path); started = time.monotonic()
    policies = policy_rows(tree, model, 'saved-network')
    policy_seconds = time.monotonic() - started; rows = []
    for branch, policy in zip(tree['branches'], policies):
        started = time.monotonic(); compact = evaluate(tree, branch, policy, weights)
        compact_seconds = time.monotonic() - started
        started = time.monotonic(); dense, mass_error, conservation = forward(tree, branch, policy, weights, context)
        dense_seconds = time.monotonic() - started
        error = max(float(np.max(abs(a-b))) for a,b in zip(compact,dense))
        assert error < 1e-7
        value_path = folder / f"branch-{branch['branch']}-values.json"
        save(value_path, dict(compact=[v.tolist() for v in compact], dense=[v.tolist() for v in dense]))
        rows.append(dict(branch=branch['branch'], max_hand_value_error=error,
                         terminal_mass_error=mass_error, cashflow_conservation_error=conservation,
                         compact_seconds=compact_seconds, dense_forward_seconds=dense_seconds,
                         values=str(value_path), values_sha256=sha(value_path)))
        assert time.monotonic() - began < 240
    inputs = dict(prior['inputs'])
    for path in (prior_path, Path(__file__), request, tree_path): inputs[str(path)] = sha(path)
    result = dict(passed=True, board=board, supported_holdings=[len(h) for h in hands],
                  rows=rows, native_export_seconds=native_seconds, policy_seconds=policy_seconds,
                  seconds=time.monotonic()-began, inputs=inputs, model_generation=77,
                  gpu_used=False, production_modified=False, training_changed=False,
                  scope='Complete supported private ranges on one fixed board, saved postflop network only. No board expectation, preflop action integration, averaged-bank evaluation, or solver speedup claim.')
    save(OUT / f'{PREFIX}-result.json', result)
    print(json.dumps({k:result[k] for k in ('passed','supported_holdings','rows','native_export_seconds','policy_seconds','seconds')}))


if __name__ == '__main__': main()
