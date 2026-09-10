"""Derive CPU comparisons from immutable raw logs; never modifies inputs."""
import json
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent

def read(name):
    path = HERE / 'raw' / (name + '.log')
    return [json.loads(line[6:]) for line in path.read_text(encoding='utf-8').splitlines()
            if line.startswith('BENCH ')]

def max_difference(a, b):
    if len(a) != len(b):
        raise ValueError('Mismatched comparison dimensions')
    return max((abs(x-y) for x, y in zip(a, b)), default=0)

out = {'terminal': [], 'solve': []}
baseline = read('cpu-terminal-baseline-a')
for path in sorted((HERE / 'raw').glob('cpu-terminal-*.log')):
    if 'baseline' in path.stem:
        continue
    candidate = read(path.stem)
    if len(candidate) != len(baseline):
        continue
    for a, b in zip(baseline, candidate):
        assert (a['opponents'], a['sparse']) == (b['opponents'], b['sparse'])
        before, after = median(a['times_ms']), median(b['times_ms'])
        out['terminal'].append({'run': path.stem, 'opponents': a['opponents'],
            'sparse': a['sparse'], 'baseline_ms': before, 'candidate_ms': after,
            'time_reduction_pct': (1-after/before)*100,
            'max_equity_error': max_difference(a['equities'], b['equities'])})
for fixture, baseline_id in [('three', 'cpu-three-baseline-b'),
                              ('four', 'cpu-four-baseline-a'),
                              ('six', 'cpu-six-baseline-a')]:
    original = read(baseline_id)
    a = [r for r in original if r['phase'] == 'cpu_solve'][-1]
    strategy_a = [r for r in original if r['phase'] == 'cpu_strategy'][-1]
    for path in sorted((HERE / 'raw').glob(f'cpu-{fixture}-*.log')):
        if 'baseline' in path.stem:
            continue
        candidate = read(path.stem)
        checkpoints = [r for r in candidate if r['phase'] == 'cpu_solve']
        strategies = [r for r in candidate if r['phase'] == 'cpu_strategy']
        if not checkpoints or not strategies:
            continue
        b, strategy_b = checkpoints[-1], strategies[-1]
        out['solve'].append({'run': path.stem, 'baseline_run': baseline_id,
            'baseline_iterations': a['iteration'], 'candidate_iterations': b['iteration'],
            'baseline_reached_target': a['reached'], 'candidate_reached_target': b['reached'],
            'target': a['target'], 'baseline_ms': a['elapsed_ms'], 'candidate_ms': b['elapsed_ms'],
            'time_reduction_pct': (1-b['elapsed_ms']/a['elapsed_ms'])*100,
            'max_gap_error': max_difference(a['gaps'], b['gaps']),
            'max_ev_error': max_difference(a['evs'], b['evs']),
            'max_root_strategy_error': max_difference(strategy_a['strategy'], strategy_b['strategy'])})
(HERE / 'cpu-comparisons.json').write_text(json.dumps(out, indent=2)+'\n', encoding='utf-8')
print(f"Compared {len(out['terminal'])} terminal cases and {len(out['solve'])} solves")
