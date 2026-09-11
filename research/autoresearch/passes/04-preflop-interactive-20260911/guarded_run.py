"""Run an owned research executable; stop it if live work starts or its cap expires."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import shutil
import time
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LAB = ROOT/'target/autoresearch/preflop-interactive-20260911'
DEADLINE = dt.datetime.fromisoformat('2026-09-11T03:03:27+00:00')

def live_idle():
    for route in ('/api/preflop/status','/api/status','/api/reports/status'):
        with urllib.request.urlopen('http://127.0.0.1:56708'+route,timeout=3) as f:
            status=json.load(f)
        if status.get('state')=='running' or status.get('running') is True:
            raise RuntimeError('User solve or report started')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--timeout',type=int,default=600)
    ap.add_argument('--cwd',type=Path,default=LAB)
    ap.add_argument('id')
    ap.add_argument('exe',type=Path)
    ap.add_argument('args',nargs=argparse.REMAINDER)
    a=ap.parse_args()
    if not a.id.replace('-','').replace('_','').isalnum(): raise SystemExit('Invalid run ID')
    exe=a.exe.resolve()
    if not exe.is_file() or exe.suffix.lower()!='.exe': raise SystemExit('Built executable required')
    if a.timeout<=0 or a.timeout>3600: raise SystemExit('Timeout must be 1..3600 seconds')
    live_idle()
    if dt.datetime.now(dt.timezone.utc)>=DEADLINE: raise SystemExit('Research window elapsed')
    raw=HERE/'raw';raw.mkdir(exist_ok=True)
    log=raw/(a.id+'.log')
    digest=hashlib.sha256(exe.read_bytes()).hexdigest()
    frozen_dir=LAB/'target/research-binaries';frozen_dir.mkdir(exist_ok=True)
    frozen_exe=frozen_dir/(exe.stem+'-'+digest[:16]+'.exe')
    if not frozen_exe.exists():shutil.copy2(exe,frozen_exe)
    if hashlib.sha256(frozen_exe.read_bytes()).hexdigest()!=digest:raise SystemExit('Frozen binary mismatch')
    env=os.environ.copy()
    removed={k:v for k,v in env.items() if k.startswith(('PREFLOP_MW_','PREFLOP_GPU_','PREFLOP_PHASE_'))}
    for k in removed:del env[k]
    cache_bytes=(ROOT/'cache/preflop_eq169.bin').read_bytes()
    cache_samples=int.from_bytes(cache_bytes[:4],'little')
    if len(cache_bytes)!=4+169*169*4 or cache_samples<=0:raise SystemExit('Invalid frozen equity cache')
    fixed_env={'SOLVER_THREADS':'16','RAYON_NUM_THREADS':'16','SOLVER_GPU':'1',
               'SOLVER_GPU_MEM_MB':'23000','PREFLOP_EQ_SAMPLES':str(cache_samples),
               'REALIZATION_FIT':str(ROOT/'cache/realization_fit.json')}
    env.update(fixed_env)
    env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env['PATH']
    record={'id':a.id,'started_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'command':[str(frozen_exe),*a.args],'cwd':str(a.cwd.resolve()),
            'original_executable':str(exe),'executable_sha256':digest,
            'fixed_environment':fixed_env,'removed_experiment_environment':removed,
            'equity_cache_sha256':hashlib.sha256(cache_bytes).hexdigest(),
            'realization_fit_sha256':hashlib.sha256((ROOT/'cache/realization_fit.json').read_bytes()).hexdigest(),
            'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=LAB,text=True).strip(),
            'working_diff_sha256':hashlib.sha256(subprocess.check_output(['git','diff','HEAD'],cwd=LAB)).hexdigest(),
            'timeout_seconds':a.timeout,'live_guard_seconds':0.5,'log':str(log)}
    with (raw/(a.id+'-protocol.json')).open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
    start=time.monotonic();reason=None
    with log.open('x',encoding='utf-8') as f:
        process=subprocess.Popen(record['command'],cwd=a.cwd,env=env,stdout=f,stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        (HERE/'active.json').write_text(json.dumps({**record,'running':True,'pid':process.pid}))
        try:
            while process.poll() is None:
                time.sleep(0.5)
                live_idle()
                if time.monotonic()-start>a.timeout: raise RuntimeError('Bounded run timeout')
                if dt.datetime.now(dt.timezone.utc)>=DEADLINE: raise RuntimeError('Research deadline')
        except Exception as error:
            reason=str(error)
            if process.poll() is None:process.kill()
        finally:
            process.wait(timeout=30)
            record.update(seconds=time.monotonic()-start,returncode=process.returncode,reason=reason)
            with (raw/(a.id+'-result.json')).open('x',encoding='utf-8') as f:json.dump(record,f,indent=2)
            (HERE/'active.json').write_text(json.dumps({'running':False,'last':a.id}))
    print(json.dumps(record))
    if reason or process.returncode: raise SystemExit(1)

if __name__=='__main__':main()
