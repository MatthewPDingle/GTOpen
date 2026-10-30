"""Parallel scheduling only; reuse every frozen scalar review check unchanged."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import concurrent.futures
from collections import deque
import inspect
import multiprocessing
import time
import psutil
import hu_showdown_pipelined_evaluation_review_20260927 as original
from hu_showdown_pipelined_evaluation_review_20260927 import *

PREFIX = 'showdown-parallel-readback-v1'
WORKERS = 8
STATE = None


def initialize(reg, result, source, roots):
    global STATE
    cache = load_complete_cache()
    reader = CompositeEvaluationReader(Path(result['store']), result['archive_manifest_hashes'],
        original_store=reg['original_store'], original_hashes=reg['original_manifest_hashes'],
        total_deals=reg['deals'], guard=lambda: None)
    STATE = reader, Path(result['store']), source, cache, roots


def check_one(job):
    name, batch = job
    reader, store, source, cache, roots = STATE
    return name, verify_batch(reader, store/name, batch, source, cache, roots)


def parallel(jobs, reg, result, source, roots, guard):
    """Bound queued work; propagate failures and preserve input order exactly."""
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS,
        mp_context=multiprocessing.get_context('spawn'), initializer=initialize,
        initargs=(reg, result, source, roots))
    pending = deque()
    jobs = iter(jobs)
    try:
        for _ in range(WORKERS*2):
            item = next(jobs, None)
            if item is None: break
            pending.append((item[0], pool.submit(check_one, item), time.monotonic()))
        while pending:
            guard()
            assert psutil.virtual_memory().available > 20_000_000_000
            name, future, submitted = pending.popleft()
            while True:
                guard()
                assert time.monotonic()-submitted < 300, 'Bounded batch timeout; no retry'
                try:
                    actual, value = future.result(timeout=2)
                    break
                except concurrent.futures.TimeoutError:
                    pass
            assert actual == name
            yield name, value
            item = next(jobs, None)
            if item is not None:
                pending.append((item[0], pool.submit(check_one, item), time.monotonic()))
    except BaseException:
        # Only this executor's children; keep the original reviewer untouched.
        for process in list(pool._processes.values()):
            if process.is_alive(): process.terminate()
        raise
    finally:
        pool.shutdown(wait=True, cancel_futures=True)


def inputs():
    return {str(p.resolve()): sha(p) for p in Path(__file__).parent.glob('*.py')}


def control():
    begin = time.monotonic()
    rp = OUT/f'{PREFIX}-control-registration.json'
    bindings = inputs()
    save(rp, dict(inputs=bindings, workers=WORKERS, batches=16,
        scope='Exact serial versus parallel old-decoder scalar checks; reused completed evidence only.'))
    reg = read(OUT/'showdown-pipelined-evaluation-study-v1-registration.json')
    result = read(OUT/'showdown-pipelined-evaluation-study-v1-result.json')
    source = (OUT/'bb-context-candidate.json').read_text()
    roots = read(Path(result['store'])/'root-stability.json')['root_probabilities']
    sampler = PhysicalDeals(source, mode='full_deck', seed=9267201)
    offsets = set(list(range(0,256,32)) + list(range(19776,20032,32)))
    jobs = []
    for offset in range(0,20032,32):
        deals = sampler.sample(32)['deals']
        if offset in offsets:
            name = f'test-{offset:06d}'
            jobs.append((name, dict(format=2, batch_id=f"{reg['batch_id_prefix']}-{name}",
                seed=0, query_limit=100000, deals=deals)))
    initialize(reg,result,source,roots)
    start = time.monotonic(); serial = [check_one(job) for job in jobs]
    serial_seconds = time.monotonic()-start
    start = time.monotonic(); concurrent = list(parallel(jobs,reg,result,source,roots,lambda: None))
    parallel_seconds = time.monotonic()-start
    assert serial == concurrent
    assert all(value[2] == result['batch_summary_hashes'][name] for name,value in concurrent)
    bad = (jobs[0][0], dict(jobs[0][1], batch_id='deliberately-invalid-control'))
    rejected = False
    try: list(parallel([bad],reg,result,source,roots,lambda: None))
    except AssertionError: rejected = True
    assert rejected
    for p,h in bindings.items(): assert sha(p)==h
    save(OUT/f'{PREFIX}-control-result.json', dict(passed=True,registration_sha256=sha(rp),
        batches=len(jobs),deals=512,workers=WORKERS,serial_seconds=serial_seconds,
        parallel_seconds=parallel_seconds,speedup=serial_seconds/parallel_seconds,
        old_and_new_archive_routes_checked=True, outputs_exactly_equal=True,
        malformed_batch_rejected=rejected,seconds=time.monotonic()-begin,
        production_modified=False,gpu_used=False))
    print(json.dumps(dict(serial_seconds=serial_seconds,parallel_seconds=parallel_seconds,
        speedup=serial_seconds/parallel_seconds)),flush=True)


def study():
    control_result = read(OUT/f'{PREFIX}-control-result.json')
    assert control_result['passed'] and control_result['outputs_exactly_equal']
    assert control_result['malformed_batch_rejected'] and control_result['speedup'] > 1.5
    plan = OUT/'SHOWDOWN-PARALLEL-READBACK-PLAN.md'
    bindings = inputs()
    bindings[str(plan)] = sha(plan)
    for suffix in ('registration','result'):
        p = OUT/f'{PREFIX}-control-{suffix}.json';bindings[str(p)] = sha(p)
    save(OUT/f'{PREFIX}-execution-registration.json',dict(inputs=bindings,workers=WORKERS,
        queue_limit=16,maximum_batch_seconds=300,source_review=str(Path(original.__file__).resolve()),
        scope='All 65536 deals, all original scalar scientific checks and reductions; parallel batch scheduling only.',
        original_reviewer_retained=True,production_modified=False,gpu_used=False))
    # Keep original main's admission, input hashes, chance replay, scalar final
    # statistics and evidence checks verbatim. Only dispatch and output names vary.
    body = inspect.getsource(original.main)
    old = '''        for offset,name in zip(range(0,reg['deals'],32),expected_names):
            guard();deals=sampler.sample(32)['deals'] if sampler else reused[offset:offset+32]
            batch=dict(format=2,batch_id=f"{reg['batch_id_prefix']}-{name}",seed=0,query_limit=100000,deals=deals)
            delta,n,digest=verify_batch(reader,store/name,batch,source,cache,root_policies)
            assert digest==result['batch_summary_hashes'][name];values.extend(delta);observations+=n
            if offset//32%64==0:print(json.dumps(dict(reviewed_deals=offset+32)),flush=True)
'''
    new = '''        def jobs():
            for offset,name in zip(range(0,reg['deals'],32),expected_names):
                guard();deals=sampler.sample(32)['deals'] if sampler else reused[offset:offset+32]
                batch=dict(format=2,batch_id=f"{reg['batch_id_prefix']}-{name}",seed=0,query_limit=100000,deals=deals)
                yield name,batch
        for at,(name,(delta,n,digest)) in enumerate(parallel(jobs(),reg,result,source,root_policies,guard)):
            assert digest==result['batch_summary_hashes'][name];values.extend(delta);observations+=n
            if at%64==0:print(json.dumps(dict(reviewed_deals=(at+1)*32)),flush=True)
'''
    assert body.count(old)==1
    body=body.replace(old,new)
    for suffix in ('readback-registration','independent-review'):
        before="f'{prefix}-"+suffix+".json'"
        assert before in body
        body=body.replace(before,"f'{PREFIX}-"+suffix+".json'")
    namespace=dict(globals())
    exec(compile(body, str(Path(__file__).resolve()), 'exec'),namespace)
    namespace['main']('study')
    proof=read(OUT/f'{PREFIX}-independent-review.json')
    assert proof['passed'] and proof['deals']==65536
    for p,h in bindings.items(): assert sha(p)==h
    save(OUT/f'{PREFIX}-execution-result.json',dict(passed=True,
        execution_registration_sha256=sha(OUT/f'{PREFIX}-execution-registration.json'),
        independent_review_sha256=sha(OUT/f'{PREFIX}-independent-review.json'),
        deals=65536,workers=WORKERS,production_modified=False,gpu_used=False))


if __name__=='__main__':
    assert sys.argv[1:] in (['control'], ['study'])
    control() if sys.argv[1]=='control' else study()
