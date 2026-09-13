"""Audit rollout qualification separately from candidate speed retention."""
import hashlib
import json
import math
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    records=[]
    first=None
    for name,version,expected in [('r03-production-selection-v1','v1','1 passed; 0 failed'),
            ('r03-bounds-partials-v2','v2','2 passed; 0 failed'),('r03-numerical-v2','v2','6 passed; 0 failed; 1 ignored'),
            ('r03-reuse-tests-v2','v2','4 passed; 0 failed; 1 ignored'),('r03-selection-tests-v2','v2','3 passed; 0 failed; 1 ignored')]:
        r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<300
        assert expected in (RAW/(name+'.log')).read_text()
        mapping={str(Path(k)):v for k,v in read(HERE/f'artifacts/r03-{version}-source-map.json').items()}
        for f,h in r['solver_source_files'].items():
            if f in mapping:assert sha(HERE/mapping[f])==h,f
            else:assert hashlib.sha256(subprocess.check_output(['git','show',r['source_commit']+':'+Path(f).as_posix()],cwd=LAB)).hexdigest()==h,f
        for f,h in r['inputs'].items():assert sha(f)==h,f
        if first is None:first=r
        elif records:assert r['solver_source_files']==records[-1]['solver_source_files']
        if version=='v2':records.append(r)
    changes={Path(f).as_posix() for f,h in first['solver_source_files'].items() if h!=records[-1]['solver_source_files'][f]}
    assert changes=={'crates/solver/src/preflop/gpu/exact_reuse/tests.rs','crates/solver/src/preflop/gpu/adaptive_throughput/allocation_recovery.rs'}
    for kind in ['exact','cohort']:
        for variant in ['control','candidate']:
            assert sha(RAW/'r03-compiler-v2'/f'{kind}-{variant}.ptx')==sha(RAW/'c14-compiler-v1'/f'{kind}-{variant}.ptx')
    resource=read(RAW/'r03-compiler-v2/resources.json')
    assert resource['exact'] and resource['cases_per_variant']==420 and resource['hand_values_per_case']==169
    import re
    witnesses=[json.loads(row) for row in re.findall(r'R02_RECOVERY (\{[^\n]+\})',(RAW/'r03-selection-tests-v2.log').read_text())]
    assert [x['narrow'] for x in witnesses]==[False,True]
    for w in witnesses:
        assert w['selection']['mode']=='normal_gpu' and not w['selection']['narrow_offsets']
        assert len(w['events'])==1 and 'CUDA_ERROR_OUT_OF_MEMORY' in w['events'][0]['error']
        assert w['events'][0]['requested_bytes']==2**50 and w['events'][0]['partial_extra_bytes']>0
        assert w['fallback_memory']['used']==w['before']['used']+w['normal_allocation_bytes']
        assert w['after_drop']['used']==w['after_retry']['used']==w['before']['used']
        assert w['full_arenas_roots_gap_ev_equal'] and w['captured_stop_sync_equal'] and w['retry_optimized_succeeded']
    sources=records[-1]['solver_source_files'];exe=LAB/'target/r03-qualification-frozen.exe'
    results={}
    for fixture,np,age,nodes in [('small',6,1000,23038),('large',8,1050,1567754)]:
        rows={}
        for mode in ['retained','adaptive','normal','fallback']:
            name=f'r03-{fixture}-{mode}-v1';r=read(RAW/(name+'-exit.json'));x=read(RAW/(name+'.json'))
            assert r['returncode']==0 and r['reason'] is None and 0<r['seconds']<240
            assert r['solver_source_files']==sources and r['exe_sha256']==sha(exe)
            for p,h in r['inputs'].items():assert sha(p)==h,p
            for side in ['before','after']:assert read(RAW/(name+'-gpu-'+side+'.json'))['returncode']==0
            assert r['environment_overrides']['PREFLOP_GPU_ROLLOUT_MODE']==mode
            assert x['mode']==mode and x['nodes']==nodes and x['initial_iteration']==age
            assert x['continued_iteration']==age+7 and len(x['rows'])==6
            assert x['metadata_preserved'] and x['save_reload_arenas_bitwise_equal']
            save=Path(x['save']).resolve();assert save.is_relative_to((LAB/'target').resolve()) and save.exists()
            for i,row in enumerate(x['rows']):
                assert row['index']==i and row['iteration']==age+1+i
                for k in ['gaps','evs']:assert len(row[k])==np and all(math.isfinite(v) for v in row[k])
                assert row['iteration_seconds']>0 and row['check_seconds']>0
            assert x['six_step_seconds']>=x['init_seconds']+sum(row['iteration_seconds']+row['check_seconds'] for row in x['rows'])
            for k in ['continued_gaps','continued_evs']:assert len(x[k])==np and all(math.isfinite(v) for v in x[k])
            for key in ['selection','reload_selection']:
                report=x[key]
                if mode in ['retained','normal']:assert report is None
                else:
                    assert report['configured_budget_mb']==23000
                    assert report['mode']==('retained_cohorts' if mode=='adaptive' else 'normal_gpu')
                    assert report['cohort_limit_mb']==(20500 if mode=='adaptive' else 1)
                    assert (report['fallback_reason'] is None)==(mode=='adaptive')
                    assert report['narrow_offsets']==(mode=='adaptive')
            rows[mode]=x
        reference=rows['retained'];old=read(RAW/f'c14-{fixture}-candidate-1-bench.json');previous=read(RAW/f'r01-{fixture}-retained-v1.json')
        for mode,x in rows.items():
            for key in ['arena_fingerprint','continued_fingerprint','continued_gaps','continued_evs']:
                assert x[key]==reference[key],(fixture,mode,key)
            assert x['arena_fingerprint']==old['arena_fingerprint']
            assert x['continued_fingerprint']==previous['continued_fingerprint']
            assert x['continued_gaps']==previous['continued_gaps'] and x['continued_evs']==previous['continued_evs']
            assert x['layout']['narrow_offsets']==(mode in ['retained','adaptive'])
            assert x['layout']['batch']==old['batch']
            for a,b,c in zip(x['rows'],reference['rows'],old['rows']):
                for key in ['iteration','gaps','evs']:assert a[key]==b[key]==c[key],(fixture,mode,key)
        assert rows['adaptive']['layout']==rows['retained']['layout']
        assert rows['fallback']['layout']==rows['normal']['layout']
        assert rows['retained']['layout']['cohort']==old['cohort_plan']
        saves={mode:dict(path=x['save'],sha256=sha(x['save'])) for mode,x in rows.items()}
        assert len({x['sha256'] for x in saves.values()})==1,fixture
        results[fixture]=dict(arena_fingerprint=reference['arena_fingerprint'],continued_fingerprint=reference['continued_fingerprint'],
            all_four_modes_match=True, saved_files=saves,
            observed_six_step_seconds={mode:x['six_step_seconds'] for mode,x in rows.items()})
    result=dict(status='Saved-game production-path qualification passed', source_input_hashes_verified=True,
        saved_fixture_results=results, optimized_and_fallback_keep_reference_grouping=True,
        scope='Public production selection and explicit/reference/fallback paths match saved-game continuation. PTX and actual allocation-error recovery verified. Complete-work overhead, full regressions and isolated-server checks remain required; no deployment or new speed claim.')
    target=RAW/'r03-saved-verified.json'
    if target.exists():assert read(target)==result
    else:target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
