"""C18 source/resource/state/first-pair audit; no retention from one pair."""
import hashlib,json,math,statistics,subprocess
from pathlib import Path
from check_d09 import entries
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw';LAB=HERE.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def source_audit(record,version):
    mapping={str(Path(k)):v for k,v in read(HERE/f'artifacts/c18-{version}-source-map.json').items()}
    for p,h in record['solver_source_files'].items():
        if p in mapping:assert sha(HERE/mapping[p]['archive'])==mapping[p]['sha256']==h,p
        else:assert hashlib.sha256(subprocess.check_output(['git','show',record['source_commit']+':'+Path(p).as_posix()],cwd=LAB)).hexdigest()==h,p

def main():
    for name,version,count in [('c18-kernel-v1','v1',1),('c18-numerical-v1','v2',7),('c18-numerical-v2','v3',8),('c18-kernel-v2','v4',1)]:
        rec=read(RAW/(name+'-exit.json'));assert rec['returncode']==0 and rec['reason'] is None and rec['seconds']<=300
        assert f'{count} passed; 0 failed;' in (RAW/(name+'.log')).read_text(encoding='utf-8')
        source_audit(rec,version)
        for p,h in rec['inputs'].items():assert sha(p)==h,p
    source=read(RAW/'c18-kernel-v2-exit.json')['solver_source_files'];exe=LAB/'target/c18-benchmark-frozen.exe';exe_hash=sha(exe)
    def record(name):
        r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None and r['seconds']<=180
        assert r['solver_source_files']==source and r['exe_sha256']==exe_hash
        for p,h in r['inputs'].items():assert sha(p)==h,p
        return r
    nr=record('c18-numerical-v3');assert nr['environment_overrides']['PREFLOP_GPU_RANK_COMPACT']=='1'
    assert '8 passed; 0 failed; 1 ignored' in (RAW/'c18-numerical-v3.log').read_text(encoding='utf-8')
    for version in ['v1','v2']:
        folder=RAW/f'c18-kernel-{version}-compiler';k=read(folder/'resources.json')
        assert k['exact'] and k['cases']==5040 and k['mapping_bytes']==2080768 and k['guard_values']==23
        assert len(k['resources'])==14
        for i,r in enumerate(k['resources']):
            assert r['opponents']==i%7+2 and r['compact']==(i>=7) and r['local_bytes']==0
            assert r['shared_bytes']==(169*((r['opponents']+2)//2)*4 if r['compact'] else 0)
        a,b=[entries((folder/(role+'.ptx')).read_text(encoding='utf-8')) for role in ['control','candidate']]
        assert a.keys()==b.keys() and {k for k in a if a[k]!=b[k]}=={f'audit_{o}' for o in range(2,9)}
    resources={}
    for version,shared in [('v1',15592),('v2',3424)]:
        folder=RAW/f'c18-integrated-{version}-compiler';resources[version]={}
        for kind,name in [('exact','pf_exact_reuse_terminal'),('cohort','pf_cohort_terminal')]:
            a,b=[(folder/(name+'-'+role+'.ptx')).read_text(encoding='utf-8') for role in ['control','candidate']]
            assert a==(RAW/('r03-compiler-v2/'+kind+'-candidate.ptx')).read_text(encoding='utf-8')
            aa,bb=entries(a),entries(b);assert aa.keys()==bb.keys() and [k for k in aa if aa[k]!=bb[k]]==[name]
            r=read(folder/(name+'-resources.json'));assert r['shared_bytes']==shared and r['local_bytes']==0
            resources[version][kind]=r
    for fixture in ['small','large']:
        name=f'c18-{fixture}-layout-v1';r=record(name);x=read(RAW/(name+'.json'));old=read(RAW/f'c14-{fixture}-layout-v1.json')
        assert r['environment_overrides']['PREFLOP_GPU_RANK_COMPACT']=='1' and x['rank_compact'] and x['rank_mapping_bytes']==2080768
        for k in ['plan','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
        expected=dict(old['buffer_bytes'],rank_lower=692224,rank_upper=692224,rank_hand=692224,rank_count=4096)
        assert x['buffer_bytes']==expected and x['actual_device_bytes']==old['actual_device_bytes']+2080768
        assert x['actual_device_bytes']+256*1024*1024<=20_500_000_000
    results=[];old=read(RAW/'c14-large-candidate-1-bench.json')
    for role in ['control','candidate']:
        name=f'c18-large-{role}-1';r=record(name);b=read(RAW/(name+'-bench.json'));on=role=='candidate'
        assert r['environment_overrides']['PREFLOP_GPU_RANK_COMPACT']==str(int(on)) and b['rank_compact']==on
        assert b['rank_mapping_bytes']==2080768*on and b['extra_bytes']==old['extra_bytes']+2080768*on
        assert b['enabled'] and b['cohorts'] and b['unrolled'] and b['narrow_offsets'] and not b['profile'] and not b['production_selection']
        for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','arena_entries','arena_fingerprint']:assert b[k]==old[k],k
        assert len(b['rows'])==6
        for row,ref in zip(b['rows'],old['rows']):
            for k in ['index','iteration','warmup','gaps','evs']:assert row[k]==ref[k],k
            for k in ['iteration_seconds','check_seconds']:assert math.isfinite(row[k]) and row[k]>0
        assert b['complete_seconds']>=b['init_seconds']+b['sync_seconds']+sum(x['iteration_seconds']+x['check_seconds'] for x in b['rows'])
        for side in ['before','after']:assert read(RAW/(name+'-gpu-'+side+'.json'))['returncode']==0
        results.append(b)
    a,b=results;ratio=b['complete_seconds']/a['complete_seconds'];passed=ratio<.99
    phase_ratios={k:statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:]) for k in ['iteration','check']}
    result=dict(verified=True,retained=False,passed_first_screen=passed,status='First screen passed - repeat pairs and regressions remain' if passed else 'Rejected by complete-runtime screen',
        complete_ratio=ratio,control_seconds=a['complete_seconds'],candidate_seconds=b['complete_seconds'],warm_ratios=phase_ratios,
        kernel_exact_cases=5040,solver_tests=8,source_input_executable_hashes_verified=True,exact_saved_checkpoints_and_arenas=True,
        mapping_bytes=2080768,integrated_resources=resources,executable_sha256=exe_hash,
        scope='First fixed-work pair only; no retained gain, convergence qualification or deployment.')
    target=RAW/'c18-verified.json';target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
