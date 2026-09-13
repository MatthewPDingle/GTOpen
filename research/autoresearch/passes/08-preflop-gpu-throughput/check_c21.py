"""Audit complete C21 solver qualification, dispatch and first timing pair."""
import hashlib,json,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(rec):
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c21-v2-source-map.json').items()}
    for p,h in rec['solver_source_files'].items():
        if p in mapping:
            v=mapping[p];assert sha(HERE/v['archive'])==h==v['sha256']
        else:assert hashlib.sha256(subprocess.check_output(['git','show',rec['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h
    for p,h in rec['inputs'].items():assert sha(Path(p))==h
def main():
    admission=read(RAW/'c21-screen-verified.json');assert admission['verified'] and admission['admitted']
    success=read(RAW/'c21-numerical-v1-exit.json')
    assert success['returncode']==0 and success['reason'] is None and success['seconds']<=300
    audit(success);log=(RAW/'c21-numerical-v1.log').read_text(encoding='utf-8')
    assert '9 passed; 0 failed; 1 ignored' in log
    assert 'sparse_scan_constructor_resets_selection_after_error ...' in log
    old=(HERE/'artifacts/c21-v1/src/preflop/gpu/cdf_zero_predicate.rs').read_text()
    final=(HERE/'artifacts/c21-v2/src/preflop/gpu/cdf_zero_predicate.rs').read_text();assert final.startswith(old)
    exact=(HERE/'artifacts/c21-v2/src/preflop/gpu/exact_reuse.rs').read_text()
    assert 'self.stream.launch_builder(r.cdf_for_gate(gate))' in exact
    assert 'if gate!=0 {if let Some(f)=self.cdf_learning.as_ref(){return f;}}' in exact
    assert 'cdf:module.load_function("pf_exact_reuse_cdf")' in exact
    assert 'module.load_function("pf_exact_reuse_cdf_sparse_predicate")' in exact
    # Cohort checks still call the original function directly, with gate0.
    cohort=subprocess.check_output(['git','show',success['source_commit']+':crates/solver/src/preflop/gpu/cohort_reuse.rs'],cwd=LAB).decode()
    assert 'launch_builder(&r.cdf).arg(&c.work)' in cohort and 'cdf_learning' not in cohort
    exe=LAB/'target/c21-benchmark-frozen.exe';exe_hash=sha(exe)
    def record(name):
        rec=read(RAW/(name+'-exit.json'))
        assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
        assert rec['solver_source_files']==success['solver_source_files'] and rec['exe_sha256']==exe_hash
        audit(rec);return rec
    layouts={}
    for fixture in ['small','large']:
        rec=record(f'c21-{fixture}-layout-v1');x=read(RAW/f'c21-{fixture}-layout-v1.json');old=read(RAW/f'c14-{fixture}-layout-v1.json')
        assert rec['environment_overrides']['PREFLOP_GPU_CDF_ZERO_PREDICATE']=='1'
        assert x['sparse_scan_cdf'] and x['narrow_offsets'] and x['unrolled']
        for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k]
        layouts[fixture]=dict(actual_device_bytes=x['actual_device_bytes'],batch=x['batch'],buffers_match_retained=True)
    pair={}
    for role in ['control','candidate']:
        rec=record(f'c21-large-{role}-1');pair[role]=read(RAW/f'c21-large-{role}-1-bench.json')
        assert rec['environment_overrides']['PREFLOP_GPU_CDF_ZERO_PREDICATE']==str(int(role=='candidate'))
        assert pair[role]['sparse_scan_cdf']==(role=='candidate')
    control,candidate=pair['control'],pair['candidate'];retained=read(RAW/'c14-large-candidate-1-bench.json')
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:
        assert control[k]==candidate[k]==retained[k],k
    assert len(control['rows'])==len(candidate['rows'])==len(retained['rows'])==6
    for x,y,z in zip(control['rows'],candidate['rows'],retained['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k]==z[k],k
    ratio=candidate['complete_seconds']/control['complete_seconds']
    warm=lambda x,k:statistics.median(r[k] for r in x['rows'] if not r['warmup'])
    summary={k:{role:pair[role][k] for role in pair} for k in ['complete_seconds','init_seconds','sync_seconds']}
    summary.update(ratio=ratio,warm_iteration_ratio=warm(candidate,'iteration_seconds')/warm(control,'iteration_seconds'),
        warm_check_ratio=warm(candidate,'check_seconds')/warm(control,'check_seconds'))
    assert sha(LAB/'target/r03-v3-server-frozen.exe')==read(RAW/'r03-release-verified.json')['executable_sha256']
    passed=ratio<.99
    out=dict(verified=True,retained=False,passed_screen=passed,
        status='Sparse predicate scan admits extended timing' if passed else 'Rejected: sparse predicate scan fails complete runtime screen',
        first_pair=summary,layouts=layouts,exact_checkpoints_and_arena=True,
        arena_entries=candidate['arena_entries'],arena_fingerprint=candidate['arena_fingerprint'],
        solver_tests_passed=9,standalone_prefix_cases=1008,executable_sha256=exe_hash,
        learning_only_dispatch_verified=True,original_check_writer_unchanged=True,
        scope='One complete large timing pair; not retained without extended timing and regression qualification.')
    dest=RAW/'c21-timing-screen-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    (RAW/'c21-verified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
