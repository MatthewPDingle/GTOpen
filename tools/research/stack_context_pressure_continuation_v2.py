"""Continue only authenticated complete cycles after one exact storage stop.

The old failed supervisor and handoff remain evidence. Workers and scientific
pipeline are imported unchanged. This coordinator reduces scheduling only;
it never recovers a partial cycle or launches any scientific evaluation.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
                  OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import time
import traceback
import uuid
import psutil
import stack_context_parallel_continuation_v2 as original
from board_prefix_publication_v1 import atomic_json
from board_study_storage_v1 import measure
from global_research_inventory_v3 import measure as inventory

NAME = 'stack-context-pressure-continuation-v2'
OUT, STORE = original.legacy.OUT, original.legacy.STORE
ARMS = ('A-relative', 'B-relative', 'A-baseline', 'B-baseline')
COUNTS = {'A-baseline':60, 'A-relative':57, 'B-baseline':60, 'B-relative':57}
INVOCATION = '50734e9f930b452f86f401651ff76526'
OLD_PARENT = (106792,1790797645.7329068)
OLD_HELPER = (12064,1790769110.417745)
OLD_WORKERS = {'A-baseline':(46908,1790797923.476029),
    'A-relative':(101848,1790797925.3251064),
    'B-relative':(89924,1790797927.225422),
    'B-baseline':(103456,1790797929.1780753)}
REG_SHA = 'ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'
PRESSURE_ERROR = 'ValueError("Parallel failure requires review: ([], \'Logical cap exceeded\')")'
MAX_LOGICAL, GLOBAL_CAP = 70_000_000_000, 800_000_000_000
MAX_ACTIVE, ARM_TRANSIENT, CYCLE_GROWTH = 2, 8_000_000_000, 250_000_000
PLAN = OUT/'STACK-CONTEXT-PRESSURE-CONTINUATION-V2-PLAN.md'
CONTROL = OUT/(NAME+'-check-result.json')
REVIEW = OUT/(NAME+'-boundary-review-result.json')
READBACK = OUT/(NAME+'-boundary-readback-result.json')
ADMISSION, ATTEMPT, STATUS, RESULT, FAILURE = (OUT/(NAME+s+'.json') for s in
    ('-admission','-attempt','-status','-training-result','-failure'))


def require(ok, message):
    if not ok:raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_bytes())


def encoded(value):
    return (json.dumps(value,separators=(',',':'),allow_nan=False)+'\n').encode()


def save(path,value):
    with Path(path).open('xb') as stream:
        stream.write(encoded(value));stream.flush();os.fsync(stream.fileno())


def prefix_hash(progress,count):
    require(type(count) is int and 1<=count<=progress['completed_cycles']<=64
        and len(progress['updates'])==progress['completed_cycles'], 'Invalid complete prefix')
    require([r['cycle'] for r in progress['updates']]==list(range(1,progress['completed_cycles']+1)),
        'Reordered or repeated cycles')
    require(progress['checkpoint']==progress['updates'][-1]['checkpoint'], 'Detached current checkpoint')
    prefix=dict(progress,completed_cycles=count,checkpoint=progress['updates'][count-1]['checkpoint'],
        updates=progress['updates'][:count])
    return hashlib.sha256(encoded(prefix)).hexdigest()


def validate_failure(failure,finished,outcomes,progress):
    """Recognize this exact operational stop, never a scientific worker failure."""
    require(failure.get('error')==PRESSURE_ERROR and failure.get('invocation')==INVOCATION
        and failure.get('automatic_retry_allowed') is False
        and failure.get('original_registration_sha256')==REG_SHA, 'Unrecognized terminal failure')
    require(finished.get('pid')==OLD_PARENT[0] and finished.get('created')==OLD_PARENT[1]
        and finished.get('phase')=='training' and finished.get('index')==1
        and finished.get('exit_code')==1, 'Wrong definitive failed child outcome')
    require(set(outcomes)==set(progress)==set(COUNTS), 'Four exact successful boundaries required')
    for arm,count in COUNTS.items():
        row,p=outcomes[arm],progress[arm]
        require(row.get('arm')==arm and row.get('pid')==OLD_WORKERS[arm][0]
            and row.get('process_created')==OLD_WORKERS[arm][1] and not row.get('failed')
            and row.get('complete') is False and row.get('stopped_at_complete_boundary') is True,
            'A worker failed or did not stop at a complete boundary')
        require(p.get('registration_sha256')==REG_SHA and p['completed_cycles']>=count
            and prefix_hash(p,count)==row.get('progress_sha256'), 'Changed completed scientific prefix')
    return dict(COUNTS)


def choose_arm(pending,active,counts,logical):
    """Reserve full remaining growth of active arms and scratch before launch.

    Reservations are conservative estimates from retained sizes, not a hard
    mathematical bound. The unchanged 70 GB cap still stops at full boundaries.
    """
    if len(active)>=MAX_ACTIVE:return None
    for arm in pending:
        candidates=[*active,arm]
        require(all(type(counts[a]) is int and 0<=counts[a]<64 for a in candidates),
            'Invalid pending arm horizon')
        growth=sum((64-counts[a])*CYCLE_GROWTH for a in candidates)
        if logical+len(candidates)*ARM_TRANSIENT+growth<=MAX_LOGICAL:return arm
    return None


def assert_absent(identity):
    try:p=psutil.Process(identity[0])
    except psutil.NoSuchProcess:return
    require(abs(p.create_time()-identity[1])>.01, 'Original scientific/observer identity still live')


def clean_owners():
    require(not original.legacy.LOCK.exists() and not original.legacy.OTHER.exists()
        and not (OUT/'stack-context-completion-handoff-v3-owner.json').exists(), 'Existing research owner')
    for identity in (OLD_PARENT,OLD_HELPER,*OLD_WORKERS.values()):assert_absent(identity)


def retired_raw(root):
    # Original retirement retains empty directories; reject remaining files.
    return not any(p.is_file() for p in Path(root).rglob('*'))


def review_actual():
    clean_owners()
    original.known_failure()
    spec=read(original.legacy.REG)
    require(sha(original.legacy.REG)==REG_SHA, 'Changed original registration')
    original.legacy.verify(spec['inputs'])
    control=read(original.CONTROL)
    require(control['complete'] and control['passed']
        and control['runner_sha256']==sha(original.__file__), 'Original worker qualification changed')
    original.legacy.verify(control['inputs'])
    old_inv=STORE/(original.NAME+'-invocation-'+INVOCATION+'.json')
    invocation=read(old_inv)
    require(invocation['pid']==OLD_PARENT[0] and invocation['process_created']==OLD_PARENT[1]
        and sha(old_inv)=='7b9535024ba13abd4254e8aa6598cf9e11e5c6366f257315445b5b05fa3de469',
        'Wrong resource-pressure invocation')
    finished_path=OUT/'stack-context-completion-handoff-v3-001-training-finished.json'
    finished=read(finished_path)
    started_path=OUT/'stack-context-completion-handoff-v3-001-training-started.json'
    started=read(started_path)
    require(started['pid']==finished['pid'] and started['created']==finished['created']
        and started['command']==finished['command'], 'Detached launch/exit evidence')
    logs=[OUT/('stack-context-completion-handoff-v3-001-training-'+s+'.log') for s in ('stdout','stderr')]
    require(all(sha(p)==finished[s+'_sha256'] for p,s in zip(logs,('stdout','stderr'))),
        'Changed definitive child logs')
    helper_failure=OUT/'stack-context-completion-handoff-v3-failure.json'
    h=read(helper_failure)
    require(h['error']=="ValueError('Child failed; no automatic retry: training')"
        and h['automatic_retry_allowed'] is False and h['preserve_evidence'] is True
        and h['production_modified'] is False, 'Unrecognized handoff failure')
    paths={Path(__file__).resolve(),PLAN,original.FAILURE,finished_path,started_path,
        helper_failure,old_inv,original.CONTROL,original.AMENDMENT,Path(original.__file__).resolve(),
        original.legacy.REG,original.legacy.ATTEMPT,*logs}
    outcomes={};progress={};boundaries={};raw_max={};metadata={}
    for arm in COUNTS:
        path=STORE/(original.NAME+'-'+INVOCATION+'-'+arm+'.json')
        outcomes[arm]=read(path);paths.add(path)
        folder=STORE/arm;progress[arm]=read(folder/'progress.json')
        count=progress[arm]['completed_cycles']
        require(count==COUNTS[arm], 'Unexpected post-stop scientific work')
        require(not (folder/f'cycle-{count+1:04d}').exists()
            and not (folder/f'archive-{count+1:04d}').exists(), 'Unpublished next scientific cycle')
        boundaries[arm]=dict(count=count,progress_sha256=sha(folder/'progress.json'),
            checkpoint=progress[arm]['checkpoint'])
        maximum=0;archive_bytes=0
        for cycle,row in enumerate(progress[arm]['updates'],1):
            dest=folder/f'archive-{cycle:04d}'
            require(row['cycle']==cycle and row['archive']==str(dest.relative_to(STORE)), 'Wrong cycle archive')
            require(sha(dest/'index.json')==row['archive_index_sha256']
                and sha(dest/'retired.json')==row['retirement_sha256'], 'Changed archive boundary metadata')
            plan,index,retired=(read(dest/p) for p in ('plan.json','index.json','retired.json'))
            require(plan['owner']==str(STORE) and plan['source']==str(folder/f'cycle-{cycle:04d}')
                and plan['destination']==str(dest) and index['plan_sha256']==sha(dest/'plan.json')
                and retired['index_sha256']==sha(dest/'index.json') and retired['raw_files_remaining']==0,
                'Incomplete retirement/ownership proof')
            require(plan['raw_bytes']==sum(r['bytes'] for r in plan['members'])
                and retired['original_bytes']==plan['raw_bytes'], 'Raw byte accounting differs')
            require(retired_raw(folder/f'cycle-{cycle:04d}'), 'Published raw scratch files were not retired')
            cp=folder/'objects'/row['checkpoint']['file']
            require(sha(cp)==row['checkpoint']['sha256'], 'Changed immutable checkpoint')
            document=read(cp)
            require(document['completed_cycles']==cycle and document['config']==spec['arms'][arm]['config'],
                'Checkpoint scientific config/count differs')
            for p in (dest/'plan.json',dest/'index.json',dest/'retired.json',cp):paths.add(p)
            maximum=max(maximum,plan['raw_bytes']);archive_bytes+=row['packed_bytes']
        raw_max[arm]=maximum;metadata[arm]=dict(archives=count,packed_bytes=archive_bytes)
    validate_failure(read(original.FAILURE),finished,outcomes,progress)
    prepared=read(OUT/'stack-context-population-v1-result.json')
    restored=original.validate_boundaries(spec,prepared,write_receipts=False)
    require(restored==COUNTS, 'Original full checkpoint restoration differs')
    inputs={str(p):sha(p) for p in paths}
    return dict(complete=True,passed=True,original_registration_sha256=REG_SHA,
        operational_pressure_only=True,all_workers_successful_complete_boundaries=True,
        no_unpublished_scientific_cycle=True,old_owners_released=True,failed_evidence_preserved=True,
        original_worker_sha256=sha(original.__file__),inputs=inputs,boundaries=boundaries,
        invocation=INVOCATION,raw_cycle_maxima=raw_max,metadata=metadata,
        logical_bytes=original.logical_bytes(STORE),scientific_fits=0,native_calls=0,
        full_archive_payload_readback=False,production_modified=False,unix=time.time())


def verify_review(*,initial=False):
    check,review,reader=read(CONTROL),read(REVIEW),read(READBACK)
    require(check.get('passed') is True and check.get('complete') is True
        and check['coordinator_sha256']==sha(__file__), 'Unqualified coordinator')
    for record in (check,review,reader):
        require(record.get('passed') is True and record.get('complete') is True, 'Incomplete review')
        original.legacy.verify(record['inputs'])
    require(reader['review_sha256']==sha(REVIEW) and reader['coordinator_sha256']==sha(__file__)
        and reader['all_prefixes_unchanged'] is True and reader['native_calls']==reader['scientific_fits']==0,
        'Independent complete-boundary readback differs')
    progress={a:read(STORE/a/'progress.json') for a in COUNTS}
    outcomes={a:read(STORE/(original.NAME+'-'+INVOCATION+'-'+a+'.json')) for a in COUNTS}
    validate_failure(read(original.FAILURE),read(OUT/'stack-context-completion-handoff-v3-001-training-finished.json'),outcomes,progress)
    if initial:require({a:p['completed_cycles'] for a,p in progress.items()}==COUNTS,
        'Scientific work advanced before operational admission')
    return review


def publish(stage,**values):
    atomic_json(STATUS,dict(stage=stage,pid=os.getpid(),process_created=psutil.Process().create_time(),
        unix=time.time(),**values),replace=True)


def main(run=False):
    if not run:
        print(json.dumps(dict(prepared=True,admitted=ADMISSION.exists(),started=ATTEMPT.exists(),
            complete=RESULT.exists(),failed=FAILURE.exists(),maximum_concurrent_arms=MAX_ACTIVE,
            evaluation_launched=False)));return
    require(not any(p.exists() for p in (ATTEMPT,RESULT,FAILURE,original.RESULT,original.legacy.RESULT)),
        'Existing or terminal attempt: preserve; no automatic retry')
    clean_owners();review=verify_review(initial=True)
    original.legacy.verify(read(original.legacy.REG)['inputs'])
    admitted=read(original.legacy.ATTEMPT)['admitted_unix']
    require(time.time()<admitted+72*3600, 'Original scientific deadline expired')
    ready,gpu=original.legacy.available()
    require(ready and gpu['free_bytes']>=12_000_000_000
        and psutil.virtual_memory().available>=40_000_000_000, 'Resource admission unavailable')
    usage=inventory();allocated=sum(r['allocated_file_bytes'] for r in usage)
    own=measure(STORE)['allocated_file_bytes']
    require(allocated+max(0,MAX_LOGICAL-own)<=GLOBAL_CAP, 'Original global reservation cap exceeded')
    admission=read(ADMISSION)
    original.legacy.verify(admission['inputs'])
    require(admission['boundary_review_sha256']==sha(REVIEW) and admission['readback_sha256']==sha(READBACK)
        and admission['coordinator_sha256']==sha(__file__) and admission['maximum_concurrent_arms']==MAX_ACTIVE
        and admission['logical_reservation']==MAX_LOGICAL and admission['global_allocated_cap']==GLOBAL_CAP
        and admission['original_deadline_unix']==admitted+72*3600
        and admission['scientific_inputs_gates_unchanged'] is True and admission['scientific_cycles_retried'] is False,
        'Operational admission differs')
    spec=read(original.legacy.REG);native={key:original.legacy.ROOT/'target/release/examples'/name
        for key,name in dict(bridge='hu_sampled_allin_history_bridge_v1.exe',
            trace='hu_sampled_action_trace_v2.exe',integration='hu_sampled_profile_allin_evaluation_v1.exe',
            river='hu_river_two_stage_stream_v1.exe',board='hu_fixed_board_tree_v1.exe').items()}
    require(all(sha(p)==spec['inputs'][str(p)] for p in native.values()), 'Changed native worker executable')
    ctx=mp.get_context('spawn');stop=ctx.Event();invocation=uuid.uuid4().hex
    active={};all_processes={};pending=list(ARMS);pressure=None;began=time.monotonic()
    lock=original.legacy.LOCK
    with lock.open('x') as stream:stream.write(str(os.getpid()))
    try:
        save(ATTEMPT,dict(pid=os.getpid(),process_created=psutil.Process().create_time(),unix=time.time(),
            invocation=invocation,admission_sha256=sha(ADMISSION),boundaries=COUNTS,
            original_worker_sha256=sha(original.__file__),production_modified=False))
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        while active or pending:
            counts={a:read(STORE/a/'progress.json')['completed_cycles'] for a in ARMS}
            for arm,p in list(active.items()):
                if p.is_alive():continue
                p.join();require(p.exitcode==0, 'Scientific worker failed: '+arm)
                row=read(STORE/(original.NAME+'-'+invocation+'-'+arm+'.json'))
                require(row.get('complete') is True and not row.get('failed')
                    and counts[arm]==64 and row['progress_sha256']==sha(STORE/arm/'progress.json'),
                    'Worker did not finish actual 64-cycle bank')
                del active[arm]
            logical=original.logical_bytes(STORE)
            if logical>MAX_LOGICAL:pressure='Logical cap exceeded';stop.set()
            if time.monotonic()-began>=12*3600:pressure='Bounded invocation incomplete';stop.set()
            if stop.is_set():
                for p in active.values():p.join()
                require(False,'Operational/scientific stop requires review: '+str(pressure))
            arm=choose_arm(pending,list(active),counts,logical)
            if arm is not None:
                require(time.time()<admitted+72*3600, 'Original scientific deadline expired')
                require(original.legacy.production_available() and not original.legacy.OTHER.exists(),
                    'Production workload has priority')
                p=ctx.Process(target=original.worker,args=(arm,spec,native,stop,invocation),name=arm)
                p.start();active[arm]=p;all_processes[arm]=p;pending.remove(arm)
                save(OUT/(NAME+'-'+arm+'-started.json'),dict(pid=p.pid,
                    process_created=psutil.Process(p.pid).create_time(),arm=arm,invocation=invocation,
                    starts_after_complete_cycle=counts[arm],logical_bytes=logical,unix=time.time()))
            elif not active and pending:require(False,'Insufficient unchanged temporary evidence allowance')
            publish('training',logical_bytes=logical,counts=counts,pending=pending,
                active=[dict(arm=a,pid=p.pid) for a,p in active.items()],maximum_concurrent_arms=MAX_ACTIVE)
            if active:time.sleep(30)
        verify_review();original.legacy.verify(spec['inputs'])
        counts=original.validate_boundaries(spec,read(OUT/'stack-context-population-v1-result.json'))
        require(all(n==64 for n in counts.values()), 'Incomplete final banks')
        for seed in ('A','B'):
            for cycle in range(1,65):
                original.compare_receipts(*(read(STORE/(seed+'-'+rep)/f'chance-{cycle:04d}.json')
                    for rep in ('baseline','relative')))
        terminal=dict(training_complete=True,scientific_evaluation_complete=False,accuracy_qualified=False,
            registration_sha256=REG_SHA,continuation_amendment_sha256=sha(original.AMENDMENT),
            original_failure_sha256=sha(original.legacy.FAILURE),
            resource_pressure_failure_sha256=sha(original.FAILURE),
            resource_pressure_review_sha256=sha(REVIEW),operational_admission_sha256=sha(ADMISSION),
            arms={a:read(STORE/a/'progress.json') for a in original.ARMS},storage=measure(STORE),
            original_scientific_worker_unchanged=True,cycles_retried=False,production_modified=False)
        save(RESULT,terminal);publish('training-complete-consumer-provenance-review-required',counts=counts)
    except BaseException as error:
        stop.set()
        for p in all_processes.values():p.join()
        save(FAILURE,dict(error=repr(error),traceback=traceback.format_exc(),invocation=invocation,
            automatic_retry_allowed=False,preserve_failed_evidence=True,production_modified=False))
        publish('review-required',error=repr(error));raise
    finally:
        if lock.exists() and lock.read_text()==str(os.getpid()):lock.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(run=parser.parse_args().run)
