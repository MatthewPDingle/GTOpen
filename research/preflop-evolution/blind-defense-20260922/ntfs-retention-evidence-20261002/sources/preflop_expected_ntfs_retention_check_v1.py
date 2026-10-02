"""One-shot byte-identical NTFS control on the entire audited native profile.

No new poker deals, native poker calculation, fitting, historical compression,
linking or deletion. New copied artifacts and failures are retained.
"""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
import traceback
from unittest.mock import patch

sys.dont_write_bytecode=True
STAGE=Path(__file__).resolve().parent
TOOLS=Path(r'T:\Dev\GTOpen\tools\research')
sys.path.append(str(TOOLS))
import psutil
import ntfs_expected_retention_v1 as ntfs
import preflop_expected_native_execution_v1 as execution
from bounded_parallel_evaluation_archive_v2 import production_available

STORE=Path(r'S:\GTOpen-research\ntfs-expected-profile-control-v1')
PROFILE=Path(r'S:\GTOpen-research\preflop-expected-native-cycle-profile-v1')
MANIFEST=STAGE/'preflop-expected-native-cycle-independent-readback-v2/retained-files.json'
RESULT=STAGE/'preflop-expected-ntfs-retention-control-v1-result.json'
def sha(path):return execution.sha(path)
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n')
        stream.flush();os.fsync(stream.fileno())
def main():
    began=time.monotonic();psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    def guard():
        if time.monotonic()-began>600:raise TimeoutError('NTFS software control deadline')
        if psutil.virtual_memory().available<20_000_000_000:raise RuntimeError('RAM reserve')
        if psutil.disk_usage('S:/').free<40_000_000_000:raise RuntimeError('Disk reserve')
    guard();assert production_available()
    assert not STORE.exists() and not RESULT.exists()
    manifest=json.loads(MANIFEST.read_bytes())
    assert len(manifest)==809
    assert set(manifest)=={str(p.relative_to(PROFILE)) for p in PROFILE.rglob('*') if p.is_file()}
    pinned={str(p):sha(p) for p in (Path(__file__).resolve(),Path(ntfs.__file__).resolve(),
            Path(execution.__file__).resolve(),MANIFEST,PROFILE/'registration.json',PROFILE/'result.json')}
    store=ntfs.create_new_store(STORE)
    save(store/'attempt.json',dict(scope='Software-only transparent-retention control; original artifacts unchanged',
        inputs=pinned,source=str(PROFILE),files=len(manifest),started_unix=time.time(),maximum_seconds=600,copy_workers=8))
    try:
        copyroot=store/'profile-copy'
        # Precreate nested directories in the same parent-before-child pattern
        # as worker artifacts. Existing files are never opened for writing.
        for parent in sorted({copyroot/Path(name).parent for name in manifest},key=lambda p:len(p.parts)):
            parent.mkdir(parents=True,exist_ok=True)
            assert ntfs.attributes(parent)&ntfs.COMPRESSED
        def copy_one(item):
            name,entry=item;guard();source=PROFILE/name;target=copyroot/name
            before=source.stat();assert before.st_size==entry['bytes'] and sha(source)==entry['sha256']
            at=time.monotonic();content=source.read_bytes()
            with target.open('xb') as stream:stream.write(content);stream.flush();os.fsync(stream.fileno())
            assert target.stat().st_size==entry['bytes'] and sha(target)==entry['sha256']
            after=source.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
            assert sha(source)==entry['sha256']
            assert ntfs.attributes(target)&ntfs.COMPRESSED
            return dict(path=name,bytes=entry['bytes'],sha256=entry['sha256'],original_unchanged=True,
                        original_compressed=bool(ntfs.attributes(source)&ntfs.COMPRESSED),
                        original_named_allocated_bytes=ntfs.allocated_bytes(source),
                        copied_named_allocated_bytes=ntfs.allocated_bytes(target),seconds=time.monotonic()-at)
        at=time.monotonic()
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:copied=list(pool.map(copy_one,manifest.items()))
        copy_seconds=time.monotonic()-at
        measured=ntfs.measure_tree(copyroot,guard)
        assert measured['files']==len(manifest) and measured['compressed_files']==len(manifest)
        assert measured['logical_bytes']==sum(row['bytes'] for row in copied)
        assert measured['named_allocated_file_bytes']==sum(row['copied_named_allocated_bytes'] for row in copied)
        # Actual independently launched Python uses inherited compression with
        # native-style stdout and separate output files. This is not poker work.
        fixtures=store/'fixture'/'nested';fixtures.mkdir(parents=True)
        script=fixtures/'writer.py'
        script.write_text('import os,sys\nfrom pathlib import Path\np=Path(sys.argv[1])\n'
            'raw=b"abcdef0123456789"*524288\n'
            'with p.open("xb") as f:f.write(raw);f.flush();os.fsync(f.fileno())\n'
            'sys.stdout.buffer.write(raw)\n',encoding='utf-8')
        target=fixtures/'direct-output.bin'
        native=execution.run_native(sys.executable,['-B',str(script),str(target)],folder=fixtures,label='python-writer',
            expected_identities={str(Path(sys.executable).resolve()):sha(sys.executable),str(script.resolve()):sha(script)},
            guard=guard,timeout=30,max_output_bytes=10_000_000)
        assert sha(native['stdout_path'])==sha(target)
        assert all(ntfs.attributes(p)&ntfs.COMPRESSED for p in (target,Path(native['stdout_path'])))
        # Reopening, seeking, appending and renaming preserve logical data.
        boundary=fixtures/'random-access.bin';raw=bytearray(random.Random(3181).randbytes(2_000_000))
        with boundary.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        patchbytes=b'qualified-random-access';raw[77777:77777+len(patchbytes)]=patchbytes;raw.extend(b'append-tail')
        with boundary.open('r+b') as stream:
            stream.seek(77777);stream.write(patchbytes);stream.seek(0,2);stream.write(b'append-tail');stream.flush();os.fsync(stream.fileno())
        renamed=fixtures/'renamed.bin';boundary.rename(renamed)
        assert renamed.read_bytes()==raw and ntfs.attributes(renamed)&ntfs.COMPRESSED
        refused=[]
        for label,path in [('existing',store),('root',store.parent),('outside',STAGE/'outside-ntfs-control'),('nested-existing-parent',fixtures/'new-store')]:
            try:ntfs.create_new_store(path)
            except ValueError:refused.append(label)
            else:raise AssertionError('Unsafe compression path accepted: '+label)
        with patch.object(ntfs,'attributes',return_value=ntfs.REPARSE):
            try:ntfs.measure_tree(copyroot,guard)
            except ValueError:refused.append('reparse-point')
            else:raise AssertionError('Reparse root accepted')
        # No hardlink savings are counted. Probe only two newly owned files.
        linked=fixtures/'hardlink.bin';os.link(renamed,linked)
        try:ntfs.measure_tree(fixtures,guard)
        except ValueError:refused.append('hardlink-accounting')
        else:raise AssertionError('Hardlinked accounting accepted')
        # Preserve the refusal fixture; do not remove/rewrite it for a pass.
        for p,h in pinned.items():assert sha(p)==h,p
        save(store/'copied-manifest.json',copied)
        original=sum(row['original_named_allocated_bytes'] for row in copied)
        result=dict(passed=True,scope='Complete 809-file retained profile copy and synthetic Python I/O; no poker accuracy/training claim',
            inputs=pinned,store=str(store),files=len(copied),original_named_allocated_bytes=original,
            copied_storage=measured,original_compressed_files=sum(row['original_compressed'] for row in copied),
            compressed_over_original=measured['named_allocated_file_bytes']/original,copy_seconds=copy_seconds,
            logical_hashes_exact=True,all_originals_unchanged=True,nested_inheritance=True,
            actual_python_stdout_and_direct_output=True,seek_append_rename_exact=True,refused=refused,
            copied_manifest_sha256=sha(store/'copied-manifest.json'),native_fixture=native,
            seconds=time.monotonic()-began,scientific_accuracy_qualified=False,production_modified=False,
            note='Candidate-specific retention measurement; no guaranteed bound for deeper stacks, no historical compression, no filesystem quota')
        assert result['compressed_over_original']<.8
        save(RESULT,result);save(store/'result.json',result)
        print(json.dumps({k:result[k] for k in ('passed','files','original_named_allocated_bytes','copied_storage','compressed_over_original','copy_seconds','seconds')}),flush=True)
    except BaseException as exc:
        save(store/'failure.json',dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc()))
        raise
if __name__=='__main__':main()
