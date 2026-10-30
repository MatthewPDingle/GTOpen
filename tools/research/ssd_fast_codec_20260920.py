"""Lossless LZ4 screening in an isolated dependency folder, immutable owned states."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
sys.path.insert(0,str(ROOT/'target/ssd-codec-python'))
import lz4
import lz4.block


def main():
    label=sys.argv[1]
    assert label in ['small60','connected20']
    assert lz4.__version__=='4.4.5'
    if label=='small60':
        directory=Path('S:/GTOpen-research/ssd-storage-20260920-parity-v1')
        assert json.loads((OUT/'ssd-paging-v1-review.json').read_text())['passed']
    else:
        directory=Path('S:/GTOpen-research/ssd-connected-v1-ssd')
        assert 'ssd' in json.loads((OUT/'connected-v1-status.json').read_text())['completed']
    paths=sorted(directory.glob('entry-*-generation-*.bin'))
    assert len(paths)==6
    rows=[]
    for path in paths:
        raw=path.read_bytes();h=struct.unpack_from('<9Q',raw)
        assert h[0]==0x47544f5353440001 and len(raw)==72+sum(h[4:8])*4
        offset=72;digest=hashlib.sha256(raw).hexdigest()
        for k,n in enumerate(h[4:8]):
            payload=raw[offset:offset+n*4];offset+=n*4
            for mode,acceleration in [('default',1),('fast',4)]:
                start=time.perf_counter();blocks=[];stored=0
                for i in range(0,len(payload),4*1024**2):
                    b=payload[i:i+4*1024**2]
                    packed=lz4.block.compress(b,mode=mode,acceleration=acceleration,store_size=False)
                    compressed=len(packed)<len(b)
                    blocks.append((len(b),compressed,packed if compressed else b))
                    stored+=16+len(blocks[-1][2])
                encode=time.perf_counter()-start
                start=time.perf_counter()
                decoded=b''.join(lz4.block.decompress(b,uncompressed_size=n) if flag else b for n,flag,b in blocks)
                decode=time.perf_counter()-start
                assert decoded==payload
                rows.append(dict(path=str(path),source_sha256=digest,iteration=h[3],entry=h[1],array=k,
                    mode=mode,acceleration=acceleration,raw_bytes=len(payload),stored_bytes=stored,
                    encode_seconds=encode,decode_seconds=decode,exact=True))
    totals={mode:{key:sum(r[key] for r in rows if r['mode']==mode) for key in
        ['raw_bytes','stored_bytes','encode_seconds','decode_seconds']} for mode in ['default','fast']}
    result=dict(passed=True,label=label,version=lz4.__version__,rows=rows,totals=totals,
        caveat='Early snapshots, background research CPU activity; not a mature-state memory bound or native solver benchmark.',
        install_report_sha256=hashlib.sha256((OUT/'lz4-install-report.json').read_bytes()).hexdigest())
    with (OUT/(label+'-fast-codec.json')).open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(totals,indent=2))


if __name__=='__main__':main()
