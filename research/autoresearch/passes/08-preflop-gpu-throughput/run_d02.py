from pathlib import Path
import sys,json,re
p=Path('research/autoresearch/passes/08-preflop-gpu-throughput').resolve()
sys.path.insert(0,str(p.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=p/'raw';run07.RAW.mkdir(exist_ok=True)
run07.run('d02-classifier-v2',['cargo','test','--release','-p','solver','--features','gpu,preflop-research','--lib','exact_reuse_classifier','--','--nocapture','--test-threads=1'],240,[p/'D02_PROTOCOL.md'])
log=(run07.RAW/'d02-classifier-v2.log').read_text()
m=re.search(r'Running unittests .*?\(([^)]+\.exe)\)',log)
if not m: raise RuntimeError('test executable absent')
exe=run07.LAB/m.group(1)
(p/'d02-test-executable.json').write_text(json.dumps({'path':str(exe),'sha256':run07.digest(exe)},indent=2)+'\n',encoding='utf-8')
for name,save in [('small','behavioral-fixed-e0-v1'),('large','eight-native-a')]:
 source=run07.LAB/'target/convergence'/save/'final.gtop'
 eq=run07.LAB/'cache/preflop_eq169.bin';fit=run07.LAB/'cache/realization_fit.json'
 out=run07.RAW/f'd02-{name}-v1.json'
 run07.run(f'd02-{name}-v1',[exe,'exact_reuse_inventory_from_saved_state','--ignored','--nocapture','--test-threads=1'],180,[source,eq,fit,p/'D02_PROTOCOL.md'],{'PREFLOP_GPU_REUSE_INPUT':str(source),'PREFLOP_GPU_REUSE_OUTPUT':str(out),'PREFLOP_GPU_REUSE_EQUITY':str(eq),'REALIZATION_FIT':str(fit)})
