"""One fixed-work comparison role at a time, independent of historical chains."""
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
    assert not a['packed'] and b['packed'] and b['static_cdf']['row_stride'] == 2160
    return b['complete_seconds'] / a['complete_seconds']

def main():
    fixture, pair, role = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    assert fixture in ['small', 'large']
    index = ORDER.index((pair, role))
    full = read(RAW / 'c24-full-verified.json')
    assert full['admitted'] and len(full['pairs']) == 3
    for n, r in ORDER[:index]:
        receipt = read(RAW / f'c24-witness{fixture}-{r}-full{n}-exit.json')
        assert receipt['returncode'] == 0 and receipt['reason'] is None
    for n in range(1, pair):
        compare(read(RAW / f'c24-witness{fixture}-control-full{n}-bench.json'),
                read(RAW / f'c24-witness{fixture}-candidate-full{n}-bench.json'))
    if fixture == 'large':
        for n in range(1, 4):
            compare(read(RAW / f'c24-witnesssmall-control-full{n}-bench.json'),
                    read(RAW / f'c24-witnesssmall-candidate-full{n}-bench.json'))
    source = run07.LAB / ('target/convergence/eight-native-a/final.gtop' if fixture == 'large'
                         else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    # Bind the witness to a completed C23 input receipt, not merely its filename.
    records = list(RAW.glob(f'c23-{fixture}-*-exit.json'))
    hashes = {digest for path in records for file, digest in read(path)['inputs'].items()
              if Path(file) == source}
    assert len(hashes) == 1 and run07.digest(source) in hashes
    exe = run07.LAB / 'target/c24-native-benchmark-frozen.exe'
    assert run07.digest(exe) == read(RAW / 'c24-native-frozen.json')['sha256']
    name = f'c24-witness{fixture}-{role}-full{pair}'
    output = RAW / (name + '-bench.json')
    eq = run07.LAB / 'cache/preflop_eq169.bin'
    fit = run07.LAB / 'cache/realization_fit.json'
    inputs = [Path(__file__), HERE / 'C24_PROTOCOL.md', HERE / 'C24_COMPARISON_TIMING.md',
              HERE / 'artifacts/c24-benchmark-source-map.json', RAW / 'c24-full-verified.json',
              source, exe, eq, fit]
    snapshot(name, 'before')
    run07.run(name, [exe, 'preflop::gpu::static_cdf::ordinary::tests::frozen_native_benchmark',
                    '--exact', '--ignored', '--nocapture', '--test-threads=1'], 300, inputs,
              {'PREFLOP_GPU_REUSE_INPUT': str(source), 'PREFLOP_GPU_REUSE_OUTPUT': str(output),
               'PREFLOP_GPU_ORDINARY_STATIC_ENABLE': str(int(role == 'candidate')),
               'PREFLOP_GPU_ORDINARY_BUDGET': '23911', 'PREFLOP_GPU_ORDINARY_BATCH': '32',
               'PREFLOP_GPU_ORDINARY_ROUNDS': '6',
               'PREFLOP_GPU_ORDINARY_STATIC_OUTPUT': str(RAW / 'c24-native-artifacts-v1'),
               'REALIZATION_FIT': str(fit)})
    snapshot(name, 'after')
    if index % 2 == 1:
        ratio = compare(read(RAW / f'c24-witness{fixture}-control-full{pair}-bench.json'),
                        read(RAW / f'c24-witness{fixture}-candidate-full{pair}-bench.json'))
        print(f'{fixture} pair {pair}: ratio {ratio:.9f}; exact checkpoints and arena fingerprint.', flush=True)

if __name__ == '__main__':
    main()
