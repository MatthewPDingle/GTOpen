"""Fail-closed audit of all C07 pairs and required regression evidence."""
import json,math,re,statistics
from check_c07 import HERE,LAB,RAW,read,digest,check_layouts,evidence

def main():
    pre,layouts=check_layouts();summary={}
    for fixture,nodes,age,np in [('large',1567754,1050,8),('small',23038,1000,6)]:
        pairs=[]
        for pair in range(1,4):
            runs={};times={}
            for role in ['control','candidate']:
                name=f'c07-{fixture}-{role}-{pair}';rec=evidence(name,pre);x=read(RAW/(name+'-bench.json'))
                assert rec['command'][1:]==['preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark','--exact','--ignored','--nocapture','--test-threads=1']
                assert rec['environment_overrides']['PREFLOP_GPU_COHORT_ENABLE']==str(int(role=='candidate'))
                assert x['cohorts']==(role=='candidate') and x['enabled'] and not x['profile'] and x['batch']==32
                assert x['nodes']==nodes and x['initial_iteration']==age and x['iteration']==age+6 and len(x['rows'])==6
                for i,r in enumerate(x['rows']):
                    assert r['index']==i and r['iteration']==age+i+1 and r['warmup']==(i<2)
                    for k in ['gaps','evs']:assert len(r[k])==np and all(math.isfinite(v) for v in r[k])
                    for k in ['iteration_seconds','check_seconds']:assert r[k]>0 and math.isfinite(r[k])
                for k in ['complete_seconds','init_seconds','sync_seconds']:assert x[k]>0 and math.isfinite(x[k])
                assert x['complete_seconds']>=x['init_seconds']+x['sync_seconds']+sum(r['iteration_seconds']+r['check_seconds'] for r in x['rows'])
                times[role]=[read(RAW/(name+'-gpu-'+side+'.json'))['time'] for side in ['before','after']]
                assert times[role][0]<times[role][1]
                runs[role]=x
            first,second=('candidate','control') if pair%2==0 else ('control','candidate')
            assert times[first][1]<times[second][0],(fixture,pair,'order or overlapping invocations')
            a,b=runs['control'],runs['candidate']
            for k in ['input','nodes','initial_iteration','iteration','batch','arena_entries','arena_fingerprint','original_cdf_bytes']:assert a[k]==b[k],(fixture,pair,k)
            for x,y in zip(a['rows'],b['rows']):
                for k in ['gaps','evs','index','warmup','iteration']:assert x[k]==y[k],(fixture,pair,k)
            assert b['cohort_plan']==layouts[fixture]['plan']
            assert b['cdf_bytes']==layouts[fixture]['buffer_bytes']['d_mw_cdf']
            extra=b['cohort_plan']['extra_bytes']+layouts[fixture]['buffer_bytes']['d_mw_normalized']-b['original_cdf_bytes']//(32*170)*169
            assert b['extra_bytes']==extra
            ratios=dict(complete=b['complete_seconds']/a['complete_seconds'])
            for k in ['iteration','check']:ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
            pairs.append(dict(pair=pair,ratios=ratios,control_seconds=a['complete_seconds'],candidate_seconds=b['complete_seconds']))
        summary[fixture]=dict(pairs=pairs,median_ratios={k:statistics.median(p['ratios'][k] for p in pairs) for k in ['complete','iteration','check']})
    large=summary['large']['median_ratios']['complete'];small=summary['small']['median_ratios']['complete']
    assert large<=.97 and small<=1.03 and all(p['ratios']['complete']<1 for p in summary['large']['pairs'])
    prerequisites={}
    for name,expected in [('c07-numerical-v1',4),('c07-reuse-regression-v1',4),('c07-native-regression-v1',19),('c07-default-regression-v1',None)]:
        rec=read(RAW/(name+'-exit.json'));assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=240
        assert rec['solver_source_files']==pre['solver_source_files']
        for p,h in rec['inputs'].items():assert digest(p)==h,p
        log=(RAW/(name+'.log')).read_text();counts=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed',log)
        assert counts and all(int(f)==0 for _,f in counts)
        passed=sum(int(n) for n,_ in counts)
        assert passed==expected if expected is not None else passed>=100
        prerequisites[name]=dict(passed=passed,seconds=rec['seconds'])
    result=dict(retained=True,status='Retained - bounded check cohorts',display_gain=f'{100*(1-large):.1f}% less time vs C01',
        fixtures=summary,prerequisites=prerequisites,source_input_hashes_verified=True,exact_checkpoints_and_arena=True,
        allocation_matches_static_preflight=True,allocated_device_bytes=layouts['large']['actual_device_bytes'],
        archived_executable_sha256=digest(LAB/'target/c07-benchmark-frozen.exe'),
        numerical='All 12 paired runs agree in every checkpoint gap/EV and final arena fingerprint. Small adversarial tests compare arena, terminal and prefix bits, including errors and recovery.',
        scope='Fixed-work GPU throughput; opt-in research constructor only. No full convergence qualification or deployment to 56708. Small complete-time runs are short and noisy; median and pair range are reported.')
    (RAW/'c07-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
