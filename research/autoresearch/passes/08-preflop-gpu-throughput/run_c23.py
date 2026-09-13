"""Guard full-solver static-CDF qualification and later fixed-work pairs."""
import hashlib,json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
from run_c07 import snapshot
run07.RAW=RAW
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def run(fixture,role,pair=1,layout=False):
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json';exe=run07.LAB/'target/c23-benchmark-frozen.exe'
    name=f'c23-{fixture}-layout-v1' if layout else f'c23-{fixture}-{role}-{pair}'
    out=RAW/(name+('.json' if layout else '-bench.json'))
    test='preflop::gpu::cohort_reuse::tests::cohort_constructor_from_saved_state' if layout else 'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark'
    snapshot(name,'before')
    run07.run(name,[exe,test,'--exact','--ignored','--nocapture','--test-threads=1'],180,
        [source,eq,fit,exe,HERE/'C23_PROTOCOL.md',HERE/'C23_INTEGRATION.md',Path(__file__),HERE/'artifacts/c23-v2-source-map.json'],
        {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1',
         'PREFLOP_GPU_COHORT_ENABLE':'1','PREFLOP_GPU_TERMINAL_UNROLL':'1','PREFLOP_GPU_NARROW_OFFSETS':'1',
         'PREFLOP_GPU_STATIC_CDF':str(int(role=='candidate')),'REALIZATION_FIT':str(fit)})
    snapshot(name,'after');rec=read(RAW/(name+'-exit.json'));assert rec['returncode']==0 and rec['reason'] is None
    return read(out)
def compare(a,b):
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k],k
    assert len(a['rows'])==len(b['rows'])==6
    for x,y in zip(a['rows'],b['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k],k
    assert a['static_cdf'] is None and b['static_cdf']['row_stride']==2160
    assert b['cdf_bytes']*5440==a['cdf_bytes']*2160
    return b['complete_seconds']/a['complete_seconds']
def main():
    stage=sys.argv[1];frozen=run07.LAB/'target/c23-benchmark-frozen.exe'
    if stage=='qualify':
        assert read(RAW/'c23-screen-verified.json')['admitted']
        run07.run('c23-numerical-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib',
            'cohort_reuse::tests::','--','--nocapture','--test-threads=1'],300,
            [HERE/'C23_PROTOCOL.md',HERE/'C23_INTEGRATION.md',HERE/'prepare_c23_integration.py',HERE/'c23_integration.rs.txt',HERE/'c23_recovery_tests.rs.txt',Path(__file__),HERE/'artifacts/c23-v2-source-map.json'],
            {'PREFLOP_GPU_STATIC_CDF_INTEGRATED_OUTPUT':str(RAW/'c23-integrated-v1')})
        rec=read(RAW/'c23-numerical-v1-exit.json');assert rec['returncode']==0 and rec['reason'] is None
        log=(RAW/'c23-numerical-v1.log').read_text(encoding='utf-8');assert '10 passed; 0 failed; 1 ignored' in log
        exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        assert not frozen.exists();shutil.copyfile(exe,frozen)
        (RAW/'c23-benchmark-frozen.json').write_text(json.dumps(dict(source_run='c23-numerical-v1',sha256=hashlib.sha256(frozen.read_bytes()).hexdigest()),indent=2)+'\n',encoding='utf-8')
    elif stage=='layouts':
        assert read(RAW/'c23-numerical-v1-exit.json')['returncode']==0
        for fixture in ['small','large']:
            x=run(fixture,'candidate',layout=True);old=read(RAW/f'c14-{fixture}-layout-v1.json');plan=read(RAW/'d19-verified.json')['fixtures'][fixture]
            for k in ['plan','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
            assert x['static_cdf']==dict(row_stride=2160,static_bytes=1392644,original_cdf_bytes=plan['cdf_bytes_before'])
            assert x['actual_device_bytes']==plan['final_device_bytes']
            expected=dict(old['buffer_bytes'],d_mw_cdf=plan['cdf_bytes_after'],static_prefix=696320,static_hand=692224,static_offsets=4100)
            assert x['buffer_bytes']==expected
    elif stage=='screen':
        assert read(RAW/'c23-integration-verified.json')['admitted']
        a=run('large','control');b=run('large','candidate');ratio=compare(a,b)
        print(json.dumps(dict(first_pair_ratio=ratio,passed_screen=ratio<=.99,numerical_equal=True)),flush=True)
    else:raise ValueError(stage)
if __name__=='__main__':main()
