"""One diagnosed numerical repair of the completed allin candidate evaluation.

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
PREFIX = 'sampled-physical-allin-repair-v1'
STAGES = [
    ('evaluation-prepare','hu_sampled_physical_allin_evaluation_v2_20260923.py',['--prepare']),
    ('evaluation','hu_sampled_physical_allin_evaluation_v2_20260923.py',['--run']),
    ('evaluation-audit','hu_sampled_physical_allin_evaluation_review_v2_20260923.py',[]),
    ('btn-evaluation','hu_sampled_physical_allin_btn_evaluation_v2_20260923.py',[]),
    ('btn-evaluation-audit','hu_sampled_physical_allin_btn_review_v2_20260923.py',[]),
]


def main():
    import os
    parser = argparse.ArgumentParser(); parser.add_argument('--run',action='store_true',required=True); parser.parse_args()
    assert idle()
    dense_review_path = OUT/'sampled-physical-allin-precision-control-v1-independent-review.json'
    dense_result_path = OUT/'sampled-physical-allin-precision-control-v1-result.json'
    review = json.loads(dense_review_path.read_text())
    assert review['passed'] and review['result_sha256'] == sha(dense_result_path)
    assert not (OUT/'sampled-physical-allin-evaluation-v2-registration.json').exists()
    assert not Path('S:/GTOpen-research/sampled-physical-allin-evaluation-v2').exists()
    assert not (ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock').exists()
    assert not (ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock').exists()
    paths = [Path(__file__),dense_review_path,dense_result_path,OUT/'ALLIN-NUMERICAL-REPAIR.md',
             *[ROOT/'tools/research'/name for _,name,_ in STAGES]]
    registration = dict(inputs={str(p):sha(p) for p in paths},stages=STAGES,
        scope='Diagnosed float64 repair of the unchanged completed allin candidate. Original failure retained; same reserved chance streams, no original held-out outcomes. Original five BB-root comparisons and three predeclared BTN-vs-jam comparisons retain alpha .025 per family. Stop on any failed stage without retry; no production or preview deployment.',
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
