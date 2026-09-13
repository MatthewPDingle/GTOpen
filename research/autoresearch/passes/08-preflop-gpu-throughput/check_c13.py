"""Independent C13 numerical, provenance, memory and complete-work gate audit."""
import hashlib,json,math,re,statistics,subprocess
from pathlib import Path
from check_c07 import HERE,LAB,RAW,read,digest

def main():
    initial=read(RAW/'c13-bounds-partials-v1-exit.json')
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c13-source-map.json').items()}
    for p,h in initial['solver_source_files'].items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        else:assert hashlib.sha256(subprocess.check_output(['git','show',initial['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    for name,expected in [('c13-bounds-partials-v1','2 passed; 0 failed'),('c13-numerical-v1','6 passed; 0 failed; 1 ignored'),('c13-reuse-tests-v1','4 passed; 0 failed; 1 ignored')]:
        r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<300
        assert r['solver_source_files']==initial['solver_source_files']
        assert expected in (RAW/(name+'.log')).read_text()
        for p,h in r['inputs'].items():assert digest(p)==h,p
    text=(RAW/'c13-bounds-partials-v1.log').read_text()
    witness=json.loads(re.search(r'C13_ADDRESS (\{[^\n]+\})',text).group(1))
    assert witness==dict(cases=48,exact=True,max_byte_offset=17179868836,oversized_buffers_refused=True)
    compiler=RAW/'c13-compiler-v1';record=read(compiler/'resources.json')
    assert record['exact'] and record['cases_per_variant']==420 and record['hand_values_per_case']==169
    assert record['opponents']==list(range(2,9)) and record['counts']==[1,7,23,31,32] and record['offsets']==[0,1,37,992]
    for kind in ['exact','cohort']:
        assert digest(compiler/(kind+'-control.ptx'))==digest(RAW/'c10-runtime-compiler-v1'/(kind+'-2.ptx'))
        for narrow in [False,True]:
            r=[r for r in record['resources'] if r.get('module')==kind and r['narrow']==narrow];assert len(r)==1
            assert r[0]['registers']==(40 if narrow else 54) and r[0]['local_bytes']==0 and r[0]['shared_bytes']==(44 if narrow else 84)
    exe=LAB/'target/c13-benchmark-frozen.exe'
    def evidence(name):
        r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and 0<r['seconds']<180
        assert r['solver_source_files']==initial['solver_source_files'] and r['exe_sha256']==digest(exe)
        for p,h in r['inputs'].items():assert digest(p)==h,p
        for side in ['before','after']:assert read(RAW/(name+'-gpu-'+side+'.json'))['returncode']==0
        return r
    layouts={}
    for fixture in ['small','large']:
        name=f'c13-{fixture}-layout-v1';r=evidence(name);x=read(RAW/(name+'.json'));old=read(RAW/f'c07-{fixture}-layout-v1.json')
        assert r['environment_overrides']['PREFLOP_GPU_NARROW_OFFSETS']=='1' and x['narrow_offsets'] and x['unrolled']
        for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
        assert x['actual_device_bytes']==sum(x['buffer_bytes'].values())+x['plan']['extra_bytes']
        assert x['plan']['capacity']*32*170<=2**32-1;layouts[fixture]=x
    def pair(fixture,n):
        old=read(RAW/f'c09-{fixture}-candidate-1-bench.json');runs=[]
        for role in ['control','candidate']:
            name=f'c13-{fixture}-{role}-{n}';r=evidence(name);b=read(RAW/(name+'-bench.json'))
            assert r['environment_overrides']['PREFLOP_GPU_NARROW_OFFSETS']==str(int(role=='candidate'))
            assert b['narrow_offsets']==(role=='candidate') and b['cohorts'] and b['enabled'] and not b['profile']
            assert b['terminal_unroll_factor']==2 and b['unrolled'] and len(b['rows'])==6
            for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert b[k]==old[k],k
            for row,ref in zip(b['rows'],old['rows']):
                for k in ['gaps','evs','index','warmup','iteration']:assert row[k]==ref[k],k
                for k in ['iteration_seconds','check_seconds']:assert row[k]>0 and math.isfinite(row[k])
            for k in ['complete_seconds','init_seconds','sync_seconds']:assert b[k]>0 and math.isfinite(b[k])
            assert b['complete_seconds']>=b['init_seconds']+b['sync_seconds']+sum(row['iteration_seconds']+row['check_seconds'] for row in b['rows'])
            assert b['cohort_plan']==layouts[fixture]['plan'];runs.append(b)
        a,b=runs;ratios=dict(complete=b['complete_seconds']/a['complete_seconds'])
        for k in ['iteration','check']:ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
        return dict(pair=n,ratios=ratios,control_seconds=a['complete_seconds'],candidate_seconds=b['complete_seconds'])
    first=pair('large',1);fixtures={'large':dict(pairs=[first])};retained=False
    if first['ratios']['complete']<.99:
        for fixture in ['large','small']:
            ps=([first] if fixture=='large' else [])+[pair(fixture,i) for i in ([2,3] if fixture=='large' else [1,2,3])]
            fixtures[fixture]=dict(pairs=ps,medians={k:statistics.median(p['ratios'][k] for p in ps) for k in ['complete','iteration','check']})
        retained=fixtures['large']['medians']['complete']<=.97 and fixtures['small']['medians']['complete']<=1.03
    regressions={}
    if retained:
        for name,count in [('c13-native-regressions-v1',19),('c13-default-regressions-v1',181)]:
            r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<300
            assert r['solver_source_files']==initial['solver_source_files']
            for p,h in r['inputs'].items():assert digest(p)==h,p
            log=(RAW/(name+'.log')).read_text();assert 'test result: FAILED' not in log
            assert sum(int(v) for v in re.findall(r'test result: ok\. (\d+) passed; 0 failed;',log))==count
            regressions[name]=count
    result=dict(retained=retained,status='Retained - bounded element indices' if retained else 'Rejected - complete-work gate not met',
        fixtures=fixtures,regressions=regressions,source_input_hashes_verified=True,exact_checkpoints_and_arena=True,
        global_allocations_match_C09=True,reference_PTX_matches_C09=True,address_witness=witness,
        compiler_resources=record['resources'],compiler_hashes={p.name:digest(p) for p in sorted(compiler.iterdir())},
        archived_executable_sha256=digest(exe),scope='Same model, samples and float arithmetic. Complete-work throughput only; full convergence and live deployment remain unqualified.')
    target=RAW/'c13-verified.json'
    if target.exists():assert read(target)==result
    else:target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
