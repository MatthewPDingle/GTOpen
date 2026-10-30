"""Lossless codec screen on immutable, trained (iteration 2000) checkpoint blocks.

Selection is registered before reading payloads. No checkpoint writes, solver
calls, CUDA allocation, production access, or changes to numeric values.
"""
import hashlib
import json
import platform
import struct
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
DEPS = Path('S:/GTOpen-research/python-codecs-20260922')
sys.path.insert(0, str(DEPS))
import zstandard as zstd
import lz4.frame as lz4
import zlib

SOURCES = {name: Path(f'S:/GTOpen-research/strategic-segments-v1/strategic-{name}112-2000-v1/final')
           for name in ('weighted', 'equal')}
BLOCK = 256*1024


def sha_file(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def digest(b):
    return hashlib.sha256(b).hexdigest()


def transform(raw, layout):
    assert len(raw) % 4 == 0
    if layout == 'raw':
        return raw
    if layout == 'xor_shuffle':
        a = np.frombuffer(raw, dtype='<u4')
        a = np.concatenate([a[:1], np.bitwise_xor(a[1:], a[:-1])])
        raw = a.tobytes()
    return np.frombuffer(raw, dtype=np.uint8).reshape(-1, 4).T.copy().tobytes()


def restore(raw, layout):
    if layout == 'raw':
        return raw
    raw = np.frombuffer(raw, dtype=np.uint8).reshape(4, -1).T.copy().tobytes()
    if layout == 'xor_shuffle':
        raw = np.bitwise_xor.accumulate(np.frombuffer(raw, dtype='<u4')).tobytes()
    return raw


def codecs():
    return {
        'zstd1': (zstd.ZstdCompressor(level=1, write_checksum=True).compress, zstd.ZstdDecompressor().decompress),
        'zstd3': (zstd.ZstdCompressor(level=3, write_checksum=True).compress, zstd.ZstdDecompressor().decompress),
        'lz4': (lambda b: lz4.compress(b, compression_level=0, content_checksum=True), lz4.decompress),
        'zlib1': (lambda b: zlib.compress(b, 1), zlib.decompress),
    }


def main():
    registration = OUT/'compression-probe-registration.json'
    destination = OUT/'compression-probe-result.json'
    assert not registration.exists() and not destination.exists(), 'preserve evidence'
    indices = {k: json.loads((p/'index.json').read_text()) for k, p in SOURCES.items()}
    boards = indices['weighted']['shape']['boards']
    assert len(boards) == 112 and indices['equal']['shape']['boards'] == boards
    for d in indices.values():
        assert d['iteration'] == 2000 and d['shape']['continuation_counts'] == [112, 112]
    selected = {}
    for i, board in enumerate(boards):
        cards = [board[k:k+2] for k in (0, 2, 4)]
        category = 'paired' if len({c[0] for c in cards}) < 3 else {1:'mono', 2:'two-tone', 3:'rainbow'}[len({c[1] for c in cards})]
        selected.setdefault(category, i)
    selected['middle-index'] = len(boards)//2
    selected['last-index'] = len(boards)-1
    board_ids = sorted(set(selected.values()))
    entries = [(branch, i+pot*112) for branch in SOURCES for pot in range(2) for i in board_ids]
    reg = {'purpose':'Codec feasibility only; old narrow-range states do not prove wide-BB compression',
           'iteration':2000, 'block_bytes':BLOCK, 'selection':selected,
           'boards':{str(i):boards[i] for i in board_ids}, 'entries':entries,
           'array_selection':'All four arrays; first, middle, final aligned 256 KiB windows, de-duplicated',
           'layouts':['raw', 'shuffle', 'xor_shuffle'], 'codecs':list(codecs()),
           'source_indices':{str(p/'index.json'):sha_file(p/'index.json') for p in SOURCES.values()},
           'script_sha256':sha_file(Path(__file__)), 'created_at_unix':time.time()}
    with registration.open('x') as f:
        json.dump(reg, f, indent=2)
    cs = codecs()
    # Exact bit-pattern controls include +/-zero, infinities and NaN payloads.
    rng = np.random.default_rng(20260922)
    control = np.concatenate([np.array([0, 0x80000000, 0x7f800000, 0xff800000, 0x7fc00001, 0x7fffffff], dtype='<u4'),
                              rng.integers(0, 2**32, size=4096, dtype=np.uint32)]).tobytes()
    controls = []
    for layout in reg['layouts']:
        for name, (encode, decode) in cs.items():
            encoded = encode(transform(control, layout))
            assert restore(decode(encoded), layout) == control
            corrupt = bytearray(encoded)
            corrupt[len(corrupt)//2] ^= 1
            try:
                decoded = restore(decode(bytes(corrupt)), layout)
                assert digest(decoded) != digest(control), 'corruption not detected'
            except (ValueError, RuntimeError, zstd.ZstdError, zlib.error):
                pass
            controls.append(f'{layout}/{name}')
    rows, source_hashes = [], {}
    for branch, key in entries:
        path = SOURCES[branch]/f'entry-{key}-generation-0.bin'
        before = sha_file(path)
        descriptor = indices[branch]['entries'][key]
        with path.open('rb') as f:
            header = struct.unpack('<9Q', f.read(72))
            assert header[0] == 0x47544f5353440001 and list(header[1:]) == descriptor
            assert header[1:4] == (key, 0, 2000)
            lengths = header[4:8]
            assert path.stat().st_size == 72+sum(lengths)*4
            base = 72
            for array, count in enumerate(lengths):
                size = count*4
                length = min(BLOCK, size)
                assert length > 0
                offsets = sorted({0, ((size-length)//2)//4*4, size-length})
                for offset in offsets:
                    f.seek(base+offset)
                    raw = f.read(length)
                    assert len(raw) == length
                    assert np.isfinite(np.frombuffer(raw, dtype='<f4')).all(), 'nonfinite trained state'
                    bits = np.frombuffer(raw, dtype='<u4')
                    row = {'branch':branch, 'entry':key, 'array':array, 'offset':offset,
                           'raw_bytes':length, 'sha256':digest(raw),
                           'zero_fraction':float(np.mean((bits & 0x7fffffff) == 0)), 'codecs':{}}
                    for layout in reg['layouts']:
                        for name, (encode, decode) in cs.items():
                            start = time.perf_counter()
                            encoded = encode(transform(raw, layout))
                            packed_at = time.perf_counter()
                            restored = restore(decode(encoded), layout)
                            end = time.perf_counter()
                            assert restored == raw, (branch, key, array, offset, layout, name)
                            row['codecs'][f'{layout}/{name}'] = {'encoded_bytes':len(encoded),
                                'encode_seconds':packed_at-start, 'decode_seconds':end-packed_at}
                    rows.append(row)
                base += size
        assert sha_file(path) == before, 'source checkpoint changed'
        source_hashes[str(path)] = before
        print(f'checked {branch} entry {key}; sampled blocks={len(rows)}', flush=True)
    totals = defaultdict(lambda: {'raw_bytes':0, 'encoded_bytes':0, 'encode_seconds':0., 'decode_seconds':0.})
    by_array = defaultdict(lambda: {'raw_bytes':0, 'encoded_bytes':0})
    for row in rows:
        for name, result in row['codecs'].items():
            totals[name]['raw_bytes'] += row['raw_bytes']
            for k, value in result.items():
                totals[name][k] += value
            key = f'{row["array"]}/{name}'
            by_array[key]['raw_bytes'] += row['raw_bytes']
            by_array[key]['encoded_bytes'] += result['encoded_bytes']
    for result in totals.values():
        result['ratio'] = result['raw_bytes']/result['encoded_bytes']
        result['encode_MB_per_second'] = result['raw_bytes']/result['encode_seconds']/1e6
        result['decode_MB_per_second'] = result['raw_bytes']/result['decode_seconds']/1e6
    for p, expected in reg['source_indices'].items():
        assert sha_file(Path(p)) == expected
    result = {'registration_sha256':sha_file(registration), 'rows':rows, 'totals':dict(totals),
              'by_array':dict(by_array), 'source_hashes':source_hashes, 'bit_controls_passed':controls,
              'checkpoint_files_modified':False, 'all_roundtrips_exact':True,
              'environment':{'python':sys.version, 'platform':platform.platform(), 'numpy':np.__version__,
                             'zstandard':zstd.__version__, 'zlib':zlib.ZLIB_RUNTIME_VERSION,
                             'lz4_frame_library':str(lz4.__file__)},
              'limitations':['Sampled windows; not whole-file compression ratios.',
                             'Original narrow-range checkpoint; not the new BB context.',
                             'Single-process timing screen, not sustained disk or solver throughput.',
                             'Signed zero and all bits preserved; no numerical quantization.']}
    with destination.open('x') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result['totals'], indent=2))


if __name__ == '__main__':
    main()
