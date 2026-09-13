"""Guarded retained C14 profiling, with unprofiled matched numerical controls."""
import json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
from run_c07 import snapshot
run07.RAW=HERE/'raw'

def main():
    stage=sys.argv[1];frozen=run07.LAB/'target/d11-profile-frozen.exe'
    if stage=='freeze':
        rec=json.loads((run07.RAW/'d11-tracing-v1-exit.json').read_text());assert rec['returncode']==0 and rec['reason'] is None
        log=(run07.RAW/'d11-tracing-v1.log').read_text();assert '1 passed; 0 failed' in log
        exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
        assert not frozen.exists();shutil.copyfile(exe,frozen);return
    assert stage in ['small','large'];fixture=stage
    source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
    eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json';runs=[]
    for profile in [False,True]:
        name=f'd11-{fixture}-'+('profiled' if profile else 'control')+'-v1';out=run07.RAW/(name+'.json')
        snapshot(name,'before')
        run07.run(name,[frozen,'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark',
            '--exact','--ignored','--nocapture','--test-threads=1'],180,[source,eq,fit,frozen,HERE/'D11_PROTOCOL.md',Path(__file__)],
            {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1',
             'PREFLOP_GPU_COHORT_ENABLE':'1','PREFLOP_GPU_TERMINAL_UNROLL':'1','PREFLOP_GPU_NARROW_OFFSETS':'1',
             'PREFLOP_GPU_REUSE_PROFILE':str(int(profile)),'REALIZATION_FIT':str(fit)})
        snapshot(name,'after');runs.append(json.loads(out.read_text()))
    a,b=runs;old=json.loads((run07.RAW/f'c14-{fixture}-candidate-1-bench.json').read_text())
    for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k]==old[k],k
    for x,y,z in zip(a['rows'],b['rows'],old['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k]==z[k],k
    print(json.dumps(dict(fixture=fixture,profile_numerically_equal=True)),flush=True)
if __name__=='__main__':main()
