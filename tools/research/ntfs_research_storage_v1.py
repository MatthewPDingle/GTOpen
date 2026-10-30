"""Transparent NTFS compression confined to a newly created research folder.

No existing directory or file is recompressed. Logical bytes and file names
remain unchanged for native readers and registered artifact hashes.
"""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess

STORAGE_ROOT = Path('T:/GTOpen-research')
COMPRESSED = 0x800


def attributes(path):
    dll = ctypes.WinDLL('kernel32',use_last_error=True)
    call = dll.GetFileAttributesW
    call.argtypes = [wintypes.LPCWSTR];call.restype = wintypes.DWORD
    value = call(str(Path(path).resolve()))
    if value == 0xffffffff:
        raise ctypes.WinError(ctypes.get_last_error())
    return value


def allocated_bytes(path):
    dll = ctypes.WinDLL('kernel32',use_last_error=True)
    call = dll.GetCompressedFileSizeW
    call.argtypes = [wintypes.LPCWSTR,ctypes.POINTER(wintypes.DWORD)]
    call.restype = wintypes.DWORD
    high = wintypes.DWORD();ctypes.set_last_error(0)
    low = call(str(Path(path).resolve()),ctypes.byref(high))
    if low == 0xffffffff and ctypes.get_last_error():
        raise ctypes.WinError(ctypes.get_last_error())
    return (high.value << 32) | low


def create_compressed_directory(path):
    if os.name != 'nt':
        raise ValueError('This storage option requires Windows NTFS')
    path = Path(path).resolve();root = STORAGE_ROOT.resolve()
    if path == root or not path.is_relative_to(root) or path.exists():
        raise ValueError('Only a new descendant of the research storage root is allowed')
    if not path.parent.is_dir():
        raise ValueError('Existing research parent required')
    path.mkdir()
    command = Path(os.environ['SystemRoot'])/'System32/compact.exe'
    result = subprocess.run([str(command),'/C','/Q',str(path)],capture_output=True,
        text=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode or not attributes(path) & COMPRESSED:
        raise RuntimeError('Could not enable inherited NTFS compression: '+result.stdout+result.stderr)
    return path


def measure_tree(path, guard):
    path = Path(path).resolve()
    if not path.is_relative_to(STORAGE_ROOT.resolve()) or path == STORAGE_ROOT.resolve():
        raise ValueError('Research descendant required')
    logical = allocated = count = compressed = 0
    for p in path.rglob('*'):
        guard()
        if p.is_symlink():
            raise ValueError('Linked research artifacts are unsupported')
        if p.is_file():
            logical += p.stat().st_size;allocated += allocated_bytes(p);count += 1
            compressed += bool(attributes(p) & COMPRESSED)
    return dict(logical_bytes=logical,allocated_file_bytes=allocated,files=count,
                compressed_files=compressed,
                note='File allocation only; free-volume guard separately includes directory and filesystem overhead.')
