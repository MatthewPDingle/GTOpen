"""Reversible NTFS compression of two completed evaluation stores.

Original paths, decoded file bytes, sizes and last-write times must be retained.
No deletion, archival relocation, compression of the active store, or production
changes. The Windows compressor runs below normal priority without a window.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha, save
from reboot_research_idle_v1 import idle

PREFIX='completed-evidence-ntfs-compression-v1'
NAMES=('sampled-physical-hybrid-allin-evaluation-v1', 'sampled-visible-hybrid-completion-evaluation-v1')


def snapshot(folder):
    result={}
    for p in sorted(folder.rglob('*')):
        if p.is_dir(): continue
        if p.is_symlink(): raise ValueError('Do not follow evidence symlinks')
        s=p.stat()
        with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
        result[str(p.relative_to(folder))]=dict(bytes=s.st_size,mtime_ns=s.st_mtime_ns,sha256=digest)
    return result


def main():
    started=time.monotonic(); assert idle()
    rp=OUT/f'{PREFIX}-registration.json'; assert not rp.exists()
    inputs={str(Path(__file__)):sha(Path(__file__))}; folders=[]
    for name in NAMES:
        rpath,ppath,apath=[OUT/f'{name}-{k}.json' for k in ('registration','result','independent-review')]
        r,p,a=map(read,(rpath,ppath,apath))
        assert p['terminal'] and a['passed'] and a['result_sha256']==sha(ppath) and a['registration_sha256']==sha(rpath)
        folder=Path(r['store']).resolve()
        assert folder==Path('S:/GTOpen-research',name).resolve() and folder.is_dir()
        folders.append(folder); inputs.update({str(x):sha(x) for x in (rpath,ppath,apath)})
    volume=subprocess.check_output(['powershell','-NoProfile','-Command',"(Get-Volume -DriveLetter S).FileSystem"],text=True,creationflags=subprocess.CREATE_NO_WINDOW).strip()
    assert volume=='NTFS'
    save(rp,dict(inputs=inputs,folders=[str(p) for p in folders],operation='Native lossless NTFS compression only; original decoded bytes and last-write times verified for every file.',
        maximum_seconds=900,production_modified=False,active_study_modified=False,no_deletion=True))
    completed=[]; error=None
    try:
        for index,folder in enumerate(folders):
            assert idle() and time.monotonic()-started<900
            before=snapshot(folder)
            manifest=OUT/f'{PREFIX}-{index}-manifest.json';save(manifest,before)
            free_before=shutil.disk_usage(folder).free
            log=OUT/f'{PREFIX}-{index}.log'
            with log.open('x') as stream:
                done=subprocess.run(['compact.exe','/C',f'/S:{folder}','/Q'],stdout=stream,stderr=subprocess.STDOUT,
                    timeout=600,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            assert done.returncode==0, f'Compression returned {done.returncode}; retain log and partially compressed files'
            after=snapshot(folder)
            assert after==before, 'File content, size, path set or last-write time changed'
            free_after=shutil.disk_usage(folder).free
            record=dict(folder=str(folder),files_verified=len(before),logical_bytes=sum(v['bytes'] for v in before.values()),
                manifest=str(manifest),manifest_sha256=sha(manifest),all_file_bytes_sizes_mtimes_unchanged=True,
                drive_free_before=free_before,drive_free_after=free_after,
                free_change_caveat='Drive-wide free-space change includes concurrent training writes.',log_sha256=sha(log))
            completed.append(record);print(json.dumps(record),flush=True)
        for p,h in inputs.items():assert sha(p)==h,p
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(rp),folders=completed,
            seconds=time.monotonic()-started,production_modified=False,active_study_modified=False,no_deletion=True,
            reverse='NTFS uncompression with compact /U on these exact completed folders, provided enough disk space is available.'))
    except Exception as exc:
        error=repr(exc);raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='complete' if error is None else 'stopped',error=error,completed=completed,seconds=time.monotonic()-started))


if __name__=='__main__':main()
