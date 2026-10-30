"""One explicitly reviewed clean-boundary continuation; never retry a batch.

Runs the unchanged existing evaluator with its existing --resume option once.
Preserves original attempt, registration, deadlines, failures and checkpoints.
No training, independent reader, extra trial, deployment or automatic restart.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import psutil

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME = 'stack-context-clean-boundary-resume-v1'
EVAL = 'stack-context-matched-evaluation-v5'
STORE = Path('S:/GTOpen-research')/EVAL
REVIEW = OUT/(NAME+'-review.json')
REVIEW_SHA = 'afe9873ce9718c9bc45abb386f25302ddbe005853c242f6d6b26e1224812ac9a'
ATTEMPT, RESULT, FAILED, OWNER = (OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure','-owner'))
LOCKS = (ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock',
         ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock',
         OUT/'stack-context-pressure-evaluation-handoff-v1-owner.json')
COMMAND = ['C:/Program Files/Python312/python.exe','-B',str(ROOT/'tools/research/stack_context_matched_evaluation_v5.py'),'--run','--resume']

def read(path): return json.loads(Path(path).read_bytes())
def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def require(value,message):
    if not value: raise ValueError(message)
def publish(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,sort_keys=True,separators=(',',':'));stream.flush();os.fsync(stream.fileno())

def reviewed_state():
    require(sha(REVIEW)==REVIEW_SHA,'Changed explicit complete-boundary review')
    review=read(REVIEW)
    require(review['complete'] and review['passed'] and review['qualified_clean_boundary_continuation']
            and review['remaining_deals']==1888 and review['resume_attempts_allowed']==1
            and not review['partial_scientific_batch_retry_allowed'],'Incomplete explicit review')
    for path,digest in review['inputs'].items(): require(sha(path)==digest,'Changed reviewed boundary input: '+path)
    require(time.time()<review['original_evaluation_deadline_unix'],'Original 72-hour deadline remains binding')
    require(not any(p.exists() for p in (*LOCKS,OUT/(EVAL+'-result.json'),OUT/(EVAL+'-failure.json'),
            OUT/'stack-context-matched-readback-v6-attempt.json')),'Live ownership, scientific failure or downstream attempt')
    require(len(list(STORE.glob('invocation-*.json')))==1,'Explicit continuation already attempted')
    return review

def main(run=False):
    if not run:
        print(json.dumps(dict(prepared=True,command=COMMAND,review_present=REVIEW.exists(),
                              started=ATTEMPT.exists(),terminal=RESULT.exists(),failed=FAILED.exists())));return
    require(not any(p.exists() for p in (ATTEMPT,RESULT,FAILED,OWNER)),'Never restart or duplicate this once-only continuation')
    review=reviewed_state()
    sys.path.insert(0,str(ROOT/'tools/research'))
    from river_matched_training_pilot_v1 import available,production_available
    ready,probe=available()
    require(ready and production_available() and psutil.virtual_memory().available>=40_000_000_000,
            'Resources unavailable; leave scientific attempt unchanged')
    self_id=dict(pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time(),
                 runner_sha256=sha(__file__),review_sha256=REVIEW_SHA,command=COMMAND)
    publish(OWNER,self_id);publish(ATTEMPT,self_id)
    prefix=OUT/(NAME+'-evaluation')
    try:
        with Path(str(prefix)+'-stdout.log').open('xb') as stdout,Path(str(prefix)+'-stderr.log').open('xb') as stderr:
            child=subprocess.Popen(COMMAND,cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            started=dict(pid=child.pid,created=psutil.Process(child.pid).create_time(),unix=time.time(),
                         parent_pid=os.getpid(),command=COMMAND,original_attempt_sha256=sha(OUT/(EVAL+'-attempt.json')))
            publish(str(prefix)+'-started.json',started)
            code=child.wait()
        finished=dict(**started,exit_code=code,finished_unix=time.time(),
                      stdout_sha256=sha(str(prefix)+'-stdout.log'),stderr_sha256=sha(str(prefix)+'-stderr.log'))
        publish(str(prefix)+'-finished.json',finished)
        require(code==0,'Resumed evaluator failed; preserve without retry')
        require(not any(p.exists() for p in (*LOCKS,OUT/(EVAL+'-failure.json'))),'Scientific failure or unreleased ownership')
        terminal_path=OUT/(EVAL+'-result.json')
        require(terminal_path.exists(),'Clean partial stop requires another explicit review; never automatically resume')
        terminal=read(terminal_path)
        require(terminal['fixed_policy_evaluation_complete'] is True and terminal['production_modified'] is False
                and terminal['registration_sha256']==review['registration_sha256']
                and terminal['bank_identities_sha256']==sha(STORE/'bank-identities.json')
                and set(terminal['journals'])=={'20','40','60','100','150','200','400'}
                and all(r['completed_deals']==4096 for r in terminal['journals'].values())
                and len(terminal['range_exports'])==28,'Incomplete original final evaluation')
        require(sha(OUT/(EVAL+'-attempt.json'))==started['original_attempt_sha256'],'Original admission/deadline changed')
        invocations=[read(p) for p in STORE.glob('invocation-*.json')]
        resumed=[r for r in invocations if r['resume'] is True]
        require(len(invocations)==2 and len(resumed)==1 and resumed[0]['pid']==started['pid']
                and abs(resumed[0]['process_created']-started['created'])<.01,'Resumed invocation identity differs')
        for path,digest in review['inputs'].items():
            if Path(path) != OUT/(EVAL+'-status.json'):
                require(sha(path)==digest,'Original review evidence changed during continuation: '+path)
        require(sha(__file__)==self_id['runner_sha256'],'Continuation runner changed')
        publish(RESULT,dict(complete=True,passed=True,unix=time.time(),review_sha256=REVIEW_SHA,
            evaluation_result_sha256=sha(terminal_path),evaluation_registration_sha256=sha(OUT/(EVAL+'-registration.json')),
            original_attempt_preserved=True,original_helper_failure_preserved=True,
            only_unstarted_remaining_batches_allowed=True,original_budgets_and_sources_unchanged=True,
            independent_readback_outstanding=True,broad_goal_complete=False,production_modified=False))
    except BaseException as error:
        publish(FAILED,dict(error=repr(error),traceback=traceback.format_exc(),unix=time.time(),
                            automatic_retry_allowed=False,preserve_evidence=True,production_modified=False))
        raise
    finally:
        if OWNER.exists() and read(OWNER)==self_id: OWNER.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
