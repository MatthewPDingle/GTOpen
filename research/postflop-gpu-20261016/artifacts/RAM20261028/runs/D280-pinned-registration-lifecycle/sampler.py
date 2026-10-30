"""Read-only Win32 process statistics and global NVML memory, no GPU counters."""
import ctypes as c, os, sys, json, time, subprocess
from pathlib import Path
DWORD=c.c_uint32; U64=c.c_uint64; SIZE=c.c_size_t; HANDLE=c.c_void_p
class FileTime(c.Structure):
    _fields_=[('lo',DWORD),('hi',DWORD)]
    def ticks(self):return self.lo|(self.hi<<32)
class Memory(c.Structure):
    _fields_=[('cb',DWORD),('PageFaultCount',DWORD)]+[(x,SIZE) for x in ['PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage']]
class SystemMemory(c.Structure):
    _fields_=[('length',DWORD),('load',DWORD)]+[(x,U64)for x in ['total_physical','available_physical','total_pagefile','available_pagefile','total_virtual','available_virtual','extended']]
def system_memory():
    info=SystemMemory();info.length=c.sizeof(info)
    if not KERNEL.GlobalMemoryStatusEx(c.byref(info)):raise c.WinError(c.get_last_error())
    return {'available_physical_bytes':int(info.available_physical),'system_commit_used_bytes':int(info.total_pagefile-info.available_pagefile),'system_commit_limit_bytes':int(info.total_pagefile)}
class GpuMemory(c.Structure):
    _fields_=[('total',U64),('free',U64),('used',U64)]
assert c.sizeof(FileTime)==8 and c.sizeof(Memory)==80 and c.sizeof(GpuMemory)==24 and c.sizeof(HANDLE)==8
KERNEL=c.WinDLL(r'C:\Windows\System32\kernel32.dll',use_last_error=True)
KERNEL.GlobalMemoryStatusEx.argtypes=[c.POINTER(SystemMemory)];KERNEL.GlobalMemoryStatusEx.restype=c.c_int
KERNEL.OpenProcess.argtypes=[DWORD,c.c_int,DWORD];KERNEL.OpenProcess.restype=HANDLE
KERNEL.CloseHandle.argtypes=[HANDLE];KERNEL.CloseHandle.restype=c.c_int
KERNEL.GetCurrentProcess.argtypes=[];KERNEL.GetCurrentProcess.restype=HANDLE
KERNEL.K32GetProcessMemoryInfo.argtypes=[HANDLE,c.POINTER(Memory),DWORD];KERNEL.K32GetProcessMemoryInfo.restype=c.c_int
KERNEL.GetProcessTimes.argtypes=[HANDLE]+[c.POINTER(FileTime)]*4;KERNEL.GetProcessTimes.restype=c.c_int

def process_memory(handle):
    info=Memory();info.cb=c.sizeof(info)
    if not KERNEL.K32GetProcessMemoryInfo(handle,c.byref(info),c.sizeof(info)):raise c.WinError(c.get_last_error())
    return {name:int(getattr(info,name)) for name,_ in info._fields_}
def process_times(handle,terminal=False):
    values=[FileTime() for _ in range(4)]
    if not KERNEL.GetProcessTimes(handle,*[c.byref(v) for v in values]):raise c.WinError(c.get_last_error())
    creation,exit_,kernel,user=[x.ticks() for x in values]
    return {'creation_FILETIME':creation,'exit_FILETIME':exit_ if terminal else None,'kernel_100ns':kernel,'user_100ns':user,'CPU_ms':(kernel+user)/10000,'lifetime_ms':(exit_-creation)/10000 if terminal else None}

class Nvml:
    def __init__(self):
        self.dll=c.CDLL(r'C:\Windows\System32\nvml.dll')
        for name,args in [('nvmlInit_v2',[]),('nvmlShutdown',[]),('nvmlDeviceGetHandleByUUID',[c.c_char_p,c.POINTER(HANDLE)]),('nvmlDeviceGetMemoryInfo',[HANDLE,c.POINTER(GpuMemory)]),('nvmlSystemGetDriverVersion',[c.c_char_p,DWORD]),('nvmlSystemGetNVMLVersion',[c.c_char_p,DWORD]),('nvmlDeviceGetUUID',[HANDLE,c.c_char_p,DWORD])]:
            fn=getattr(self.dll,name);fn.argtypes=args;fn.restype=c.c_int
        self.check(self.dll.nvmlInit_v2());self.handle=HANDLE()
        self.check(self.dll.nvmlDeviceGetHandleByUUID(b'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee',c.byref(self.handle)))
        uuid=c.create_string_buffer(128);self.check(self.dll.nvmlDeviceGetUUID(self.handle,uuid,128));self.uuid=uuid.value.decode()
        assert self.uuid=='GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee'
    def check(self,code):assert code==0,('NVML',code)
    def memory(self):
        value=GpuMemory();self.check(self.dll.nvmlDeviceGetMemoryInfo(self.handle,c.byref(value)))
        result={name:int(getattr(value,name)) for name,_ in value._fields_}
        assert result['total']>0 and 0<=result['used']<=result['total'] and 0<=result['free']<=result['total']
        return result
    def versions(self):
        out={}
        for name in ['nvmlSystemGetDriverVersion','nvmlSystemGetNVMLVersion']:
            value=c.create_string_buffer(128);self.check(getattr(self.dll,name)(value,128));out[name]=value.value.decode()
        return {'uuid':self.uuid,**out}
    def close(self):self.check(self.dll.nvmlShutdown())

def run(command,out,label,h,nvml,timeout=1200):
    out=Path(out);proc=None;handle=None;error=None;cleanup=None;start=h.now();clock=time.perf_counter();samples=[];terminal=None
    h.save(out/(label+'.invocation.json'),{'at':start,'command':command,'cwd':str(h.REPO),'sample_interval_ms':50,'GPU_memory_scope':'NVML global WDDM/device; sampled,not exact per-process peak','CPU_time_scope':'GetProcessTimes through confirmed exit,all threads including destructors'})
    print('Starting',label,flush=True)
    try:
        before=nvml.memory();system_before=system_memory();assert system_before['available_physical_bytes']>=32*1024**3
        with (out/(label+'.stdout.log')).open('xb') as stdout,(out/(label+'.stderr.log')).open('xb') as stderr:
            proc=subprocess.Popen(command,cwd=h.REPO,env=h.env(),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
            # Keep our own queried child handle alive through confirmed termination.
            handle=KERNEL.OpenProcess(0x1000|0x0010,False,proc.pid)
            if not handle:raise c.WinError(c.get_last_error())
            announced=0
            while proc.poll() is None:
                stamp=time.perf_counter();gpu=nvml.memory();memory=None;race=None
                try:memory=process_memory(handle)
                except OSError as exc:
                    if proc.poll() is None:raise
                    race=repr(exc)
                system=system_memory();assert system['available_physical_bytes']>=32*1024**3
                if memory:assert memory['WorkingSetSize']<=8*1024**3 and memory['PrivateUsage']<=8*1024**3
                cpu=process_times(handle)
                samples.append({'elapsed_ms':(stamp-clock)*1000,'NVML_global':gpu,'process_memory':memory,'CPU':cpu,'system_memory':system,'terminal_memory_query_race':race})
                elapsed=time.perf_counter()-clock
                if elapsed>timeout:raise TimeoutError(label)
                if elapsed-announced>=30:print(label,'running;',int(elapsed),'seconds; PID',proc.pid,flush=True);announced=elapsed
                try:proc.wait(timeout=0.05)
                except subprocess.TimeoutExpired:pass
            terminal=process_times(handle,True);after=nvml.memory()
        assert proc.returncode==0,(label,(out/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
        good=[x['process_memory'] for x in samples if x['process_memory'] is not None]
        assert good and terminal['exit_FILETIME']>=terminal['creation_FILETIME'] and terminal['lifetime_ms']>0
        gaps=[b['elapsed_ms']-a['elapsed_ms'] for a,b in zip(samples,samples[1:])]
        peak_used=max(x['NVML_global']['used'] for x in samples)
        record={'at':h.now(),'pid':proc.pid,'returncode':proc.returncode,'terminal_process_times':terminal,'parent_wall_ms':(time.perf_counter()-clock)*1000,'NVML_versions':nvml.versions(),'NVML_before':before,'NVML_after':after,'system_before':system_before,'system_after':system_memory(),'samples':samples,'sample_count':len(samples),'max_sample_gap_ms':max(gaps,default=0),'reported_working_set_high_water_bytes':max(x['PeakWorkingSetSize'] for x in good),'reported_commit_high_water_bytes':max(x['PeakPagefileUsage'] for x in good),'sampled_private_commit_max_bytes':max(x['PrivateUsage'] for x in good),'sampled_global_GPU_used_max_bytes':peak_used,'sampled_global_GPU_increment_bytes':max(0,peak_used-before['used']),'sampled_system_commit_max_increment_bytes':max(0,max(x['system_memory']['system_commit_used_bytes']for x in samples)-system_before['system_commit_used_bytes']),'scope':'Reported Windows lifetime high-water counters observed while alive; late transient after final sample can be missed. CPU/lifetime terminal FILETIME covers all process execution/cleanup. NVML memory is sampled global device accounting under WDDM,not per-process allocations or a guaranteed instantaneous peak. Resource-only measurements,never performance-qualification samples.'}
        h.save(out/(label+'.resource.json'),record)
    except BaseException as exc:error=repr(exc);cleanup=h.ar.cleanup_child(proc);raise
    finally:
        if handle:assert KERNEL.CloseHandle(handle)
        h.save(out/(label+'.exit.json'),{'started_at':start,'finished_at':h.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
    return record

if __name__=='__main__':
    ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
    H=ROOT/'runs/D157-sampler-calibration';H.mkdir(exist_ok=False)
    handle=KERNEL.GetCurrentProcess();before=process_memory(handle);cpu_before=process_times(handle)
    data=bytearray(b'\xa5')*(32*1024**2);assert data[0]==data[-1]==0xa5
    during=process_memory(handle);cpu_during=process_times(handle);del data
    assert during['PrivateUsage']>=before['PrivateUsage']+32*1024**2 and during['PeakPagefileUsage']>=during['PrivateUsage']
    assert cpu_during['kernel_100ns']+cpu_during['user_100ns']>=cpu_before['kernel_100ns']+cpu_before['user_100ns']
    n=Nvml()
    try:gpu=n.memory();versions=n.versions()
    finally:n.close()
    h.save(H/'report.json',{'at':h.now(),'status':'pass_sampler_API_self_calibration','struct_sizes':{'FILETIME':c.sizeof(FileTime),'PROCESS_MEMORY_COUNTERS_EX':c.sizeof(Memory),'nvmlMemory_t':c.sizeof(GpuMemory)},'CPU_before':cpu_before,'CPU_during':cpu_during,'memory_before':before,'memory_during32MiB_touch':during,'NVML_global_memory':gpu,'NVML_versions':versions,'application_solver_processes':0,'GPU_contexts_or_kernels_started':0,'sampler_sha256':h.sha(__file__),'scope':'Own Python process32MiB touched-allocation checks commit/high-water accounting and monotonic CPU counters. One read-only NVML identity/memory query. Not calibration of missed transient peaks,driver memory accuracy or full sample overhead.'})
    print(json.dumps({'API_calibration':'pass','NVML_versions':versions,'sizes':[c.sizeof(FileTime),c.sizeof(Memory),c.sizeof(GpuMemory)]}),flush=True)
