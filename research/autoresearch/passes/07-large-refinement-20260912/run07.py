"""Guarded serial validation and large saved-game experiments."""
import hashlib,json,os,subprocess,sys,time,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
LAB=HERE.parents[3]
RAW=HERE/'raw'
RAW.mkdir(exist_ok=True)

def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def idle():
    for route in ('/api/preflop/status','/api/status','/api/reports/status'):
        with urllib.request.urlopen('http://127.0.0.1:56708'+route,timeout=3) as f:s=json.load(f)
        if s.get('state') in ('running','building') or s.get('running') is True:
            raise RuntimeError('User work active; stop owned research only')

def run(name,command,cap=600,inputs=(),overrides=None):
    idle();log=RAW/f'{name}.log';record_path=RAW/f'{name}-exit.json'
    if log.exists() or record_path.exists():raise RuntimeError('Existing output '+name)
    record=dict(command=list(map(str,command)),inputs={str(p):digest(p) for p in inputs},
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=LAB,text=True).strip(),
        source_diff_sha256=hashlib.sha256(subprocess.check_output(['git','diff','HEAD','--','crates'],cwd=LAB)).hexdigest())
    if Path(command[0]).is_file():record['exe_sha256']=digest(command[0])
    record['solver_source_files']={str(p.relative_to(LAB)):digest(p) for p in (LAB/'crates/solver').rglob('*') if p.is_file() and p.suffix in ('.rs','.cu','.toml')}
    env=os.environ.copy()
    for key in list(env):
        if key.startswith(('PREFLOP_MW_','PREFLOP_GPU_','PREFLOP_PHASE_','CONVERGENCE_')):del env[key]
    env['PATH']='T:/Dev/GTOpen/.cuda-nvrtc/nvidia/cuda_nvrtc/bin'+os.pathsep+env['PATH']
    env['RAYON_NUM_THREADS']='8'
    env.update(overrides or {})
    record['environment_overrides']=overrides or {}
    started=time.monotonic();reason=None
    with log.open('x') as f:
        child=subprocess.Popen(list(map(str,command)),cwd=LAB,env=env,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        print(json.dumps(dict(started=name,pid=child.pid)),flush=True)
        try:
            while child.poll() is None:
                time.sleep(1);idle()
                if time.monotonic()-started>cap:raise RuntimeError('Registered time cap')
        except Exception as e:
            reason=str(e)
            if child.poll() is None:subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        child.wait(timeout=30)
    for p,h in record['inputs'].items():
        if digest(p)!=h:reason='Input changed: '+p
    record.update(returncode=child.returncode,reason=reason,seconds=time.monotonic()-started)
    record_path.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(finished=name,returncode=child.returncode,reason=reason,seconds=record['seconds'])),flush=True)
    if child.returncode or reason:raise RuntimeError(name+' failed')

if __name__=='__main__':
    run('large-refine-tests',['cargo','test','--release','-p','solver','--features','preflop-research','--lib','convergence_','--','--nocapture'])
    run('large-refine-build',['cargo','build','--release','-p','solver','--features','preflop-research','--example','convergence_refine_large'])
    exe=LAB/'target/release/examples/convergence_refine_large.exe'
    cases=[('eight-native-a',HERE.parent/'05-preflop-convergence-20260911/raw/eight-native-a-local-v3.json'),
        ('followup-eight-gamma15-s64-42',HERE.parent/'06-preflop-followup-20260911/raw/followup-eight-gamma15-s64-42-local-v3.json')]
    for name,audit in cases:
        source=LAB/'target/convergence'/name/'final.gtop'
        out=LAB/'target/convergence'/('large-plan-'+name)
        run('plan-'+name,[exe,source,audit,'0',out],180,[source,audit])
        (RAW/f'plan-{name}.json').write_bytes((out/'plan.json').read_bytes())
