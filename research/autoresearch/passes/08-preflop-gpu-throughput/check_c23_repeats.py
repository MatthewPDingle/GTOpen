"""Check registered full-work pairs; passing timing is not release approval."""
import hashlib
import json
import statistics
import sys
from pathlib import Path
from run_c23 import HERE, RAW, read, compare


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    qualified = read(RAW/'c23-integration-verified.json')
    source = read(RAW/'c23-numerical-v1-exit.json')['solver_source_files']
    fixtures = {}
    large_only = '--large-only' in sys.argv
    for fixture, pairs in ([('large', [2, 3, 4])] if large_only else [('large', [2, 3, 4]), ('small', [1, 2, 3])]):
        results = []
        reference = read(RAW/f'c14-{fixture}-control-1-bench.json')
        for pair in pairs:
            values = {}
            for role in ['control', 'candidate']:
                name = f'c23-{fixture}-{role}-{pair}'
                record = read(RAW/(name+'-exit.json'))
                assert record['returncode'] == 0 and record['reason'] is None and record['seconds'] <= 180
                assert record['exe_sha256'] == qualified['executable_sha256']
                assert record['solver_source_files'] == source
                for path, expected in record['inputs'].items():
                    assert sha(path) == expected, path
                assert record['environment_overrides']['PREFLOP_GPU_STATIC_CDF'] == str(int(role == 'candidate'))
                value = read(RAW/(name+'-bench.json'))
                for key in ['arena_entries', 'arena_fingerprint', 'initial_iteration', 'iteration']:
                    assert value[key] == reference[key], (name, key)
                for row, ref in zip(value['rows'], reference['rows']):
                    for key in ['gaps', 'evs', 'iteration', 'index', 'warmup']:
                        assert row[key] == ref[key], (name, key)
                values[role] = value
            a, b = values['control'], values['candidate']
            results.append({'pair': pair, 'ratio': compare(a, b),
                'control_seconds': a['complete_seconds'], 'candidate_seconds': b['complete_seconds']})
        fixtures[fixture] = {'pairs': results, 'median_ratio': statistics.median(r['ratio'] for r in results)}
    passed = fixtures['large']['median_ratio'] <= .97 and (large_only or fixtures['small']['median_ratio'] <= 1.03)
    result = {'verified': True, 'retained': False, 'admitted': passed, 'passed_timing': passed,
        'status': ('Large timing passed; small fixture and regressions pending' if large_only else 'Repeated timing passed; regression qualification pending') if passed else 'Repeated timing failed retention gate',
        'fixtures': fixtures, 'exact_checkpoints_and_arena': True,
        'executable_sha256': qualified['executable_sha256'],
        'scope': ('Three large pairs only; small fixture is untested.' if large_only else 'Six complete pairs;') + ' No convergence or deployment claim. Native and default regressions still required.'}
    destination = RAW/('c23-large-repeats-verified.json' if large_only else 'c23-repeats-verified.json')
    if destination.exists():
        assert read(destination) == result
    else:
        destination.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
