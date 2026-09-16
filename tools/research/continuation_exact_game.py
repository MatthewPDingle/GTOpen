"""Independent tiny-game diagnostic; no app endpoints, production code or GPU use."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import itertools
import json
import time
from pathlib import Path

import numpy as np
from scipy.interpolate import RBFInterpolator
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/continuation/exact-game-20260917'
LEGAL = 1 - np.eye(3)
SIGN = np.sign(np.arange(3)[:, None] - np.arange(3)[None, :])
BITS = np.array(list(itertools.product([0., 1.], repeat=3)))
PURE = np.array(list(itertools.product([0., 1.], repeat=9))).reshape(512, 3, 3)
CHECKPOINTS = [100, 500, 2000, 5000]


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n',
                            encoding='utf-8', newline='\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equilibrium(matrix):
    """P0 maximizes, P1 minimizes. Independent primal and dual LPs."""
    n, m = matrix.shape
    a = linprog(np.r_[np.zeros(n), -1.],
                A_ub=np.c_[-matrix.T, np.ones(m)], b_ub=np.zeros(m),
                A_eq=[np.r_[np.ones(n), 0.]], b_eq=[1.],
                bounds=[(0, None)] * n + [(None, None)], method='highs')
    b = linprog(np.r_[np.zeros(m), 1.],
                A_ub=np.c_[matrix, -np.ones(n)], b_ub=np.zeros(n),
                A_eq=[np.r_[np.ones(m), 0.]], b_eq=[1.],
                bounds=[(0, None)] * m + [(None, None)], method='highs')
    assert a.success and b.success, (a.message, b.message)
    x = np.maximum(a.x[:-1], 0); x /= x.sum()
    y = np.maximum(b.x[:-1], 0); y /= y.sum()
    gap = float(np.max(matrix @ y) - np.min(x @ matrix))
    assert gap < 1e-8, gap
    return x, y, float(x @ matrix @ y), gap


def normalize(x):
    return x / x.sum() if x.sum() > 0 else np.ones(3) / 3


def continuation_matrix(c, bet, call):
    return ((1-bet[:, None]) * SIGN * c
            + bet[:, None] * ((1-call[None, :]) * c
                              + call[None, :] * SIGN * (c+2)))


def exact(c, x, y):
    """Return conditional values for both players and equilibrium behaviors."""
    x, y = normalize(x), normalize(y)
    weights = LEGAL * x[:, None] * y[None, :]
    fallback = weights.sum() <= 1e-15
    if fallback:
        x = y = np.ones(3)/3
        weights = LEGAL * x[:, None] * y[None, :]
    weights /= weights.sum()
    payoffs = np.empty((8, 8))
    for i, bet in enumerate(BITS):
        for j, call in enumerate(BITS):
            payoffs[i, j] = np.sum(weights * continuation_matrix(c, bet, call))
    a, b, _, gap = equilibrium(payoffs)
    bet, call = a @ BITS, b @ BITS
    utility = continuation_matrix(c, bet, call)
    mass0, mass1 = LEGAL @ y, LEGAL.T @ x
    v0 = np.divide((utility * LEGAL) @ y, mass0,
                   out=np.zeros(3), where=mass0 > 0)
    v1 = np.divide((-utility * LEGAL).T @ x, mass1,
                   out=np.zeros(3), where=mass1 > 0)
    return np.array([v0, v1]), (bet, call), gap, fallback


def payoff(p, q):
    """Independent complete-game evaluator, supporting batched pure responses.

    p: root bet, post-check bet, post-call bet, each by private card.
    q: root call, post-check call, post-call call, each by private card.
    """
    result = np.zeros(np.broadcast_shapes(p.shape[:-2], q.shape[:-2]))
    for i in range(3):
        for j in range(3):
            if i == j:
                continue
            s = float(np.sign(i-j))
            first = p[..., 0, i]
            reply = q[..., 0, j]
            vcheck = ((1-p[..., 1, i])*s
                      + p[..., 1, i]*((1-q[..., 1, j])+q[..., 1, j]*s*3))
            vcall = ((1-p[..., 2, i])*s*2
                     + p[..., 2, i]*((1-q[..., 2, j])*2+q[..., 2, j]*s*4))
            result += ((1-first)*vcheck + first*((1-reply)+reply*vcall))/6
    return result


def pack(policy):
    return policy[[0, 2, 4], :, 1], policy[[1, 3, 5], :, 1]


def measure(policy):
    p, q = pack(policy)
    ev = float(payoff(p, q))
    br0, br1 = float(np.max(payoff(PURE, q))), float(np.max(-payoff(p, PURE)))
    assert br0-ev > -1e-10 and br1+ev > -1e-10
    return {'ev_p0': ev, 'nashconv': br0+br1,
            'gain_p0': br0-ev, 'gain_p1': br1+ev}


def behavior_from_mixture(a, b):
    out = np.ones((6, 3, 2))*.5
    out[0, :, 1], out[1, :, 1] = a @ PURE[:, 0], b @ PURE[:, 0]
    for node, mix, index, condition in [
            (2, a, 1, 1-PURE[:, 0]), (4, a, 2, PURE[:, 0]),
            (3, b, 1, np.ones((512, 3))), (5, b, 2, PURE[:, 0])]:
        den = mix @ condition
        out[node, :, 1] = np.divide(mix @ (condition*PURE[:, index]), den,
                                    out=np.ones(3)*.5, where=den > 0)
    out[:, :, 0] = 1-out[:, :, 1]
    return out


def upper_ranges(policy):
    return [(1-policy[0, :, 1], np.ones(3)),
            (policy[0, :, 1], policy[1, :, 1])]


def complete_upper(policy):
    result = policy.copy()
    for c, (x, y), node in zip([1, 2], upper_ranges(policy), [2, 4]):
        _, (bet, call), _, _ = exact(c, x, y)
        result[node, :, 1], result[node+1, :, 1] = bet, call
        result[node:node+2, :, 0] = 1-result[node:node+2, :, 1]
    return result


class CFR:
    def __init__(self, leaf=None):
        self.leaf = leaf
        self.regrets = np.zeros((6, 3, 2))
        self.sums = np.zeros_like(self.regrets)
        self.fallbacks = 0

    def policy(self):
        r = np.maximum(self.regrets, 0)
        return np.divide(r, r.sum(axis=2, keepdims=True),
                         out=np.ones_like(r)*.5, where=r.sum(axis=2, keepdims=True)>0)

    def average(self):
        den = self.sums.sum(axis=2, keepdims=True)
        return np.divide(self.sums, den, out=np.ones_like(self.sums)*.5, where=den>0)

    def walk(self, node, reach, policy, update=False, fixed=None, br=None):
        if node < 0:
            # -1/-2 = fold, -11/-12/-13/-14 = matched showdown contribution.
            u = np.ones((3, 3))*(-node) if node in [-1, -2] else SIGN*(-node-10)
            return np.array([(u*LEGAL) @ reach[1], (-u*LEGAL).T @ reach[0]])/6
        if self.leaf is not None and node in [2, 4]:
            c = 1 if node == 2 else 2
            if fixed is None:
                values, behavior, _, fallback = self.leaf(c, *reach)
                self.fallbacks += int(fallback)
            else:
                values, behavior = fixed[node]
            if update and behavior is not None:
                for target, player, actions in [(node, 0, behavior[0]), (node+1, 1, behavior[1])]:
                    self.sums[target] += reach[player, :, None]*np.array([1-actions, actions]).T
            return values * np.array([LEGAL @ reach[1], LEGAL.T @ reach[0]])/6
        actor = node % 2
        if update:
            self.sums[node] += reach[actor, :, None]*policy[node]
        children = {0: (2, 1), 1: (-1, 4), 2: (-11, 3),
                    3: (-1, -13), 4: (-12, 5), 5: (-2, -14)}[node]
        cv = []
        for action, child in enumerate(children):
            child_reach = reach.copy()
            child_reach[actor] *= policy[node, :, action]
            cv.append(self.walk(child, child_reach, policy, update, fixed, br))
        cv = np.array(cv)
        out = cv.sum(axis=0)
        out[actor] = (cv[:, actor].T*policy[node]).sum(axis=1)
        if actor == br:
            out[actor] = cv[:, actor].max(axis=0)
        if update:
            self.regrets[node] += cv[:, actor].T-out[actor, :, None]
        return out

    def step(self):
        self.walk(0, np.ones((2, 3)), self.policy(), update=True)

    def frozen_gap(self, policy):
        fixed = {}
        for c, (x, y), node in zip([1, 2], upper_ranges(policy), [2, 4]):
            values, behavior, _, _ = self.leaf(c, x, y)
            fixed[node] = values, behavior
        return sum(float(self.walk(0, np.ones((2, 3)), policy, fixed=fixed, br=p)[p].sum())
                   for p in range(2))


class Surrogate:
    def __init__(self, datasets):
        self.models = {c: RBFInterpolator(data['x'], data['y'], neighbors=32,
                         kernel='thin_plate_spline', degree=1, smoothing=.0001)
                       for c, data in datasets.items()}

    def raw(self, c, x, y):
        x, y = normalize(x), normalize(y)
        return self.models[c](np.r_[x[:2], y[:2]][None])[0].reshape(2, 3)*c

    def __call__(self, c, x, y):
        x, y = normalize(x), normalize(y)
        v = self.raw(c, x, y)
        # Common shift after clipping with bisection preserves bounds and zero sum.
        w = np.array([x*(LEGAL@y), y*(LEGAL.T@x)])
        fallback = w.sum() <= 1e-15
        if fallback:
            return exact(c, x, y)
        low, high = -float(np.max(np.abs(v)))-c-2, float(np.max(np.abs(v)))+c+2
        for _ in range(45):
            mid = (low+high)/2
            if np.sum(w*np.clip(v-mid, -c-2, c+2)) > 0:
                low = mid
            else:
                high = mid
        v = np.clip(v-(low+high)/2, -c-2, c+2)
        return v, None, None, False


def dataset(n, seed):
    rng = np.random.default_rng(seed)
    datasets = {}
    for c in [1, 2]:
        inputs, outputs = [], []
        for k in range(n):
            alpha = [.25, 1., 4.][k % 3]
            x, y = rng.dirichlet(np.ones(3)*alpha, size=2)
            v, _, _, fallback = exact(c, x, y)
            assert not fallback
            inputs.append(np.r_[x[:2], y[:2]])
            outputs.append(v.ravel()/c)
        datasets[c] = {'x': np.array(inputs), 'y': np.array(outputs)}
    return datasets


def run_arm(name, leaf, reference):
    start = time.perf_counter()
    solver = CFR(leaf)
    rows = []
    for t in range(1, CHECKPOINTS[-1]+1):
        solver.step()
        if t not in CHECKPOINTS:
            continue
        learning_elapsed = time.perf_counter()-start
        avg = solver.average()
        completed = complete_upper(avg) if leaf is not None else avg
        row = {'iteration': t, 'elapsed_seconds': learning_elapsed,
               'full_game': measure(completed), 'root_bet_by_hand': avg[0, :, 1].tolist(),
               'first_call_by_hand': avg[1, :, 1].tolist(),
               'root_max_difference_to_lp': float(np.max(np.abs(avg[:2]-reference[:2]))),
               'policy': completed.tolist(), 'degenerate_fallbacks': solver.fallbacks}
        if leaf is not None:
            row['frozen_value_gap'] = solver.frozen_gap(avg)
            if name == 'exact_cutoff':
                row['accumulated_full_policy'] = measure(avg)
        rows.append(row)
        write(name+'.json', {'arm': name, 'rows': rows, 'complete': t == CHECKPOINTS[-1]})
        print(name, t, 'NashConv', row['full_game']['nashconv'],
              'frozen', row.get('frozen_value_gap'), 'seconds', learning_elapsed, flush=True)
    return rows


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'freeze.json').exists(), 'Do not overwrite registered runs'
    files = [Path(__file__), ROOT/'tools/research/test_continuation_exact_game.py', OUT/'PROTOCOL.md']
    write('freeze.json', {'registered_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                         'inputs': {str(p.relative_to(ROOT)): sha(p) for p in files},
                         'production_enabled': False})
    matrix = payoff(PURE[:, None], PURE[None, :])
    a, b, value, gap = equilibrium(matrix)
    reference = behavior_from_mixture(a, b)
    metrics = measure(reference)
    assert metrics['nashconv'] < 1e-8 and abs(metrics['ev_p0']-value) < 1e-8
    write('reference.json', {'game_value': value, 'lp_gap': gap, 'metrics': metrics,
                            'policy': reference.tolist()})
    full = run_arm('full_cfr', None, reference)
    cutoff = run_arm('exact_cutoff', exact, reference)
    passed = (full[-1]['full_game']['nashconv'] <= .005
              and cutoff[-1]['full_game']['nashconv'] <= .005)
    write('integration-gate.json', {'passed': passed, 'threshold': .005})
    if not passed:
        print('Exact integration gate failed; no surrogate training', flush=True)
        return
    train, test = dataset(512, 20260917), dataset(128, 20260918)
    model = Surrogate(train)
    write('datasets.json', {part: {str(c): {k: v.tolist() for k, v in data.items()}
                                     for c, data in ds.items()}
                            for part, ds in [('training', train), ('held_out', test)]})
    raw_errors, errors = [], []
    for c, data in test.items():
        for features, target in zip(data['x'], data['y']):
            x = np.r_[features[:2], 1-features[:2].sum()]
            y = np.r_[features[2:], 1-features[2:].sum()]
            raw_errors.extend(np.abs(model.raw(c, x, y).ravel()-target*c))
            errors.extend(np.abs(model(c, x, y)[0].ravel()-target*c))
    write('prediction-errors.json', {label: {'mae_chips': float(np.mean(e)),
            'p95_absolute_error': float(np.quantile(e, .95)), 'max_absolute_error': float(np.max(e))}
            for label, e in [('raw', raw_errors), ('corrected', errors)]})
    predicted = run_arm('predicted_cutoff', model, reference)
    ng = predicted[-1]['full_game']['nashconv']
    write('prediction-gate.json', {'passed': ng <= .005 and ng <= cutoff[-1]['full_game']['nashconv']+.002,
                                  'oracle_completed_nashconv': ng, 'production_enabled': False})
    print('Completed; production untouched', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['run'])
    parser.parse_args()
    run()
