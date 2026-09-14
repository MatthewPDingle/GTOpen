"""Retain the research candidate only after every registered gate passes."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from run_c23 import HERE, RAW, read


def sha(path):
    with Path(path).open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()


def main():
    for script in ['check_c23_integration.py', 'check_c23_repeats.py']:
        subprocess.run([sys.executable, str(HERE/script)], check=True, stdout=subprocess.DEVNULL)
    timing = read(RAW/'c23-repeats-verified.json')
    numerical = read(RAW/'c23-integration-verified.json')
    assert timing['passed_timing'] and numerical['admitted']
    source = read(RAW/'c23-numerical-v1-exit.json')['solver_source_files']
    lab = HERE.parents[3]
    for path, expected in source.items():
        assert sha(lab/path) == expected, path
    tests = {}
    for stage, expected in [('native', 20), ('default', 181)]:
        name = 'c23-'+stage+'-v1'
        record = read(RAW/(name+'-exit.json'))
        assert record['returncode'] == 0 and record['reason'] is None and record['seconds'] <= 300
        assert record['solver_source_files'] == source
        for path, expected_sha in record['inputs'].items():
            assert sha(path) == expected_sha, path
        command = record['command']
        assert command[:5] == ['cargo', 'test', '--release', '-p', 'solver']
        if stage == 'native':
            for target in ['gpu', 'preflop_gpu', 'preflop_throughput']:
                assert target in command
        else:
            assert command == ['cargo', 'test', '--release', '-p', 'solver']
        log = (RAW/(name+'.log')).read_text(encoding='utf-8')
        results = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed;', log)
        assert results and all(int(failed) == 0 for _, failed in results)
        count = sum(int(passed) for passed, _ in results)
        assert count == expected, (stage, count)
        tests[stage] = {'passed': count, 'guard_seconds': record['seconds'], 'log_sha256': sha(RAW/(name+'.log'))}
    result = {**timing, 'retained': True, 'admitted': True,
        'status': 'Retained: static rank-boundary CDF storage',
        'display_gain': '14.0% less large-game runtime', 'regressions': tests,
        'solver_tests': numerical['solver_tests'], 'deployed': False,
        'scope': 'Research constructor retained: six exact fixed-work pairs, numerical/stop/save/recovery qualification, 20 native GPU and 181 default tests. Normal app integration and deployment are separate; convergence qualification remains open.'}
    destination = RAW/'c23-retention-verified.json'
    if destination.exists():
        assert read(destination) == result
    else:
        destination.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    (RAW/'c23-verified.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
