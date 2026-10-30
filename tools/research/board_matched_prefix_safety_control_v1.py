"""Fault-inject the prefix runner's storage/publication/restart orchestration.

Real Windows files and measurements, tiny deterministic fake training states.
No CUDA, native poker calls, real research locks, or playing-strength outcomes.
This qualifies orchestration only, not trained-state correctness.
"""
import contextlib
import copy
import io
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import time
from unittest.mock import patch
import numpy as np
import psutil
import board_matched_prefix_v2 as runner
import board_prefix_publication_v1 as publication
import hu_root_retained_storage_admitted_study_20260924 as global_storage
from board_study_storage_v1 import create, measure
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save

PREFIX = 'board-matched-prefix-safety-control-v1'
STORE = Path('S:/GTOpen-research') / PREFIX


def expect_error(function, error_type, text):
    try:
        function()
    except error_type as error:
        assert text in str(error), repr(error)
    else:
        raise AssertionError('Expected fault did not reject the operation')


def marker_checks():
    folder = STORE / 'markers'; folder.mkdir()
    final = folder / 'result.json'; document = dict(passed=True, registration_sha256='fixture')
    # Failure midway through serialization must never expose a final marker.
    def interrupted(value, stream, **kwargs):
        stream.write('{"passed":'); raise OSError('injected partial write')
    with patch.object(publication.json, 'dump', side_effect=interrupted):
        expect_error(lambda: publication.atomic_json(final, document), OSError, 'partial write')
    assert not final.exists() and len(list(folder.glob('.partial-*'))) == 1
    publication.atomic_json(final, document)
    before = final.read_bytes()
    with patch.object(publication.os, 'replace', side_effect=OSError('injected rename failure')):
        expect_error(lambda: publication.atomic_json(final, dict(document, newer=True), replace=True),
                     OSError, 'rename failure')
    assert final.read_bytes() == before
    expect_error(lambda: publication.atomic_json(final, document), FileExistsError, 'result.json')
    publication.atomic_json(final, dict(document, newer=True), replace=True)
    assert publication.completion(final, 'fixture')['newer']
    expect_error(lambda: publication.completion(final, 'different', resume=True), ValueError, 'mismatch')
    corrupt = folder / 'legacy-result.json'; corrupt.write_bytes(b'{"passed":')
    original = sha(corrupt)
    expect_error(lambda: publication.completion(corrupt, 'fixture'), ValueError, 'explicit resume')
    recovered = []
    assert publication.completion(corrupt, 'fixture', resume=True, recovered=recovered) is None
    assert len(recovered) == 1 and sha(recovered[0]['preserved_path']) == original
    publication.atomic_json(corrupt, document)
    assert publication.completion(corrupt, 'fixture') == document
    return dict(partial_write_preserved=True, failed_replacement_preserved_previous=True,
                new_marker_refuses_overwrite=True, wrong_registration_rejected=True,
                malformed_marker_preserved_before_recovery=True)


def quota_checks():
    folder = STORE / 'quota'; folder.mkdir()
    (folder / 'artifact.bin').write_bytes(np.random.default_rng(9272710).bytes(131072))
    observed = measure(folder)
    for key, field in (('allocated_file_bytes', 'maximum_allocated_bytes'),
                       ('logical_bytes', 'maximum_logical_bytes')):
        limits = dict(maximum_allocated_bytes=10_000_000, maximum_logical_bytes=10_000_000)
        limits[field] = observed[key] - 1
        expect_error(lambda: publication.storage_boundary(folder, limits, 'after-write'), RuntimeError, key)
        limits[field] = observed[key]
        publication.storage_boundary(folder, limits, 'exact-boundary')
        expect_error(lambda: publication.storage_boundary(folder, limits, 'reserve', reserve_bytes=1),
                     RuntimeError, key)
    return dict(real_measurement=observed, allocation_and_logical_overage_rejected=True,
                required_reserve_enforced=True)


def orchestration(name, *, quota_stage=None, quota_field=None, fail_marker=None):
    folder = STORE / name; folder.mkdir()
    out = folder / 'metadata'; out.mkdir()
    study = folder / 'study'
    fake_root = folder / 'repo'; examples = fake_root / 'target/release/examples'; examples.mkdir(parents=True)
    for exe in ('hu_sampled_allin_bridge_v3.exe', 'hu_sampled_action_trace_v2.exe',
                'hu_sampled_profile_allin_evaluation_v1.exe', 'hu_fixed_board_tree_v1.exe'):
        (examples / exe).write_text('Never executed. Orchestration fixture only.')
    for upstream in ('weighted-complete-evaluation-queue-v1', 'board-training-pipeline-queue-v2'):
        rp = out / f'{upstream}-registration.json'; save(rp, dict(inputs={}))
        save(out / f'{upstream}-result.json', dict(passed=True, registration_sha256=sha(rp)))
    cfg = dict(torch_version='fixture', numpy_version=np.__version__, board_root={}, allin_cache_sha256='fixture')
    arms = [dict(name=f'arm-{i}', control=f'control-{i}', config=copy.deepcopy(cfg)) for i in range(2)]
    calls = []; fault_enabled = True; boundaries = []
    def update(destination, objects, state, config, **kwargs):
        destination.mkdir()
        state['completed_iterations'] += 1
        (destination / 'mock-checkpoint.bin').write_bytes(np.random.default_rng(9272711).bytes(32768))
        calls.append((kwargs['batch_prefix'], state['completed_iterations'], destination.name))
        metric = dict(checkpoint=copy.deepcopy(state), subbatches=[state['completed_iterations']],
                      seconds=0., timings={})
        save(destination / 'metrics.json', metric)
        return metric
    def bounded(store, registration, stage, **kwargs):
        boundaries.append(stage)
        if fault_enabled and quota_stage and quota_stage in stage:
            registration = dict(registration)
            key = 'allocated_file_bytes' if quota_field == 'maximum_allocated_bytes' else 'logical_bytes'
            registration[quota_field] = measure(store)[key] - 1
        return publication.storage_boundary(store, registration, stage, **kwargs)
    real_atomic = publication.atomic_json
    def atomic(path, value, **kwargs):
        if fault_enabled and fail_marker and Path(path).name == fail_marker:
            with patch.object(publication.os, 'rename', side_effect=OSError('injected publication failure')):
                return real_atomic(path, value, **kwargs)
        return real_atomic(path, value, **kwargs)
    fake_torch = SimpleNamespace(__version__='fixture', cuda=SimpleNamespace(is_available=lambda: True,
        mem_get_info=lambda: (24_000_000_000, 24_000_000_000)), set_num_threads=lambda n: None,
        use_deterministic_algorithms=lambda b: None, backends=SimpleNamespace(
            cuda=SimpleNamespace(matmul=SimpleNamespace(allow_tf32=False)), cudnn=SimpleNamespace(allow_tf32=False)))
    result_path = out / f'{runner.PREFIX}-result.json'
    lock = folder / 'running.lock'
    patches = [patch.object(runner, 'OUT', out), patch.object(runner, 'ROOT', fake_root),
        patch.object(runner, 'STORE', study), patch.object(runner, 'LOCK', lock),
        patch.object(runner, 'OTHER', folder / 'other.lock'),
        patch.object(runner, 'specification', return_value=(arms, [], {}, {})),
        patch.object(runner, 'qualifications', return_value=([], [])),
        patch.object(runner, 'safe_read_only_resources', return_value=True),
        patch.object(runner.psutil, 'cpu_percent', return_value=0),
        patch.object(runner.psutil, 'virtual_memory', return_value=SimpleNamespace(available=100_000_000_000)),
        patch.object(runner.psutil, 'disk_usage', return_value=SimpleNamespace(free=100_000_000_000)),
        patch.object(runner.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='0, 24000')),
        # Directory confinement and real allocation scans remain active; skip compact.exe only.
        patch.object(runner, 'create', side_effect=lambda p: p.mkdir()),
        patch.object(runner, 'initialize', side_effect=lambda *a, **k: dict(completed_iterations=0)),
        patch.object(runner.checkpoint, 'save_checkpoint', side_effect=lambda o, s, c, **k: copy.deepcopy(s)),
        patch.object(runner.checkpoint, 'restore_checkpoint', side_effect=lambda o, r, c, **k: copy.deepcopy(r)),
        patch.object(runner, 'compare_states', side_effect=lambda a, b: expect_equal(a, b)),
        patch.object(runner, 'load_complete_cache', return_value=SimpleNamespace(sha256='fixture')),
        patch.object(runner, 'update', side_effect=update), patch.object(runner, 'storage_boundary', side_effect=bounded),
        patch.object(runner, 'atomic_json', side_effect=atomic),
        patch.object(global_storage, 'measure', return_value=[dict(allocated_file_bytes=0)]),
        patch.dict(sys.modules, torch=fake_torch)]
    with contextlib.ExitStack() as stack:
        for item in patches: stack.enter_context(item)
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        if quota_stage:
            expect_error(lambda: runner.main(run=True), RuntimeError, 'exceeds')
            assert not result_path.exists() and not lock.exists()
            progress = read(study / 'arm-0/progress.json')
            if quota_stage == 'after-generation-1': assert progress['completed'] == 0
            if 'replay' in quota_stage: assert not (study / 'arm-0/restart-replay.json').exists()
        elif fail_marker:
            expect_error(lambda: runner.main(run=True), OSError, 'publication failure')
            assert not result_path.exists() and not lock.exists()
            partials = list(folder.rglob('.partial-*')); hashes = {str(p): sha(p) for p in partials}
            assert hashes
            generation_calls = [c for c in calls if c[2].startswith('generation-')]
            fault_enabled = False
            runner.main(run=True, resume=True)
            assert all(sha(p) == h for p, h in hashes.items())
            if fail_marker.endswith('-result.json'):
                assert len(calls) == 6 and len(generation_calls) == 4
            else:
                assert len(calls) == 7 and len([c for c in calls if c[2].startswith('generation-')]) == 4
            assert read(result_path)['passed'] and not lock.exists()
        else:
            runner.main(run=True)
            result = read(result_path)
            assert result['passed'] and len(calls) == 6 and not lock.exists()
            assert len(result['arms']) == 2 and result['measurement']['stage'] == 'before-success-publication'
            expect_error(lambda: runner.main(run=True, resume=True), AssertionError, 'Preserve completed prefix')
            assert not lock.exists()
    return dict(case=name, update_calls=len(calls), boundary_checks=boundaries,
                result_published=result_path.exists(), mock_training=True)


def expect_equal(a, b):
    assert a == b


def main():
    began = time.monotonic()
    assert psutil.cpu_percent(interval=.2) < 50 and psutil.virtual_memory().available > 28_000_000_000
    assert not STORE.exists()
    inputs = {str(p): sha(p) for p in (Path(__file__).resolve(), Path(runner.__file__),
              Path(publication.__file__), Path(__file__).with_name('board_study_storage_v1.py'))}
    rp = OUT / f'{PREFIX}-registration.json'
    save(rp, dict(inputs=inputs, store=str(STORE), maximum_seconds=120, maximum_logical_bytes=10_000_000,
                 scope='Fault-injected orchestration with mocked poker/GPU state; actual Windows storage and publication.',
                 gpu_used=False, training_started=False, production_modified=False))
    create(STORE)
    markers = marker_checks(); quota = quota_checks(); cases = [orchestration('normal')]
    for stage in ('after-generation-1', 'before-replay', 'after-replay', 'before-success-publication'):
        for field in ('maximum_allocated_bytes', 'maximum_logical_bytes'):
            cases.append(orchestration(stage + '-' + field, quota_stage=stage, quota_field=field))
    cases.append(orchestration('interrupted-replay', fail_marker='restart-replay.json'))
    cases.append(orchestration('interrupted-result', fail_marker=f'{runner.PREFIX}-result.json'))
    for p, h in inputs.items(): assert sha(p) == h
    allocation = measure(STORE)
    assert allocation['logical_bytes'] < 10_000_000 and time.monotonic() - began < 120
    result = dict(passed=True, registration_sha256=sha(rp), markers=markers, quota=quota, cases=cases,
                  measurement=allocation, seconds=time.monotonic()-began, gpu_used=False,
                  training_started=False, production_modified=False,
                  limitation='Qualifies failure handling only. Genuine GPU training and independent trained-state audits remain required.')
    save(OUT / f'{PREFIX}-result.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__': main()
