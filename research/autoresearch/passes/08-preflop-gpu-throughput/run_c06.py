"""C06 guarded first large pair; no extended runs until the screen passes."""
import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
def main():
    for name in ['c06-expanded-numerical-v2','c06-small-layout-v1','c06-large-layout-v1']:
        rec=json.loads((run07.RAW/(name+'-exit.json')).read_text());assert rec['returncode']==0 and rec['reason'] is None
    run07.run('c06-benchmark-build-v1',['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib',
        'cohort_reuse','--','--nocapture','--test-threads=1'],240,[HERE/'C06_PROTOCOL.md'])
    log=(run07.RAW/'c06-benchmark-build-v1.log').read_text();assert '3 passed; 0 failed; 1 ignored' in log
    exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
    results=[]
    for enabled in [False,True]:
        source=run07.LAB/'target/convergence/eight-native-a/final.gtop'
        eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
        name='c06-large-'+('candidate' if enabled else 'control')+'-1';out=run07.RAW/(name+'-bench.json')
        run07.run(name,[exe,'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark',
            '--exact','--ignored','--nocapture','--test-threads=1'],180,[source,eq,fit,exe,HERE/'C06_PROTOCOL.md'],
            {'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1',
            'PREFLOP_GPU_COHORT_ENABLE':str(int(enabled)),'REALIZATION_FIT':str(fit)})
        results.append(json.loads(out.read_text()))
    a,b=results
    for k in ['input','nodes','initial_iteration','iteration','batch','arena_entries','arena_fingerprint','original_cdf_bytes']:assert a[k]==b[k],k
    for x,y in zip(a['rows'],b['rows']):
        for k in ['gaps','evs','iteration','index','warmup']:assert x[k]==y[k],k
    ratio=b['complete_seconds']/a['complete_seconds']
    print(json.dumps({'first_pair_ratio':ratio,'passed_screen':ratio<.99,'numerical_equal':True}),flush=True)
if __name__=='__main__':main()
