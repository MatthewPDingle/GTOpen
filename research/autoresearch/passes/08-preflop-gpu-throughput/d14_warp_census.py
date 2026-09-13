"""Bounded architecture-model screen, not a GPU benchmark."""
import gzip, hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
RAW=HERE/'raw'

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def census(keys):
    rows=[]
    for start in range(0,len(keys),32):
        lanes=keys[start:start+32]; first={}
        for lane,key in enumerate(lanes): first.setdefault(key,lane)
        leaders=[lanes[i] for i in first.values()]
        # Independent election: keep the last matching lane, without a set.
        last=[key for i,key in enumerate(lanes) if key not in lanes[i+1:]]
        assert sorted(leaders)==sorted(last) and leaders
        loads=[]
        for component in (0,1):
            words=set(k[component] for k in lanes)
            chosen=set(k[component] for k in leaders)
            assert words==chosen==set(k[component] for k in last)
            before=[];after=[]
            for offset in range(0,32,4):
                sectors=set((offset+4*w)//32 for w in words)
                picked=set((offset+4*w)//32 for w in chosen)
                assert sectors==picked
                before.append(len(sectors));after.append(len(picked))
            loads.append(dict(words_before=len(words),words_after=len(chosen),
                              sectors_before=before,sectors_after=after))
        rows.append(dict(lanes=len(lanes),leaders=len(leaders),loads=loads))
    return rows

def main():
    sources=['d13-fixed-ranks-v1.json.gz','d13-ranks-manifest.json',
             'd13-verified.json','d11-work-census.json']
    m=read(RAW/sources[1]); packed=(RAW/sources[0]).read_bytes()
    assert hashlib.sha256(packed).hexdigest()==m['compressed_sha256']
    data=gzip.decompress(packed)
    assert hashlib.sha256(data).hexdigest()==m['table_sha256']
    t=json.loads(data); assert (t['samples'],t['classes'])==(1024,169)
    synthetic=[[(0,169)]*169,[(i,i+1) for i in range(169)],
               [(i%2*80,i%2*80+80) for i in range(169)],
               [(0,33) if i<33 else (33,169) for i in range(169)]]
    for keys in synthetic: assert len(census(keys))==6
    rows=[]
    for sample in range(1024):
        start=sample*169
        keys=list(zip(t['lower'][start:start+169],t['upper'][start:start+169]))
        rr=census(keys)
        assert [r['lanes'] for r in rr]==[32]*5+[9]
        assert sum(r['leaders'] for r in rr)==t['rows'][sample]['warp_groups']
        rows.extend(dict(sample=sample,warp=i,**r) for i,r in enumerate(rr))
    full=sum(r['lanes'] for r in rows); leaders=sum(r['leaders'] for r in rows)
    d13=read(RAW/'d13-verified.json')['schedules']['original_warps']
    assert leaders==d13['groups'] and full==173056
    # Per CDF opponent and base offset; no cross-instruction coalescing.
    sectors={which:[sum(r['loads'][c]['sectors_'+which][a]
               for r in rows for c in (0,1)) for a in range(8)]
             for which in ('before','after')}
    fixtures={}
    for fixture,f in read(RAW/'d11-work-census.json')['fixtures'].items():
        modes={}
        for mode,v in f['modes'].items():
            hist=v['terminal_opponent_histogram']; warp_ops=0;lane_before=0;lane_after=0;gathers=0
            for o,n in enumerate(hist[2:],2):
                q=(o+2)//2; shared=o+3*q*o;acc=2*q
                warp_ops+=n*len(rows)*(shared+acc)
                lane_before+=n*full*(shared+acc)
                lane_after+=n*(leaders*shared+full*acc)
                gathers+=n*len(rows)*2*o
            assert lane_before==v['logical_fp_operations']
            assert lane_after==d13['fixtures'][fixture][mode]['optimistic_source_operations_after']
            modes[mode]=dict(original_warp_source_slots_before=warp_ops,
                original_warp_source_slots_after=warp_ops,warp_source_reduction=0.0,
                original_warp_gather_slots_before=gathers,original_warp_gather_slots_after=gathers,
                sector_reduction_by_offset=[1-b/a for a,b in zip(sectors['before'],sectors['after'])],
                active_lane_source_before=lane_before,active_lane_source_after=lane_after,
                active_lane_source_reduction=1-lane_after/lane_before)
        fixtures[fixture]=modes
    admitted=all(v['warp_source_reduction']>=.10 or min(v['sector_reduction_by_offset'])>=.10
                 for v in fixtures['large'].values())
    out=dict(sources={s:sha(RAW/s) for s in sources},protocol_sha256=sha(HERE/'D14_PROTOCOL.md'),
        script_sha256=sha(Path(__file__)),samples=1024,classes=169,warps=len(rows),
        lanes=full,leaders=leaders,synthetic_cases=len(synthetic),rows=rows,
        sectors_per_opponent_by_offset=sectors,fixtures=fixtures,admitted=admitted,
        scope='Source/architecture model; no compiled instruction, runtime, cache-miss or DRAM measurement.')
    dest=RAW/'d14-warp-census.json'
    with dest.open('x',encoding='utf-8') as f:json.dump(out,f,separators=(',',':'));f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
