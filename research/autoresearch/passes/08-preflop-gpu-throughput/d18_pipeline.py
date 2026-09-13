"""Resource and logical-work screen for a two-kernel compact rank pipeline."""
import gzip,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    manifest=read(RAW/'d13-ranks-manifest.json');z=(RAW/'d13-fixed-ranks-v1.json.gz').read_bytes()
    assert hashlib.sha256(z).hexdigest()==manifest['compressed_sha256'];data=gzip.decompress(z)
    assert hashlib.sha256(data).hexdigest()==manifest['table_sha256'];table=json.loads(data)
    assert (table['samples'],table['classes'])==(1024,169)
    counts=[]
    for sample in range(1024):
        offset=sample*169;order=table['order'][offset:offset+169]
        assert sorted(order)==list(range(169))
        groups=set(zip(table['lower'][offset:offset+169],table['upper'][offset:offset+169]))
        spans=sorted(groups);assert spans[0][0]==0 and spans[-1][1]==169
        assert all(a[1]==b[0] for a,b in zip(spans,spans[1:]))
        counts.append(len(groups));assert counts[-1]==table['rows'][sample]['global_groups']
    total_groups=sum(counts);maximum=max(counts);static_bytes=(3*169*1024+1024)*4
    d11=read(RAW/'d11-work-census.json');fixtures={};sources={}
    for fixture in ['small','large']:
        f=d11['fixtures'][fixture];np_=f['players'];nt=f['terminals'];max_q=(np_+1)//2
        layout=read(RAW/f'c14-{fixture}-layout-v1.json');assert layout['batch']==32 and layout['players']==np_
        row_bytes=32*maximum*max_q*4
        choices=[n for n in [8192,16384,32768,65536] if min(n,nt)*row_bytes+static_bytes<=1<<30]
        tile=min(max(choices),nt) if choices else None
        scratch=tile*row_bytes if tile else None
        allocations=dict(max_groups=maximum,max_quadrature=max_q,rank_map_bytes=static_bytes,
            bytes_per_terminal=row_bytes,tile_capacity=tile,float_scratch_bytes=scratch,
            total_additional_bytes=scratch+static_bytes if tile else None,
            retained_device_bytes=layout['actual_device_bytes'],
            candidate_device_bytes=layout['actual_device_bytes']+scratch+static_bytes if tile else None)
        modes={}
        for label,old in f['modes'].items():
            hist=old['terminal_opponent_histogram'];before=after=gathers=writes=reads=0
            for o,n in enumerate(hist):
                if o<2:continue
                q=(o+2)//2
                before+=n*169*1024*(o+3*q*o+2*q)
                after+=n*(total_groups*(o+3*q*o)+169*1024*2*q)
                gathers+=n*total_groups*2*o*4
                writes+=n*total_groups*q*4
                reads+=n*169*1024*q*4
            assert before==old['logical_fp_operations']
            old_bytes=old['logical_cdf_gather_bytes'];new_bytes=gathers+writes+reads
            chunks=(nt+tile-1)//tile if tile else None;original_launches=np_*32
            producer=np_*32*chunks if tile else None
            modes[label]=dict(opponent_histogram=hist,source_operations_before=before,source_operations_after=after,
                source_arithmetic_reduction=1-after/before,logical_terminal_bytes_before=old_bytes,
                grouped_cdf_gather_bytes=gathers,product_write_bytes=writes,product_read_bytes=reads,
                logical_terminal_bytes_after=new_bytes,logical_terminal_traffic_reduction=1-new_bytes/old_bytes,
                unchanged_cdf_write_bytes=old['minimum_logical_cdf_write_bytes'],
                terminal_chunks=chunks,original_terminal_launches=original_launches,
                producer_launches=producer,consumer_launches=producer,
                additional_launches=2*producer-original_launches if tile else None)
        fits=tile is not None and allocations['candidate_device_bytes']<=23000*(1<<20)
        fixtures[fixture]=dict(players=np_,terminals=nt,allocations=allocations,modes=modes,resource_gate=fits)
        for name in [f'c14-{fixture}-layout-v1.json',f'd10-{fixture}-v1.json',f'd10-{fixture}-v1-witness-manifest.json',f'd10-{fixture}-v1-witness.bin.gz']:
            sources[name]=sha(RAW/name)
    large_gates={m:dict(arithmetic=x['source_arithmetic_reduction']>=.30,
        logical_traffic=x['logical_terminal_traffic_reduction']>=.10,
        launches=x['additional_launches'] is not None and x['additional_launches']<=32768)
        for m,x in fixtures['large']['modes'].items()}
    admitted=all(f['resource_gate'] for f in fixtures.values()) and all(all(x.values()) for x in large_gates.values())
    for name in ['d13-ranks-manifest.json','d13-fixed-ranks-v1.json.gz','d11-work-census.json']:
        sources[name]=sha(RAW/name)
    out=dict(fixtures=fixtures,large_gates=large_gates,admitted=admitted,
        rank_group_sum=total_groups,max_rank_groups=maximum,rank_group_counts=counts,sources=sources,
        protocol_sha256=sha(HERE/'D18_PROTOCOL.md'),script_sha256=sha(Path(__file__)),
        scope='Structural resource/logical-work screen only. No measured runtime or memory traffic.')
    with (RAW/'d18-pipeline.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps(dict(admitted=admitted,large_gates=large_gates,fixtures={n:dict(allocations=f['allocations'],modes=f['modes']) for n,f in fixtures.items()}),indent=2))
if __name__=='__main__':main()
