"""Registered native/default regression checks after all C23 timing passes.

The candidate stays research-only. Native tests exercise production feature
isolation; the prior 10-test research suite exercises the actual C23 dispatch.
No server build, deployment or change to the live solve is performed here.
"""
import sys
from pathlib import Path
from run_c23 import HERE, RAW, read, run07


def main():
    assert read(RAW/'c23-repeats-verified.json')['passed_timing']
    stage = sys.argv[1]
    commands = {
        'native': ['cargo', 'test', '--release', '-p', 'solver', '--features', 'gpu',
                   '--test', 'gpu', '--test', 'preflop_gpu', '--test', 'preflop_throughput',
                   '--', '--test-threads=1'],
        'default': ['cargo', 'test', '--release', '-p', 'solver'],
    }
    run07.run('c23-'+stage+'-v1', commands[stage], 300,
        [Path(__file__), HERE/'C23_PROTOCOL.md', HERE/'C23_INTEGRATION.md',
         RAW/'c23-repeats-verified.json', RAW/'c23-integration-verified.json'], {})
    record = read(RAW/('c23-'+stage+'-v1-exit.json'))
    assert record['returncode'] == 0 and record['reason'] is None
    assert record['solver_source_files'] == read(RAW/'c23-numerical-v1-exit.json')['solver_source_files']


if __name__ == '__main__':
    main()
