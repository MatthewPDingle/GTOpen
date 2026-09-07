"""Fresh pass-start control followed by the final combined GPU workloads."""
from pathlib import Path
import json
import subprocess
import sys
import lab
config=json.loads((lab.HERE/'run.json').read_text())
final=config['final_kept_commit']
files=['crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/kernels.cu','crates/solver/src/gpu/plan.rs','crates/solver/src/preflop/gpu.rs','crates/solver/src/preflop/kernels.cu']
def restore(commit, message):
    for name in files:
        (lab.LAB/name).write_bytes(subprocess.check_output(['git','show',commit+':'+name],cwd=lab.LAB))
    subprocess.run(['git','add',*files],cwd=lab.LAB,check=True)
    subprocess.run(['git','commit','--allow-empty','-m',message],cwd=lab.LAB,check=True)
def run(id,path,hypothesis,tests,convergence=False,status='candidate',package='solver'):
    cmd=[sys.executable,str(lab.HERE/'lab.py'),'run','--id',id,'--path',path,'--status',status,'--hypothesis',hypothesis]
    if convergence: cmd+=['--env','POSTFLOP_PERF_CONVERGENCE=1']
    cmd+=['--','cargo','test','--release','-p',package,'--features','gpu']
    for test in tests: cmd+=['--test',test]
    cmd+=['--','--include-ignored','--nocapture','--test-threads=1']
    print('Running '+id,flush=True)
    with (lab.HERE/'raw'/('runner-'+id+'.log')).open('w',encoding='utf-8') as log:
        subprocess.run(cmd,cwd=lab.ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    result=next(r for r in lab.rows() if r['id']==id)
    assert result['returncode']==0, id+' failed'
restore(config['pass_baseline_commit'],'research fresh pass-start postflop and memory control')
try:
    run('B035','baseline','Fresh pass-start fixed-step postflop, device memory, full cold/warm transfers, and first/capture/steady checks; original source and frozen inputs.', ['postflop_perf','postflop_memory_perf','postflop_full_memory_perf','gpu_check_perf'],status='baseline')
finally:
    restore(final,'research restore final retained source after postflop lifecycle control')
    config=json.loads((lab.HERE/'run.json').read_text()); config['final_kept_commit']=lab.git('rev-parse','HEAD'); (lab.HERE/'run.json').write_text(json.dumps(config,indent=2),encoding='utf-8',newline='\n')
run('G005','postflop_cuda','Final combined fixed-step postflop and lifecycle comparison after fresh B035; numerical output and workload unchanged.', ['postflop_perf','postflop_memory_perf','postflop_full_memory_perf','gpu_check_perf'])
config=json.loads((lab.HERE/'run.json').read_text()); config['pass_final_runs'].append('G005'); (lab.HERE/'run.json').write_text(json.dumps(config,indent=2),encoding='utf-8',newline='\n')
print('Fresh postflop lifecycle controls complete',flush=True)
