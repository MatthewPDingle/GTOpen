"""Exercise transient and persistent reader locks before resuming collection."""
import ctypes
import errno
import json
import os
from pathlib import Path
import threading
import time
from ctypes import wintypes
from board_river_deal_coverage_common_v1 import ROOT,OUT,STORE,PREFIX,read,sha,verify
from board_prefix_publication_v1 import atomic_json
from research_progress_replace_v1 import progress_json


def main():
    folder=STORE/'resume-control-v1';assert not folder.exists();folder.mkdir()
    paths=[Path(__file__),ROOT/'tools/research/research_progress_replace_v1.py']
    hashes={str(p):sha(p) for p in paths};path=folder/'fixture-status.json'
    progress_json(path,dict(value='old'));before=path.read_bytes()
    def blocked(*args):raise PermissionError(13,'injected sharing denial')
    result=progress_json(path,dict(value='pending'),attempts=3,delay=0,_replace=blocked)
    assert not result['published'] and result['attempts']==3 and path.read_bytes()==before
    assert read(result['preserved'])==dict(value='pending')
    attempt=[0]
    def transient(source,dest):
        attempt[0]+=1
        if attempt[0]<3:raise PermissionError(13,'injected transient lock')
        return os.replace(source,dest)
    retry=progress_json(path,dict(value='after retry'),delay=0,_replace=transient)
    assert retry==dict(published=True,attempts=3) and read(path)==dict(value='after retry')
    def full(*args):raise OSError(errno.ENOSPC,'injected disk full')
    rejected=False
    try:progress_json(path,dict(value='never published'),_replace=full)
    except OSError as error:assert error.errno==errno.ENOSPC;rejected=True
    assert rejected and read(path)==dict(value='after retry')
    rejected=False
    try:progress_json(folder/'completion.json',dict(passed=True))
    except AssertionError:rejected=True
    assert rejected
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    create=kernel.CreateFileW;create.argtypes=(wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE);create.restype=wintypes.HANDLE
    close=kernel.CloseHandle;close.argtypes=(wintypes.HANDLE,);close.restype=wintypes.BOOL
    handle=create(str(path),0x80000000,1,None,3,0x80,None)
    assert handle!=ctypes.c_void_p(-1).value,ctypes.get_last_error()
    try:
        actual_block=progress_json(path,dict(value='real locked write'),attempts=2,delay=.01)
        assert not actual_block['published'] and read(path)==dict(value='after retry')
    finally:assert close(handle)
    handle=create(str(path),0x80000000,1,None,3,0x80,None);assert handle!=ctypes.c_void_p(-1).value
    released=threading.Event();out=[]
    def release():
        time.sleep(.12);out.append(bool(close(handle)));released.set()
    thread=threading.Thread(target=release);thread.start()
    actual_retry=progress_json(path,dict(value='real recovered write'),attempts=10,delay=.05)
    thread.join();assert released.is_set() and out==[True]
    assert actual_retry['published'] and actual_retry['attempts']>1 and read(path)==dict(value='real recovered write')
    verify(hashes);proof=dict(passed=True,inputs=hashes,persistent_lock_nonfatal=True,previous_progress_preserved=True,
        pending_progress_retained=True,temporary_lock_recovers=True,real_windows_handle_controls=True,
        disk_full_not_suppressed=True,completion_marker_rejected=True,production_modified=False)
    dest=OUT/(PREFIX+'-resume-control-v1.json');assert not dest.exists();atomic_json(dest,proof)
    print(json.dumps(proof),flush=True)


if __name__=='__main__':main()
