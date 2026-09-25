"""Replay one audited GPU update after copying its preceding checkpoint to S:.

Run only when the research GPU owner has released its lock. This is a fixed
pilot implementation control, not a fresh trial or a retry of a live worker.
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
from immutable_checkpoint_copy_v1 import inspect_closure,copy_closure
from new_volume_research_store_v1 import create_store,measure_store
from hu_action_integrated_exact_20260925 import bank_args
from hu_paired_continuation_support_20260925 import setup_cuda,LOCK,OTHER

PREFIX='checkpoint-volume-replay-control-v1'
PILOT='later-action-joint-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
CAP=400_000_000


def verify(inputs,guard=lambda:None):
    for p,h in inputs.items():guard();assert sha(p)==h,p


def resource_guard(started,reg,gpu=False):
    last=last_size=0.
    def guard():
        nonlocal last,last_size
        now=time.monotonic()
        assert now-started<reg['maximum_seconds']
        if now-last>2:
            assert idle() and not OTHER.exists()
            assert psutil.virtual_memory().available>20_000_000_000
            assert shutil.disk_usage('S:/').free>40_000_000_000
            # Training data is written to S:. T: receives bounded small control
            # metadata only; the live trial's original T: reserve is untouched.
            assert shutil.disk_usage('T:/').free>1_000_000_000
            if gpu:
                import torch
                assert torch.cuda.mem_get_info()[0]>3_000_000_000
            last=now
        if now-last_size>10:
            if STORE.exists():
                assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())<CAP
            last_size=now
    return guard


def worker(reg):
    import torch
    from later_action_training_v1 import update
    from later_action_checkpoint_v1 import restore_checkpoint
    started=time.monotonic();setup_cuda();guard=resource_guard(started,reg,gpu=True)
    guard();verify(reg['inputs'],guard)
    result=read(OUT/f'{PILOT}-result.json');cfg=result['config']
    assert cfg['torch_version']==torch.__version__ and cfg['numpy_version']==np.__version__
    assert cfg['device_name']==torch.cuda.get_device_name()
    source=Path(result['store']);old=read(source/'iteration-0002/metrics.json')
    create_store(STORE)
    closure=copy_closure(source/'objects',STORE/'objects',reg['checkpoint'],maximum_bytes=CAP,guard=guard)
    assert closure==reg['closure']
    cp=OUT/'bb-context-candidate.json';args=bank_args(cp.read_text())
    state=restore_checkpoint(STORE/'objects',reg['checkpoint'],config=cfg,**args)
    assert state['completed_iterations']==1
    step=dict(context_path=cp,catalog_source=args['catalog_source'],
        matrix_source=(OUT/'preflop-allin-matrix-control-v1-matrix.json').read_text(),
        matrix_sha256=args['matrix_sha256'],cache=load_complete_cache(),
        executable=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe',
        integration_executable=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe',
        trace_executable=ROOT/'target/release/examples/hu_sampled_action_trace_v2.exe',
        batch_prefix=PILOT,guard=guard)
    began=time.monotonic()
    new=update(STORE/'iteration-0002',STORE/'objects',state,cfg,**step)
    update_seconds=time.monotonic()-began
    assert new['checkpoint']==old['checkpoint']==result['final_checkpoint']
    for key in old:
        if key not in ('fits','root_integration_seconds'):assert new[key]==old[key],key
    timing={'setup_seconds','optimizer_seconds','graph_capture_seconds'}
    for a,b in zip(old['fits'],new['fits']):
        assert {k:v for k,v in a.items() if k not in timing}=={k:v for k,v in b.items() if k not in timing}
    expected_files={p.relative_to(source/'iteration-0002'):sha(p)
                    for p in (source/'iteration-0002').rglob('*') if p.is_file() and p.name!='metrics.json'}
    observed_files={p.relative_to(STORE/'iteration-0002'):sha(p)
                    for p in (STORE/'iteration-0002').rglob('*') if p.is_file() and p.name!='metrics.json'}
    assert observed_files==expected_files
    before=restore_checkpoint(source/'objects',old['checkpoint'],config=cfg,**args)
    after=restore_checkpoint(STORE/'objects',new['checkpoint'],config=cfg,**args)
    for key in ('completed_iterations','played_bank','next_model','next_model_document'):
        assert before[key]==after[key],key
    for key in ('exact_btn_state','root_regret_state'):
        assert before[key].document()==after[key].document(),key
    for a,b in zip(before['reservoirs'],after['reservoirs']):
        assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
        for key in ('keys','active','arity','values','iterations'):
            assert getattr(a,key).tobytes()==getattr(b,key).tobytes(),key
    assert before['sampler'].checkpoint()==after['sampler'].checkpoint()
    assert before['sampler'].sample(8)==after['sampler'].sample(8)
    assert before['action_rng'].bit_generator.state==after['action_rng'].bit_generator.state
    assert np.array_equal(before['action_rng'].integers(2**63,size=64),after['action_rng'].integers(2**63,size=64))
    verify(reg['inputs'],guard)
    allocation=measure_store(STORE,guard)
    assert allocation['files']==allocation['compressed_files']
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        copied_checkpoint=reg['checkpoint'],result_checkpoint=new['checkpoint'],
        exact_checkpoint=True,exact_native_artifacts=True,exact_reservoirs_and_accumulators=True,
        next_action_and_deal_streams_exact=True,artifact_files_compared=len(expected_files),
        update_seconds=update_seconds,seconds=time.monotonic()-started,storage=allocation,
        artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
        gpu_used=True,live_trial_modified=False,production_modified=False,accuracy_qualified=False,
        scope='Exact fixed pilot update replay after checkpoint copy to S:. Live continuation still requires terminal-prefix audit and remaining resource admission.'))


def main():
    assert sys.argv[1:] in (['--run'],['--worker'])
    rp=OUT/f'{PREFIX}-registration.json'
    if sys.argv[1:]==['--worker']:worker(read(rp));return
    assert idle() and not LOCK.exists() and not OTHER.exists()
    assert not STORE.exists() and not rp.exists()
    result=read(OUT/f'{PILOT}-result.json');audit=read(OUT/f'{PILOT}-independent-review.json')
    oldrp=OUT/f'{PILOT}-registration.json';oldpp=OUT/f'{PILOT}-result.json'
    assert result['passed'] and result['terminal'] and audit['passed']
    assert result['registration_sha256']==audit['source_registration_sha256']==sha(oldrp)
    assert audit['source_result_sha256']==sha(oldpp)
    assert result['completed_iterations']==audit['completed_updates']==2
    assert audit['readback_registration_sha256']==sha(OUT/f'{PILOT}-readback-registration.json')
    first=read(Path(result['store'])/'iteration-0001/metrics.json')['checkpoint']
    closure=inspect_closure(Path(result['store'])/'objects',first,maximum_bytes=CAP,guard=lambda:None)
    inputs=dict(read(oldrp)['inputs'])
    inputs.update(result['artifacts'])
    paths=list((ROOT/'tools/research').glob('*.py'))
    paths.extend(OUT/f'{PILOT}-{s}.json' for s in ('registration','result','readback-registration','independent-review'))
    for prefix in ('checkpoint-volume-copy-control-v1','split-history-readback-control-v1'):
        p=OUT/f'{prefix}-result.json';r=read(p);assert r['passed']
        rpath=OUT/f'{prefix}-registration.json';assert r['registration_sha256']==sha(rpath)
        paths.extend([p,rpath])
    live_rp=OUT/'later-action-matched-replication-v1-registration.json';paths.append(live_rp)
    inputs.update({str(p):sha(p) for p in paths});verify(inputs)
    admission=read(live_rp)['storage_admission']
    projected=admission['projected_allocated_bytes']+250_000_000+350_000_000+CAP
    assert projected<=admission['limit_bytes']==800_000_000_000
    assert shutil.disk_usage('S:/').free>40_000_000_000+CAP
    assert int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free',
               '--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2>5_000_000_000
    reg=dict(inputs=inputs,checkpoint=first,closure=closure,config=result['config'],
        maximum_seconds=900,maximum_output_bytes=CAP,store=str(STORE),
        projected_allocated_bytes=projected,source_volume_free_floor_bytes=1_000_000_000,
        destination_volume_free_floor_bytes=40_000_000_000,production_modified=False,
        scope='Same CUDA update, same pilot seed, same batch identifiers; location changes only. No active-trial retry or optimization adoption.')
    save(rp,reg)
    started=time.monotonic();guard=resource_guard(started,reg);child=None;error=None;acquired=False
    try:
        with LOCK.open('x') as stream:stream.write(str(os.getpid()))
        acquired=True;guard()
        env=os.environ.copy();env['PYTHONUNBUFFERED']='1'
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],cwd=ROOT,
                env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                guard()
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
        assert child.returncode==0,'Inspect retained control log; no automatic retry'
        assert read(OUT/f'{PREFIX}-result.json')['passed'];verify(inputs)
    except BaseException as exc:error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:
            for descendant in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:descendant.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        save(OUT/f'{PREFIX}-status.json',dict(state='failed' if error else 'complete',error=error,
            exit_code=child.returncode if child else None,seconds=time.monotonic()-started,
            production_modified=False))


if __name__=='__main__':main()
