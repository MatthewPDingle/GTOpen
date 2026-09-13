"""Independent C05 first-pair rejection audit against frozen source and executable."""
import functools,hashlib,json,math,statistics,subprocess,collections
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
    mapping={str(Path(k)):v for k,v in read(HERE/'artifacts/c05-source-map.json').items()}
    num=read(RAW/'c05-numerical-v1-exit.json');prefix=read(RAW/'c05-prefix-v1-exit.json')
    for r in [num,prefix]:assert r['returncode']==0 and r['reason'] is None
    assert '4 passed; 0 failed; 1 ignored' in (RAW/'c05-numerical-v1.log').read_text()
    assert '2 passed; 0 failed; 0 ignored' in (RAW/'c05-prefix-v1.log').read_text()
    sources=num['solver_source_files'];assert prefix['solver_source_files']==sources
    for p,h in sources.items():
        if p in mapping:assert digest(HERE/mapping[p])==h,p
        else:
            blob=subprocess.check_output(['git','show',num['source_commit']+':'+Path(p).as_posix()],cwd=LAB)
            assert hashlib.sha256(blob).hexdigest()==h,p
    exe=LAB/'target/c05-benchmark-frozen.exe';exe_hash=digest(exe);runs=[]
    for enabled in [False,True]:
        name='c05-large-'+('candidate' if enabled else 'control')+'-1'
        rec=read(RAW/(name+'-exit.json'));b=read(RAW/(name+'-bench.json'))
        assert rec['returncode']==0 and rec['reason'] is None
        assert rec['solver_source_files']==sources and rec['exe_sha256']==exe_hash
        for p,h in rec['inputs'].items():assert digest(exe if p==rec['command'][0] else Path(p))==h,p
        assert rec['environment_overrides']['PREFLOP_GPU_ALIGNED']==str(int(enabled))
        assert b['enabled'] and b['aligned']==enabled and b['nodes']==1567754 and b['initial_iteration']==1050 and b['iteration']==1056 and b['batch']==32
        assert len(b['rows'])==6
        for i,r in enumerate(b['rows']):
            assert r['index']==i and r['iteration']==1051+i and r['warmup']==(i<2)
            for k in ['gaps','evs']:assert len(r[k])==8 and all(math.isfinite(v) for v in r[k])
            for k in ['iteration_seconds','check_seconds']:assert math.isfinite(r[k]) and r[k]>0
        assert math.isfinite(b['complete_seconds']) and b['complete_seconds']>0
        runs.append(b)
    a,b=runs
    for k in ['arena_fingerprint','arena_entries','nodes','iteration','batch','original_cdf_bytes','input']:assert a[k]==b[k],k
    assert a['extra_bytes']==b['extra_bytes']
    assert b['cdf_bytes']-a['cdf_bytes']==1_092_839_040
    assert b['transient_cdf_bytes']==9_537_503_360 and a['transient_cdf_bytes']==0
    for x,y in zip(a['rows'],b['rows']):
        for k in ['gaps','evs','index','iteration','warmup']:assert x[k]==y[k],k
    ratios={'complete':b['complete_seconds']/a['complete_seconds']}
    for k in ['iteration','check']:ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
    assert ratios['complete']>.99,'First-pair rejection not proven'
    diagnostic=[]
    for enabled in [False,True]:
        name='c05-large-'+('candidate' if enabled else 'control')+'-profile-v1'
        rec=read(RAW/(name+'-exit.json'));d=read(RAW/(name+'.json'))
        assert rec['returncode']==0 and rec['reason'] is None and rec['solver_source_files']==sources and rec['exe_sha256']==exe_hash
        for p,h in rec['inputs'].items():assert digest(exe if p==rec['command'][0] else Path(p))==h,p
        assert d['aligned']==enabled and d['profile'] and d['enabled'] and d['arena_fingerprint']==a['arena_fingerprint']
        assert rec['environment_overrides']['PREFLOP_GPU_REUSE_PROFILE']=='1' and rec['environment_overrides']['PREFLOP_GPU_ALIGNED']==str(int(enabled))
        assert len(d['rows'])==6
        for x,y in zip(d['rows'],a['rows']):
            for k in ['gaps','evs','index','iteration','warmup']:assert x[k]==y[k],k
        ops={}
        for key in ['iteration_phases','check_phases']:
            times=collections.defaultdict(list)
            for row in d['rows']:
                v=row[key];assert v['execution']=='eager_cuda_events' and math.isfinite(v['gpu_ms']) and v['gpu_ms']>0
                total=sum(r['ms'] for r in v['rows']);assert abs(total-v['gpu_ms'])<1+total*.001
                counts=collections.Counter();sums=collections.defaultdict(float)
                for r in v['rows']:
                    assert math.isfinite(r['ms']) and r['ms']>=0 and r['intervals']>0
                    counts[r['phase']]+=r['intervals'];sums[r['phase']]+=r['ms']
                for phase in ['cdf','coupled_terminals']:assert counts[phase]==8*32
                for phase in ['normalize','classify','prepare']:assert counts[phase]==8
                if not row['warmup']:
                    for k,val in sums.items():times[k].append(val)
            ops[key]={k:statistics.median(v) for k,v in times.items()}
        diagnostic.append(ops)
    result={'retained':False,'status':'Rejected - first-pair timing screen','ratios':ratios,
        'diagnostic_phase_ms':{'control':diagnostic[0],'candidate':diagnostic[1]},
        'control_seconds':a['complete_seconds'],'candidate_seconds':b['complete_seconds'],
        'reason':f"Complete run was {100*(ratios['complete']-1):.2f}% slower; no extended trials.",
        'source_input_hashes_verified':True,'numerical':'All logical-prefix bits, four full solver tests, all six large paired checkpoint gaps/EVs and final arena fingerprint match.',
        'scope':'One fixed-work large pair. Rejected prototype removed. No deployment.', 'archived_executable_sha256':exe_hash}
    (RAW/'c05-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
