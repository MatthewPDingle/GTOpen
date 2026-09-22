"""Registered fixed-data optimizer schedule comparison; no self-play changes."""
import json
import math
import os
from pathlib import Path
import time
import numpy as np
import psutil
from hu_sampled_neural_residual_diagnostic_20260922 import ROOT, OUT, sha, save
from hu_sampled_neural_control_20260922 import geometry
from hu_sampled_neural_fallback_20260922 import highest_regret_fallback
from hu_sampled_neural_table_control_20260922 import sums
from loopback_research_validation import idle

PREFIX = 'sampled-schedule-fit-cpu-v1'


def main():
    assert idle() and psutil.virtual_memory().available >= 20_000_000_000
    parent_reg = OUT / 'sampled-mean-fit-cpu-v1-registration.json'
    parent_result = OUT / 'sampled-mean-fit-cpu-v1-result.json'
    prior = json.loads(parent_reg.read_text())
    completed = json.loads(parent_result.read_text())
    assert completed['terminal'] and completed['registration_sha256'] == sha(parent_reg)
    assert all(c['maximum_gradient_error'] < 1e-10 and c['loss_decomposition_error'] < 1e-10 for c in completed['controls'])
    for name, digest in prior['inputs'].items():
        assert sha(ROOT / name) == digest, name
    paths = [ROOT / name for name in prior['inputs']]
    paths += [Path(__file__), parent_reg, parent_result,
              ROOT / 'tools/research/hu_sampled_neural_residual_diagnostic_20260922.py']
    frozen = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    regpath = OUT / (PREFIX + '-registration.json')
    reg = dict(inputs=frozen, maximum_seconds=300, model_seeds=[991, 20260922],
        steps=[512, 2048], schedules=['constant', 'cosine'], architecture=[28, 64, 64, 3],
        initial_learning_rate=.003, final_cosine_learning_rate=.00001,
        formula='lr(step)=end+(start-end)*(1+cos(pi*step/(steps-1)))/2; before each Adam step',
        objective='Same count-weighted retained-data mean MSE, target scaling, legal masks and fresh initialization as prior exact-mean control.',
        primary='For each budget, cosine must weakly improve both excess mean-fit MSE and visitation-weighted policy L1 in all four player/initialization pairs; otherwise do not promote on this control.',
        scope='Exploratory CPU fixed-data fitting control on an already inspected table-generated reservoir; not self-play, held-out prediction or physical-poker accuracy.',
        stopping='All 16 predeclared fits or production/resource/deadline guard; no outcome-dependent retries.',
        no_gpu=True, production_modified=False)
    save(regpath, reg)
    started = time.monotonic(); last_guard = 0.; results = []
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    import torch
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    def network():
        return torch.nn.Sequential(torch.nn.Linear(28,64), torch.nn.ReLU(),
                                   torch.nn.Linear(64,64), torch.nn.ReLU(), torch.nn.Linear(64,3))
    data = json.loads((OUT / 'sampled-convergence-v1-fixture.json').read_text())
    x, mask, actors = geometry(data); features = torch.from_numpy(x)
    snapshots = sorted(p for p in paths if p.suffix == '.npz')
    assert len(snapshots) == 2
    result_path = OUT / (PREFIX + '-result.json')
    assert not result_path.exists()
    def publish(document):
        temp = OUT / (PREFIX + '-result.tmp')
        with temp.open('x', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(document, indent=2)+'\n')
        temp.replace(result_path)
    for player, snapshot in enumerate(snapshots):
        assert snapshot.name.endswith(f'player{player}.npz')
        with np.load(snapshot, allow_pickle=False) as stored:
            ids = stored['ids']; values = stored['values']
        counts = np.bincount(ids, minlength=len(mask))
        means = sums(ids, values, len(mask))/np.maximum(counts[:,None], 1)
        raw = torch.as_tensor(values, dtype=torch.float32)
        scale = raw.square().mean().sqrt().clamp_min(.01)
        normalized = (raw/scale).numpy().astype(float)
        empirical = sums(ids, normalized, len(mask))/np.maximum(counts[:,None], 1)
        weighted_mask = mask*counts[:,None]; denominator = float(weighted_mask.sum())
        target = torch.as_tensor(empirical, dtype=torch.float32)
        weights = torch.as_tensor(weighted_mask, dtype=torch.float32)
        ideal = highest_regret_fallback(means, mask)
        for initial in reg['model_seeds']:
            for steps in reg['steps']:
                for schedule in reg['schedules']:
                    began = time.monotonic(); torch.manual_seed(initial+player)
                    model = network(); opt = torch.optim.Adam(model.parameters(), lr=.003)
                    for step in range(steps):
                        now = time.monotonic(); assert now-started < reg['maximum_seconds']
                        if now-last_guard >= 2:
                            assert idle() and psutil.virtual_memory().available >= 20_000_000_000
                            last_guard = now
                        lr = .003 if schedule == 'constant' else .00001+(.003-.00001)*(1+math.cos(math.pi*step/(steps-1)))/2
                        for group in opt.param_groups: group['lr'] = lr
                        loss = ((model(features)-target).square()*weights).sum()/denominator
                        opt.zero_grad(set_to_none=True); loss.backward(); opt.step()
                    with torch.no_grad(): prediction = (model(features)*scale).numpy().astype(float)
                    inferred = highest_regret_fallback(prediction, mask)
                    excess = float((((prediction-means)**2)*weighted_mask).sum()/denominator)
                    l1 = np.abs(inferred-ideal).sum(axis=1)
                    row = dict(player=player, initial_seed=initial, steps=steps, schedule=schedule,
                        seconds=time.monotonic()-began, excess_mean_fit_mse=excess,
                        visitation_weighted_policy_l1=float(l1@counts/counts.sum()),
                        rows=[dict(information_id=i, key=data['information_keys'][i], count=int(counts[i]),
                                   target_means=means[i].tolist(), prediction=prediction[i].tolist(),
                                   target_policy=ideal[i].tolist(), predicted_policy=inferred[i].tolist())
                              for i in range(len(mask)) if actors[i]==player and counts[i]>0])
                    if schedule == 'constant':
                        baseline = next(r for r in completed['results'] if r['player']==player and r['initial_seed']==initial and r['steps']==steps)
                        assert abs(excess-baseline['excess_mean_fit_mse']) < 1e-12
                        assert abs(row['visitation_weighted_policy_l1']-baseline['visitation_weighted_policy_l1']) < 1e-12
                    results.append(row)
                    publish(dict(terminal=False, results=results))
                    print(json.dumps({k:v for k,v in row.items() if k!='rows'}), flush=True)
    decisions = []
    for steps in reg['steps']:
        comparisons = []
        for player in (0,1):
            for initial in reg['model_seeds']:
                pair = {r['schedule']:r for r in results if r['player']==player and r['initial_seed']==initial and r['steps']==steps}
                comparisons.append(dict(player=player, initial_seed=initial,
                    mse_not_worse=pair['cosine']['excess_mean_fit_mse'] <= pair['constant']['excess_mean_fit_mse'],
                    policy_l1_not_worse=pair['cosine']['visitation_weighted_policy_l1'] <= pair['constant']['visitation_weighted_policy_l1']))
        decisions.append(dict(steps=steps, qualifies_for_next_control=all(r['mse_not_worse'] and r['policy_l1_not_worse'] for r in comparisons), comparisons=comparisons))
    for name, digest in frozen.items(): assert sha(ROOT/name)==digest, name
    publish(dict(terminal=True, results=results, decisions=decisions, inputs_verified=len(frozen),
                 registration_sha256=sha(regpath), seconds=time.monotonic()-started,
                 device='cpu', torch_version=torch.__version__, strategic_improvement_demonstrated=False,
                 production_modified=False))
    print(json.dumps(decisions), flush=True)


if __name__ == '__main__':
    main()
