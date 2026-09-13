"""Independent bit-vector and sorted-run audit of the warp census."""
import gzip,hashlib,itertools,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rec=read(RAW/'d14-warp-inventory-v1-exit.json');r=read(RAW/'d14-warp-census.json')
    assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
    assert rec['source_diff_sha256']==hashlib.sha256(b'').hexdigest()
    for p,h in rec['inputs'].items():assert sha(Path(p))==h,p
    for p,h in rec['solver_source_files'].items():assert sha(LAB/p)==h,p
    for p,h in r['sources'].items():assert sha(RAW/p)==h,p
    assert r['protocol_sha256']==sha(HERE/'D14_PROTOCOL.md')
    assert r['script_sha256']==sha(HERE/'d14_warp_census.py')
    assert not subprocess.check_output(['git','diff','HEAD','--','crates'],cwd=LAB)
    m=read(RAW/'d13-ranks-manifest.json');z=(RAW/'d13-fixed-ranks-v1.json.gz').read_bytes()
    assert hashlib.sha256(z).hexdigest()==m['compressed_sha256']
    data=gzip.decompress(z);assert hashlib.sha256(data).hexdigest()==m['table_sha256']
    t=json.loads(data);assert len(r['rows'])==6144
    totals=[0]*8;group_count=0;lane_count=0
    for row in r['rows']:
        s,w=row['sample'],row['warp'];assert 0<=s<1024 and 0<=w<6
        assert row is r['rows'][s*6+w]
        start=s*169+w*32;end=min(s*169+169,start+32)
        pairs=list(zip(t['lower'][start:end],t['upper'][start:end]))
        elected=[key for key,_ in itertools.groupby(sorted(pairs))]
        assert row['lanes']==len(pairs) and row['leaders']==len(elected)>0
        lane_count+=len(pairs);group_count+=len(elected)
        for c in (0,1):
            word_bits=sum(1<<n for n in range(170) if any(k[c]==n for k in pairs))
            selected_bits=0
            for k in elected:selected_bits|=1<<k[c]
            assert word_bits==selected_bits
            assert row['loads'][c]['words_before']==row['loads'][c]['words_after']==word_bits.bit_count()
            for a in range(8):
                original=0;after=0
                for k in pairs:original|=1<<((a+k[c])//8)
                for k in elected:after|=1<<((a+k[c])//8)
                assert original==after
                count=original.bit_count();totals[a]+=count
                assert count==row['loads'][c]['sectors_before'][a]==row['loads'][c]['sectors_after'][a]
    assert (lane_count,group_count)==(173056,105329)==(r['lanes'],r['leaders'])
    assert totals==r['sectors_per_opponent_by_offset']['before']==r['sectors_per_opponent_by_offset']['after']
    d11=read(RAW/'d11-work-census.json');d13=read(RAW/'d13-verified.json')
    for fixture,modes in r['fixtures'].items():
        for mode,v in modes.items():
            h=d11['fixtures'][fixture]['modes'][mode]['terminal_opponent_histogram']
            ops=sum(h[o]*6144*(o+3*((o+2)//2)*o+2*((o+2)//2)) for o in range(2,9))
            loads=sum(h[o]*6144*2*o for o in range(2,9))
            assert ops==v['original_warp_source_slots_before']==v['original_warp_source_slots_after']
            assert loads==v['original_warp_gather_slots_before']==v['original_warp_gather_slots_after']
            assert v['sector_reduction_by_offset']==[0.0]*8 and v['warp_source_reduction']==0
            d=d13['schedules']['original_warps']['fixtures'][fixture][mode]
            assert v['active_lane_source_before']==d['source_operations_before']
            assert v['active_lane_source_after']==d['optimistic_source_operations_after']
            assert v['active_lane_source_reduction']==d['source_arithmetic_reduction']
    assert r['admitted'] is False
    out=dict(verified=True,admitted=False,retained=False,
        status='Warp-local sharing rejected by execution-model screen',
        original_warp_source_reduction=0.0,requested_sector_reduction=0.0,
        sample_warp_cases=6144,float_base_alignments=8,loads_per_case=2,
        leaders=group_count,active_hand_sample_tasks=lane_count,
        independent_sector_word_and_election_checks=True,fixtures=r['fixtures'],
        protocol_sha256=r['protocol_sha256'],census_sha256=sha(RAW/'d14-warp-census.json'),
        runtime_sources_unchanged=True,
        scope='Analytical source/architecture model; not timing or hardware counters. Secondary compiler and register effects not excluded.')
    dest=RAW/'d14-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k!='fixtures'},indent=2))
if __name__=='__main__':main()
