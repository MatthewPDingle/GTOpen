"""Serial retained-C01 eager phase diagnosis, not a speed candidate."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
def main():
    pre=json.loads((run07.RAW/'d03-numerical-v2-exit.json').read_text())
    assert pre['returncode']==0 and pre['reason'] is None
    for p,h in pre['solver_source_files'].items():assert run07.digest(run07.LAB/p)==h,p
    log=(run07.RAW/'d03-numerical-v2.log').read_text()
    assert '4 passed; 0 failed; 1 ignored' in log
    exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    for fixture,save in [('small','behavioral-fixed-e0-v1'),('large','eight-native-a')]:
        results=[]
        for profiled in [False,True]:
            name=f"d03-{fixture}-{'profiled' if profiled else 'control'}-v1"
            source=run07.LAB/'target/convergence'/save/'final.gtop'
            eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
            out=run07.RAW/(name+'.json')
            run07.run(name,[exe,'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark','--exact','--ignored','--nocapture','--test-threads=1'],180,
                [source,eq,fit,HERE/'D03_PROTOCOL.md',exe],
                {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1','PREFLOP_GPU_REUSE_PROFILE':str(int(profiled)),'REALIZATION_FIT':str(fit)})
            results.append(json.loads(out.read_text()))
        a,b=results
        for k in ['input','nodes','iteration','initial_iteration','batch','cdf_bytes','extra_bytes','arena_entries','arena_fingerprint']:assert a[k]==b[k],(fixture,k)
        assert len(a['rows'])==len(b['rows'])==6
        for x,y in zip(a['rows'],b['rows']):
            for k in ['index','iteration','warmup','gaps','evs']:assert x[k]==y[k],(fixture,k)
        print(json.dumps({'fixture':fixture,'exact_checkpoints_and_arena':True}),flush=True)
if __name__=='__main__':main()
