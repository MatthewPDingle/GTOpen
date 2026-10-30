"""Bounded regular-file NVMe test: aligned Windows unbuffered + write-through I/O.

No raw device access, cache flushing tools, system settings or existing files.
Every read is CRC-checked. Reports pure synchronous I/O time AND inclusive wall
time so verification overhead and gaps cannot be hidden as solver throughput.
"""
import ctypes as c
from ctypes import wintypes as w
import hashlib
import json
from pathlib import Path
import random
import shutil
import struct
import time
import zlib
import psutil
from loopback_research_validation import idle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/ssd-storage-20260920'
SCRATCH = Path('S:/GTOpen-research/ssd-storage-20260920-physical-v1')
CHUNK = 8 * 1024**2
SIZE = 16 * 1024**3
PASSES = 2


def main():
    assert not SCRATCH.exists()
    assert idle(), 'Production is active'
    for p in [ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock',
              ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock']:
        assert not p.exists(), p
    assert psutil.virtual_memory().available >= 20_000_000_000
    assert shutil.disk_usage('S:/').free >= 100_000_000_000 + SIZE
    inputs = [Path(__file__), OUT/'PROTOCOL.md', ROOT/'tools/research/loopback_research_validation.py']
    with (OUT/'physical-v1-freeze.json').open('x') as f:
        json.dump(dict(inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
                       scratch=str(SCRATCH), bytes_per_pass=SIZE, passes=PASSES,
                       chunk_bytes=CHUNK, unbuffered=True, write_through=True,
                       seed=20260920, deadline_seconds=900), f, indent=2)
    SCRATCH.mkdir(parents=True)
    path = SCRATCH/'payload.bin'
    k = c.WinDLL('kernel32', use_last_error=True)
    k.CreateFileW.argtypes = [w.LPCWSTR,w.DWORD,w.DWORD,c.c_void_p,w.DWORD,w.DWORD,w.HANDLE]
    k.CreateFileW.restype = w.HANDLE
    k.VirtualAlloc.argtypes = [c.c_void_p,c.c_size_t,w.DWORD,w.DWORD]
    k.VirtualAlloc.restype = c.c_void_p
    k.VirtualFree.argtypes = [c.c_void_p,c.c_size_t,w.DWORD]
    k.VirtualFree.restype = w.BOOL
    for name in ['WriteFile','ReadFile']:
        fn = getattr(k,name)
        fn.argtypes = [w.HANDLE,c.c_void_p,w.DWORD,c.POINTER(w.DWORD),c.c_void_p]
        fn.restype = w.BOOL
    k.SetFilePointerEx.argtypes = [w.HANDLE,c.c_longlong,c.POINTER(c.c_longlong),w.DWORD]
    k.SetFilePointerEx.restype = w.BOOL
    k.FlushFileBuffers.argtypes = [w.HANDLE]
    k.FlushFileBuffers.restype = w.BOOL
    k.CloseHandle.argtypes = [w.HANDLE]
    k.CloseHandle.restype = w.BOOL
    def checked(ok):
        if not ok: raise c.WinError(c.get_last_error())
    ptr = k.VirtualAlloc(None,CHUNK,0x3000,0x04)
    checked(ptr)
    assert ptr % 4096 == 0 and CHUNK % 4096 == 0
    handle = None
    started = time.perf_counter()
    next_guard = 0.
    result = dict(passed=False, phases=[], scratch=str(path), allocation_bytes=SIZE,
                  total_written_bytes=0, total_read_bytes=0, error=None)
    try:
        # CREATE_NEW, no sharing. FILE_FLAG_NO_BUFFERING | WRITE_THROUGH | SEQUENTIAL_SCAN.
        handle = k.CreateFileW(str(path),0xC0000000,0,None,1,0xA8000080,None)
        if handle == c.c_void_p(-1).value: raise c.WinError(c.get_last_error())
        base = random.Random(20260920).randbytes(CHUNK)
        c.memmove(ptr,base,CHUNK)
        del base
        view = memoryview((c.c_ubyte * CHUNK).from_address(ptr)).cast('B')
        def guard():
            nonlocal next_guard
            now = time.perf_counter()
            if now-started > 900: raise RuntimeError('Registered time bound reached')
            if now < next_guard: return
            assert idle(), 'Production became active; stop research only'
            assert psutil.virtual_memory().available >= 20_000_000_000
            assert shutil.disk_usage('S:/').free >= 100_000_000_000
            next_guard = now + 2
        for repeat in range(PASSES):
            expected = []
            for action in ['write','read']:
                checked(k.SetFilePointerEx(handle,0,None,0))
                phase_start = time.perf_counter()
                io_seconds = 0.
                flush_seconds = 0.
                rows = []
                for index in range(SIZE//CHUNK):
                    guard()
                    if action == 'write':
                        struct.pack_into('<QQ',view,0,repeat,index)
                        expected.append(zlib.crc32(view))
                    done = w.DWORD()
                    before = time.perf_counter()
                    checked(getattr(k,'WriteFile' if action == 'write' else 'ReadFile')(
                        handle,ptr,CHUNK,c.byref(done),None))
                    elapsed = time.perf_counter()-before
                    assert done.value == CHUNK
                    io_seconds += elapsed
                    if action == 'read':
                        assert struct.unpack_from('<QQ',view,0) == (repeat,index)
                        assert zlib.crc32(view) == expected[index], (repeat,index)
                    result['total_written_bytes' if action == 'write' else 'total_read_bytes'] += CHUNK
                    rows.append(elapsed)
                    if index % 128 == 127:
                        print(json.dumps(dict(repeat=repeat,action=action,completed_bytes=(index+1)*CHUNK,
                                              seconds=time.perf_counter()-phase_start)),flush=True)
                if action == 'write':
                    before = time.perf_counter(); checked(k.FlushFileBuffers(handle))
                    flush_seconds = time.perf_counter()-before
                wall = time.perf_counter()-phase_start
                result['phases'].append(dict(repeat=repeat,action=action,bytes=SIZE,
                    io_seconds=io_seconds,flush_seconds=flush_seconds,wall_seconds=wall,
                    io_mib_per_second=SIZE/1024**2/(io_seconds+flush_seconds),
                    inclusive_mib_per_second=SIZE/1024**2/wall,
                    chunk_io_seconds=rows))
                (OUT/'physical-v1-result.json').write_text(json.dumps(result,indent=2))
        result['passed'] = True
    except Exception as ex:
        result['error'] = repr(ex)
        raise
    finally:
        if handle is not None and handle != c.c_void_p(-1).value:
            checked(k.CloseHandle(handle))
        checked(k.VirtualFree(ptr,0,0x8000))
        result['wall_seconds'] = time.perf_counter()-started
        (OUT/'physical-v1-result.json').write_text(json.dumps(result,indent=2))
        # Retain the bounded, owned file for inspection. No broad filesystem cleanup.
        print(json.dumps({k:v for k,v in result.items() if k != 'phases'}),flush=True)


if __name__ == '__main__':
    main()
