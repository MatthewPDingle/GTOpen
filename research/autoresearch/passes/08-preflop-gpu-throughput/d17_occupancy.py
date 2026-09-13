"""Actual empty scans from exact support masks and fixed rank permutations."""
import collections,gzip,hashlib,json,struct
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def masks(fixture):
    name=f'd17-{fixture}-v1';m=read(RAW/(name+'-manifest.json'))
    z=(RAW/(name+'-support.bin.gz')).read_bytes();assert hashlib.sha256(z).hexdigest()==m['compressed_sha256']
    data=gzip.decompress(z);assert hashlib.sha256(data).hexdigest()==m['support_sha256'] and len(data)==m['support_bytes']
    assert data[:8]==b'D17V1\0\0\0';players=struct.unpack_from('<I',data,8)[0]
    old=read(RAW/f'd10-{fixture}-v1.json');assert players==old['players']
    counters=[collections.Counter() for _ in range(players)];hist=[[0]*170 for _ in range(players)];next_id=[0]*players
    for mode,seat,identity,a,b,c in struct.iter_unpack('<IIIQQQ',data[12:]):
        assert mode==0 and 0<=seat<players and identity==next_id[seat];next_id[seat]+=1
        assert c>>41==0;mask=a|(b<<64)|(c<<128);assert mask
        counters[seat][mask]+=1;hist[seat][mask.bit_count()]+=1
    for row in old['rows']:
        if row['mode']==0:
            p=row['player'];assert hist[p]==row['unique_support_histogram']
            assert next_id[p]==row['unique_distributions']
    return counters
def main():
    m=read(RAW/'d13-ranks-manifest.json');z=(RAW/'d13-fixed-ranks-v1.json.gz').read_bytes()
    assert hashlib.sha256(z).hexdigest()==m['compressed_sha256'];data=gzip.decompress(z)
    assert hashlib.sha256(data).hexdigest()==m['table_sha256'];t=json.loads(data)
    assert (t['samples'],t['classes'])==(1024,169)
    tile_masks=[]
    for sample in range(1024):
        order=t['order'][sample*169:(sample+1)*169];assert sorted(order)==list(range(169))
        for tile in range(0,169,32):
            mask=sum(1<<h for h in order[tile:tile+32]);tile_masks.append(mask)
    unique_tiles=collections.Counter(tile_masks);assert sum(unique_tiles.values())==6144
    tc=list(unique_tiles);wordmask=(1<<64)-1
    tiles=np.array([[(v>>(64*i))&wordmask for i in range(3)] for v in tc],dtype=np.uint64)
    weights=np.array([unique_tiles[v] for v in tc],dtype=np.int64)
    fixtures={};sources={};all_results={}
    for fixture in ['small','large']:
        counters=masks(fixture);combined=sum(counters,collections.Counter());patterns=sorted(combined)
        print(json.dumps(dict(fixture=fixture,distinct_support_patterns=len(patterns),unique_tile_masks=len(tc))),flush=True)
        empty={}
        for start in range(0,len(patterns),256):
            part=patterns[start:start+256]
            values=np.array([[(v>>(64*i))&wordmask for i in range(3)] for v in part],dtype=np.uint64)
            zero=np.ones((len(part),len(tc)),dtype=np.bool_)
            for word in range(3):zero&=(values[:,None,word]&tiles[None,:,word])==0
            counts=zero.astype(np.int64)@weights
            for p,n in zip(part,counts):empty[p]=int(n)
        # Independent arbitrary-precision intersections; zero high-support
        # cases are proved directly by the <=32 tile capacity.
        for p in patterns:
            actual=0 if p.bit_count()>160 else sum(w for tile,w in unique_tiles.items() if p&tile==0)
            assert actual==empty[p]
        rows=sum(combined.values());n=sum(combined[p]*empty[p] for p in patterns)
        per_seat=[dict(seat=i,rows=sum(c.values()),empty_tile_scans=sum(v*empty[p] for p,v in c.items())) for i,c in enumerate(counters)]
        assert sum(x['rows'] for x in per_seat)==rows and sum(x['empty_tile_scans'] for x in per_seat)==n
        prior=read(RAW/'d16-learning-bound.json')['fixtures'][fixture]
        assert prior['distinct_rows']==rows and prior['guaranteed_empty_tile_scans']<=n<=prior['optimistic_empty_tile_scans']
        fixtures[fixture]=dict(distinct_rows=rows,unique_support_patterns=len(patterns),
            empty_tile_scans=n,total_tile_scans=rows*6144,empty_fraction=n/(rows*6144),seats=per_seat)
        all_results[fixture]=[dict(mask=hex(p),rows=combined[p],empty_tiles=empty[p]) for p in patterns]
        for suffix in ['-manifest.json','-support.bin.gz','.json','-exit.json']:
            name=f'd17-{fixture}-v1'+suffix;sources[name]=sha(RAW/name)
    for name in ['d13-ranks-manifest.json','d13-fixed-ranks-v1.json.gz','d16-learning-bound.json']:
        sources[name]=sha(RAW/name)
    out=dict(fixtures=fixtures,unique_tile_masks=len(tc),sources=sources,
        independent_three_word_and_integer_methods_agree=True,
        admit_gpu_prototype=fixtures['large']['empty_fraction']>=.20,
        protocol_sha256=sha(HERE/'D17_PROTOCOL.md'),script_sha256=sha(Path(__file__)))
    pattern_data=(json.dumps(all_results,separators=(',',':'))+'\n').encode()
    compressed=gzip.compress(pattern_data,mtime=0);dest=RAW/'d17-pattern-counts.json.gz';assert not dest.exists();dest.write_bytes(compressed)
    out['pattern_counts_sha256']=hashlib.sha256(pattern_data).hexdigest();out['pattern_counts_compressed_sha256']=sha(dest)
    with (RAW/'d17-occupancy.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps(dict(fixtures=fixtures,admit_gpu_prototype=out['admit_gpu_prototype']),indent=2),flush=True)
if __name__=='__main__':main()
