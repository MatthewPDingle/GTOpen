"""Root-scheduled adaptive diagnostics only; does not run when imported."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PASS = Path('T:/Dev/GTOpen/research/autoresearch/passes/04-preflop-interactive-20260911')
RAW = PASS / 'raw'
DEADLINE = dt.datetime(2026, 9, 11, 3, 3, 27, tzinfo=dt.timezone.utc)
PIN = {
    'preview128-eight-1000-a': '069f5c041297194e6690ed94f26180ad0b5fbbf178fbc32ab5b076770131fb67',
    'quality-large128-1000-a': 'bc9890c1b75b02abb7cacd15e05a08b33089d1ef173fbf8b8c9697c0b7c9ad0c',
    'small128-fixed-frozen-primary-a': '421df2e04a5d307878935a5758f7ebb25766d07b1fdcd73ddf0abf6439ce93ca',
    'quality-small128-fixed-frozen-primary-a-checkpoint-100': 'bf057d98c84b832ddd1422243f86210b08a8048061108c0feef68d139bfc60c3',
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for part in iter(lambda: source.read(8 * 1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def protocol(run):
    record = json.loads((RAW / (run + '-protocol.json')).read_text(encoding='utf-8-sig'))
    result = json.loads((RAW / (run + '-result.json')).read_text(encoding='utf-8-sig'))
    assert result['returncode'] == 0, 'Original run did not complete'
    assert record['executable_sha256'] == PIN[run]
    assert sha(record['command'][0]) == PIN[run], 'Frozen executable changed'
    assert record['equity_cache_sha256'] == '78b4656ddace5efdb84c77811e9e7891982fb9180d9909a770e7ca4a28fd27ad'
    assert record['realization_fit_sha256'] == '3f3040ca917930fafa0c9ab8982c44d31513321f3e63d44f39b3d2157673bf18'
    return record


def input_hashes(paths):
    return {str(Path(path).resolve()): sha(path) for path in paths}


def unchanged(expected):
    actual = input_hashes(expected)
    if actual != expected:
        raise RuntimeError('Immutable input changed: ' + ', '.join(
            path for path in expected if actual.get(path) != expected[path]))


def run_job(record, name, command, timeout, results, protected):
    unchanged(protected)
    invocation = [sys.executable, str(PASS / 'guarded_run.py'), '--timeout', str(timeout),
                  '--cwd', record['cwd'], name, *command]
    with (RAW / (name + '-driver.txt')).open('x', encoding='utf-8') as trace:
        child = subprocess.run(invocation, stdout=trace, stderr=subprocess.STDOUT, check=False)
    result_path = RAW / (name + '-result.json')
    terminal = json.loads(result_path.read_text(encoding='utf-8-sig')) if result_path.exists() else {}
    results.append({'id': name, 'command': command, 'driver_returncode': child.returncode,
                    'returncode': terminal.get('returncode'), 'reason': terminal.get('reason')})
    unchanged(protected)
    results[-1]['immutable_inputs_exact'] = True
    if child.returncode != 0 or terminal.get('returncode') != 0:
        raise RuntimeError('Incomplete job; later jobs remain unrun: ' + name)
    for field in ('executable_sha256', 'equity_cache_sha256', 'realization_fit_sha256'):
        if terminal.get(field) != record[field]:
            raise RuntimeError('Guarded execution provenance changed: ' + field)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True, choices=['small', 'large'])
    args = parser.parse_args()
    report = {'group': args.group, 'adaptive_followup': True, 'status': 'unrun', 'jobs': []}
    destination = RAW / ('adaptive128-' + args.group + '-followup-a-summary.json')
    with destination.open('x', encoding='utf-8') as output:
        try:
            reserve = 120 if args.group == 'small' else 720
            if (DEADLINE - dt.datetime.now(dt.timezone.utc)).total_seconds() < reserve:
                report['reason'] = 'Insufficient reserved deadline window; no jobs started'
                return
            base = protocol('small128-fixed-frozen-primary-a' if args.group == 'small' else 'preview128-eight-1000-a')
            quality = protocol('quality-small128-fixed-frozen-primary-a-checkpoint-100' if args.group == 'small' else 'quality-large128-1000-a')
            cache = Path(quality['command'][3])
            assert sha(cache) == base['equity_cache_sha256'], 'Current cache changed'
            assert sha(base['fixed_environment']['REALIZATION_FIT']) == base['realization_fit_sha256'], 'Current fit changed'
            protected = input_hashes([
                base['command'][0], quality['command'][0], base['command'][1],
                quality['command'][2], cache, base['fixed_environment']['REALIZATION_FIT']])
            if args.group == 'small':
                command = list(base['command'])
                old100 = Path(command[5]) / 'checkpoint-100.gtop'
                protected.update(input_hashes([old100, quality['command'][5]]))
                if sha(command[1]) != '709fe72192af25e3f9c964be7cc6a596265e5d753119bd1aa35a7c8ed388e13b':
                    raise RuntimeError('Registered small corpus changed')
                if json.loads(Path(quality['command'][5]).read_text()) != [[], [1], [2]]:
                    raise RuntimeError('Registered local paths changed')
                report['immutable_inputs_before'] = dict(protected)
                report['prior100_sha256'] = protected[str(old100.resolve())]
                newdir = Path(command[5]).parent / 'small128-fixed-frozen-fixed500-followup-a'
                assert not newdir.exists(), 'Output already exists'
                command[5] = str(newdir)
                command.append('--fixed-iterations=500')
                run_job(base, 'small128-fixed-frozen-fixed500-followup-a', command, 60, report['jobs'], protected)
                report['followup100_sha256'] = sha(newdir / 'checkpoint-100.gtop')
                report['trajectory100_exact'] = report['prior100_sha256'] == report['followup100_sha256']
                assert report['trajectory100_exact'], 'Trajectory identity mismatch; stop before interpretation'
                for iteration in (100, 500):
                    command = list(quality['command'])
                    command[1] = str(newdir / f'checkpoint-{iteration}.gtop')
                    audited_inputs = {**protected, **input_hashes([command[1]])}
                    run_job(quality, f'quality-small128-fixed-frozen-followup-{iteration}-a', command, 30, report['jobs'], audited_inputs)
            else:
                report['immutable_inputs_before'] = dict(protected)
                command = list(base['command'])
                native = Path(command[4]).parent / 'preview128-eight-500-followup-a.gtop'
                assert not native.exists(), 'Output already exists'
                command[3], command[4] = '500', str(native)
                run_job(base, 'preview128-eight-500-followup-a', command, 500, report['jobs'], protected)
                report['native_sha256'] = sha(native)
                command = list(quality['command'])
                command[1] = str(native)
                run_job(quality, 'quality-large128-500-followup-a', command, 180, report['jobs'], {**protected, **input_hashes([native])})
            unchanged(protected)
            report['immutable_inputs_after_exact'] = True
            report['status'] = 'completed'
        except Exception as error:
            report['status'] = 'incomplete'
            report['reason'] = str(error)
            raise
        finally:
            json.dump(report, output, indent=2)
            output.write('\n')


if __name__ == '__main__':
    main()
