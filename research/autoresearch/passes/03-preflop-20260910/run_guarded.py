"""Run one already-built test executable with the same live-work safety guard."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from measure import HERE, ROOT, LAB, live_busy

run_id, exe, *args = sys.argv[1:]
exe = Path(exe).resolve()
if not exe.is_file() or exe.suffix.lower() != '.exe':
    raise SystemExit('Pass a built test executable, not a shell or cargo wrapper.')
if live_busy():
    raise SystemExit('User workload active; tests deferred.')
log = HERE/'raw'/f'{run_id}.log'
if log.exists():
    raise SystemExit('Choose an unused run ID.')
env=os.environ.copy()
env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env['PATH']
env['SOLVER_THREADS']='16'
env['RAYON_NUM_THREADS']='16'
record={'event':'validation','id':run_id,'utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'command':[str(exe),*args], 'executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),
        'commit':subprocess.check_output(['git','-C',str(LAB),'rev-parse','HEAD'],text=True).strip()}
reason=None
start=time.monotonic()
with log.open('w',encoding='utf-8') as output:
    proc=subprocess.Popen([str(exe),*args],cwd=LAB,env=env,stdout=output,stderr=subprocess.STDOUT,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    (HERE/'active.json').write_text(json.dumps({**record,'pid':proc.pid,'log':str(log)}),encoding='utf-8')
    while proc.poll() is None:
        time.sleep(3)
        try:
            busy=live_busy()
        except Exception as error:
            busy=True
            reason=f'Cannot verify user server: {error}'
        if busy or time.monotonic()-start > 600:
            reason=reason or ('User workload started' if busy else '600 second validation timeout')
            proc.kill()
            proc.wait()
            break
record.update(seconds=time.monotonic()-start,returncode=proc.returncode,reason=reason)
with (HERE/'events.jsonl').open('a',encoding='utf-8') as out:
    out.write(json.dumps(record)+'\n')
(HERE/'active.json').write_text(json.dumps({'running':False,'last':run_id}),encoding='utf-8')
print(json.dumps(record))
sys.exit(proc.returncode)
