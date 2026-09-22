"""Continue the completed dense trial after a pre-stage status-write failure.

Require terminal successful training. Never restart training or retry a failed
scientific stage. All GPU stages retain their own production/resource locks.
"""
import argparse
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-dense-finish-v2'
STAGES = [
    ('training-audit','hu_sampled_physical_dense_review_20260922.py',[]),
    ('training-fit-diagnosis','hu_sampled_physical_dense_fit_diagnosis_20260922.py',[]),
    ('training-noise-diagnosis','hu_sampled_physical_root_noise_20260922.py',['--source','dense']),
    ('hybrid-gpu-control','hu_sampled_physical_hybrid_gpu_control_20260922.py',['--run']),
    ('evaluation-prepare','hu_sampled_physical_dense_evaluation_20260922.py',['--prepare']),
    ('evaluation','hu_sampled_physical_dense_evaluation_20260922.py',['--run']),
    ('evaluation-audit','hu_sampled_physical_dense_evaluation_review_20260922.py',[]),
]


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--run',action='store_true',required=True); parser.parse_args()
    assert idle()
    training_status = OUT/'sampled-physical-dense-pilot-v1-status.json'
    training_result = OUT/'sampled-physical-dense-pilot-v1-result.json'
    terminal = json.loads(training_status.read_text()); result = json.loads(training_result.read_text())
    assert terminal['state'] == 'complete' and terminal['exit_code'] == 0 and terminal['error'] is None
    assert result['terminal'] and result['completed_iterations'] == 78
    previous_registration = OUT/'sampled-physical-dense-finish-v1-registration.json'
    previous = json.loads(previous_registration.read_text())
    for p,h in previous['inputs'].items(): assert sha(p) == h,p
    assert all(not (OUT/f'sampled-physical-dense-finish-v1-{label}.log').exists() for label,_,_ in STAGES)
    for process in psutil.process_iter(['name','cmdline']):
        if (process.info['name'] or '').lower().startswith('python'):
            assert not any(Path(a).name in ('hu_sampled_physical_dense_finish_20260922.py','hu_sampled_physical_dense_pilot_20260922.py') for a in (process.info['cmdline'] or [])[1:])
    assert not (OUT/f'{PREFIX}-registration.json').exists()
    stage_paths = [ROOT/'tools/research'/name for _,name,_ in STAGES]
    reg = dict(inputs={str(p):sha(p) for p in [Path(__file__),*stage_paths,training_status,training_result,previous_registration]},stages=STAGES,
        supersedes='v1 status writer used create-only save for a mutable status file. It failed before starting any stage. Training completed successfully and no scientific stage is being retried.',production_modified=False,
        scope='One sequential continuation of the successfully completed registered dense trial. No restart, retry, extension, candidate selection or deployment.')
    regpath = OUT/f'{PREFIX}-registration.json'; save(regpath,reg)
    records = []; started = time.monotonic(); state = 'admitted'; error = None
    def status():
        path = OUT/f'{PREFIX}-status.json'; temporary = path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
        save(temporary,dict(state=state,error=error,
            controller_pid=psutil.Process().pid,
            completed_stages=records,seconds=time.monotonic()-started,
            registration_sha256=sha(regpath),production_modified=False))
        temporary.replace(path)
    status(); print(json.dumps(dict(state=state)),flush=True)
    try:
        # The reviewer independently requires a full successful 78-update run,
        # recorded resource compliance and no live trainer process.
        for label,name,arguments in STAGES:
            assert idle()
            for p,h in reg['inputs'].items(): assert sha(p) == h,p
            state = label; status(); print(json.dumps(dict(state=state)),flush=True)
            stage_started = time.monotonic()
            logpath = OUT/f'{PREFIX}-{label}.log'
            with logpath.open('x') as log:
                child = subprocess.Popen([sys.executable,str(ROOT/'tools/research'/name),*arguments],
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                # Every stage owns its deadline/activity handling. Do not place
                # an outer kill timer around it that could orphan GPU workers.
                code = child.wait()
            record = dict(stage=label,exit_code=code,seconds=time.monotonic()-stage_started,
                          log=str(logpath),log_sha256=sha(logpath))
            records.append(record); status(); print(json.dumps(record),flush=True)
            assert code == 0, f'{label} failed; inspect its preserved log, no automatic retry'
        state = 'complete'
    except Exception as exc:
        error = str(exc); state = 'stopped'; raise
    finally:
        status()


if __name__ == '__main__': main()
