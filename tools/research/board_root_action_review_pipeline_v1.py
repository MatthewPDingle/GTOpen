"""Continue the active replay into verification and reporting, once only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from board_prefix_publication_v1 import atomic_json

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-root-action-review-pipeline-v1'
REG=OUT/(PREFIX+'-registration.json')
STATUS=OUT/(PREFIX+'-status.json')
REPLAY_PID=51220
REPLAY_CREATED=1790561572.256763


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())


def main(run=False):
    if not run:
        print(json.dumps(dict(would_wait_for_pid=REPLAY_PID,starts_nothing=True)));return
    replay_reg=OUT/'board-root-action-replay-v1-registration.json'
    replay_result=OUT/'board-root-action-replay-v1-replay.json'
    reviewer=ROOT/'tools/research/board_root_action_replay_readback_v1.py'
    reporter=ROOT/'tools/research/board_root_action_interpretation_v1.py'
    assert sha(replay_reg) == '224aaef02de74c1191cce8bcdade3718481528f98bd7146a8002c1b3242846cf'
    assert sha(reviewer) == '602bb5fe13a35bc796d270922adf73e0269f599bb5def4ab9a7a8ba15b969136'
    assert not REG.exists() and not STATUS.exists()
    sources=[replay_reg,reviewer,reporter,Path(__file__)]
    registration=dict(format=1,controller_pid=os.getpid(),controller_created=psutil.Process().create_time(),
        replay_pid=REPLAY_PID,replay_created=REPLAY_CREATED,inputs={str(p):sha(p) for p in sources},
        deadline_for_replay=read(replay_reg)['deadline_unix'],readback_maximum_seconds=3800,
        launches_training=False,restarts_replay=False,production_modified=False)
    atomic_json(REG,registration)
    def status(state,**extra):
        atomic_json(STATUS,dict(state=state,registration_sha256=sha(REG),updated_unix=time.time(),**extra))
    child=None
    def launch(script,arguments,stage,limit):
        nonlocal child
        for p,h in registration['inputs'].items():assert sha(p) == h,p
        out=OUT/(PREFIX+'-'+stage+'.log');err=OUT/(PREFIX+'-'+stage+'.stderr.log')
        with out.open('xb') as stdout,err.open('xb') as stderr:
            child=subprocess.Popen([sys.executable,'-B',str(script),*arguments],cwd=ROOT,
                stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            status(stage,child_pid=child.pid,stdout=str(out),stderr=str(err))
            deadline=time.monotonic()+limit
            while child.poll() is None:
                assert time.monotonic() < deadline,stage+' exceeded its bound'
                time.sleep(5)
            code=child.returncode;child=None
            assert code == 0,stage+' failed; inspect '+str(err)
    try:
        status('waiting_for_existing_replay')
        while True:
            assert time.time() < registration['deadline_for_replay'],'Original replay deadline reached'
            try:
                process=psutil.Process(REPLAY_PID)
                assert abs(process.create_time()-REPLAY_CREATED) < .01,'Replay PID was reused'
                assert 'board_root_action_replay_v1.py' in ' '.join(process.cmdline())
            except psutil.NoSuchProcess:
                break
            time.sleep(10)
        assert replay_result.exists(),'Replay terminated without its result; no automatic retry'
        result=read(replay_result)
        assert result['replay_finished'] and result['registration_sha256'] == sha(replay_reg)
        launch(reviewer,['--run'],'readback',3800)
        launch(reporter,[],'interpretation',120)
        status('finished',readback_result=str(OUT/'board-root-action-replay-readback-v1-result.json'),
            report=str(OUT/'BOARD-ROOT-ACTION-VALUE-FINDINGS.md'),
            scientific_interpretation_pending=True,accuracy_qualified=False)
    except BaseException as error:
        status('failed',error=repr(error),automatic_retry=False)
        raise
    finally:
        if child is not None and child.poll() is None:
            try:
                for descendant in psutil.Process(child.pid).children(recursive=True):
                    try:descendant.kill()
                    except psutil.NoSuchProcess:pass
            except psutil.NoSuchProcess:pass
            child.kill();child.wait(timeout=15)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true')
    main(parser.parse_args().run)
