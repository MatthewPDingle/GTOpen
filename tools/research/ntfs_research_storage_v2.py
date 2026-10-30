"""Single directory scan with cached Win32 calls; same research storage totals."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path

STORAGE_ROOT=Path('T:/GTOpen-research')
COMPRESSED=0x800
REPARSE_POINT=0x400


def measure_tree(path,guard):
    if os.name!='nt':raise ValueError('Windows NTFS required')
    path=Path(path).resolve();root=STORAGE_ROOT.resolve()
    if path==root or not path.is_relative_to(root):
        raise ValueError('Research descendant required')
    dll=ctypes.WinDLL('kernel32',use_last_error=True)
    allocated_size=dll.GetCompressedFileSizeW
    allocated_size.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(wintypes.DWORD)]
    allocated_size.restype=wintypes.DWORD
    logical=allocated=count=compressed=0
    pending=[str(path)]
    while pending:
        guard()
        with os.scandir(pending.pop()) as entries:
            for entry in entries:
                guard()
                stat=entry.stat(follow_symlinks=False)
                if stat.st_file_attributes & REPARSE_POINT:
                    raise ValueError('Linked research artifacts are unsupported')
                if entry.is_dir(follow_symlinks=False):
                    pending.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    high=wintypes.DWORD();ctypes.set_last_error(0)
                    low=allocated_size(entry.path,ctypes.byref(high))
                    if low==0xffffffff and ctypes.get_last_error():
                        raise ctypes.WinError(ctypes.get_last_error())
                    logical+=stat.st_size;allocated+=(high.value<<32)|low;count+=1
                    compressed+=bool(stat.st_file_attributes & COMPRESSED)
    return dict(logical_bytes=logical,allocated_file_bytes=allocated,files=count,
        compressed_files=compressed,
        note='File allocation only; free-volume guard separately includes directory and filesystem overhead.')
