"""Run one owned offline GPU experiment, with read-only live-app guard."""
import hashlib, json, os, subprocess, sys, time, urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parent
LAB = HERE.parents[3]
ROOT = Path('T:/Dev/GTOpen')

def idle():
    for route in ('/api/preflop/status','/api/status','/api/reports/status'):
        with urllib.request.urlopen('http://127.0.0.1:56708'+route,timeout=3) as f: s=json.load(f)
        if s.get('state') in ('running','building') or s.get('running') is True:
            raise RuntimeError('User work active; stopped owned research process')

def run(name, input_path, schedule, samples, seed, limit, cadence, cap=7200):
    idle()
    raw=HERE/'raw';raw.mkdir(exist_ok=True)
    out=LAB/'target/convergence'/name
    exe=LAB/'target/release/examples/convergence_bench.exe'
    env=os.environ.copy()
    for k in list(env):
        if k.startswith(('PREFLOP_MW_','PREFLOP_GPU_','PREFLOP_PHASE_')): del env[k]
    env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env['PATH']
    env['RAYON_NUM_THREADS']='8'
    cmd=[str(exe),str(input_path),schedule,str(samples),str(seed),str(limit),str(cadence),str(out)]
    record={'name':name,'command':cmd,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=LAB,text=True).strip(),
        'diff_sha256':hashlib.sha256(subprocess.check_output(['git','diff','HEAD','--','crates'],cwd=LAB)).hexdigest(),
        'exe_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
        'cache_sha256':hashlib.sha256((LAB/'cache/preflop_eq169.bin').read_bytes()).hexdigest(),
        'fit_sha256':hashlib.sha256((LAB/'cache/realization_fit.json').read_bytes()).hexdigest(),
        'started_unix':time.time(),'cap_seconds':cap,'target':env.get('CONVERGENCE_TARGET','0.005')}
    with (raw/(name+'-protocol.json')).open('x') as f: json.dump(record,f,indent=2)
    reason=None;started=time.monotonic()
    with (raw/(name+'.log')).open('x') as log:
        p=subprocess.Popen(cmd,cwd=LAB,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        (HERE/'active.json').write_text(json.dumps({'pid':p.pid,'name':name,'exe':str(exe),'started_unix':time.time()}))
        try:
            while p.poll() is None:
                time.sleep(1)
                idle()
                if time.monotonic()-started>cap: raise RuntimeError('Registered wall-clock cap reached')
        except Exception as e:
            reason=str(e)
            if p.poll() is None: p.kill()
        finally:
            p.wait(timeout=30)
    record.update(returncode=p.returncode,seconds=time.monotonic()-started,reason=reason)
    (HERE/'active.json').write_text(json.dumps({'last_pid':p.pid,'name':name,'returncode':p.returncode,'running':False}))
    (raw/(name+'-exit.json')).write_text(json.dumps(record,indent=2))
    if (out/'result.json').exists(): (raw/(name+'-result.json')).write_bytes((out/'result.json').read_bytes())
    print(json.dumps(record),flush=True)
    if reason or p.returncode: raise RuntimeError(reason or 'Benchmark failed')

if __name__=='__main__':
    run(sys.argv[1],Path(sys.argv[2]),sys.argv[3],*map(int,sys.argv[4:]))
