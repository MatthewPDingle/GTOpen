from pathlib import Path
import json,sys,re
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
pre=json.loads((run07.RAW/'c05-numerical-v1-exit.json').read_text());assert pre['returncode']==0 and pre['reason'] is None
for p,h in pre['solver_source_files'].items():assert run07.digest(run07.LAB/p)==h,p
log=(run07.RAW/'c05-numerical-v1.log').read_text();exe=run07.LAB/re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log).group(1)
source=run07.LAB/'target/convergence/eight-native-a/final.gtop';eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
runs=[]
for enabled in [False,True]:
    name='c05-large-'+('candidate' if enabled else 'control')+'-profile-v1';out=run07.RAW/(name+'.json')
    run07.run(name,[exe,'preflop::gpu::exact_reuse::tests::exact_reuse_frozen_benchmark','--exact','--ignored','--nocapture','--test-threads=1'],180,
        [source,eq,fit,HERE/'C05_DIAGNOSTIC.md',exe],{'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_ENABLE':'1','PREFLOP_GPU_ALIGNED':str(int(enabled)),'PREFLOP_GPU_REUSE_PROFILE':'1','REALIZATION_FIT':str(fit)})
    runs.append(json.loads(out.read_text()))
a,b=runs
assert a['arena_fingerprint']==b['arena_fingerprint']
for x,y in zip(a['rows'],b['rows']):
    for k in ['gaps','evs','index','iteration','warmup']:assert x[k]==y[k],k
print('Diagnostic pair complete; exact outputs match.',flush=True)
