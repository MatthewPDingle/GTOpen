"""Verify first completed C23 timing pair against frozen numerical evidence."""
import hashlib,json,statistics
from pathlib import Path
from run_c23 import compare
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    qualified=read(RAW/'c23-integration-verified.json');assert qualified['admitted']
    source=read(RAW/'c23-numerical-v1-exit.json')['solver_source_files'];rows={};runs={}
    for role in ['control','candidate']:
        name=f'c23-large-{role}-2';r=read(RAW/(name+'-exit.json'))
        assert r['returncode']==0 and r['reason'] is None and r['seconds']<=180
        assert r['exe_sha256']==qualified['executable_sha256'] and r['solver_source_files']==source
        for path,h in r['inputs'].items():assert sha(path)==h,path
        assert r['environment_overrides']['PREFLOP_GPU_STATIC_CDF']==str(int(role=='candidate'))
        rows[role]=read(RAW/(name+'-bench.json'));runs[role]=r['seconds']
    a,b=rows['control'],rows['candidate'];ratio=compare(a,b)
    reference=read(RAW/'c14-large-control-1-bench.json')
    for x in [a,b]:
        assert x['arena_entries']==reference['arena_entries'] and x['arena_fingerprint']==reference['arena_fingerprint']
        for actual,expected in zip(x['rows'],reference['rows']):
            for k in ['iteration','gaps','evs','warmup']:assert actual[k]==expected[k],k
    screen=read(RAW/'c23-timing-screen.json');assert screen['first_completed_pair']==2 and screen['first_pair_ratio']==ratio and screen['passed_screen']==(ratio<=.99)
    assert screen['retry_script_sha256']==sha(HERE/'run_c23_timing.py')
    warm={role:{k:statistics.median(row[k] for row in x['rows'] if not row['warmup']) for k in ['iteration_seconds','check_seconds']} for role,x in rows.items()}
    out=dict(verified=True,retained=False,admitted=ratio<=.99,status='Static CDF passes first timing screen; repeated pairs required' if ratio<=.99 else 'Static CDF fails first complete-work timing screen',
        first_completed_pair=2,complete_control_seconds=a['complete_seconds'],complete_candidate_seconds=b['complete_seconds'],ratio=ratio,
        warm_seconds=warm,guard_seconds=runs,exact_checkpoints_and_arena=True,arena_entries=a['arena_entries'],arena_fingerprint=a['arena_fingerprint'],
        executable_sha256=qualified['executable_sha256'],scope='One complete large pair; not yet a retained gain or convergence qualification.')
    dest=RAW/'c23-first-pair-verified.json'
    if dest.exists():assert read(dest)==out
    else:dest.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
