"""Bounded external-sampling advantage/average networks; finite control only.

This deliberately uses the separately qualified exact finite evaluator. Nothing
here is a production policy, a physical hold'em model, or a Wizard fit.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from hu_sampled_convergence_fixture_20260922 import evaluate


class Reservoir:
    """Uniform priority reservoir: retain the K smallest independent U(0,1)s.

    One record per actual visit, never one per distinct information set. All
    iterations have equal weight (ordinary CFR), including repeat visits.
    """
    def __init__(self, capacity, seed):
        self.capacity = capacity
        self.rng = np.random.default_rng(seed)
        self.ids = np.empty(0, dtype=np.int64)
        self.values = np.empty((0, 3), dtype=np.float64)
        self.priorities = np.empty(0, dtype=np.float64)
        self.seen = 0

    def add(self, ids, values):
        ids = np.asarray(ids, dtype=np.int64)
        values = np.asarray(values, dtype=np.float64).reshape(-1, 3)
        assert len(ids) == len(values) and np.isfinite(values).all()
        self.seen += len(ids)
        self.ids = np.concatenate((self.ids, ids))
        self.values = np.concatenate((self.values, values))
        self.priorities = np.concatenate((self.priorities, self.rng.random(len(ids))))
        if len(self.ids) > self.capacity:
            keep = np.argpartition(self.priorities, self.capacity-1)[:self.capacity]
            self.ids = self.ids[keep]
            self.values = self.values[keep]
            self.priorities = self.priorities[keep]

    def summary(self):
        return dict(seen=self.seen, retained=len(self.ids),
                    occupied_information_sets=len(np.unique(self.ids)),
                    retained_payload_bytes=self.ids.nbytes+self.values.nbytes+self.priorities.nbytes)


def geometry(data):
    keys = data['information_keys']
    # Public node encodes the complete action history in this finite tree.
    # No information-set lookup embedding or opponent/future-card input.
    x = np.zeros((len(keys), 28), dtype=np.float32)
    mask = np.zeros((len(keys), 3), dtype=bool)
    actors = []
    for i, (node, own_card, board) in enumerate(keys):
        x[i, node] = 1
        x[i, 19+own_card] = 1
        x[i, 23+(board+1)] = 1  # 0 means unobserved, 1..4 public card.
        mask[i, :data['arity'][node]] = True
        actors.append(data['actors'][node])
    return x, mask, np.asarray(actors)


def flat_policy(data, policy):
    return [float(policy[i, a]) for i in range(len(policy))
            for a in range(data['offsets'][i+1]-data['offsets'][i])]


def regret_policy(values, mask):
    p = np.maximum(values, 0)*mask
    total = p.sum(axis=1, keepdims=True)
    return np.divide(p, total, out=mask/mask.sum(axis=1, keepdims=True), where=total>0)


def sample_batch(data, case, policy, deals, uniforms, updater):
    """Vectorized external sampling; deal/action draws supplied for replay.

    Chance and opponent reach are represented by sampling, not multiplied a
    second time. Every updater action is traversed, even at zero own reach.
    """
    arity = data['arity']; actor = data['actors']; child = data['children']
    infos = np.asarray(data['deal_infos'])[deals]
    utilities = np.asarray(data['cases'][case]['utilities'])[deals, :, updater]
    count = len(deals)
    visited = np.zeros((count, 19), dtype=bool); visited[:, 0] = True
    choices = np.zeros((count, 19), dtype=np.int64)
    rows = np.arange(count)
    for n in range(19):
        if not arity[n]:
            continue
        if actor[n] == updater:
            for c in child[n][:arity[n]]:
                visited[:, c] = visited[:, n]
        else:
            cdf = policy[infos[:, n]].cumsum(axis=1)
            chosen = (uniforms[:, n, None] >= cdf).sum(axis=1)
            chosen = np.minimum(chosen, arity[n]-1)
            choices[:, n] = chosen
            for a, c in enumerate(child[n][:arity[n]]):
                visited[:, c] = visited[:, n] & (chosen == a)
    values = utilities.copy(); advantages=[]; averages=[]
    for n in reversed(range(19)):
        if not arity[n]:
            continue
        selected = visited[:, n]
        ids = infos[selected, n]
        if actor[n] == updater:
            action_values = values[:, child[n][:arity[n]]]
            v = (action_values*policy[infos[:, n], :arity[n]]).sum(axis=1)
            values[:, n] = v
            targets = np.zeros((int(selected.sum()), 3))
            targets[:, :arity[n]] = action_values[selected]-v[selected, None]
            advantages.append((ids, targets))
        else:
            values[:, n] = values[rows, np.asarray(child[n])[choices[:, n]]]
            averages.append((ids, policy[ids].copy()))
    join = lambda groups: (np.concatenate([g[0] for g in groups]), np.concatenate([g[1] for g in groups]))
    return join(advantages), join(averages), values[:, 0]


def exact_average_increment(data, policy):
    """Finite-control diagnostic only, not a scalable average-model shortcut."""
    out = np.zeros_like(policy)
    for d, chance in enumerate(data['probabilities']):
        reach = np.zeros((19, 2)); reach[0] = 1
        for n, arity in enumerate(data['arity']):
            if not arity:
                continue
            actor = data['actors'][n]; info = data['deal_infos'][d][n]
            out[info] += chance*reach[n, actor]*policy[info]
            for a, c in enumerate(data['children'][n][:arity]):
                reach[c] = reach[n]
                reach[c, actor] *= policy[info, a]
    return out


def normalize_average(values, mask):
    total = values.sum(axis=1, keepdims=True)
    return np.divide(values, total, out=mask/mask.sum(axis=1, keepdims=True), where=total>0)


def fit(reservoir, features, mask, seed, steps, strategy=False):
    import torch
    torch.manual_seed(seed)
    model = torch.nn.Sequential(torch.nn.Linear(28, 64), torch.nn.ReLU(),
                                torch.nn.Linear(64, 64), torch.nn.ReLU(), torch.nn.Linear(64, 3)).cuda()
    optimizer = torch.optim.Adam(model.parameters(), lr=.003)
    ids = torch.as_tensor(reservoir.ids, device='cuda')
    targets = torch.as_tensor(reservoir.values, dtype=torch.float32, device='cuda')
    scale = torch.tensor(1., device='cuda') if strategy else targets.square().mean().sqrt().clamp_min(.01)
    targets = targets/scale
    rng = torch.Generator(device='cuda').manual_seed(seed+1000003)
    for _ in range(steps):
        selected = torch.randint(len(ids), (512,), generator=rng, device='cuda')
        information = ids[selected]; legal = mask[information]
        pred = model(features[information])
        if strategy:
            pred = pred.masked_fill(~legal, -1e9).softmax(dim=1)
        loss = ((pred-targets[selected]).square()*legal).sum()/legal.sum()
        optimizer.zero_grad(set_to_none=True); loss.backward(); optimizer.step()
    with torch.no_grad():
        prediction = model(features)
        if strategy:
            prediction = prediction.masked_fill(~mask, -1e9).softmax(dim=1)
        else:
            prediction = prediction*scale
        residual = ((prediction[ids]-targets*scale).square()*mask[ids]).sum()/mask[ids].sum()
    result = prediction.cpu().numpy().astype(np.float64)
    return result, {'reservoir_mse':float(residual.cpu()), 'target_scale':float(scale.cpu()),
                    'parameters':sum(p.numel() for p in model.parameters())}


def run(data, case, seed, config, result_path):
    import torch
    start = time.monotonic()
    x, mask, actors = geometry(data)
    features = torch.as_tensor(x, device='cuda'); legal = torch.as_tensor(mask, device='cuda')
    policy = mask/mask.sum(axis=1, keepdims=True)
    exact_average = np.zeros_like(policy)
    sampled_average = np.zeros_like(policy)
    advantages = [Reservoir(config['reservoir_capacity'], seed+100*p) for p in range(2)]
    averages = [Reservoir(config['reservoir_capacity'], seed+100*p+10000) for p in range(2)]
    rng = np.random.default_rng(seed+20000)
    checkpoints=[]; streak=0
    for iteration in range(1, config['max_iterations']+1):
        exact_average += exact_average_increment(data, policy)
        # Both players see the same frozen policy; train only after both passes.
        for updater in range(2):
            deals = rng.choice(24, size=config['traversals_per_player'], p=data['probabilities'])
            uniforms = rng.random((len(deals), 19))
            adv, avg, _ = sample_batch(data, case, policy, deals, uniforms, updater)
            advantages[updater].add(*adv)
            averages[1-updater].add(*avg)
            np.add.at(sampled_average, avg[0], avg[1])
        fits=[]
        for player in range(2):
            prediction, metrics = fit(advantages[player], features, legal,
                seed+iteration*200003+player, config['advantage_train_steps'])
            new = regret_policy(prediction, mask)
            policy[actors==player] = new[actors==player]
            fits.append(metrics)
        assert np.isfinite(policy).all() and (policy>=0).all()
        assert np.max(np.abs(policy.sum(axis=1)-1))<1e-7 and not np.any(policy[~mask])
        if iteration in config['checkpoints']:
            learned = np.zeros_like(policy); average_fits=[]
            for player in range(2):
                prediction, metrics = fit(averages[player], features, legal,
                    seed+iteration*300007+player, config['strategy_train_steps'], strategy=True)
                prediction *= mask
                prediction /= prediction.sum(axis=1, keepdims=True)
                learned[actors==player] = prediction[actors==player]
                average_fits.append(metrics)
            policies={'learned_average':learned,
                      'exact_reach_average_diagnostic':normalize_average(exact_average, mask),
                      'sampled_visit_average_diagnostic':normalize_average(sampled_average, mask)}
            evaluations={name:dict(evaluate(data, flat_policy(data, p), case), policy=flat_policy(data, p))
                         for name,p in policies.items()}
            gap=evaluations['learned_average']['gap']
            streak=streak+1 if gap<=config['target_gap'] else 0
            checkpoint=dict(iteration=iteration, seconds=time.monotonic()-start,
                evaluations=evaluations, advantage_fit=fits, strategy_fit=average_fits,
                advantage_reservoirs=[r.summary() for r in advantages],
                strategy_reservoirs=[r.summary() for r in averages], target_streak=streak)
            checkpoints.append(checkpoint)
            partial=dict(case=case, seed=seed, checkpoints=checkpoints,
                target_reached_twice=streak>=2, terminal=False)
            result_path.write_text(json.dumps(partial,indent=2)+'\n',encoding='utf-8',newline='\n')
            print(json.dumps(dict(case=case,seed=seed,iteration=iteration,
                gaps={k:v['gap'] for k,v in evaluations.items()},seconds=checkpoint['seconds'])),flush=True)
            if streak>=2:
                break
    partial['terminal']=True
    partial['seconds']=time.monotonic()-start
    result_path.write_text(json.dumps(partial,indent=2)+'\n',encoding='utf-8',newline='\n')
    return partial


def main():
    parser=argparse.ArgumentParser();parser.add_argument('registration');args=parser.parse_args()
    reg=json.loads(Path(args.registration).read_text())
    import torch
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False
    environment=dict(torch_version=torch.__version__, cuda_version=torch.version.cuda,
                     gpu=torch.cuda.get_device_name(0), deterministic_algorithms=True,
                     tf32=False, cpu_threads=torch.get_num_threads())
    Path(reg['output_prefix']+'-environment.json').write_text(
        json.dumps(environment,indent=2)+'\n',encoding='utf-8',newline='\n')
    data=json.loads(Path(reg['fixture']).read_text())
    for case in reg['cases']:
        for seed in reg['seeds']:
            run(data,case,seed,reg['config'],Path(reg['output_prefix']+f'-case{case}-seed{seed}.json'))


if __name__=='__main__':main()
