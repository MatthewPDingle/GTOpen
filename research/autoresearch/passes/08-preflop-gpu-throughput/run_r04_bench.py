"""Same-executable overhead pairs: C23 private constructor vs normal selection."""
import json
import sys
from pathlib import Path
from run_c23 import HERE, RAW, read, run07
from run_c07 import snapshot

def main():
    assert read(RAW/'r04-initial-verified.json')['admitted']
    fixture=sys.argv[1];assert fixture in ['small','large']
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    exe=run07.LAB/'target/r04-benchmark-frozen.exe';eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
    for pair in [1,2,3]:
        values={}
        for role in (['control','candidate'] if pair%2 else ['candidate','control']):
            run07.idle()
            name=f'r04-{fixture}-{role}-{pair}';out=RAW/(name+'-bench.json')
            snapshot(name,'before')
            run07.run(name,[exe,'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark','--exact','--ignored','--nocapture','--test-threads=1'],180,
                [source,eq,fit,exe,HERE/'R04_PROTOCOL.md',Path(__file__),HERE/'raw/r04-initial-verified.json'],
                {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'REALIZATION_FIT':str(fit),
                 'PREFLOP_GPU_REUSE_ENABLE':'1','PREFLOP_GPU_COHORT_ENABLE':'1','PREFLOP_GPU_TERMINAL_UNROLL':'1','PREFLOP_GPU_NARROW_OFFSETS':'1',
                 'PREFLOP_GPU_STATIC_CDF':str(int(role=='control')),'PREFLOP_GPU_PRODUCTION_SELECTION':str(int(role=='candidate'))})
            snapshot(name,'after');r=read(RAW/(name+'-exit.json'));assert r['returncode']==0 and r['reason'] is None
            values[role]=read(out)
        a,b=values['control'],values['candidate']
        for key in ['nodes','initial_iteration','iteration','arena_entries','arena_fingerprint','batch','cdf_bytes','static_cdf','cohort_plan']:
            assert a[key]==b[key],key
        assert b['selection']['static_cdf'] and b['selection']['narrow_offsets'] and b['selection']['static_cdf_fallback_reason'] is None
        for x,y in zip(a['rows'],b['rows']):
            for key in ['gaps','evs','iteration','index','warmup']:assert x[key]==y[key],key
        print(json.dumps({'fixture':fixture,'pair':pair,'ratio':b['complete_seconds']/a['complete_seconds'],'exact':True}),flush=True)

if __name__=='__main__':main()
