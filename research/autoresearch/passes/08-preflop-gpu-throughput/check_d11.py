"""Audit C14 phase diagnostics without interpreting them as a speed result."""
import collections,hashlib,json,math,statistics,subprocess
from check_c07 import HERE,LAB,RAW,read,digest

def main():
    pre=read(RAW/'d11-tracing-v1-exit.json')
    assert pre['returncode']==0 and pre['reason'] is None and pre['seconds']<=300
    assert pre['source_commit']=='7e1fe7f19e76c02d8a1d93758183faba1d29d6c5'
    assert '1 passed; 0 failed; 0 ignored' in (RAW/'d11-tracing-v1.log').read_text()
    for p,h in pre['inputs'].items(): assert digest(Path(p))==h,p
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/d11-v1-source-map.json').items()}
    for p,h in pre['solver_source_files'].items():
        if p in mapping:assert digest(HERE/mapping[p]['archive'])==mapping[p]['sha256']==h,p
        else:
            blob=subprocess.check_output(['git','show',pre['source_commit']+':'+Path(p).as_posix()],cwd=LAB)
            assert hashlib.sha256(blob).hexdigest()==h,p
    exe=LAB/'target/d11-profile-frozen.exe';fixtures={}
    for fixture,nodes,age,np in [('small',23038,1000,6),('large',1567754,1050,8)]:
        runs=[]
        for profile in [False,True]:
            name=f'd11-{fixture}-'+('profiled' if profile else 'control')+'-v1'
            rec=read(RAW/(name+'-exit.json'));b=read(RAW/(name+'.json'))
            assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
            assert rec['solver_source_files']==pre['solver_source_files'] and rec['exe_sha256']==digest(exe)
            for p,h in rec['inputs'].items():assert digest(exe if p==rec['command'][0] else Path(p))==h,p
            assert rec['environment_overrides']['PREFLOP_GPU_REUSE_PROFILE']==str(int(profile))
            assert b['enabled'] and b['cohorts'] and b['profile']==profile and b['nodes']==nodes and b['initial_iteration']==age and b['iteration']==age+6 and b['batch']==32
            groups=len(b['cohort_plan']['groups']);assert groups==(2 if fixture=='small' else 3)
            assert b['cohort_plan']==read(RAW/f'c14-{fixture}-candidate-1-bench.json')['cohort_plan']
            assert b['narrow_offsets'] and b['unrolled']
            for flag in ['PREFLOP_GPU_REUSE_ENABLE','PREFLOP_GPU_COHORT_ENABLE','PREFLOP_GPU_TERMINAL_UNROLL','PREFLOP_GPU_NARROW_OFFSETS']:
                assert rec['environment_overrides'][flag]=='1'
            assert len(b['rows'])==6
            for i,r in enumerate(b['rows']):
                assert r['index']==i and r['iteration']==age+i+1 and r['warmup']==(i<2)
                for k in ['gaps','evs']:assert len(r[k])==np and all(math.isfinite(v) for v in r[k])
                for k in ['iteration_phases','check_phases']:
                    v=r[k]
                    if not profile:assert v is None;continue
                    average=k=='check_phases';assert v['execution']=='eager_cuda_events'
                    rows=v['rows'];total=v['gpu_ms'];assert math.isfinite(total) and total>0
                    assert all(math.isfinite(x['ms']) and x['ms']>=0 and x['intervals']>0 for x in rows)
                    assert abs(sum(x['ms'] for x in rows)-v['interval_sum_ms'])<1e-6
                    assert abs(total-v['interval_sum_ms'])<1+total*.001
                    counts=collections.Counter()
                    for x in rows:counts[x['phase']]+=x['intervals']
                    for phase in ['prepare','ordinary_terminals']:assert counts[phase]==np
                    for phase in ['normalize','classify']:assert counts[phase]==(groups if average else np)
                    assert counts['cdf']==(groups if average else np)*32
                    assert counts['coupled_terminals']==np*32
                    assert counts['down']==(1 if average else np)
                    for phase in ['up_average','up_br']:assert counts[phase]==(np if average else 0)
                    assert counts['up_learn']==(0 if average else np)
                    assert counts['root_copy']==(np*2 if average else 0)
                    assert counts['scratch_restore']==int(average)
            runs.append(b)
        a,b=runs;old=read(RAW/f'c14-{fixture}-candidate-1-bench.json')
        for k in ['input','nodes','iteration','initial_iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k]==old[k],(fixture,k)
        for x,y,z in zip(a['rows'],b['rows'],old['rows']):
            for k in ['index','iteration','warmup','gaps','evs']:assert x[k]==y[k]==z[k],(fixture,k)
        ops={}
        for key in ['iteration_phases','check_phases']:
            times=collections.defaultdict(list);shares=collections.defaultdict(list)
            for row in b['rows'][2:]:
                totals=collections.defaultdict(float)
                for x in row[key]['rows']:totals[x['phase']]+=x['ms']
                for k,v in totals.items():times[k].append(v);shares[k].append(v/row[key]['gpu_ms'])
            ops[key]=dict(median_total_ms=statistics.median(row[key]['gpu_ms'] for row in b['rows'][2:]),
                phases={k:dict(median_ms=statistics.median(v),median_share=statistics.median(shares[k])) for k,v in times.items()})
        for key,op in ops.items():
            combined=[]
            for row in b['rows'][2:]:
                v=row[key]
                combined.append(sum(x['ms'] for x in v['rows'] if x['phase'] in ['cdf','coupled_terminals'])/v['gpu_ms'])
            f=statistics.median(combined)
            for phase in op['phases'].values():phase['ideal_total_speedup_if_free']=1/(1-phase['median_share'])
            op['combined_cdf_terminal_share']=f
            op['ideal_total_speedup_if_both_free']=1/(1-f)
            op['required_combined_speedup_for_10x']=f/(f-.9) if f>.9 else None
        fixtures[fixture]=dict(operations=ops,control_complete_seconds=a['complete_seconds'],profiled_complete_seconds=b['complete_seconds'])
    import d11_work_census
    import contextlib,io
    with contextlib.redirect_stdout(io.StringIO()):d11_work_census.main()
    census=read(RAW/'d11-work-census.json')
    for p,h in census['sources'].items():assert digest(RAW/p)==h,p
    result=dict(status='Diagnosis complete - retained C14 cost breakdown',kind='diagnostic',verified=True,fixtures=fixtures,
        source_input_hashes_verified=True,exact_checkpoints_and_arenas=True,archived_C14_outputs_match=True,
        independent_work_census_verified=True,work_census_sha256=digest(RAW/'d11-work-census.json'),
        scope='Eager events and logical snapshot counts only. Amdahl assumes other phases fixed; no new speed or convergence claim. Port 56708 unchanged.',executable_sha256=digest(exe))
    dest=RAW/'d11-verified.json'
    if dest.exists():assert read(dest)==result
    else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result,indent=2))

from pathlib import Path
if __name__=='__main__':main()
