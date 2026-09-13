"""Guarded C07 profiling, with unprofiled matched numerical controls."""
import json,re,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
from run_c07 import snapshot
run07.RAW=HERE/'raw'

def main():
    rec=json.loads((run07.RAW/'d06-numerical-v1-exit.json').read_text());assert rec['returncode']==0 and rec['reason'] is None
    log=(run07.RAW/'d06-numerical-v1.log').read_text();assert '5 passed; 0 failed; 1 ignored' in log
    run07.run('d06-reuse-tests-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib',
        'exact_reuse::tests::','--','--nocapture','--test-threads=1'],240,[HERE/'D06_PROTOCOL.md'])
    assert '4 passed; 0 failed; 1 ignored' in (run07.RAW/'d06-reuse-tests-v1.log').read_text()
    exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    frozen=run07.LAB/'target/d06-profile-frozen.exe';assert not frozen.exists();shutil.copyfile(exe,frozen)
    for fixture in ['small','large']:
        source=run07.LAB/('target/convergence/eight-native-a/final.gtop' if fixture=='large' else 'target/convergence/behavioral-fixed-e0-v1/final.gtop')
        eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json';runs=[]
        for profile in [False,True]:
            name=f'd06-{fixture}-'+('profiled' if profile else 'control')+'-v1';out=run07.RAW/(name+'.json')
            snapshot(name,'before')
            run07.run(name,[frozen,'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark',
                '--exact','--ignored','--nocapture','--test-threads=1'],180,[source,eq,fit,frozen,HERE/'D06_PROTOCOL.md'],
                {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1',
                 'PREFLOP_GPU_COHORT_ENABLE':'1','PREFLOP_GPU_REUSE_PROFILE':str(int(profile)),'REALIZATION_FIT':str(fit)})
            snapshot(name,'after');runs.append(json.loads(out.read_text()))
        a,b=runs
        for k in ['input','nodes','initial_iteration','iteration','batch','cohort_plan','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k],k
        for x,y in zip(a['rows'],b['rows']):
            for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k],k
        print(json.dumps(dict(fixture=fixture,profile_numerically_equal=True)),flush=True)
if __name__=='__main__':main()
