"""In-memory lossless compression probe; legacy evidence is never modified."""
import hashlib
import json
import lzma
from pathlib import Path
import struct
import time
from sampled_evidence_archive_gzip6_v1 import read_artifact
from sampled_physical_root_evaluation_v1 import sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle


def main():
    started = time.monotonic()
    def guard():
        assert idle() and time.monotonic() - started < 600
    guard()
    prefix = 'evaluation-lossless-xz-probe-v1'
    rp, dest = (OUT / f'{prefix}-{kind}.json' for kind in ('registration', 'result'))
    assert not rp.exists() and not dest.exists()
    source = OUT / 'later-action-compact-evaluation-study-v1-result.json'
    result = read(source)
    assert result['passed'] and result['complete'] and result['deals'] == 65536
    root = Path(result['store'])
    names = ['test-000000', 'test-032768', 'test-065504']
    inputs = {str(source): sha(source), str(Path(__file__).resolve()): sha(Path(__file__))}
    for name in names:
        path = root / name / 'manifest.json'
        assert sha(path) == result['archive_manifest_hashes'][name]
        inputs[str(path)] = sha(path)
        for p in (root / name).glob('*.gz'):
            inputs[str(p)] = sha(p)
    save(rp, dict(inputs=inputs, batches=names, presets=[6, 9],
        mode='in-memory-only', maximum_seconds=600, production_modified=False))
    rows = []
    try:
        for name in names:
            guard()
            manifest = read(root / name / 'manifest.json')
            parts = {k: read_artifact(root / name, manifest, k, guard=guard)
                     for k in sorted(manifest['artifacts'])}
            header = (json.dumps([dict(name=k, bytes=len(v), sha256=hashlib.sha256(v).hexdigest())
                      for k, v in parts.items()], sort_keys=True, separators=(',', ':')) + '\n').encode()
            payload = b'GTOARCH1' + struct.pack('<Q', len(header)) + header + b''.join(parts.values())
            for preset in (6, 9):
                guard()
                began = time.monotonic()
                packed = lzma.compress(payload, preset=preset)
                encode_seconds = time.monotonic() - began
                began = time.monotonic()
                restored = lzma.decompress(packed, memlimit=128*1024**2)
                decode_seconds = time.monotonic() - began
                assert restored == payload
                row = dict(batch=name, preset=preset, raw_bytes=len(payload),
                    existing_gzip_bytes=sum(v['compressed_bytes'] for v in manifest['artifacts'].values()),
                    xz_bytes=len(packed), encode_seconds=encode_seconds, decode_seconds=decode_seconds,
                    packed_sha256=hashlib.sha256(packed).hexdigest(), byte_identical=True)
                rows.append(row)
                print(json.dumps(row), flush=True)
        for p, h in inputs.items():
            assert sha(p) == h
        save(dest, dict(passed=True, registration_sha256=sha(rp), rows=rows,
            seconds=time.monotonic()-started, legacy_files_modified=False, compressed_files_written=False,
            gpu_used=False, production_modified=False,
            scope='Three fixed old evaluation batches only; compression feasibility, not a future storage admission.'))
    except BaseException as exc:
        save(dest, dict(passed=False, error=repr(exc), registration_sha256=sha(rp), rows=rows))
        raise


if __name__ == '__main__':
    main()
