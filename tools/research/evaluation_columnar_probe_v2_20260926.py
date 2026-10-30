"""Qualify lossless profile transformation on fixed historical batches in RAM."""
import hashlib
import json
import lzma
from pathlib import Path
import struct
import time
from crossed_profile_columnar_v2 import encode, decode
from crossed_profile_columnar_v1 import encoded
from sampled_evidence_archive_gzip6_v1 import read_artifact
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle


def main():
    started = time.monotonic()
    def guard():
        assert idle() and time.monotonic() - started < 600
    guard()
    prefix = 'evaluation-lossless-columnar-probe-v2'
    rp, destination = (OUT / f'{prefix}-{kind}.json' for kind in ('registration', 'result'))
    assert not rp.exists() and not destination.exists()
    previous = OUT / 'evaluation-lossless-xz-probe-v1-result.json'
    assert read(previous)['passed']
    source = OUT / 'later-action-compact-evaluation-study-v1-result.json'
    result = read(source)
    root = Path(result['store'])
    names = ['test-000000', 'test-032768', 'test-065504']
    inputs = {str(p): sha(p) for p in [source, previous, Path(__file__).resolve(),
              ROOT/'tools/research/crossed_profile_columnar_v2.py']}
    for name in names:
        path = root/name/'manifest.json'
        assert sha(path) == result['archive_manifest_hashes'][name]
        inputs[str(path)] = sha(path)
        for p in (root/name).glob('*.gz'):
            inputs[str(p)] = sha(p)
    save(rp, dict(inputs=inputs, batches=names, presets=[6], mode='in-memory-only',
                 maximum_seconds=600, production_modified=False))
    rows, rejections = [], []
    try:
        for name in names:
            guard()
            manifest = read(root/name/'manifest.json')
            parts = {k: read_artifact(root/name, manifest, k, guard=guard)
                     for k in sorted(manifest['artifacts'])}
            began = time.monotonic()
            transformed = encode(parts['profiles.json'])
            transform_seconds = time.monotonic()-began
            small = dict(parts, **{'profiles.json': transformed})
            header = encoded([dict(name=k, codec='columnar-profiles-v2' if k=='profiles.json' else 'raw',
                bytes=len(v), raw_sha256=hashlib.sha256(parts[k]).hexdigest()) for k, v in small.items()])
            payload = b'GTOEVP01'+struct.pack('<Q',len(header))+header+b''.join(small.values())
            began = time.monotonic()
            packed = lzma.compress(payload, preset=6)
            compression_seconds = time.monotonic()-began
            restored = lzma.decompress(packed, memlimit=128*1024**2)
            assert restored == payload
            length = struct.unpack('<Q',restored[8:16])[0]
            layout = json.loads(restored[16:16+length]);offset = 16+length
            for member in layout:
                data = restored[offset:offset+member['bytes']];offset += member['bytes']
                original = decode(data) if member['codec']=='columnar-profiles-v2' else data
                assert original == parts[member['name']]
                assert hashlib.sha256(original).hexdigest() == member['raw_sha256']
            assert offset == len(restored)
            if not rejections:
                # A mixed profile cannot silently lose a distinct probability.
                bad = json.loads(parts['profiles.json'])
                p = bad['profiles'][1]['policies'][0]['probabilities']
                p[0] = 0.125 if p[0] != 0.125 else 0.25
                for label, action in [('changed mixed profile', lambda: encode(encoded(bad))),
                                      ('trailing bytes', lambda: decode(transformed+b'\0')),
                                      ('truncated bytes', lambda: decode(transformed[:-1])),
                                      ('noncanonical serialization', lambda: encode(parts['profiles.json']+b' '))]:
                    try:
                        action()
                    except ValueError:
                        rejections.append(label)
                    else:
                        raise AssertionError('Accepted '+label)
            row = dict(batch=name, raw_bytes=sum(map(len,parts.values())), transformed_bytes=len(payload),
                xz_bytes=len(packed), original_profile_sha256=hashlib.sha256(parts['profiles.json']).hexdigest(),
                packed_sha256=hashlib.sha256(packed).hexdigest(), transform_seconds=transform_seconds,
                compression_seconds=compression_seconds, byte_identical=True)
            rows.append(row);print(json.dumps(row),flush=True)
        for p,h in inputs.items():
            assert sha(p)==h
        save(destination,dict(passed=True,registration_sha256=sha(rp),rows=rows,rejections=rejections,
            seconds=time.monotonic()-started,legacy_files_modified=False,compressed_files_written=False,
            gpu_used=False,production_modified=False,
            scope='Exact reconstruction of every archived member for three fixed old batches. Not a disk-retirement control or future storage admission.'))
    except BaseException as exc:
        save(destination,dict(passed=False,error=repr(exc),registration_sha256=sha(rp),rows=rows))
        raise


if __name__=='__main__':
    main()
