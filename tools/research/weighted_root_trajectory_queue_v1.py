"""Run the qualified CPU trajectory analysis after the live bank-control queue."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from bounded_parallel_evaluation_archive_v2 import production_available

PREFIX='weighted-root-trajectory-queue-v1'


def main(queue_pid):
    process=psutil.Process(queue_pid)
    assert process.is_running() and any('weighted_complete_evaluation_queue_20260927.py' in a for a in process.cmdline())
    identity=dict(pid=queue_pid,created=process.create_time(),command=process.cmdline())
    script=ROOT/'tools/research/weighted_root_trajectory_v1.py'
    helper=OUT/'weighted-root-trajectory-control-v1-result.json'
    helperreg=OUT/'weighted-root-trajectory-control-v1-registration.json'
    check=read(helper)
    assert check['passed'] and check['source_sha256']==sha(script) and check['registration_sha256']==sha(helperreg)
    inputs={str(p):sha(p) for p in [helper,helperreg,*Path(__file__).parent.glob('*.py')]}
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,upstream=identity,workers=2,gpu_used=False,maximum_seconds=86400,
        policy='Wait for independently reviewed complete-bank control, then one CPU diagnostic invocation; no retries or outcome-based policy selection.'))
    started=time.monotonic();child=None
    try:
        path=OUT/'weighted-complete-evaluation-control-v1-independent-review.json'
        while not path.exists():
            assert time.monotonic()-started<86400
            assert process.is_running() and process.create_time()==identity['created'], 'Original upstream queue ended before reviewed control'
            failure=OUT/'weighted-complete-evaluation-queue-v1-failure.json'
            assert not failure.exists(), 'Upstream queue reported failure'
            time.sleep(30)
        resultpath=OUT/'weighted-complete-evaluation-control-v1-result.json'
        assert read(path)['passed'] and read(path)['source_result_sha256']==sha(resultpath)
        while not (production_available() and psutil.virtual_memory().available>28_000_000_000 and psutil.cpu_percent(interval=1)<50):
            assert time.monotonic()-started<86400
            time.sleep(30)
        for p,h in inputs.items(): assert sha(p)==h,p
        logpath=OUT/f'{PREFIX}.log'
        print(json.dumps(dict(starting=str(script),log=str(logpath))),flush=True)
        with logpath.open('x',encoding='utf-8') as log:
            child=subprocess.Popen([sys.executable,str(script)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW)
            assert child.wait(timeout=1600)==0, 'Trajectory failed; preserve log and evidence'
        child=None
        result=OUT/'weighted-root-trajectory-v1-result.json'
        assert read(result)['passed']
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),
            result=str(result),result_sha256=sha(result),seconds=time.monotonic()-started,
            gpu_used=False,production_modified=False,scientific_interpretation_pending=True))
    except BaseException as e:
        save(OUT/f'{PREFIX}-failure.json',dict(passed=False,registration_sha256=sha(rp),error=repr(e),
            seconds=time.monotonic()-started,production_modified=False))
        raise
    finally:
        if child is not None and child.poll() is None:
            for p in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:p.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--queue-pid',type=int,required=True)
    main(parser.parse_args().queue_pid)
