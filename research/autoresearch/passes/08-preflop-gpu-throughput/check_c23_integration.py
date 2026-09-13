"""Audit integrated static-CDF arithmetic, exact suite and saved layouts."""
import hashlib,json,subprocess
from pathlib import Path
from check_d09 import entries
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    rec=read(RAW/'c23-numerical-v1-exit.json');assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=300
    log=(RAW/'c23-numerical-v1.log').read_text(encoding='utf-8');assert '10 passed; 0 failed; 1 ignored' in log
    for p,h in rec['inputs'].items():assert sha(p)==h,p
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c23-v2-source-map.json').items()}
    for p,h in rec['solver_source_files'].items():
        if p in mapping:assert sha(HERE/mapping[p]['archive'])==mapping[p]['sha256']==h,p
        else:assert hashlib.sha256(subprocess.check_output(['git','show',rec['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    folder=RAW/'c23-integrated-v1';source=(folder/'candidate.cu').read_text();prior=RAW/'c23-static-v1'
    control=(prior/'control.cu').read_text();qualified=(prior/'candidate.cu').read_text()
    start=control.index('extern "C" __global__ void pf_exact_reuse_terminal(');end=control.index('\n}\n',start)+3
    terminal=control[start:end].replace('pf_exact_reuse_terminal(','pf_static_terminal(')
    for old,new in [
        ('float* val, const u32* aliases)','float* val, const u32* aliases, u32 row_stride, const u32* sample_offsets, int cohort)'),
        ('compact_slots[(size_t)p * union_slots + global_slot]','compact_slots[(cohort ? 0 : (size_t)p * union_slots) + global_slot]'),
        ('cdf_slot * batch_capacity * (NC + 1)','cdf_slot * row_stride')]:
        assert terminal.count(old)==1;terminal=terminal.replace(old,new)
    assert terminal.count('sample_start, sample_count);')==7
    terminal=terminal.replace('pf_multiway_sum<','pf_static_init<').replace('sample_start, sample_count);','sample_start, sample_count, 0.f, sample_offsets);')
    assert source==qualified+terminal
    a=entries((prior/'control.ptx').read_text());b=entries((folder/'candidate.ptx').read_text());q=entries((prior/'candidate.ptx').read_text())
    assert len(a)==20 and all(b[k]==v for k,v in a.items())
    assert set(b)-set(q)=={'pf_static_terminal'}
    assert all(b[k]==v for k,v in q.items()),'qualified standalone entries changed'
    resources=read(folder/'resources.json');assert [x['kernel'] for x in resources]==['writer','terminal']
    gates=dict(no_spills=all(x['local_bytes']==0 for x in resources),bounded_registers=all(x['registers']<=64 for x in resources),original_shared_metadata=[x['shared_bytes'] for x in resources]==[0,44])
    receipt=read(RAW/'c23-benchmark-frozen.json');frozen=sha(LAB/'target/c23-benchmark-frozen.exe');assert receipt==dict(source_run='c23-numerical-v1',sha256=frozen)
    fixtures={}
    for fixture in ['small','large']:
        name=f'c23-{fixture}-layout-v1';r=read(RAW/(name+'-exit.json'))
        assert r['returncode']==0 and r['reason'] is None and r['seconds']<=180
        assert r['exe_sha256']==frozen and r['solver_source_files']==rec['solver_source_files']
        for path,h in r['inputs'].items():assert sha(path)==h,path
        x=read(RAW/(name+'.json'));old=read(RAW/f'c14-{fixture}-layout-v1.json');planned=read(RAW/'d19-verified.json')['fixtures'][fixture]
        for k in ['plan','arenas_unchanged','batch','hu_cache','input','iteration','nodes','players']:assert x[k]==old[k],k
        expected=dict(old['buffer_bytes'],d_mw_cdf=planned['cdf_bytes_after'],static_prefix=696320,static_hand=692224,static_offsets=4100)
        assert x['buffer_bytes']==expected and x['actual_device_bytes']==planned['final_device_bytes']
        assert x['actual_device_bytes']==old['actual_device_bytes']-planned['cdf_bytes_before']+planned['cdf_bytes_after']+1392644
        assert x['static_cdf']==dict(row_stride=2160,static_bytes=1392644,original_cdf_bytes=planned['cdf_bytes_before'])
        assert x['actual_device_bytes']+268435456<=23000000000
        fixtures[fixture]=dict(cdf_bytes=x['buffer_bytes']['d_mw_cdf'],total_device_bytes=x['actual_device_bytes'],static_bytes=1392644)
    tests=(HERE/'artifacts/c23-v2/src/preflop/gpu/cohort_reuse/tests.rs').read_text(encoding='utf-8')
    assert tests.count('for mode in 0..7 {')==2 and tests.count('assert_eq!(runs[5],runs[6],"C23 ')==2
    for test in ['static_cdf_phase_tracing_preserves_solver_bits','static_cdf_real_allocation_failure_and_retry','static_cdf_save_reload_and_interrupted_replay']:assert f'fn {test}()' in tests and test in log
    assert 'for stage in [1,2,3]' in tests and 'assert_eq!(used(),before)' in tests
    assert 'Some(&AtomicBool::new(true))' in tests and 'g.try_iterate(&mut s,Some(&stop))' in tests
    assert 'assert!(!completed' in tests and 'must have completed actual player work' in tests
    continuation=read(folder/'continuation.json');assert continuation==dict(continuation_rounds=3,interrupted_continuation_exact=True,interrupted_iteration=3,matched_last_player=1,saved_files_identical=True)
    assert sha(folder/'continued-false.gtop')==sha(folder/'continued-true.gtop')
    constructor=(HERE/'artifacts/c23-v2/src/preflop/gpu/static_cdf.rs').read_text(encoding='utf-8')
    assert 'drop(std::mem::replace(&mut g.d_mw_cdf,empty));' in constructor
    assert constructor.index('drop(std::mem::replace')<constructor.index('fault(&g,2)?;')<constructor.index('g.d_mw_cdf=g.stream.alloc_zeros')<constructor.index('fault(&g,3)?;')
    assert 'sys::CUresult::CUDA_ERROR_OUT_OF_MEMORY' in constructor
    for name,writer,reader in [('exact_reuse.rs','self','self'),('cohort_reuse.rs','self','g')]:
        host=(HERE/f'artifacts/c23-v2/src/preflop/gpu/{name}').read_text(encoding='utf-8')
        assert f'{writer}.stream.launch_builder(&k.writer)' in host and f'{reader}.stream.launch_builder(&k.terminal)' in host
        assert '.arg(&k.stride).arg(&k.prefix).arg(&k.offsets)' in host and '.arg(&k.hand)' in host
        assert f'.arg(&k.stride).arg(&k.offsets).arg(&{int(name=="cohort_reuse.rs")}i32)' in host
    out=dict(verified=True,admitted=all(gates.values()),retained=False,status='Static CDF ready for first complete timing' if all(gates.values()) else 'Static CDF integration resource gate failed',solver_tests=10,original_entries_unchanged=20,standalone_entries_unchanged=len(q),resources=resources,gates=gates,fixtures=fixtures,executable_sha256=frozen,continuation=continuation,real_allocation_failure_stages=[1,2,3],protocol_sha256=sha(HERE/'C23_PROTOCOL.md'),integration_protocol_sha256=sha(HERE/'C23_INTEGRATION.md'),artifacts={p.name:sha(p) for p in folder.iterdir() if p.is_file()},scope='Full synthetic numerical/graph/stop/recovery and saved-fixture allocations qualified. Complete large workload timing and convergence remain unqualified.')
    dest=RAW/'c23-integration-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
