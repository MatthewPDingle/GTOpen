"""Independent source, allocation, compiler and paired-result audit of C09."""
import hashlib,json,math,re,statistics,subprocess
from pathlib import Path
from check_c07 import HERE,LAB,RAW,read,digest

def main():
    pre=read(RAW/'c09-numerical-v1-exit.json')
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c09-source-map.json').items()}
    for p,h in pre['solver_source_files'].items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        else:assert hashlib.sha256(subprocess.check_output(['git','show',pre['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p
    prerequisites={}
    for name,expected in [('c09-numerical-v1',5),('c09-reuse-tests-v1',4),('c09-partial-v1',1),('c09-native-regression-v1',19),('c09-default-regression-v1',181)]:
        rec=read(RAW/(name+'-exit.json'));assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=240
        assert rec['solver_source_files']==pre['solver_source_files']
        for p,h in rec['inputs'].items():assert digest(p)==h,p
        log=(RAW/(name+'.log')).read_text(encoding='utf8');counts=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed',log)
        assert counts and all(int(f)==0 for _,f in counts) and sum(int(n) for n,_ in counts)==expected
        prerequisites[name]=dict(passed=expected,seconds=rec['seconds'])
    exe=LAB/'target/c09-benchmark-frozen.exe'
    def evidence(name):
        rec=read(RAW/(name+'-exit.json'));assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
        assert rec['solver_source_files']==pre['solver_source_files'] and rec['exe_sha256']==digest(exe)
        for p,h in rec['inputs'].items():assert digest(p)==h,p
        times=[]
        for side in ['before','after']:
            x=read(RAW/(name+'-gpu-'+side+'.json'));assert x['returncode']==0;times.append(x['time'])
        assert times[0]<times[1]
        return rec,times
    layouts={}
    for fixture in ['small','large']:
        name=f'c09-{fixture}-layout-v1';evidence(name);x=read(RAW/(name+'.json'));old=read(RAW/f'c07-{fixture}-layout-v1.json')
        assert x['unrolled']
        for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
        assert x['actual_device_bytes']==sum(x['buffer_bytes'].values())+x['plan']['extra_bytes']
        layouts[fixture]=x
    summary={}
    for fixture,nodes,age,np in [('large',1567754,1050,8),('small',23038,1000,6)]:
        old=read(RAW/f'c07-{fixture}-candidate-1-bench.json');pairs=[]
        for pair in range(1,4):
            runs={};times={}
            for role in ['control','candidate']:
                name=f'c09-{fixture}-{role}-{pair}';rec,times[role]=evidence(name);x=read(RAW/(name+'-bench.json'))
                assert rec['command'][1:]==['preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark','--exact','--ignored','--nocapture','--test-threads=1']
                assert rec['environment_overrides']['PREFLOP_GPU_TERMINAL_UNROLL']==str(int(role=='candidate'))
                assert x['unrolled']==(role=='candidate') and x['cohorts'] and x['enabled'] and not x['profile']
                assert x['terminal_unroll_factor']==(2 if role=='candidate' else 1)
                assert x['nodes']==nodes and x['initial_iteration']==age and x['iteration']==age+6 and x['batch']==32 and len(x['rows'])==6
                for i,r in enumerate(x['rows']):
                    assert r['index']==i and r['iteration']==age+i+1 and r['warmup']==(i<2)
                    for k in ['gaps','evs']:assert len(r[k])==np and all(math.isfinite(v) for v in r[k])
                    for k in ['iteration_seconds','check_seconds']:assert r[k]>0 and math.isfinite(r[k])
                for k in ['complete_seconds','init_seconds','sync_seconds']:assert x[k]>0 and math.isfinite(x[k])
                assert x['complete_seconds']>=x['init_seconds']+x['sync_seconds']+sum(r['iteration_seconds']+r['check_seconds'] for r in x['rows'])
                for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert x[k]==old[k],(fixture,pair,role,k)
                for a,b in zip(x['rows'],old['rows']):
                    for k in ['gaps','evs','index','warmup','iteration']:assert a[k]==b[k],(fixture,pair,role,k)
                assert x['cohort_plan']==layouts[fixture]['plan']
                runs[role]=x
            first,second=('candidate','control') if pair%2==0 else ('control','candidate');assert times[first][1]<times[second][0]
            a,b=runs['control'],runs['candidate'];ratios=dict(complete=b['complete_seconds']/a['complete_seconds'])
            for k in ['iteration','check']:ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
            pairs.append(dict(pair=pair,ratios=ratios,control_seconds=a['complete_seconds'],candidate_seconds=b['complete_seconds']))
        summary[fixture]=dict(pairs=pairs,median_ratios={k:statistics.median(p['ratios'][k] for p in pairs) for k in ['complete','iteration','check']})
    large=summary['large']['median_ratios']['complete'];small=summary['small']['median_ratios']['complete']
    assert summary['large']['pairs'][0]['ratios']['complete']<.99
    assert large<=.97 and small<=1.03 and all(p['ratios']['complete']<1 for p in summary['large']['pairs'])
    compiler=RAW/'c09-compiler-v1';r=read(compiler/'resources.json')
    assert r['exact'] and r['cases_per_variant']==420 and r['hand_values_per_case']==169
    assert r['opponents']==list(range(2,9)) and r['counts']==[1,7,23,31,32] and r['offsets']==[0,1,37,992]
    assert len(r['resources'])==16 and all(x['local_bytes']==0 for x in r['resources'])
    emission={}
    for o in range(2,9):
        result={}
        for role in ['control','candidate']:
            src=(compiler/(role+'.ptx')).read_text(encoding='utf8');body=src.split(f'.visible .entry audit_{o}(')[1].split('.visible .entry')[0]
            increments=re.findall(r'add.s32\s+%r\d+, %r\d+, (-?\d+);',body)
            assert '-2' in increments if role=='candidate' or o<=3 else '-2' not in increments
            result[role]=dict(ptx_bytes=len(body),float_loads=len(re.findall(r'ld.global.f32',body)),fmas=len(re.findall(r'fma.rn.f32',body)),loop_increments=increments)
        emission[str(o)]=result
    result=dict(retained=True,status='Retained - partial terminal unrolling',display_gain=f'{100*(1-large):.1f}% less time vs C07',
        fixtures=summary,prerequisites=prerequisites,source_input_hashes_verified=True,exact_checkpoints_and_arena=True,
        global_allocation_matches_C07=True,allocated_device_bytes=layouts['large']['actual_device_bytes'],
        archived_executable_sha256=digest(exe),compiler_artifact_hashes={f.name:digest(f) for f in compiler.iterdir()},compiler_emission=emission,
        numerical='All 12 paired runs match C07 at every checkpoint and final arena fingerprint. Full arenas, terminal/prefix bits, locked/frozen seats, zero recovery, capture and 420 direct partial batches per variant also pass.',
        scope='Fixed-work GPU throughput only. Small complete runs are short/noisy: median +1.8%, worst pair +6.0%. Compiler attributes come from the diagnostic base terminal and helper wrappers, not measured C01/C07 runtime functions. No full convergence claim or deployment to 56708.')
    (RAW/'c09-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k!='compiler_emission'},indent=2))
if __name__=='__main__':main()
