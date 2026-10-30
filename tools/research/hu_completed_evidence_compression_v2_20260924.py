"""Reversible NTFS compression of one completed evaluation, with per-file hashes.

No file is deleted, moved, renamed or logically edited. Journals live outside
the registered evidence. Resume verifies every completed batch and the next
batch's pre-compression hashes before continuing.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from ntfs_research_storage_v1 import allocated_bytes, attributes, COMPRESSED
from reboot_research_idle_v1 import idle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
SOURCE = Path('T:/GTOpen-research/exact-initial-wider-study-v1/evaluation')
PREFIX = 'completed-evidence-compression-v2'


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def write(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temp, path)


def inventory(root):
    result = []
    for p in sorted(root.rglob('*')):
        if attributes(p) & 0x400:
            raise ValueError('Reparse points are not supported')
        if p.is_file():
            s = p.stat()
            result.append(dict(name=p.relative_to(root).as_posix(), size=s.st_size,
                               mtime_ns=s.st_mtime_ns))
    return result


def main(control=False):
    started = time.monotonic()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    prefix = PREFIX + ('-control' if control else '')
    journal = OUT / prefix
    source = SOURCE.resolve()
    result_path = OUT / (prefix + '-result.json')
    reg_path = OUT / (prefix + '-registration.json')
    dependencies = {str(Path(__file__).resolve()): digest(__file__),
                    str(ROOT/'tools/research/ntfs_research_storage_v1.py'):
                    digest(ROOT/'tools/research/ntfs_research_storage_v1.py')}
    if control:
        source = Path('T:/GTOpen-research') / prefix
        if not reg_path.exists():
            source.mkdir()
            sample = SOURCE/'train-040320/profiles.json'
            shutil.copyfile(sample, source/'profiles.json')
    else:
        gate = OUT/'exact-initial-wider-study-v1-result.json'
        gate_reg = OUT/'exact-initial-wider-study-v1-registration.json'
        complete = read(gate)
        assert complete['passed'] and complete['registration_sha256'] == digest(gate_reg)
        dependencies.update({str(gate): digest(gate), str(gate_reg): digest(gate_reg)})
        check = OUT/(PREFIX+'-control-result.json')
        assert read(check)['passed']
        assert read(check)['source_sha256'] == digest(__file__)
        dependencies[str(check)] = digest(check)
    source = source.resolve()
    assert source.is_dir()
    if control:
        assert source.parent == Path('T:/GTOpen-research').resolve()
    else:
        assert source == SOURCE.resolve()

    def guard():
        assert time.monotonic()-started < 4*3600
        assert shutil.disk_usage('T:/').free > 40_000_000_000
        assert idle(), 'Production became active; compression can resume later'

    guard()
    files = inventory(source)
    assert sum(f['size'] for f in files) < 80_000_000_000
    if not reg_path.exists():
        journal.mkdir()
        write(reg_path, dict(source=str(source), files=files, dependencies=dependencies,
            batch_size=48, byte_preserving=True, deletes_allowed=False,
            production_modified=False, free_reserve_bytes=40_000_000_000))
    reg = read(reg_path)
    assert reg['source'] == str(source) and reg['files'] == files
    assert reg['dependencies'] == dependencies
    before_total = after_total = verified = 0
    for start in range(0,len(files),48):
        guard()
        batch = files[start:start+48]
        before_path = journal/f'{start:06d}-before.json'
        after_path = journal/f'{start:06d}-after.json'
        if not before_path.exists():
            before = {f['name']: dict(sha256=digest(source/f['name']),
                allocated=allocated_bytes(source/f['name'])) for f in batch}
            write(before_path, before)
        before = read(before_path)
        assert set(before) == {f['name'] for f in batch}
        for f in batch:
            assert digest(source/f['name']) == before[f['name']]['sha256']
        if not after_path.exists():
            command = Path(os.environ['SystemRoot'])/'System32/compact.exe'
            call = subprocess.run([str(command),'/C','/Q',*[str(source/f['name']) for f in batch]],
                capture_output=True, text=True, timeout=180, creationflags=subprocess.CREATE_NO_WINDOW)
            assert call.returncode == 0, call.stdout+call.stderr
            after = {}
            for f in batch:
                p=source/f['name']
                assert digest(p) == before[f['name']]['sha256']
                assert p.stat().st_size == f['size'] and p.stat().st_mtime_ns == f['mtime_ns']
                assert attributes(p)&COMPRESSED
                after[f['name']] = dict(sha256=before[f['name']]['sha256'], allocated=allocated_bytes(p))
            write(after_path, after)
        after=read(after_path)
        for f in batch:
            p=source/f['name']
            assert after[f['name']]['sha256'] == before[f['name']]['sha256']
            assert allocated_bytes(p) == after[f['name']]['allocated'] and attributes(p)&COMPRESSED
        before_total += sum(v['allocated'] for v in before.values())
        after_total += sum(v['allocated'] for v in after.values())
        verified += len(batch)
        status=dict(state='running',files_verified=verified,total_files=len(files),
            allocated_before=before_total,allocated_after=after_total,
            saved_bytes=before_total-after_total,seconds=time.monotonic()-started,
            controller_pid=os.getpid(),source=str(source),production_modified=False)
        write(OUT/(prefix+'-status.json'),status)
        if start % 480 == 0: print(json.dumps(status),flush=True)
        time.sleep(.1)
    assert inventory(source) == files
    for path,h in dependencies.items(): assert digest(path)==h
    status.update(state='complete',passed=True,registration_sha256=digest(reg_path),
        source_sha256=digest(__file__),seconds=time.monotonic()-started,
        logical_bytes=sum(f['size'] for f in files),deleted_files=0)
    write(result_path,status);write(OUT/(prefix+'-status.json'),status)
    print(json.dumps(status),flush=True)


if __name__ == '__main__':
    assert sys.argv[1:] in (['--control'],['--run'])
    main(control=sys.argv[1:] == ['--control'])
