"""Audit C07 phase diagnostics without interpreting them as a speed result."""
import collections,hashlib,json,math,statistics,subprocess
from check_c07 import HERE,LAB,RAW,read,digest

def main():
    pre=read(RAW/'d06-numerical-v1-exit.json');reuse=read(RAW/'d06-reuse-tests-v1-exit.json')
    for x in [pre,reuse]:assert x['returncode']==0 and x['reason'] is None and x['seconds']<=240
    assert pre['solver_source_files']==reuse['solver_source_files']
    assert '5 passed; 0 failed; 1 ignored' in (RAW/'d06-numerical-v1.log').read_text()
    assert '4 passed; 0 failed; 1 ignored' in (RAW/'d06-reuse-tests-v1.log').read_text()
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/d06-source-map.json').items()}
    for p,h in pre['solver_source_files'].items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        else:
            blob=subprocess.check_output(['git','show',pre['source_commit']+':'+Path(p).as_posix()],cwd=LAB)
            assert hashlib.sha256(blob).hexdigest()==h,p
    exe=LAB/'target/d06-profile-frozen.exe';fixtures={}
    for fixture,nodes,age,np in [('small',23038,1000,6),('large',1567754,1050,8)]:
        runs=[]
        for profile in [False,True]:
            name=f'd06-{fixture}-'+('profiled' if profile else 'control')+'-v1'
            rec=read(RAW/(name+'-exit.json'));b=read(RAW/(name+'.json'))
            assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
            assert rec['solver_source_files']==pre['solver_source_files'] and rec['exe_sha256']==digest(exe)
            for p,h in rec['inputs'].items():assert digest(exe if p==rec['command'][0] else Path(p))==h,p
            assert rec['environment_overrides']['PREFLOP_GPU_REUSE_PROFILE']==str(int(profile))
            assert b['enabled'] and b['cohorts'] and b['profile']==profile and b['nodes']==nodes and b['initial_iteration']==age and b['iteration']==age+6 and b['batch']==32
            groups=len(b['cohort_plan']['groups']);assert groups==(2 if fixture=='small' else 3)
            assert b['cohort_plan']==read(RAW/f'c07-{fixture}-layout-v1.json')['plan']
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
        a,b=runs;old=read(RAW/f'c07-{fixture}-candidate-1-bench.json')
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
        fixtures[fixture]=dict(operations=ops,control_complete_seconds=a['complete_seconds'],profiled_complete_seconds=b['complete_seconds'])
    result=dict(status='Diagnosis complete - shared-check phase breakdown',kind='diagnostic',verified=True,fixtures=fixtures,
        source_input_hashes_verified=True,exact_checkpoints_and_arenas=True,archived_C07_outputs_match=True,
        scope='Eager events only. No new speed or convergence claim. Port 56708 unchanged.',executable_sha256=digest(exe))
    (RAW/'d06-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result,indent=2))

from pathlib import Path
if __name__=='__main__':main()
