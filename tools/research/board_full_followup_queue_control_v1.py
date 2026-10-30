"""Check dependency races, process identity, and final-stage dispatch arguments.

Only short synthetic child processes are started. No study stage is executed.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import psutil


def main(module_path, root, destination):
    sys.path.insert(0,str(root/'tools/research'))
    spec = importlib.util.spec_from_file_location('followup_under_test',module_path)
    queue = importlib.util.module_from_spec(spec);spec.loader.exec_module(queue)
    assert not destination.exists()
    checked = 0
    for alive,success,failure in ((a,s,f) for a in (False,True) for s in (False,True) for f in (False,True)):
        rejected = failure or (not alive and not success)
        try:
            value = queue.dependency_ready(alive=alive,success_exists=success,failure_exists=failure)
        except RuntimeError:
            assert rejected
        else:
            assert not rejected and value == (success and not alive)
        checked += 1
    process = subprocess.Popen([sys.executable,'-c','import time; time.sleep(20)'],
        creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    identity = dict(pid=process.pid,created=psutil.Process(process.pid).create_time())
    try:
        assert queue.live(identity)
        assert not queue.live(dict(identity,created=identity['created']-1))
        queue.stop_owned(process,dict(identity,created=identity['created']-1))
        assert process.poll() is None, 'Mismatched process identity must not be terminated'
        queue.stop_owned(process,identity)
        assert process.poll() is not None and not queue.live(identity)
    finally:
        if process.poll() is None:
            process.terminate();process.wait(timeout=10)
    assert [s[0] for s in queue.STAGES] == [
        'training-audit','bank-control','control-audit','evaluation','evaluation-audit','report']
    assert [s[2] for s in queue.STAGES] == [
        ['--workers','8'],['--stage','control','--run'],['--run'],
        ['--stage','evaluation','--run'],['--run'],['--run']]
    assert [s[3] for s in queue.STAGES] == [False,True,False,True,False,False]
    outputs = [n for s in queue.STAGES for n in s[-1]]
    assert len(outputs) == len(set(outputs))
    assert all((root/'tools/research'/s[1]).is_file() for s in queue.STAGES)
    result = dict(passed=True,inputs={str(module_path):queue.sha(module_path),str(Path(__file__)):queue.sha(__file__)},
        dependency_states_checked=checked,reused_pid_rejected=True,mismatched_process_preserved=True,
        owned_synthetic_process_stopped=True,stage_order_and_arguments_checked=True,
        scientific_stages_started=0,production_modified=False)
    with destination.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'inputs'}),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--module',type=Path,required=True)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--result',type=Path,required=True)
    a = parser.parse_args();main(a.module,a.root,a.result)
