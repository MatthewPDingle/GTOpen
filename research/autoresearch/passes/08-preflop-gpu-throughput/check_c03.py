"""Audit rejected C03 using its explicit archived source/executable."""
import functools,hashlib,json,math,statistics
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
    mapping=read(HERE/'artifacts/c03-source-map.json');sources=None;exe_hash=None;fixtures={}
    num=read(RAW/'c03-numerical-v1-exit.json')
    assert num['returncode']==0 and num['reason'] is None
    assert '3 passed; 0 failed; 1 ignored' in (RAW/'c03-numerical-v1.log').read_text()
    for fixture,nodes,age,np in [('large',1567754,1050,8),('small',23038,1000,6)]:
        pairs=[]
        for pair in range(1,4):
            runs=[]
            for enabled in [False,True]:
                variant='candidate' if enabled else 'control';name=f'c03-{fixture}-{variant}-{pair}'
                rec=read(RAW/(name+'-exit.json'));b=read(RAW/(name+'-bench.json'))
                assert rec['returncode']==0 and rec['reason'] is None
                if sources is None:sources=rec['solver_source_files'];exe_hash=rec['exe_sha256']
                assert rec['solver_source_files']==sources==num['solver_source_files']
                assert rec['exe_sha256']==exe_hash==digest(LAB/'target/c03-benchmark-frozen.exe')
                for p,h in sources.items():assert digest(HERE/mapping[p] if p in mapping else LAB/p)==h,p
                for p,h in rec['inputs'].items():assert digest(LAB/'target/c03-benchmark-frozen.exe' if p==rec['command'][0] else Path(p))==h,p
                assert rec['environment_overrides']['PREFLOP_GPU_NO_TIE']==str(int(enabled))
                assert b['enabled'] and b['no_tie']==enabled and b['nodes']==nodes and b['initial_iteration']==age and b['iteration']==age+6 and b['batch']==32
                assert len(b['rows'])==6
                for i,r in enumerate(b['rows']):
                    assert r['index']==i and r['iteration']==age+i+1 and r['warmup']==(i<2)
                    for k in ['gaps','evs']:assert len(r[k])==np and all(math.isfinite(v) for v in r[k])
                    for k in ['iteration_seconds','check_seconds']:assert math.isfinite(r[k]) and r[k]>0
                assert math.isfinite(b['complete_seconds']) and b['complete_seconds']>0
                runs.append(b)
            a,b=runs
            for k in ['arena_fingerprint','arena_entries','nodes','iteration','batch','cdf_bytes','extra_bytes','input']:assert a[k]==b[k],(fixture,pair,k)
            for x,y in zip(a['rows'],b['rows']):
                for k in ['gaps','evs','index','iteration','warmup']:assert x[k]==y[k],(fixture,pair,k)
            ratios={'complete':b['complete_seconds']/a['complete_seconds']}
            for k in ['iteration','check']:ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
            pairs.append({'pair':pair,'ratios':ratios,'control_seconds':a['complete_seconds'],'candidate_seconds':b['complete_seconds']})
        fixtures[fixture]={'pairs':pairs,'median_ratios':{k:statistics.median(p['ratios'][k] for p in pairs) for k in ['complete','iteration','check']}}
    ratio=fixtures['large']['median_ratios']['complete']
    assert ratio>.97,'Rejection not proven; passing candidate needs full regression review'
    result={'retained':False,'status':'Rejected - below 3% retention threshold','fixtures':fixtures,
        'reason':f'Large median complete saving {100*(1-ratio):.2f}% is below the predeclared 3%.',
        'source_input_hashes_verified':True,'numerical':'All six paired checkpoint gaps/EVs and arena fingerprints match in every pair; three adversarial tests passed.',
        'scope':'Fixed-work throughput. Rejected prototype removed. No deployment.', 'archived_executable_sha256':exe_hash}
    (RAW/'c03-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
