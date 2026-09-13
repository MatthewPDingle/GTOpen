"""Serial C19 full solver qualification and fixed-work timing gates."""
import json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;RAW=HERE/'raw'
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
from run_c07 import snapshot
run07.RAW=RAW
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def run(fixture,role,pair=1,layout=False):
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json';exe=run07.LAB/'target/c19-benchmark-frozen.exe'
    name=f'c19-{fixture}-layout-v1' if layout else f'c19-{fixture}-{role}-{pair}'
    out=RAW/(name+('.json' if layout else '-bench.json'))
    test='preflop::gpu::cohort_reuse::tests::cohort_constructor_from_saved_state' if layout else 'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark'
    snapshot(name,'before')
    run07.run(name,[exe,test,'--exact','--ignored','--nocapture','--test-threads=1'],180,
        [source,eq,fit,exe,HERE/'C19_PROTOCOL.md',Path(__file__),HERE/'artifacts/c19-v2-source-map.json'],
        {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1',
         'PREFLOP_GPU_COHORT_ENABLE':'1','PREFLOP_GPU_TERMINAL_UNROLL':'1','PREFLOP_GPU_NARROW_OFFSETS':'1',
         'PREFLOP_GPU_CDF_INTERLEAVE':str(int(role=='candidate')),'REALIZATION_FIT':str(fit)})
    snapshot(name,'after');return read(out)
def compare(a,b):
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:
        assert a[k]==b[k],k
    assert len(a['rows'])==len(b['rows'])==6
    for x,y in zip(a['rows'],b['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k],k
    assert not a['interleaved_cdf'] and b['interleaved_cdf']
    return b['complete_seconds']/a['complete_seconds']
def main():
    stage=sys.argv[1];frozen=run07.LAB/'target/c19-benchmark-frozen.exe'
    if stage=='qualify':
        assert read(RAW/'c19-screen-verified.json')['admitted']
        run07.run('c19-numerical-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib',
            'cohort_reuse::tests::','--','--nocapture','--test-threads=1'],300,
            [HERE/'C19_PROTOCOL.md',HERE/'prepare_c19_integration.py',Path(__file__),HERE/'artifacts/c19-v2-source-map.json'])
        log=(RAW/'c19-numerical-v1.log').read_text(encoding='utf-8');assert '9 passed; 0 failed; 1 ignored' in log
        exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        assert not frozen.exists();shutil.copyfile(exe,frozen)
        for fixture in ['small','large']:
            x=run(fixture,'candidate',layout=True);old=read(RAW/f'c14-{fixture}-layout-v1.json')
            assert x['interleaved_cdf'] and x['narrow_offsets'] and x['unrolled']
            for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
    elif stage=='screen':
        for fixture in ['small','large']:
            r=read(RAW/f'c19-{fixture}-layout-v1-exit.json');assert r['returncode']==0 and r['reason'] is None
        a=run('large','control');b=run('large','candidate');ratio=compare(a,b)
        print(json.dumps(dict(first_pair_ratio=ratio,passed_screen=ratio<.99,numerical_equal=True)),flush=True)
    elif stage=='extended':
        assert compare(read(RAW/'c19-large-control-1-bench.json'),read(RAW/'c19-large-candidate-1-bench.json'))<.99
        for fixture,pairs in [('large',[2,3]),('small',[1,2,3])]:
            for pair in pairs:
                rr={role:run(fixture,role,pair) for role in (['candidate','control'] if pair%2==0 else ['control','candidate'])}
                print(json.dumps(dict(fixture=fixture,pair=pair,ratio=compare(rr['control'],rr['candidate']))),flush=True)
    else:raise ValueError(stage)
if __name__=='__main__':main()
