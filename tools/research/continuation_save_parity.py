"""Read-only full-arena parity for research preflop saves; never loads the app."""
import hashlib
import json
import struct
from pathlib import Path
import numpy as np


def inspect(path):
    path=Path(path);size=path.stat().st_size
    with path.open('rb') as stream:
        magic=stream.readline()
        assert magic in [b'GTOPREFLOP1\n',b'GTOPREFLOP2\n',b'GTOPREFLOP3\n',b'GTOPREFLOP4\n'],'Unknown save format'
        header=json.loads(stream.readline())
        arrays=[]
        for name in ['regrets','strategy_sums']+(['hero_regrets','hero_sums'] if header.get('hero_backup') is not None else []):
            encoded=stream.read(8);assert len(encoded)==8,'Truncated arena length'
            count=struct.unpack('<Q',encoded)[0];offset=stream.tell()
            assert count*4<=size-offset,'Truncated arena'
            arrays.append(dict(name=name,count=count,offset=offset))
            stream.seek(count*4,1)
        assert stream.tell()==size,'Unexpected trailing save data'
    return magic,header,arrays


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()


def compare(left,right):
    a=inspect(left);b=inspect(right)
    assert a[0]==b[0] and a[1]==b[1],'Save headers differ'
    assert len(a[2])==len(b[2])
    results=[]
    for x,y in zip(a[2],b[2]):
        assert x['name']==y['name'] and x['count']==y['count'],'Arena shapes differ'
        changed=0;maximum=0.
        if x['count']:
            av=np.memmap(left,mode='r',dtype='<f4',offset=x['offset'],shape=(x['count'],))
            bv=np.memmap(right,mode='r',dtype='<f4',offset=y['offset'],shape=(y['count'],))
            for start in range(0,x['count'],1048576):
                u=av[start:start+1048576];v=bv[start:start+1048576]
                assert np.isfinite(u).all() and np.isfinite(v).all(),'Nonfinite arena entry'
                changed+=int(np.count_nonzero(u!=v))
                maximum=max(maximum,float(np.max(np.abs(u.astype(float)-v.astype(float)))))
            del u,v,av,bv
        results.append(dict(arena=x['name'],entries=x['count'],changed=changed,max_absolute_change=maximum))
    hashes=[digest(p) for p in [left,right]]
    return dict(iteration=a[1]['iteration'],arenas=results,all_numeric_entries_equal=all(r['changed']==0 for r in results),
        byte_identical=hashes[0]==hashes[1],sha256=hashes)
