"""New compressed study directories and fast allocation scans on S: or T:."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess

ROOTS=(Path('S:/GTOpen-research'),Path('T:/GTOpen-research'))
COMPRESSED=0x800
REPARSE=0x400


def path_within_research(path):
    if os.name!='nt': raise ValueError('Windows NTFS required')
    path=Path(path)
    if not path.is_absolute() or path.resolve()!=path:
        raise ValueError('Absolute canonical path required')
    if not any(path!=root and path.is_relative_to(root) for root in ROOTS):
        raise ValueError('Named research descendant required')
    for parent in path.parents:
        if parent.exists() and parent.lstat().st_file_attributes&REPARSE:
            raise ValueError('Linked research path')
    if path.exists() and path.lstat().st_file_attributes&REPARSE:
        raise ValueError('Linked research path')
    return path


def create(path):
    path=path_within_research(path)
    if path.exists() or not path.parent.is_dir(): raise ValueError('New child of an existing research directory required')
    path.mkdir()
    command=Path(os.environ['SystemRoot'])/'System32/compact.exe'
    result=subprocess.run([str(command),'/C','/Q',str(path)],capture_output=True,text=True,
                          timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode or not path.stat().st_file_attributes&COMPRESSED:
        raise RuntimeError('Inherited NTFS compression unavailable')
    return path


def measure(path,guard=lambda:None):
    path=path_within_research(path)
    if not path.is_dir(): raise ValueError('Existing research directory required')
    dll=ctypes.WinDLL('kernel32',use_last_error=True)
    get_size=dll.GetCompressedFileSizeW
    get_size.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(wintypes.DWORD)]
    get_size.restype=wintypes.DWORD
    logical=allocated=count=compressed=0; pending=[str(path)]
    while pending:
        guard()
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                stat=entry.stat(follow_symlinks=False)
                if stat.st_file_attributes&REPARSE: raise ValueError('Linked study artifact')
                if entry.is_dir(follow_symlinks=False): pending.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    high=wintypes.DWORD();ctypes.set_last_error(0)
                    low=get_size(entry.path,ctypes.byref(high))
                    if low==0xffffffff and ctypes.get_last_error(): raise ctypes.WinError(ctypes.get_last_error())
                    logical+=stat.st_size; allocated+=(high.value<<32)|low; count+=1
                    compressed+=bool(stat.st_file_attributes&COMPRESSED)
    return dict(logical_bytes=logical,allocated_file_bytes=allocated,files=count,compressed_files=compressed,
        note='Quiescent study-directory file allocation; free-volume guards cover filesystem overhead separately.')
