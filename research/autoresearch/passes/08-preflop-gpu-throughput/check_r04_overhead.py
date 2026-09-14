"""Verify all integration overhead pairs against the frozen qualified source."""
import hashlib
import json
import statistics
from pathlib import Path
from run_c23 import HERE, RAW, read

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    initial=read(RAW/'r04-initial-verified.json');fixtures={}
    for fixture in ['small','large']:
        pairs=[];reference=read(RAW/f'c23-{fixture}-candidate-{2 if fixture=="large" else 1}-bench.json')
        for pair in [1,2,3]:
            values={}
            for role in ['control','candidate']:
                name=f'r04-{fixture}-{role}-{pair}';r=read(RAW/(name+'-exit.json'))
                assert r['returncode']==0 and r['reason'] is None and r['seconds']<=180
                assert r['exe_sha256']==initial['executable_sha256'] and r['solver_source_files']==initial['solver_source_files']
                for p,h in r['inputs'].items():assert sha(p)==h,p
                assert r['environment_overrides']['PREFLOP_GPU_PRODUCTION_SELECTION']==str(int(role=='candidate'))
                assert r['environment_overrides']['PREFLOP_GPU_STATIC_CDF']==str(int(role=='control'))
                x=read(RAW/(name+'-bench.json'));values[role]=x
                for k in ['input','nodes','initial_iteration','iteration','arena_entries','arena_fingerprint','batch','cdf_bytes','static_cdf','cohort_plan']:
                    assert x[k]==reference[k],(name,k)
                assert len(x['rows'])==6
                for a,b in zip(x['rows'],reference['rows']):
                    for k in ['gaps','evs','iteration','index','warmup']:assert a[k]==b[k],(name,k)
                if role=='candidate':
                    s=x['selection'];assert s['static_cdf'] and s['narrow_offsets'] and s['mode']=='retained_cohorts'
                    assert s['fallback_reason'] is None and s['static_cdf_fallback_reason'] is None
                else:assert x['selection'] is None
            a,b=values['control'],values['candidate']
            pairs.append({'pair':pair,'ratio':b['complete_seconds']/a['complete_seconds'],'control_seconds':a['complete_seconds'],'candidate_seconds':b['complete_seconds']})
        fixtures[fixture]={'pairs':pairs,'median_ratio':statistics.median(p['ratio'] for p in pairs)}
    passed=all(x['median_ratio']<=1.03 for x in fixtures.values())
    result={'verified':True,'passed':passed,'admitted':passed,'retained':False,'deployed':False,
        'status':'Normal app overhead passed; saved-session/server qualification next' if passed else 'Normal app overhead failed',
        'fixtures':fixtures,'exact_checkpoints_and_arena':True,'executable_sha256':initial['executable_sha256'],
        'scope':'Integration overhead only. No additional gain credited. Default/server regressions, saved-fixture continuation and isolated-server qualification remain.'}
    dest=RAW/'r04-overhead-verified.json'
    if dest.exists():assert read(dest)==result
    else:dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (RAW/'r04-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
