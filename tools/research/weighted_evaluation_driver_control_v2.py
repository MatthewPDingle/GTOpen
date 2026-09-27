"""Mechanical driver integration using old outcomes instead of GPU evaluation.

This tests checkpoint boundaries, archive routing and final statistics, not
neural inference or the scientific admission gates (which are mocked here).
"""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import time
import numpy as np
import weighted_complete_evaluation_study_v2 as driver
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from owned_columnar_evaluation_archive_v1 import restore
from weighted_evaluation_runtime_v2 import runtime_guard, owned_scratch_path

PREFIX = 'weighted-complete-driver-control-v2'


def main():
    started = time.monotonic()
    old_path = OUT / 'showdown-pipelined-evaluation-study-v1-result.json'
    old_reg = OUT / 'showdown-pipelined-evaluation-study-v1-registration.json'
    old, reg = read(old_path), read(old_reg)
    assert old['passed'] and old['registration_sha256'] == sha(old_reg)
    store = Path('S:/GTOpen-research') / PREFIX
    assert not store.exists()
    registration = OUT / f'{PREFIX}-registration.json'
    assert not registration.exists()
    training_lock = driver.LOCK
    before = training_lock.read_bytes() if training_lock.exists() else None
    identities = read(Path(old['store']) / 'bank-identities.json')
    roots = read(Path(old['store']) / 'root-stability.json')['root_probabilities']
    args = dict(context_source=driver.CONTEXT.read_text())
    fixtures, paths = {}, [old_path, old_reg]
    for offset in (0, 32):
        name = f'test-{offset:06d}'
        mp = Path(reg['original_store']) / (name + '.manifest.json')
        ap = mp.with_name(name + '.xz')
        assert sha(mp) == old['archive_manifest_hashes'][name]
        fixtures[name] = restore(ap, read(mp), guard=lambda: None)
        paths.extend([mp, ap])
    calls = []
    def copied_evaluation(*, batch, folder, guard, **unused):
        guard()
        name = batch['batch_id'].removeprefix(PREFIX + '-')
        assert name in fixtures and name not in calls
        parts = fixtures[name]
        assert batch['deals'] == json.loads(parts['query-batch.json'])['deals']
        calls.append(name)
        folder.mkdir()
        for member, raw in parts.items():
            with (folder / member).open('xb') as f:
                f.write(raw)
        return json.loads(parts['summary.json'])
    test_lock = OUT / (PREFIX + '.lock')
    assert not test_lock.exists()
    def fake_gpu_probe(command, **unused):
        assert command[0] == 'nvidia-smi'
        return SimpleNamespace(returncode=0, stdout='0,24000\n')
    substitutions = dict(PREFIX=PREFIX, CONTROL='showdown-pipelined-evaluation-study-v1', STORE=store, REG=registration, TEST_DEALS=64, TEST_SEED=9267201,
        LOCK=test_lock, qualification=lambda: (paths, old), setup_cuda=lambda: None,
        load_banks=lambda **kw: ([], [], identities, [], args),
        catalog_roots=lambda *a, **kw: (np.asarray(roots), []), evaluate_batch=copied_evaluation,
        runtime_guard=lambda path, **kw: runtime_guard(path, gpu=False, **kw))
    with patch.multiple(driver, **substitutions), patch('subprocess.run', side_effect=fake_gpu_probe), patch('psutil.cpu_percent', return_value=0.):
        driver.run(max_batches=1)
        assert calls == ['test-000000']
        assert not (OUT / (PREFIX + '-result.json')).exists()
        first = read(OUT / (PREFIX + '-status.json'))
        assert first['state'] == 'checkpointed invocation limit' and first['completed_deals'] == 32
        assert not test_lock.exists()
        driver.run(resume=True, max_batches=1)
        assert calls == ['test-000000', 'test-000032']
    result = read(OUT / (PREFIX + '-result.json'))
    assert result['passed'] and result['deals'] == 64 and result['checkpoint']['completed_deals'] == 64
    assert set(result['routes']) == set(calls)
    assert len({r['attempt'] for r in result['routes'].values()}) == 2
    assert (training_lock.read_bytes() if training_lock.exists() else None) == before
    assert not test_lock.exists()
    from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
    context = json.loads(args['context_source'])
    reference = CompletePolicyComparison(stack=context['config']['stack'], dead_money=context['dead_money'], deals=64)
    for name in calls:
        reference.add(json.loads(fixtures[name]['summary.json'])['values'])
    expected = reference.finish()
    expected['control_only'] = False
    assert read(store / 'analysis.json') == expected
    assert owned_scratch_path(store / ('attempt-' + 'a' * 32) / '.batch-work/test-000000/summary.json', store)
    assert not owned_scratch_path(store / ('attempt-' + 'a' * 32) / 'test-000000.xz', store)
    assert not owned_scratch_path(store.parent / '.batch-work/summary.json', store)
    proof = dict(passed=True, mechanical_driver_only=True, source_registration_sha256=sha(registration),
                 source_result_sha256=sha(OUT / (PREFIX + '-result.json')), deals=64, invocations=2,
                 reused_seed=9267201, calls=calls, distinct_attempts=2,
                 final_statistics_exactly_equal=True, training_lock_unchanged=True,
                 driver_sha256=sha(Path(driver.__file__)), runtime_sha256=sha(Path(__file__).parent / 'weighted_evaluation_runtime_v2.py'),
                 seconds=time.monotonic() - started, gpu_used=False, production_modified=False,
                 accuracy_qualified=False,
                 scope='GPU and admission replaced with old-outcome replay; actual archive workers, checkpoints and controller resume executed. Not full-bank qualification.')
    save(OUT / (PREFIX + '-integration-proof.json'), proof)
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()
