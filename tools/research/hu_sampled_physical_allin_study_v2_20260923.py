"""One conditional-all-in trial, audit and two predeclared evaluation families.

No automatic retry or partial-candidate substitution. Child stages retain their
own activity/resource guards and deadlines; production is never restarted.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-allin-study-v2'
STAGES = [
    ('training','hu_sampled_physical_allin_pilot_20260923.py',['--run']),
    ('training-audit','hu_sampled_physical_allin_review_20260923.py',[]),
    ('evaluation-prepare','hu_sampled_physical_allin_evaluation_20260923.py',['--prepare']),
    ('evaluation','hu_sampled_physical_allin_evaluation_20260923.py',['--run']),
    ('evaluation-audit','hu_sampled_physical_allin_evaluation_review_20260923.py',[]),
    ('btn-evaluation','hu_sampled_physical_allin_btn_evaluation_20260923.py',[]),
    ('btn-evaluation-audit','hu_sampled_physical_allin_btn_review_20260923.py',[]),
]


def main():
    import os
    parser = argparse.ArgumentParser(); parser.add_argument('--run',action='store_true',required=True); parser.parse_args()
    assert idle()
    from sampled_allin_admission_v2 import completed_hybrid_paths
    prerequisites = completed_hybrid_paths(OUT)
    assert not (OUT/'sampled-physical-allin-pilot-v1-registration.json').exists()
    assert not Path('S:/GTOpen-research/sampled-physical-allin-pilot-v1').exists()
    assert not (ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock').exists()
    assert not (ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock').exists()
    from sampled_allin_protocol_v3 import AllinCache
    cache_review_path = OUT/'sampled-physical-allin-training-cache-v1-independent-review.json'
    AllinCache.from_review(cache_review_path)
    pipeline_path = OUT/'sampled-physical-allin-pipeline-control-v1-result.json'
    pipeline = json.loads(pipeline_path.read_text()); assert pipeline['passed']
    for p,h in pipeline['inputs'].items(): assert sha(p) == h,p
    paths = [Path(__file__),*prerequisites,cache_review_path,pipeline_path,
             ROOT/'tools/research/sampled_allin_admission_v2.py',OUT/'ALLIN-ADMISSION-V2.md',
             *[ROOT/'tools/research'/name for _,name,_ in STAGES]]
    registration = dict(inputs={str(p):sha(p) for p in paths},stages=STAGES,
        scope='Predeclared conditional-preflop-all-in hypothesis. One complete training candidate followed by five BB root and three BTN response comparisons, with two family error budgets of .025. Stop on any failed stage without retry. No production or preview deployment.',
        production_modified=False)
    regpath = OUT/f'{PREFIX}-registration.json'; save(regpath,registration)
    started = time.monotonic(); state = 'admitted'; error = None; records = []
    def status():
        path = OUT/f'{PREFIX}-status.json'
        temporary = path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
        save(temporary,dict(state=state,error=error,controller_pid=os.getpid(),
            completed_stages=records,seconds=time.monotonic()-started,
            registration_sha256=sha(regpath),production_modified=False))
        temporary.replace(path)
    try:
        status()
        for label,name,arguments in STAGES:
            assert idle()
            for p,h in registration['inputs'].items(): assert sha(p) == h,p
            state = label; status(); print(json.dumps(dict(stage=label)),flush=True)
            stage_started = time.monotonic(); logpath = OUT/f'{PREFIX}-{label}.log'
            with logpath.open('x') as log:
                child = subprocess.Popen([sys.executable,str(ROOT/'tools/research'/name),*arguments],
                    cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                code = child.wait()
            record = dict(stage=label,exit_code=code,seconds=time.monotonic()-stage_started,
                log=str(logpath),log_sha256=sha(logpath))
            records.append(record); status(); print(json.dumps(record),flush=True)
            assert code == 0, f'{label} failed; inspect preserved evidence, no automatic retry'
        state = 'complete'
    except Exception as exc:
        state = 'stopped'; error = str(exc); raise
    finally: status()


if __name__ == '__main__': main()
