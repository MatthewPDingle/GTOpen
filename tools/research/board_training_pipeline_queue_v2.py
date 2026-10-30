"""Preserve the evaluation; globally budget storage before the queued GPU control."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from bounded_parallel_evaluation_archive_v2 import production_available
from weighted_learning_cuda_control_20260927 import LOCK,OTHER
from hu_root_retained_storage_admitted_study_20260924 import measure

PREFIX='board-training-pipeline-queue-v2'


def main(upstream_pid,check_ready=False):
    process=psutil.Process(upstream_pid)
    assert process.is_running() and any('weighted_complete_evaluation_queue_20260927.py' in x for x in process.cmdline())
    upstream=dict(pid=upstream_pid,created=process.create_time(),command=process.cmdline())
    control=ROOT/'tools/research/board_training_pipeline_control_v1.py'
    ready=subprocess.run([sys.executable,str(control),'--check-ready'],cwd=ROOT,capture_output=True,text=True,
                         timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    assert ready.returncode==0,ready.stderr[-2000:]
    assert json.loads(ready.stdout)['ready']
    outputs=['weighted-final-report-evidence.json','board-training-pipeline-control-v1-result.json']
    assert not any((OUT/n).exists() for n in outputs)
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    if check_ready:
        print(json.dumps(dict(ready=True,upstream=upstream,stages=['complete-report','GPU-pipeline-control'])));return
    paths=[OUT/'weighted-complete-evaluation-queue-v1-registration.json',
           OUT/'BOARD-TRAINING-PIPELINE-CONTROL-PLAN.md',*Path(__file__).parent.glob('*.py')]
    inputs={str(p):sha(p) for p in paths}
    save(rp,dict(inputs=inputs,upstream=upstream,maximum_seconds=86400,
        policy='Wait for completed evaluation and independent readback. Never interrupt upstream, retry failures, or promote a trained model.',
        stage_limits_seconds=[180,1860],global_storage_limit=800_000_000_000,
        gpu_control_output_reserve=6_000_000_000,metadata_reserve=2_000_000_000,production_modified=False))
    began=time.monotonic();child=None;completed=[]
    def deadline():assert time.monotonic()-began<86400,'Queue deadline reached'
    def sources():
        for p,h in inputs.items():assert sha(p)==h,p
    try:
        result_path=OUT/'weighted-complete-evaluation-queue-v1-result.json'
        while not result_path.exists():
            deadline()
            assert process.is_running() and process.create_time()==upstream['created'],'Original evaluation queue ended without result'
            assert not (OUT/'weighted-complete-evaluation-queue-v1-failure.json').exists(),'Upstream reported failure'
            time.sleep(30)
        result=read(result_path);assert result['passed']
        assert result['registration_sha256']==sha(OUT/'weighted-complete-evaluation-queue-v1-registration.json')
        for stage in result['stages']:assert sha(stage['result'])==stage['sha256'] and read(stage['result'])['passed']
        stages=[('weighted_final_findings_v1.py',outputs[0],False,180),
                ('board_training_pipeline_control_v1.py',outputs[1],True,1860)]
        for script,output,gpu,limit in stages:
            storage_checked=0.;storage_ok=False
            while True:
                deadline()
                available=production_available() and psutil.virtual_memory().available>28_000_000_000 and psutil.cpu_percent(interval=1)<50
                if gpu:
                    available=available and not LOCK.exists() and not OTHER.exists() and psutil.disk_usage('S:/').free>50*2**30
                    state=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.free','--format=csv,noheader,nounits'],
                        capture_output=True,text=True,timeout=5,creationflags=subprocess.CREATE_NO_WINDOW)
                    if state.returncode==0:
                        util,free=map(float,state.stdout.strip().splitlines()[0].split(','));available=available and util<20 and free>6000
                    else:available=False
                if gpu and available:
                    if time.monotonic()-storage_checked>300:
                        inventory=measure();total=sum(x['allocated_file_bytes'] for x in inventory)
                        storage_ok=total+6_000_000_000+2_000_000_000<=800_000_000_000
                        storage_checked=time.monotonic()
                        print(json.dumps(dict(storage_admitted=storage_ok,allocated_bytes=total,
                            required_reserve_bytes=8_000_000_000)),flush=True)
                    available=storage_ok
                if available:break
                time.sleep(30)
            sources();logpath=OUT/f'{PREFIX}-{Path(script).stem}.log'
            print(json.dumps(dict(starting=script,log=str(logpath))),flush=True)
            with logpath.open('x',encoding='utf-8') as log:
                child=subprocess.Popen([sys.executable,str(ROOT/'tools/research'/script)],cwd=ROOT,
                    stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                assert child.wait(timeout=limit)==0,'Stage failed; inspect '+str(logpath)
            child=None;path=OUT/output;value=read(path)
            if gpu:assert value['passed']
            else:
                assert value['interpretation_pending']
                for p,h in value['outputs'].items():assert sha(p)==h,p
            completed.append(dict(script=script,result=str(path),sha256=sha(path)))
            print(json.dumps(dict(completed=script)),flush=True)
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),stages=completed,
            seconds=time.monotonic()-began,visual_review_and_analysis_pending=True,production_modified=False))
    except BaseException as error:
        save(OUT/f'{PREFIX}-failure.json',dict(passed=False,registration_sha256=sha(rp),error=repr(error),
            completed=completed,seconds=time.monotonic()-began,production_modified=False));raise
    finally:
        if child is not None and child.poll() is None:
            for p in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:p.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate();child.wait(timeout=20)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--upstream-pid',type=int,required=True)
    parser.add_argument('--check-ready',action='store_true');a=parser.parse_args()
    main(a.upstream_pid,a.check_ready)
