"""Static exact prefix requirements; no GPU or solver mutation."""
import gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=read(RAW/'d13-ranks-manifest.json');compressed=(RAW/'d13-fixed-ranks-v1.json.gz').read_bytes()
    assert hashlib.sha256(compressed).hexdigest()==m['compressed_sha256'];data=gzip.decompress(compressed)
    assert hashlib.sha256(data).hexdigest()==m['table_sha256'];r=json.loads(data)
    needed=[];prefix_maps=[];hand_maps=[];offsets=[0]
    for sample in range(1024):
        at=sample*169;lo=r['lower'][at:at+169];hi=r['upper'][at:at+169];order=r['order'][at:at+169]
        assert sorted(order)==list(range(169));groups=sorted(set(zip(lo,hi)))
        assert groups[0][0]==0 and groups[-1][1]==169 and all(x[1]==y[0] for x,y in zip(groups,groups[1:]))
        boundaries=sorted(set(lo+hi));assert len(boundaries)==len(groups)+1
        packed={p:i for i,p in enumerate(boundaries)};pm=[packed.get(i,0xffffffff) for i in range(170)]
        hm=[packed[l] for l in lo]
        for h in range(169):assert boundaries[hm[h]]==lo[h] and boundaries[hm[h]+1]==hi[h]
        needed.append(len(boundaries));prefix_maps.extend(pm);hand_maps.extend(hm);offsets.append(offsets[-1]+len(boundaries))
    windows=[sum(needed[start:start+32]) for start in range(1024)];stride=max(windows)
    static_bytes=(len(prefix_maps)+len(hand_maps)+len(offsets))*4
    maps=dict(prefix=prefix_maps,hand_group=hand_maps,sample_offsets=offsets,row_stride=stride)
    encoded=json.dumps(maps,separators=(',',':')).encode();mapfile=RAW/'d19-static-cdf-maps.json.gz'
    packed=gzip.compress(encoded,mtime=0)
    if mapfile.exists():assert mapfile.read_bytes()==packed
    else:mapfile.write_bytes(packed)
    fixtures={}
    for fixture in ['small','large']:
        old=read(RAW/f'c14-{fixture}-layout-v1.json');assert old['batch']==32
        capacity=old['plan']['capacity'];before=old['buffer_bytes']['d_mw_cdf'];assert before==capacity*32*170*4
        after=capacity*stride*4;total=old['actual_device_bytes']-before+after+static_bytes
        steady=total+256*1024**2;overlap=old['actual_device_bytes']+after+static_bytes+256*1024**2
        fixtures[fixture]=dict(capacity=capacity,cdf_bytes_before=before,cdf_bytes_after=after,cdf_allocation_reduction=1-after/before,static_bytes=static_bytes,final_device_bytes=total,final_with_reserve_bytes=steady,overlap_with_reserve_bytes=overlap,overlap_fits=overlap<=23000000000,final_fits=steady<=23000000000,u32_elements_fit=capacity*stride<=2**32-1)
    stores_before=1024*170;stores_after=sum(needed);reduction=1-stores_after/stores_before
    gates=dict(allocation=all(x['cdf_allocation_reduction']>=.3 for x in fixtures.values()),logical_stores=reduction>=.3,static_maps=static_bytes<=4*1024**2,final_budget=all(x['final_fits'] for x in fixtures.values()),u32_elements=all(x['u32_elements_fit'] for x in fixtures.values()))
    out=dict(admitted=all(gates.values()),gates=gates,required_prefixes_per_sample=needed,row_stride=stride,max_window_starts=[i for i,n in enumerate(windows) if n==stride],static_bytes=static_bytes,logical_float_stores_before=stores_before,logical_float_stores_after=stores_after,logical_store_reduction=reduction,fixtures=fixtures,maps_sha256=hashlib.sha256(encoded).hexdigest(),maps_compressed_sha256=sha(mapfile),maps_bytes=len(encoded),protocol_sha256=sha(HERE/'D19_PROTOCOL.md'),script_sha256=sha(Path(__file__)),sources={n:sha(RAW/n) for n in ['d13-ranks-manifest.json','d13-fixed-ranks-v1.json.gz','c14-small-layout-v1.json','c14-large-layout-v1.json']})
    file=RAW/'d19-static-cdf.json'
    if file.exists():assert read(file)==out
    else:file.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k not in ['required_prefixes_per_sample','sources']},indent=2))
if __name__=='__main__':main()
