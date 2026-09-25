"""Frozen inputs and bounded ownership for paired continuation diagnostics."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from reboot_research_idle_v1 import idle
from hu_root_retained_storage_admitted_study_20260924 import measure

LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
TRIALS = ('action-integrated-fresh-pilot-v1', 'action-integrated-replication-v1')


def frozen_inputs():
    inputs = {}
    trials = []
    for name in TRIALS:
        paths = {s: OUT/f'{name}-{s}.json' for s in ('registration','result','independent-review')}
        reg, result, audit = [read(paths[s]) for s in paths]
        assert result['passed'] and result['terminal'] and audit['passed']
        assert result['completed_iterations'] == audit['completed_updates'] == 78
        assert result['registration_sha256'] == audit['source_registration_sha256'] == sha(paths['registration'])
        assert audit['source_result_sha256'] == sha(paths['result'])
        assert all(result['config'][k] == v for k, v in reg['config'].items())
        inputs.update(reg['inputs'])
        inputs.update({str(p): sha(p) for p in paths.values()})
        metrics = Path(reg['store'])/'iteration-0078/metrics.json'
        assert sha(metrics) == result['steps'][77]['metrics_sha256']
        query = metrics.parent/'batch-00/queries.json'
        assert sha(query) == read(metrics)['subbatches'][0]['artifacts']['queries']
        inputs.update({str(p): sha(p) for p in (metrics, query)})
        trials.append(dict(name=name, registration=str(paths['registration']),
            result=str(paths['result']), audit=str(paths['independent-review']), query=str(query)))
    # Freeze the complete research Python source inventory. Do not modify a
    # registered dependency while a worker is live.
    inputs.update({str(p):sha(p) for p in (ROOT/'tools/research').glob('*.py')})
    for path, digest in inputs.items(): assert sha(path) == digest, path
    return inputs, trials


def guard_for(reg, *, gpu=True):
    started = time.monotonic(); last = 0.; last_size = 0.
    def guard():
        nonlocal last, last_size
        now = time.monotonic()
        assert now-started < reg['maximum_seconds']
        if now-last > 2:
            assert idle() and not OTHER.exists()
            assert psutil.virtual_memory().available >= 20_000_000_000
            assert shutil.disk_usage('T:/').free >= 40_000_000_000
            if gpu:
                import torch
                assert torch.cuda.mem_get_info()[0] >= 3_000_000_000
            last = now
        if now-last_size > 10:
            paths = list(OUT.glob(reg['prefix']+'*'))
            if reg.get('store') and Path(reg['store']).exists():
                paths.extend(Path(reg['store']).rglob('*'))
            assert sum(p.stat().st_size for p in paths if p.is_file()) <= reg['maximum_output_bytes']
            last_size = now
    return guard


def setup_cuda():
    import torch
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    assert torch.cuda.is_available()


def launch(script, prefix, extra, *, cap, seconds):
    assert idle() and not LOCK.exists() and not OTHER.exists()
    rp = OUT/f'{prefix}-registration.json'; assert not rp.exists()
    if extra.get('store'): assert not Path(extra['store']).exists()
    inputs, trials = frozen_inputs()
    for path in extra.get('extra_inputs', []): inputs[str(path)] = sha(path)
    roots = measure()
    assert sum(r['allocated_file_bytes'] for r in roots)+cap+2_000_000_000 <= 800_000_000_000
    reg = dict(inputs=inputs,trials=trials,prefix=prefix,storage_inventory=roots,
        maximum_output_bytes=cap,maximum_seconds=seconds,production_modified=False,**extra)
    save(rp,reg)
    child=None; error=None; started=time.monotonic()
    with LOCK.open('x') as f: f.write(str(os.getpid()))
    try:
        guard=guard_for(reg,gpu=False)
        with (OUT/f'{prefix}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(script),'--worker'],cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                guard()
                try: child.wait(timeout=5)
                except subprocess.TimeoutExpired: pass
        assert child.returncode==0, 'Worker failed; preserve evidence and log'
        assert read(OUT/f'{prefix}-result.json')['passed']
    except BaseException as exc:
        error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:
            child.terminate();child.wait(timeout=15)
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        save(OUT/f'{prefix}-status.json',dict(state='failed' if error else 'complete',
            error=error,exit_code=child.returncode if child else None,
            seconds=time.monotonic()-started,production_modified=False))
