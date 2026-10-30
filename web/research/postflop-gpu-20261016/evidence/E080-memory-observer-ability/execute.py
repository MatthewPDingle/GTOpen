"""One compiler and one frozen CPU/GPU allocation-and-release calibration."""
from pathlib import Path
import json,os,shutil,statistics,subprocess,sys,time,traceback
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
from win_observer import GpuMemory,process_sample
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');B=H/'build';E=H/'execution'
def verify():
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
verify();assert not B.exists()and not E.exists();observer=None;proc=None;fault=None
try:
    with old.ar.exclusive_lock(R/'gpu-run.lock'):
        old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;B.mkdir();E.mkdir();old.child(P['rustc_command'],B,'rustc',old.env(),600);verify();binary=B/'probe.exe';bsha=old.sha(binary)
        observer=GpuMemory(P['counter_paths']);started=old.now();command=[str(binary)];old.save(E/'native.invocation.json',{'started_at':started,'command':command,'binary_sha256':bsha,'environment':'accepted E051 live helper env; unchanged CUDA settings','purpose':'known own CPU/GPU allocation accounting calibration only'})
        records=[]
        with(E/'native.stdout.log').open('w',encoding='utf-8',newline='\n')as out,(E/'native.stderr.log').open('w',encoding='utf-8',newline='\n')as err:
            proc=subprocess.Popen(command,cwd=old.REPO,env=old.env(),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True,bufsize=1,creationflags=subprocess.CREATE_NO_WINDOW)
            for spec in P['states']:
                line=proc.stdout.readline();out.write(line);out.flush();assert line.startswith('E080_MEM_ABILITY '),(spec['stage'],line,proc.poll());row=json.loads(line.split('E080_MEM_ABILITY ',1)[1]);assert row['stage']==spec['stage']and row['PID']==proc.pid and row['CPU_owned_payload_bytes']==spec['CPU_bytes']and row['GPU_owned_payload_bytes']==spec['GPU_bytes']
                samples=[]
                for _ in range(P['samples_per_state']):
                    tick=time.perf_counter_ns();cpu=process_sample(proc._handle);gpu=observer.sample(proc.pid);samples.append({'CPU':cpu,'GPU':gpu});elapsed=time.perf_counter_ns()-tick;time.sleep(max(0,P['interval_ms']/1000-elapsed/1e9))
                assert all(x['GPU']['pid']==proc.pid for x in samples);assert all(a['CPU']['CPU_ticks100ns']<=b['CPU']['CPU_ticks100ns']for a,b in zip(samples,samples[1:]));records.append({'stage':spec['stage'],'native':row,'samples':samples})
                old.save(E/(spec['stage']+'.json'),records[-1]);print('Observed fixed allocation state',spec['stage'],flush=True);proc.stdin.write('continue\n');proc.stdin.flush()
            line=proc.stdout.readline();out.write(line);out.flush();assert line.startswith('E080_MEM_ABILITY ');final=json.loads(line.split('E080_MEM_ABILITY ',1)[1]);assert final=={'stage':'complete','states':9,'GPU_allocations_including_prime':4,'GPU_release_calls':4,'CPU_allocations':1,'canary_bytes_checked':512,'application_kernels':0,'NVRTC_compiles':0}
            remainder=proc.stdout.read();out.write(remainder);out.flush();assert proc.wait(timeout=30)==0
        observer.close();observer=None;old.save(E/'native.exit.json',{'started_at':started,'finished_at':old.now(),'command':command,'returncode':0,'error':None,'cleanup':None,'PID':proc.pid,'binary_sha256':bsha,'stdout_sha256':old.sha(E/'native.stdout.log'),'stderr_sha256':old.sha(E/'native.stderr.log')});verify()
        plateau={}
        for row in records:
            tail=row['samples'][-P['plateau_samples']:];gpu=[x['GPU']['counters']['Dedicated Usage']['sum_bytes']for x in tail];private=[x['CPU']['PrivateUsage']for x in tail];rss=[x['CPU']['WorkingSetSize']for x in tail]
            plateau[row['stage']]={'GPU_dedicated_bytes':None if any(x is None for x in gpu)else statistics.median(gpu),'GPU_span_bytes':None if any(x is None for x in gpu)else max(gpu)-min(gpu),'private_bytes':statistics.median(private),'working_set_bytes':statistics.median(rss),'creation_filetime':tail[0]['CPU']['creation_filetime']}
        assert len({x['creation_filetime']for x in plateau.values()})==1;base=plateau['baseline'];checks=[];tol=P['maximum_accounting_error_bytes']
        def ck(label,observed,expected):
            good=observed is not None and abs(observed-expected)<=tol;checks.append({'label':label,'observed_delta_bytes':observed,'expected_delta_bytes':expected,'absolute_tolerance_bytes':tol,'passed':good})
        ck('CPU private allocation',plateau['CPU128']['private_bytes']-base['private_bytes'],128*1024*1024);ck('CPU working-set allocation',plateau['CPU128']['working_set_bytes']-base['working_set_bytes'],128*1024*1024);ck('CPU private release',plateau['CPU_free']['private_bytes']-base['private_bytes'],0)
        for spec in P['states']:
            x=plateau[spec['stage']];delta=None if x['GPU_dedicated_bytes']is None or base['GPU_dedicated_bytes']is None else x['GPU_dedicated_bytes']-base['GPU_dedicated_bytes'];ck(spec['stage']+' GPU allocation/release',delta,spec['GPU_bytes']);ck(spec['stage']+' GPU plateau stability',x['GPU_span_bytes'],0)
        passed=all(x['passed']for x in checks);old.save(H/'report.json',{'id':'E080-memory-observer-ability','at':old.now(),'status':'eligible_software_memory_observer_for_fixed_resource_trial'if passed else'decline_software_memory_observer_accounting_mismatch','protocol_sha256':sys.argv[1],'binary_sha256':bsha,'plateaus':plateau,'checks':checks,'all_checks_pass':passed,'native_processes':1,'compiler_processes':1,'states':9,'source_candidate_activated':False,'solver_executions':0,'performance_claim':False,'actual_CPU_cost_qualification':False,'candidate_accepted':False,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'excluded_states':[],'extra_samples':0,'limits':'One known-allocation/readback and repeated-release calibration on this Windows/driver/RTX5090. PID-filtered software memory accounting is not a shader hardware counter or universal measurement guarantee. Other GPU memory counters are diagnostic only. A failed calibration closes this observer form without threshold/sample variants. No GTOpen cost, responsiveness, final scope or adoption conclusion.'});verify()
        print(json.dumps({'status':'eligible_software_memory_observer'if passed else'observer_declined','checks':len(checks),'failed_checks':[x['label']for x in checks if not x['passed']],'plateaus':plateau}),flush=True)
except BaseException as exc:
    fault=repr(exc);old.save(H/'execution-failure.json',{'at':old.now(),'error':fault,'traceback':traceback.format_exc(),'candidate_accepted':False,'source_candidate_activated':False});raise
finally:
    if proc is not None and proc.poll()is None:
        proc.terminate();proc.wait(timeout=30)
    if observer is not None:observer.close()
    old.custody()
