"""Guarded C16 fixed-work screen; preserve every rejected run."""
import json,re,shutil,sys
from pathlib import Path
from run_r03 import HERE,run07,snapshot

def run(fixture,role,pair=1,layout=False):
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json';exe=run07.LAB/'target/c16-benchmark-frozen.exe'
    name=f'c16-{fixture}-layout-v1' if layout else f'c16-{fixture}-{role}-{pair}'
    out=run07.RAW/(name+('.json' if layout else '-bench.json'))
    test='preflop::gpu::cohort_reuse::tests::cohort_constructor_from_saved_state' if layout else 'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark'
    snapshot(name,'before')
    run07.run(name,[exe,test,'--exact','--ignored','--nocapture','--test-threads=1'],180,[source,eq,fit,exe,HERE/'C16_PROTOCOL.md',HERE/'C16_INTEGRATION.md',Path(__file__)],
        {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1',
         'PREFLOP_GPU_COHORT_ENABLE':'1','PREFLOP_GPU_TERMINAL_UNROLL':'1','PREFLOP_GPU_NARROW_OFFSETS':'1',
         'PREFLOP_GPU_FUSED_CDF':str(int(role=='candidate')),'REALIZATION_FIT':str(fit)})
    snapshot(name,'after');return json.loads(out.read_text(encoding='utf8'))

def compare(a,b):
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint','narrow_offsets']:assert a[k]==b[k],k
    assert not a['fused_cdf'] and b['fused_cdf']
    for x,y in zip(a['rows'],b['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k],k
    return b['complete_seconds']/a['complete_seconds']

if __name__=='__main__':
    stage=sys.argv[1]
    if stage=='freeze-layout':
        rec=json.loads((run07.RAW/'c16-numerical-v1-exit.json').read_text());assert rec['returncode']==0 and rec['reason'] is None
        log=(run07.RAW/'c16-numerical-v1.log').read_text();assert '6 passed; 0 failed; 1 ignored' in log
        exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        frozen=run07.LAB/'target/c16-benchmark-frozen.exe';assert not frozen.exists();shutil.copyfile(exe,frozen)
        for fixture in ['small','large']:
            x=run(fixture,'candidate',layout=True);old=json.loads((run07.RAW/f'c14-{fixture}-layout-v1.json').read_text())
            assert x['fused_cdf'] and x['unrolled'] and x['narrow_offsets']
            for k in ['plan','buffer_bytes','actual_device_bytes','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
    elif stage=='screen':
        for fixture in ['small','large']:
            x=json.loads((run07.RAW/f'c16-{fixture}-layout-v1-exit.json').read_text());assert x['returncode']==0 and x['reason'] is None
        a=run('large','control');b=run('large','candidate');ratio=compare(a,b)
        old=json.loads((run07.RAW/'c14-large-candidate-1-bench.json').read_text())
        for k in ['arena_fingerprint','batch','cohort_plan','cdf_bytes','extra_bytes']:assert a[k]==old[k],k
        for x,y in zip(a['rows'],old['rows']):
            for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k],k
        print(json.dumps({'first_pair_ratio':ratio,'passed_screen':ratio<.99,'exact':True}),flush=True)
    elif stage=='extended':
        a=json.loads((run07.RAW/'c16-large-control-1-bench.json').read_text());b=json.loads((run07.RAW/'c16-large-candidate-1-bench.json').read_text());assert compare(a,b)<.99
        for fixture,pairs in [('large',[2,3]),('small',[1,2,3])]:
            for pair in pairs:
                result={role:run(fixture,role,pair) for role in (['candidate','control'] if pair%2==0 else ['control','candidate'])}
                print(json.dumps({'fixture':fixture,'pair':pair,'ratio':compare(result['control'],result['candidate']),'exact':True}),flush=True)
    else:raise ValueError(stage)
