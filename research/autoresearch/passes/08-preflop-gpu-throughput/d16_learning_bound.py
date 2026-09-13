"""Guaranteed empty scan tiles, independent of each sample permutation."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent; RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    d15=read(RAW/'d15-zero-bound.json');d11=read(RAW/'d11-work-census.json')
    sources={};fixtures={}
    for fixture in ['small','large']:
        path=RAW/f'd10-{fixture}-v1.json';sources[path.name]=sha(path)
        assert sources[path.name]==d15['sources'][path.name]
        old=read(path);assert old['read_only'] and old['arenas_unchanged']
        hist=[0]*170;seats=[]
        for row in old['rows']:
            if row['mode']!=0:continue
            h=row['unique_support_histogram'];assert len(h)==170 and h[0]==0
            assert sum(h)==row['unique_distributions']
            hist=[x+y for x,y in zip(hist,h)]
            n=sum(h);lo=sum(v*max(0,6-k) for k,v in enumerate(h) if k)
            seats.append(dict(seat=row['player'],distinct_rows=n,
                guaranteed_empty_tiles_per_sample=lo,guaranteed_empty_fraction=lo/(6*n)))
        n=sum(hist);lo=sum(v*max(0,6-k) for k,v in enumerate(hist) if k)
        hi=sum(v*(6-(k+31)//32) for k,v in enumerate(hist) if k)
        assert n==d11['fixtures'][fixture]['modes']['learning']['distinct_distribution_rows']
        previous=d15['fixtures'][fixture]['modes']['learning']
        assert hist==previous['support_histogram'] and hi*1024==previous['empty_tile_upper_bound']
        fixtures[fixture]=dict(distinct_rows=n,support_histogram=hist,seats=seats,
            total_tile_scans=n*6*1024,guaranteed_empty_tile_scans=lo*1024,
            optimistic_empty_tile_scans=hi*1024,
            guaranteed_empty_fraction=lo/(6*n),optimistic_empty_fraction=hi/(6*n))
    for name in ['d15-zero-bound.json','d15-verified.json','d11-work-census.json']:
        sources[name]=sha(RAW/name)
    out=dict(fixtures=fixtures,sources=sources,
        protocol_sha256=sha(HERE/'D16_PROTOCOL.md'),script_sha256=sha(Path(__file__)),
        admit_gpu_prototype=fixtures['large']['guaranteed_empty_fraction']>=.20,
        scope='Guaranteed empty tile count only; no observed native instruction or timing reduction.')
    with (RAW/'d16-learning-bound.json').open('x',encoding='utf-8') as f:
        json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({f:{k:v[k] for k in ['guaranteed_empty_fraction','optimistic_empty_fraction']}
        for f,v in fixtures.items()},indent=2))
if __name__=='__main__':main()
