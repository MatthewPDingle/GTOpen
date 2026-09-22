"""Finish the already-running dense trial's fixed audits and evaluation.

Wait only for the explicitly identified controller. Never restart training or
retry a failed stage. All GPU stages retain their own production/resource locks.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-dense-finish-v1'
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--controller-pid',type=int,required=True)
    parser.add_argument('--controller-created',type=float,required=True)
    args = parser.parse_args()
    process = psutil.Process(args.controller_pid)
    assert process.create_time() == args.controller_created
    assert any(Path(a).name == 'hu_sampled_physical_dense_pilot_20260922.py' for a in process.cmdline()[1:])
    assert '--run' in process.cmdline() and idle()
    assert not (OUT/f'{PREFIX}-registration.json').exists()
    stage_paths = [ROOT/'tools/research'/name for _,name,_ in STAGES]
    reg = dict(controller_pid=args.controller_pid,controller_created=args.controller_created,
        inputs={str(p):sha(p) for p in [Path(__file__),*stage_paths]},stages=STAGES,
        wait_limit_seconds=7200,production_modified=False,
        scope='One sequential continuation of the live registered dense trial. No restart, retry, extension, candidate selection or deployment.')
    regpath = OUT/f'{PREFIX}-registration.json'; save(regpath,reg)
    records = []; started = time.monotonic(); state = 'waiting'; error = None
    def status():
        save(OUT/f'{PREFIX}-status.json',dict(state=state,error=error,
            controller_pid=psutil.Process().pid,source_controller_pid=args.controller_pid,
            completed_stages=records,seconds=time.monotonic()-started,
            registration_sha256=sha(regpath),production_modified=False))
    status(); print(json.dumps(dict(state=state,source_controller_pid=args.controller_pid)),flush=True)
    try:
        while process.is_running():
            assert process.create_time() == args.controller_created
            assert time.monotonic()-started < reg['wait_limit_seconds'] and idle()
            time.sleep(5)
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
