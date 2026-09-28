"""Fixed-input CPU throughput qualification; no new scientific observations."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import argparse
import concurrent.futures
import json
import multiprocessing
from pathlib import Path
import time
import psutil
from board_root_action_decomposition_v1 import (digest, encoded, publish, restore_batch,
    validate_original, force_root, validate_forced, invoke, compare, unlinked)
from weighted_evaluation_readback_v1 import worker_guard
from global_research_inventory_v2 import measure

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'board-root-action-workers-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
CONTROL = Path('S:/GTOpen-research/board-root-action-control-v1')
WORKERS = (1,4,8,12)
STATE = None


def sha(path):
    return digest(Path(path).read_bytes())


def initialize(registration):
    global STATE
    reg = json.loads(Path(registration).read_bytes())
    context = Path(reg['context_path'])
    executable = Path(reg['executable'])
    assert sha(context) == reg['inputs'][str(context)]
    assert sha(executable) == reg['inputs'][str(executable)]
    STATE = reg, context.read_bytes().decode(), context, executable


def work(job):
    workers, index, name = job
    started = time.monotonic()
    reg, source, context, executable = STATE
    def guard():
        assert time.monotonic()-started < 180
        assert psutil.virtual_memory().available > 20_000_000_000
    guard()
    folder = STORE/f'w{workers:02d}-j{index:02d}'
    assert not folder.exists()
    folder.mkdir()
    owner = dict(root=str(folder), parent=str(STORE), workers=workers, index=index, batch=name)
    publish(folder/'owner.json',encoded(owner))
    raw = restore_batch(Path(reg['source_store']),name,reg['routes'][name],guard)
    original, roots, deal_rows, deals = validate_original(raw,source)
    forced = force_root(original,roots);validate_forced(original,forced,roots)
    files = {'conditional-batch.json':raw['conditional-batch.json'], 'forced-profiles.json':encoded(forced)}
    temporary_hashes = {}
    for n,b in files.items():
        publish(folder/n,b);temporary_hashes[n] = digest(b)
    native_seconds = invoke(executable,context,folder/'conditional-batch.json',
        folder/'forced-profiles.json',folder/'native.json',guard)
    saved = json.loads(raw['native.json'])
    values = compare(saved,saved,json.loads((folder/'native.json').read_bytes()),
        original,deal_rows,deals,json.loads(source)['dead_money'])
    expected = CONTROL/name/'action-values.json'
    assert sha(expected) == reg['inputs'][str(expected)]
    assert encoded(values) == expected.read_bytes(), 'Worker changed qualified action values'
    assert sha(folder/'native.json') == reg['expected_native_hashes'][name]
    publish(folder/'action-values.json',encoded(values))
    receipt = dict(name=name,workers=workers,index=index,all_values_exactly_equal=True,
        existing_deals_replayed=32,new_deals=0,maximum_mixture_error=values['maximum_mixture_error'],
        temporary_input_sha256=temporary_hashes,native_sha256=sha(folder/'native.json'),
        action_values_sha256=sha(folder/'action-values.json'),native_seconds=native_seconds,
        total_seconds=time.monotonic()-started,original_native_rerun=False)
    publish(folder/'receipt.json',encoded(receipt))
    # Only two newly owned, verified scratch files are retired. No recursive
    # deletion and no traversal into the original archive or another job.
    assert unlinked(folder).parent == unlinked(STORE)
    assert json.loads((folder/'owner.json').read_bytes()) == owner
    for n,h in temporary_hashes.items():
        path=unlinked(folder/n)
        assert path.parent == folder and sha(path) == h
        path.unlink()
    return receipt


def benchmark(registration, workers, guard):
    started=time.monotonic()
    jobs=[(workers,i,('test-000000','test-032768')[i % 2]) for i in range(12)]
    pool=concurrent.futures.ProcessPoolExecutor(max_workers=workers,
        mp_context=multiprocessing.get_context('spawn'),initializer=initialize,initargs=(str(registration),))
    pending={pool.submit(work,j):j for j in jobs}; rows=[]
    try:
        while pending:
            guard()
            done,_=concurrent.futures.wait(pending,timeout=1,return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                job=pending.pop(future);row=future.result()
                assert (row['workers'],row['index'],row['name']) == job
                rows.append(row)
    except BaseException:
        # Stop only this executor's verified worker families, including native
        # subprocesses, before leaving all completed/incomplete evidence intact.
        for proc in list(pool._processes.values()):
            if proc.is_alive():
                owned=psutil.Process(proc.pid)
                for child in owned.children(recursive=True):
                    try: child.kill()
                    except psutil.NoSuchProcess: pass
                proc.terminate()
        raise
    finally:
        pool.shutdown(wait=True,cancel_futures=True)
    return dict(workers=workers,jobs=12,seconds=time.monotonic()-started,
        rows=sorted(rows,key=lambda r:r['index']))


def main(run):
    if not run:
        print(json.dumps(dict(worker_counts=WORKERS,jobs_per_count=12,new_deals=0,benchmark_not_run=True)))
        return
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        assert time.monotonic()-started < 2400
        if time.monotonic()-last > 2:
            worker_guard()
            assert psutil.disk_usage('S:/').free > 10_000_000_000
            last=time.monotonic()
    guard()
    cpu=psutil.cpu_percent(interval=1)
    assert cpu < 50, 'Yield to substantial existing CPU work'
    pr=OUT/'board-root-action-control-v1-registration.json'
    pp=OUT/'board-root-action-control-v1-result.json'
    review=OUT/'board-root-action-control-v1-review.json'
    result,audit=json.loads(pp.read_bytes()),json.loads(review.read_bytes())
    assert result['passed'] and audit['passed'] and audit['control_result_sha256'] == sha(pp)
    assert audit['control_registration_sha256'] == result['registration_sha256'] == sha(pr)
    assert audit['original_native_replays_exactly_equal'] and audit['non_root_policies_unchanged']
    old_reg=json.loads(pr.read_bytes())
    for p,h in old_reg['inputs'].items(): assert sha(p) == h
    study=json.loads((OUT/'weighted-complete-board-root-study-v1-result.json').read_bytes())
    executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    context=OUT/'bb-context-candidate.json'
    paths=[Path(__file__),pr,pp,review,executable,context,
        ROOT/'tools/research/board_root_action_decomposition_v1.py',
        ROOT/'tools/research/board_root_action_readback_v1.py']
    paths += [CONTROL/n/'action-values.json' for n in ('test-000000','test-032768')]
    assert not STORE.exists()
    rp=OUT/(PREFIX+'-registration.json');assert not rp.exists()
    inventory=measure()
    assert sum(r['allocated_file_bytes'] for r in inventory)+2_000_000_000 < 800_000_000_000
    reg=dict(format=1,inputs={str(p):sha(p) for p in paths},worker_counts=WORKERS,jobs_per_count=12,
        job_sequence=['test-000000','test-032768']*6,context_path=str(context),executable=str(executable),
        source_store=study['store'],routes=old_reg['routes'],
        expected_native_hashes={n:sha(CONTROL/n/'forced-native.json') for n in old_reg['batches']},
        maximum_seconds=2400,global_inventory=inventory,maximum_additional_bytes=2_000_000_000,
        existing_cpu_percent=cpu,gpu_used=False,new_deals=0,
        selection_rule='Lowest elapsed time; choose fewer workers if within 5% of the minimum.',
        interpretation='Operational repeated-input benchmark, not additional scientific samples.')
    publish(rp,encoded(reg));STORE.mkdir()
    publish(STORE/'owner.json',encoded(dict(root=str(STORE),registration_sha256=sha(rp))))
    timings=[]
    try:
        for workers in WORKERS:
            row=benchmark(rp,workers,guard);timings.append(row)
            print(json.dumps({k:v for k,v in row.items() if k != 'rows'}),flush=True)
        best=min(r['seconds'] for r in timings)
        chosen=min(r['workers'] for r in timings if r['seconds'] <= best*1.05)
        for p,h in reg['inputs'].items(): assert sha(p) == h
        report=dict(passed=True,registration_sha256=sha(rp),timings=timings,recommended_workers=chosen,
            exact_values_in_every_job=True,new_deals=0,gpu_used=False,full_replay_launched=False,
            maximum_mixture_error=max(x['maximum_mixture_error'] for r in timings for x in r['rows']),
            seconds=time.monotonic()-started,retained_bytes=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()))
        publish(OUT/(PREFIX+'-result.json'),encoded(report))
        print(json.dumps({k:v for k,v in report.items() if k != 'timings'}),flush=True)
    except BaseException as error:
        publish(OUT/(PREFIX+'-failure.json'),encoded(dict(passed=False,error=repr(error),
            registration_sha256=sha(rp),completed_worker_counts=[r['workers'] for r in timings])))
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
