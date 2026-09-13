"""Independent C17 source, compiler, exact-state and paired timing audit."""
import json,math,statistics,hashlib,subprocess
from pathlib import Path
from check_r03_saved import HERE,RAW,LAB,read,sha
from check_d09 import entries

def main():
    kernel=read(RAW/'c17-kernel-v1-exit.json');source=kernel['solver_source_files']
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c17-v1-source-map.json').items()}
    for f,h in source.items():
        if f in mapping:assert sha(HERE/mapping[f]['archive'])==mapping[f]['sha256']==h,f
        else:assert hashlib.sha256(subprocess.check_output(['git','show',kernel['source_commit']+':'+Path(f).as_posix()],cwd=LAB)).hexdigest()==h,f
    def evidence(name,cap):
        r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<cap
        assert r['solver_source_files']==source
        for f,h in r['inputs'].items():assert sha(f)==h,f
        return r
    evidence('c17-kernel-v1',300);assert '1 passed; 0 failed' in (RAW/'c17-kernel-v1.log').read_text(encoding='utf8')
    k=read(RAW/'c17-compiler-v1/results.json');assert k['exact'] and k['guarded'] and k['zero_recovery'] and k['cases']==2*8*7*6*3*2
    assert k['task_counts']==[1,2,3,4,5,7,8,9] and k['opponents']==list(range(2,9))
    for r in k['resources']:assert r['registers']==40 and r['local_bytes']==0 and r['shared_bytes']==(176 if r['packed'] else 44)
    changed={}
    for kind,name in [('exact','pf_exact_reuse_terminal'),('cohort','pf_cohort_terminal')]:
        folder=RAW/'c17-compiler-v1';control=(folder/(kind+'-control.ptx')).read_text(encoding='utf8');candidate=(folder/(kind+'-candidate.ptx')).read_text(encoding='utf8')
        assert control==(RAW/('r03-compiler-v2/'+kind+'-candidate.ptx')).read_text(encoding='utf8')
        a,b=entries(control),entries(candidate);assert a.keys()==b.keys();changed[kind]=[key for key in a if a[key]!=b[key]];assert changed[kind]==[name]
        sa=(folder/(kind+'-control.cu')).read_text(encoding='utf8');sb=(folder/(kind+'-candidate.cu')).read_text(encoding='utf8');marker='extern "C" __global__ void '+name+'('
        before,body=sa.split(marker,1);end=body.index('\n}\n')+3
        assert sb.startswith(before+marker) and sb.endswith(body[end:])
    evidence('c17-numerical-v1',300);assert '6 passed; 0 failed; 1 ignored' in (RAW/'c17-numerical-v1.log').read_text(encoding='utf8')
    assert read(RAW/'c17-numerical-v1-exit.json')['environment_overrides']['PREFLOP_GPU_WARP_TERMINALS']=='1'
    exe=LAB/'target/c17-benchmark-frozen.exe'
    for fixture in ['small','large']:
        name=f'c17-{fixture}-layout-v1';r=evidence(name,180);x=read(RAW/(name+'.json'));old=read(RAW/f'c14-{fixture}-layout-v1.json')
        assert r['exe_sha256']==sha(exe) and x['packed_terminals'] and x['unrolled'] and x['narrow_offsets']
        for key in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[key]==old[key],key
    pairs={}
    for fixture in ['large','small']:
        rows=[];old=read(RAW/f'c14-{fixture}-candidate-1-bench.json')
        for pair in [1,2,3]:
            if not (RAW/f'c17-{fixture}-candidate-{pair}-bench.json').exists():continue
            a,b=[read(RAW/f'c17-{fixture}-{role}-{pair}-bench.json') for role in ['control','candidate']]
            for role,x in [('control',a),('candidate',b)]:
                name=f'c17-{fixture}-{role}-{pair}';r=evidence(name,180);assert r['exe_sha256']==sha(exe)
                assert r['environment_overrides']['PREFLOP_GPU_WARP_TERMINALS']==str(int(role=='candidate'))
                assert x['packed_terminals']==(role=='candidate') and x['narrow_offsets'] and x['cohorts'] and x['enabled'] and not x['profile'] and not x['production_selection']
                assert len(x['rows'])==6
                for i,row in enumerate(x['rows']):
                    assert row['index']==i and row['iteration']==x['initial_iteration']+i+1 and row['warmup']==(i<2)
                    for key in ['gaps','evs']:assert len(row[key])==x['players'] if 'players' in x else len(row[key])==len(old['rows'][i][key])
                    assert all(math.isfinite(v) for key in ['gaps','evs'] for v in row[key])
                    assert all(math.isfinite(row[key]) and row[key]>0 for key in ['iteration_seconds','check_seconds'])
                assert x['complete_seconds']>=x['init_seconds']+x['sync_seconds']+sum(z['iteration_seconds']+z['check_seconds'] for z in x['rows'])
                for side in ['before','after']:assert read(RAW/(name+'-gpu-'+side+'.json'))['returncode']==0
            for key in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[key]==b[key]==old[key],key
            for x,y,z in zip(a['rows'],b['rows'],old['rows']):
                for key in ['gaps','evs','index','iteration','warmup']:assert x[key]==y[key]==z[key],key
            ratios={'complete':b['complete_seconds']/a['complete_seconds']}
            for key in ['iteration','check']:ratios[key]=statistics.median(z[key+'_seconds'] for z in b['rows'][2:])/statistics.median(z[key+'_seconds'] for z in a['rows'][2:])
            rows.append({'pair':pair,'ratios':ratios,'control_seconds':a['complete_seconds'],'candidate_seconds':b['complete_seconds']})
        pairs[fixture]=rows
    assert pairs['large'];passed=pairs['large'][0]['ratios']['complete']<.99
    allpairs=all(len(pairs[f])==3 for f in pairs)
    median={f:{key:statistics.median(x['ratios'][key] for x in runs) for key in ['complete','iteration','check']} for f,runs in pairs.items() if runs}
    timing=allpairs and median['large']['complete']<=.97 and median['small']['complete']<=1.03
    if not passed:
        assert not subprocess.check_output(['git','diff','9c242ce','--','crates'],cwd=LAB)
        assert not (LAB/'crates/solver/src/preflop/gpu/warp_terminals.rs').exists()
    assert sha(LAB/'target/r03-v3-server-frozen.exe')==read(RAW/'r03-release-verified.json')['executable_sha256']
    result={'retained':False,'status':'Timing gate passed; full regression qualification required' if timing else ('First timing screen passed; extended pairs required' if passed else 'Rejected - first-pair timing screen'),
        'first_screen_passed':passed,'timing_gate_passed':timing,'pairs':pairs,'median_ratios':median,'kernel_cases':4032,'expanded_tests':6,'exact_checkpoints_and_arena':True,
        'source_input_hashes_verified':True,'other_kernel_entries_unchanged':True,'global_allocation_matches_C14':True,'runtime_restored':not passed,'executable_sha256':sha(exe),
        'scope':'Fixed-work throughput qualification only; no convergence gain or deployment. A timing pass alone is not retention.'}
    target=RAW/'c17-verified.json';target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
