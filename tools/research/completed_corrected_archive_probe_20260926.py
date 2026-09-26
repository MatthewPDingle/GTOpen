"""Measure full completed-corrected object compression in RAM; never retire files."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
import lzma
from pathlib import Path
import struct
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from reboot_research_idle_v1 import idle
from owned_research_archive_v1 import MAGIC, MAX_RAW, MAX_PACKED, MAX_HEADER, encoded, name
from owned_columnar_evaluation_archive_v1 import unlinked

PREFIX = 'completed-corrected-archive-probe-v1'


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    started = time.monotonic()
    last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        assert now - started < 600
        assert psutil.virtual_memory().available >= 20_000_000_000
        if now - last > 2:
            assert idle(); last = now
    guard()
    rp, dest = [OUT / f'{PREFIX}-{s}.json' for s in ('registration', 'result')]
    assert not rp.exists() and not dest.exists()
    tr = OUT / 'showdown-matched-training-v1-registration.json'
    registration = read(tr)
    case = Path(registration['store']) / '9266201-corrected'
    fp = case / 'result.json'; final = read(fp)
    ap = OUT / 'showdown-training-readback-v2-9266201-corrected-0078-result.json'
    ar = OUT / 'showdown-training-readback-v2-9266201-corrected-0078-registration.json'
    audit = read(ap)
    assert final['completed_iterations'] == 78 and final['final_restore_verified']
    assert audit['passed'] and audit['complete_arm'] and audit['arm'] == final['name']
    assert audit['source_registration_sha256'] == sha(tr)
    assert audit['readback_registration_sha256'] == sha(ar)
    objects = unlinked(case / 'objects')
    files = sorted(objects.iterdir())
    assert files and all(p.is_file() for p in files)
    assert sum(p.stat().st_size for p in files) <= MAX_RAW
    paths = [tr, fp, ap, ar, *files, Path(__file__).resolve(),
             ROOT / 'tools/research/owned_research_archive_v1.py']
    inputs = {}
    for p in paths:
        guard(); unlinked(p); inputs[str(p)] = sha(p)
    save(rp, dict(inputs=inputs, maximum_seconds=600, gpu_used=False,
                  scope='In-memory full completed object bundle; no archive publication or deletion.'))
    try:
        items, payload = [], []
        for p in files:
            guard(); raw = p.read_bytes(); h = hashlib.sha256(raw).hexdigest()
            assert h == inputs[str(p)] == p.stem.split('-')[1]
            items.append(dict(name=name(p.name), bytes=len(raw), sha256=h)); payload.append(raw)
        header = encoded(items)
        assert len(header) <= MAX_HEADER
        original = MAGIC + struct.pack('<Q', len(header)) + header + b''.join(payload)
        del payload
        began = time.monotonic()
        packed = lzma.compress(original, preset=6)
        compression_seconds = time.monotonic() - began
        guard(); assert len(packed) <= MAX_PACKED
        decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ, memlimit=128*1024**2)
        decoded = decoder.decompress(packed, max_length=MAX_RAW+MAX_HEADER+17)
        assert decoder.eof and not decoder.unused_data and decoded == original
        offset = 16 + len(header)
        assert json.loads(decoded[16:offset]) == items
        for item in items:
            raw = decoded[offset:offset+item['bytes']]; offset += item['bytes']
            assert hashlib.sha256(raw).hexdigest() == item['sha256']
        assert offset == len(decoded)
        assert sorted(p.name for p in objects.iterdir()) == [p.name for p in files]
        for p, h in inputs.items():
            guard(); assert sha(p) == h, p
        raw_bytes = sum(i['bytes'] for i in items)
        result = dict(passed=True, registration_sha256=sha(rp), objects=len(items),
            raw_bytes=raw_bytes, packed_bytes=len(packed), packed_sha256=hashlib.sha256(packed).hexdigest(),
            raw_minus_packed_bytes=raw_bytes-len(packed), compression_seconds=compression_seconds,
            seconds=time.monotonic()-started, exact_bytes_recovered=True,
            original_inputs_unchanged=True, archive_published=False, files_retired=0,
            gpu_used=False, production_modified=False,
            scope='Full completed corrected fits existing codec limits in memory. This is not storage admission, durable retention, checkpoint continuation, or poker accuracy qualification.')
        save(dest, result); print(json.dumps(result), flush=True)
    except BaseException as exc:
        save(dest, dict(passed=False, error=repr(exc), registration_sha256=sha(rp)))
        raise


if __name__ == '__main__':
    main()
