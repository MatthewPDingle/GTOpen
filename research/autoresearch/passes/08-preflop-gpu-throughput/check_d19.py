"""Independent run-boundary, compact-address and allocation audit."""
import gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    rec=read(RAW/'d19-static-cdf-v1-exit.json');r=read(RAW/'d19-static-cdf.json')
    assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
    for p,h in rec['inputs'].items():assert sha(p)==h,p
    for p,h in r['sources'].items():assert sha(RAW/p)==h,p
    assert sha(HERE/'D19_PROTOCOL.md')==r['protocol_sha256'] and sha(HERE/'d19_static_cdf.py')==r['script_sha256']
    packed=(RAW/'d19-static-cdf-maps.json.gz').read_bytes();assert hashlib.sha256(packed).hexdigest()==r['maps_compressed_sha256']
    raw=gzip.decompress(packed);assert len(raw)==r['maps_bytes'] and hashlib.sha256(raw).hexdigest()==r['maps_sha256'];maps=json.loads(raw)
    t=json.loads(gzip.decompress((RAW/'d13-fixed-ranks-v1.json.gz').read_bytes()))
    required=[];offsets=[0];all_pm=[];all_hm=[]
    for s in range(1024):
        order=t['order'][s*169:(s+1)*169];assert sorted(order)==list(range(169))
        pm=[0xffffffff]*170;hm=[-1]*169;boundaries=[0];pm[0]=0;rank=0
        while rank<169:
            h=order[rank];at=s*169+h;lower,upper=t['lower'][at],t['upper'][at];assert lower==rank and lower<upper<=169
            group=len(boundaries)-1
            for pos in range(lower,upper):
                hand=order[pos];idx=s*169+hand;assert (t['lower'][idx],t['upper'][idx])==(lower,upper);hm[hand]=group
            rank=upper;boundaries.append(rank);pm[rank]=group+1
        assert boundaries[-1]==169 and len(set(boundaries))==len(boundaries)
        for h,g in enumerate(hm):
            assert 0<=g<len(boundaries)-1
            assert (boundaries[g],boundaries[g+1])==(t['lower'][s*169+h],t['upper'][s*169+h])
        required.append(len(boundaries));offsets.append(offsets[-1]+len(boundaries));all_pm.extend(pm);all_hm.extend(hm)
    assert maps['prefix']==all_pm and maps['hand_group']==all_hm and maps['sample_offsets']==offsets
    assert required==r['required_prefixes_per_sample'] and sum(required)==59590
    # Every legal start/count, including partial final batches and unaligned starts.
    windows=[];cases=0
    for start in range(1024):
        for count in range(1,min(32,1024-start)+1):
            used=offsets[start+count]-offsets[start];windows.append((used,start,count));cases+=1
            assert used<=maps['row_stride']
            for sample in range(start,start+count):
                first=offsets[sample]-offsets[start];last=offsets[sample+1]-offsets[start]-1
                assert 0<=first<=last<used
                if sample>start:
                    previous_end=offsets[sample-1]-offsets[start]+required[sample-1]-1
                    assert first==previous_end+1
    stride=max(x[0] for x in windows);assert stride==maps['row_stride']==r['row_stride']==2160
    assert sorted(set(start for n,start,count in windows if n==stride))==r['max_window_starts']==[237]
    static=(1024*170+1024*169+1025)*4;assert static==r['static_bytes']==1392644
    before=1024*170;after=offsets[-1];reduction=(before-after)/before
    assert before==r['logical_float_stores_before'] and after==r['logical_float_stores_after']
    assert abs(reduction-r['logical_store_reduction'])<1e-15
    fixtures={}
    for name in ['small','large']:
        old=read(RAW/f'c14-{name}-layout-v1.json');x=r['fixtures'][name];cap=old['plan']['capacity']
        original=cap*32*170*4;compact=cap*stride*4;final=old['actual_device_bytes']-original+compact+static
        overlap=old['actual_device_bytes']+compact+static+268435456
        expected=dict(capacity=cap,cdf_bytes_before=original,cdf_bytes_after=compact,cdf_allocation_reduction=1-compact/original,static_bytes=static,final_device_bytes=final,final_with_reserve_bytes=final+268435456,overlap_with_reserve_bytes=overlap,overlap_fits=overlap<=23000000000,final_fits=final+268435456<=23000000000,u32_elements_fit=cap*stride<=2**32-1)
        assert x==expected and old['buffer_bytes']['d_mw_cdf']==original
        for row in [0,1,cap//2,cap-1]:
            base=row*stride;end=base+stride-1;assert 0<=base<=end<cap*stride<=2**32-1
            if row<cap-1:assert end<(row+1)*stride
        fixtures[name]=expected
    gates=dict(allocation=all(x['cdf_allocation_reduction']>=.3 for x in fixtures.values()),logical_stores=reduction>=.3,static_maps=static<=4*1024**2,final_budget=all(x['final_fits'] for x in fixtures.values()),u32_elements=all(x['u32_elements_fit'] for x in fixtures.values()))
    assert gates==r['gates'] and all(gates.values())==r['admitted']
    out=dict(verified=True,admitted=r['admitted'],retained=False,status='Static rank-boundary CDF layout admits GPU prototype' if r['admitted'] else 'Static rank-boundary CDF layout declined',row_stride=stride,logical_store_reduction=reduction,static_bytes=static,windows_checked=cases,hand_boundaries_checked=1024*169,fixtures=fixtures,independent_partition_and_address_audit=True,census_sha256=sha(RAW/'d19-static-cdf.json'),protocol_sha256=r['protocol_sha256'],scope='Fixed sampled-rank storage and logical-write counts only; GPU exactness and timing remain unqualified. Large old/new CDF overlap exceeds budget; fresh private construction is required.')
    dest=RAW/'d19-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
