"""Archive already-passed native qualification artifacts without deleting them."""
import hashlib
import json
from pathlib import Path
import time
import zipfile
import psutil

ROOT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME = 'stack-context-teacher-native-plan-check-v1'
store = ROOT/NAME
result_path = ROOT/(NAME+'-result.json')
reader_path = ROOT/'stack-context-teacher-native-plan-readback-v1-result.json'
archive = ROOT/(NAME+'-artifacts.zip')
receipt = ROOT/(NAME+'-archive.json')


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    if archive.exists() or receipt.exists():raise ValueError('Preserve existing archive attempt')
    r = json.loads(result_path.read_bytes());reader = json.loads(reader_path.read_bytes())
    assert r['complete'] and r['passed'] and reader['complete'] and reader['passed']
    assert reader['result_sha256'] == sha(result_path)
    members = {Path(p).relative_to(store).as_posix():h for p, h in r['artifacts'].items()}
    assert len(members) == 448
    for p, h in r['artifacts'].items():assert sha(p) == h
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name in sorted(members):z.write(store/name, name)
    with zipfile.ZipFile(archive, 'r') as z:
        assert set(z.namelist()) == set(members) and len(z.namelist()) == len(members)
        for name, h in members.items():assert hashlib.sha256(z.read(name)).hexdigest() == h
    for p, h in r['artifacts'].items():assert sha(p) == h
    doc = dict(complete=True, passed=True, unix=time.time(), qualification_only=True,
        consumed_result_sha256=sha(result_path), consumed_readback_sha256=sha(reader_path),
        archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
        source_bytes=r['artifact_bytes'], source_artifacts_retained=True, source_artifacts_modified=False,
        scientific_samples=0, fits=0, native_calls=0, gpu=False,
        member_sha256=members, archive_source_sha256=sha(__file__))
    with receipt.open('xb') as stream:stream.write((json.dumps(doc, sort_keys=True, separators=(',',':'))+'\n').encode())
    print(json.dumps({k:doc[k] for k in ('passed','archive_bytes','source_bytes','source_artifacts_retained')}))


if __name__ == '__main__':main()
