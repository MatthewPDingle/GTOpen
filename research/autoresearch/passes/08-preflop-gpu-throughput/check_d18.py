"""Independent witness decoding, rank partition and pipeline capacity audit."""
import gzip,hashlib,json
from pathlib import Path
from d11_work_census import decode_struct,decode_array
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rec=read(RAW/'d18-pipeline-v1-exit.json');r=read(RAW/'d18-pipeline.json')
    assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
    assert rec['source_diff_sha256']==hashlib.sha256(b'').hexdigest()
    for p,h in rec['inputs'].items():assert sha(Path(p))==h
    for p,h in rec['solver_source_files'].items():assert sha(LAB/p)==h
    for p,h in r['sources'].items():assert sha(RAW/p)==h
    assert r['protocol_sha256']==sha(HERE/'D18_PROTOCOL.md') and r['script_sha256']==sha(HERE/'d18_pipeline.py')
    manifest=read(RAW/'d13-ranks-manifest.json');z=(RAW/'d13-fixed-ranks-v1.json.gz').read_bytes()
    assert hashlib.sha256(z).hexdigest()==manifest['compressed_sha256'];data=gzip.decompress(z)
    assert hashlib.sha256(data).hexdigest()==manifest['table_sha256'];t=json.loads(data);group_counts=[]
    for sample in range(1024):
        start=sample*169;order=t['order'][start:start+169];assert sorted(order)==list(range(169))
        pairs=list(zip(t['lower'][start:start+169],t['upper'][start:start+169]));groups={}
        for hand,pair in enumerate(pairs):groups.setdefault(pair,[]).append(hand)
        spans=sorted(groups);assert spans[0][0]==0 and spans[-1][1]==169
        for lo,hi in spans:
            assert 0<=lo<hi<=169 and sorted(order[lo:hi])==groups[(lo,hi)]
        assert all(a[1]==b[0] for a,b in zip(spans,spans[1:]))
        group_counts.append(len(groups))
    assert group_counts==r['rank_group_counts'] and sum(group_counts)==r['rank_group_sum'] and max(group_counts)==r['max_rank_groups']
    static_bytes=(len(t['lower'])+len(t['upper'])+len(t['order'])+len(group_counts))*4
    d11=read(RAW/'d11-work-census.json');d13=read(RAW/'d13-verified.json');summary={};all_resources=True;large_gates={}
    for fixture,f in r['fixtures'].items():
        name=f'd10-{fixture}-v1';m=read(RAW/(name+'-witness-manifest.json'))
        z=(RAW/(name+'-witness.bin.gz')).read_bytes();assert hashlib.sha256(z).hexdigest()==m['compressed_sha256']
        data=gzip.decompress(z);assert hashlib.sha256(data).hexdigest()==m['witness_sha256']
        decoded=decode_array(data);assert decoded==decode_struct(data);players,terminals,rows=decoded
        assert (players,terminals)==(f['players'],f['terminals']);a=f['allocations'];max_q=max((o+2)//2 for o in range(2,players))
        row_bytes=4*32*max(group_counts)*max_q;capacity=((1<<30)-static_bytes)//row_bytes
        power=min(65536,1<<(capacity.bit_length()-1));tile=min(power,terminals) if power>=8192 else None
        assert a['tile_capacity']==tile and a['bytes_per_terminal']==row_bytes and a['max_quadrature']==max_q
        assert a['rank_map_bytes']==static_bytes and a['max_groups']==max(group_counts)
        layout=read(RAW/f'c14-{fixture}-layout-v1.json');extra=row_bytes*tile+static_bytes if tile else None
        assert a['float_scratch_bytes']==tile*row_bytes and a['total_additional_bytes']==extra
        assert a['retained_device_bytes']==layout['actual_device_bytes']
        assert a['candidate_device_bytes']==layout['actual_device_bytes']+extra
        fits=tile is not None and extra<=1<<30 and a['candidate_device_bytes']<=23000*(1<<20)
        assert fits==f['resource_gate'];all_resources&=fits
        details={}
        for mode,label in [(0,'learning'),(1,'check')]:
            x=f['modes'][label];hist=[sum(row['opponents'][i] for row in rows if row['mode']==mode) for i in range(9)]
            assert hist==x['opponent_histogram']==d11['fixtures'][fixture]['modes'][label]['terminal_opponent_histogram']
            assert sum(hist)==terminals*players
            before=after=old_bytes=gathers=writes=reads=0
            for opponents in range(2,9):
                n=hist[opponents];q=(opponents+2)//2
                per_group=sum(1+sum(3 for _ in range(q)) for _ in range(opponents))
                accumulation=sum(2 for _ in range(q))
                for groups in group_counts:
                    before+=n*169*(per_group+accumulation)
                    after+=n*(groups*per_group+169*accumulation)
                    old_bytes+=n*169*sum(8 for _ in range(opponents))
                    gathers+=n*groups*sum(8 for _ in range(opponents))
                    writes+=n*groups*sum(4 for _ in range(q));reads+=n*169*sum(4 for _ in range(q))
            for k,v in [('source_operations_before',before),('source_operations_after',after),('logical_terminal_bytes_before',old_bytes),
                        ('grouped_cdf_gather_bytes',gathers),('product_write_bytes',writes),('product_read_bytes',reads)]:assert x[k]==v,k
            assert after==d13['schedules']['compact_groups']['fixtures'][fixture][label]['optimistic_source_operations_after']
            net=gathers+writes+reads;assert x['logical_terminal_bytes_after']==net
            arithmetic=1-after/before;traffic=1-net/old_bytes
            assert arithmetic==x['source_arithmetic_reduction'] and traffic==x['logical_terminal_traffic_reduction']
            chunks=len(range(0,terminals,tile));producer=sum(1 for p in range(players) for sample in range(0,1024,32) for term in range(0,terminals,tile))
            original=players*len(range(0,1024,32));additional=producer*2-original
            assert x['terminal_chunks']==chunks and x['producer_launches']==x['consumer_launches']==producer
            assert x['original_terminal_launches']==original and x['additional_launches']==additional
            assert x['unchanged_cdf_write_bytes']==d11['fixtures'][fixture]['modes'][label]['minimum_logical_cdf_write_bytes']
            if fixture=='large':large_gates[label]=dict(arithmetic=arithmetic>=.30,logical_traffic=traffic>=.10,launches=additional<=32768)
            details[label]=dict(source_arithmetic_reduction=arithmetic,logical_traffic_reduction=traffic,additional_launches=additional)
        summary[fixture]=dict(additional_bytes=extra,tile_capacity=tile,planned_device_bytes=a['candidate_device_bytes'],modes=details)
    assert large_gates==r['large_gates'];admitted=all_resources and all(all(g.values()) for g in large_gates.values());assert admitted==r['admitted']
    out=dict(verified=True,admitted=admitted,retained=False,
        status='Two-kernel rank pipeline admits GPU prototype' if admitted else 'Two-kernel rank pipeline rejected by resource/work gate',
        fixtures=summary,independent_binary_and_rank_partition_audit=True,
        census_sha256=sha(RAW/'d18-pipeline.json'),protocol_sha256=r['protocol_sha256'],
        scope='Planned allocation/launch and source-work counts. Not measured GPU timing or DRAM traffic.')
    dest=RAW/'d18-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
