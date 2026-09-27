"""Research allocation scan with the established closed-port-aware activity check.

The original scan remains frozen. File/link handling and accounting are unchanged;
a verified absent production listener is idle, while an open server must pass its
API checks. Exceptions remain failures, never evidence of an idle server.
"""
import os
from pathlib import Path
import time
from bounded_parallel_evaluation_archive_v2 import production_available
from hu_root_retained_storage_admitted_study_20260924 import ROOTS, stable_file, inventory_error
from ntfs_research_storage_v1 import allocated_bytes


def measure(*, roots=None, activity=production_available):
    began = time.monotonic()
    rows = []
    last_probe = 0.
    assert activity(), 'Production is active or cannot be verified idle'
    for root in ROOTS if roots is None else roots:
        root = Path(root)
        assert root.is_dir() and not root.lstat().st_file_attributes & 0x400, str(root)
        logical = allocated = count = 0
        for folder, dirs, files in os.walk(root, followlinks=False, onerror=inventory_error):
            now = time.monotonic()
            assert now - began < 600
            if now - last_probe > 2:
                assert activity(), 'Production became active or unverified during inventory'
                last_probe = now
            for name in dirs:
                path = Path(folder) / name
                assert not path.lstat().st_file_attributes & 0x400, str(path)
            for name in files:
                path = Path(folder) / name
                try:
                    stable_file(path)
                    logical += path.stat().st_size
                    allocated += allocated_bytes(path)
                    count += 1
                except FileNotFoundError:
                    assert path.suffix == '.tmp' or path.name.startswith('.partial-')
        rows.append(dict(root=str(root), files=count, logical_bytes=logical, allocated_file_bytes=allocated))
    assert activity(), 'Production became active before inventory completion'
    return rows
