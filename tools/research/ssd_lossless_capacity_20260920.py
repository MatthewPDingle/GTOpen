"""Read immutable owned snapshots; exact zero-word size model and zlib baseline."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import time
import zlib
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'


def main():
    label=sys.argv[1]
    assert label in ['small60','connected20']
    if label=='small60':
        directory=Path('S:/GTOpen-research/ssd-storage-20260920-parity-v1')
        assert json.loads((OUT/'ssd-paging-v1-review.json').read_text())['passed']
    else:
        directory=Path('S:/GTOpen-research/ssd-connected-v1-ssd')
        status=json.loads((OUT/'connected-v1-status.json').read_text())
        assert 'ssd' in status['completed']
    paths=sorted(directory.glob('entry-*-generation-*.bin'))
    assert len(paths)==6
    rows=[]
    for path in paths:
        raw=path.read_bytes()
        header=struct.unpack_from('<9Q',raw)
        magic,key,generation,iteration,*rest=header
        lengths=rest[:4]
        assert magic==0x47544f5353440001 and len(raw)==72+sum(lengths)*4
        assert iteration==(60 if label=='small60' else 20)
        offset=72
        for k,n in enumerate(lengths):
            payload=raw[offset:offset+n*4];offset+=n*4
            words=np.frombuffer(payload,dtype='<u4')
            zeros=int(np.count_nonzero(words==0))
            masked=4*((n+31)//32)+4*(n-zeros)
            start=time.perf_counter();compressed=zlib.compress(payload,level=1);encode=time.perf_counter()-start
            start=time.perf_counter();decoded=zlib.decompress(compressed);decode=time.perf_counter()-start
            assert decoded==payload
            rows.append(dict(path=str(path),source_sha256=hashlib.sha256(raw).hexdigest(),
                entry=key,generation=generation,iteration=iteration,array=k,
                words=n,positive_zero_words=zeros,raw_bytes=len(payload),
                zero_mask_with_raw_fallback_bytes=min(masked,len(payload)),
                zlib1_bytes=len(compressed),zlib1_encode_seconds=encode,zlib1_decode_seconds=decode,
                zlib1_roundtrip_exact=True))
        del raw
    totals={key:sum(r[key] for r in rows) for key in ['raw_bytes','zero_mask_with_raw_fallback_bytes','zlib1_bytes',
        'zlib1_encode_seconds','zlib1_decode_seconds']}
    result=dict(label=label,passed=True,rows=rows,totals=totals,
        limitations='Early-state sample, not mature-state or full-panel memory bound. Masking is size-only forecast; zlib timing includes Python allocation and is not integrated solver performance.')
    with (OUT/(label+'-lossless-capacity.json')).open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(totals,indent=2))


if __name__=='__main__':main()
