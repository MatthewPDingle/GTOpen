"""Replay both final CUDA fits with bulk features; require exact saved networks."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2', CUBLAS_WORKSPACE_CONFIG=':4096:8')
import cProfile
import hashlib
import io
import json
from pathlib import Path
import pstats
import shutil
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_root_retained_storage_admitted_study_20260924 import measure
from reboot_research_idle_v1 import idle

PREFIX = 'visible-features-bulk-cuda-replay-v1'
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
CAP = 10_000_000


def worker(reg):
    import numpy as np
    import torch
    from action_integrated_checkpoint_v1 import restore_checkpoint
    from sampled_visible_hybrid_checkpoint_v1 import read_object
    from sampled_visible_hybrid_fit_bulk_v1 import fit
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    assert torch.cuda.is_available()
    started=time.monotonic();last_guard=0.
    def guard():
        nonlocal last_guard
        now=time.monotonic()
        if now-last_guard>2:
            assert now-started<1200 and idle()
            assert psutil.virtual_memory().available>=20_000_000_000
            assert torch.cuda.mem_get_info()[0]>=3_000_000_000
            assert shutil.disk_usage('T:/').free>=40_000_000_000
            last_guard=now
    guard()
    result=read(reg['trial_result']);registration=read(reg['trial_registration']);cfg=result['config']
    assert all(cfg[k]==v for k,v in registration['config'].items())
    assert cfg['torch_version']==torch.__version__ and cfg['numpy_version']==np.__version__
    assert cfg['device_name']==torch.cuda.get_device_name()
    store=Path(registration['store']);objects=store/'objects';source=Path(reg['context']).read_text()
    matrix=read(reg['matrix']);metrics=read(store/'iteration-0078/metrics.json')
    state=restore_checkpoint(objects,result['final_checkpoint'],config=cfg,
        context_source=source,catalog_source=Path(reg['catalog']).read_text(),
        matrix_sha256=sha(reg['matrix']),entry_mass=np.asarray(matrix['class_mass']).sum(axis=0))
    original=json.loads(read_object(objects,metrics['next_model']))['exact_model']['base_model']['networks']
    records=[]
    for player,reservoir in enumerate(state['reservoirs']):
        guard();before=time.monotonic()
        net,metric=fit(reservoir,seed=cfg['fit_seed_base']+78*200003+player,
            steps=cfg['fit_steps'],device='cuda',chunk_size=cfg['chunk_size'],guard=guard,
            learning_rate=cfg['learning_rate'])
        assert net==original[player],f'Player {player}: trained weights changed'
        baseline=metrics['fits'][player];exclude={'setup_seconds','optimizer_seconds'}
        assert {k:v for k,v in metric.items() if k not in exclude}=={k:v for k,v in baseline.items() if k not in exclude}
        records.append(dict(player=player,seconds=time.monotonic()-before,weights_identical=True,
            nontiming_metrics_identical=True,metrics=metric,
            historical_setup_seconds=baseline['setup_seconds'],historical_optimizer_seconds=baseline['optimizer_seconds']))
        print(json.dumps({k:v for k,v in records[-1].items() if k!='metrics'}),flush=True)
    for path,digest in reg['inputs'].items():guard();assert sha(path)==digest,path
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        players=records,seconds=time.monotonic()-started,production_modified=False,gpu_used=True,
        scope='Reproduce both original final-update 512-step CUDA fits from unchanged reservoirs and seeds. Exact network and nontiming-metric equality; no new trial or range-quality claim. Historical timing comparison is not a paired full-training benchmark.'))


def main():
    if sys.argv[1:]==['--worker']:
        worker(read(OUT/f'{PREFIX}-registration.json'));return
    assert sys.argv[1:]==['--run'] and idle()
    assert not LOCK.exists() and not OTHER.exists()
    rp=OUT/f'{PREFIX}-registration.json'; assert not rp.exists()
    trial='action-integrated-replication-v1'
    tr=OUT/f'{trial}-registration.json'; result=OUT/f'{trial}-result.json'
    audit=OUT/f'{trial}-independent-review.json'
    assert read(result)['terminal'] and read(audit)['passed']
    assert read(audit)['source_result_sha256']==sha(result)
    assert read(OUT/'action-integrated-comparison-continuation-v1-result.json')['passed']
    assert read(OUT/'visible-features-bulk-control-v1-result.json')['passed']
    paths=[Path(__file__).resolve(),tr,result,audit,OUT/'bb-context-candidate.json',
        OUT/'preflop-allin-matrix-control-v1-matrix.json',
        Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')]
    paths.extend([ROOT/'tools/research/sampled_visible_hybrid_fit_bulk_v1.py',
        OUT/'visible-features-bulk-control-v1-result.json',
        OUT/'visible-features-bulk-control-v1-registration.json',
        ROOT/'tools/research/sampled_visible_features_bulk_v1.py',
        OUT/'saved-preparation-profile-v2-result.json',
        ROOT/'tools/research/hu_saved_preparation_profile_20260925.py',
        OUT/'saved-preparation-profile-v1-registration.json',OUT/'saved-preparation-profile-v1-status.json',
        OUT/'saved-preparation-profile-v1.log'])
    inputs=dict(read(tr)['inputs']);inputs.update({str(p):sha(p) for p in paths})
    for path,digest in inputs.items():assert sha(path)==digest,path
    roots=measure();assert sum(x['allocated_file_bytes'] for x in roots)+CAP+2_000_000_000<=800_000_000_000
    reg=dict(inputs=inputs,trial_registration=str(tr),trial_result=str(result),
        context=str(paths[4]),matrix=str(paths[5]),catalog=str(paths[6]),storage_inventory=roots,
        maximum_seconds=1200,maximum_output_bytes=CAP,production_modified=False,gpu_used=True,
        selection='Replay both final-update fits from original completed reservoirs, seeds and full 512 steps; no candidate selection.')
    save(rp,reg);child=None;error=None;started=time.monotonic()
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],
                cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                assert time.monotonic()-started<1200 and idle() and not OTHER.exists()
                assert psutil.virtual_memory().available>=20_000_000_000
                assert shutil.disk_usage('T:/').free>=40_000_000_000
                assert sum(p.stat().st_size for p in OUT.glob(PREFIX+'*') if p.is_file())<=CAP
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
        assert child.returncode==0, 'Feature control failed; preserve log'
        assert read(OUT/f'{PREFIX}-result.json')['passed']
    except BaseException as exc:
        error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:
            child.terminate();child.wait(timeout=15)
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        save(OUT/f'{PREFIX}-status.json',dict(state='failed' if error else 'complete',error=error,
            exit_code=child.returncode if child else None,seconds=time.monotonic()-started,
            production_modified=False))


if __name__=='__main__':main()
