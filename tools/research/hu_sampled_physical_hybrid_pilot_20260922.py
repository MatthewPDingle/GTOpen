"""Prepared direct-preflop hybrid trial; admit only after dense evaluation and GPU control."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np
import psutil

from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from loopback_research_validation import idle
from sampled_physical_hybrid_policy_v1 import probabilities as hybrid_probabilities
from sampled_physical_preflop_table_v1 import build
from sampled_batch_protocol_v2 import policy_document
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import PhysicalReservoir, ingest
from sampled_physical_fit_cuda_cached_v1 import fit
from sampled_physical_hybrid_checkpoint_v1 import uniform_networks, write_model, model_document, save_checkpoint

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-hybrid-pilot-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def output(suffix): return OUT/f'{PREFIX}-{suffix}.json'


def verify(reg):
    for name,digest in reg['inputs'].items(): assert sha(ROOT/name) == digest, name


def status(document):
    path = output('status'); tmp = path.with_suffix('.tmp')
    save(tmp,document); tmp.replace(path)


def free_gpu():
    return int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free',
        '--format=csv,noheader,nounits'],text=True).splitlines()[0])*1024**2


def worker(reg):
    import torch
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    assert torch.cuda.is_available()
    verify(reg)
    config = dict(reg['config'],torch_version=torch.__version__,numpy_version=np.__version__,
                  device_name=torch.cuda.get_device_name())
    save(output('environment'),config)
    context_path = OUT/'bb-context-candidate.json'; context = context_path.read_text()
    STORE.mkdir(parents=True,exist_ok=False); objects = STORE/'checkpoint-objects'; objects.mkdir()
    sampler = PhysicalDeals(context,mode='full_deck',seed=config['sampler_seed'])
    action_rng = np.random.Generator(np.random.PCG64(config['action_seed']))
    reservoirs = [PhysicalReservoir(config['reservoir_capacity'],p,config['reservoir_seeds'][p],context) for p in (0,1)]
    bank = []; current = write_model(objects,0,uniform_networks(),[1.,1.],[None,None],context_source=context); metrics = []
    started = time.monotonic(); last_guard = 0.

    def guard():
        nonlocal last_guard
        now = time.monotonic()
        if now-last_guard >= 2:
            assert now-started < reg['maximum_seconds'] and idle(), 'Deadline or production activity'
            assert psutil.virtual_memory().available >= reg['host_reserve_bytes']
            assert shutil.disk_usage(STORE).free >= reg['disk_reserve_bytes']
            assert torch.cuda.mem_get_info()[0] >= reg['gpu_reserve_bytes']
            last_guard = now

    guard()
    exe = ROOT/'target/release/examples/hu_sampled_batch_bridge_v2.exe'
    checkpoint = save_checkpoint(objects,completed=0,context_source=context,config=config,sampler=sampler,
        action_rng=action_rng,reservoirs=reservoirs,bank=bank,current=current)
    save(STORE/'checkpoint-0000.json',checkpoint)
    for iteration in range(1,config['max_iterations']+1):
        guard(); began = time.monotonic(); folder = STORE/f'iteration-{iteration:04d}'; folder.mkdir()
        # Every subbatch and both updater passes use this same pair of models.
        used = current; model = model_document(objects,used,context_source=context); chunks = []
        total_counts = [0,0]; total_observations = 0
        for chunk in range(config['subbatches_per_iteration']):
            guard(); part = folder/f'batch-{chunk:02d}'; part.mkdir()
            batch = dict(format=2,batch_id=f'{PREFIX}-iteration-{iteration}-batch-{chunk}',
                query_limit=config['query_limit'],seed=int(action_rng.integers(0,2**63)),
                deals=sampler.sample(config['deals_per_subbatch'])['deals'])
            batch_path = part/'batch.json'; query_path = part/'queries.json'
            policy_path = part/'policies.json'; update_path = part/'updates.json'; save(batch_path,batch)

            def invoke(mode,policy,destination):
                guard()
                done = subprocess.run([str(exe),mode,str(context_path),str(batch_path),str(policy),str(destination)],
                    cwd=ROOT,timeout=120,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
                assert done.returncode == 0, done.stderr[-2000:]

            invoke('queries','-',query_path); queries = json.loads(query_path.read_text())
            probabilities,covered = hybrid_probabilities(queries,model,'cuda')
            save(policy_path,policy_document(queries,probabilities)); invoke('verify',policy_path,update_path)
            updates = json.loads(update_path.read_text())
            assert updates['verified_traversals'] == 2*config['deals_per_subbatch']
            assert updates['maximum_reference_error'] == 0
            counts = ingest(queries,updates,reservoirs,iteration)
            total_counts = [a+b for a,b in zip(total_counts,counts)]; total_observations += len(queries['observations'])
            chunks.append(dict(chunk=chunk,used_model=used,observations=len(queries['observations']),
                advantage_records=counts,preflop_table_queries=covered,artifacts={p.name:sha(p) for p in (batch_path,query_path,policy_path,update_path)}))
        fits = []; trained = []
        for player,reservoir in enumerate(reservoirs):
            net,metric = fit(reservoir,seed=config['fit_seed_base']+iteration*200003+player,
                steps=config['fit_steps'],device='cuda',chunk_size=config['chunk_size'],guard=guard,
                learning_rate=config['learning_rate'])
            trained.append(net); fits.append(metric)
        tables = [build(r,context) for r in reservoirs]
        current = write_model(objects,iteration,trained,[m['advantage_scale'] for m in fits],tables,context_source=context); bank.append(used)
        checkpoint = save_checkpoint(objects,completed=iteration,context_source=context,config=config,sampler=sampler,
            action_rng=action_rng,reservoirs=reservoirs,bank=bank,current=current)
        save(STORE/f'checkpoint-{iteration:04d}.json',checkpoint)
        row = dict(iteration=iteration,seconds=time.monotonic()-began,total_seconds=time.monotonic()-started,
            deals=config['deals_per_iteration'],observations=total_observations,advantage_records=total_counts,
            subbatches=chunks,reservoirs=[r.summary() for r in reservoirs],fits=fits,checkpoint=checkpoint)
        save(folder/'metrics.json',row); metrics.append(row)
        tmp = STORE/'latest.tmp'; save(tmp,dict(completed_iterations=iteration,checkpoint=checkpoint,config=config)); tmp.replace(STORE/'latest.json')
        print(json.dumps(dict(iteration=iteration,seconds=row['seconds'],fresh_deals=sampler.draws,
            retained=[r.size for r in reservoirs],seen=[r.seen for r in reservoirs])),flush=True)
    verify(reg)
    save(output('result'),dict(terminal=True,completed_iterations=len(metrics),config=config,store=str(STORE),
        checkpoint=checkpoint,steps=metrics,seconds=time.monotonic()-started,
        physical_poker_convergence_qualified=False,production_modified=False,
        scope='Direct retained preflop means and unchanged neural postflop prediction. No strength evaluation or promotion. Full played hybrid bank only.'))


def main():
    assert '--run' in sys.argv and idle() and not STORE.exists()
    assert not LOCK.exists() and not OTHER.exists()
    oldpath = OUT/'sampled-physical-dense-pilot-v1-registration.json'; old = json.loads(oldpath.read_text())
    prerequisite_paths = [OUT/'sampled-physical-dense-pilot-v1-independent-review.json',
        OUT/'sampled-physical-dense-evaluation-v1-independent-review.json',
        OUT/'sampled-physical-preflop-table-control-v1-result.json',
        OUT/'sampled-physical-hybrid-checkpoint-control-v1-result.json',
        OUT/'sampled-physical-hybrid-gpu-control-v1-result.json',
        OUT/'sampled-physical-hybrid-policy-control-v1-result.json']
    for p in prerequisite_paths:
        prerequisite = json.loads(p.read_text()); assert prerequisite['passed'], str(p)
    assert json.loads(prerequisite_paths[0].read_text())['terminal_complete']
    gpu_control = json.loads(prerequisite_paths[4].read_text())
    gpu_regpath = OUT/'sampled-physical-hybrid-gpu-control-v1-registration.json'
    gpu_reg = json.loads(gpu_regpath.read_text())
    assert gpu_control['registration_sha256'] == sha(gpu_regpath)
    for p,h in gpu_reg['inputs'].items(): assert sha(p) == h,p
    for p,h in gpu_control['artifacts'].items(): assert sha(p) == h,p
    gpu_review_path = OUT/'sampled-physical-hybrid-gpu-control-v1-independent-review.json'
    gpu_review = json.loads(gpu_review_path.read_text())
    assert gpu_review['passed'] and gpu_review['registration_sha256'] == sha(gpu_regpath)
    assert gpu_review['result_sha256'] == sha(prerequisite_paths[4])
    assert gpu_review['reviewer_sha256'] == sha(ROOT/'tools/research/hu_sampled_physical_hybrid_gpu_review_20260922.py')
    adapter_path = OUT/'sampled-physical-hybrid-evaluation-v1-adapter-control.json'
    adapter = json.loads(adapter_path.read_text()); assert adapter['passed']
    for p,h in adapter['inputs'].items(): assert sha(p) == h,p
    policy_regpath = OUT/'sampled-physical-hybrid-policy-control-v1-registration.json'
    policy_reg = json.loads(policy_regpath.read_text())
    assert json.loads(prerequisite_paths[5].read_text())['registration_sha256'] == sha(policy_regpath)
    for p,h in policy_reg['inputs'].items(): assert sha(p) == h,p
    control = OUT/'sampled-physical-cached-fit-v1-independent-review.json'
    assert json.loads(control.read_text())['exported_weights_exactly_equal']
    input_paths = [ROOT/name for name in old['inputs']]
    input_paths += [oldpath,control,OUT/'sampled-physical-cached-fit-v1-registration.json',
        OUT/'sampled-physical-cached-fit-v1-result.json',OUT/'sampled-physical-cached-fit-v1-review.json',
        OUT/'sampled-physical-pilot-gpu-v1-independent-review.json',
        OUT/'sampled-physical-root-study-gpu-v1-independent-review.json',
        OUT/'SAMPLED-PHYSICAL-HYBRID-PLAN.md',Path(__file__),
        *prerequisite_paths,gpu_regpath,policy_regpath,gpu_review_path,
        ROOT/'tools/research/hu_sampled_physical_hybrid_gpu_review_20260922.py',
        ROOT/'tools/research/sampled_physical_hybrid_evaluation_v1.py',
        ROOT/'tools/research/hu_sampled_physical_hybrid_evaluation_20260922.py',
        ROOT/'tools/research/hu_sampled_physical_hybrid_evaluation_review_20260922.py',
        adapter_path,ROOT/'tools/research/hu_sampled_physical_hybrid_evaluation_control_20260922.py',
        ROOT/'tools/research/sampled_physical_hybrid_policy_v1.py',
        ROOT/'tools/research/sampled_physical_hybrid_checkpoint_v1.py',
        ROOT/'tools/research/sampled_physical_preflop_table_v1.py',
        ROOT/'tools/research/hu_sampled_physical_hybrid_review_20260922.py',
        ROOT/'tools/research/sampled_physical_fit_cuda_cached_v1.py']
    verify(old)
    cfg = dict(old['config'],max_iterations=78,deals_per_iteration=512,
        subbatches_per_iteration=8,deals_per_subbatch=64)
    reg = dict(inputs={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in input_paths},config=cfg,
        maximum_seconds=10800,host_reserve_bytes=20_000_000_000,gpu_reserve_bytes=3_000_000_000,
        disk_reserve_bytes=40_000_000_000,maximum_store_bytes=40_000_000_000,store=str(STORE),
        candidate='Exactly 78 complete iterations; equal-weight own-reach average of played models 0..77. Model 78 unused. An incomplete run is not a substitute candidate.',
        changes='Direct regret matching on retained means at observed preflop information sets; neural fallback for missing rows and unchanged neural postflop. Same game, support, fresh-deal schedule, seeds, fitting objective, architecture, steps and reservoir cap as dense trial.',
        stopping='78 iterations or three-hour execution cap, production activity, resource or integrity failure. No automatic extension or retry; only complete iteration checkpoints are publishable.',
        evaluation='Separate audited evaluation after completion. Reserve seeds 69101 for response training and 69102 for held-out test, 8192/16384 deals and the same five root-deviation comparisons. No inspected prior test reuse and no intermediate quality-based selection.',
        production_modified=False)
    assert cfg['deals_per_iteration'] == cfg['subbatches_per_iteration']*cfg['deals_per_subbatch']
    assert psutil.virtual_memory().available >= reg['host_reserve_bytes'] and free_gpu() >= reg['gpu_reserve_bytes']
    assert shutil.disk_usage(STORE.anchor).free >= reg['disk_reserve_bytes']+reg['maximum_store_bytes']
    regpath = output('registration'); save(regpath,reg)
    child = None; acquired = False; error = None; resources = []; started = time.monotonic()
    try:
        with LOCK.open('x') as f: f.write(str(os.getpid()))
        acquired = True; verify(reg)
        save(output('admission'),dict(controller_pid=os.getpid(),registration_sha256=sha(regpath),production_modified=False))
        env = os.environ.copy(); env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',OMP_NUM_THREADS='2',PYTHONUNBUFFERED='1')
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child = subprocess.Popen([sys.executable,str(Path(__file__)),'--worker',str(regpath)],cwd=ROOT,
                env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            status(dict(state='running',controller_pid=os.getpid(),worker_pid=child.pid,production_modified=False))
            last_resource = 0.
            while child.poll() is None:
                time.sleep(2); elapsed = time.monotonic()-started
                assert elapsed < reg['maximum_seconds'], 'Execution deadline'
                assert idle(), 'Production activity'
                if elapsed-last_resource >= 10:
                    host = psutil.virtual_memory().available; gpu = free_gpu(); disk = shutil.disk_usage(STORE.anchor).free
                    used = sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) if STORE.exists() else 0
                    resources.append(dict(seconds=elapsed,free_host_bytes=host,free_gpu_bytes=gpu,free_disk_bytes=disk,store_bytes=used))
                    assert host >= reg['host_reserve_bytes'] and gpu >= reg['gpu_reserve_bytes'] and disk >= reg['disk_reserve_bytes'] and used <= reg['maximum_store_bytes'], 'Resource reserve or storage limit'
                    last_resource = elapsed
        assert child.returncode == 0, f'Worker exited {child.returncode}; inspect log, no retry'
        verify(reg); result = json.loads(output('result').read_text())
        assert result['terminal'] and result['completed_iterations'] == cfg['max_iterations']
    except Exception as exc:
        error = str(exc); raise
    finally:
        if child is not None and child.poll() is None:
            for descendant in reversed(psutil.Process(child.pid).children(recursive=True)):
                try: descendant.terminate()
                except psutil.NoSuchProcess: pass
            child.terminate(); child.wait(timeout=20)
        status(dict(state='stopped' if error else 'complete',error=error,exit_code=child.returncode if child else None,
            execution_seconds=time.monotonic()-started,store=str(STORE),production_modified=False))
        save(output('resources'),resources)
        if acquired:
            assert LOCK.read_text().strip() == str(os.getpid()); LOCK.unlink()


if __name__ == '__main__':
    if '--worker' in sys.argv: worker(json.loads(Path(sys.argv[-1]).read_text()))
    else: main()
