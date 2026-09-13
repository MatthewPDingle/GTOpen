"""Audit C12 rejection, exact outputs, compiler evidence and immutable provenance."""
import hashlib,json,math,re,statistics,subprocess
from pathlib import Path
from check_c07 import HERE,LAB,RAW,read,digest
def main():
    pre=read(RAW/'c12-prefix-v1-exit.json')
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c12-source-map.json').items()}
    for p,h in pre['solver_source_files'].items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        else:assert hashlib.sha256(subprocess.check_output(['git','show',pre['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    for name,expected in [('c12-prefix-v1','1 passed; 0 failed'),('c12-numerical-v1','5 passed; 0 failed; 1 ignored'),('c12-reuse-tests-v1','4 passed; 0 failed; 1 ignored')]:
        r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<=240
        assert r['solver_source_files']==pre['solver_source_files']
        assert expected in (RAW/(name+'.log')).read_text()
        for p,h in r['inputs'].items():assert digest(p)==h,p
    exe=LAB/'target/c12-benchmark-frozen.exe'
    def evidence(name):
        r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<=180
        assert r['solver_source_files']==pre['solver_source_files'] and r['exe_sha256']==digest(exe)
        for p,h in r['inputs'].items():assert digest(exe if p==r['command'][0] else Path(p))==h,p
        for side in ['before','after']:assert read(RAW/(name+'-gpu-'+side+'.json'))['returncode']==0
        return r
    layouts={}
    for fixture in ['small','large']:
        name=f'c12-{fixture}-layout-v1';r=evidence(name);x=read(RAW/(name+'.json'));old=read(RAW/f'c07-{fixture}-layout-v1.json')
        assert r['environment_overrides']['PREFLOP_GPU_PREDICATED_CDF']=='1' and x['unrolled']
        for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
        assert x['actual_device_bytes']==sum(x['buffer_bytes'].values())+x['plan']['extra_bytes'];layouts[fixture]=x
    diag=RAW/'c12-compiler-v1';resources=read(diag/'resources.json');assert len(resources)==2
    for r in resources:assert r['registers']==26 and r['local_bytes']==0 and r['shared_bytes']==0
    for name in ['reference','candidate']:
        s=(diag/(name+'.ptx')).read_text();assert s.count('shfl.sync.up.b32')==30
        assert s.count('selp.f32')==(30 if name=='reference' else 0)
        assert len(re.findall(r'@\w+\s+add.rn.f32',s))==(30 if name=='candidate' else 0)
    runs=[]
    for role in ['control','candidate']:
        name=f'c12-large-{role}-1';r=evidence(name);b=read(RAW/(name+'-bench.json'))
        assert r['environment_overrides']['PREFLOP_GPU_PREDICATED_CDF']==str(int(role=='candidate'))
        assert b['predicated_cdf']==(role=='candidate') and b['cohorts'] and b['enabled'] and not b['profile']
        assert b['terminal_unroll_factor']==2 and b['unrolled']
        assert b['nodes']==1567754 and b['initial_iteration']==1050 and b['iteration']==1056 and b['batch']==32 and len(b['rows'])==6
        for i,row in enumerate(b['rows']):
            assert row['index']==i and row['iteration']==1051+i and row['warmup']==(i<2)
            for k in ['gaps','evs']:assert len(row[k])==8 and all(math.isfinite(v) for v in row[k])
            for k in ['iteration_seconds','check_seconds']:assert row[k]>0 and math.isfinite(row[k])
        for k in ['complete_seconds','init_seconds','sync_seconds']:assert b[k]>0 and math.isfinite(b[k])
        assert b['complete_seconds']>=b['init_seconds']+b['sync_seconds']+sum(row['iteration_seconds']+row['check_seconds'] for row in b['rows'])
        runs.append(b)
    a,b=runs;old=read(RAW/'c09-large-candidate-1-bench.json')
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k]==old[k],k
    for x,y,z in zip(a['rows'],b['rows'],old['rows']):
        for k in ['gaps','evs','index','warmup','iteration']:assert x[k]==y[k]==z[k],k
    assert b['cohort_plan']==layouts['large']['plan']
    ratios=dict(complete=b['complete_seconds']/a['complete_seconds'])
    for k in ['iteration','check']:ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
    assert ratios['complete']>=.99
    result=dict(retained=False,status='Rejected - no meaningful complete-run gain',ratios=ratios,
        control_seconds=a['complete_seconds'],candidate_seconds=b['complete_seconds'],reason='First complete pair below 1% screening gain; no extended campaign.',
        source_input_hashes_verified=True,exact_checkpoints_and_arena=True,global_allocation_matches_C09=True,
        archived_executable_sha256=digest(exe),compiler_resources=resources,compiler_artifact_hashes={str(f.relative_to(RAW)):digest(f) for f in diag.iterdir()},
        scope='One complete large pair; exact but effectively tied. PTX removes 30 selects; no measured meaningful speed or convergence gain. Candidate removed, no deployment.')
    target=RAW/'c12-verified.json'
    if target.exists():assert read(target)==result
    else:target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
