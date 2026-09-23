"""Bounded wider root study with frozen class training and independent test draws."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2',CUBLAS_WORKSPACE_CONFIG=':4096:8')
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_wider_inputs_v1 import admitted
from compressed_research_store_v1 import create_parent,inventory
from reboot_research_idle_v1 import idle

PREFIX='later-average-wider-study-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
CONFIG=dict(id=PREFIX,train_seed=224331,test_seed=224332,per_class=256,test_deals=131072,
    batch_size=64,minimum_training_deals=16,family_alpha=.025)


def replace_json(path,value):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,separators=(',',':'),allow_nan=False)+'\n',newline='\n');tmp.replace(path)


def check_inputs(reg):
    for p,h in reg['inputs'].items():assert sha(p)==h,p


def worker(rp,reviewing):
    reg=read(rp);check_inputs(reg);assert LOCK.read_text().strip()==str(reg['controller_pid'])
    assert reg['config']==CONFIG and reg['store']==str(STORE)
    start=time.monotonic();last=[0.];cuda=[False];active=['admission']
    seconds=reg['review_maximum_seconds'] if reviewing else reg['evaluation_maximum_seconds']
    def guard():
        assert time.monotonic()-start<seconds
        if time.monotonic()-last[0]>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000 and shutil.disk_usage('S:/').free>40_000_000_000
            if cuda[0]:assert torch.cuda.mem_get_info()[0]>3_000_000_000
            replace_json(OUT/f'{PREFIX}-progress.json',dict(stage='readback' if reviewing else 'evaluation',
                worker_pid=os.getpid(),seconds=time.monotonic()-start,active_batch=active[0],production_modified=False))
            last[0]=time.monotonic()
    guard();folder=STORE/'evaluation'
    if reviewing:
        from wider_root_readback_v1 import review
        prior=read(OUT/f'{PREFIX}-evaluation.json')
        assert prior['registration_sha256']==sha(rp) and prior['complete'] and prior['result_sha256']==sha(folder/'result.json')
        audit=review(OUT/'bb-context-candidate.json',folder,CONFIG,reg['exact'],reg['cache_sha256'],guard)
        check_inputs(reg);guard()
        audit.update(registration_sha256=sha(rp),evaluation_sha256=sha(OUT/f'{PREFIX}-evaluation.json'),
            result_sha256=sha(folder/'result.json'),seconds=time.monotonic()-start)
        save(OUT/f'{PREFIX}-independent-review.json',audit);print(audit,flush=True);return
    data=admitted();assert data['exact']==reg['exact'] and data['policy_sha256']==reg['policy_sha256']
    assert data['cache'].sha256==reg['cache_sha256'] and data['checkpoint']==reg['checkpoint']
    import torch
    from sampled_visible_hybrid_gpu_bank_v1 import VisibleHybridCudaBank64
    from wider_root_evaluation_v1 import run
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    cuda[0]=True;guard()
    bank=VisibleHybridCudaBank64(data['models'],data['weights'],context_source=data['context_source'],models_per_chunk=8,guard=guard)
    class VisibleOnly:
        def average(self,q,*,guard):
            batch=json.loads(q['batch_source'])
            assert batch['format']==2 and not any(k.startswith('allin_') or k=='terminal_estimator' for k in batch)
            active[0]=batch['batch_id'];guard();return bank.average(q,guard=guard)
    result=run(data['context_path'],VisibleOnly(),data['cache'],reg['exact'],CONFIG,folder,guard)
    assert result['complete'] and result['training_deals']==43264 and result['test_deals']==131072
    assert result['training_counts']==[256]*169
    active[0]='final file flush'
    for p in folder.rglob('*'):
        guard();assert not p.is_symlink()
        if p.is_file():
            with p.open('r+b') as f:os.fsync(f.fileno())
    disk=inventory(folder,guard);assert disk['compressed_files']==len(disk['files'])
    assert disk['allocated_bytes']<reg['maximum_allocated_bytes'] and disk['logical_bytes']<reg['maximum_logical_bytes']
    save(OUT/f'{PREFIX}-storage.json',disk)
    check_inputs(reg);guard()
    save(OUT/f'{PREFIX}-evaluation.json',dict(complete=True,registration_sha256=sha(rp),
        result_sha256=sha(folder/'result.json'),storage_sha256=sha(OUT/f'{PREFIX}-storage.json'),
        training_deals=result['training_deals'],test_deals=result['test_deals'],intervals=result['intervals'],
        stability=result['stability'],phase_timings=result['phase_timings'],seconds=time.monotonic()-start,
        accuracy_qualified=False,production_modified=False))
    print(dict(complete=True,phase_timings=result['phase_timings'],intervals=result['intervals']),flush=True)


def main():
    started=time.monotonic();assert idle() and not LOCK.exists() and not OTHER.exists() and not STORE.exists()
    data=admitted();inputs=data['inputs']
    ar,ap,ast=[OUT/f'later-average-wider-admission-v1-{s}.json' for s in ('registration','result','status')]
    control,checked,status=map(read,(ar,ap,ast))
    assert checked['passed'] and checked['registration_sha256']==sha(ar) and status['state']=='complete' and status['error'] is None
    assert control['checkpoint']==data['checkpoint'] and control['policy_sha256']==data['policy_sha256']
    assert control['cache_sha256']==data['cache'].sha256
    inputs.update(control['inputs'])
    for phase,key in (('gpu','gpu_summary_sha256'),('cpu','cpu_summary_sha256')):
        folder=Path(control['store'])/phase;summary=read(folder/'summary.json')
        assert sha(folder/'summary.json')==checked[key]
        inputs[str(folder/'summary.json')]=sha(folder/'summary.json')
        for name,h in summary['artifacts'].items():assert sha(folder/name)==h;inputs[str(folder/name)]=h
    total=169*CONFIG['per_class']+CONFIG['test_deals']
    projected=checked['gpu_batch_storage']['allocated_bytes']*total/control['deals']*1.5
    assert projected+40_000_000_000<shutil.disk_usage('S:/').free,'Storage margin not available'
    readback_control=OUT/'wider-root-readback-control-v1-result.json'
    storage_control=OUT/'wider-root-storage-control-v2-result.json'
    assert read(readback_control)['passed'] and read(storage_control)['passed']
    for p in (Path(__file__),ar,ap,ast,readback_control,storage_control,OUT/'WIDER-RESPONSE-FULL-PLAN.md'):
        inputs[str(p)]=sha(p)
    for name in ('later_average_wider_inputs_v1.py','wider_root_evaluation_v1.py','wider_root_readback_v1.py',
                 'exact_aware_root_response_v1.py','root_residual_evaluation_v1.py','sampled_evaluation_intervals_v1.py',
                 'sampled_player_stratified_response_deals_v2.py','compressed_research_store_v1.py','reboot_research_idle_v1.py'):
        p=ROOT/'tools/research'/name;inputs[str(p)]=sha(p)
    for p,h in inputs.items():assert sha(p)==h,p
    rp=OUT/f'{PREFIX}-registration.json'
    reg=dict(inputs=inputs,controller_pid=os.getpid(),config=CONFIG,store=str(STORE),exact=data['exact'],
        checkpoint=data['checkpoint'],policy_sha256=data['policy_sha256'],cache_sha256=data['cache'].sha256,
        evaluation_maximum_seconds=43200,review_maximum_seconds=7200,maximum_allocated_bytes=44_000_000_000,
        maximum_logical_bytes=120_000_000_000,planning_allocation_with_50pct_margin=projected,
        host_reserve_bytes=20_000_000_000,gpu_reserve_bytes=3_000_000_000,disk_reserve_bytes=40_000_000_000,
        scope='Five fixed BB first-decision deviations against the complete linear bank; subsequent play frozen. Not full best response, convergence or general preflop accuracy.',
        stopping='Fixed counts, one final look; stop on first integrity/resource/deadline/production-activity failure. No retry, budget extension or deployment.',production_modified=False)
    save(rp,reg);del data
    acquired=False;child=None;records=[];error=None;resources=[]
    def status(state,**extra):replace_json(OUT/f'{PREFIX}-status.json',dict(state=state,controller_pid=os.getpid(),
        seconds=time.monotonic()-started,stages=records,production_modified=False,**extra))
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        create_parent(STORE,lambda:None)
        for label,flag,cap in [('evaluation','--worker',43200),('readback','--review',7200)]:
            assert idle();check_inputs(reg);before=time.monotonic()
            with (OUT/f'{PREFIX}-{label}.log').open('x') as stream:
                child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),flag,str(rp)],cwd=ROOT,
                    stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                status('running',stage=label,worker_pid=child.pid)
                while child.poll() is None:
                    assert time.monotonic()-before<cap and idle()
                    host=psutil.virtual_memory().available;disk=shutil.disk_usage('S:/').free
                    assert host>=reg['host_reserve_bytes'] and disk>=reg['disk_reserve_bytes']
                    resources.append(dict(stage=label,seconds=time.monotonic()-started,free_host_bytes=host,free_disk_bytes=disk))
                    replace_json(OUT/f'{PREFIX}-resources.json',resources)
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:pass
            records.append(dict(stage=label,exit_code=child.returncode,seconds=time.monotonic()-before))
            assert child.returncode==0,f'{label} failed; preserve artifacts, no automatic retry'
            print(records[-1],flush=True)
        check_inputs(reg)
        audit=read(OUT/f'{PREFIX}-independent-review.json');evaluation=read(OUT/f'{PREFIX}-evaluation.json')
        assert audit['passed'] and audit['evaluation_sha256']==sha(OUT/f'{PREFIX}-evaluation.json')
        assert audit['registration_sha256']==evaluation['registration_sha256']==sha(rp)
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),stages=records,
            intervals=evaluation['intervals'],stability=evaluation['stability'],seconds=time.monotonic()-started,
            accuracy_qualified=False,production_modified=False,scope=reg['scope']))
    except BaseException as exc:error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:
            subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
            child.wait(timeout=30)
        status('stopped' if error else 'complete',error=error)
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1] in ('--worker','--review'):worker(Path(sys.argv[2]),sys.argv[1]=='--review')
    elif sys.argv[1:]==['--run']:main()
    else:raise SystemExit('Use --run for a new admitted study; direct worker restart is not a resume protocol.')
