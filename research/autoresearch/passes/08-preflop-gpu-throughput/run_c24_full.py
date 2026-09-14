"""One full C24 role per invocation; fixed order, cap and immutable executable."""
import math
import sys
from pathlib import Path
from run_c23 import HERE, RAW, read, run07
from run_c07 import snapshot

ORDER = [(1, 'control'), (1, 'candidate'), (2, 'candidate'),
         (2, 'control'), (3, 'control'), (3, 'candidate')]

def compare(a, b):
    for key in ['input', 'nodes', 'initial_iteration', 'iteration', 'batch', 'budget_mb',
                'hu_cache', 'samples', 'initial_buffers', 'arena_entries', 'arena_fingerprint']:
        assert a[key] == b[key], key
    assert len(a['rows']) == len(b['rows']) == 6
    for x, y in zip(a['rows'], b['rows']):
        for key in ['index', 'iteration', 'warmup', 'gaps', 'evs']:
            assert x[key] == y[key], key
    assert not a['packed'] and b['packed']
    assert a['final_device_bytes'] - b['final_device_bytes'] == 1792219820
    return b['complete_seconds'] / a['complete_seconds']

def main():
    pair, role = int(sys.argv[1]), sys.argv[2]
    index = ORDER.index((pair, role))
    assert read(RAW / 'c24-native-screen-verified.json')['admitted']
    # Require all previous roles to finish, and verify every complete pair.
    for previous_pair, previous_role in ORDER[:index]:
        receipt = read(RAW / f'c24-current-{previous_role}-full{previous_pair}-exit.json')
        assert receipt['returncode'] == 0 and receipt['reason'] is None
    for previous_pair in range(1, pair):
        compare(read(RAW / f'c24-current-control-full{previous_pair}-bench.json'),
                read(RAW / f'c24-current-candidate-full{previous_pair}-bench.json'))
    fixture = read(RAW / 'c24-user-fixture.json')
    source = Path(fixture['frozen'])
    exe = run07.LAB / 'target/c24-native-benchmark-frozen.exe'
    assert run07.digest(source) == fixture['sha256']
    assert run07.digest(exe) == read(RAW / 'c24-native-frozen.json')['sha256']
    cap = math.ceil(read(RAW / 'c24-native-screen-protocol.json')['baseline_guarded_seconds'] * 2 * 1.2 / 60) * 60
    assert cap == 600
    name = f'c24-current-{role}-full{pair}'
    output = RAW / (name + '-bench.json')
    eq = run07.LAB / 'cache/preflop_eq169.bin'
    fit = run07.LAB / 'cache/realization_fit.json'
    inputs = [Path(__file__), HERE / 'C24_PROTOCOL.md', HERE / 'C24_FULL_TIMING.md',
              HERE / 'artifacts/c24-benchmark-source-map.json', RAW / 'c24-native-screen-protocol.json',
              RAW / 'c24-native-screen-verified.json', RAW / 'c24-user-fixture.json', source, exe, eq, fit]
    snapshot(name, 'before')
    run07.run(name, [exe, 'preflop::gpu::static_cdf::ordinary::tests::frozen_native_benchmark',
                    '--exact', '--ignored', '--nocapture', '--test-threads=1'], cap, inputs,
              {'PREFLOP_GPU_REUSE_INPUT': str(source), 'PREFLOP_GPU_REUSE_OUTPUT': str(output),
               'PREFLOP_GPU_ORDINARY_STATIC_ENABLE': str(int(role == 'candidate')),
               'PREFLOP_GPU_ORDINARY_BUDGET': str(fixture['native_budget_mb']),
               'PREFLOP_GPU_ORDINARY_BATCH': str(fixture['expected_batch']),
               'PREFLOP_GPU_ORDINARY_ROUNDS': '6',
               'PREFLOP_GPU_ORDINARY_STATIC_OUTPUT': str(RAW / 'c24-native-artifacts-v1'),
               'REALIZATION_FIT': str(fit)})
    snapshot(name, 'after')
    result = read(output)
    assert len(result['rows']) == 6 and result['initial_iteration'] == 53 and result['iteration'] == 59
    if index % 2 == 1:
        ratio = compare(read(RAW / f'c24-current-control-full{pair}-bench.json'),
                        read(RAW / f'c24-current-candidate-full{pair}-bench.json'))
        print(f'Full pair {pair}: ratio {ratio:.9f}; exact checkpoint values and arena fingerprint.', flush=True)

if __name__ == '__main__':
    main()
