"""Six full solve suites with native CPU/host snapshots and PID GPU-memory sampling."""
from pathlib import Path
import ctypes as ct,json,statistics,subprocess,sys,threading,time,traceback
from ctypes import wintypes as w
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
sys.path.insert(0,str(R/'runs/E080-memory-observer-ability'));import win_observer as win
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');E=H/'execution'
def verify():
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
def final_cpu(handle):
    v=[win.FileTime()for _ in range(4)];assert win._k.GetProcessTimes(w.HANDLE(int(handle)),*[ct.byref(x)for x in v]),ct.get_last_error();ticks=lambda x:(x.high<<32)|x.low
    return{'CPU_ticks100ns':ticks(v[2])+ticks(v[3]),'creation_filetime':ticks(v[0]),'exit_filetime':ticks(v[1])}
def markers(text,tag):return[json.loads(x.split(tag+' ',1)[1])for x in text.splitlines()if tag+' 'in x]
def one(spec,binary,folder):
    folder.mkdir();cmd=[str(binary),'postflop_complete_cycle','--ignored','--nocapture','--test-threads=1'];env=old.env();env.pop('POSTFLOP_AUTORESEARCH_FIXTURE',None);env['POSTFLOP_AUTORESEARCH_STORAGE']='compressed';env['POSTFLOP_AUTORESEARCH_PROFILE']='0'
    started=old.now();old.save(folder/'native.invocation.json',{'started_at':started,'command':cmd,'binary_sha256':old.sha(binary),'environment_controls':{k:env.get(k)for k in['RAYON_NUM_THREADS','POSTFLOP_AUTORESEARCH_STORAGE','POSTFLOP_AUTORESEARCH_PROFILE','POSTFLOP_AUTORESEARCH_FIXTURE']},'resource_observation_only':True})
    observer=win.GpuMemory(P['GPU_counter_paths']);proc=None;reader=None;samples=[];read_errors=[]
    try:
        with(folder/'native.stdout.log').open('w',encoding='utf-8',newline='\n')as out,(folder/'native.stderr.log').open('w',encoding='utf-8',newline='\n')as err:
            proc=subprocess.Popen(cmd,cwd=old.REPO,env=env,stdout=subprocess.PIPE,stderr=err,text=True,bufsize=1,creationflags=subprocess.CREATE_NO_WINDOW)
            def read():
                try:
                    for line in proc.stdout:out.write(line);out.flush()
                except BaseException as exc:read_errors.append(repr(exc))
            reader=threading.Thread(target=read,name='resource-stdout',daemon=True);reader.start();deadline=time.monotonic()+600
            while proc.poll()is None:
                assert time.monotonic()<deadline,'resource child timeout';t=time.perf_counter_ns();samples.append(observer.sample(proc.pid));time.sleep(max(0,P['sampling_interval_ms']/1000-(time.perf_counter_ns()-t)/1e9))
            returncode=proc.wait(timeout=30);cpu_end=final_cpu(proc._handle);reader.join(timeout=30);assert not reader.is_alive()and not read_errors;out.flush();assert returncode==0
        observer.close();observer=None;old.save(folder/'native.exit.json',{'started_at':started,'finished_at':old.now(),'command':cmd,'returncode':returncode,'error':None,'cleanup':None,'PID':proc.pid,'final_CPU':cpu_end,'stdout_sha256':old.sha(folder/'native.stdout.log'),'stderr_sha256':old.sha(folder/'native.stderr.log')})
        old.save(folder/'GPU-samples.json',{'at':old.now(),'PID':proc.pid,'sampling_interval_ms':P['sampling_interval_ms'],'samples':samples});text=(folder/'native.stdout.log').read_text(encoding='utf-8');results=markers(text,'AUTORESEARCH_RESULT');stages=markers(text,'AUTORESEARCH_STAGE');points=[{k:x[k]for k in['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']}for x in stages if x.get('stage')=='convergence_check'];anchor=old.historical.exact_raw('E020C1');assert([{k:v for k,v in x.items()if k not in old.historical.EXCLUDED}for x in results],points)==anchor
        resources=[x for x in stages if x.get('stage')=='resource_fixture'];assert[x['fixture_id']for x in resources]==['rainbow','two-tone','river'];suite=[x for x in stages if x.get('stage')=='resource_suite_complete'];assert len(suite)==1
        all_os=[x[k]for x in resources for k in['os_begin','os_timing_complete','os_after_fingerprint']]+[suite[0]['OS']];assert all(x['memory_structure_bytes']==80 for x in all_os);assert len({x['creation_filetime']for x in all_os}|{cpu_end['creation_filetime']})==1;assert cpu_end['exit_filetime']>cpu_end['creation_filetime']and cpu_end['CPU_ticks100ns']>=suite[0]['OS']['cpu_ticks100ns']
        phase={}
        for row in resources:
            b=row['os_begin']['cpu_ticks100ns'];c=row['os_timing_complete']['cpu_ticks100ns'];assert c>=b and row['cpu_delta_ticks100ns']==c-b;phase[row['fixture_id']]=(c-b)/10000.0
        gpu_peaks={};coverage={}
        for name in['Dedicated Usage','Shared Usage']:
            values=[(x['sample_perf_ns'],x['counters'][name]['sum_bytes'])for x in samples if x['counters'][name]['sum_bytes']is not None];assert len(values)>=5;peak=max(v for _,v in values);gpu_peaks[name]=peak
            near=[t for t,v in values if v>=peak-P['guards']['GPU_peak_allowance_bytes']];coverage[name]={'samples':len(values),'near_peak_samples':len(near),'near_peak_span_ms':(max(near)-min(near))/1e6}
        assert gpu_peaks['Dedicated Usage']>=P['minimum_GPU_peak_bytes'];assert coverage['Dedicated Usage']['near_peak_samples']>=P['minimum_GPU_peak_samples']and coverage['Dedicated Usage']['near_peak_span_ms']>=P['minimum_GPU_peak_span_ms']
        gaps=[(b['sample_perf_ns']-a['sample_perf_ns'])/1e6 for a,b in zip(samples,samples[1:])];assert gaps;sg=sorted(gaps);p99=sg[min(len(sg)-1,int(.99*len(sg)))];assert p99<=P['maximum_p99_sampling_gap_ms']
        row={'id':spec['id'],'arm':spec['arm'],'binary_sha256':old.sha(binary),'PID':proc.pid,'phase_CPU_ms':phase,'phase_sum_CPU_ms':sum(phase.values()),'whole_process_CPU_ms':cpu_end['CPU_ticks100ns']/10000.0,'peak_working_bytes':max(x['peak_working_bytes']for x in all_os),'peak_total_commit_bytes':max(x['peak_commit_bytes']for x in all_os),'GPU_dedicated_peak_bytes':gpu_peaks['Dedicated Usage'],'GPU_shared_peak_bytes':gpu_peaks['Shared Usage'],'GPU_sample_count':len(samples),'GPU_sampling_p99_gap_ms':p99,'GPU_sampling_max_gap_ms':max(gaps),'GPU_peak_coverage':coverage,'native_OS_snapshots':resources,'suite_OS':suite[0]['OS'],'all_full_results_and_checkpoints_exact':True,'fixtures':3,'checkpoints':23,'timing_score':False,'stdout_sha256':old.sha(folder/'native.stdout.log'),'GPU_samples_sha256':old.sha(folder/'GPU-samples.json')};old.save(folder/'parsed.json',row);return row
    finally:
        if proc is not None and proc.poll()is None:proc.terminate();proc.wait(timeout=30)
        if reader is not None and reader.is_alive():reader.join(timeout=30)
        if observer is not None:observer.close()
verify();built=old.read(H/'build/complete.json');assert built['all_compilers_terminal']and built['solver_executions']==0
for p,h in built['artifact_sha256'].items():old.pin(p,h)
assert not E.exists();E.mkdir();rows={}
try:
    with old.ar.exclusive_lock(R/'gpu-run.lock'):
        for spec in P['order']:
            verify();old.ar.refuse_active(old.ar.live_status());binary=next(Path(x['binary'])for x in P['compilers']if x['arm']==spec['arm']);old.pin(binary,built['artifact_sha256'][str(binary)]);row=one(spec,binary,E/spec['id']);rows[spec['id']]=row;print(json.dumps({k:row[k]for k in['id','phase_sum_CPU_ms','whole_process_CPU_ms','peak_working_bytes','peak_total_commit_bytes','GPU_dedicated_peak_bytes','GPU_shared_peak_bytes']}),flush=True)
        old.save(E/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'all_owned_children_terminal':True,'order':P['order'],'rows':rows,'all_18_results_138_checkpoints_exact':True,'no_extra_samples_or_exclusions':True,'source_main_live_PTX_unchanged':True});verify()
except BaseException as exc:old.save(E/'failure.json',{'at':old.now(),'error':repr(exc),'traceback':traceback.format_exc(),'completed_ids':list(rows),'candidate_accepted':False});raise
