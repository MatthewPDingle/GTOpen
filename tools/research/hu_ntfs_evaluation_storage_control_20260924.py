"""Byte-preserving storage/native-I/O control on copied prior 64-deal evidence."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import shutil
import subprocess
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle
from ntfs_research_storage_v1 import create_compressed_directory,measure_tree,attributes,COMPRESSED

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='ntfs-evaluation-storage-control-v1'
STORE=Path('T:/GTOpen-research')/PREFIX


def read(p):return json.loads(Path(p).read_bytes())


def main():
    start=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-start<600
        if now-last>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000
            assert shutil.disk_usage('T:/').free>40_000_000_000
            last=now
    guard();assert not STORE.exists()
    rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    sr,sp=[OUT/f'exact-initial-wider-admission-v1-{s}.json' for s in ('registration','result')]
    reg,result=read(sr),read(sp)
    assert result['passed'] and result['registration_sha256']==sha(sr)
    source=Path(reg['store'])/'gpu';summary=read(source/'summary.json')
    assert sha(source/'summary.json')==result['gpu_summary_sha256']
    files={**summary['artifacts'],'summary.json':sha(source/'summary.json')}
    assert set(files)=={p.name for p in source.iterdir() if p.is_file()}
    for n,h in files.items():assert sha(source/n)==h,n
    exe=ROOT/'target/release/examples/hu_sampled_profile_allin_evaluation_v1.exe'
    context=OUT/'bb-context-candidate.json'
    inputs={str(source/n):h for n,h in files.items()}
    for p in [sr,sp,exe,context,Path(__file__),ROOT/'tools/research/ntfs_research_storage_v1.py']:
        inputs[str(p)]=sha(p)
    save(rp,dict(inputs=inputs,store=str(STORE),source=str(source),maximum_seconds=600,
        scope='Copy one prior 64-deal batch into new plain and inherited NTFS-compressed directories; verify logical hashes, JSON readers and native deterministic replay. No GPU, training, new poker samples or modification of original evidence.',
        production_modified=False,gpu_used=False))
    STORE.mkdir();plain=STORE/'plain';plain.mkdir()
    compressed=create_compressed_directory(STORE/'compressed')
    results={}
    for label,parent in [('plain',plain),('compressed',compressed)]:
        # Match the two-level directory creation used by the wider evaluator.
        folder=parent/'evaluation'/'batch-000000';folder.mkdir(parents=True)
        began=time.monotonic()
        for n,h in files.items():
            guard();destination=folder/n
            with destination.open('xb') as f:
                f.write((source/n).read_bytes());f.flush();os.fsync(f.fileno())
            assert sha(destination)==h
            assert read(destination)==read(source/n)
        write_seconds=time.monotonic()-began
        measured=measure_tree(parent,guard)
        if label=='compressed':
            assert attributes(folder)&COMPRESSED
            assert measured['compressed_files']==len(files)
        else:
            assert measured['compressed_files']==0
        replay=folder/'native-replayed.json';guard();began=time.monotonic()
        native=subprocess.run([str(exe),str(context),str(folder/'conditional-batch.json'),
            str(folder/'profiles.json'),str(replay)],cwd=ROOT,capture_output=True,text=True,
            timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
        assert native.returncode==0,native.stderr[-2000:]
        native_seconds=time.monotonic()-began;guard()
        assert sha(replay)==files['native.json']
        results[label]=dict(storage=measured,write_and_verify_seconds=write_seconds,
            native_replay_seconds=native_seconds,native_replay_sha256=sha(replay),
            logical_hashes_identical=True)
    ratio=results['compressed']['storage']['allocated_file_bytes']/results['plain']['storage']['allocated_file_bytes']
    assert ratio<.8,'Compression did not materially reduce this fixture'
    for p,h in inputs.items():assert sha(p)==h,p
    out=dict(passed=True,registration_sha256=sha(rp),results=results,
        allocated_ratio=ratio,seconds=time.monotonic()-start,gpu_used=False,production_modified=False,
        scope='Storage/I-O control only. Allocation ratio and timings from one fixture are not a guaranteed full-study bound. Future admission requires candidate-specific storage measurements plus free-volume guards.')
    save(OUT/f'{PREFIX}-result.json',out);print(json.dumps(out))


if __name__=='__main__':main()
