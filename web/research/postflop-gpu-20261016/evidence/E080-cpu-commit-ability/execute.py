"""One CPU-only control, retaining the earlier combined failure unchanged."""
from pathlib import Path
import json,statistics,subprocess,sys,time,traceback
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
sys.path.insert(0,str(R/'runs/E080-memory-observer-ability'));from win_observer import process_sample
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');E=H/'execution';assert not E.exists();proc=None;rows=[]
def verify():
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
verify()
try:
    with old.ar.exclusive_lock(R/'gpu-run.lock'):
        old.ar.refuse_active(old.ar.live_status());E.mkdir();started=old.now();command=[sys.executable,'-B',str(H/'probe.py')];old.save(E/'native.invocation.json',{'started_at':started,'command':command,'purpose':'CPU-only explicit commitment accounting validation; no solver or CUDA'})
        with(E/'native.stdout.log').open('w',encoding='utf-8',newline='\n')as out,(E/'native.stderr.log').open('w',encoding='utf-8',newline='\n')as err:
            proc=subprocess.Popen(command,cwd=old.REPO,env=old.env(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,bufsize=1,creationflags=subprocess.CREATE_NO_WINDOW)
            for spec in P['states']:
                line=proc.stdout.readline();out.write(line);out.flush();assert line.startswith('E080_CPU_COMMIT ');row=json.loads(line.split('E080_CPU_COMMIT ',1)[1]);assert row=={'stage':spec['stage'],'PID':proc.pid,'committed_touched_owned_bytes':spec['bytes'],'CUDA_loaded':False};samples=[]
                for _ in range(P['samples_per_state']):
                    t=time.perf_counter_ns();samples.append(process_sample(proc._handle));time.sleep(max(0,P['interval_ms']/1000-(time.perf_counter_ns()-t)/1e9))
                assert all(a['CPU_ticks100ns']<=b['CPU_ticks100ns']for a,b in zip(samples,samples[1:]));rows.append({'native':row,'samples':samples});old.save(E/(spec['stage']+'.json'),rows[-1]);print('Observed CPU-only commitment state',spec['stage'],flush=True);proc.stdin.write('continue\n');proc.stdin.flush()
            line=proc.stdout.readline();out.write(line);out.flush();assert line.startswith('E080_CPU_COMMIT ');assert json.loads(line.split('E080_CPU_COMMIT ',1)[1])=={'stage':'complete','states':7,'VirtualAlloc_calls':3,'VirtualFree_calls':3,'CUDA_loaded':False};out.write(proc.stdout.read());out.flush();assert proc.wait(timeout=30)==0
        old.save(E/'native.exit.json',{'started_at':started,'finished_at':old.now(),'command':command,'returncode':0,'error':None,'cleanup':None,'PID':proc.pid,'stdout_sha256':old.sha(E/'native.stdout.log'),'stderr_sha256':old.sha(E/'native.stderr.log')});verify();levels={}
        for row in rows:
            tail=row['samples'][-P['plateau_samples']:];levels[row['native']['stage']]={key:statistics.median(x[key]for x in tail)for key in['PrivateUsage','WorkingSetSize']};levels[row['native']['stage']]['Private_span_bytes']=max(x['PrivateUsage']for x in tail)-min(x['PrivateUsage']for x in tail);levels[row['native']['stage']]['creation_filetime']=tail[0]['creation_filetime']
        assert len({x['creation_filetime']for x in levels.values()})==1;checks=[];base=levels['baseline']
        for spec in P['states']:
            x=levels[spec['stage']]
            for metric in['PrivateUsage','WorkingSetSize']:
                delta=x[metric]-base[metric];checks.append({'label':spec['stage']+' '+metric,'observed_delta_bytes':delta,'expected_delta_bytes':spec['bytes'],'absolute_tolerance_bytes':P['tolerance_bytes'],'passed':abs(delta-spec['bytes'])<=P['tolerance_bytes']})
            checks.append({'label':spec['stage']+' stable total commitment','span_bytes':x['Private_span_bytes'],'absolute_tolerance_bytes':P['tolerance_bytes'],'passed':x['Private_span_bytes']<=P['tolerance_bytes']})
        passed=all(x['passed']for x in checks);old.save(H/'report.json',{'id':'E080-CPU-explicit-commit-ability','at':old.now(),'status':'CPU_commit_and_RSS_API_calibration_pass'if passed else'CPU_commit_observer_declined','protocol_sha256':sys.argv[1],'all_checks_pass':passed,'checks':checks,'plateaus':levels,'native_processes':1,'solver_executions':0,'CUDA_contexts':0,'VirtualAlloc_calls':3,'VirtualFree_calls':3,'original_combined_calibration_pass':False,'original_combined_report_sha256':old.sha(R/'runs/E080-memory-observer-ability/report.json'),'excluded_states':[],'extra_samples':0,'candidate_accepted':False,'actual_solver_costs_qualified':False,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'scope':'Independent Windows commitment/RSS API validation with explicit own-process committed/touched pages. CUDA absence checked in child. Original mixed-process failed calibration remains failed. This does not replace any solver workload, exclude driver commitment from actual profiling, or qualify whole solver cost.'});verify();print(json.dumps({'status':'CPU_commit_calibration_pass'if passed else'CPU_commit_observer_declined','failed_checks':[x['label']for x in checks if not x['passed']],'plateaus':levels}),flush=True)
except BaseException as exc:
    old.save(H/'execution-failure.json',{'at':old.now(),'error':repr(exc),'traceback':traceback.format_exc(),'candidate_accepted':False});raise
finally:
    if proc is not None and proc.poll()is None:proc.terminate();proc.wait(timeout=30)
    old.custody()
