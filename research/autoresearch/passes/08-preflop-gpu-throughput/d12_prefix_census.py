"""D12 bounded exact ordered-prefix reuse census; host-only, immutable inputs."""
import array,collections,gzip,hashlib,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; RAW=HERE/'raw'
BUDGET=512*1024**2; RESERVED=16*1024**2; ENTRY=32*169*2*4; CAP=(BUDGET-RESERVED)//ENTRY

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(b):return hashlib.sha256(b).hexdigest()

def records(data):
    assert data[:8]==b'D10V1\0\0\0'
    np,nt=struct.unpack_from('<2I',data,8);at=16
    for mode in [0,1]:
        for seat in range(np):
            m,p,n=struct.unpack_from('<3I',data,at);assert (m,p)==(mode,seat);at+=12+4*n
            pairs=collections.Counter();hist=[0]*9
            for _ in range(nt):
                k=struct.unpack_from('<I',data,at)[0];at+=4
                assert k==0 or 2<=k<np;hist[k]+=1
                if k in [2,3]:pairs[struct.unpack_from('<2I',data,at)]+=1
                at+=4*k
            yield mode,seat,n,hist,pairs
    assert at==len(data)

def words(data):
    a=array.array('I');a.frombytes(data[8:]);assert a.itemsize==4
    if sys.byteorder!='little':a.byteswap()
    np,nt=a[:2];at=2
    for index in range(2*np):
        mode,seat,n=a[at:at+3];assert (mode,seat)==divmod(index,np);at+=3+n
        pairs={};hist=[0]*9
        for _ in range(nt):
            k=a[at];hist[k]+=1
            if k==2 or k==3:
                key=(a[at+1],a[at+2]);pairs[key]=pairs.get(key,0)+1
            at+=1+k
        yield mode,seat,n,hist,pairs
    assert at==len(a)

def summarize(counters,base):
    groups=[];saved_ops=0;saved_bytes=0
    for c in counters:
        selected=sorted(((key,n) for key,n in c.items() if n>=4),key=lambda z:(-z[1],z[0]))[:CAP]
        nk=len(selected);uses=sum(n for _,n in selected)
        ops=sum(14*(n-1) for _,n in selected)
        traffic=sum(4*(2*n-6) for _,n in selected)
        # Independent gross-original minus builder and consumer calculation.
        assert ops==14*uses-14*nk
        assert traffic==4*(4*uses-(4*nk+2*nk+2*uses))
        assert nk*ENTRY+RESERVED<=BUDGET
        saved_ops+=ops*169*1024;saved_bytes+=traffic*169*1024
        groups.append(dict(unique_pairs=len(c),eligible_pairs=sum(n>=4 for n in c.values()),selected_pairs=nk,
            selected_uses=uses,payload_bytes=nk*ENTRY,selected_keys_sha256=sha(json.dumps(selected,separators=(',',':')).encode())))
    return dict(groups=groups,saved_source_operations=saved_ops,source_arithmetic_reduction=saved_ops/base['logical_fp_operations'],
        saved_logical_bytes=saved_bytes,logical_terminal_traffic_reduction=saved_bytes/base['logical_cdf_gather_bytes'])

def main():
    census=read(RAW/'d11-work-census.json');d10=read(RAW/'d10-verified.json');sources={};fixtures={}
    for fixture in ['small','large']:
        name=f'd10-{fixture}-v1';path=RAW/(name+'-witness.bin.gz');manifest=RAW/(name+'-witness-manifest.json')
        m=read(manifest);compressed=path.read_bytes();assert sha(compressed)==m['compressed_sha256']
        data=gzip.decompress(compressed);assert sha(data)==m['witness_sha256'] and len(data)==m['witness_bytes']
        for p in [path,manifest]:sources[p.name]=sha(p.read_bytes())
        np,nt=struct.unpack_from('<2I',data,8);assert np==census['fixtures'][fixture]['players'] and nt==d10['fixtures'][fixture]['terminals']
        old=read(RAW/(name+'.json'));current=[];average=[];hists=[[0]*9,[0]*9]
        for a,b in zip(records(data),words(data),strict=True):
            assert a==b
            mode,seat,n,hist,counter=a;r=old['rows'][mode*np+seat]
            assert (mode,seat,n)==(r['mode'],r['player'],r['unique_distributions'])
            assert sum(hist)==nt and sum(hist[2:])==r['positive_terminals'] and sum(o*hist[o] for o in range(2,9))==r['weighted_terminals']
            assert sum(counter.values())==hist[2]+hist[3]
            hists[mode]=[x+y for x,y in zip(hists[mode],hist)]
            (current if mode==0 else average).append(counter)
        grouped=[]
        for seats in d10['fixtures'][fixture]['cohorts']:
            c=collections.Counter()
            for seat in seats:c.update(average[seat])
            grouped.append(c)
        modes={}
        for mode,label,cs in [(0,'learning',current),(1,'check',grouped)]:
            base=census['fixtures'][fixture]['modes'][label];assert hists[mode]==base['terminal_opponent_histogram']
            modes[label]=summarize(cs,base)
        fixtures[fixture]=modes
        print(json.dumps(dict(fixture=fixture,modes=modes)),flush=True)
        del data,current,average,grouped
    for name in ['d11-work-census.json','d10-verified.json']:
        sources[name]=sha((RAW/name).read_bytes())
    admitted=all(v['source_arithmetic_reduction']>=.2 and v['logical_terminal_traffic_reduction']>=.1 for v in fixtures['large'].values())
    result=dict(admitted=admitted,independent_pair_counters_agree=True,budget_bytes=BUDGET,reserved_bytes=RESERVED,
        bytes_per_pair=ENTRY,pair_capacity=CAP,fixtures=fixtures,sources=sources,
        protocol_sha256=sha((HERE/'D12_PROTOCOL.md').read_bytes()),script_sha256=sha(Path(__file__).read_bytes()),
        status='Admits separately qualified prototype' if admitted else 'Rejected by registered work-reduction gate',
        scope='Optimistic exact snapshot reuse counts, not runtime, DRAM traffic or convergence. Selection overhead excluded. No production mutation.')
    dest=RAW/'d12-prefix-census.json'
    if dest.exists():assert read(dest)==result
    else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(admitted=admitted,status=result['status'])),flush=True)
if __name__=='__main__':main()
