"""Resume-safe sequencing of the already specified night-shift checks."""
import datetime as dt
import json
import msvcrt
import os
import subprocess
import sys
import time
import continuation_bridge_run as bridge

study=bridge.study
OUT=study.ROOT/'research/preflop-evolution/continuation/night-shift-20260916'
BASE=OUT.parent


def processes():
    command='Get-CimInstance Win32_Process | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress'
    result=subprocess.run(['powershell.exe','-NoProfile','-Command',command],capture_output=True,text=True,check=True)
    value=json.loads(result.stdout)
    return value if isinstance(value,list) else [value]


def dependency_alive(snapshot,pid):
    matches=[p for p in snapshot if p['ProcessId']==pid]
    if not matches:return False
    assert len(matches)==1
    process=matches[0]
    assert process['Name'].lower() in ['python.exe','pythonw.exe'] and 'continuation_bridge_run.py run' in (process['CommandLine'] or '').lower(), 'Dependency PID has an unexpected identity; inspect before proceeding'
    return True


def state(stage,**extra):
    value=dict(stage=stage,controller_pid=os.getpid(),updated=study.night.now(),production_enabled=False,**extra)
    study.night.dump(OUT/'queue-status.json',value)
    print(stage,extra,flush=True)


def training_ready(count,total,status):
    # A file can exist while its writer is still finishing. The reference
    # controller publishes these stages only after waiting for the child.
    acknowledged=(status.get('stage')=='training' and status.get('completed')==total)
    acknowledged |= status.get('stage') in ['evaluation','rejected_training_screen','complete']
    return count==total and acknowledged


def deadline():
    if dt.datetime.now(dt.timezone.utc)>=bridge.DEADLINE:
        state('deadline_checkpoint');raise SystemExit(4)


def child(script,args,label,marker):
    deadline()
    if marker.exists():
        state('existing_result',result=str(marker.relative_to(study.ROOT)))
        return
    # GPU children enforce the live-app and research-overlap guards themselves.
    # CPU screens are sequential and finish before the timing benchmark.
    with (OUT/f'queue-{label}.log').open('a') as log:
        process=subprocess.Popen([sys.executable,str(study.ROOT/'tools/research'/script),*args],
            cwd=study.ROOT,stdout=log,stderr=subprocess.STDOUT)
        state(label,active_child_pid=process.pid,command=script+' '+' '.join(args))
        code=process.wait()
    assert code==0,f'{label} exited {code}; see its queue log before resuming'
    assert marker.exists(),f'{label} produced no expected result'


def run(dependency_pid):
    with (OUT/'queue.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
        msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            manifest=bridge.checked('training')
            while True:
                deadline()
                live=dependency_alive(processes(),dependency_pid)
                count=sum((bridge.OUT/'training/jobs'/f"{j['id']}.json").exists() for j in manifest['jobs'])
                reference_state=study.read(bridge.OUT/'status.json')
                if training_ready(count,len(manifest['jobs']),reference_state):break
                if not live:
                    state('dependency_stopped_before_training_complete',completed=count,total=len(manifest['jobs']))
                    return
                state('waiting_for_training',dependency_pid=dependency_pid,completed=count,total=len(manifest['jobs']))
                time.sleep(30)
            # All references are audited by each screen's contexts loader.
            child('continuation_nonlinear_expanded.py',[],'nonlinear_screen',BASE/'nonlinear-expanded-20260916/training-screen.json')
            child('continuation_precision_weighted.py',[],'precision_screen',BASE/'precision-weighted-20260916/training-screen.json')
            child('continuation_depth_expanded.py',[],'depth_expanded_screen',BASE/'depth-priors-expanded-20260916/training-screen.json')
            depth_eligible=study.read(BASE/'depth-priors-expanded-20260916/training-screen.json')['eligible']
            if depth_eligible:
                child('continuation_depth_evaluation.py',['prepare'],'register_depth_candidate',BASE/'depth-priors-expanded-20260916/evaluation-registration.json')
            while dependency_alive(processes(),dependency_pid):
                deadline();state('waiting_for_reference_controller',dependency_pid=dependency_pid);time.sleep(30)
            # Do not launch any GPU workload after a failed/deferred dependency.
            terminal=study.read(bridge.OUT/'status.json')['stage']
            assert terminal in ['complete','rejected_training_screen'],f'Reference dependency stopped in {terminal}; inspect before continuing'
            child('continuation_bridge_report.py',[],'reference_report',bridge.OUT/'RESULTS.md')
            child('continuation_interface_reuse.py',['benchmark'],'runtime_benchmark',BASE/'interface-work-reuse-20260916/timing.json')
            child('continuation_prior_evaluation.py',['run'],'prior_evaluation',BASE/'recalibrated-priors-20260916/evaluation.json')
            if study.read(BASE/'recalibrated-priors-20260916/evaluation.json')['accuracy_screen_passed']:
                child('continuation_prior_gpu.py',['oracle'],'prior_gpu_oracle',BASE/'recalibrated-priors-gpu-20260916/oracle-check.json')
                child('continuation_prior_gpu.py',['benchmark'],'prior_gpu_benchmark',BASE/'recalibrated-priors-gpu-20260916/timing.json')
            child('continuation_final_evaluation.py',['register'],'register_candidates',BASE/'expanded-validation-20260916/registered-models.json')
            registry=study.read(BASE/'expanded-validation-20260916/registered-models.json')
            if registry['models']:
                child('continuation_final_evaluation.py',['run'],'fresh_evaluation',BASE/'expanded-validation-20260916/evaluation.json')
            if depth_eligible:
                child('continuation_depth_evaluation.py',['run'],'depth_fresh_evaluation',BASE/'depth-priors-expanded-20260916/evaluation.json')
            state('queued_checks_complete',registered_models=[r['name'] for r in registry['models']],
                note='Review, reporting, GitHub push and any qualified combined-model checks remain; this does not complete the night-shift goal.')
        except Exception as error:
            state('failed',error=str(error));raise
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':run(int(sys.argv[1]))
