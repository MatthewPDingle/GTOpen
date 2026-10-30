"""Transparent compression and named-file accounting for NEW research stores.

Existing sources/evidence are never compressed, relinked or removed. Ordinary
reads and file hashes see unchanged logical bytes. This is no filesystem quota.
"""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess

ROOTS=(Path(r'S:\GTOpen-research'),Path(r'T:\GTOpen-research'))
COMPRESSED=0x800
REPARSE=0x400

def _api():
    if os.name!='nt':raise ValueError('Windows NTFS required')
    dll=ctypes.WinDLL('kernel32',use_last_error=True)
    dll.GetFileAttributesW.argtypes=[wintypes.LPCWSTR]
    dll.GetFileAttributesW.restype=wintypes.DWORD
    dll.GetCompressedFileSizeW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(wintypes.DWORD)]
    dll.GetCompressedFileSizeW.restype=wintypes.DWORD
    return dll

def _long(path):return '\\\\?\\'+str(Path(path).absolute())

def attributes(path):
    value=_api().GetFileAttributesW(_long(path))
    if value==0xffffffff:raise ctypes.WinError(ctypes.get_last_error())
    return value

def allocated_bytes(path):
    dll=_api();high=wintypes.DWORD();ctypes.set_last_error(0)
    low=dll.GetCompressedFileSizeW(_long(path),ctypes.byref(high))
    if low==0xffffffff and ctypes.get_last_error():raise ctypes.WinError(ctypes.get_last_error())
    return (high.value<<32)|low

class FileInformation(ctypes.Structure):
    _fields_=[('attributes',wintypes.DWORD),('created',wintypes.FILETIME),
        ('accessed',wintypes.FILETIME),('written',wintypes.FILETIME),
        ('volume',wintypes.DWORD),('size_high',wintypes.DWORD),('size_low',wintypes.DWORD),
        ('links',wintypes.DWORD),('index_high',wintypes.DWORD),('index_low',wintypes.DWORD)]

def file_identity(path):
    """Python 3.12 stat.nlink can report 1 for Windows hardlinks; query handle."""
    dll=_api()
    dll.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,
                              wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    dll.CreateFileW.restype=wintypes.HANDLE
    dll.GetFileInformationByHandle.argtypes=[wintypes.HANDLE,ctypes.POINTER(FileInformation)]
    dll.GetFileInformationByHandle.restype=wintypes.BOOL
    dll.CloseHandle.argtypes=[wintypes.HANDLE];dll.CloseHandle.restype=wintypes.BOOL
    handle=dll.CreateFileW(_long(path),0,7,None,3,0x02000000,None)
    if handle==wintypes.HANDLE(-1).value:raise ctypes.WinError(ctypes.get_last_error())
    try:
        info=FileInformation()
        if not dll.GetFileInformationByHandle(handle,ctypes.byref(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        return dict(volume=info.volume,index=(info.index_high<<32)|info.index_low,links=info.links,
                    attributes=info.attributes,logical_bytes=(info.size_high<<32)|info.size_low)
    finally:
        if not dll.CloseHandle(handle):raise ctypes.WinError(ctypes.get_last_error())

def _rooted(path):
    lexical=Path(os.path.abspath(path)); resolved=lexical.resolve()
    root=next((r for r in ROOTS if lexical!=r and lexical.is_relative_to(r)),None)
    if root is None or lexical!=resolved:raise ValueError('Canonical research descendant required')
    for p in [lexical,*lexical.parents]:
        if p.exists() and attributes(p)&REPARSE:raise ValueError('Reparse-point artifacts are unsupported')
        if p==Path(root.anchor):break
    return lexical,root

def create_new_store(path):
    path,root=_rooted(path)
    if path.parent!=root or path.exists() or not root.is_dir():
        raise ValueError('Only a new immediate research-root descendant may be compressed')
    path.mkdir(exist_ok=False)
    command=Path(os.environ['SystemRoot'])/'System32/compact.exe'
    result=subprocess.run([str(command),'/C','/Q',str(path)],capture_output=True,text=True,
                          timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode or not attributes(path)&COMPRESSED:
        raise RuntimeError('Inherited compression was not enabled: '+result.stdout+result.stderr)
    return path

def measure_tree(path,guard):
    path,_=_rooted(path)
    if not path.is_dir():raise ValueError('Existing owned store required')
    dll=_api();pending=[path];logical=allocated=count=compressed=0
    while pending:
        guard()
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                guard();stat=entry.stat(follow_symlinks=False)
                if stat.st_file_attributes&REPARSE:
                    raise ValueError('Reparse-point files receive no storage credit')
                if entry.is_dir(follow_symlinks=False):pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False):
                    info=file_identity(entry.path)
                    if info['links']!=1 or info['attributes']&REPARSE or info['logical_bytes']!=stat.st_size:
                        raise ValueError('Hardlinked or concurrently changed files receive no storage credit')
                    high=wintypes.DWORD();ctypes.set_last_error(0)
                    low=dll.GetCompressedFileSizeW(_long(entry.path),ctypes.byref(high))
                    if low==0xffffffff and ctypes.get_last_error():raise ctypes.WinError(ctypes.get_last_error())
                    logical+=stat.st_size;allocated+=(high.value<<32)|low;count+=1
                    compressed+=bool(stat.st_file_attributes&COMPRESSED)
    return dict(logical_bytes=logical,named_allocated_file_bytes=allocated,files=count,compressed_files=compressed,
                accounting='GetCompressedFileSizeW summed per name; hardlinks/reparse points refused; volume free-space guard must separately include metadata and transient allocation')
