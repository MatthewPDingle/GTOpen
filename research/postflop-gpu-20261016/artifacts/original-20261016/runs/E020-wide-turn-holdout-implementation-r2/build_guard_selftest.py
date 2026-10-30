"""Host-only prospective build-provenance checks; never launches Cargo or CUDA."""
from pathlib import Path
import copy, hashlib, importlib.util, json, sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
R1=HERE.with_name('E020-wide-turn-holdout-implementation')
spec=importlib.util.spec_from_file_location('holdout_r2',HERE/'run.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
results=[]
def check(name,fn,reject=False):
    try:fn()
    except AssertionError as error:
        assert reject,(name,str(error))
        results.append({'name':name,'expected_rejection':True,'passed':True,'error':str(error)})
    else:
        assert not reject,name
        results.append({'name':name,'expected_rejection':False,'passed':True})
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for role in ['E015','E020']:
    binary=R1/'build/binaries'/f'{role}-holdout.exe'
    check(f'R1_{role}_binary_expected_arm',lambda role=role,binary=binary:runner.embedded_cuda(binary,role+'-holdout'),role=='E020')
check('R1_resource_contains_both',lambda:runner.embedded_cuda(R1/'build/binaries/E015-resource.exe','E015-resource'))
check('resource_cannot_substitute_holdout',lambda:runner.embedded_cuda(R1/'build/binaries/E015-resource.exe','E015-holdout'),True)
logs=[json.loads(line) for line in (R1/'build/E015/stdout.log').read_text(encoding='utf-8').splitlines()]
workspace=HERE/'workspaces/E015';target=runner.TARGET/'E015'
wanted={'postflop_wide_turn_holdout':'E015-holdout','postflop_wide_turn_resources':'E015-resource'}
oldtarget=runner.ROOT/'build-holdout-e020'
def relocated(value):
    if isinstance(value,str):return value.replace(str(oldtarget),str(target)).replace(str(R1),str(HERE))
    if isinstance(value,list):return [relocated(x) for x in value]
    if isinstance(value,dict):return {k:relocated(v) for k,v in value.items()}
    return value
valid=relocated(logs)
check('synthetic_isolated_fresh_metadata',lambda:runner.check_cargo_artifacts(valid,workspace,target,wanted))
def mutated(target_name,key,value):
    changed=copy.deepcopy(valid)
    row=next(x for x in changed if x.get('reason')=='compiler-artifact' and x['target']['name']==target_name)
    if key.startswith('target.'):row['target'][key.split('.')[1]]=value
    else:row[key]=value
    return changed
for name,rows in [
    ('cached_solver',mutated('solver','fresh',True)),
    ('cached_holdout',mutated('postflop_wide_turn_holdout','fresh',True)),
    ('wrong_solver_manifest',mutated('solver','manifest_path',str(HERE/'workspaces/E020/crates/solver/Cargo.toml'))),
    ('wrong_solver_source',mutated('solver','target.src_path',str(HERE/'workspaces/E020/crates/solver/src/lib.rs'))),
    ('wrong_evaluator_source',mutated('postflop_wide_turn_holdout','target.src_path',str(HERE/'resource.rs'))),
    ('cross_arm_executable',mutated('postflop_wide_turn_holdout','executable',str(runner.TARGET/'E020/old.exe'))),
    ('cross_arm_dependency',mutated('solver','filenames',[str(runner.TARGET/'E020/libsolver.rlib')]))]:
    check(name,lambda rows=rows:runner.check_cargo_artifacts(rows,workspace,target,wanted),True)
check('unaltered_R1_shared_target_logs',lambda:runner.check_cargo_artifacts(logs,workspace,target,wanted),True)
out=HERE/'build-guard-selftest.json'
with out.open('x',encoding='utf-8',newline='\n') as f:
    json.dump({'status':'pass','scope':'host-only guard checks using preserved invalid R1 binaries/logs and labeled synthetic metadata',
      'cases':results,'native_tests':0,'compiler_executions':0,'gpu_executions':0,
      'runner_sha256':sha(HERE/'run.py'),'script_sha256':sha(Path(__file__)),
      'R1_inputs':{str(p):sha(p) for p in [R1/'build/E015/stdout.log',R1/'build/binaries/E015-holdout.exe',R1/'build/binaries/E020-holdout.exe',R1/'build/binaries/E015-resource.exe']}},f,indent=2);f.write('\n')
print(json.dumps({'status':'pass','cases':len(results),'report':str(out),'gpu_executions':0}))
