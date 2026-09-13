"""Three paired integration-overhead checks against explicit retained C14."""
import json,statistics
from pathlib import Path
from run_r03_v3 import HERE,run07,snapshot

def run(fixture,role,pair):
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
    exe=run07.LAB/'target/r03-v3-qualification-frozen.exe'
    name=f'r03-v3-bench-{fixture}-{role}-{pair}';out=run07.RAW/(name+'.json')
    snapshot(name,'before')
    run07.run(name,[exe,'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark','--exact','--ignored','--nocapture','--test-threads=1'],180,
        [source,eq,fit,exe,HERE/'R03_PROTOCOL.md',HERE/'R03_QUALIFICATION.md',HERE/'R03_V3.md',Path(__file__)],
        {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),
         'PREFLOP_GPU_REUSE_ENABLE':'1','PREFLOP_GPU_COHORT_ENABLE':'1','PREFLOP_GPU_TERMINAL_UNROLL':'1',
         'PREFLOP_GPU_NARROW_OFFSETS':'1','PREFLOP_GPU_PRODUCTION_SELECTION':str(int(role=='adaptive')),'REALIZATION_FIT':str(fit)})
    snapshot(name,'after');return json.loads(out.read_text())

if __name__=='__main__':
    results={}
    for fixture in ['large','small']:
        ratios=[];old=json.loads((run07.RAW/f'c14-{fixture}-candidate-1-bench.json').read_text())
        for pair in [1,2,3]:
            xs={role:run(fixture,role,pair) for role in (['adaptive','retained'] if pair%2==0 else ['retained','adaptive'])}
            for role,x in xs.items():
                for key in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:
                    assert x[key]==old[key],(fixture,role,key)
                for a,b in zip(x['rows'],old['rows']):
                    for k in ['index','iteration','gaps','evs','warmup']:assert a[k]==b[k],k
                assert x['narrow_offsets'] and x['production_selection']==(role=='adaptive')
            ratio=xs['adaptive']['complete_seconds']/xs['retained']['complete_seconds'];ratios.append(ratio)
            print(json.dumps(dict(fixture=fixture,pair=pair,ratio=ratio,exact=True)),flush=True)
        results[fixture]=dict(ratios=ratios,median=statistics.median(ratios),passed=statistics.median(ratios)<=1.03)
    print(json.dumps(results,indent=2),flush=True)
