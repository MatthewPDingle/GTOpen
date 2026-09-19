"""Exploratory block-codec screen; never changes solver state or app packages.

FIXTURE_DIRECTORY OUTPUT. Isolated dependencies: target/storage-codecs.
Every block falls back to raw storage if compression does not shrink it.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import struct
import sys
import time
import numpy as np
import continuation_storage_screen as base

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'target/storage-codecs'))
import lz4.block
import zstandard

BLOCK = 1024*1024
ZC = zstandard.ZstdCompressor(level=1, threads=0)
ZD = zstandard.ZstdDecompressor()
MODES = ['raw', 'lz4', 'shuffle_lz4', 'zstd1', 'shuffle_zstd1']


def encode(raw, mode):
    assert len(raw) % 4 == 0
    original = struct.pack('<Q', len(raw))
    if mode == 'raw':
        return original+b'R'+raw
    shuffled = mode.startswith('shuffle_')
    source = np.frombuffer(raw, dtype=np.uint8).reshape(-1,4).T.copy().tobytes() if shuffled else raw
    packed = lz4.block.compress(source, mode='fast', acceleration=1) if mode.endswith('lz4') else ZC.compress(source)
    return original+(b'C'+packed if len(packed) < len(raw) else b'R'+raw)


def decode(packed, mode):
    size, = struct.unpack('<Q', packed[:8])
    if packed[8:9] == b'R':
        raw = packed[9:]
    else:
        assert packed[8:9] == b'C'
        raw = lz4.block.decompress(packed[9:]) if mode.endswith('lz4') else ZD.decompress(packed[9:], max_output_size=size)
        if mode.startswith('shuffle_'):
            raw = np.frombuffer(raw, dtype=np.uint8).reshape(4,-1).T.copy().tobytes()
    assert len(raw) == size
    return raw


def main():
    folder, output = map(Path, sys.argv[1:])
    assert not output.exists()
    random = np.random.default_rng(20260919).integers(0, 2**32, 4096, dtype=np.uint32)
    random[:8] = [0, 0x80000000, 1, 0x007fffff, 0x7f800000, 0xff800000, 0x7fc12345, 0xffffffff]
    for raw in [b'', random.astype('<u4').tobytes(), b'\0'*BLOCK]:
        for mode in MODES:
            packed = encode(raw, mode)
            assert decode(packed, mode) == raw
            assert len(packed) <= len(raw)+9
    manifest_path = folder/'fixtures.json'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['storage'] == 'F32'
    rows = []
    hashes = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(base.__file__),manifest_path]}
    for fixture in manifest['rows']:
        path = folder/fixture['file']
        digest = hashlib.sha256()
        raw_total = 0
        for header, name, raw in base.read_arenas(path):
            assert header['iteration'] == fixture['iteration']
            digest.update(raw);raw_total += len(raw)
            for mode in MODES:
                encoded_bytes = raw_blocks = blocks = 0
                enc_time = dec_time = 0.
                for offset in range(0,len(raw),BLOCK):
                    chunk = raw[offset:offset+BLOCK]
                    t = time.perf_counter(); packed = encode(chunk,mode); enc_time += time.perf_counter()-t
                    t = time.perf_counter(); restored = decode(packed,mode); dec_time += time.perf_counter()-t
                    assert restored == chunk
                    encoded_bytes += len(packed);raw_blocks += packed[8:9] == b'R';blocks += 1
                rows.append(dict(fixture=fixture['file'],iteration=fixture['iteration'],arena=name,mode=mode,
                                 raw_bytes=len(raw),encoded_bytes=encoded_bytes,blocks=blocks,raw_blocks=raw_blocks,
                                 encode_seconds=enc_time,decode_seconds=dec_time))
        assert raw_total == fixture['arena_bytes']
        hashes[str(path)+':arena_bytes_only'] = digest.hexdigest()
    summaries = []
    for iteration in sorted({r['iteration'] for r in rows}):
        for mode in MODES:
            group = [r for r in rows if r['iteration']==iteration and r['mode']==mode]
            raw_size = sum(r['raw_bytes'] for r in group)
            summaries.append(dict(iteration=iteration,mode=mode,raw_bytes=raw_size,
                encoded_fraction=sum(r['encoded_bytes'] for r in group)/raw_size,
                encode_seconds=sum(r['encode_seconds'] for r in group),decode_seconds=sum(r['decode_seconds'] for r in group),
                raw_fallback_blocks=sum(r['raw_blocks'] for r in group)))
    packages = {p:importlib.metadata.version(p) for p in ['lz4','zstandard']}
    result = dict(bitwise_roundtrips_passed=True,edge_cases_passed=True,block_bytes=BLOCK,packages=packages,
                  summaries=summaries,rows=rows,inputs_sha256=hashes,
                  note='Exploratory CPU compression screen. Single-pass concurrent timings include allocation and copies; small turn fixtures may fit CPU caches. No native paging integration, full-flop capacity or solver-speed claim.')
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'passed':True,'packages':packages,'summaries':summaries},indent=2))


if __name__ == '__main__':
    main()
