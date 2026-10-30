"""Wait for the reviewed existing evaluation, then audit it once without GPU.

No training or evaluation launch/resume; no retry of an admitted reader. The
unchanged reader retains its prespecified archives, replays and 12-hour limit.
"""
import os
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import psutil
sys.path.insert(0,r'T:\Dev\GTOpen\tools\research')
import stack_context_final_report_v2 as evidence
ROOT,OUT=evidence.ROOT,evidence.OUT
NAME=evidence.READBACK_RUN
COMMAND=['C:/Program Files/Python312/python.exe','-B',str(ROOT/'tools/research/stack_context_matched_readback_v6.py'),'--run']
ATTEMPT,RESULT,FAILED,OWNER,STATUS=(OUT/(NAME+s+'.json') for s in ('-attempt','-result','-failure','-owner','-status'))
CONTROL=OUT/(NAME+'-control-result.json')
read,sha,require=evidence.read,evidence.sha,evidence.require

def publish(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,sort_keys=True,separators=(',',':'));stream.flush();os.fsync(stream.fileno())

def status(stage,**fields):
    temporary=STATUS.with_suffix('.writing')
    with temporary.open('w',encoding='utf-8') as stream:
        json.dump(dict(stage=stage,pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time(),**fields),stream)
        stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,STATUS)

def existing_evaluator():
    launcher=read(OUT/(evidence.RESUME+'-attempt.json'))
    child=read(OUT/(evidence.RESUME+'-evaluation-started.json'))
    require(launcher['pid']==116060 and abs(launcher['created']-1790881505.2185621)<.01
            and child['pid']==115596 and abs(child['created']-1790881507.9160383)<.01
            and child['parent_pid']==launcher['pid'],'Unrecognized continuation identities')
    records=((launcher,['C:\\Program Files\\Python312\\pythonw.exe','-B',str(ROOT/'tools/research/stack_context_clean_boundary_resume_v1.py'),'--run']),
             (child,child['command']))
    live=[]
    for record,command in records:
        try:
            p=psutil.Process(record['pid'])
            same=abs(p.create_time()-record['created'])<.01 and p.is_running()
            if same:
                require(p.cmdline()==command,'Unexpected live continuation command')
                if record is child:require(p.ppid()==launcher['pid'],'Unexpected continuation parent')
            live.append(same)
        except psutil.NoSuchProcess:live.append(False)
    return live

def main(run=False):
    if not run:
        print(json.dumps(dict(prepared=True,command=COMMAND,started=ATTEMPT.exists(),
            reader_started=(OUT/(evidence.base.READER+'-attempt.json')).exists(),terminal=RESULT.exists())));return
    require(not any(p.exists() for p in (ATTEMPT,RESULT,FAILED,OWNER,
        OUT/(evidence.base.READER+'-attempt.json'),OUT/(evidence.base.READER+'-result.json'),OUT/(evidence.base.READER+'-failure.json'))),
        'Never duplicate/retry this reader or handoff')
    control=read(CONTROL)
    require(control['complete'] and control['passed'] and control['runner_sha256']==sha(__file__)
            and control['evidence_source_sha256']==sha(Path(evidence.__file__)),
            'Current qualified readback ordering/identity controls required')
    original=read(OUT/(evidence.base.HANDOFF+'-attempt.json'))
    deadline=original['unix']+96*3600
    owner=dict(pid=os.getpid(),created=psutil.Process().create_time(),unix=time.time(),runner_sha256=sha(__file__),
        evidence_source_sha256=sha(Path(evidence.__file__)),launcher_command=[sys.executable,'-B',str(Path(__file__).resolve()),'--run'],
        child_command=COMMAND,original_next_stage_admission_deadline_unix=deadline)
    publish(OWNER,owner);publish(ATTEMPT,owner)
    try:
        while True:
            require(time.time()<deadline,'Original next-stage admission window expired; preserve evidence')
            failures=[OUT/(name+'-failure.json') for name in
                (evidence.RESUME,evidence.base.EVALUATION,evidence.base.READER,'stack-context-pressure-continuation-v2')]
            require(not any(p.exists() for p in failures),'Current science/continuation failed; no retry')
            alive=existing_evaluator()
            if any(alive):status('waiting-for-existing-evaluation',actual_identities_live=alive);time.sleep(30);continue
            require((OUT/(evidence.RESUME+'-result.json')).exists(),'Existing continuation stopped without successful terminal evidence')
            # This helper's own owner is expected during admission. The evidence
            # function still checks every other owner and all terminal/exit pins.
            original_locks=evidence.LOCKS
            evidence.LOCKS=tuple(p for p in original_locks if p!=OWNER)
            try:terminal,_,inputs=evidence.terminal_evidence(include_reader=False)
            finally:evidence.LOCKS=original_locks
            from river_matched_training_pilot_v1 import available,production_available
            ready,probe=available()
            if not ready or not production_available() or psutil.virtual_memory().available<40_000_000_000:
                status('waiting-before-reader-admission',probe=probe);time.sleep(30);continue
            require(not any((OUT/(evidence.base.READER+suffix+'.json')).exists() for suffix in ('-attempt','-result','-failure')),
                    'Independent reader already admitted')
            prefix=OUT/(NAME+'-reader')
            with Path(str(prefix)+'-stdout.log').open('xb') as stdout,Path(str(prefix)+'-stderr.log').open('xb') as stderr:
                child=subprocess.Popen(COMMAND,cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
                started=dict(pid=child.pid,created=psutil.Process(child.pid).create_time(),parent_pid=os.getpid(),unix=time.time(),
                    command=COMMAND,evaluation_result_sha256=sha(OUT/(evidence.base.EVALUATION+'-result.json')))
                publish(str(prefix)+'-started.json',started);status('reader-running',child=started)
                code=child.wait()
            finished=dict(**started,exit_code=code,finished_unix=time.time(),
                stdout_sha256=sha(str(prefix)+'-stdout.log'),stderr_sha256=sha(str(prefix)+'-stderr.log'))
            publish(str(prefix)+'-finished.json',finished)
            require(code==0,'Independent reader failed; preserve without retry')
            reader_path=OUT/(evidence.base.READER+'-result.json');reader=read(reader_path)
            require(all(reader[k] is True for k in ('complete','passed','independent_readback_complete'))
                    and reader['evaluation_result_sha256']==started['evaluation_result_sha256'],
                    'Independent reader lacks successful matching terminal evidence')
            require(not (ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock').exists(),
                    'Reader did not release its study lock')
            require(sha(__file__)==owner['runner_sha256'] and sha(Path(evidence.__file__))==owner['evidence_source_sha256'],
                    'Readback handoff/evidence source changed')
            publish(RESULT,dict(complete=True,passed=True,unix=time.time(),reader_result_sha256=sha(reader_path),
                evaluation_result_sha256=started['evaluation_result_sha256'],independent_readback_complete=True,
                original_evaluation_and_reader_unchanged=True,new_scientific_deals=False,fitting=False,
                native_execution=False,gpu_used=False,production_modified=False,broad_goal_complete=False))
            status('independent-readback-complete-root-analysis-outstanding');return
    except BaseException as error:
        publish(FAILED,dict(error=repr(error),traceback=traceback.format_exc(),unix=time.time(),
            automatic_retry_allowed=False,preserve_evidence=True,production_modified=False));raise
    finally:
        if OWNER.exists() and read(OWNER)==owner:OWNER.unlink()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');main(parser.parse_args().run)
