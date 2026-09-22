"""Whole-record follow-up to the registered trained-state block codec screen."""
import json
import struct
import time
from collections import defaultdict
from pathlib import Path
from hu_state_compression_probe_20260922 import OUT, zstd, sha_file


def main():
    result_path = OUT/'compression-whole-record-result.json'
    assert not result_path.exists(), 'preserve evidence'
    probe_path = OUT/'compression-probe-result.json'
    probe = json.loads(probe_path.read_text())
    # All 24 previously selected records, not records chosen by compression ratio.
    sources = probe['source_hashes']
    registration = {'source_probe_sha256':sha_file(probe_path), 'sources':sources,
                    'codecs':['zstd1', 'zstd3'], 'chunk_bytes':1024*1024,
                    'reason':'Raw zstd3 was best in the block screen; zstd1 is the faster alternative.',
                    'created_at_unix':time.time(), 'script_sha256':sha_file(Path(__file__))}
    with (OUT/'compression-whole-record-registration.json').open('x') as f:
        json.dump(registration, f, indent=2)
    codecs = {f'zstd{k}':(zstd.ZstdCompressor(level=k, write_checksum=True), zstd.ZstdDecompressor()) for k in (1,3)}
    rows = []
    for path, expected in sources.items():
        p = Path(path)
        assert sha_file(p) == expected
        stats = defaultdict(lambda: dict(raw_bytes=0, encoded_bytes=0, chunks=0, encode_seconds=0., decode_seconds=0.))
        with p.open('rb') as f:
            header = struct.unpack('<9Q', f.read(72))
            assert header[0] == 0x47544f5353440001 and header[3] == 2000
            assert p.stat().st_size == 72+4*sum(header[4:8])
            for count in header[4:8]:
                left = count*4
                while left:
                    raw = f.read(min(left, registration['chunk_bytes']))
                    assert raw
                    left -= len(raw)
                    for name, (encoder, decoder) in codecs.items():
                        begin = time.perf_counter(); packed = encoder.compress(raw); middle = time.perf_counter()
                        restored = decoder.decompress(packed); end = time.perf_counter()
                        assert restored == raw
                        s = stats[name]
                        s['raw_bytes'] += len(raw)
                        s['encoded_bytes'] += len(packed)
                        s['chunks'] += 1
                        s['encode_seconds'] += middle-begin
                        s['decode_seconds'] += end-middle
            assert f.read(1) == b''
        assert sha_file(p) == expected
        rows.append({'path':path, 'sha256':expected, 'codecs':dict(stats)})
        print(f'whole-record verified {len(rows)}/{len(sources)}', flush=True)
    totals = {name:{key:sum(r['codecs'][name][key] for r in rows) for key in rows[0]['codecs'][name]} for name in codecs}
    for s in totals.values():
        # Allow an additional 64 bytes per chunk for a future outer checksum/index.
        s['framed_bytes_with_allowance'] = s['encoded_bytes']+64*s['chunks']+72*len(rows)
        s['ratio_with_allowance'] = s['raw_bytes']/s['framed_bytes_with_allowance']
        s['encode_MB_per_second'] = s['raw_bytes']/s['encode_seconds']/1e6
        s['decode_MB_per_second'] = s['raw_bytes']/s['decode_seconds']/1e6
    result = {'registration':registration, 'rows':rows, 'totals':totals,
              'all_roundtrips_exact':True, 'source_files_unchanged':True,
              'compressed_files_written':False,
              'limitations':['Entire payloads of the previously selected 24 old-context records only.',
                             'Does not establish the full checkpoint or wide BB compression ratio.',
                             'CPU codec timing excludes SSD writes and GPU transfers.']}
    with result_path.open('x') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(totals, indent=2))


if __name__ == '__main__':
    main()
