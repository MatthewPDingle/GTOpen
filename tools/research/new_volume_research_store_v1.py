"""Compressed allocation only for a newly created named research directory."""
import os
from pathlib import Path
import subprocess
from ntfs_research_storage_v1 import attributes,allocated_bytes,COMPRESSED

ROOTS=(Path('T:/GTOpen-research'),Path('S:/GTOpen-research'))


def checked_root(path):
    path=Path(path)
    if not path.is_absolute():raise ValueError('Absolute research path required')
    resolved=path.resolve()
    if not any(resolved.parent==root.resolve() for root in ROOTS):
        raise ValueError('Only a direct child of a declared research volume is allowed')
    for parent in (path.parent,*path.parent.parents):
        if parent.is_symlink() or parent.is_junction():raise ValueError('Linked research parent')
    if not path.parent.is_dir():raise ValueError('Existing research volume parent required')
    return resolved


def create_store(path):
    path=checked_root(path)
    if path.exists():raise ValueError('Existing evidence cannot be recompressed')
    path.mkdir()
    result=subprocess.run([str(Path(os.environ['SystemRoot'])/'System32/compact.exe'),
        '/C','/Q',str(path)],capture_output=True,text=True,timeout=30,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode or not attributes(path)&COMPRESSED:
        raise RuntimeError('New research folder compression failed: '+result.stdout+result.stderr)
    return path


def measure_store(path,guard):
    path=checked_root(path);logical=allocated=count=compressed=0
    if path.is_symlink() or path.is_junction():raise ValueError('Linked research store')
    for p in path.rglob('*'):
        guard()
        if p.is_symlink() or p.is_junction():raise ValueError('Linked research artifact')
        if p.is_file():
            logical+=p.stat().st_size;allocated+=allocated_bytes(p);count+=1
            compressed+=bool(attributes(p)&COMPRESSED)
    return dict(logical_bytes=logical,allocated_file_bytes=allocated,files=count,compressed_files=compressed)
