"""Independent, fail-closed C01 evidence audit. No GPU or live-app mutation."""
import functools, hashlib, json, math, re, statistics
from pathlib import Path
HERE=Path(__file__).resolve().parent
LAB=HERE.parents[3]
RAW=HERE/'raw'
TEST=Path('crates/solver/src/preflop/gpu/exact_reuse/tests.rs')
EXE_HASH='14b1b19e3ffa221154226b3b61c1a43870424947b1f996853c7dbc5bd223d8fa'
TEST_HASH='a941f22d424d6cdbfabe2503009707c5a87eae1246194c0cd918bdb0129dfd69'
@functools.cache
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def successful(name):
    x=read(RAW/(name+'-exit.json'))
    assert x['returncode']==0 and x['reason'] is None,name
    assert x['seconds']>0,name
    return x

def main():
    original=read(RAW/'c01-large-control-1-exit.json')
    assert digest(LAB/'target/c01-benchmark-frozen.exe')==EXE_HASH
    assert digest(HERE/'artifacts/c01-benchmark-tests.rs')==TEST_HASH
    original_sources=original['solver_source_files']
    for name,h in original_sources.items():
        p=Path(name)
        actual=HERE/'artifacts/c01-benchmark-tests.rs' if p==TEST else LAB/p
        assert digest(actual)==h,('benchmark source',name)
    # The only source change after timing was appending an all-opponent-count test.
    archived=(HERE/'artifacts/c01-benchmark-tests.rs').read_text()
    current=(LAB/TEST).read_text()
    assert current.startswith(archived.rstrip())
    assert 'fn exact_reuse_all_opponent_counts_match_terminal_bits()' in current[len(archived.rstrip()):]
    prerequisites={}
    for name,expected in [('c01-numerical-v1',2),('c01-numerical-v2',3),('c01-native-regression-v1',19),('c01-default-regression-v1',None)]:
        x=successful(name)
        expected_sources=original_sources if name.endswith('numerical-v1') else {k:digest(LAB/Path(k)) for k in original_sources}
        assert x['solver_source_files']==expected_sources,('regression source',name)
        log=(RAW/(name+'.log')).read_text()
        counts=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed',log)
        assert counts and all(int(f)==0 for _,f in counts),name
        passed=sum(int(n) for n,_ in counts)
        if expected is not None:assert passed==expected,(name,passed)
        else:assert passed>=100,(name,passed)
        prerequisites[name]={'passed':passed,'seconds':x['seconds']}
    summary={}
    for fixture,nodes,age in [('large',1567754,1050),('small',23038,1000)]:
        pairs=[]
        for pair in range(1,4):
            runs=[]
            for enabled in [False,True]:
                variant='candidate' if enabled else 'control'
                name=f'c01-{fixture}-{variant}-{pair}'
                x=successful(name); b=read(RAW/(name+'-bench.json'))
                assert x['exe_sha256']==EXE_HASH and x['solver_source_files']==original_sources,name
                assert x['command'][1:]==['preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark','--exact','--ignored','--nocapture','--test-threads=1']
                for p,h in x['inputs'].items():
                    actual=LAB/'target/c01-benchmark-frozen.exe' if p==x['command'][0] else Path(p)
                    assert digest(actual)==h,(name,p)
                assert x['environment_overrides']['PREFLOP_GPU_REUSE_ENABLE']==str(int(enabled))
                assert b['enabled']==enabled and b['nodes']==nodes and b['initial_iteration']==age
                assert b['iteration']==age+6 and b['batch']==32 and len(b['rows'])==6
                assert 0<b['extra_bytes']<=16*1024**2 if enabled else b['extra_bytes']==0
                for i,row in enumerate(b['rows']):
                    assert row['index']==i and row['iteration']==age+i+1 and row['warmup']==(i<2)
                    for k in ['iteration_seconds','check_seconds']:assert math.isfinite(row[k]) and row[k]>0
                    for k in ['gaps','evs']:assert len(row[k])==(8 if fixture=='large' else 6) and all(math.isfinite(v) for v in row[k])
                for k in ['init_seconds','sync_seconds','complete_seconds']:assert math.isfinite(b[k]) and b[k]>0
                assert b['complete_seconds']>=b['init_seconds']+b['sync_seconds']+sum(r['iteration_seconds']+r['check_seconds'] for r in b['rows'])
                runs.append(b)
            a,b=runs
            for k in ['input','nodes','initial_iteration','iteration','batch','cdf_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k],(fixture,pair,k)
            for ar,br in zip(a['rows'],b['rows']):
                for k in ['index','iteration','warmup','gaps','evs']:assert ar[k]==br[k],(fixture,pair,k)
            ratios={'complete':b['complete_seconds']/a['complete_seconds']}
            for k in ['iteration','check']:
                ratios[k]=statistics.median(r[k+'_seconds'] for r in b['rows'][2:])/statistics.median(r[k+'_seconds'] for r in a['rows'][2:])
            pairs.append({'pair':pair,'ratios':ratios,'control_seconds':a['complete_seconds'],'candidate_seconds':b['complete_seconds']})
        summary[fixture]={'pairs':pairs,'median_ratios':{k:statistics.median(p['ratios'][k] for p in pairs) for k in ['complete','iteration','check']}}
    large=summary['large']['median_ratios']['complete'];small=summary['small']['median_ratios']['complete']
    retained=large<=.97 and small<=1.03 and all(p['ratios']['complete']<1 for p in summary['large']['pairs'])
    result={'retained':retained,'status':'Retained - exact CDF reuse' if retained else 'Rejected - timing gate',
        'display_gain':f'{100*(1-large):.1f}% less time','fixtures':summary,'prerequisites':prerequisites,
        'numerical':'Every paired checkpoint gap and EV agrees exactly; final full-arena fingerprints agree. Adversarial small tests compare every arena bit.',
        'scope':'Fixed-work GPU throughput only; not full convergence qualification. No live deployment.',
        'provenance':{'benchmark_exe_sha256':EXE_HASH,'benchmark_test_source_sha256':TEST_HASH,
        'source_note':'Benchmark executable archived locally before extra validation test was appended; all algorithm sources unchanged.'}}
    (RAW/'c01-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
