"""Audit retained integration evidence only; no inference, fitting or new labels."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import hashlib
import json
from pathlib import Path
import time
import numpy as np

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
STORE = Path('S:/GTOpen-research/stack-context-full-control-v1')
QUERIES = Path('S:/GTOpen-research/stack-context-model-control-v1')
PREFIX = 'stack-context-full-control-v1'
DEST = OUT / (PREFIX + '-readback.json')
ATTEMPT = OUT / (PREFIX + '-readback-attempt.json')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, allow_nan=False, indent=2)
        stream.write('\n')


def main():
    assert not DEST.exists() and not ATTEMPT.exists()
    registration_path = OUT / (PREFIX + '-registration.json')
    result_path = OUT / (PREFIX + '-result.json')
    reg, result = read(registration_path), read(result_path)
    write(ATTEMPT, dict(pid=os.getpid(), source_sha256=sha(__file__),
                       result_sha256=sha(result_path), started_unix=time.time()))
    began = time.monotonic()
    try:
        assert result['passed'] and result['complete']
        assert result['registration_sha256'] == sha(registration_path)
        identities = {str(registration_path):sha(registration_path), str(result_path):sha(result_path)}
        for records in (reg['inputs'], result['artifacts']):
            for path, expected in records.items():
                assert sha(path) == expected, path
                identities[path] = expected
        depths = reg['depths']
        expected_pairs = {(width, depth) for width in reg['input_widths'] for depth in depths}
        checks = result['multi_context_checks']
        assert len(checks) == len(expected_pairs)
        assert {(c['width'],c['stack']) for c in checks} == expected_pairs
        summaries = []
        for item in checks:
            width, depth = item['width'], item['stack']
            query_path = QUERIES / f'stack-{depth}-queries.json'
            assert str(query_path) in identities
            observations = read(query_path)['observations']
            n = len(observations)
            legal = np.arange(4)[None,:] < np.asarray([o['n'] for o in observations])[:,None]
            path = STORE / f'{width}-{depth}-comparison.npz'
            assert str(path) in identities and item['rows'] == n
            with np.load(path, allow_pickle=False) as data:
                assert set(data.files) == {'cpu','gpu','average_cpu','average_gpu','reach_cpu','reach_gpu'}
                errors = {}
                for a,b in (('cpu','gpu'), ('average_cpu','average_gpu'), ('reach_cpu','reach_gpu')):
                    left,right = data[a],data[b]
                    assert left.shape == right.shape == ((n,) if a.startswith('reach') else (n,4))
                    assert np.isfinite(left).all() and np.isfinite(right).all()
                    for array in (left,right):
                        assert np.all(array >= 0)
                        if not a.startswith('reach'):
                            assert not np.any(array[~legal])
                            assert np.max(abs(array.sum(axis=1)-1)) <= 1e-12
                    error = float(np.max(abs(left-right)))
                    tolerance = reg['reach_absolute_tolerance'] if a.startswith('reach') else reg['policy_absolute_tolerance']
                    assert error <= tolerance
                    errors[a] = error
                assert errors['cpu'] == item['maximum_error']
            heldout = depth in reg['heldout']
            assert item['split'] == ('heldout' if heldout else 'fit')
            assert item['coverage']['learned_local_state'] == (not heldout)
            for field in ('exact_btn_rows','board_root_rows'):
                assert (item['coverage'][field] == 0) if heldout else (item['coverage'][field] > 0)
            summaries.append(dict(width=width, stack=depth, rows=n, maximum_errors=errors))
        assert len(result['retained_checks']) == 16 and len(result['negative_controls']) == 12
        for row in result['retained_checks']:
            assert row['maximum_error'] <= reg['policy_absolute_tolerance']
            if 'maximum_reach_error' in row:
                assert row['maximum_reach_error'] <= reg['reach_absolute_tolerance']
        for width in reg['input_widths']:
            fixture = read(STORE / f'{width}-fixture.json')
            contexts = fixture['registry']['contexts']
            fitting = {c['context_sha256'] for c in contexts if c['split'] == 'fit'}
            assert set(fixture['model']['local_states']) == set(fixture['resources']) == fitting
            assert fixture['changed_context'] in fitting and fixture['changed_rows'] > 0
        report = dict(complete=True, passed=True, source_sha256=sha(__file__), identities=identities,
                      arrays=summaries, seconds=time.monotonic()-began,
                      scope='Rehash inputs and outputs; recompute saved multi-context CPU/CUDA differences and probability invariants.',
                      limitations=['Retained single-context raw arrays were not saved; their scalar errors are checked as recorded, not independently replayed.',
                                   'Context-isolation and rejection executions are recorded controls, not independently rerun by this audit.',
                                   'Synthetic integration evidence is not trained-policy accuracy or a training checkpoint qualification.'],
                      scientific_training=False, accuracy_qualified=False)
    except Exception as error:
        report = dict(complete=False, passed=False, error=repr(error), seconds=time.monotonic()-began,
                      source_sha256=sha(__file__), retry_allowed=False)
    write(DEST, report)
    print(json.dumps({k:report[k] for k in ('complete','passed','seconds')}))
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
