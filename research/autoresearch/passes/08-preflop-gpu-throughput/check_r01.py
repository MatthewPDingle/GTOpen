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
    for version in [1,2]:
        name=f'r01-selection-tests-v{version}';r=read(RAW/(name+'-exit.json'))
        assert r['returncode']==0 and r['reason'] is None and r['seconds']<300
        assert '2 passed; 0 failed' in (RAW/(name+'.log')).read_text()
        mapping=read(HERE/'artifacts/r01-selection-v1-map.json') if version==1 else {}
        for p,h in r['solver_source_files'].items():
            posix=Path(p).as_posix()
            target=HERE/mapping[posix] if posix in mapping else LAB/p
            assert sha(target)==h,p
        for p,h in r['inputs'].items():assert sha(p)==h,p
        records.append(r)
    sources=records[-1]['solver_source_files'];exe=LAB/'target/r01-qualification-frozen.exe'
    results={}
    for fixture,np,age,nodes in [('small',6,1000,23038),('large',8,1050,1567754)]:
        rows={}
        for mode in ['retained','adaptive','normal','fallback']:
            name=f'r01-{fixture}-{mode}-v1';r=read(RAW/(name+'-exit.json'));x=read(RAW/(name+'.json'))
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
            rows[mode]=x
        reference=rows['retained'];old=read(RAW/f'c09-{fixture}-candidate-1-bench.json')
        for mode,x in rows.items():
            for key in ['arena_fingerprint','continued_fingerprint','continued_gaps','continued_evs']:
                assert x[key]==reference[key],(fixture,mode,key)
            assert x['arena_fingerprint']==old['arena_fingerprint']
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
    result=dict(status='Initial rollout qualification passed', source_input_hashes_verified=True,
        saved_fixture_results=results, optimized_and_fallback_keep_reference_grouping=True,
        scope='Opt-in research constructor only. Error injection and synthetic low memory do not prove recovery from a real device allocation failure. Full regressions and production integration remain required. Single diagnostic timings are not a new speed claim.')
    target=RAW/'r01-verified.json'
    if target.exists():assert read(target)==result
    else:target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
