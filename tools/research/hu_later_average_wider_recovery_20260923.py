"""New, explicitly admitted attempt after the S: volume reserve stop.

Preserves failed evidence and original sample streams/counts. Completed batches
are verified and copied to T:, and only the missing suffix is computed.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_wider_inputs_v1 import admitted
from hu_later_average_wider_study_20260923 import CONFIG, LOCK, OTHER, replace_json
from compressed_research_store_v1 import compressed
from reboot_research_idle_v1 import idle
from wider_root_recovery_v1 import capture

PREFIX = 'later-average-wider-recovery-v1'
STORE = Path('T:/GTOpen-research') / PREFIX
OLD = 'later-average-wider-study-v1'


def verify(reg):
    for p, digest in reg['inputs'].items():
        assert sha(p) == digest, p


def worker(rp, reviewing):
    reg = read(rp)
    verify(reg)
    assert reg['config'] == CONFIG and reg['store'] == str(STORE)
    assert LOCK.read_text().strip() == str(reg['controller_pid'])
    started = time.monotonic()
    limit = reg['review_maximum_seconds'] if reviewing else reg['evaluation_maximum_seconds']
    last = [0.]
    cuda = [False]
    active = ['replaying retained batches' if not reviewing else 'independent readback']
    def guard():
        assert time.monotonic() - started < limit
        if time.monotonic() - last[0] > 2:
            assert idle() and psutil.virtual_memory().available > 20_000_000_000
            assert shutil.disk_usage('T:/').free > 40_000_000_000
            if cuda[0]:
                assert torch.cuda.mem_get_info()[0] > 3_000_000_000
            replace_json(OUT / f'{PREFIX}-progress.json', dict(
                stage='readback' if reviewing else 'evaluation', worker_pid=os.getpid(),
                seconds=time.monotonic()-started, active_batch=active[0], production_modified=False))
            last[0] = time.monotonic()
    guard()
    folder = STORE / 'evaluation'
    if reviewing:
        from wider_root_readback_v1 import review
        previous = read(OUT / f'{PREFIX}-evaluation.json')
        assert previous['complete'] and previous['registration_sha256'] == sha(rp)
        assert previous['result_sha256'] == sha(folder / 'result.json')
        result = review(OUT / 'bb-context-candidate.json', folder, CONFIG,
                        reg['exact'], reg['cache_sha256'], guard)
        assert result['passed']
        verify(reg)
        result.update(registration_sha256=sha(rp),
            evaluation_sha256=sha(OUT / f'{PREFIX}-evaluation.json'),
            seconds=time.monotonic()-started)
        save(OUT / f'{PREFIX}-independent-review.json', result)
        print(dict(readback_passed=True, seconds=result['seconds']), flush=True)
        return
    data = admitted()
    assert data['exact'] == reg['exact'] and data['policy_sha256'] == reg['policy_sha256']
    assert data['checkpoint'] == reg['checkpoint'] and data['cache'].sha256 == reg['cache_sha256']
    import torch
    from sampled_visible_hybrid_gpu_bank_v1 import VisibleHybridCudaBank64
    from wider_root_recovery_v1 import run
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    cuda[0] = True
    bank = VisibleHybridCudaBank64(data['models'], data['weights'],
        context_source=data['context_source'], models_per_chunk=8, guard=guard)
    class VisibleOnly:
        def average(self, q, *, guard):
            batch = json.loads(q['batch_source'])
            assert batch['format'] == 2 and not any(k.startswith('allin_') or k == 'terminal_estimator' for k in batch)
            active[0] = batch['batch_id']
            guard()
            return bank.average(q, guard=guard)
    result, transport = run(data['context_path'], VisibleOnly(), data['cache'],
        reg['exact'], CONFIG, folder, guard, reg['recovery_manifest'])
    assert result['complete'] and result['training_deals'] == 43264 and result['test_deals'] == 131072
    assert result['training_counts'] == [256] * 169
    assert len(transport['reused_batches']) == reg['reused_batches']
    assert len(transport['computed_batches']) == reg['remaining_batches']
    logical = 0
    for p in folder.rglob('*'):
        guard()
        assert not p.is_symlink()
        if p.is_file():
            logical += p.stat().st_size
    assert logical < reg['maximum_logical_bytes']
    verify(reg)
    save(OUT / f'{PREFIX}-evaluation.json', dict(complete=True,
        registration_sha256=sha(rp), result_sha256=sha(folder/'result.json'),
        transport=transport, logical_bytes=logical, intervals=result['intervals'],
        stability=result['stability'], phase_timings=result['phase_timings'],
        seconds=time.monotonic()-started, accuracy_qualified=False, production_modified=False))
    print(dict(evaluation_complete=True, seconds=time.monotonic()-started), flush=True)


def main():
    started = time.monotonic()
    assert idle() and not LOCK.exists() and not OTHER.exists() and not STORE.exists()
    oldrp, oldsp = [OUT / f'{OLD}-{s}.json' for s in ('registration', 'status')]
    oldreg, oldstatus = read(oldrp), read(oldsp)
    assert oldstatus['state'] == 'stopped' and oldstatus['error'] == 'AssertionError()'
    assert not psutil.pid_exists(oldreg['controller_pid'])
    assert not (OUT / f'{OLD}-result.json').exists()
    assert not (Path(oldreg['store']) / 'evaluation/result.json').exists()
    assert oldreg['config'] == CONFIG
    maximum_logical = 105_000_000_000
    assert shutil.disk_usage('T:/').free > 2 * maximum_logical + 40_000_000_000
    controlrp, controlpp = [OUT / f'wider-root-recovery-control-v1-{s}.json' for s in ('registration', 'result')]
    control = read(controlpp)
    assert control['passed'] and control['registration_sha256'] == sha(controlrp)
    assert control['original_nontiming_result_fields_identical'] and control['independent_readback']['passed']
    assert len(control['corruptions_rejected']) == 3
    verify(oldreg)
    data = admitted()
    assert data['exact'] == oldreg['exact'] and data['checkpoint'] == oldreg['checkpoint']
    assert data['policy_sha256'] == oldreg['policy_sha256'] and data['cache'].sha256 == oldreg['cache_sha256']
    manifest = capture(Path(oldreg['store']) / 'evaluation', CONFIG, lambda: None)
    assert manifest['completed_deals'] == dict(train=43264, test=34752)
    assert len(manifest['batches']) == 1219
    inputs = dict(oldreg['inputs'])
    for p in (oldrp, oldsp, controlrp, controlpp, Path(__file__),
              ROOT/'tools/research/wider_root_recovery_v1.py',
              OUT/'WIDER-RESPONSE-RECOVERY-PLAN.md'):
        inputs[str(p.resolve())] = sha(p)
    reg = dict(inputs=inputs, controller_pid=os.getpid(), config=CONFIG, store=str(STORE),
        exact=oldreg['exact'], checkpoint=oldreg['checkpoint'], policy_sha256=oldreg['policy_sha256'],
        cache_sha256=oldreg['cache_sha256'], recovery_manifest=manifest,
        reused_batches=1219, remaining_batches=1505,
        evaluation_maximum_seconds=oldreg['evaluation_maximum_seconds']-oldstatus['seconds'],
        review_maximum_seconds=7200, original_elapsed_seconds=oldstatus['seconds'],
        maximum_logical_bytes=maximum_logical, disk_reserve_bytes=40_000_000_000,
        storage_admission='Twice the 105 GB uncompressed logical cap plus 40 GB reserve; no compression savings assumed.',
        stopping='Original fixed sample count and final look only; combined original/recovery evaluation time <= 12h. Stop on first failure; no automatic restart.',
        scope=oldreg['scope'], production_modified=False)
    rp = OUT / f'{PREFIX}-registration.json'
    save(rp, reg)
    del data
    acquired = False
    child = None
    stages = []
    resources = []
    error = None
    def status(state, **extra):
        replace_json(OUT / f'{PREFIX}-status.json', dict(state=state,
            controller_pid=os.getpid(), stages=stages, seconds=time.monotonic()-started,
            production_modified=False, **extra))
    try:
        with LOCK.open('x') as f:
            f.write(str(os.getpid()))
        acquired = True
        STORE.mkdir()
        assert not compressed(STORE), 'Recovery must not depend on NTFS compression'
        for label, flag, limit in [('evaluation', '--worker', reg['evaluation_maximum_seconds']),
                                   ('readback', '--review', 7200)]:
            verify(reg)
            before = time.monotonic()
            with (OUT / f'{PREFIX}-{label}.log').open('x') as stream:
                child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), flag, str(rp)],
                    cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
                status('running', stage=label, worker_pid=child.pid)
                while child.poll() is None:
                    assert time.monotonic()-before < limit and idle()
                    host, disk = psutil.virtual_memory().available, shutil.disk_usage('T:/').free
                    assert host > 20_000_000_000 and disk > 40_000_000_000
                    resources.append(dict(stage=label, seconds=time.monotonic()-started,
                        free_host_bytes=host, free_disk_bytes=disk))
                    replace_json(OUT / f'{PREFIX}-resources.json', resources)
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
            stages.append(dict(stage=label, exit_code=child.returncode, seconds=time.monotonic()-before))
            assert child.returncode == 0, f'{label} failed; retain all artifacts'
            print(stages[-1], flush=True)
        verify(reg)
        audit = read(OUT / f'{PREFIX}-independent-review.json')
        evaluation = read(OUT / f'{PREFIX}-evaluation.json')
        assert audit['passed'] and audit['registration_sha256'] == evaluation['registration_sha256'] == sha(rp)
        assert audit['evaluation_sha256'] == sha(OUT / f'{PREFIX}-evaluation.json')
        save(OUT / f'{PREFIX}-result.json', dict(passed=True, registration_sha256=sha(rp),
            stages=stages, intervals=evaluation['intervals'], stability=evaluation['stability'],
            seconds=time.monotonic()-started, original_elapsed_seconds=oldstatus['seconds'],
            accuracy_qualified=False, production_modified=False, scope=reg['scope']))
    except BaseException as exc:
        error = repr(exc)
        raise
    finally:
        if child is not None and child.poll() is None:
            subprocess.run(['taskkill', '/PID', str(child.pid), '/T', '/F'], capture_output=True,
                timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
            child.wait(timeout=30)
        status('stopped' if error else 'complete', error=error)
        if acquired:
            assert LOCK.read_text().strip() == str(os.getpid())
            LOCK.unlink()


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] in ('--worker', '--review'):
        worker(Path(sys.argv[2]), sys.argv[1] == '--review')
    elif sys.argv[1:] == ['--run']:
        main()
    else:
        raise SystemExit('Use --run for the explicitly admitted recovery attempt.')
