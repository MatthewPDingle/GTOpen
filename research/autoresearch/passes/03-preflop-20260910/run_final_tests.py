"""Build then serialize final Cargo test binaries through the live-work guard."""
import json, os, subprocess, sys
from pathlib import Path
from measure import HERE, LAB, live_busy
mode, prefix = sys.argv[1:3]
if mode not in ('cpu','gpu','server'): raise SystemExit('mode must be cpu/gpu/server')
if live_busy(): raise SystemExit('Live workload active')
package = 'server' if mode=='server' else 'solver'
args = ['cargo','test','--release','-p',package,'--no-run','--message-format=json']
if mode!='cpu': args += ['--features','gpu']
if mode=='gpu':
    args += ['--lib']
    for name in ['preflop_gpu','gpu','cuda_resources','save_compat','save_locks','postflop_resume_state']:
        args += ['--test',name]
manifest = HERE/'raw'/f'{prefix}-build.jsonl'
errors = HERE/'raw'/f'{prefix}-build.stderr.log'
if manifest.exists() or errors.exists(): raise SystemExit('Prefix already used')
with manifest.open('w',encoding='utf8') as out, errors.open('w',encoding='utf8') as err:
    subprocess.run(args,cwd=LAB,stdout=out,stderr=err,check=True)
artifacts=[]
for line in manifest.read_text(encoding='utf8').splitlines():
    r=json.loads(line)
    if r.get('reason')=='compiler-artifact' and r.get('executable') and r.get('profile',{}).get('test'):
        artifacts.append((r['target']['name'],r['executable']))
if not artifacts: raise SystemExit('No compiled test executables')
env=os.environ.copy()
env.update(PREFLOP_TEST_CWD=str(LAB/'crates'/package),SOLVER_THREADS='16',RAYON_NUM_THREADS='16')
for name,exe in artifacts:
    subprocess.run([sys.executable,str(HERE/'run_guarded.py'),f'{prefix}-{name}',exe,'--test-threads=1'],env=env,check=True)
if mode=='gpu':
    lib=[exe for name,exe in artifacts if name=='solver']
    assert len(lib)==1
    for label,test in [('minimal','coupled_minimal_metadata_retains_former_union_budget_fit'),('normalization','coupled_minimum_budget_direct_and_normalized_paths_match')]:
        subprocess.run([sys.executable,str(HERE/'run_guarded.py'),f'{prefix}-{label}',lib[0],test,'--ignored','--nocapture','--test-threads=1'],env=env,check=True)
if mode=='cpu':
    if live_busy(): raise SystemExit('Live workload started before doc tests')
    with (HERE/'raw'/f'{prefix}-doctests.log').open('w',encoding='utf8') as stream:
        subprocess.run(['cargo','test','--release','-p','solver','--doc'],cwd=LAB,env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
print(json.dumps({'mode':mode,'prefix':prefix,'binaries':len(artifacts),'status':'passed'}))
