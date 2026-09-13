"""Guarded C09 qualification and complete-work timing against C07."""
import json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
from run_c07 import snapshot
run07.RAW=HERE/'raw'

def run(fixture,role,pair=1,layout=False):
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json';exe=run07.LAB/'target/c09-benchmark-frozen.exe'
    name=f'c09-{fixture}-layout-v1' if layout else f'c09-{fixture}-{role}-{pair}'
    out=run07.RAW/(name+('.json' if layout else '-bench.json'))
    test='preflop::gpu::cohort_reuse::tests::cohort_constructor_from_saved_state' if layout else 'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark'
    snapshot(name,'before')
    run07.run(name,[exe,test,'--exact','--ignored','--nocapture','--test-threads=1'],180,[source,eq,fit,exe,HERE/'C09_PROTOCOL.md'],
        {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1',
         'PREFLOP_GPU_COHORT_ENABLE':'1','PREFLOP_GPU_TERMINAL_UNROLL':str(int(role=='candidate')),'REALIZATION_FIT':str(fit)})
    snapshot(name,'after');return json.loads(out.read_text())

def compare(a,b):
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k],k
    for x,y in zip(a['rows'],b['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k],k
    return b['complete_seconds']/a['complete_seconds']

def main():
    stage=sys.argv[1]
    if stage=='layouts':
        rec=json.loads((run07.RAW/'c09-numerical-v1-exit.json').read_text());assert rec['returncode']==0 and rec['reason'] is None
        log=(run07.RAW/'c09-numerical-v1.log').read_text();assert '5 passed; 0 failed; 1 ignored' in log
        run07.run('c09-reuse-tests-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib',
            'exact_reuse::tests::','--','--nocapture','--test-threads=1'],240,[HERE/'C09_PROTOCOL.md'])
        assert '4 passed; 0 failed; 1 ignored' in (run07.RAW/'c09-reuse-tests-v1.log').read_text()
        run07.run('c09-partial-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib','terminal_unroll::tests::','--','--nocapture','--test-threads=1'],240,[HERE/'C09_PROTOCOL.md'],{'PREFLOP_GPU_UNROLL_DIAGNOSTICS':str(HERE/'raw/c09-compiler-v1')})
        assert '1 passed; 0 failed' in (run07.RAW/'c09-partial-v1.log').read_text()
        exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        frozen=run07.LAB/'target/c09-benchmark-frozen.exe';assert not frozen.exists();shutil.copyfile(exe,frozen)
        for fixture in ['small','large']:
            x=run(fixture,'candidate',layout=True);old=json.loads((run07.RAW/f'c07-{fixture}-layout-v1.json').read_text())
            assert x['unrolled']
            for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
    elif stage=='screen':
        for fixture in ['small','large']:
            x=json.loads((run07.RAW/f'c09-{fixture}-layout-v1-exit.json').read_text());assert x['returncode']==0 and x['reason'] is None
        a=run('large','control');b=run('large','candidate');ratio=compare(a,b)
        print(json.dumps(dict(first_pair_ratio=ratio,passed_screen=ratio<.99,numerical_equal=True)),flush=True)
    elif stage=='extended':
        a=json.loads((run07.RAW/'c09-large-control-1-bench.json').read_text());b=json.loads((run07.RAW/'c09-large-candidate-1-bench.json').read_text());assert compare(a,b)<.99
        for fixture,pairs in [('large',[2,3]),('small',[1,2,3])]:
            for pair in pairs:
                result={role:run(fixture,role,pair) for role in (['candidate','control'] if pair%2==0 else ['control','candidate'])}
                print(json.dumps(dict(fixture=fixture,pair=pair,ratio=compare(result['control'],result['candidate']),numerical_equal=True)),flush=True)
    else:raise ValueError(stage)
if __name__=='__main__':main()
