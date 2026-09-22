"""Queue a bounded CUDA query/traversal/replay/fit control behind existing GPU work."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import psutil

from loopback_research_validation import idle
from sampled_batch_model_v1 import predict
from sampled_batch_protocol_v2 import policy_document
from sampled_physical_reservoir_v1 import PhysicalReservoir, ingest
from sampled_physical_fit_v1 import grouped_rows, fresh_network, objective, fit

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-pipeline-gpu-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER_LOCK=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p,d,exclusive=True):
    with p.open('x' if exclusive else 'w',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(d,separators=(',',':'))+'\n')


def output(suffix):return OUT/(PREFIX+'-'+suffix+'.json')


def worker(reg):
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    assert torch.cuda.is_available()
    started=time.monotonic();next_guard=0.
    def guard():
        nonlocal next_guard
        now=time.monotonic()-started
        if now>=next_guard:
            assert now<reg['maximum_seconds'] and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            next_guard=now+2
    def invoke(args):
        guard()
        r=subprocess.run(list(map(str,args)),cwd=ROOT,timeout=60,capture_output=True,text=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)
        assert r.returncode==0,r.stderr[:2000]
    context=OUT/'bb-context-candidate.json';batch=OUT/'sampled-batch-bridge-v2-batch.json'
    bridge=ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe'
    queries_path=output('queries');invoke([bridge,'queries',context,batch,'-',queries_path])
    queries=json.loads(queries_path.read_text())
    teacher=json.loads((OUT/'sampled-physical-stream-fit-v1-weights.json').read_text())['networks']
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
    rng_cpu=torch.get_rng_state().clone();rng_cuda=torch.cuda.get_rng_state().clone()
    cpu_scores,cpu_policy=predict(queries['observations'],teacher,'cpu')
    gpu_scores,gpu_policy=predict(queries['observations'],teacher,'cuda')
    teacher_error=float(np.max(np.abs(cpu_scores-gpu_scores)))
    teacher_policy_error=float(np.max(np.abs(cpu_policy-gpu_policy)))
    assert teacher_error<2e-5 and teacher_policy_error<1e-4
    policies_path=output('policies');save(policies_path,policy_document(queries,gpu_policy))
    updates_path=output('updates');invoke([bridge,'verify',context,batch,policies_path,updates_path])
    updates=json.loads(updates_path.read_text())
    assert updates['verified_traversals']==32 and updates['maximum_reference_error']==0
    buffers=[PhysicalReservoir(257,p,5301+p,queries['context_source']) for p in (0,1)]
    for iteration in (1,2,3):ingest(queries,updates,buffers,iteration)
    networks=[];fits=[];gradient_error=0.
    for player,r in enumerate(buffers):
        grouped=grouped_rows(r);cpu=fresh_network(6301+player)
        cuda=fresh_network(6301+player).cuda()
        objective(cpu,grouped,31,guard,backward=True)
        objective(cuda,grouped,31,guard,backward=True)
        difference=max(float((a.grad-b.grad.cpu()).abs().max()) for a,b in zip(cpu.parameters(),cuda.parameters()))
        gradient_error=max(gradient_error,difference);assert difference<1e-5
        net,metric=fit(r,seed=6301+player,steps=64,device='cuda',chunk_size=31,guard=guard)
        assert metric['normalized_grouped_loss_after']<metric['normalized_grouped_loss_before']
        networks.append(net);fits.append(metric)
    assert torch.equal(rng_cpu,torch.get_rng_state()) and torch.equal(rng_cuda,torch.cuda.get_rng_state())
    weights_path=output('weights');save(weights_path,dict(networks=networks,
        advantage_scales=[m['advantage_scale'] for m in fits],scope='Fixed-data CUDA pipeline control only.'))
    rust_path=output('engine-inference')
    exe=ROOT/'target/release/examples/hu_sampled_physical_fit_control.exe'
    invoke([exe,'infer',context,queries_path,weights_path,rust_path])
    fitted_scores,fitted_policy=predict(queries['observations'],networks,'cuda')
    rust=json.loads(rust_path.read_text())['rows']
    score_error=float(np.max(np.abs(fitted_scores-np.array([r['scores'] for r in rust]))))
    policy_error=float(np.max(np.abs(fitted_policy-np.array([r['policy'] for r in rust]))))
    assert score_error<2e-5 and policy_error<1e-4
    # Consume the newly fitted CUDA policy in a second verified traversal batch.
    fitted_path=output('fitted-policies');save(fitted_path,policy_document(queries,fitted_policy))
    fitted_updates=output('fitted-updates');invoke([bridge,'verify',context,batch,fitted_path,fitted_updates])
    second=json.loads(fitted_updates.read_text());assert second['maximum_reference_error']==0 and second['verified_traversals']==32
    result=dict(passed=True,observations=len(queries['observations']),verified_traversals=64,
        teacher_cpu_cuda_score_error=teacher_error,teacher_cpu_cuda_policy_error=teacher_policy_error,
        maximum_cpu_cuda_gradient_error=gradient_error,trained_rust_score_error=score_error,
        trained_rust_policy_error=policy_error,fits=fits,caller_cpu_cuda_rng_preserved=True,
        peak_allocated_gpu_bytes=torch.cuda.max_memory_allocated(),device=torch.cuda.get_device_name(),
        torch_version=torch.__version__,tf32=False,seconds=time.monotonic()-started,
        artifacts={p.relative_to(ROOT).as_posix():sha(p) for p in (queries_path,policies_path,updates_path,
            weights_path,rust_path,fitted_path,fitted_updates)},
        physical_poker_convergence_qualified=False,production_modified=False)
    save(output('result'),result);print(json.dumps(result),flush=True)


def main():
    assert idle()
    prior=OUT/'sampled-physical-stream-fit-v1-result.json';assert json.loads(prior.read_text())['passed']
    paths=[Path(__file__),prior]+[ROOT/'tools/research'/p for p in ('sampled_batch_model_v1.py',
        'sampled_batch_protocol_v2.py','sampled_physical_reservoir_v1.py','sampled_physical_fit_v1.py',
        'loopback_research_validation.py')]+[OUT/p for p in ('sampled-physical-stream-fit-v1-weights.json',
        'bb-context-candidate.json','sampled-batch-bridge-v2-batch.json')]
    paths += [ROOT/'target/release/examples'/p for p in ('hu_sampled_batch_bridge_v2.exe','hu_sampled_physical_fit_control.exe')]
    paths += [ROOT/'crates/solver/examples'/p for p in ('hu_sampled_batch_bridge_v2.rs','hu_sampled_physical_fit_control.rs',
        'research_sampled/state.rs','research_sampled/poker_reference_v1.rs','research_sampled/observation_v1.rs',
        'research_sampled/network_v1.rs','research_sampled/policy_walk_v1.rs','research_sampled/batch_queries_v1.rs')]
    frozen={p.relative_to(ROOT).as_posix():sha(p) for p in paths}
    reg=dict(inputs=frozen,maximum_seconds=300,queue_limit_seconds=14400,capacity=257,steps=64,
        repeated_fixture_batches=3,chunk_size=31,fit_seeds=[6301,6302],reservoir_seeds=[5301,5302],
        tolerances=dict(score=2e-5,policy=1e-4,gradient_absolute=1e-5),
        scope='Combined physical CUDA data path and fixed-data fitting control; not fresh self-play or strategic qualification.',
        queue_rule='Wait behind a live GPU-lock owner; cancel on production activity, stale lock, changed input or deadline. No automatic retry.',
        production_modified=False,tf32=False)
    regpath=output('registration');save(regpath,reg)
    queued=time.monotonic();child=None;acquired=False;error=None;samples=[];started=None
    save(output('status'),dict(state='queued',controller_pid=os.getpid(),production_modified=False))
    try:
        while LOCK.exists() or OTHER_LOCK.exists():
            assert '--wait' in sys.argv,'GPU reserved; explicit queue flag required'
            assert time.monotonic()-queued<reg['queue_limit_seconds'] and idle(),'Queue deadline or production activity'
            for lock in (LOCK,OTHER_LOCK):
                try:owner=int(lock.read_text().strip())
                except FileNotFoundError:continue
                assert psutil.pid_exists(owner),'Stale GPU lock; owner must be inspected'
            time.sleep(2)
        assert idle() and psutil.virtual_memory().available>=20_000_000_000
        for name,h in frozen.items():assert sha(ROOT/name)==h,name
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;started=time.monotonic()
        save(output('status'),dict(state='running',controller_pid=os.getpid(),queue_seconds=started-queued),False)
        env=os.environ.copy();env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='2')
        with (OUT/(PREFIX+'.log')).open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__)),'--worker',str(regpath)],cwd=ROOT,
                env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2);elapsed=time.monotonic()-started
                assert elapsed<reg['maximum_seconds'] and idle(),'Deadline or production activity'
                host=psutil.virtual_memory().available
                gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2
                samples.append(dict(seconds=elapsed,host_free_bytes=host,gpu_free_bytes=gpu))
                assert host>=20_000_000_000 and gpu>=3_000_000_000,'Memory reserve reached'
        assert child.returncode==0,f'Worker failed {child.returncode}; preserve evidence, no retry'
        for name,h in frozen.items():assert sha(ROOT/name)==h,name
        resultpath=output('result');result=json.loads(resultpath.read_text());assert result['passed']
        for name,h in result['artifacts'].items():assert sha(ROOT/name)==h,name
        save(output('review'),dict(passed=True,inputs_verified=len(frozen),registration_sha256=sha(regpath),
            result_sha256=sha(resultpath),artifacts_verified=len(result['artifacts']),
            physical_poker_convergence_qualified=False,production_modified=False))
    except Exception as ex:error=str(ex);raise
    finally:
        if child is not None and child.poll() is None:
            descendants=psutil.Process(child.pid).children(recursive=True)
            for p in reversed(descendants):
                try:p.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)
        save(output('status'),dict(state='failed' if error else 'complete',error=error,
            exit_code=child.returncode if child else None,total_seconds=time.monotonic()-queued,
            production_modified=False),False)
        save(output('resources'),samples)
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    if '--worker' in sys.argv:worker(json.loads(Path(sys.argv[-1]).read_text()))
    else:main()
