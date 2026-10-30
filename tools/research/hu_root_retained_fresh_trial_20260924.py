"""Fresh fixed-budget all-root-retention training; production untouched."""
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
from sampled_allin_protocol_v3 import ESTIMATOR
from exact_initial_hybrid_checkpoint_v1 import CONFIG_KEY, POLICY_TYPE
from root_retained_checkpoint_v1 import CONFIG_KEY as ROOT_KEY, POLICY_TYPE as ROOT_POLICY

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
CONTROL = False
PREFIX = 'root-retained-fresh-pilot-v1'
STORE = Path('T:/GTOpen-research')/PREFIX
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
    from root_retained_training_v1 import initialize, save_state, update
    from preflop_allin_matrix_v1 import AllinMatrix
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    assert torch.cuda.is_available()
    verify(reg)
    config = dict(reg['config'],torch_version=torch.__version__,numpy_version=np.__version__,
                  device_name=torch.cuda.get_device_name())
    save(output('environment'),config)
    context_path = OUT/'bb-context-candidate.json'; source = context_path.read_text()
    matrix_path = OUT/'preflop-allin-matrix-control-v1-matrix.json'; matrix_source = matrix_path.read_text()
    catalog_source = Path(reg['catalog']).read_text()
    matrix = AllinMatrix(json.loads(matrix_source), source)
    cache = load_complete_cache()
    assert cache.sha256 == config['allin_cache_sha256'] and config['terminal_estimator'] == ESTIMATOR
    STORE.mkdir(parents=True,exist_ok=False); objects = STORE/'objects'; objects.mkdir()
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
    args = dict(context_source=source,catalog_source=catalog_source,
                matrix_sha256=sha(matrix_path),entry_mass=matrix.btn_mass)
    step_args = dict(context_path=context_path,catalog_source=catalog_source,
        matrix_source=matrix_source,matrix_sha256=sha(matrix_path),cache=cache,
        executable=ROOT/'target/release/examples/hu_sampled_allin_bridge_v3.exe',batch_prefix=PREFIX,guard=guard)
    state = initialize(objects,config,**args)
    initial = save_state(objects,state,config,**args); save(STORE/'checkpoint-0000.json',initial)
    metrics = []
    for iteration in range(1,config['max_iterations']+1):
        guard(); began = time.monotonic()
        row = update(STORE/f'iteration-{iteration:04d}',objects,state,config,**step_args)
        checkpoint = row['checkpoint']; save(STORE/f'checkpoint-{iteration:04d}.json',checkpoint)
        metrics.append(dict(iteration=iteration,seconds=time.monotonic()-began,
                            checkpoint=checkpoint,metrics_sha256=sha(STORE/f'iteration-{iteration:04d}'/'metrics.json')))
        tmp = STORE/'latest.tmp'
        save(tmp,dict(completed_iterations=iteration,checkpoint=checkpoint,config=config)); tmp.replace(STORE/'latest.json')
        print(json.dumps(dict(iteration=iteration,seconds=metrics[-1]['seconds'],
            fresh_deals=state['sampler'].draws,retained=[r.size for r in state['reservoirs']],
            seen=[r.seen for r in state['reservoirs']])),flush=True)
    verify(reg)
    files = {}
    for path in sorted(STORE.rglob('*')):
        if path.is_file(): guard(); files[str(path)] = sha(path)
    save(output('result'),dict(passed=True,terminal=True,registration_sha256=sha(output('registration')),
        completed_iterations=len(metrics),config=config,store=str(STORE),
        initial_checkpoint=initial,final_checkpoint=checkpoint,steps=metrics,artifacts=files,
        seconds=time.monotonic()-started,control_only=CONTROL,
        physical_poker_convergence_qualified=False,production_modified=False,
        scope='Fresh complete played bank with all corrected sampled BB root advantages retained. Integration and accuracy must be reviewed separately.'))


def main():
    global PREFIX, STORE, CONTROL
    CONTROL = '--control' in sys.argv
    PREFIX = 'root-retained-fresh-control-v1' if CONTROL else 'root-retained-fresh-pilot-v1'
    STORE = Path('T:/GTOpen-research')/PREFIX
    if '--worker' in sys.argv:
        worker(json.loads(Path(sys.argv[-1]).read_text())); return
    assert '--run' in sys.argv and idle() and not STORE.exists()
    assert not LOCK.exists() and not OTHER.exists()
    basepath = OUT/'later-average-fresh-pilot-v1-registration.json'
    base = json.loads(basepath.read_text()); verify(base)
    cfg = dict(base['config'], max_iterations=2 if CONTROL else 78,
        sampler_seed=356501 if CONTROL else 121301, action_seed=356502 if CONTROL else 121302,
        reservoir_seeds=[356503,356504] if CONTROL else [121303,121304],
        fit_seed_base=356505 if CONTROL else 121305,
        **{CONFIG_KEY:POLICY_TYPE,ROOT_KEY:ROOT_POLICY},exact_bb_root_targets='exact-initial-bb-training-targets-v2',
        current_policy_inference='float64-widened-float32-weights-v1')
    assert cfg['iteration_weights']=='equal' and cfg['deals_per_iteration']==512
    inputs = dict(base['inputs'])
    paths = [basepath,Path(__file__),ROOT/'tools/research/hu_root_retained_fresh_review_20260924.py',
             OUT/'ROOT-RETAINED-FRESH-TRIAL-PLAN.md']
    catalog = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    paths.append(catalog)
    for prefix in ('root-retained-joint-cpu-control-v1','root-retained-joint-gpu-control-v1','root-retained-policy-control-v1'):
        rp,pp=[OUT/f'{prefix}-{s}.json' for s in ('registration','result')]
        r,p=json.loads(rp.read_text()),json.loads(pp.read_text())
        assert p['passed'] and p['registration_sha256']==sha(rp)
        inputs.update(r['inputs']);paths.extend([rp,pp])
    if not CONTROL:
        ar,ap=[OUT/f'root-retained-fresh-control-v1-{s}.json' for s in ('readback-registration','independent-review')]
        audit=json.loads(ap.read_text())
        assert audit['passed'] and audit['completed_updates']==2
        assert audit['readback_registration_sha256']==sha(ar)
        inputs.update(json.loads(ar.read_text())['inputs']);paths.extend([ar,ap])
    inputs.update({str(p.resolve()):sha(p) for p in paths})
    reg=dict(inputs=inputs,config=cfg,maximum_seconds=1800 if CONTROL else 21600,
        host_reserve_bytes=20_000_000_000,gpu_reserve_bytes=3_000_000_000,
        disk_reserve_bytes=40_000_000_000,maximum_store_bytes=40_000_000_000,
        store=str(STORE),catalog=str(catalog),control_only=CONTROL,production_modified=False,
        primary_output_weights='linear w(g)=g+1 for both players',
        diagnostic_output_weights='equal w(g)=1; not a second candidate-selection chance',
        played_generations=list(range(cfg['max_iterations'])),excluded_generation=cfg['max_iterations'],
        changes='Preserve every corrected sampled BB root advantage in a separate cumulative state. Existing exact initial targets, BTN accumulator, reservoirs, fitting and inference unchanged. Fresh uniform initialization, matched training seeds, no checkpoint reuse.',
        evaluation='Audit first. Report restricted all-in gains against the preceding exact-initial candidate. Subject to correctness and separately checked storage, run a prospectively registered fresh wider call/raise response test. No checkpoint selection or production deployment.',
        stopping='Fixed update count or resource/deadline/activity stop; no outcome-dependent stopping, retry, checkpoint selection or partial quality claim.')
    verify(reg)
    assert psutil.virtual_memory().available>=reg['host_reserve_bytes'] and free_gpu()>=reg['gpu_reserve_bytes']
    assert shutil.disk_usage(STORE.anchor).free>=reg['disk_reserve_bytes']+reg['maximum_store_bytes']
    rp=output('registration');assert not rp.exists();save(rp,reg)
    child=None; acquired=False; error=None; resources=[]; started=time.monotonic()
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True
        assert not OTHER.exists() and idle()
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
