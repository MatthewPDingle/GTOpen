"""Read-only complete storage/hardware snapshot; admits no study or profile."""
import os
import ctypes
from ctypes import wintypes
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

os.environ['PYTHONDONTWRITEBYTECODE']='1'
TOOLS=Path(r'T:\Dev\GTOpen\tools\research')
sys.path.insert(0,str(TOOLS))
import psutil
import ntfs_expected_retention_v2 as ntfs
from bounded_parallel_evaluation_archive_v2 import production_available

STAGE=Path(__file__).resolve().parent
DEST=STAGE/'preflop-five-depth-resource-preflight-v1'
ROOTS=[Path(r'S:\GTOpen-research'),Path(r'T:\GTOpen-research'),TOOLS.parents[1]/'research']

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def inventory(root):
    dll=ntfs._api();pending=[root];allocated=logical=files=directories=0
    while pending:
        directory=pending.pop();directories+=1
        with os.scandir(directory) as items:
            for item in items:
                stat=item.stat(follow_symlinks=False)
                if getattr(stat,'st_file_attributes',0)&ntfs.REPARSE:
                    raise ValueError('Reparse storage inventory entry: '+item.path)
                if item.is_dir(follow_symlinks=False):pending.append(Path(item.path));continue
                if not item.is_file(follow_symlinks=False):raise ValueError('Nonordinary storage entry')
                high=wintypes.DWORD();ctypes.set_last_error(0)
                low=dll.GetCompressedFileSizeW(ntfs._long(item.path),ctypes.byref(high))
                if low==0xffffffff and ctypes.get_last_error():raise ctypes.WinError(ctypes.get_last_error())
                allocated+=(high.value<<32)|low;logical+=stat.st_size;files+=1
    return dict(root=str(root),allocated_file_bytes=allocated,logical_file_bytes=logical,files=files,directories=directories)

def main():
    if DEST.exists():raise FileExistsError('Preserve the complete existing observation')
    DEST.mkdir();started=time.time()
    with ThreadPoolExecutor(max_workers=3) as pool:roots=list(pool.map(inventory,ROOTS))
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=name,utilization.gpu,memory.used,memory.free',
        '--format=csv,noheader,nounits'],creationflags=subprocess.CREATE_NO_WINDOW,text=True,timeout=15).strip()
    relevant=[]
    for p in psutil.process_iter(['pid','create_time','name','cmdline']):
        try:
            args=p.info['cmdline'] or []
            selected=[a for a in args if ('preflop_expected' in a.lower() or 'stack_context_' in a.lower()
                or 'native-bounded' in a.lower() or 'gto-server' in a.lower())]
            if selected:
                relevant.append(dict(pid=p.pid,creation_time=p.info['create_time'],name=p.info['name'],
                    relevant_arguments=selected))
        except (psutil.AccessDenied,psutil.NoSuchProcess):pass
    record=dict(read_only=True,observed_unix=time.time(),observation_started_unix=started,
        roots=roots,allocated_total_bytes=sum(r['allocated_file_bytes'] for r in roots),
        cap_bytes=800_000_000_000,remaining_named_allocation_bytes=800_000_000_000-sum(r['allocated_file_bytes'] for r in roots),
        available_ram_bytes=psutil.virtual_memory().available,logical_cpus=psutil.cpu_count(),
        physical_cpus=psutil.cpu_count(logical=False),gpu=gpu,
        volume_free_bytes={d:psutil.disk_usage(d+':\\').free for d in ('S','T')},
        production_available=production_available(),relevant_live_processes=relevant,
        source_sha256=sha(__file__),ntfs_helper_sha256=sha(ntfs.__file__),seconds=time.time()-started,
        accounting='Named GetCompressedFileSizeW totals only; no filesystem metadata quota, no compression-ratio credit',
        profile_prepared=False,profile_started=False,scientific_attempt=False)
    with (DEST/'result.json').open('x',encoding='utf-8',newline='\n') as f:
        json.dump(record,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
    print(json.dumps(record),flush=True)

if __name__=='__main__':main()
