"""Bounded full-deck physical self-play pilot; never a production promotion."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np
import psutil
from hu_sampled_neural_residual_diagnostic_20260922 import ROOT, OUT, sha, save
from loopback_research_validation import idle
from sampled_batch_model_v1 import predict
from sampled_batch_protocol_v2 import policy_document
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import PhysicalReservoir, ingest
from sampled_physical_fit_v1 import fit
from sampled_physical_checkpoint_v1 import uniform_networks, write_model, model_document, save_checkpoint

PREFIX='sampled-physical-pilot-gpu-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
STORE=Path('S:/GTOpen-research')/PREFIX


def output(suffix):return OUT/(PREFIX+'-'+suffix+'.json')


def status(document):
    path=output('status');temporary=path.with_suffix('.tmp')
    with temporary.open('x',encoding='utf-8',newline='\n') as f:f.write(json.dumps(document,indent=2)+'\n')
    temporary.replace(path)


def free_gpu():
    return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2


def worker(reg):
    import torch
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    config=reg['config'];device=config['device'];assert device in ('cpu','cuda')
    if device=='cuda':assert torch.cuda.is_available()
    context_path=OUT/'bb-context-candidate.json';context=context_path.read_text()
    config=dict(config,torch_version=torch.__version__,numpy_version=np.__version__,device_name=torch.cuda.get_device_name() if device=='cuda' else 'cpu')
    save(output('environment'),config)
    STORE.mkdir(parents=True,exist_ok=False);objects=STORE/'checkpoint-objects';objects.mkdir()
    sampler=PhysicalDeals(context,mode='full_deck',seed=config['sampler_seed'])
    action_rng=np.random.Generator(np.random.PCG64(config['action_seed']))
    reservoirs=[PhysicalReservoir(config['reservoir_capacity'],p,config['reservoir_seeds'][p],context) for p in (0,1)]
    bank=[];current=write_model(objects,0,uniform_networks(),[1.,1.]);metrics=[]
    started=time.monotonic();last_guard=0.;last_checkpoint=None
    def guard():
        nonlocal last_guard
        now=time.monotonic()
        if now-last_guard>=2:
            assert now-started<reg['maximum_seconds'] and idle(),'Pilot deadline or production activity'
            assert psutil.virtual_memory().available>=reg['host_reserve_bytes']
            assert shutil.disk_usage(STORE).free>=reg['disk_reserve_bytes']
            last_guard=now
    exe=ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe'
    # Save the initial state too: an interrupted first iteration has a boundary.
    last_checkpoint=save_checkpoint(objects,completed=0,context_source=context,config=config,
        sampler=sampler,action_rng=action_rng,reservoirs=reservoirs,bank=bank,current=current)
    save(STORE/'checkpoint-0000.json',last_checkpoint)
    for iteration in range(1,config['max_iterations']+1):
        guard();began=time.monotonic();folder=STORE/f'iteration-{iteration:04d}';folder.mkdir()
        batch=dict(format=2,batch_id=f'{PREFIX}-iteration-{iteration}',query_limit=config['query_limit'],
            seed=int(action_rng.integers(0,2**63)),deals=sampler.sample(config['deals_per_iteration'])['deals'])
        batch_path=folder/'batch.json';queries_path=folder/'queries.json';policies_path=folder/'policies.json';updates_path=folder/'updates.json'
        save(batch_path,batch)
        def invoke(mode,policy,path):
            guard();completed=subprocess.run([str(exe),mode,str(context_path),str(batch_path),str(policy),str(path)],
                cwd=ROOT,timeout=120,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
            assert completed.returncode==0,completed.stderr[-2000:]
        invoke('queries','-',queries_path);queries=json.loads(queries_path.read_text())
        networks=model_document(objects,current)['networks'];used=current
        _,probabilities=predict(queries['observations'],networks,device)
        save(policies_path,policy_document(queries,probabilities));invoke('verify',policies_path,updates_path)
        updates=json.loads(updates_path.read_text())
        assert updates['verified_traversals']==2*config['deals_per_iteration'] and updates['maximum_reference_error']==0
        counts=ingest(queries,updates,reservoirs,iteration)
        fits=[];networks=[]
        for player,reservoir in enumerate(reservoirs):
            network,metric=fit(reservoir,seed=config['fit_seed_base']+iteration*200003+player,
                steps=config['fit_steps'],device=device,chunk_size=config['chunk_size'],guard=guard,
                learning_rate=config['learning_rate'])
            networks.append(network);fits.append(metric)
        current=write_model(objects,iteration,networks,[m['advantage_scale'] for m in fits]);bank.append(used)
        last_checkpoint=save_checkpoint(objects,completed=iteration,context_source=context,config=config,
            sampler=sampler,action_rng=action_rng,reservoirs=reservoirs,bank=bank,current=current)
        save(STORE/f'checkpoint-{iteration:04d}.json',last_checkpoint)
        row=dict(iteration=iteration,seconds=time.monotonic()-began,total_seconds=time.monotonic()-started,
            deals=config['deals_per_iteration'],observations=len(queries['observations']),advantage_records=counts,
            reservoirs=[r.summary() for r in reservoirs],fits=fits,checkpoint=last_checkpoint,
            artifacts={p.name:sha(p) for p in (batch_path,queries_path,policies_path,updates_path)})
        metrics.append(row);save(folder/'metrics.json',row)
        # An atomic pointer references only a fully published completed boundary.
        pointer=STORE/'latest.json';temporary=STORE/'latest.tmp'
        save(temporary,dict(completed_iterations=iteration,checkpoint=last_checkpoint,config=config));temporary.replace(pointer)
        print(json.dumps(dict(iteration=iteration,seconds=row['seconds'],observations=row['observations'],
                              retained=[r.size for r in reservoirs])),flush=True)
    save(output('result'),dict(terminal=True,completed_iterations=len(metrics),config=config,store=str(STORE),
        checkpoint=last_checkpoint,steps=metrics,seconds=time.monotonic()-started,
        physical_poker_convergence_qualified=False,production_modified=False,
        scope='Training/resource pilot. No fresh held-out strength evaluation or best-response certificate.'))


def main():
    assert '--queue' in sys.argv and idle() and not STORE.exists()
    cpu=OUT/'sampled-neural-mean-cpu-v1-independent-review.json'
    assert json.loads(cpu.read_text())['all_four_finite_targets_passed']
    prior_names=['sampled-physical-stream-fit-v1-result.json','sampled-physical-deals-v1-result.json',
        'sampled-physical-checkpoint-v1-result.json','sampled-physical-bank-bridge-v1-result.json',
        'sampled-profile-evaluation-v1-result.json','sampled-physical-pilot-controller-v1-review.json']
    prerequisites=[OUT/n for n in prior_names]
    assert all(json.loads(p.read_text())['passed'] for p in prerequisites)
    gpu_reg=OUT/'sampled-neural-mean-gpu-v1-registration.json'
    pipeline_reg=OUT/'sampled-physical-pipeline-gpu-v1-registration.json'
    paths=[Path(__file__),cpu,gpu_reg,pipeline_reg,*prerequisites,OUT/'bb-context-candidate.json',
           ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe']
    paths += [ROOT/'tools/research'/n for n in ('sampled_batch_model_v1.py','sampled_batch_protocol_v2.py',
        'sampled_physical_deals_v1.py','sampled_physical_reservoir_v1.py','sampled_physical_fit_v1.py',
        'sampled_physical_checkpoint_v1.py','storage_strategic_common_prior_20260920.py',
        'loopback_research_validation.py','hu_sampled_neural_residual_diagnostic_20260922.py')]
    paths += [ROOT/'crates/solver/examples'/n for n in ('hu_sampled_batch_bridge_v2.rs',
        'research_sampled/state.rs','research_sampled/poker_reference_v1.rs','research_sampled/observation_v1.rs',
        'research_sampled/policy_walk_v1.rs','research_sampled/batch_queries_v1.rs')]
    reg=dict(inputs={p.relative_to(ROOT).as_posix():sha(p) for p in paths},maximum_seconds=3600,
        queue_limit_seconds=14400,host_reserve_bytes=20_000_000_000,gpu_reserve_bytes=3_000_000_000,
        disk_reserve_bytes=40_000_000_000,maximum_store_bytes=40_000_000_000,store=str(STORE),
        config=dict(max_iterations=128,deals_per_iteration=64,query_limit=100000,fit_steps=512,
            fit_seed_base=19301,reservoir_capacity=262144,sampler_seed=17301,action_seed=18301,
            reservoir_seeds=[18302,18303],chance='full_deck',device='cuda',threads=2,tf32=False,
            architecture=[269,64,64,4],chunk_size=4096,learning_rate=.003,iteration_weights='equal'),
        admission='Wait for the finite GPU run to become terminal and the combined CUDA pipeline to pass; preserve and hash both outcomes. CPU finite comparison must have all four passes. No claiming GPU strategic qualification from these conditions.',
        stopping='128 iterations or one-hour execution ceiling; stop on production activity, resource limit, changed input, failed prerequisite or error. Preserve completed checkpoints; no automatic extension or retry.',
        scope='First bounded fresh full-deck physical training/resource pilot, with complete saved BB/BTN support and unchanged action tree. GPU finite accuracy is not qualified; this diagnostic is not a promotion.',
        evaluation='No test-deal outcomes inspected during training. Subsequent strength evaluation needs separate independently frozen policies/responders/chance law and fresh draws.',
        production_modified=False)
    regpath=output('registration');save(regpath,reg)
    queued=time.monotonic();child=None;acquired=False;error=None;started=None;resources=[]
    status(dict(state='queued',controller_pid=os.getpid(),production_modified=False))
    try:
        gpu_status=OUT/'sampled-neural-mean-gpu-v1-status.json'
        pipeline_status=OUT/'sampled-physical-pipeline-gpu-v1-status.json'
        pipeline_review=OUT/'sampled-physical-pipeline-gpu-v1-review.json'
        while True:
            assert time.monotonic()-queued<reg['queue_limit_seconds'] and idle(),'Queue deadline or production activity'
            ps=json.loads(pipeline_status.read_text())
            assert ps['state']!='failed','Combined CUDA prerequisite failed; no pilot'
            if gpu_status.exists() and ps['state']=='complete' and pipeline_review.exists() and not LOCK.exists() and not OTHER.exists():break
            for lock in (LOCK,OTHER):
                try:owner=int(lock.read_text().strip())
                except FileNotFoundError:continue
                assert psutil.pid_exists(owner),'Stale GPU lock; inspect owner'
            time.sleep(2)
        assert json.loads(pipeline_review.read_text())['passed']
        for name,digest in reg['inputs'].items():assert sha(ROOT/name)==digest,name
        assert psutil.virtual_memory().available>=reg['host_reserve_bytes'] and free_gpu()>=reg['gpu_reserve_bytes']
        assert shutil.disk_usage(STORE.anchor).free>=reg['disk_reserve_bytes']+reg['maximum_store_bytes']
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;started=time.monotonic()
        # Bind the completed upstream outcomes before any physical training draw.
        save(output('admission'),dict(prerequisites={p.relative_to(ROOT).as_posix():sha(p) for p in (gpu_status,pipeline_status,pipeline_review)},
             finite_gpu_outcome=json.loads(gpu_status.read_text()),pipeline_passed=True,
             gpu_strategic_target_qualified=False,registration_sha256=sha(regpath)))
        status(dict(state='running',controller_pid=os.getpid(),production_modified=False))
        env=os.environ.copy();env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',PYTHONUNBUFFERED='1',OMP_NUM_THREADS='2')
        with (OUT/(PREFIX+'.log')).open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__)),'--worker',str(regpath)],cwd=ROOT,env=env,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            last_resource=0.
            while child.poll() is None:
                time.sleep(2);elapsed=time.monotonic()-started
                assert elapsed<reg['maximum_seconds'] and idle(),'Execution deadline or production activity'
                if elapsed-last_resource>=10:
                    host=psutil.virtual_memory().available;gpu=free_gpu();disk=shutil.disk_usage(STORE.anchor).free
                    used=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) if STORE.exists() else 0
                    resources.append(dict(seconds=elapsed,free_host_bytes=host,free_gpu_bytes=gpu,free_disk_bytes=disk,store_bytes=used))
                    assert host>=reg['host_reserve_bytes'] and gpu>=reg['gpu_reserve_bytes'] and disk>=reg['disk_reserve_bytes'] and used<=reg['maximum_store_bytes'],'Resource reserve or storage limit'
                    last_resource=elapsed
        assert child.returncode==0,f'Worker exited {child.returncode}; preserve checkpoints, no retry'
        for name,digest in reg['inputs'].items():assert sha(ROOT/name)==digest,name
        result=json.loads(output('result').read_text());assert result['terminal'] and result['completed_iterations']==reg['config']['max_iterations']
    except Exception as exc:error=str(exc);raise
    finally:
        if child is not None and child.poll() is None:
            for descendant in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:descendant.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)
        status(dict(state='stopped' if error else 'complete',error=error,exit_code=child.returncode if child else None,
                    total_seconds=time.monotonic()-queued,store=str(STORE),production_modified=False))
        save(output('resources'),resources)
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':
    if '--worker' in sys.argv:worker(json.loads(Path(sys.argv[-1]).read_text()))
    else:main()
