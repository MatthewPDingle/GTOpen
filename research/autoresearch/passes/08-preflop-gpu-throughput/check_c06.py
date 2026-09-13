"""Audit C06 first-pair rejection and exact numerical/allocation evidence."""
import functools,hashlib,json,math,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3];RAW=HERE/'raw'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
@functools.cache
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    pre=read(RAW/'c06-benchmark-build-v1-exit.json');sources=pre['solver_source_files']
    assert pre['returncode']==0 and pre['reason'] is None
    assert '3 passed; 0 failed; 1 ignored' in (RAW/'c06-benchmark-build-v1.log').read_text()
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c06-source-map.json').items()}
    for p,h in sources.items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        else:
            blob=subprocess.check_output(['git','show',pre['source_commit']+':'+Path(p).as_posix()],cwd=LAB)
            assert hashlib.sha256(blob).hexdigest()==h,p
    frozen=LAB/'target/c06-benchmark-frozen.exe';exe_hash=digest(frozen);runs=[]
    for role in ['control','candidate']:
        name=f'c06-large-{role}-1';rec=read(RAW/(name+'-exit.json'));x=read(RAW/(name+'-bench.json'))
        assert rec['returncode']==0 and rec['reason'] is None and rec['exe_sha256']==exe_hash and rec['solver_source_files']==sources
        for p,h in rec['inputs'].items():assert digest(frozen if p==rec['command'][0] else Path(p))==h,p
        assert rec['environment_overrides']['PREFLOP_GPU_COHORT_ENABLE']==str(int(role=='candidate'))
        assert x['cohorts']==(role=='candidate') and x['enabled'] and not x['profile'] and x['batch']==32
        assert x['nodes']==1567754 and x['initial_iteration']==1050 and x['iteration']==1056 and len(x['rows'])==6
        for i,row in enumerate(x['rows']):
            assert row['index']==i and row['iteration']==1051+i and row['warmup']==(i<2)
            for k in ['gaps','evs']:assert len(row[k])==8 and all(math.isfinite(v) for v in row[k])
            for k in ['iteration_seconds','check_seconds']:assert row[k]>0 and math.isfinite(row[k])
        runs.append(x)
    a,b=runs
    for k in ['input','nodes','initial_iteration','iteration','batch','arena_entries','arena_fingerprint','original_cdf_bytes']:assert a[k]==b[k],k
    for x,y in zip(a['rows'],b['rows']):
        for k in ['gaps','evs','index','warmup','iteration']:assert x[k]==y[k],k
    layouts={}
    for fixture in ['small','large']:
        name=f'c06-{fixture}-layout-v1';rec=read(RAW/(name+'-exit.json'));x=read(RAW/(name+'.json'))
        assert rec['returncode']==0 and rec['reason'] is None
        changed={p for p,h in sources.items() if rec['solver_source_files'].get(p)!=h}
        assert changed=={str(Path('crates/solver/src/preflop/gpu/exact_reuse/tests.rs'))},changed
        # Only ignored benchmark wiring changed after allocation validation;
        # constructor, kernels, memory planner and its numerical tests are identical.
        for p,h in rec['inputs'].items():
            if p!=rec['command'][0]:assert digest(Path(p))==h,p
        d=read(RAW/f'd05-{fixture}-v1.json');expected=d['cohorts']['selected_static_plan'];actual=x['plan']
        for k in ['groups','group_masks','total_bytes','static_rows']:assert actual[k]==expected[k],k
        assert actual['capacity']==expected['static_capacity'] and actual['peak_bytes']==expected['planned_initial_peak_bytes']
        assert actual['base_bytes']==d['base_bytes'] and x['actual_device_bytes']==sum(x['buffer_bytes'].values())+actual['extra_bytes']==actual['total_bytes']
        assert actual['peak_bytes']<=23_000_000_000 and x['arenas_unchanged'] and x['batch']==32
        assert x['buffer_bytes']['d_eq_cache']==d['buffer_bytes']['d_eq_cache']
        layouts[fixture]=x
    assert b['cohort_plan']==layouts['large']['plan']
    assert b['cdf_bytes']==15_714_462_720 and b['original_cdf_bytes']==8_444_664_320
    expected_extra=b['cohort_plan']['extra_bytes']+layouts['large']['buffer_bytes']['d_mw_normalized']-b['original_cdf_bytes']//(32*170)*169
    assert b['extra_bytes']==expected_extra
    ratios={'complete':b['complete_seconds']/a['complete_seconds']}
    for k in ['iteration','check']:ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
    assert ratios['complete']>=.99
    result=dict(retained=False,status='Rejected - first-pair timing screen',ratios=ratios,
        control_seconds=a['complete_seconds'],candidate_seconds=b['complete_seconds'],
        reason=f"Complete run was {100*(ratios['complete']-1):.2f}% slower; no extended trials.",
        source_input_hashes_verified=True,exact_checkpoints_and_arena=True,allocation_matches_D05=True,
        allocated_device_bytes=b['cohort_plan']['total_bytes'],archived_executable_sha256=exe_hash,
        scope='One fixed-work large pair. Numerically equal but slower. Allocation fits; cause of slowdown not established. No deployment.')
    (RAW/'c06-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
