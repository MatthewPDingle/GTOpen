"""Own-process CPU/host accounting and PID-filtered Windows GPU memory data."""
import ctypes as ct,time
from ctypes import wintypes as w

class FileTime(ct.Structure):_fields_=[('low',w.DWORD),('high',w.DWORD)]
class MemoryEx(ct.Structure):
    _fields_=[('cb',w.DWORD),('PageFaultCount',w.DWORD),('PeakWorkingSetSize',ct.c_size_t),('WorkingSetSize',ct.c_size_t),('QuotaPeakPagedPoolUsage',ct.c_size_t),('QuotaPagedPoolUsage',ct.c_size_t),('QuotaPeakNonPagedPoolUsage',ct.c_size_t),('QuotaNonPagedPoolUsage',ct.c_size_t),('PagefileUsage',ct.c_size_t),('PeakPagefileUsage',ct.c_size_t),('PrivateUsage',ct.c_size_t)]
class FmtUnion(ct.Union):_fields_=[('largeValue',ct.c_longlong),('doubleValue',ct.c_double),('longValue',w.LONG),('wideValue',w.LPWSTR)]
class FmtValue(ct.Structure):_fields_=[('CStatus',w.DWORD),('value',FmtUnion)]
class FmtItem(ct.Structure):_fields_=[('szName',w.LPWSTR),('FmtValue',FmtValue)]
assert ct.sizeof(ct.c_void_p)==8 and ct.sizeof(FileTime)==8 and ct.sizeof(MemoryEx)==80
assert MemoryEx.PrivateUsage.offset==72 and ct.sizeof(FmtValue)==16 and FmtValue.value.offset==8 and ct.sizeof(FmtItem)==24
_k=ct.WinDLL('kernel32',use_last_error=True)
_k.GetProcessTimes.argtypes=[w.HANDLE,*[ct.POINTER(FileTime)]*4];_k.GetProcessTimes.restype=w.BOOL
_k.K32GetProcessMemoryInfo.argtypes=[w.HANDLE,ct.POINTER(MemoryEx),w.DWORD];_k.K32GetProcessMemoryInfo.restype=w.BOOL
def process_sample(handle):
    values=[FileTime()for _ in range(4)];assert _k.GetProcessTimes(w.HANDLE(int(handle)),*[ct.byref(x)for x in values]),ct.get_last_error()
    m=MemoryEx();m.cb=80;assert _k.K32GetProcessMemoryInfo(w.HANDLE(int(handle)),ct.byref(m),80),ct.get_last_error()
    row={name:int(getattr(m,name))for name,_ in m._fields_};row['CPU_ticks100ns']=sum((x.high<<32)|x.low for x in values[2:]);row['creation_filetime']=(values[0].high<<32)|values[0].low;row['sample_perf_ns']=time.perf_counter_ns();return row
def rc(value):return int(value)&0xffffffff
class GpuMemory:
    def __init__(self,paths):
        self.dll=ct.WinDLL('pdh',use_last_error=True);p=self.dll
        p.PdhOpenQueryW.argtypes=[w.LPCWSTR,ct.c_size_t,ct.POINTER(w.HANDLE)];p.PdhOpenQueryW.restype=w.LONG
        p.PdhAddCounterW.argtypes=[w.HANDLE,w.LPCWSTR,ct.c_size_t,ct.POINTER(w.HANDLE)];p.PdhAddCounterW.restype=w.LONG
        p.PdhCollectQueryData.argtypes=[w.HANDLE];p.PdhCollectQueryData.restype=w.LONG
        p.PdhGetFormattedCounterArrayW.argtypes=[w.HANDLE,w.DWORD,ct.POINTER(w.DWORD),ct.POINTER(w.DWORD),ct.c_void_p];p.PdhGetFormattedCounterArrayW.restype=w.LONG
        p.PdhCloseQuery.argtypes=[w.HANDLE];p.PdhCloseQuery.restype=w.LONG
        self.query=w.HANDLE();assert rc(p.PdhOpenQueryW(None,0,ct.byref(self.query)))==0;self.counters={}
        try:
            for path in paths:
                handle=w.HANDLE();assert rc(p.PdhAddCounterW(self.query,path,0,ct.byref(handle)))==0,path;self.counters[path.rsplit('\\',1)[1]]=handle
            assert rc(p.PdhCollectQueryData(self.query))==0
        except BaseException:self.close();raise
    def sample(self,pid):
        status=rc(self.dll.PdhCollectQueryData(self.query));assert status==0,hex(status);result={};prefix=f'pid_{pid}_'
        for name,handle in self.counters.items():
            size=w.DWORD(0);count=w.DWORD(0);status=rc(self.dll.PdhGetFormattedCounterArrayW(handle,0x400|0x1000,ct.byref(size),ct.byref(count),None))
            assert status in[0,0x800007d2],(name,hex(status));assert size.value>0 and size.value<64*1024*1024
            allocated=size.value+65536;buf=ct.create_string_buffer(allocated);size.value=allocated;status=rc(self.dll.PdhGetFormattedCounterArrayW(handle,0x400|0x1000,ct.byref(size),ct.byref(count),buf));assert status==0,(name,hex(status));assert count.value*ct.sizeof(FmtItem)<=allocated
            items=ct.cast(buf,ct.POINTER(FmtItem));values=[]
            for i in range(count.value):
                item=items[i];instance=item.szName
                if not instance.lower().startswith(prefix):continue
                assert item.FmtValue.CStatus in[0,1],(name,instance,item.FmtValue.CStatus);value=int(item.FmtValue.value.largeValue);assert value>=0
                values.append({'instance':instance,'CStatus':int(item.FmtValue.CStatus),'bytes':value})
            result[name]={'instances':values,'sum_bytes':sum(x['bytes']for x in values)if values else None}
        return{'pid':pid,'sample_perf_ns':time.perf_counter_ns(),'counters':result}
    def close(self):
        if self.query and self.query.value:
            status=rc(self.dll.PdhCloseQuery(self.query));self.query=w.HANDLE();assert status==0,hex(status)
