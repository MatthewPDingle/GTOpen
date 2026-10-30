"""Continue a verified terminal prefix on S: with the original training algorithm.

All completed raw evidence remains on T:. Only the last checkpoint's dependency
closure is copied. New updates retain the original prefix, seeds, configuration,
full played history, and remaining portion of the original wall-time budget.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read,load_complete_cache
from reboot_research_idle_v1 import idle
from hu_paired_continuation_support_20260925 import LOCK,OTHER,setup_cuda
from hu_root_retained_storage_admitted_study_20260924 import measure,LIMIT,METADATA_RESERVE
from stopped_later_action_trial_v1 import assert_original_stopped
from immutable_checkpoint_copy_v1 import inspect_closure,copy_closure
from new_volume_research_store_v1 import create_store,measure_store
from hu_action_integrated_exact_20260925 import bank_args

ORIGINAL='later-action-matched-replication-v1'
PREFIX_AUDIT='later-action-replication-storage-prefix-v1'
PREFIX='later-action-replication-volume-continuation-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def verify(inputs,guard=lambda:None):
    for p,h in inputs.items():guard();assert sha(p)==h,p


def prefix_audit_state(reg):
    path=Path(reg['prefix_review_path'])
    if path.exists():
        audit=read(path)
        assert audit['passed'],'Independent prefix audit failed; stop continuation'
        assert audit['source_registration_sha256']==reg['prefix_registration_sha256']
        assert audit['source_result_sha256']==reg['prefix_result_sha256']
        assert audit['readback_registration_sha256']==reg['prefix_readback_registration_sha256']
        assert audit['completed_updates']==reg['prefix_completed_iterations']
        assert audit['final_checkpoint']==reg['resume_checkpoint']
        return True
    process=psutil.Process(reg['prefix_reader_pid'])
    assert process.is_running() and process.create_time()==reg['prefix_reader_create_time']
    assert any(Path(s).name=='hu_later_action_prefix_audit_20260925.py' for s in process.cmdline())
    return False


def guard_for(started,reg,gpu=False):
    last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        assert now-started<reg['maximum_seconds'],'Remaining original runtime exhausted'
        if now-last>2:
            assert idle() and not OTHER.exists(),'Production or other research activity'
            assert psutil.virtual_memory().available>20_000_000_000
            assert shutil.disk_usage('S:/').free>40_000_000_000
            assert shutil.disk_usage('T:/').free>1_000_000_000
            if gpu:
                import torch
                assert torch.cuda.mem_get_info()[0]>3_000_000_000
            last=now
    return guard


def worker(reg):
    import torch
    from later_action_training_v1 import update
    from later_action_checkpoint_v1 import restore_checkpoint
    from root_retained_replication_resume_support_v1 import durable_iteration
    started=time.monotonic();setup_cuda();guard=guard_for(started,reg,gpu=True)
    guard();verify(reg['inputs'],guard);cfg=reg['config']
    assert cfg['torch_version']==torch.__version__ and cfg['numpy_version']==np.__version__
    assert cfg['device_name']==torch.cuda.get_device_name()
    source=Path(reg['original_store']);create_store(STORE)
    closure=copy_closure(source/'objects',STORE/'objects',reg['resume_checkpoint'],
        maximum_bytes=reg['closure']['logical_bytes'],guard=guard)
    assert closure==reg['closure']
    save(STORE/'imported-state.json',dict(source=str(source/'objects'),checkpoint=reg['resume_checkpoint'],
        objects=closure,original_registration_sha256=reg['original_registration_sha256']))
    cp=OUT/'bb-context-candidate.json';args=bank_args(cp.read_text())
    state=restore_checkpoint(STORE/'objects',reg['resume_checkpoint'],config=cfg,**args)
    assert state['completed_iterations']==reg['prefix_completed_iterations']
    step=dict(context_path=cp,catalog_source=args['catalog_source'],
        matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(),
        matrix_sha256=args['matrix_sha256'],cache=load_complete_cache(),
        executable=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe',
        integration_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',
        trace_executable=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe',
        batch_prefix=ORIGINAL,guard=guard)
    save(OUT/f'{PREFIX}-environment.json',cfg)
    metrics=list(reg['prefix_steps'])
    for iteration in range(state['completed_iterations']+1,cfg['max_iterations']+1):
        guard();began=time.monotonic();folder=STORE/f'iteration-{iteration:04d}'
        row=update(folder,STORE/'objects',state,cfg,**step)
        checkpoint=row['checkpoint'];pointer=STORE/f'checkpoint-{iteration:04d}.json';save(pointer,checkpoint)
        metrics.append(dict(iteration=iteration,seconds=time.monotonic()-began,
            checkpoint=checkpoint,metrics_sha256=sha(folder/'metrics.json')))
        durable_iteration(folder,pointer)
        tmp=STORE/'latest.tmp';save(tmp,dict(completed_iterations=iteration,checkpoint=checkpoint,config=cfg))
        with tmp.open('r+b') as stream:os.fsync(stream.fileno())
        tmp.replace(STORE/'latest.json')
        print(json.dumps(dict(iteration=iteration,seconds=metrics[-1]['seconds'],
            fresh_deals=state['sampler'].draws,retained=[r.size for r in state['reservoirs']],
            seen=[r.seen for r in state['reservoirs']])),flush=True)
    verify(reg['inputs'],guard)
    files=dict(reg['prefix_artifacts'])
    for p in STORE.rglob('*'):
        if p.is_file():guard();files[str(p)]=sha(p)
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,terminal=True,
        registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        original_registration_sha256=reg['original_registration_sha256'],
        config=cfg,store=str(STORE),completed_iterations=len(metrics),steps=metrics,
        initial_checkpoint=reg['initial_checkpoint'],final_checkpoint=checkpoint,
        history_segments=reg['history_segments'],artifacts=files,
        seconds=time.monotonic()-started,prior_runtime_charge_seconds=reg['prior_runtime_charge_seconds'],
        production_modified=False,accuracy_qualified=False,
        scope='Same original 78-update trial, continued after a resource stop. Full independent split-history audit and fixed heldout comparison remain required.'))


def main():
    assert sys.argv[1:] in (['--run'],['--worker'])
    rp=OUT/f'{PREFIX}-registration.json'
    if sys.argv[1:]==['--worker']:worker(read(rp));return
    assert idle() and not LOCK.exists() and not OTHER.exists()
    assert_original_stopped();assert not STORE.exists() and not rp.exists()
    oldrp=OUT/f'{ORIGINAL}-registration.json';old=read(oldrp)
    pr,pp,ar,ap=[OUT/f'{PREFIX_AUDIT}-{s}.json' for s in
        ('registration','result','readback-registration','independent-review')]
    prefix,result,auditreg=map(read,(pr,pp,ar))
    assert result['passed'] and not result['terminal']
    assert result['registration_sha256']==sha(pr)
    assert prefix['original_registration_sha256']==result['original_registration_sha256']==sha(oldrp)
    n=result['completed_iterations'];cfg=result['config']
    assert 0<n<cfg['max_iterations']==78
    assert all(cfg[k]==v for k,v in old['config'].items()) and cfg==prefix['config']
    assert prefix['prior_runtime_charge_seconds']+prefix['remaining_runtime_seconds']==old['maximum_seconds']
    assert prefix['remaining_runtime_seconds']>0
    latest=read(Path(old['store'])/'latest.json');assert latest['completed_iterations']==n
    assert latest['checkpoint']==result['final_checkpoint']
    prefix_gate=dict(prefix_review_path=str(ap),prefix_registration_sha256=sha(pr),
        prefix_result_sha256=sha(pp),prefix_readback_registration_sha256=sha(ar),
        prefix_completed_iterations=n,resume_checkpoint=result['final_checkpoint'],
        prefix_reader_pid=prefix['reader_pid'],prefix_reader_create_time=prefix['reader_create_time'])
    prefix_audit_state(prefix_gate)
    cr=OUT/'checkpoint-volume-replay-control-v1-registration.json'
    cp=OUT/'checkpoint-volume-replay-control-v1-result.json';control=read(cp)
    cs=OUT/'checkpoint-volume-replay-control-v1-status.json'
    assert control['passed'] and control['registration_sha256']==sha(cr)
    assert read(cs)['state']=='complete' and read(cs)['error'] is None
    assert all(control[k] for k in ('exact_checkpoint','exact_native_artifacts',
        'exact_reservoirs_and_accumulators','next_action_and_deal_streams_exact'))
    for k in ('architecture','reservoir_capacity','fit_steps','chunk_size','learning_rate',
              'fit_implementation','device','current_policy_inference','postflop_learning_targets'):
        assert cfg[k]==read(cr)['config'][k],k
    closure=inspect_closure(Path(old['store'])/'objects',result['final_checkpoint'],
        maximum_bytes=1_000_000_000,guard=lambda:None)
    # Conservative per-update allocation allowance; it is a resource ceiling,
    # not permission to shorten training if the ceiling is reached.
    cap=(78-n)*160_000_000+closure['logical_bytes']+100_000_000
    roots=measure();total=sum(r['allocated_file_bytes'] for r in roots)
    projected=total+cap+8_000_000_000+METADATA_RESERVE
    assert projected<=LIMIT,'Continuation plus evaluation exceeds remaining global budget'
    assert shutil.disk_usage('S:/').free>40_000_000_000+cap
    inputs={**old['inputs'],**auditreg['inputs'],**read(cr)['inputs']}
    paths=list((ROOT/'tools/research').glob('*.py'))+[oldrp,pr,pp,ar,cr,cp,cs,
        OUT/'LATER-ACTION-RECOVERY-AUDIT-OVERLAP.md']
    if ap.exists():paths.append(ap)
    inputs.update({str(p):sha(p) for p in paths});verify(inputs)
    source=Path(old['store'])
    reg=dict(inputs=inputs,config=cfg,store=str(STORE),original_store=str(source),
        original_registration_sha256=sha(oldrp),prefix_completed_iterations=n,
        resume_checkpoint=result['final_checkpoint'],initial_checkpoint=read(source/'checkpoint-0000.json'),
        prefix_steps=result['steps'],prefix_artifacts=result['artifacts'],closure=closure,
        maximum_seconds=prefix['remaining_runtime_seconds'],prior_runtime_charge_seconds=prefix['prior_runtime_charge_seconds'],
        original_maximum_seconds=old['maximum_seconds'],maximum_store_bytes=cap,
        maximum_logical_bytes=(78-n)*600_000_000+closure['logical_bytes'],
        storage_admission=dict(roots=roots,allocated_file_bytes=total,projected_allocated_bytes=projected,
            limit_bytes=LIMIT,evaluation_reserve_bytes=8_000_000_000,metadata_reserve_bytes=METADATA_RESERVE),
        history_segments=[dict(first=1,last=n,store=str(source),objects=str(source/'objects')),
                          dict(first=n+1,last=78,store=str(STORE),objects=str(STORE/'objects'))],
        batch_prefix=ORIGINAL,automatic_retry=False,production_modified=False,
        stopping='Complete the original fixed 78 updates, or stop on original remaining runtime/activity/new volume reserve. No outcome-based stopping or selection.',
        changes='Storage routing only. Preserve original math, seeds, fit implementation, samples, counts, played bank, and unfinished-update redo from the last durable checkpoint.')
    reg.update(prefix_gate,scheduling='GPU continuation may overlap its immutable-prefix CPU audit. Stop if the audit fails or disappears; require its successful result before completion, then independently audit all 78 updates before evaluation.')
    save(rp,reg);child=None;error=None;acquired=False;resources=[];started=time.monotonic()
    guard=guard_for(started,reg)
    try:
        with LOCK.open('x') as stream:stream.write(str(os.getpid()))
        acquired=True;guard()
        env=os.environ.copy();env['PYTHONUNBUFFERED']='1'
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],cwd=ROOT,
                env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            save(OUT/f'{PREFIX}-admission.json',dict(controller_pid=os.getpid(),worker_pid=child.pid,
                registration_sha256=sha(rp),production_modified=False))
            last_size=0.
            while child.poll() is None:
                guard()
                prefix_audit_state(reg)
                if STORE.exists() and time.monotonic()-last_size>30:
                    allocation=measure_store(STORE,guard)
                    assert allocation['allocated_file_bytes']<=reg['maximum_store_bytes']
                    assert allocation['logical_bytes']<=reg['maximum_logical_bytes']
                    resources.append(dict(seconds=time.monotonic()-started,**allocation))
                    last_size=time.monotonic()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
        assert child.returncode==0,'Worker failed; retain evidence and do not retry automatically'
        while not prefix_audit_state(reg):
            guard();time.sleep(2)
        save(OUT/f'{PREFIX}-prefix-audit-admission.json',dict(passed=True,
            prefix_review_sha256=sha(reg['prefix_review_path']),registration_sha256=sha(rp)))
        verify(inputs);done=read(OUT/f'{PREFIX}-result.json')
        assert done['passed'] and done['terminal'] and done['completed_iterations']==78
        allocation=measure_store(STORE,guard);assert allocation['files']==allocation['compressed_files']
        assert allocation['allocated_file_bytes']<=reg['maximum_store_bytes']
        assert allocation['logical_bytes']<=reg['maximum_logical_bytes']
        save(OUT/f'{PREFIX}-storage.json',allocation)
    except BaseException as exc:error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:
            for descendant in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:descendant.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,
            exit_code=child.returncode if child else None,controller_pid=os.getpid(),
            execution_seconds=time.monotonic()-started,production_modified=False))
        save(OUT/f'{PREFIX}-resources.json',resources)
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
