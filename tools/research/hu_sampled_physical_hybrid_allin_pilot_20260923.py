"""Combined direct-preflop and exact-all-in trial; independent control admission."""
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
from sampled_allin_protocol_v3 import policy_document, ingest, AllinCache, ESTIMATOR
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_physical_fit_cuda_cached_v1 import fit
from sampled_physical_hybrid_checkpoint_v1 import uniform_networks, write_model, model_document, save_checkpoint

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
CONTROL = '--control' in sys.argv
PREFIX = 'sampled-physical-hybrid-allin-' + ('control-v1' if CONTROL else 'pilot-v1')
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
    cache = AllinCache.from_review(OUT/'sampled-physical-allin-training-cache-v1-independent-review.json')
    assert cache.sha256 == config['allin_cache_sha256'] and config['terminal_estimator'] == ESTIMATOR
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
    exe = ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe'
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
            batch = cache.batch(batch)
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
            assert updates['verified_query_lookup_traversals'] == updates['verified_cashflow_traversals'] == 2*config['deals_per_subbatch']
            assert updates['maximum_query_lookup_error'] == 0 and updates['maximum_cashflow_error'] < 1e-9
            counts = ingest(queries,updates,reservoirs,iteration,cache)
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
        scope='Direct retained preflop means combined with exact conditional preflop all-in targets. Neural postflop unchanged; complete played bank only. No accuracy qualification or deployment.'))


def main():
    assert '--run' in sys.argv and idle() and not STORE.exists()
    assert not LOCK.exists() and not OTHER.exists()
    parents = [OUT/'sampled-physical-hybrid-pilot-v1-registration.json',
        OUT/'sampled-physical-allin-pilot-v1-registration.json']
    documents = [json.loads(p.read_text()) for p in parents]
    for document in documents: verify(document)
    cache_review_path = OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    cache = AllinCache.from_review(cache_review_path)
    input_paths = [*parents,cache_review_path,Path(__file__),
        ROOT/'tools/research/hu_sampled_physical_hybrid_allin_review_20260923.py',
        OUT/'SAMPLED-PHYSICAL-HYBRID-ALLIN-PLAN.md']
    for document in documents: input_paths += [ROOT/p for p in document['inputs']]
    for prefix in ('sampled-physical-hybrid-pilot-v1','sampled-physical-allin-pilot-v1'):
        path = OUT/f'{prefix}-independent-review.json'; review = json.loads(path.read_text())
        assert review['passed'] and review['terminal_complete']
        assert review['source_registration_sha256'] == sha(OUT/f'{prefix}-registration.json')
        input_paths += [path]
    cfg = dict(documents[1]['config'])
    for k,v in documents[0]['config'].items(): assert cfg[k] == v,k
    assert cfg['allin_cache_sha256'] == cache.sha256 and cfg['terminal_estimator'] == ESTIMATOR
    if CONTROL:
        cfg['max_iterations'] = 4
    else:
        path = OUT/'sampled-physical-hybrid-allin-control-v1-independent-review.json'
        control = json.loads(path.read_text())
        assert control['passed'] and control['terminal_complete'] and control['completed_iterations'] == 4
        assert control['all_generated_tables_reconstructed'] and control['all_supported_preflop_policy_rows_exact']
        for p,h in control['evidence_hashes'].items(): assert sha(p) == h,p
        control_reg_path = OUT/'sampled-physical-hybrid-allin-control-v1-registration.json'
        assert control['source_registration_sha256'] == sha(control_reg_path)
        verify(json.loads(control_reg_path.read_text()))
        input_paths += [path,control_reg_path]
    reg = dict(inputs={str(p):sha(p) for p in set(input_paths)},config=cfg,
        maximum_seconds=10800,host_reserve_bytes=20_000_000_000,gpu_reserve_bytes=3_000_000_000,
        disk_reserve_bytes=40_000_000_000,maximum_store_bytes=40_000_000_000,store=str(STORE),
        control_only=CONTROL,
        candidate='Control: four updates, never a candidate. Trial: exactly 78 full updates; equal-weight own-reach average of played generations 0..77, unused model 78 excluded.',
        changes='Combine previously separate direct retained preflop tables and exact conditional private-pair preflop all-in labels. Original hybrid sampler, seeds, fit, reservoirs, postflop menus and averaging unchanged.',
        stopping='Fixed count or three-hour cap; stop for production activity, resources or integrity failure. No automatic retries or extensions.',
        evaluation='Candidate only: fresh response-training/test seeds 89101/89102, 8192/16384 deals, original sampled-board evaluator. Five BB-root alternatives family alpha .025; three BTN-vs-jam alternatives family alpha .025. Full-bank float64 CPU/CUDA checks before evaluation. No intermediate or test-driven selection. Conditional evaluation is a separate future study, not a replacement for this registered test.',
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
            child = subprocess.Popen([sys.executable,str(Path(__file__)),*(['--control'] if CONTROL else []),'--worker',str(regpath)],cwd=ROOT,
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
