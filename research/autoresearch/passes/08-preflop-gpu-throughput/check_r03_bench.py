"""Independent overhead gate; a failed integration is not retained speed progress."""
import json,statistics,sys
from pathlib import Path
from check_r03_saved import HERE,RAW,LAB,read,sha

def main():
    version=sys.argv[1] if len(sys.argv)>1 else 'v2';assert version in ['v2','v3']
    prefix='r03-bench' if version=='v2' else 'r03-v3-bench'
    exe=LAB/('target/r03-qualification-frozen.exe' if version=='v2' else 'target/r03-v3-qualification-frozen.exe')
    source=read(RAW/f'r03-selection-tests-{version}-exit.json')['solver_source_files']
    fixtures={}
    for fixture in ['small','large']:
        pairs=[];old=read(RAW/f'c14-{fixture}-candidate-1-bench.json')
        for pair in [1,2,3]:
            runs={}
            for role in ['retained','adaptive']:
                name=f'{prefix}-{fixture}-{role}-{pair}';r=read(RAW/(name+'-exit.json'));x=read(RAW/(name+'.json'))
                assert r['returncode']==0 and r['reason'] is None and 0<r['seconds']<180
                assert r['solver_source_files']==source and r['exe_sha256']==sha(exe)
                for p,h in r['inputs'].items():assert sha(p)==h,p
                for side in ['before','after']:assert read(RAW/(name+'-gpu-'+side+'.json'))['returncode']==0
                assert r['environment_overrides']['PREFLOP_GPU_PRODUCTION_SELECTION']==str(int(role=='adaptive'))
                assert x['production_selection']==(role=='adaptive') and x['narrow_offsets'] and len(x['rows'])==6
                for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert x[k]==old[k],k
                for a,b in zip(x['rows'],old['rows']):
                    for k in ['index','iteration','gaps','evs','warmup']:assert a[k]==b[k],k
                assert x['complete_seconds']>=x['init_seconds']+x['sync_seconds']+sum(a['iteration_seconds']+a['check_seconds'] for a in x['rows'])
                if role=='adaptive':assert x['selection']['mode']=='retained_cohorts' and x['selection']['narrow_offsets']
                else:assert x['selection'] is None
                runs[role]=x
            pairs.append(dict(pair=pair,ratio=runs['adaptive']['complete_seconds']/runs['retained']['complete_seconds'],
                retained_seconds=runs['retained']['complete_seconds'],adaptive_seconds=runs['adaptive']['complete_seconds'],
                retained_init=runs['retained']['init_seconds'],adaptive_init=runs['adaptive']['init_seconds']))
        median=statistics.median(p['ratio'] for p in pairs)
        fixtures[fixture]=dict(pairs=pairs,median=median,passed=median<=1.03)
    result=dict(version=version,passed=all(f['passed'] for f in fixtures.values()),fixtures=fixtures,
        exact=True,source_input_executable_hashes_checked=True,scope='Integration overhead versus explicit C14, not an additional speedup.')
    target=RAW/f'r03-overhead-{version}-verified.json'
    if target.exists():assert read(target)==result
    else:target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
