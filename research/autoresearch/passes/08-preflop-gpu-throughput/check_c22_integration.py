"""Audit full solver qualification and declared allocations before any timing."""
import hashlib,json,re,subprocess
from pathlib import Path
from check_d09 import entries
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    r=read(RAW/'c22-numerical-v1-exit.json');assert r['returncode']==0 and r['reason'] is None and r['seconds']<=300
    log=(RAW/'c22-numerical-v1.log').read_text(encoding='utf-8');assert '9 passed; 0 failed; 1 ignored' in log
    for p,h in r['inputs'].items():assert sha(p)==h,p
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c22-v2-source-map.json').items()}
    for p,h in r['solver_source_files'].items():
        if p in mapping:assert sha(HERE/mapping[p]['archive'])==mapping[p]['sha256']==h,p
        else:assert hashlib.sha256(subprocess.check_output(['git','show',r['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    folder=RAW/'c22-integrated-v1';source=(folder/'candidate.cu').read_text();control=(folder/'control.cu').read_text()
    helper=(HERE/'artifacts/c22-v2/src/preflop/gpu/rank_pipeline.cu').read_text()
    assert source.startswith(control+helper)
    assert sha(folder/'control.ptx')==sha(RAW/'r03-compiler-v2/exact-candidate.ptx')
    a=entries((folder/'control.ptx').read_text());b=entries((folder/'candidate.ptx').read_text())
    assert len(a)==20 and all(b[k]==v for k,v in a.items())
    assert set(b)-set(a)=={'pf_rank_pipeline_producer','pf_rank_pipeline_consumer'}
    p=source[source.index('extern "C" __global__ void pf_rank_pipeline_producer('):source.index('extern "C" __global__ void pf_rank_pipeline_consumer(')]
    c=source[source.index('extern "C" __global__ void pf_rank_pipeline_consumer('):]
    original=control[control.index('extern "C" __global__ void pf_exact_reuse_terminal('):]
    metadata=original[original.index('    __shared__ float prob;'):original.index('    for (u32 h = threadIdx.x;')]
    metadata=metadata.replace('terminal_prob[blockIdx.x]','terminal_prob[terminal]').replace('compact_slots[(size_t)p * union_slots + global_slot]','compact_slots[(cohort ? 0 : (size_t)p * union_slots) + global_slot]')
    assert metadata in p and p.count('__syncthreads')==1
    assert '__syncthreads' not in c and '__shared__' not in c
    tail=original[original.index('        float increment ='):original.index('\n    }',original.index('        float increment ='))]
    assert tail in c
    for o in range(2,9):
        q=(o+2)//2
        assert f'case {o}: pf_rank_produce<{q},{o}>(h,opponent_bases,cdf,gl,gu,gc,sample_start,sample_count,groups,quadratures,product);break;' in p
        assert f'case {o}: sum=pf_rank_consume<{q}>(h,hg,sample_start,sample_count,groups,quadratures,0.f,product);break;' in c
    assert '__popc((unsigned int)lv)-1' in c
    resources=read(folder/'resources.json');assert [x['kernel'] for x in resources]==['producer','consumer']
    gates=dict(no_spills=all(x['local_bytes']==0 for x in resources),bounded_registers=all(x['registers']<=128 for x in resources),shared_metadata_only=[x['shared_bytes'] for x in resources]==[44,0])
    exe=LAB/'target/c22-benchmark-frozen.exe';frozen=sha(exe);fixtures={}
    for fixture in ['small','large']:
        name=f'c22-{fixture}-layout-v1';rr=read(RAW/(name+'-exit.json'))
        assert rr['returncode']==0 and rr['reason'] is None and rr['seconds']<=180
        assert rr['exe_sha256']==frozen and rr['solver_source_files']==r['solver_source_files']
        for path,h in rr['inputs'].items():assert sha(path)==h,path
        x=read(RAW/(name+'.json'));old=read(RAW/f'c14-{fixture}-layout-v1.json');planned=read(RAW/'d18-verified.json')['fixtures'][fixture]
        for k in ['plan','arenas_unchanged','batch','hu_cache','input','iteration','nodes','players']:assert x[k]==old[k],k
        extra=planned['additional_bytes'];expected=dict(old['buffer_bytes'],rank_lower=692224,rank_upper=692224,rank_hand=692224,rank_count=4096,rank_products=extra-2080768)
        assert x['buffer_bytes']==expected and x['actual_device_bytes']==old['actual_device_bytes']+extra==planned['planned_device_bytes']
        assert x['rank_pipeline']==dict(extra_bytes=extra,groups=104,quadratures=(x['players']+1)//2,scratch_bytes=extra-2080768,tile=planned['tile_capacity'])
        assert x['actual_device_bytes']+256*1024*1024<=23000000000
        fixtures[fixture]=dict(extra_bytes=extra,total_device_bytes=x['actual_device_bytes'],tile=x['rank_pipeline']['tile'])
    tests=(HERE/'artifacts/c22-v2/src/preflop/gpu/cohort_reuse/tests.rs').read_text(encoding='utf-8')
    assert tests.count('for mode in 0..7 {')==2 and tests.count('assert_eq!(runs[5],runs[6],"C22 ')==2
    assert 'fn pipeline_phase_tracing_preserves_solver_bits()' in tests and 'fn pipeline_partial_allocation_and_tile_recovery()' in tests
    assert 'g.rank_pipeline.as_mut().unwrap().tile=3;g.mw_batch=5;' in tests and 'FAIL_PARTIAL.set(true)' in tests
    assert 'Some(&AtomicBool::new(true))' in tests
    admitted=all(gates.values())
    out=dict(verified=True,admitted=admitted,retained=False,status='Rank pipeline ready for first complete timing' if admitted else 'Rank pipeline resource gate failed',solver_tests=9,original_entries_unchanged=20,resources=resources,gates=gates,fixtures=fixtures,executable_sha256=frozen,protocol_sha256=sha(HERE/'C22_PROTOCOL.md'),integration_protocol_sha256=sha(HERE/'C22_INTEGRATION.md'),scope='Complete synthetic numerical/graph/stopped-flag and saved allocation qualification; actual mid-sweep interruption, save/reload continuation, complete timing and convergence are not established by these checks.')
    dest=RAW/'c22-integration-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
