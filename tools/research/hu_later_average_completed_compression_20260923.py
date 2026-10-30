"""Compress only the completed, audited fresh training store, preserving bytes."""
from pathlib import Path
import os
import shutil
import subprocess
import time
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from hu_completed_evidence_ntfs_compression_20260923 import snapshot
from compressed_research_store_v1 import inventory
from reboot_research_idle_v1 import idle

PREFIX='later-average-completed-compression-v1'
LOCK=ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER=ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def main():
    start=time.monotonic()
    def guard():assert idle() and time.monotonic()-start<900
    guard();assert not LOCK.exists() and not OTHER.exists()
    paths=[OUT/f'later-average-study-v1-{s}.json' for s in ('registration','result','status')]
    sr,sp,ss=map(read,paths)
    assert ss['state']=='complete' and sp['passed'] and sp['screening_passed'] and sp['registration_sha256']==sha(paths[0])
    trp,tpp,tap=[OUT/f'later-average-fresh-pilot-v1-{s}.json' for s in ('registration','result','independent-review')]
    tr,tp,ta=map(read,(trp,tpp,tap))
    assert tp['terminal'] and ta['passed'] and ta['terminal_complete'] and ta['completed_iterations']==78
    assert ta['source_registration_sha256']==sha(trp) and ta['evidence_hashes'][str(tpp)]==sha(tpp)
    folder=Path(tr['store']).resolve();assert folder==Path('S:/GTOpen-research/later-average-fresh-pilot-v1').resolve()
    inputs={**tr['inputs'],**ta['evidence_hashes']}
    inputs.update({str(p):sha(p) for p in [*paths,trp,tpp,tap,Path(__file__),
        ROOT/'tools/research/hu_completed_evidence_ntfs_compression_20260923.py',ROOT/'tools/research/compressed_research_store_v1.py']})
    for p,h in inputs.items():assert sha(p)==h,p
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,folder=str(folder),maximum_seconds=900,production_modified=False,
        operation='Reversible native NTFS compression of completed audited training only; every decoded file hash, size and last-write time must be unchanged. No deletes, moves or active processes.'))
    acquired=False;error=None
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;guard();before=snapshot(folder)
        manifest=OUT/f'{PREFIX}-manifest.json';save(manifest,before)
        free_before=shutil.disk_usage(folder).free
        with (OUT/f'{PREFIX}-compact.log').open('x') as stream:
            p=subprocess.run(['compact.exe','/C',f'/S:{folder}','/Q'],stdout=stream,stderr=subprocess.STDOUT,
                timeout=600,creationflags=subprocess.CREATE_NO_WINDOW|subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        assert p.returncode==0;guard();after=snapshot(folder);assert before==after
        stats=inventory(folder,lambda:None);guard()
        for p,h in inputs.items():assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),files_verified=len(before),
            logical_bytes=stats['logical_bytes'],allocated_bytes=stats['allocated_bytes'],
            drive_free_before=free_before,drive_free_after=shutil.disk_usage(folder).free,
            all_decoded_bytes_sizes_paths_mtimes_unchanged=True,manifest_sha256=sha(manifest),
            seconds=time.monotonic()-start,production_modified=False)
        save(OUT/f'{PREFIX}-result.json',result);print(result,flush=True)
    except BaseException as exc:error=repr(exc);raise
    finally:
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,seconds=time.monotonic()-start))
        if acquired:
            assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()


if __name__=='__main__':main()
