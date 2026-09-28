"""Read-only NTFS inventory with one bound API and directory-entry stat reuse.

The storage/activity/reparse contract is unchanged. Resolve approved roots once;
the walk checks every directory and file before using its absolute path. No
historical data is compressed, deleted or modified by this module.
"""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import time
from bounded_parallel_evaluation_archive_v2 import production_available
from hu_root_retained_storage_admitted_study_20260924 import ROOTS,stable_file

REPARSE=0x400
WOF=0x80000017

def measure(*,roots=None,activity=production_available):
    assert os.name=='nt','Windows NTFS required'
    began=time.monotonic();last_probe=0.;rows=[]
    assert activity(),'Production is active or cannot be verified idle'
    dll=ctypes.WinDLL('kernel32',use_last_error=True)
    get_size=dll.GetCompressedFileSizeW
    get_size.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(wintypes.DWORD)]
    get_size.restype=wintypes.DWORD
    def allocated(path):
        high=wintypes.DWORD();ctypes.set_last_error(0)
        low=get_size(path,ctypes.byref(high))
        if low==0xffffffff and ctypes.get_last_error():raise ctypes.WinError(ctypes.get_last_error())
        return (high.value<<32)|low
    def guard():
        nonlocal last_probe
        now=time.monotonic();assert now-began<600,'Inventory time limit'
        if now-last_probe>2:
            assert activity(),'Production became active or unverified during inventory'
            last_probe=now
    for supplied in ROOTS if roots is None else roots:
        root=Path(supplied)
        # A canonical absolute starting path makes per-file resolve redundant.
        assert root.is_absolute() and root.resolve()==root,str(root)
        assert root.is_dir() and not root.lstat().st_file_attributes&REPARSE,str(root)
        for parent in root.parents:
            assert not parent.lstat().st_file_attributes&REPARSE,str(parent)
        logical=used=count=0;pending=[str(root)]
        while pending:
            guard();folder=pending.pop()
            # Re-check a directory immediately before walking it.
            assert not Path(folder).lstat().st_file_attributes&REPARSE,folder
            with os.scandir(folder) as entries:
                for entry in entries:
                    guard()
                    if entry.is_dir(follow_symlinks=False):
                        st=entry.stat(follow_symlinks=False)
                        assert not st.st_file_attributes&REPARSE,entry.path
                        pending.append(entry.path)
                        continue
                    try:
                        st=entry.stat(follow_symlinks=False)
                        if st.st_file_attributes&REPARSE:
                            if st.st_reparse_tag!=WOF:
                                stable_file(Path(entry.path))
                                st=Path(entry.path).lstat()
                            assert not st.st_file_attributes&REPARSE or st.st_reparse_tag==WOF,entry.path
                        # A directory-link can report non-directory without following;
                        # it has already been rejected by the non-WOF reparse check.
                        assert not entry.is_dir(follow_symlinks=False),entry.path
                        logical+=st.st_size;used+=allocated(entry.path);count+=1
                    except FileNotFoundError:
                        path=Path(entry.path)
                        assert path.suffix=='.tmp' or path.name.startswith('.partial-'),entry.path
        rows.append(dict(root=str(root),files=count,logical_bytes=logical,allocated_file_bytes=used))
    assert activity(),'Production became active before inventory completion'
    return rows
