"""Known explicit own-process commitment; no CUDA driver loaded."""
import ctypes as ct,json,os,sys
from ctypes import wintypes as w
k=ct.WinDLL('kernel32',use_last_error=True)
k.GetModuleHandleW.argtypes=[w.LPCWSTR];k.GetModuleHandleW.restype=w.HMODULE
k.VirtualAlloc.argtypes=[w.LPVOID,ct.c_size_t,w.DWORD,w.DWORD];k.VirtualAlloc.restype=w.LPVOID
k.VirtualFree.argtypes=[w.LPVOID,ct.c_size_t,w.DWORD];k.VirtualFree.restype=w.BOOL
assert not k.GetModuleHandleW('nvcuda.dll')and not k.GetModuleHandleW('nvrtc64_120_0.dll')
def hold(stage,bytes):
    print('E080_CPU_COMMIT '+json.dumps({'stage':stage,'PID':os.getpid(),'committed_touched_owned_bytes':bytes,'CUDA_loaded':bool(k.GetModuleHandleW('nvcuda.dll'))}),flush=True)
    assert sys.stdin.readline().strip()=='continue'
hold('baseline',0);ptr=None
try:
    for name,mb in[('alloc128',128),('alloc256',256),('alloc128_repeat',128)]:
        n=mb*1024*1024;ptr=k.VirtualAlloc(None,n,0x3000,0x04);assert ptr,ct.get_last_error();ct.memset(ptr,0x6d,n);assert ct.c_ubyte.from_address(ptr).value==0x6d and ct.c_ubyte.from_address(ptr+n-1).value==0x6d
        hold(name,n);assert k.VirtualFree(ptr,0,0x8000),ct.get_last_error();ptr=None;hold(name+'_free',0)
finally:
    if ptr:assert k.VirtualFree(ptr,0,0x8000)
assert not k.GetModuleHandleW('nvcuda.dll')
print('E080_CPU_COMMIT '+json.dumps({'stage':'complete','states':7,'VirtualAlloc_calls':3,'VirtualFree_calls':3,'CUDA_loaded':False}),flush=True)
