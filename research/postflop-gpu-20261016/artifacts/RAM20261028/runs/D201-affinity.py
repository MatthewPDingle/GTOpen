"""Child-local inherited Windows process affinity; no service/global settings."""
import ctypes as c,subprocess
k=c.WinDLL('kernel32',use_last_error=True)
k.GetCurrentProcess.restype=c.c_void_p
k.GetProcessAffinityMask.argtypes=[c.c_void_p,c.POINTER(c.c_size_t),c.POINTER(c.c_size_t)];k.GetProcessAffinityMask.restype=c.c_int
k.SetProcessAffinityMask.argtypes=[c.c_void_p,c.c_size_t];k.SetProcessAffinityMask.restype=c.c_int
assert c.sizeof(c.c_void_p)==8
def query(handle=None):
 process,system=c.c_size_t(),c.c_size_t()
 if not k.GetProcessAffinityMask(k.GetCurrentProcess() if handle is None else handle,c.byref(process),c.byref(system)):raise c.WinError(c.get_last_error())
 assert process.value and system.value and process.value&~system.value==0
 return {'process_mask':process.value,'system_mask':system.value}
def set_current(mask):
 assert isinstance(mask,int) and mask>0
 if not k.SetProcessAffinityMask(k.GetCurrentProcess(),mask):raise c.WinError(c.get_last_error())
 assert query()['process_mask']==mask
def spawn(mask,witnesses,*args,**kwargs):
 original=query();assert original['process_mask']==original['system_mask']==0xffffffff and mask&~original['process_mask']==0
 proc=None;selected=None
 try:
  set_current(mask);selected=query();proc=subprocess.Popen(*args,**kwargs)
 finally:
  set_current(original['process_mask']);restored=query();assert restored==original
 try:
  child=query(int(proc._handle));assert child['process_mask']==mask and child['system_mask']==original['system_mask']
  witnesses.append({'pid':proc.pid,'original_parent':original,'selected_parent_before_spawn':selected,'restored_parent_after_spawn':restored,'actual_child_at_spawn':child,'child_inherits_mask_before_native_start':True})
 except BaseException:
  if proc is not None and proc.poll() is None:proc.kill();proc.wait(timeout=15)
  raise
 return proc
