"""Frozen serial/concurrent replay; parent-owned process tree and fixed oracles."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  CUBLAS_WORKSPACE_CONFIG=':4096:8', PYTHONDONTWRITEBYTECODE='1')
import argparse
import gc
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import uuid
import numpy as np
import psutil
import river_matched_training_pilot_v1 as pilot
import eight_worker_full_update_control_v1 as prior
import training_preparation_full_update_control_v1 as qualified
from board_training_pipeline_preparation_v1 import update as baseline_update
from river_training_pipeline_preparation_v1 import update as river_update
from visible_features_vector_gpu_control_v1 import metric_math
from owned_windows_job_v1 import OwnedJob

ROOT=pilot.ROOT; OUT=pilot.OUT; NAME='two-arm-training-throughput-control-v1'
SELF=Path(__file__).resolve(); STORE=Path('S:/GTOpen-research')/NAME
REG=OUT/(NAME+'-registration.json'); RESULT=OUT/(NAME+'-result.json')
STATUS=OUT/(NAME+'-status.json'); PLAN=OUT/'TWO-ARM-TRAINING-THROUGHPUT-PLAN.md'
LIMIT=12_000_000_000; RESERVE=2_000_000_000; SECONDS=3600; CHILD_SECONDS=1200
CUDA_PER_CHILD=2_000_000_000
CASES={'serial-baseline':'A-baseline', 'serial-river':'A-river',
       'concurrent-baseline':'A-baseline', 'concurrent-river':'A-river'}
GROUPS=(('serial-baseline',), ('serial-river',), ('concurrent-baseline','concurrent-river'))
QUALIFIED_SHA='5d8c3f22a6270ee95111e3e8c32a50828cfdac4bcf2e253fd5b295661ab282ef'
JOB_SHA='00f0405a61c96770a3e82c3f1fd504f2014b9b1717945d449bc1657975b6fb5c'


def identity(pid=None):
    p=psutil.Process(pid);return dict(pid=p.pid,created=p.create_time())


def alive(who):
    try:return psutil.Process(who['pid']).create_time()==who['created']
    except psutil.NoSuchProcess:return False


def specification():
    base=qualified.specification(require_ready=True)
    assert pilot.sha(qualified.RESULT)==QUALIFIED_SHA
    proof=pilot.read(qualified.RESULT)
    assert proof['passed'] and proof['complete'] and proof['registration_sha256']==pilot.sha(qualified.REG)
    jr=OUT/'owned-windows-job-control-v2-registration.json'
    jp=OUT/'owned-windows-job-control-v2-result.json';job=pilot.read(jp)
    assert pilot.sha(jr)==JOB_SHA and job['passed'] and job['registration_sha256']==JOB_SHA
    assert job['owner_exit_cleanup'] and job['unrelated_test_process_survived']
    pilot.verify(pilot.read(jr)['inputs'])
    inputs=dict(base['inputs'])
    paths=[SELF,PLAN,qualified.REG,qualified.RESULT,jr,jp]
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(ROOT) and Path(path).suffix=='.py':paths.append(Path(path))
    inputs.update({str(p):pilot.sha(p) for p in paths});pilot.verify(inputs)
    return dict(format=1,inputs=inputs,oracles=base['oracles'],cases=CASES,groups=GROUPS,
        parent=identity(),source_boundary=78,output_boundary=79,physical_workers_per_arm=8,
        board_workers_per_arm=4,maximum_arm_coordinators=2,cuda_budget_bytes_per_arm=CUDA_PER_CHILD,
        maximum_combined_cuda_budget_bytes=2*CUDA_PER_CHILD,external_vram_headroom_bytes=2_000_000_000,
        idle_gpu_utilization_below=65,maximum_seconds=SECONDS,maximum_child_seconds=CHILD_SECONDS,
        maximum_new_bytes=LIMIT,reserve_bytes=RESERVE,global_allocated_cap=pilot.GLOBAL_LIMIT,
        production_modified=False,new_evaluation_deals=0,fresh_training_deals=0,accuracy_claim=False,
        timing='All setup before readiness; externally timed identical update calls. Both concurrent calls finish before either verification starts.',
        limitation='One serial pair followed by one concurrent pair, one A-seed context; descriptive throughput only.')


def child(case):
    started=time.monotonic();folder=STORE/case
    reg=pilot.read(REG);reg_sha=pilot.sha(REG);parent=reg['parent']
    def ownership():
        assert time.monotonic()-started<CHILD_SECONDS,'Child invocation deadline'
        assert alive(parent),'Parent exited'
        assert not (STORE/'cancel.json').exists(),'Parent cancelled'
        assert pilot.LOCK.read_text()==str(parent['pid']),'Parent lock changed'
    def wait_marker(name):
        while not (folder/name).exists():ownership();time.sleep(.1)
        value=pilot.read(folder/name)
        assert value['registration_sha256']==reg_sha
        assert value['child']==identity()
        ownership();return value
    # No workers or CUDA context before assignment to the parent's OS job.
    wait_marker('permit.json');pilot.verify(reg['inputs'])
    pilot.STORE=STORE;pilot.STATUS=folder/'status.json';pilot.LIMIT=LIMIT
    pilot.CUDA_BUDGET_BYTES=CUDA_PER_CHILD
    import torch
    assert torch.cuda.is_available()
    torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    torch.cuda.set_per_process_memory_fraction(CUDA_PER_CHILD/torch.cuda.get_device_properties(0).total_memory)
    resources=pilot.Guard()
    def guard():ownership();resources();ownership()
    try:
        guard();original=pilot.read(prior.PILOT_REG);name=CASES[case]
        arm=dict(original['arms'][name],name=name);cfg=arm['config']
        assert cfg['torch_version']==torch.__version__ and cfg['numpy_version']==np.__version__
        source=pilot.CONTEXT.read_text();matrix=pilot.AllinMatrix(pilot.read(pilot.MATRIX),source)
        args=dict(context_source=source,catalog_source=pilot.CATALOG.read_text(),
                  matrix_sha256=pilot.sha(pilot.MATRIX),entry_mass=matrix.btn_mass)
        cache_review=pilot.read(OUT/'complete-private-allin-cache-v2-independent-review.json')
        assert cache_review['passed']
        cache=pilot.AllinCache(cache_review['cache_artifact'],cache_review['cache_sha256'])
        state,fork=pilot.copy_source(folder,arm,args);assert state['completed_iterations']==78
        oracle=pilot.read(reg['oracles'][name]['metrics']);destination=folder/'update-79'
        step=pilot.step_arguments(arm,args,cache,guard);step['workers']=8
        update=baseline_update
        if arm['treatment']=='river':
            update=river_update;step['river_executable']=pilot.EXES['river_executable']
        guard();torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
        pilot.atomic_json(folder/'ready.json',dict(registration_sha256=reg_sha,child=identity(),
                          source_fork=fork,setup_seconds=time.monotonic()-started))
        wait_marker('go.json');ownership()
        waited=resources.wait_seconds;start_ns=time.perf_counter_ns()
        metric=update(destination,folder/'objects',state,cfg,**step)
        torch.cuda.synchronize();end_ns=time.perf_counter_ns()
        timed=dict(case=case,arm=name,registration_sha256=reg_sha,child=identity(),
            start_ns=start_ns,end_ns=end_ns,external_update_seconds=(end_ns-start_ns)/1e9,
            pipeline_seconds=metric['seconds'],gpu_guard_wait_seconds=resources.wait_seconds-waited,
            peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
            peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved())
        assert timed['peak_cuda_reserved_bytes']<=CUDA_PER_CHILD
        pilot.atomic_json(folder/'timed.json',timed)
        # Readback CPU work must not overlap the other arm's timed update.
        wait_marker('verify.json');guard()
        assert metric['workers']==8 and metric['board_workers']==4
        for sub in metric['subbatches']:
            for filename,digest in sub['artifacts'].items():
                guard();assert pilot.sha(destination/f"batch-{sub['chunk']:02d}"/filename)==digest
        prior.validate(folder,arm,metric,oracle,args,guard)
        assert len(metric['fits'])==len(oracle['fits'])==2
        for actual,expected in zip(metric['fits'],oracle['fits']):assert metric_math(actual)==metric_math(expected)
        restored=pilot.checkpoint.restore_checkpoint(folder/'objects',metric['checkpoint'],cfg,**pilot.model_args(args,arm))
        pilot.compare_states(restored,state)
        pilot.verify(reg['inputs']);guard()
        proof=dict(**timed,source_fork=fork,checkpoint=metric['checkpoint'],
            metrics=str(destination/'metrics.json'),metrics_sha256=pilot.sha(destination/'metrics.json'),
            timed_sha256=pilot.sha(folder/'timed.json'),exact_saved_state=True,exact_numeric_fit_metrics=True,
            exact_artifacts=True,invocation_seconds=time.monotonic()-started,
            gpu_guard_probes=resources.probes)
        pilot.atomic_json(folder/'complete.json',proof)
        pilot.status('complete',case=case);print(json.dumps(dict(case=case,passed=True,seconds=timed['external_update_seconds'])),flush=True)
        del state,restored,metric;gc.collect()
    except BaseException as error:
        pilot.atomic_json(folder/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),
            registration_sha256=reg_sha,child=identity()))
        raise


def comparison(records):
    assert len(records)==4 and {r['case'] for r in records}==set(CASES)
    serial=[r for r in records if r['case'].startswith('serial-')]
    concurrent=[r for r in records if r['case'].startswith('concurrent-')]
    for row in records:
        assert row['end_ns']>row['start_ns']
        assert row['external_update_seconds']==(row['end_ns']-row['start_ns'])/1e9
    serial_seconds=sum(r['external_update_seconds'] for r in serial)
    concurrent_seconds=(max(r['end_ns'] for r in concurrent)-min(r['start_ns'] for r in concurrent))/1e9
    return dict(serial_sum_seconds=serial_seconds,concurrent_makespan_seconds=concurrent_seconds,
        serial_over_concurrent=serial_seconds/concurrent_seconds,
        percent_less_elapsed=100*(1-concurrent_seconds/serial_seconds),
        concurrent_start_skew_seconds=abs(concurrent[0]['start_ns']-concurrent[1]['start_ns'])/1e9,
        concurrent_overlap_seconds=max(0,min(r['end_ns'] for r in concurrent)-max(r['start_ns'] for r in concurrent))/1e9)


def main(run=False):
    began=time.monotonic();spec=specification()
    if not run:
        print(json.dumps(dict(preflight_passed=True,research_lock_present=pilot.LOCK.exists() or pilot.OTHER.exists(),gpu_started=False)),flush=True);return
    assert not any(p.exists() for p in (REG,RESULT,STORE)),'Preserve prior attempts; no automatic replay'
    ready,probe=pilot.available();assert ready,'Production or heavier external work has priority'
    acquired=False;job=None;children=[];logs=[];samples=[];last_probe=last_storage=0.
    parent=spec['parent']
    def parent_guard():
        nonlocal last_probe,last_storage
        now=time.monotonic()
        assert now-began<SECONDS,'Parent invocation deadline'
        assert pilot.LOCK.read_text()==str(parent['pid'])
        assert pilot.production_available() and not pilot.OTHER.exists(),'Production or another study has priority'
        assert not (STORE/'cancel.json').exists(),'Cancellation requested'
        assert psutil.virtual_memory().available>24_000_000_000 and psutil.disk_usage('S:/').free>40_000_000_000
        for row in children:
            if row['process'].poll() is None:
                assert alive(row['identity'])
                assert now-row['launched']<CHILD_SECONDS,'Child deadline'
        if now-last_storage>20:
            size=0
            for path in STORE.rglob('*'):
                try:
                    if path.is_file():size+=path.stat().st_size
                except FileNotFoundError:pass  # Atomic publication may rename a new temporary file.
            assert size<LIMIT,'New evidence storage allowance exhausted'
            last_storage=now
        if now-last_probe>10:
            rss=0;owned=[];seen=set()
            for row in children:
                if row['process'].poll() is not None:continue
                try:tree=[psutil.Process(row['identity']['pid']),*psutil.Process(row['identity']['pid']).children(recursive=True)]
                except psutil.NoSuchProcess:continue
                for p in tree:
                    try:
                        key=(p.pid,p.create_time())
                        if key in seen:continue
                        seen.add(key);rss+=p.memory_info().rss;owned.append(dict(pid=p.pid,created=key[1],name=p.name()))
                    except psutil.NoSuchProcess:pass
            samples.append(dict(elapsed=now-began,cpu_percent=psutil.cpu_percent(),available_ram=psutil.virtual_memory().available,
                gpu=pilot.gpu_snapshot(),observed_owned_rss_sum_bytes=rss,processes=owned,job=job.accounting()))
            pilot.atomic_json(STORE/'resource-samples.json',samples,replace=True);last_probe=now
        pilot.atomic_json(STATUS,dict(state='running',pid=parent['pid'],process_created=parent['created'],
            unix=time.time(),children=[dict(case=r['case'],**r['identity'],exit_code=r['process'].poll()) for r in children]),replace=True)
    def wait_until(fn, group):
        while not fn():
            parent_guard()
            for row in group:
                code=row['process'].poll()
                assert code is None or code==0,f"{row['case']} exited {code}; retain logs"
                if code==0:assert (STORE/row['case']/'complete.json').exists(),'Child exited without proof'
            time.sleep(.5)
    def marker(row,name):
        pilot.atomic_json(STORE/row['case']/name,dict(registration_sha256=pilot.sha(REG),child=row['identity'],
                          release_ns=time.perf_counter_ns()))
    try:
        with pilot.LOCK.open('x') as f:f.write(str(parent['pid']))
        acquired=True
        inventory=pilot.global_measure();allocated=sum(r['allocated_file_bytes'] for r in inventory)
        assert allocated+LIMIT+RESERVE<=pilot.GLOBAL_LIMIT
        pilot.atomic_json(REG,spec);pilot.create(STORE)
        pilot.atomic_json(STORE/'admission.json',dict(allocated_bytes=allocated,inventory=inventory,
            reserved_bytes=LIMIT+RESERVE,gpu=probe,unix=time.time()))
        job=OwnedJob();records=[];releases=[]
        for cases in GROUPS:
            parent_guard();group=[]
            for case in cases:
                folder=STORE/case;folder.mkdir()
                log=(folder/'process.log').open('xb');logs.append(log)
                process=subprocess.Popen([sys.executable,'-B',str(SELF),'--child',case],cwd=ROOT,
                    stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                row=dict(case=case,process=process,identity=identity(process.pid),launched=time.monotonic())
                children.append(row);group.append(row);job.assign(process)
                pilot.atomic_json(STORE/'children.json',[dict(case=r['case'],**r['identity']) for r in children],replace=True)
                marker(row,'permit.json')
            wait_until(lambda:all((STORE/r['case']/'ready.json').exists() for r in group),group)
            parent_guard()
            for row in group:
                doc=pilot.read(STORE/row['case']/'ready.json')
                assert doc['child']==row['identity'] and doc['registration_sha256']==pilot.sha(REG)
            before=time.perf_counter_ns()
            for row in group:marker(row,'go.json')
            releases.append(dict(cases=cases,first_release_ns=before,last_release_ns=time.perf_counter_ns()))
            wait_until(lambda:all((STORE/r['case']/'timed.json').exists() for r in group),group)
            for row in group:marker(row,'verify.json')
            wait_until(lambda:all(r['process'].poll() is not None for r in group),group)
            for row in group:
                assert row['process'].returncode==0
                proof=pilot.read(STORE/row['case']/'complete.json')
                assert proof['child']==row['identity'] and proof['registration_sha256']==pilot.sha(REG)
                assert proof['exact_saved_state'] and proof['exact_numeric_fit_metrics'] and proof['exact_artifacts']
                assert pilot.sha(proof['metrics'])==proof['metrics_sha256']
                assert pilot.sha(STORE/row['case']/'timed.json')==proof['timed_sha256']
                assert proof['checkpoint']==spec['oracles'][proof['arm']]['checkpoint']
                records.append(proof)
                print(json.dumps(dict(case=row['case'],passed=True,seconds=proof['external_update_seconds'])),flush=True)
        wait_until(lambda:job.accounting()['active_processes']==0,[])
        pilot.verify(spec['inputs']);parent_guard();storage=pilot.study_measure(STORE)
        assert storage['logical_bytes']<LIMIT
        global_final=pilot.global_measure();assert sum(r['allocated_file_bytes'] for r in global_final)<=pilot.GLOBAL_LIMIT
        result=dict(passed=True,complete=True,registration_sha256=pilot.sha(REG),cases=records,
            comparison=comparison(records),releases=releases,storage=storage,global_final=global_final,
            seconds=time.monotonic()-began,job_final=job.accounting(),gpu_used=True,
            production_modified=False,learning_bank_modified=False,new_evaluation_deals=0,accuracy_claim=False,
            limitation=spec['limitation'],gpu_wait_note='Guards can observe the other owned arm; wait time is not classified as external contention.')
        pilot.atomic_json(RESULT,result)
        pilot.atomic_json(STATUS,dict(state='complete',result=str(RESULT),pid=parent['pid'],process_created=parent['created'],unix=time.time()),replace=True)
        print(json.dumps(dict(passed=True,comparison=result['comparison'],seconds=result['seconds'])),flush=True)
    except BaseException as error:
        if STORE.exists() and not (STORE/'cancel.json').exists():
            pilot.atomic_json(STORE/'cancel.json',dict(error=repr(error),unix=time.time()))
        pilot.atomic_json(OUT/(NAME+'-interruption-'+uuid.uuid4().hex[:8]+'.json'),dict(error=repr(error),
            traceback=traceback.format_exc(),registration_sha256=pilot.sha(REG) if REG.exists() else None,
            preserve_partial_attempts=True))
        raise
    finally:
        if job is not None:job.close()
        for row in children:
            process=row['process']
            if process.poll() is None:
                assert alive(row['identity']);process.terminate()
            process.wait(timeout=10)
        for log in logs:log.close()
        if acquired:
            assert pilot.LOCK.read_text()==str(parent['pid']);pilot.LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--child',choices=CASES)
    opt=parser.parse_args()
    if opt.child and opt.run:parser.error('Child and run modes are mutually exclusive')
    if opt.child:child(opt.child)
    else:main(opt.run)
