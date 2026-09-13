"""Guarded C18 fixed-work screen; preserve every rejected run."""
import json,re,shutil,sys
from pathlib import Path
from run_r03 import HERE,run07,snapshot

def run(fixture,role,pair=1,layout=False):
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json';exe=run07.LAB/'target/c18-benchmark-frozen.exe'
    name=f'c18-{fixture}-layout-v1' if layout else f'c18-{fixture}-{role}-{pair}'
    out=run07.RAW/(name+('.json' if layout else '-bench.json'))
    test='preflop::gpu::cohort_reuse::tests::cohort_constructor_from_saved_state' if layout else 'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark'
    snapshot(name,'before')
    run07.run(name,[exe,test,'--exact','--ignored','--nocapture','--test-threads=1'],180,[source,eq,fit,exe,HERE/'C18_PROTOCOL.md',Path(__file__)],
        {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1',
         'PREFLOP_GPU_COHORT_ENABLE':'1','PREFLOP_GPU_TERMINAL_UNROLL':'1','PREFLOP_GPU_NARROW_OFFSETS':'1',
         'PREFLOP_GPU_RANK_COMPACT':str(int(role=='candidate')),'REALIZATION_FIT':str(fit)})
    snapshot(name,'after');return json.loads(out.read_text(encoding='utf8'))

def compare(a,b):
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','arena_entries','arena_fingerprint','narrow_offsets']:assert a[k]==b[k],k
    assert not a['rank_compact'] and b['rank_compact']
    assert a['rank_mapping_bytes']==0 and b['rank_mapping_bytes']==2080768
    assert b['extra_bytes']==a['extra_bytes']+2080768
    for x,y in zip(a['rows'],b['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k],k
    return b['complete_seconds']/a['complete_seconds']

if __name__=='__main__':
    stage=sys.argv[1]
    if stage=='freeze':
        rec=json.loads((run07.RAW/'c18-kernel-v2-exit.json').read_text());assert rec['returncode']==0 and rec['reason'] is None
        log=(run07.RAW/'c18-kernel-v2.log').read_text();assert '1 passed; 0 failed; 0 ignored' in log
        exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        frozen=run07.LAB/'target/c18-benchmark-frozen.exe';assert not frozen.exists();shutil.copyfile(exe,frozen)
    elif stage=='numerical':
        exe=run07.LAB/'target/c18-benchmark-frozen.exe'
        run07.run('c18-numerical-v3',[exe,'preflop::gpu::cohort_reuse::tests::','--nocapture','--test-threads=1'],180,
            [exe,HERE/'C18_PROTOCOL.md',Path(__file__)],{'PREFLOP_GPU_RANK_COMPACT':'1','PREFLOP_GPU_RANK_INTEGRATED_DIAGNOSTICS':str(run07.RAW/'c18-integrated-v2-compiler')})
    elif stage=='layout':
        rec=json.loads((run07.RAW/'c18-numerical-v3-exit.json').read_text());assert rec['returncode']==0 and rec['reason'] is None
        assert '8 passed; 0 failed; 1 ignored' in (run07.RAW/'c18-numerical-v3.log').read_text()
        for fixture in ['small','large']:
            x=run(fixture,'candidate',layout=True);old=json.loads((run07.RAW/f'c14-{fixture}-layout-v1.json').read_text())
            assert x['rank_compact'] and x['unrolled'] and x['narrow_offsets'] and x['rank_mapping_bytes']==2080768
            for k in ['plan','arenas_unchanged','batch','hu_cache']:assert x[k]==old[k],k
            new_buffers={k:v for k,v in x['buffer_bytes'].items() if k.startswith('rank_')}
            assert new_buffers==dict(rank_lower=692224,rank_upper=692224,rank_hand=692224,rank_count=4096)
            assert {k:v for k,v in x['buffer_bytes'].items() if not k.startswith('rank_')}==old['buffer_bytes']
            assert x['actual_device_bytes']==old['actual_device_bytes']+2080768
    elif stage=='screen':
        for fixture in ['small','large']:
            x=json.loads((run07.RAW/f'c18-{fixture}-layout-v1-exit.json').read_text());assert x['returncode']==0 and x['reason'] is None
        a=run('large','control');b=run('large','candidate');ratio=compare(a,b)
        old=json.loads((run07.RAW/'c14-large-candidate-1-bench.json').read_text())
        for k in ['arena_fingerprint','batch','cohort_plan','cdf_bytes','extra_bytes']:assert a[k]==old[k],k
        for x,y in zip(a['rows'],old['rows']):
            for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k],k
        print(json.dumps({'first_pair_ratio':ratio,'passed_screen':ratio<.99,'exact':True}),flush=True)
    elif stage=='extended':
        a=json.loads((run07.RAW/'c18-large-control-1-bench.json').read_text());b=json.loads((run07.RAW/'c18-large-candidate-1-bench.json').read_text());assert compare(a,b)<.99
        for fixture,pairs in [('large',[2,3]),('small',[1,2,3])]:
            for pair in pairs:
                result={role:run(fixture,role,pair) for role in (['candidate','control'] if pair%2==0 else ['control','candidate'])}
                print(json.dumps({'fixture':fixture,'pair':pair,'ratio':compare(result['control'],result['candidate']),'exact':True}),flush=True)
    else:raise ValueError(stage)
