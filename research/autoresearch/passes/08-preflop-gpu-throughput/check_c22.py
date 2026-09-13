"""Independent first complete-work pair and exact saved-state audit."""
import hashlib,json,statistics
from pathlib import Path
from check_c22_integration import main as integration_audit
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    integration_audit();qualified=read(RAW/'c22-integration-verified.json');assert qualified['admitted']
    source=read(RAW/'c22-numerical-v1-exit.json')['solver_source_files'];pair={}
    for role in ['control','candidate']:
        name=f'c22-large-{role}-1';r=read(RAW/(name+'-exit.json'))
        assert r['returncode']==0 and r['reason'] is None and r['seconds']<=180
        assert r['solver_source_files']==source and r['exe_sha256']==qualified['executable_sha256']
        for p,h in r['inputs'].items():assert sha(p)==h,p
        assert r['environment_overrides']['PREFLOP_GPU_RANK_PIPELINE']==str(int(role=='candidate'))
        x=read(RAW/(name+'-bench.json'));assert x['cohorts'] and x['unrolled'] and x['narrow_offsets'] and not x['profile'] and not x['production_selection']
        assert len(x['rows'])==6 and [v['index'] for v in x['rows']]==list(range(6)) and [v['warmup'] for v in x['rows']]==[True,True,False,False,False,False]
        pair[role]=x
    a,b=pair['control'],pair['candidate']
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k],k
    assert a['arena_entries']==529900514 and a['arena_fingerprint']=='27b4d2870b404cae'
    old=read(RAW/'c14-large-candidate-1-bench.json')
    for x,y,z in zip(a['rows'],b['rows'],old['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k]==z[k],k
    assert a['rank_pipeline'] is None and b['rank_pipeline']==read(RAW/'c22-large-layout-v1.json')['rank_pipeline']
    ratio=b['complete_seconds']/a['complete_seconds'];passed=ratio<.99
    warm={k:statistics.mean(r[k] for r in b['rows'][2:])/statistics.mean(r[k] for r in a['rows'][2:]) for k in ['iteration_seconds','check_seconds']}
    out=dict(verified=True,retained=False,passed_screen=passed,status='Rank pipeline passes first complete-work screen' if passed else 'Rank pipeline rejected: complete workload is slower',control_seconds=a['complete_seconds'],candidate_seconds=b['complete_seconds'],complete_ratio=ratio,warm_ratios=warm,exact_saved_checkpoints_and_arenas=True,arena_entries=a['arena_entries'],arena_fingerprint=a['arena_fingerprint'],solver_tests=9,standalone_exact_cases=5040,extra_device_bytes=b['rank_pipeline']['extra_bytes'],executable_sha256=qualified['executable_sha256'],scope='First complete fixed-work timing; failed gate prevents repeated pairs. No convergence gain or deployment.')
    p=RAW/'c22-timing-screen-verified.json'
    if p.exists():assert read(p)==out
    else:p.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    (RAW/'c22-verified.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
