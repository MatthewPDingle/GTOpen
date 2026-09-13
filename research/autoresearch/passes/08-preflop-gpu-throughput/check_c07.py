"""Independent bounded-cohort plan, numerical and first-pair audit."""
import functools,hashlib,json,math,statistics,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3];RAW=HERE/'raw'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
@functools.cache
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()

def expected_plan(fixture):
    d=read(RAW/f'd05-{fixture}-v1.json');n=d['players'];c=d['cohorts'];b=d['buffer_bytes']
    # Independent insertion enumeration; the Rust planner chooses the first block.
    partitions=[()]
    for p in range(n):
        nxt=[]
        for old in partitions:
            nxt.append(old+(1<<p,))
            for i,g in enumerate(old):
                if g.bit_count()<3:nxt.append(old[:i]+(g|(1<<p),)+old[i+1:])
        partitions=nxt
    assert len(set(partitions))==len(partitions)
    if n==8:assert len(partitions)==2780
    su,uu=c['static_subset_unions'],c['unique_subset_unions']
    for key,u in [('static_membership_histogram',su),('unique_membership_histogram',uu)]:
        h=c[key];assert u==[sum(v for m,v in enumerate(h) if m&s) for s in range(1<<n)]
    capacity=b['d_mw_normalized']//(169*4);plans=[]
    for masks in partitions:
        cap=max(capacity,max(su[m] for m in masks));largest=max(m.bit_count() for m in masks)
        table=1<<(cap*2-1).bit_length()
        extra=(cap+table)*4+len(masks)*su[-1]*4+sum(su[m]*4 for m in masks)+(largest-1)*(b['d_val']+b['d_mw_prob'])
        total=d['base_bytes']-b['d_mw_cdf']-b['d_mw_normalized']+cap*(32*170+169)*4+extra
        if total+256*1024*1024>20_500_000_000:continue
        plans.append(dict(group_masks=list(masks),groups=[[p for p in range(n) if m&(1<<p)] for m in masks],
            capacity=cap,extra_bytes=extra,base_bytes=d['base_bytes'],total_bytes=total,peak_bytes=total+256*1024*1024,
            original_cdf_bytes=b['d_mw_cdf'],static_rows=sum(su[m] for m in masks),cdf_rows=sum(uu[m] for m in masks)))
    best=min(plans,key=lambda p:(p['static_rows'],p['total_bytes'],json.dumps(p['group_masks'],separators=(',',':'))))
    if fixture=='large':
        pre=read(RAW/'c07-static-preflight.json');assert digest(RAW/'d05-large-v1.json')==pre['sha256']
        for k in ['group_masks','groups','static_rows','cdf_rows','peak_bytes']:assert best[k]==pre[k],k
        assert len(plans)==pre['fitting_partitions'] and 1-best['cdf_rows']/d['baseline_cdf_rows']>=.25
    return best,d

def source_evidence():
    pre=read(RAW/'c07-numerical-v1-exit.json');assert pre['returncode']==0 and pre['reason'] is None
    assert '4 passed; 0 failed; 1 ignored' in (RAW/'c07-numerical-v1.log').read_text()
    archive=HERE/'artifacts/c07-source-map.json'
    mapping={str(Path(k)):v for k,v in read(archive).items()} if archive.exists() else {}
    for p,h in pre['solver_source_files'].items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        elif archive.exists():
            blob=subprocess.check_output(['git','show',pre['source_commit']+':'+Path(p).as_posix()],cwd=LAB)
            assert hashlib.sha256(blob).hexdigest()==h,p
        else:assert digest(LAB/p)==h,p
    for p,h in pre['inputs'].items():assert digest(Path(p))==h,p
    return pre

def evidence(name,pre):
    rec=read(RAW/(name+'-exit.json'));frozen=LAB/'target/c07-benchmark-frozen.exe'
    assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=180
    assert rec['solver_source_files']==pre['solver_source_files'] and rec['exe_sha256']==digest(frozen)
    for p,h in rec['inputs'].items():assert digest(frozen if p==rec['command'][0] else Path(p))==h,p
    for side in ['before','after']:
        x=read(RAW/(name+'-gpu-'+side+'.json'));assert x['returncode']==0 and 'NVIDIA' in x['stdout']
    return rec

def check_layouts():
    pre=source_evidence();layouts={}
    for fixture in ['small','large']:
        name=f'c07-{fixture}-layout-v1';evidence(name,pre);x=read(RAW/(name+'.json'));expected,d=expected_plan(fixture)
        for k,v in x['plan'].items():assert v==expected[k],(fixture,k,v,expected[k])
        assert x['actual_device_bytes']==sum(x['buffer_bytes'].values())+x['plan']['extra_bytes']==expected['total_bytes']
        assert x['batch']==32 and x['arenas_unchanged'] and x['buffer_bytes']['d_eq_cache']==d['buffer_bytes']['d_eq_cache']
        for k,v in d['buffer_bytes'].items():
            if k not in ['d_mw_cdf','d_mw_normalized']:assert x['buffer_bytes'][k]==v,(fixture,k)
        layouts[fixture]=x
    return pre,layouts

def main():
    pre,layouts=check_layouts();runs=[]
    for role in ['control','candidate']:
        name=f'c07-large-{role}-1';rec=evidence(name,pre);x=read(RAW/(name+'-bench.json'))
        assert rec['environment_overrides']['PREFLOP_GPU_COHORT_ENABLE']==str(int(role=='candidate'))
        assert x['cohorts']==(role=='candidate') and x['enabled'] and not x['profile'] and x['batch']==32
        assert x['nodes']==1567754 and x['initial_iteration']==1050 and x['iteration']==1056 and len(x['rows'])==6
        for i,r in enumerate(x['rows']):
            assert r['index']==i and r['iteration']==1051+i and r['warmup']==(i<2)
            for k in ['gaps','evs']:assert len(r[k])==8 and all(math.isfinite(v) for v in r[k])
            for k in ['iteration_seconds','check_seconds']:assert r[k]>0 and math.isfinite(r[k])
        runs.append(x)
    a,b=runs
    for k in ['input','nodes','initial_iteration','iteration','batch','arena_entries','arena_fingerprint','original_cdf_bytes']:assert a[k]==b[k],k
    for x,y in zip(a['rows'],b['rows']):
        for k in ['gaps','evs','index','warmup','iteration']:assert x[k]==y[k],k
    assert b['cohort_plan']==layouts['large']['plan']
    assert b['cdf_bytes']==layouts['large']['buffer_bytes']['d_mw_cdf']
    extra=b['cohort_plan']['extra_bytes']+layouts['large']['buffer_bytes']['d_mw_normalized']-b['original_cdf_bytes']//(32*170)*169
    assert b['extra_bytes']==extra
    ratios=dict(complete=b['complete_seconds']/a['complete_seconds'])
    for k in ['iteration','check']:ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
    result=dict(retained=False,ratios=ratios,control_seconds=a['complete_seconds'],candidate_seconds=b['complete_seconds'],
        source_input_hashes_verified=True,exact_checkpoints_and_arena=True,allocation_matches_static_preflight=True,
        allocated_device_bytes=b['cohort_plan']['total_bytes'],archived_executable_sha256=digest(LAB/'target/c07-benchmark-frozen.exe'))
    if ratios['complete']>=.99:
        result.update(status='Rejected - first-pair timing screen',reason=f"Complete-time ratio {ratios['complete']:.4f} failed the <0.99 screen; no extended trials.",
            scope='One fixed-work large pair. Numerically exact, but insufficient speed. Memory snapshots do not establish the cause. No deployment.')
        (RAW/'c07-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    else:result.update(status='Screen passed - extended qualification required')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
