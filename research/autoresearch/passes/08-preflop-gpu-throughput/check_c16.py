"""Independent C16 audit against archived tested sources and frozen execution."""
import json,re,subprocess,hashlib,statistics,math
from pathlib import Path
from check_r03_saved import HERE,RAW,LAB,read,sha

def evidence(name,version,cap):
    r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<cap
    mapping={str(Path(k)):v for k,v in read(HERE/f'artifacts/c16-{version}-source-map.json').items()}
    for f,h in r['solver_source_files'].items():
        if f in mapping:assert sha(HERE/mapping[f])==h,f
        else:assert hashlib.sha256(subprocess.check_output(['git','show',r['source_commit']+':'+Path(f).as_posix()],cwd=LAB)).hexdigest()==h,f
    for f,h in r['inputs'].items():assert sha(f)==h,f
    return r

def main():
    wrong=evidence('c16-kernel-v1','v1',300);good=evidence('c16-kernel-v2','v1',180)
    assert '0 passed; 0 failed' in (RAW/'c16-kernel-v1.log').read_text(encoding='utf8')
    assert '1 passed; 0 failed' in (RAW/'c16-kernel-v2.log').read_text(encoding='utf8')
    assert wrong['solver_source_files']==good['solver_source_files']
    kernel=read(RAW/'c16-compiler-v1/results.json');assert kernel['exact'] and kernel['hand_classes']==169 and kernel['prefix_and_terminal_guards']
    expected=[dict(opponents=o,kind=k,start=s,batch=b,count=c) for k in [0,1,2,0] for b,c in [(5,1),(5,4),(5,5),(32,1),(32,7),(32,23),(32,31),(32,32)] for s in [0,17,992] for o in range(2,9)]
    assert kernel['cases']==expected and len(expected)==672
    assert len(kernel['resources'])==21 and {r['kernel'] for r in kernel['resources']}=={f'{role}_{o}' for role in ['ref','fused','prefix'] for o in range(2,9)}
    for f in ['fused_cdf.rs','fused_cdf.cu','fused_cdf/tests.rs']:
        assert sha(HERE/'artifacts/c16-v1/src/preflop/gpu'/f)==sha(HERE/'artifacts/c16-v2/src/preflop/gpu'/f)
    numerical=evidence('c16-numerical-v1','v2',300);assert '6 passed; 0 failed; 1 ignored' in (RAW/'c16-numerical-v1.log').read_text(encoding='utf8')
    assert numerical['environment_overrides']['PREFLOP_GPU_FUSED_CDF']=='1'
    exe=LAB/'target/c16-benchmark-frozen.exe';layouts={}
    for fixture in ['small','large']:
        name=f'c16-{fixture}-layout-v1';r=evidence(name,'v2',180);x=read(RAW/(name+'.json'));old=read(RAW/f'c14-{fixture}-layout-v1.json')
        assert r['solver_source_files']==numerical['solver_source_files'] and r['exe_sha256']==sha(exe)
        assert r['environment_overrides']['PREFLOP_GPU_FUSED_CDF']=='1'
        assert x['fused_cdf'] and x['narrow_offsets'] and x['unrolled']
        for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
        for side in ['before','after']:assert read(RAW/(name+'-gpu-'+side+'.json'))['returncode']==0
        layouts[fixture]=x
    runs=[]
    for role in ['control','candidate']:
        name=f'c16-large-{role}-1';r=evidence(name,'v2',180);x=read(RAW/(name+'-bench.json'))
        assert r['solver_source_files']==numerical['solver_source_files'] and r['exe_sha256']==sha(exe)
        assert r['environment_overrides']['PREFLOP_GPU_FUSED_CDF']==str(int(role=='candidate'))
        assert x['fused_cdf']==(role=='candidate') and x['narrow_offsets'] and x['cohorts'] and x['enabled'] and not x['profile'] and not x['production_selection']
        assert len(x['rows'])==6 and x['iteration']==1056 and x['nodes']==1567754 and x['batch']==32
        for i,row in enumerate(x['rows']):
            assert row['iteration']==1051+i and row['index']==i and row['warmup']==(i<2)
            for k in ['gaps','evs']:assert len(row[k])==8 and all(math.isfinite(v) for v in row[k])
            for k in ['iteration_seconds','check_seconds']:assert row[k]>0 and math.isfinite(row[k])
        assert x['complete_seconds']>=x['init_seconds']+x['sync_seconds']+sum(row['iteration_seconds']+row['check_seconds'] for row in x['rows'])
        for side in ['before','after']:assert read(RAW/(name+'-gpu-'+side+'.json'))['returncode']==0
        runs.append(x)
    a,b=runs;old=read(RAW/'c14-large-candidate-1-bench.json')
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k]==old[k],k
    for x,y,z in zip(a['rows'],b['rows'],old['rows']):
        for k in ['gaps','evs','index','iteration','warmup']:assert x[k]==y[k]==z[k],k
    assert b['cohort_plan']==layouts['large']['plan']
    ratios={'complete':b['complete_seconds']/a['complete_seconds']}
    for k in ['iteration','check']:ratios[k]=statistics.median(row[k+'_seconds'] for row in b['rows'][2:])/statistics.median(row[k+'_seconds'] for row in a['rows'][2:])
    assert ratios['complete']>=.99
    assert not subprocess.check_output(['git','diff','02c0898','--','crates'],cwd=LAB)
    assert not (LAB/'crates/solver/src/preflop/gpu/fused_cdf.rs').exists()
    assert sha(LAB/'target/r03-v3-server-frozen.exe')==read(RAW/'r03-release-verified.json')['executable_sha256']
    result={'retained':False,'status':'Rejected - first-pair timing screen','ratios':ratios,
        'control_seconds':a['complete_seconds'],'candidate_seconds':b['complete_seconds'],
        'reason':f"Complete run {100*(ratios['complete']-1):.2f}% slower than C14; no extended campaign.",
        'source_input_hashes_verified':True,'exact_checkpoints_and_arena':True,'kernel_prefix_cases':672,'expanded_tests':6,
        'global_allocation_matches_C14':True,'runtime_restored':True,'archived_executable_sha256':sha(exe),
        'scope':'One complete large pair. Extra prefix work, barriers and shared-memory effects are not separately profiled. No speed/convergence gain or deployment.'}
    target=RAW/'c16-verified.json'
    if target.exists():assert read(target)==result
    else:target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
