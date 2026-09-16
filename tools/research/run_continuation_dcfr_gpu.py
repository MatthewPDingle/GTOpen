"""Registered production-kernel miniature diagnostic. No application changes."""
import argparse
import datetime as dt
import json
import time
from pathlib import Path
import numpy as np
import torch
import continuation_exact_game as game
import continuation_exact_game_robust as robust
import continuation_exact_game_offsupport as off
import continuation_dcfr_gpu as fixture

OUT = fixture.OUT
CHECKPOINTS = [100, 500, 2000, 5000, 10000, 20000]


def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def parity(driver):
    rng = np.random.default_rng(20260917)
    maxima = {'reach': 0., 'transfer': 0., 'regrets': 0., 'sums': 0., 'up_values': 0.}
    comparisons = 0
    def check(label, a, b):
        nonlocal comparisons
        maxima[label] = max(maxima[label], float(np.max(np.abs(a-b))))
        np.testing.assert_allclose(a, b, atol=1e-5, rtol=2e-6, err_msg=label)
        comparisons += 1
    for cutoff in [False, True]:
        gpu, cpu = fixture.GPU(driver, cutoff), fixture.CPU(cutoff)
        for case in range(24):
            # Include uniform, tiny positive regrets, mixed signs, and sparse reaches.
            cpu.regrets[:] = rng.normal(size=cpu.regrets.shape).astype(np.float32)
            cpu.sums[:] = rng.random(size=cpu.sums.shape).astype(np.float32)
            cpu.regrets[:, :, 3:] = 0; cpu.sums[:, :, 3:] = 0
            if case == 0: cpu.regrets[:] = 0; cpu.sums[:] = 0
            if case == 1: cpu.regrets[:, :, :3] *= np.float32(1e-13)
            gpu.regrets_gpu.copy_(torch.from_numpy(cpu.regrets))
            gpu.sums_gpu.copy_(torch.from_numpy(cpu.sums))
            for p in range(2):
                reach = gpu.down(); check('reach', reach, cpu.down())
                pred, direct = fixture.leaf_values(cpu, reach, p, off.completed_exact)
                gpu.transfer(p, pred)
                observed = gpu.val.cpu().numpy()
                check('transfer', observed[cpu.leaves, :3], direct[cpu.leaves])
                assert not np.any(observed[cpu.leaves, 3:])
                # Identical GPU-derived leaves isolate down/up math from oracle tie choices.
                leaves = observed[:, :3].copy()
                gpu.up(p); expected = cpu.up(p, leaves)
                check('up_values', gpu.val.cpu().numpy()[cpu.order], expected[cpu.order])
                check('regrets', gpu.regrets_gpu.cpu().numpy(), cpu.regrets)
                check('sums', gpu.sums_gpu.cpu().numpy(), cpu.sums)
            t = [1, 100, 20000][case % 3]
            gpu.discount(t); cpu.discount(t)
            check('regrets', gpu.regrets_gpu.cpu().numpy(), cpu.regrets)
            check('sums', gpu.sums_gpu.cpu().numpy(), cpu.sums)
    # A serial 100-iteration parity run, using common leaves, exercises accumulation.
    gpu, cpu = fixture.GPU(driver, False), fixture.CPU(False)
    for t in range(1, 101):
        for p in range(2):
            reach = gpu.down(); check('reach', reach, cpu.down())
            pred, direct = fixture.leaf_values(cpu, reach, p, None)
            gpu.transfer(p, pred)
            leaves = gpu.val.cpu().numpy()[:, :3].copy()
            gpu.up(p); cpu.up(p, leaves)
        gpu.discount(t); cpu.discount(t)
        check('regrets', gpu.regrets_gpu.cpu().numpy(), cpu.regrets)
        check('sums', gpu.sums_gpu.cpu().numpy(), cpu.sums)
    return {'passed': True, 'comparisons': comparisons, 'maximum_absolute_errors': maxima,
            'atol': 1e-5, 'rtol': 2e-6, 'random_cases_per_layout': 24, 'serial_iterations': 100}


def run_arm(driver, name, oracle):
    solver = fixture.GPU(driver, oracle is not None)
    rows = []; start = time.perf_counter()
    for t in range(1, CHECKPOINTS[-1]+1):
        for player in range(2):
            reach = solver.down()
            pred, _ = fixture.leaf_values(solver, reach, player, oracle)
            solver.transfer(player, pred); solver.up(player)
        solver.discount(t)
        if t not in CHECKPOINTS: continue
        avg = solver.average()
        completed = game.complete_upper(avg) if oracle is not None else avg
        m = game.measure(completed)
        # Second, recursive full-tree best response in the independent harness.
        evaluator = game.CFR()
        independent = sum(evaluator.walk(0, np.ones((2, 3)), completed, br=p)[p].sum() for p in range(2))
        assert abs(independent-m['nashconv']) < 1e-10
        row = {'iteration': t, 'elapsed_seconds': time.perf_counter()-start,
               'full_game': m, 'independent_recursive_nashconv': float(independent),
               'root_bet_by_hand': avg[0, :, 1].tolist(), 'first_call_by_hand': avg[1, :, 1].tolist(),
               'policy': completed.tolist()}
        if oracle is not None: row['frozen_value_gap'] = game.CFR(oracle).frozen_gap(avg)
        assert not torch.any(solver.regrets_gpu[:, :, 3:]).item()
        assert not torch.any(solver.sums_gpu[:, :, 3:]).item()
        rows.append(row)
        write(name+'.json', {'arm': name, 'complete': t == CHECKPOINTS[-1], 'rows': rows})
        print(name, t, 'true_gap', m['nashconv'], 'frozen', row.get('frozen_value_gap'), flush=True)
    return rows


def run(smoke=False):
    OUT.mkdir(exist_ok=True)
    game.linprog = robust.robust_linprog
    if not smoke:
        assert not (OUT/'freeze.json').exists(), 'Keep registered runs immutable'
        files = [Path(__file__), Path(fixture.__file__), Path(fixture.__file__).with_suffix('.cu'),
                 Path(game.__file__), Path(robust.__file__), Path(off.__file__), fixture.SOURCE,
                 game.ROOT/'crates/solver/src/preflop/mod.rs', game.ROOT/'crates/solver/src/preflop/gpu.rs',
                 game.ROOT/'tools/research/compile_cuda_offline.py', OUT/'PROTOCOL.md',
                 OUT.with_name('exact-game-extension-20260917')/'datasets.json',
                 OUT.with_name('full-precision-20260916')/'double/interface.cu']
        write('freeze.json', {'registered_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                             'inputs': {str(p.relative_to(game.ROOT)): game.sha(p) for p in files},
                             'checkpoints': CHECKPOINTS, 'production_enabled': False})
    driver = fixture.Driver(OUT/('smoke' if smoke else 'cuda'))
    checks = parity(driver)
    write('smoke-checks.json' if smoke else 'parity-checks.json', checks)
    print(json.dumps(checks), flush=True)
    if smoke: return
    arms = {}
    for name, oracle in [('full_dcfr', None), ('exact_cutoff', game.exact), ('offsupport_cutoff', off.completed_exact)]:
        arms[name] = run_arm(driver, name, oracle)
    passed = all(rows[-1]['full_game']['nashconv'] <= .005 for rows in arms.values())
    write('integration-gate.json', {'passed': passed, 'threshold': .005})
    # Even on an exact-control failure run the predeclared prediction diagnostic,
    # but do not attribute failures solely to the predictor or claim integration passed.
    dataset_path = OUT.with_name('exact-game-extension-20260917')/'datasets.json'
    data = json.loads(dataset_path.read_text())['training']
    model = game.Surrogate({int(c): {k: np.array(v) for k, v in row.items()} for c, row in data.items()})
    arms['predicted_cutoff'] = run_arm(driver, 'predicted_cutoff', model)
    predicted = arms['predicted_cutoff'][-1]['full_game']['nashconv']
    write('prediction-gate.json', {'passed': passed and predicted <= .005 and
          predicted <= arms['exact_cutoff'][-1]['full_game']['nashconv']+.002,
          'exact_controls_passed': passed, 'nashconv': predicted, 'production_enabled': False})
    frozen = json.loads((OUT/'freeze.json').read_text())['inputs']
    assert all(game.sha(game.ROOT/p) == h for p, h in frozen.items())
    write('execution.json', {'gpu_executed': True, 'gpu': torch.cuda.get_device_name(),
          'torch': torch.__version__, 'kernel_launches': driver.launches, 'frozen_inputs_unchanged': True,
          'completed_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'production_enabled': False})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--smoke', action='store_true')
    run(parser.parse_args().smoke)
