"""Independent C19 integration, failed-harness and complete-pair audit."""
import ast,hashlib,json,re,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit_sources(rec,version):
    mapping={str(Path(k)):v for k,v in read(HERE/f'artifacts/c19-{version}-source-map.json').items()}
    for p,h in rec['solver_source_files'].items():
        if p in mapping:
            v=mapping[p];assert sha(HERE/v['archive'])==h==v['sha256'],p
        else:assert hashlib.sha256(subprocess.check_output(['git','show',rec['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    for p,h in rec['inputs'].items():
        path=HERE/'artifacts/c19-v2/run_c19.py' if version=='v2' and Path(p).name=='run_c19.py' else Path(p)
        assert sha(path)==h,p
def main():
    admission=read(RAW/'c19-screen-verified.json');assert admission['verified'] and admission['admitted']
    failed=read(RAW/'c19-numerical-v1-exit.json')
    assert failed['returncode']==101 and failed['reason'] is None and failed['seconds']<=300
    audit_sources(failed,'v2')
    log=(RAW/'c19-numerical-v1.log').read_text(encoding='utf-8')
    assert '8 passed; 1 failed; 1 ignored' in log
    assert re.findall(r"thread '([^']+)' .* panicked",log)==['preflop::gpu::cohort_reuse::tests::interleaved_constructor_resets_selection_after_error']
    arrays=[ast.literal_eval(v) for v in re.findall(r'^[ \t]+(?:left|right): (.+)$',log,re.M)]
    assert len(arrays)==2
    left,right=arrays
    assert left[:2]==right[:2] and left[2:]!=right[2:]
    assert all(x==0 for v in left[2:] for x in v)
    # Only the guard expectation changed between v2 and v3, not solver code.
    a=read(HERE/'artifacts/c19-v2-source-map.json');b=read(HERE/'artifacts/c19-v3-source-map.json')
    assert a.keys()==b.keys()
    changed=[p for p in a if a[p]['sha256']!=b[p]['sha256']]
    assert changed==['crates/solver/src/preflop/gpu/cohort_reuse/tests.rs']
    success=read(RAW/'c19-numerical-v2-exit.json')
    assert success['returncode']==0 and success['reason'] is None and success['seconds']<=300
    audit_sources(success,'v3')
    assert '9 passed; 0 failed; 1 ignored' in (RAW/'c19-numerical-v2.log').read_text(encoding='utf-8')
    # The original tested scan generator is unchanged in final integration.
    old=(HERE/'artifacts/c19-v1/src/preflop/gpu/cdf_interleave.rs').read_text(encoding='utf-8')
    final=(HERE/'artifacts/c19-v3/src/preflop/gpu/cdf_interleave.rs').read_text(encoding='utf-8')
    assert final.startswith(old)
    exe=LAB/'target/c19-benchmark-frozen.exe';exe_hash=sha(exe)
    def record(name):
        rec=read(RAW/(name+'-exit.json'))
        assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
        assert rec['solver_source_files']==success['solver_source_files'] and rec['exe_sha256']==exe_hash
        audit_sources(rec,'v3');return rec
    layouts={}
    for fixture in ['small','large']:
        rec=record(f'c19-{fixture}-layout-v1');x=read(RAW/f'c19-{fixture}-layout-v1.json');old=read(RAW/f'c14-{fixture}-layout-v1.json')
        assert rec['environment_overrides']['PREFLOP_GPU_CDF_INTERLEAVE']=='1'
        assert x['interleaved_cdf'] and x['narrow_offsets'] and x['unrolled']
        for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
        layouts[fixture]=dict(actual_device_bytes=x['actual_device_bytes'],batch=x['batch'],buffers_match_retained=True)
    pair={}
    for role in ['control','candidate']:
        rec=record(f'c19-large-{role}-1');pair[role]=read(RAW/f'c19-large-{role}-1-bench.json')
        assert rec['environment_overrides']['PREFLOP_GPU_CDF_INTERLEAVE']==str(int(role=='candidate'))
        assert pair[role]['interleaved_cdf']==(role=='candidate')
    control,candidate=pair['control'],pair['candidate'];retained=read(RAW/'c14-large-candidate-1-bench.json')
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:
        assert control[k]==candidate[k]==retained[k],k
    assert len(control['rows'])==len(candidate['rows'])==len(retained['rows'])==6
    for x,y,z in zip(control['rows'],candidate['rows'],retained['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k]==z[k],k
    ratio=candidate['complete_seconds']/control['complete_seconds'];assert ratio>=.99
    warm=lambda x,k:statistics.median(r[k] for r in x['rows'] if not r['warmup'])
    summary={k:{role:pair[role][k] for role in pair} for k in ['complete_seconds','init_seconds','sync_seconds']}
    summary['ratio']=ratio
    summary['warm_iteration_ratio']=warm(candidate,'iteration_seconds')/warm(control,'iteration_seconds')
    summary['warm_check_ratio']=warm(candidate,'check_seconds')/warm(control,'check_seconds')
    assert sha(LAB/'target/r03-v3-server-frozen.exe')==read(RAW/'r03-release-verified.json')['executable_sha256']
    out=dict(verified=True,retained=False,status='Rejected: complete runtime gain below screening threshold',
        first_pair=summary,layouts=layouts,exact_checkpoints_and_arena=True,
        arena_entries=candidate['arena_entries'],arena_fingerprint=candidate['arena_fingerprint'],
        solver_tests_passed=9,standalone_prefix_cases=672,executable_sha256=exe_hash,
        failed_harness=dict(preserved=True,learning_arrays_unchanged=True,first_evaluation_populated_empty_results=True),
        scope='One exact large timing pair; 1% screening gate failed. No extended or retention regression campaign.')
    dest=RAW/'c19-timing-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    (RAW/'c19-verified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
