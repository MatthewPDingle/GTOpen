"""Optimistic empty-tile bound from preserved support and identity evidence."""
import array,collections,gzip,hashlib,itertools,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def decode(data,method):
    assert data[:8]==b'D10V1\0\0\0'
    if method=='struct':
        at=8
        def take(n):
            nonlocal at
            v=struct.unpack_from('<'+'I'*n,data,at);at+=4*n;return v
        def skip(n):
            nonlocal at
            at+=4*n;assert at<=len(data)
        done=lambda:at==len(data)
    else:
        words=array.array('I');words.frombytes(data[8:]);assert words.itemsize==4
        if sys.byteorder!='little':words.byteswap()
        at=0
        def take(n):
            nonlocal at
            v=words[at:at+n];at+=n;assert len(v)==n;return v
        def skip(n):
            nonlocal at
            at+=n;assert at<=len(words)
        done=lambda:at==len(words)
    np,nt=take(2);rows=[]
    for mode in (0,1):
        for player in range(np):
            m,p,n=take(3);assert (m,p)==(mode,player)
            ids=list(take(n));assert ids==sorted(set(ids))
            hist=[0]*9
            for _ in range(nt):
                k=take(1)[0];assert k==0 or 2<=k<np
                hist[k]+=1;skip(k)
            rows.append(dict(mode=mode,player=player,ids=ids,opponents=hist))
    assert done();return np,nt,rows
def maximum_empty(k):return 6-(k+31)//32
def main():
    sizes=[32]*5+[9]
    for k in range(1,170):
        necessary=min(n for n in range(1,7) if any(sum(c)>=k for c in itertools.combinations(sizes,n)))
        assert maximum_empty(k)==6-necessary
    d11=read(RAW/'d11-work-census.json');d10=read(RAW/'d10-verified.json');fixtures={};sources={}
    for fixture in ['small','large']:
        prefix='d10-'+fixture+'-v1'
        names=[prefix+'-witness.bin.gz',prefix+'-witness-manifest.json',prefix+'.json',f'c14-{fixture}-layout-v1.json']
        for n in names:sources[n]=sha(RAW/n)
        m=read(RAW/names[1]);packed=(RAW/names[0]).read_bytes()
        assert hashlib.sha256(packed).hexdigest()==m['compressed_sha256']
        data=gzip.decompress(packed);assert hashlib.sha256(data).hexdigest()==m['witness_sha256'] and len(data)==m['witness_bytes']
        assert sha(RAW/names[2])==m['output_sha256']
        np,nt,rows=decode(data,'struct');assert (np,nt,rows)==decode(data,'array')
        old=read(RAW/names[2]);layout=read(RAW/names[3]);assert old['arenas_unchanged'] and old['read_only']
        assert (layout['input'],layout['players'],layout['nodes'],layout['iteration'])==(old['input'],np,old['nodes'],old['iteration'])
        groups=layout['plan']['groups'];assert groups==d10['fixtures'][fixture]['cohorts']
        support={0:[0]*170,1:[0]*170};avg=[];learning_rows=0;max_id=0
        for row,raw in zip(rows,old['rows']):
            mode,p=row['mode'],row['player'];h=raw['unique_support_histogram'];active=raw['active_support_histogram']
            assert len(h)==len(active)==170 and h[0]==active[0]==0
            assert sum(active)==raw['active_slots']
            assert (mode,p,len(row['ids']))==(raw['mode'],raw['player'],raw['unique_distributions'])
            assert sum(row['opponents'][2:])==raw['positive_terminals']
            support[mode]=[a+b for a,b in zip(support[mode],h)]
            if mode==0:
                assert sum(h)==len(row['ids']) and row['ids']==list(range(len(row['ids'])))
                learning_rows+=len(row['ids'])
            else:
                assert sum(h)==raw['identity_upper_bound']-max_id
                max_id=raw['identity_upper_bound'];avg.append(set(row['ids']))
        union=set().union(*avg);assert union==set(range(max_id)) and sum(support[1])==max_id
        weights=collections.Counter(i for group in groups for i in set().union(*(avg[p] for p in group)))
        assert set(weights)==union
        allowance=sorted((maximum_empty(k) for k,n in enumerate(support[1]) for _ in range(n)),reverse=True)
        multiplicities=sorted(weights.values(),reverse=True)
        upper_check=sum(a*w for a,w in zip(allowance,multiplicities))
        # Layer-cake identity independently checks the maximal rearrangement.
        upper_layers=sum(min(sum(a>=x for a in allowance),sum(w>=y for w in multiplicities))
            for x in range(1,6) for y in range(1,len(groups)+1))
        assert upper_check==upper_layers
        modes={}
        for mode,label,count,upper in [(0,'learning',learning_rows,sum(n*maximum_empty(k) for k,n in enumerate(support[0]) if k)),
                                      (1,'check',sum(weights.values()),upper_check)]:
            assert count==d11['fixtures'][fixture]['modes'][label]['distinct_distribution_rows']
            modes[label]=dict(distinct_cdf_rows=count,all_tile_scans=count*6*1024,
                empty_tile_upper_bound=upper*1024,empty_fraction_upper_bound=upper/(count*6),
                support_histogram=support[mode],bound_kind='exact support-count sum' if mode==0 else 'optimistic support-to-cohort rearrangement')
        fixtures[fixture]=dict(players=np,iteration=old['iteration'],cohorts=groups,modes=modes,
            check_identity_multiplicity_histogram=dict(sorted(collections.Counter(weights.values()).items())))
    for n in ['d10-verified.json','d11-work-census.json']:sources[n]=sha(RAW/n)
    admit=all(v['empty_fraction_upper_bound']>=.20 for v in fixtures['large']['modes'].values())
    result=dict(fixtures=fixtures,admit_actual_inventory=admit,sources=sources,
        protocol_sha256=sha(HERE/'D15_PROTOCOL.md'),script_sha256=sha(Path(__file__)),
        independent_decoders_and_layer_bound_agree=True,exhaustive_capacity_cases=169,
        scope='Upper bound only, not actual zero tiles, native work saved or GPU timing.')
    with (RAW/'d15-zero-bound.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(admit_actual_inventory=admit,bounds={f:{m:v['empty_fraction_upper_bound'] for m,v in x['modes'].items()} for f,x in fixtures.items()}),indent=2))
if __name__=='__main__':main()
