"""Read-only Windows CPU/RAM/disk guard for large diagnostic capture,not speed scoring."""
import ctypes as c,importlib.util,subprocess,time,shutil
from pathlib import Path
spec=importlib.util.spec_from_file_location('base_sampler',Path(__file__).with_name('sampler.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
class GlobalMemory(c.Structure):
    _fields_=[('length',c.c_uint32),('load',c.c_uint32)]+[(n,c.c_uint64) for n in ['total_physical','available_physical','total_pagefile','available_pagefile','total_virtual','available_virtual','available_extended_virtual']]
assert c.sizeof(GlobalMemory)==64
s.KERNEL.GlobalMemoryStatusEx.argtypes=[c.POINTER(GlobalMemory)];s.KERNEL.GlobalMemoryStatusEx.restype=c.c_int
def memory():
    v=GlobalMemory();v.length=c.sizeof(v)
    if not s.KERNEL.GlobalMemoryStatusEx(c.byref(v)):raise c.WinError(c.get_last_error())
    result={n:int(getattr(v,n)) for n,_ in v._fields_};assert result['length']==64 and 0<result['available_physical']<=result['total_physical']
    return result
def raw_bytes(folder):return sum(p.stat().st_size for d in Path(folder).glob('*-output') for p in d.iterdir() if p.is_file())
def run(command,out,label,h,limits,raw_root,output,workers):
    proc=handle=None;error=cleanup=None;rows=[];started=h.now();clock=time.monotonic();terminal=None
    initial=memory();assert initial['available_physical']>=limits['available_RAM_before_bytes']
    assert shutil.disk_usage(raw_root).free>=limits['required_free_bytes']
    h.save(out/(label+'.invocation.json'),{'at':started,'command':command,'cwd':str(h.REPO),'output_env':{'D156_OUTPUT':str(output),'RAYON_NUM_THREADS':str(workers)},'limits':limits,'global_memory_before':initial})
    print('Starting guarded',label,flush=True)
    try:
        env=h.env();env['D156_OUTPUT']=str(output);assert workers in [8,16,32];env['RAYON_NUM_THREADS']=str(workers)
        with (out/(label+'.stdout.log')).open('xb') as stdout,(out/(label+'.stderr.log')).open('xb') as stderr:
            proc=subprocess.Popen(command,cwd=h.REPO,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            handle=s.KERNEL.OpenProcess(0x1000|0x0010,False,proc.pid)
            if not handle:raise c.WinError(c.get_last_error())
            announced=0
            while proc.poll() is None:
                stamp=time.monotonic();global_=memory();info=None;race=None
                try:info=s.process_memory(handle)
                except OSError as exc:
                    if proc.poll() is None:raise
                    race=repr(exc)
                free=shutil.disk_usage(raw_root).free;size=raw_bytes(raw_root)
                rows.append({'elapsed_ms':(stamp-clock)*1000,'global_memory':global_,'process_memory':info,'terminal_memory_race':race,'X_free_bytes':free,'raw_bytes':size})
                assert global_['available_physical']>=limits['available_RAM_during_bytes'],'system availableRAM guard'
                assert free>=limits['disk_headroom_bytes'] and size<=limits['raw_reservation_bytes'],'raw/disk guard'
                if info:
                    assert info['PeakWorkingSetSize']<=limits['process_reported_peak_max_bytes'] and info['PeakPagefileUsage']<=limits['process_reported_peak_max_bytes'],'process reported memory guard'
                elapsed=stamp-clock
                if elapsed>limits['native_timeout_seconds']:raise TimeoutError(label)
                if elapsed-announced>=30:print(label,'running',int(elapsed),'seconds;PID',proc.pid,'raw',size,'bytes',flush=True);announced=elapsed
                try:proc.wait(timeout=limits['poll_interval_ms']/1000)
                except subprocess.TimeoutExpired:pass
            terminal=s.process_times(handle,True)
        assert proc.returncode==0,(label,(out/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-4000:])
        assert raw_bytes(raw_root)<=limits['raw_reservation_bytes'] and shutil.disk_usage(raw_root).free>=limits['disk_headroom_bytes']
        good=[x['process_memory'] for x in rows if x['process_memory']]
        assert good and terminal['lifetime_ms']>0 and terminal['CPU_ms']>0
        h.save(out/(label+'.resource.json'),{'at':h.now(),'pid':proc.pid,'returncode':proc.returncode,'samples':rows,'sample_count':len(rows),'reported_peak_working_set_bytes':max(x['PeakWorkingSetSize'] for x in good),'reported_peak_commit_bytes':max(x['PeakPagefileUsage'] for x in good),'minimum_observed_available_RAM_bytes':min(x['global_memory']['available_physical'] for x in rows),'terminal_process_times':terminal,'raw_bytes_after':raw_bytes(raw_root),'scope':'Diagnostic guard,sampled while alive. Reported high-water counters may miss a late post-final-sample transient. TerminalCPU/lifetime cover cleanup. Global availableRAM includes standby/free/zero lists andisvolatile. No GPUmemory/hardwarecounter/globalsetting call;never performance qualification.'})
    except BaseException as exc:error=repr(exc);cleanup=h.ar.cleanup_child(proc);raise
    finally:
        if handle:assert s.KERNEL.CloseHandle(handle)
        h.save(out/(label+'.exit.json'),{'started_at':started,'finished_at':h.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
