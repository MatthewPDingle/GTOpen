"""CPU control: compact tree values vs forward pair cashflows, saved network."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from board_fixed_policy_values_v1 import evaluate
from sampled_visible_features_bulk_v1 import features
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'board-fixed-policy-control-v1'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def save(p, value):
    with Path(p).open('x') as f: json.dump(value, f, separators=(',', ':'), allow_nan=False)


def policy_rows(tree, model, mode):
    result = []
    for branch in tree['branches']:
        obs = []; spans = []
        for i, node in enumerate(branch['nodes']):
            if node['kind'] == 0:
                spans.append((i, len(obs), len(node['observations'])))
                obs.extend(node['observations'])
        if mode == 'saved-network':
            x = features(obs).astype(np.float64); actors = np.array([o['actor'] for o in obs])
            scores = np.zeros((len(obs), 4))
            for player, net in enumerate(model['networks']):
                ids = np.flatnonzero(actors == player); y = x[ids]
                for layer, shape in enumerate(((64,302), (64,64), (4,64))):
                    w = np.asarray(net[f'w{layer}'], dtype=np.float32).astype(float).reshape(shape)
                    b = np.asarray(net[f'b{layer}'], dtype=np.float32).astype(float)
                    y = y @ w.T + b
                    if layer < 2: y = np.maximum(y, 0.)
                scores[ids] = y
            arity = np.array([o['n'] for o in obs]); legal = np.arange(4)[None, :] < arity[:, None]
            p = np.maximum(scores, 0.) * legal; z = p.sum(1); live = z > 0
            p[live] /= z[live, None]
            zero = np.flatnonzero(~live)
            p[zero, np.argmax(np.where(legal, scores, -np.inf), axis=1)[zero]] = 1.
        else:
            p = np.zeros((len(obs), 4))
            for i, o in enumerate(obs): p[i, :o['n']] = 1. / o['n']
        result.append({i: p[start:start+count, :len(branch['nodes'][i]['children'])]
                       for i, start, count in spans})
    return result


def forward(tree, branch, policies, weights, context):
    # Explicit joint hand-pair path mass and terminal investment accounting.
    # Does not use candidate recursion, terminal prefixes, offsets or payouts.
    h0, h1 = [np.asarray(h) for h in tree['hands']]
    compatible = (h0[:,None,0] != h1[None,:,0]) & (h0[:,None,0] != h1[None,:,1])
    compatible &= (h0[:,None,1] != h1[None,:,0]) & (h0[:,None,1] != h1[None,:,1])
    ranks = [np.asarray(r) for r in tree['ranks']]
    share = ((ranks[0][:,None] > ranks[1][None,:]).astype(float) +
             .5 * (ranks[0][:,None] == ranks[1][None,:]))
    pair_values = np.zeros((2, *compatible.shape)); terminal_mass = np.zeros(compatible.shape)
    rake_values = np.zeros(compatible.shape); stack = [(0, compatible.astype(float))]
    while stack:
        i, reach = stack.pop(); node = branch['nodes'][i]
        if node['kind'] == 0:
            p = policies[i]
            for a, child in enumerate(node['children']):
                stack.append((child, reach * (p[:,a,None] if node['actor'] == 0 else p[None,:,a])))
        elif node['kind'] == 1: stack.append((node['children'][0], reach))
        else:
            invested = np.array(context['nodes'][branch['branch']]['invested'])
            invested = invested + np.array(node['put']) - branch['starting_pot'] / 2
            matched = min(invested); pot = 2 * matched + context['dead_money']
            rake = pot * context['rake_fraction']
            if context['rake_cap'] > 0: rake = min(rake, context['rake_cap'])
            s = share if node['kind'] == 3 else float(node['actor'] == 1)
            pair_values[0] += reach * (-matched + s * (pot - rake))
            pair_values[1] += reach * (-matched + (1 - s) * (pot - rake))
            terminal_mass += reach; rake_values += reach * rake
    mass_error = float(np.max(abs(terminal_mass - compatible)))
    conservation = float(np.max(abs(pair_values.sum(0) + rake_values - compatible * context['dead_money'])))
    assert mass_error < 1e-12 and conservation < 1e-10
    return [pair_values[0] @ weights[1], pair_values[1].T @ weights[0]], mass_error, conservation


def main():
    began = time.monotonic(); context_path = OUT / 'bb-context-candidate.json'; context = read(context_path)
    audit_path = OUT / 'weighted-training-readback-parallel-v1-w4-9266201-stratified-0078-result.json'
    audit_reg_path = OUT / 'weighted-training-readback-parallel-v1-w4-9266201-stratified-0078-registration.json'
    audit = read(audit_path); reg = read(audit_reg_path)
    assert audit['passed'] and audit['readback_registration_sha256'] == sha(audit_reg_path)
    metric_path = Path(reg['folders'][-1]) / 'metrics.json'
    assert sha(metric_path) == reg['inputs'][str(metric_path)]
    ref = read(metric_path)['used_model']; assert ref['generation'] == 77
    training_reg = read(OUT / 'weighted-stratified-study-v1-registration.json')
    model_path = Path(training_reg['store']) / '9266201-stratified/objects' / ref['file']
    assert sha(model_path) == ref['sha256']; model = read(model_path)
    sampler = PhysicalDeals(context_path.read_text(), mode='full_deck', seed=0)
    # Same own holdings on two boards with identical flop and different future
    # cards: all flop observations must be byte-identical.
    boards = [[0,5,10,15,20], [0,5,10,19,24]]
    legal = ~np.isin(PAIRS, np.unique(boards)).any(1)
    rng = np.random.default_rng(9279501)
    ids = [rng.choice(np.flatnonzero(legal & (sampler.weights[p] > 0)), n, replace=False)
           for p, n in enumerate((128, 96))]
    hands = [PAIRS[x].tolist() for x in ids]; weights = [sampler.weights[p,x] for p,x in enumerate(ids)]
    folder = OUT / PREFIX; folder.mkdir(exist_ok=False)
    exe = ROOT / 'target/release/examples/hu_fixed_board_tree_v1.exe'
    paths = [Path(__file__), exe, context_path, model_path, audit_path, audit_reg_path, metric_path,
             ROOT / 'crates/solver/examples/hu_fixed_board_tree_v1.rs',
             ROOT / 'crates/solver/src/evaluator.rs']
    paths += [ROOT / 'crates/solver/examples/research_sampled' / n for n in
              ('state.rs','poker_reference_v1.rs','observation_v1.rs')]
    paths += [ROOT / 'tools/research' / n for n in ('board_fixed_policy_values_v1.py',
              'board_sorted_terminal_v1.py','board_sorted_terminal_v2.py',
              'sampled_visible_features_bulk_v1.py','sampled_visible_poker_features_v1.py',
              'sampled_physical_deals_v1.py','storage_strategic_common_prior_20260920.py')]
    rows = []; trees = []
    for bi, board in enumerate(boards):
        request = folder / f'board-{bi}-request.json'; save(request, dict(board=board, hands=hands)); paths.append(request)
        raw = subprocess.check_output([str(exe), str(context_path), str(request)], creationflags=subprocess.CREATE_NO_WINDOW)
        output = folder / f'board-{bi}-tree.json'; output.write_bytes(raw); paths.append(output)
        tree = json.loads(raw); trees.append(tree)
        for mode in ('uniform','saved-network'):
            policies = policy_rows(tree, model, mode)
            for branch, policy in zip(tree['branches'], policies):
                started = time.monotonic(); compact = evaluate(tree, branch, policy, weights)
                compact_seconds = time.monotonic() - started
                dense, mass_error, conservation = forward(tree, branch, policy, weights, context)
                error = max(float(np.max(abs(a-b))) for a,b in zip(compact,dense))
                assert error < 1e-7
                rows.append(dict(board=board, policy=mode, branch=branch['branch'],
                                 hand_value_max_error=error, terminal_mass_error=mass_error,
                                 cashflow_conservation_error=conservation, compact_seconds=compact_seconds))
            assert time.monotonic() - began < 240
    leakage_checks = 0
    for a,b in zip(trees[0]['branches'], trees[1]['branches']):
        for x,y in zip(a['nodes'], b['nodes']):
            if x['kind'] == 0 and x['street'] == 0:
                assert x['observations'] == y['observations']; leakage_checks += len(x['observations'])
    result = dict(passed=True, rows=rows, future_board_invariance_observations=leakage_checks,
                  own_holdings=[len(x) for x in hands], model_generation=77,
                  inputs={str(p):sha(p) for p in paths}, seconds=time.monotonic()-began,
                  gpu_used=False, production_modified=False, training_changed=False,
                  scope='Fixed-runout postflop branch propagation, two boards and restricted private supports; not preflop chance integration, averaged-bank strength, or a production speedup.')
    save(OUT / f'{PREFIX}-result.json', result)
    print(json.dumps(dict(passed=True, cases=len(rows), max_error=max(x['hand_value_max_error'] for x in rows),
                         leakage_checks=leakage_checks, seconds=result['seconds'])))


if __name__ == '__main__': main()
