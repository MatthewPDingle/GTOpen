"""Lossless byte-codec screen on newly generated F32 storage fixtures.

FIXTURE_DIRECTORY OUTPUT. Reads research copies only; never loads the app.
Compression ratios on these turn-board fixtures cannot predict full-flop fit.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import zlib
import numpy as np


def encode(raw, mode):
    assert len(raw) % 4 == 0
    header = struct.pack('<Q', len(raw)//4)
    if mode == 'raw':
        return header+raw
    if mode == 'zero_bitmap':
        words = np.frombuffer(raw, dtype='<u4')
        mask = words != 0  # bitwise +0 only; -0, subnormals and NaNs survive
        return header+np.packbits(mask, bitorder='little').tobytes()+words[mask].tobytes()
    if mode == 'deflate1':
        return header+zlib.compress(raw, level=1)
    assert mode == 'byte_shuffle_deflate1'
    shuffled = np.frombuffer(raw, dtype=np.uint8).reshape(-1,4).T.copy().tobytes()
    return header+zlib.compress(shuffled, level=1)


def decode(packed, mode):
    count, = struct.unpack('<Q', packed[:8])
    data = packed[8:]
    if mode == 'raw':
        result = data
    elif mode == 'zero_bitmap':
        mask_bytes = (count+7)//8
        mask = np.unpackbits(np.frombuffer(data[:mask_bytes], dtype=np.uint8),
                             bitorder='little')[:count].astype(bool)
        values = np.frombuffer(data[mask_bytes:], dtype='<u4')
        assert len(values) == mask.sum()
        result = np.zeros(count, dtype='<u4')
        result[mask] = values
        result = result.tobytes()
    elif mode == 'deflate1':
        result = zlib.decompress(data)
    else:
        assert mode == 'byte_shuffle_deflate1'
        result = np.frombuffer(zlib.decompress(data), dtype=np.uint8).reshape(4,-1).T.copy().tobytes()
    assert len(result) == count*4
    return result


def read_arenas(path):
    with path.open('rb') as file:
        assert file.readline() == b'GTOSOLVE2\n'
        header = json.loads(file.readline())
        for name in ['oop_regret', 'ip_regret', 'oop_average', 'ip_average']:
            count, = struct.unpack('<Q', file.read(8))
            raw = file.read(count*4)
            assert len(raw) == count*4
            yield header, name, raw
        assert file.read() == b''


def main():
    folder, output = map(Path, sys.argv[1:])
    assert not output.exists()
    modes = ['raw', 'zero_bitmap', 'deflate1', 'byte_shuffle_deflate1']
    random = np.random.default_rng(20260919).integers(0, 2**32, 4096, dtype=np.uint32)
    random[::3] = 0
    random[:8] = [0, 0x80000000, 1, 0x007fffff, 0x7f800000, 0xff800000, 0x7fc12345, 0xffffffff]
    for raw in [b'', random.astype('<u4').tobytes(), b'\0'*4096]:
        for mode in modes:
            assert decode(encode(raw, mode), mode) == raw
    manifest_path = folder/'fixtures.json'
    manifest = json.loads(manifest_path.read_text())
    assert manifest['storage'] == 'F32'
    rows = []
    hashes = {str(manifest_path):hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
              str(Path(__file__)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for fixture in manifest['rows']:
        path = folder/fixture['file']
        digest = hashlib.sha256()
        arena_bytes = 0
        for header, name, raw in read_arenas(path):
            assert header['iteration'] == fixture['iteration']
            digest.update(raw)
            arena_bytes += len(raw)
            for mode in modes:
                started = time.perf_counter()
                encoded = encode(raw, mode)
                encode_seconds = time.perf_counter()-started
                started = time.perf_counter()
                restored = decode(encoded, mode)
                decode_seconds = time.perf_counter()-started
                assert restored == raw, (path, name, mode)
                rows.append(dict(fixture=fixture['file'], board=fixture['board'], pot=fixture['pot'],
                    iteration=fixture['iteration'], arena=name, mode=mode,
                    raw_bytes=len(raw), encoded_bytes=len(encoded),
                    encode_seconds=encode_seconds, decode_seconds=decode_seconds,
                    positive_zero_fraction=float((np.frombuffer(raw,dtype='<u4')==0).mean())))
        assert arena_bytes == fixture['arena_bytes']
        hashes[str(path)+':arena_bytes_only'] = digest.hexdigest()
    summary = []
    for iteration in [1, 100]:
        for mode in modes:
            group = [r for r in rows if r['iteration']==iteration and r['mode']==mode]
            raw_size = sum(r['raw_bytes'] for r in group)
            summary.append(dict(iteration=iteration, mode=mode, raw_bytes=raw_size,
                encoded_fraction=sum(r['encoded_bytes'] for r in group)/raw_size,
                encode_seconds=sum(r['encode_seconds'] for r in group),
                decode_seconds=sum(r['decode_seconds'] for r in group)))
    result = dict(bitwise_roundtrips_passed=True, edge_cases_passed=True, summaries=summary, rows=rows,
                  inputs_sha256=hashes,
                  note='CPU-only exploratory storage screen on two turn-board F32 fixtures. Single-pass, concurrent timings include Python copies and are not isolated throughput benchmarks. No GPU integration, live solver change, full-flop fit, convergence or poker-accuracy claim.')
    output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'bitwise_roundtrips_passed':True, 'summaries':summary}, indent=2))


if __name__ == '__main__':
    main()
