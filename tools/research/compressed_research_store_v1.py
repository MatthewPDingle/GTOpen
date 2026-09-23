"""Lossless NTFS storage for new research output only; never compress live inputs."""
import ctypes
from ctypes import wintypes
from pathlib import Path
import subprocess

BASE=Path('S:/GTOpen-research')
COMPRESSED=0x800


def kernel():
    dll=ctypes.WinDLL('kernel32',use_last_error=True)
    dll.GetFileAttributesW.argtypes=[wintypes.LPCWSTR]
    dll.GetFileAttributesW.restype=wintypes.DWORD
    dll.GetCompressedFileSizeW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(wintypes.DWORD)]
    dll.GetCompressedFileSizeW.restype=wintypes.DWORD
    return dll


def compressed(path):
    value=kernel().GetFileAttributesW(str(Path(path).resolve()))
    if value==0xffffffff:raise ctypes.WinError(ctypes.get_last_error())
    return bool(value&COMPRESSED)


def create_parent(path,guard):
    """Mark a new empty directory; subsequently created children inherit it."""
    guard();path=Path(path).resolve();base=BASE.resolve()
    assert path!=base and path.is_relative_to(base) and path.parent.is_dir()
    assert not path.exists() and not path.parent.is_symlink()
    path.mkdir()
    result=subprocess.run(['compact.exe','/C','/Q',str(path)],capture_output=True,text=True,
        timeout=60,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    guard()
    if result.returncode or not compressed(path):
        raise RuntimeError(f'New output directory compression failed: {result.stdout} {result.stderr}')
    return result.stdout


def inventory(path,guard):
    dll=kernel();files=[]
    for p in sorted(Path(path).rglob('*')):
        guard()
        if p.is_symlink():raise ValueError('Research storage must not contain links')
        if not p.is_file():continue
        high=wintypes.DWORD(0);ctypes.set_last_error(0)
        low=dll.GetCompressedFileSizeW(str(p.resolve()),ctypes.byref(high))
        if low==0xffffffff and ctypes.get_last_error():raise ctypes.WinError(ctypes.get_last_error())
        files.append(dict(path=str(p.relative_to(path)),logical_bytes=p.stat().st_size,
            allocated_bytes=(high.value<<32)|low,compressed=compressed(p)))
    return dict(files=files,logical_bytes=sum(x['logical_bytes'] for x in files),
        allocated_bytes=sum(x['allocated_bytes'] for x in files),
        compressed_files=sum(x['compressed'] for x in files))
