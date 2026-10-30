"""Fresh fixed-budget training bank for the prospective averaging comparison."""
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
from reboot_research_idle_v1 import idle
from later_average_support_v1 import load_complete_cache
from sampled_visible_hybrid_policy_v1 import probabilities as hybrid_probabilities
from sampled_physical_preflop_table_v1 import build
from sampled_allin_protocol_v3 import policy_document, ingest, AllinCache, ESTIMATOR
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_visible_hybrid_fit_v1 import fit
from sampled_visible_hybrid_checkpoint_v1 import uniform_networks, write_model, model_document, save_checkpoint, FEATURE_SPEC

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
CONTROL = False
PREFIX = 'later-average-fresh-pilot-v1'
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
    cache = load_complete_cache()
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
        scope='Fresh fixed-budget bank for two predeclared output averages; training targets and reservoir weighting unchanged. Accuracy unqualified.'))


def main():
    global PREFIX, STORE, CONTROL
    CONTROL = '--control' in sys.argv
    PREFIX = 'later-average-fresh-control-v1' if CONTROL else 'later-average-fresh-pilot-v1'
    STORE = Path('S:/GTOpen-research')/PREFIX
    if '--worker' in sys.argv:
        worker(json.loads(Path(sys.argv[-1]).read_text())); return
    assert '--run' in sys.argv and idle() and not STORE.exists()
    assert not LOCK.exists() and not OTHER.exists()
    basepath = OUT/'sampled-visible-hybrid-trial-pilot-v1-registration.json'
    base = json.loads(basepath.read_text()); verify(base)
    cfg = dict(base['config'], max_iterations=4 if CONTROL else 78,
        sampler_seed=131301 if CONTROL else 121301, action_seed=131302 if CONTROL else 121302,
        reservoir_seeds=[131303,131304] if CONTROL else [121303,121304],
        fit_seed_base=131305 if CONTROL else 121305)
    cache = load_complete_cache(); cfg['allin_cache_sha256'] = cache.sha256
    assert cfg['iteration_weights'] == 'equal'  # Training targets retain the original recipe.
    inputs = dict(base['inputs'])
    paths = [basepath,Path(__file__),ROOT/'tools/research/hu_later_average_fresh_review_20260923.py',
             ROOT/'tools/research/later_average_support_v1.py', ROOT/'tools/research/reboot_research_idle_v1.py',
             OUT/'LATER-WEIGHTED-AVERAGING-PLAN.md']
    for suffix in ('registration','result','independent-review'):
        paths.append(OUT/f'complete-private-allin-cache-v2-{suffix}.json')
    weightpath=OUT/'later-average-weight-control-v1-result.json'
    weight=json.loads(weightpath.read_text()); assert weight['passed']
    wrp=OUT/'later-average-weight-control-v1-registration.json';wr=json.loads(wrp.read_text())
    assert weight['registration_sha256']==sha(wrp)
    inputs.update(wr['inputs']);paths.extend([weightpath,wrp])
    if not CONTROL:
        cp=OUT/'later-average-fresh-control-v1-independent-review.json'; cr=json.loads(cp.read_text())
        assert cr['passed'] and cr['terminal_complete'] and cr['completed_iterations']==4
        assert cr['control_only'] and min(cr['nonuniform_table_rows'])>0
        for p,h in cr['evidence_hashes'].items():assert sha(p)==h,p
        paths.extend([cp,OUT/'later-average-fresh-control-v1-registration.json',
            ROOT/'tools/research/hu_later_average_exact_evaluation_20260923.py',
            ROOT/'tools/research/hu_later_average_exact_review_20260923.py'])
    inputs.update({str(p):sha(p) for p in paths})
    reg=dict(inputs=inputs,config=cfg,maximum_seconds=1200 if CONTROL else 14400,
        host_reserve_bytes=20_000_000_000,gpu_reserve_bytes=3_000_000_000,
        disk_reserve_bytes=40_000_000_000,maximum_store_bytes=40_000_000_000,
        store=str(STORE),control_only=CONTROL,production_modified=False,
        output_schedules={'equal':'w(g)=1','linear':'w(g)=g+1'},played_generations=list(range(cfg['max_iterations'])),
        excluded_generation=cfg['max_iterations'],
        changes='Fresh chance/action/reservoir/fit seeds; complete exact cache covers these new draws with unchanged board-count outcomes. Training objective unchanged. Compare two output averages of the same complete bank.',
        evaluation='All four equal/linear player pairings; complete exact BB fold/shove and BTN fold/call deviation gains, all classes. Both own-pair gains must fall at least 25% to justify a separately registered wider evaluation. No deployment.',
        stopping='Fixed update count or resource/deadline/activity stop; no retry, selection or partial quality claim.')
    verify(reg)
    assert psutil.virtual_memory().available>=reg['host_reserve_bytes'] and free_gpu()>=reg['gpu_reserve_bytes']
    assert shutil.disk_usage(STORE.anchor).free>=reg['disk_reserve_bytes']+reg['maximum_store_bytes']
    rp=output('registration');save(rp,reg)
    child=None; acquired=False; error=None; resources=[]; started=time.monotonic()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        save(output('admission'),dict(controller_pid=os.getpid(),registration_sha256=sha(rp),production_modified=False))
        env=os.environ.copy();env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONUNBUFFERED='1')
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__)),*(['--control'] if CONTROL else []),'--worker',str(rp)],
                cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            status(dict(state='running',controller_pid=os.getpid(),worker_pid=child.pid,production_modified=False))
            last_resource=-10.
            while child.poll() is None:
                time.sleep(2);elapsed=time.monotonic()-started
                assert elapsed<reg['maximum_seconds'] and idle(), 'Deadline or production activity'
                if elapsed-last_resource>=10:
                    host=psutil.virtual_memory().available;gpu=free_gpu();disk=shutil.disk_usage(STORE.anchor).free
                    used=sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) if STORE.exists() else 0
                    resources.append(dict(seconds=elapsed,free_host_bytes=host,free_gpu_bytes=gpu,free_disk_bytes=disk,store_bytes=used))
                    assert host>=reg['host_reserve_bytes'] and gpu>=reg['gpu_reserve_bytes'] and disk>=reg['disk_reserve_bytes'] and used<=reg['maximum_store_bytes']
                    last_resource=elapsed
        assert child.returncode==0, f'Worker exited {child.returncode}; inspect preserved log'
        verify(reg);result=json.loads(output('result').read_text())
        assert result['terminal'] and result['completed_iterations']==cfg['max_iterations']
    except Exception as exc:
        error=repr(exc);raise
    finally:
        try:
            if child is not None and child.poll() is None:
                for descendant in reversed(psutil.Process(child.pid).children(recursive=True)):
                    try:descendant.terminate()
                    except psutil.NoSuchProcess:pass
                child.terminate();child.wait(timeout=20)
            status(dict(state='stopped' if error else 'complete',error=error,exit_code=child.returncode if child else None,
                execution_seconds=time.monotonic()-started,store=str(STORE),production_modified=False))
            save(output('resources'),resources)
        finally:
            if acquired:
                assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__': main()
