"""Audit immutable profiling inputs, numerical equivalence and phase coverage."""
import functools,hashlib,json,math,statistics,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3];RAW=HERE/'raw'
@functools.cache
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    num=read(RAW/'d03-numerical-v2-exit.json');original=read(RAW/'d03-original-tracer-v1-exit.json')
    for r in [num,original]:assert r['returncode']==0 and r['reason'] is None
    assert '4 passed; 0 failed; 1 ignored' in (RAW/'d03-numerical-v2.log').read_text()
    assert '1 passed; 0 failed' in (RAW/'d03-original-tracer-v1.log').read_text()
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/d03-source-map.json').items()}
    sources=num['solver_source_files'];assert original['solver_source_files']==sources
    for p,h in sources.items():assert digest(HERE/mapping[p] if p in mapping else LAB/p)==h,p
    exe=LAB/'target/d03-profile-frozen.exe';exe_hash=digest(exe);fixtures={}
    for fixture,nodes,age,np in [('small',23038,1000,6),('large',1567754,1050,8)]:
        runs=[]
        for profile in [False,True]:
            name=f"d03-{fixture}-{'profiled' if profile else 'control'}-v1"
            rec=read(RAW/(name+'-exit.json'));b=read(RAW/(name+'.json'))
            assert rec['returncode']==0 and rec['reason'] is None and rec['solver_source_files']==sources
            assert rec['exe_sha256']==exe_hash
            for p,h in rec['inputs'].items():assert digest(exe if p==rec['command'][0] else Path(p))==h,p
            assert rec['environment_overrides']['PREFLOP_GPU_REUSE_PROFILE']==str(int(profile))
            assert b['enabled'] and b['profile']==profile and b['nodes']==nodes and b['initial_iteration']==age and b['iteration']==age+6 and b['batch']==32
            assert len(b['rows'])==6
            for i,r in enumerate(b['rows']):
                assert r['index']==i and r['iteration']==age+i+1 and r['warmup']==(i<2)
                for k in ['gaps','evs']:assert len(r[k])==np and all(math.isfinite(v) for v in r[k])
                for k in ['iteration_phases','check_phases']:
                    v=r[k]
                    if not profile:assert v is None;continue
                    assert v['execution']=='eager_cuda_events'
                    rows=v['rows'];total=v['gpu_ms'];assert math.isfinite(total) and total>0
                    assert all(math.isfinite(x['ms']) and x['ms']>=0 and x['intervals']>0 for x in rows)
                    assert abs(sum(x['ms'] for x in rows)-v['interval_sum_ms'])<1e-6
                    assert abs(total-v['interval_sum_ms'])<1+total*.001
                    counts=collections.Counter()
                    for x in rows:counts[x['phase']]+=x['intervals']
                    for phase in ['prepare','normalize','classify','ordinary_terminals']:assert counts[phase]==np,(fixture,k,phase)
                    for phase in ['cdf','coupled_terminals']:assert counts[phase]==np*32,(fixture,k,phase)
                    assert counts['down']==(np if k=='iteration_phases' else 1)
                    for phase in ['up_average','up_br']:assert counts[phase]==(np if k=='check_phases' else 0)
                    assert counts['up_learn']==(np if k=='iteration_phases' else 0)
            runs.append(b)
        a,b=runs
        for k in ['input','nodes','iteration','initial_iteration','batch','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k],(fixture,k)
        for x,y in zip(a['rows'],b['rows']):
            for k in ['index','iteration','warmup','gaps','evs']:assert x[k]==y[k],(fixture,k)
        ops={}
        for key in ['iteration_phases','check_phases']:
            phase_times=collections.defaultdict(list);shares=collections.defaultdict(list)
            for row in b['rows'][2:]:
                totals=collections.defaultdict(float)
                for x in row[key]['rows']:totals[x['phase']]+=x['ms']
                for k,v in totals.items():phase_times[k].append(v);shares[k].append(v/row[key]['gpu_ms'])
            ops[key]={'median_total_ms':statistics.median(row[key]['gpu_ms'] for row in b['rows'][2:]),
                'phases':{k:{'median_ms':statistics.median(v),'median_share':statistics.median(shares[k])} for k,v in phase_times.items()}}
        fixtures[fixture]={'control_complete_seconds':a['complete_seconds'],'profiled_complete_seconds':b['complete_seconds'],'operations':ops}
    result={'status':'Diagnosis complete - CDF and terminal work dominate','kind':'diagnostic','fixtures':fixtures,
        'verified':True,'source_input_hashes_verified':True,'exact_checkpoints_and_arenas':True,
        'scope':'Eager timing only; no speedup or convergence claim. Port 56708 unchanged.','executable_sha256':exe_hash}
    (RAW/'d03-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
