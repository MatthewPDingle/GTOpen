"""Read-only audit of the interrupted parallel invocation; never resumes it."""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import hashlib
import json
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor
import psutil
import stack_context_parallel_continuation_v2 as run

legacy = run.legacy
OUT, STORE = legacy.OUT, legacy.STORE
NAME = 'stack-context-parallel-interruption-audit-v1'
IDENTITIES = {75720:1790747932.4205804, 98836:1790747994.7217212,
    100152:1790747997.5592933, 94212:1790748000.4328887, 83740:1790748003.4320004}


def read(p):
    return json.loads(Path(p).read_bytes())


def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, sort_keys=True); f.write('\n')


def absent():
    for pid, created in IDENTITIES.items():
        try:
            p = psutil.Process(pid)
            assert abs(p.create_time()-created) > .01, 'Original research process is still live'
        except psutil.NoSuchProcess:
            pass
    assert legacy.LOCK.read_text().strip() == '75720' and not legacy.OTHER.exists()
    assert not run.FAILURE.exists() and not run.RESULT.exists()


def main():
    began = time.monotonic(); absent()
    attempt = OUT/(NAME+'-attempt.json'); result = OUT/(NAME+'-result.json')
    assert not attempt.exists() and not result.exists()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    spec = read(legacy.REG); legacy.verify(spec['inputs'])
    prepared = read(OUT/'stack-context-population-v1-result.json')
    proofs = [Path(__file__).resolve(), legacy.REG, legacy.ATTEMPT, run.AMENDMENT, run.STATUS,
        legacy.LOCK, OUT/'stack-context-parallel-resource-readmission-v1.json',
        OUT/'stack-context-parallel-resource-readmission-v1-stdout.log',
        OUT/'stack-context-parallel-resource-readmission-v1-stderr.log']
    proofs.extend(OUT/(run.NAME+'-'+a+'-status.json') for a in run.ARMS)
    proofs.extend(STORE/a/'progress.json' for a in run.ARMS)
    bindings = {str(p):sha(p) for p in proofs}
    save(attempt, dict(unix=time.time(),original_process_identities=IDENTITIES,inputs=bindings,
        read_only_scientific_store=True,new_native_calls=False,new_fits=False,maximum_seconds=1200))
    roots = []; arms = {}
    for arm in run.ARMS:
        folder = STORE/arm; progress = read(folder/'progress.json'); n = progress['completed_cycles']+1
        rt = run.runtime_for(arm,spec,prepared); cfg = spec['arms'][arm]['config']
        prior = legacy.checkpoint.restore_checkpoint(folder/'objects', progress['checkpoint'],cfg,rt['registry'],rt['resources'])
        assert prior['completed_cycles'] == n-1
        raw, arc = folder/f'cycle-{n:04d}', folder/f'archive-{n:04d}'
        assert raw.is_dir(); roots.append(raw)
        if arc.exists(): roots.append(arc)
        metric = raw/'metrics.json'
        state = dict(published_cycles=n-1,interrupted_cycle=n,raw=str(raw),archive=str(arc),
            prior_checkpoint_restored=True,complete_metric=metric.exists(),archive_index=(arc/'index.json').exists(),
            archive_retired=(arc/'retired.json').exists(),contexts=[])
        if metric.exists():
            m = read(metric)
            recovered = legacy.checkpoint.restore_checkpoint(folder/'objects',m['checkpoint'],cfg,rt['registry'],rt['resources'])
            assert m['used_model'] == prior['next_model'] and recovered['completed_cycles'] == n
            assert recovered['next_model'] == m['next_model'] and recovered['played_bank'][-1] == prior['next_model']
            state.update(complete_checkpoint_restored=True,metric_sha256=sha(metric),checkpoint=m['checkpoint'])
        for key in rt['registry'].fit_contexts:
            context = raw/key; batches = sorted(context.glob('batch-*'))
            state['contexts'].append(dict(key=key,exists=context.exists(),collection=(context/'collection.json').exists(),
                batches=len(batches),published_workers=sum((p/'worker-result.json').exists() for p in batches),
                board_result=(context/'board-targets/board-000/result.json').exists()))
        arms[arm] = state
    paths = sorted(p for root in roots for p in root.rglob('*') if p.is_file())
    assert len(paths) == len(set(paths))
    def capture(p):
        assert time.monotonic()-began < 1200
        assert p.is_absolute() and p.resolve() == p and p.is_relative_to(STORE)
        for parent in (p,*p.parents): assert not parent.lstat().st_file_attributes & 0x400
        before = p.stat(); digest = sha(p); after = p.stat()
        assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
        return dict(path=str(p),bytes=after.st_size,mtime_ns=after.st_mtime_ns,
            birth_ns=after.st_birthtime_ns,sha256=digest)
    with ThreadPoolExecutor(max_workers=4) as pool:
        files = list(pool.map(capture,paths))
    identities = {r['path']:r['sha256'] for r in files}; verified_workers=0
    for p in paths:
        if p.name != 'worker-result.json': continue
        record = read(p)
        for name, expected in record['artifacts'].items():
            artifact = p.parent/name
            assert artifact.resolve().is_relative_to(p.parent.resolve())
            assert identities[str(artifact)] == expected, str(artifact)
        verified_workers += 1
    absent()
    for p,h in bindings.items(): assert sha(p) == h, p
    assert not run.torch.cuda.is_initialized()
    value = dict(complete=True,read_only_audit_passed=True,unix=time.time(),seconds=time.monotonic()-began,
        attempt_sha256=sha(attempt),original_processes_absent=True,os_reboot_since_launch=psutil.boot_time()>1790747932.4205804,
        termination_cause='Not established; original processes absent without their normal outcome/failure files.',
        arms=arms,files=files,hashed_files=len(files),hashed_logical_bytes=sum(r['bytes'] for r in files),
        authenticated_worker_results=verified_workers,stale_lock_preserved=True,scientific_inputs_modified=False,
        scientific_retries=0,cuda_initialized=False,partial_cycle_recovery_qualified=False,production_modified=False)
    save(result,value)
    print(json.dumps({k:v for k,v in value.items() if k not in ('files','arms')}),flush=True)
    for arm, row in arms.items(): print(json.dumps(dict(arm=arm,**row)),flush=True)


if __name__ == '__main__': main()
