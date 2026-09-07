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
restore(config['pass_baseline_commit'],'research fresh pass-start performance control')
try:
    run('B034','baseline','Fresh pass-start CUDA implementation on the current machine, with unchanged frozen workloads; compare final combined gains.', ['preflop_perf','preflop_generic_perf','preflop_target_perf','capacity_perf','postflop_perf'], True, 'baseline')
finally:
    restore(final,'research restore final retained GPU implementation after fresh control')
    config=json.loads((lab.HERE/'run.json').read_text()); config['final_kept_commit']=lab.git('rev-parse','HEAD'); (lab.HERE/'run.json').write_text(json.dumps(config,indent=2),encoding='utf-8',newline='\n')
run('G001','preflop_cuda','Final combined preflop source: all seven large fingerprints, 48 variants and unchanged target stopping states.', ['preflop_perf','preflop_generic_perf','preflop_target_perf','preflop_variants'])
run('G002','postflop_cuda','Final combined postflop source: saved states, resume and CPU query materialization, action menus and unchanged convergence targets.', ['postflop_perf','postflop_state_perf','postflop_resume_state','postflop_action_menus'],True)
run('G003','memory_transfers','Final combined memory and evaluation checks: actual device allocation, cold and warm lifecycle, and repeated first/capture/steady evaluations.', ['capacity_perf','postflop_capacity_perf','postflop_memory_perf','postflop_full_memory_perf','gpu_check_perf'])
run('G004','reports_profiles','Final combined server report adaptation tests and fixed 80-iteration performance workload.',[],package='server')
config=json.loads((lab.HERE/'run.json').read_text()); config['pass_final_runs']=['G001','G002','G003','G004']; (lab.HERE/'run.json').write_text(json.dumps(config,indent=2),encoding='utf-8',newline='\n')
print('Final combined research runs complete',flush=True)
