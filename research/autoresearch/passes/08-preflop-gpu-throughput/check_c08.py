"""Audit the C08 rejection against C07, including archived source and layouts."""
import hashlib,json,math,statistics,subprocess
from pathlib import Path
from check_c07 import HERE,LAB,RAW,read,digest

def main():
    pre=read(RAW/'c08-numerical-v1-exit.json');reuse=read(RAW/'c08-reuse-tests-v1-exit.json')
    for x in [pre,reuse]:assert x['returncode']==0 and x['reason'] is None and x['seconds']<=240
    assert reuse['solver_source_files']==pre['solver_source_files']
    assert '5 passed; 0 failed; 1 ignored' in (RAW/'c08-numerical-v1.log').read_text()
    assert '4 passed; 0 failed; 1 ignored' in (RAW/'c08-reuse-tests-v1.log').read_text()
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c08-source-map.json').items()}
    for p,h in pre['solver_source_files'].items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        else:
            blob=subprocess.check_output(['git','show',pre['source_commit']+':'+Path(p).as_posix()],cwd=LAB)
            assert hashlib.sha256(blob).hexdigest()==h,p
    exe=LAB/'target/c08-benchmark-frozen.exe'
    def evidence(name):
        rec=read(RAW/(name+'-exit.json'));assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
        assert rec['solver_source_files']==pre['solver_source_files'] and rec['exe_sha256']==digest(exe)
        for p,h in rec['inputs'].items():assert digest(exe if p==rec['command'][0] else Path(p))==h,p
        for side in ['before','after']:
            x=read(RAW/(name+'-gpu-'+side+'.json'));assert x['returncode']==0
        return rec
    layouts={}
    for fixture in ['small','large']:
        name=f'c08-{fixture}-layout-v1';evidence(name);x=read(RAW/(name+'.json'));old=read(RAW/f'c07-{fixture}-layout-v1.json')
        assert x['staged']
        for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
        assert x['actual_device_bytes']==sum(x['buffer_bytes'].values())+x['plan']['extra_bytes']
        layouts[fixture]=x
    runs=[]
    for role in ['control','candidate']:
        name=f'c08-large-{role}-1';rec=evidence(name);b=read(RAW/(name+'-bench.json'))
        assert rec['environment_overrides']['PREFLOP_GPU_TERMINAL_STAGING']==str(int(role=='candidate'))
        assert b['staged']==(role=='candidate') and b['cohorts'] and b['enabled'] and not b['profile']
        assert b['shared_staging_bytes_per_block']==(5440 if role=='candidate' else 0)
        assert b['nodes']==1567754 and b['initial_iteration']==1050 and b['iteration']==1056 and b['batch']==32 and len(b['rows'])==6
        for i,r in enumerate(b['rows']):
            assert r['index']==i and r['iteration']==1051+i and r['warmup']==(i<2)
            for k in ['gaps','evs']:assert len(r[k])==8 and all(math.isfinite(v) for v in r[k])
            for k in ['iteration_seconds','check_seconds']:assert r[k]>0 and math.isfinite(r[k])
        for k in ['complete_seconds','init_seconds','sync_seconds']:assert b[k]>0 and math.isfinite(b[k])
        assert b['complete_seconds']>=b['init_seconds']+b['sync_seconds']+sum(r['iteration_seconds']+r['check_seconds'] for r in b['rows'])
        runs.append(b)
    a,b=runs;old=read(RAW/'c07-large-candidate-1-bench.json')
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k]==old[k],k
    for x,y,z in zip(a['rows'],b['rows'],old['rows']):
        for k in ['gaps','evs','index','warmup','iteration']:assert x[k]==y[k]==z[k],k
    assert b['cohort_plan']==layouts['large']['plan']
    ratios=dict(complete=b['complete_seconds']/a['complete_seconds'])
    for k in ['iteration','check']:ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
    assert ratios['complete']>=.99
    result=dict(retained=False,status='Rejected - first-pair timing screen',ratios=ratios,
        control_seconds=a['complete_seconds'],candidate_seconds=b['complete_seconds'],
        reason=f"Complete run {100*(ratios['complete']-1):.2f}% slower than C07; no extended campaign.",
        source_input_hashes_verified=True,exact_checkpoints_and_arena=True,global_allocation_matches_C07=True,
        shared_staging_bytes_per_block=5440,archived_executable_sha256=digest(exe),
        scope='One complete large pair; exact but slower. No speed/convergence gain or deployment. Barrier/cache/occupancy causes not separately established.')
    (RAW/'c08-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
