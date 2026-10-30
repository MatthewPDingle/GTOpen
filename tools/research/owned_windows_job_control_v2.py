"""Bounded lifecycle control using only newly spawned hidden test processes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import uuid
import psutil
from owned_windows_job_v1 import OwnedJob

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME = 'owned-windows-job-control-v2'
STORE = OUT/NAME
REG = OUT/(NAME+'-registration.json')
RESULT = OUT/(NAME+'-result.json')
SELF = Path(__file__).resolve()


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p, x):
    p=Path(p);temp=p.with_name(p.name+'.tmp-'+uuid.uuid4().hex)
    with temp.open('x', encoding='utf-8') as f:
        json.dump(x, f);f.flush();os.fsync(f.fileno())
    os.rename(temp,p)  # Windows refuses an existing destination.
def read(p): return json.loads(Path(p).read_text())
def identity(p): return dict(pid=p.pid, created=psutil.Process(p.pid).create_time())
def live(x):
    try: return psutil.Process(x['pid']).create_time() == x['created']
    except psutil.NoSuchProcess: return False
def wait_for(fn, seconds=10):
    end=time.monotonic()+seconds
    while not fn():
        if time.monotonic()>end: raise TimeoutError('Lifecycle control deadline')
        time.sleep(.05)
def launch(*args):
    return subprocess.Popen([sys.executable, '-B', str(SELF), *map(str,args)],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW)


def worker(folder, owner=False):
    folder=Path(folder)
    wait_for(lambda:(folder/'permit.json').exists())
    if owner:
        owned=folder/'owned';owned.mkdir()
        job=OwnedJob();child=launch('--worker',owned);job.assign(child)
        save(owned/'permit.json',{})
        wait_for(lambda:(owned/'tree.json').exists())
        save(folder/'tree.json',dict(owner=identity(psutil.Process()), **read(owned/'tree.json')))
        time.sleep(120)  # Outer control terminates this owner, closing its OS handle.
    else:
        child=subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(120)'],
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW)
        save(folder/'tree.json',dict(root=identity(psutil.Process()),grandchild=identity(child)))
        time.sleep(120)


def main():
    assert not any(p.exists() for p in (REG,RESULT,STORE)), 'Preserve earlier attempts'
    began=time.monotonic();STORE.mkdir()
    inputs={str(p):sha(p) for p in (SELF,SELF.with_name('owned_windows_job_v1.py'))}
    save(REG,dict(inputs=inputs,maximum_seconds=60,gpu_used=False,
        cases=['normal exit','close kills owned tree only','owner termination closes job'],
        production_modified=False))
    outsider=None;owned=[];jobs=[]
    result=dict(passed=False,registration_sha256=sha(REG),gpu_used=False,production_modified=False)
    try:
        normal=OwnedJob();jobs.append(normal)
        p=subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(2)'],
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW)
        owned.append(p);normal.assign(p);assert p.wait(timeout=5)==0
        wait_for(lambda:normal.accounting()['active_processes']==0)
        normal.close()
        outsider=subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(120)'],
            stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW)
        folder=STORE/'close';folder.mkdir();job=OwnedJob();jobs.append(job)
        p=launch('--worker',folder);owned.append(p);job.assign(p);save(folder/'permit.json',{})
        wait_for(lambda:(folder/'tree.json').exists());tree=read(folder/'tree.json')
        result['close_case_accounting']=job.accounting()
        result['close_case_descendants']=[dict(identity(c), name=c.name()) for c in psutil.Process(p.pid).children(recursive=True)]
        assert job.accounting()['active_processes']>=2, result['close_case_accounting']
        job.close();p.wait(timeout=5)
        wait_for(lambda:not any(live(x) for x in tree.values()))
        assert outsider.poll() is None
        folder=STORE/'owner-exit';folder.mkdir()
        p=launch('--owner',folder);owned.append(p);save(folder/'permit.json',{})
        wait_for(lambda:(folder/'tree.json').exists());tree=read(folder/'tree.json')
        # Only this newly created Popen owner is terminated; OS closes its job.
        p.terminate();p.wait(timeout=5)
        wait_for(lambda:not any(live(x) for x in tree.values()))
        assert outsider.poll() is None
        for path,h in inputs.items():assert sha(path)==h
        assert time.monotonic()-began<60
        result.update(passed=True,normal_exit=True,owned_descendants_terminated=True,
                      unrelated_test_process_survived=True,owner_exit_cleanup=True)
    except BaseException as error:
        result.update(error=repr(error),traceback=traceback.format_exc())
        raise
    finally:
        for job in jobs:job.close()
        for p in owned:
            if p.poll() is None:p.terminate()
            p.wait(timeout=5)
        if outsider is not None:
            if outsider.poll() is None:outsider.terminate()
            outsider.wait(timeout=5)
        result['seconds']=time.monotonic()-began;save(RESULT,result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--worker');parser.add_argument('--owner')
    args=parser.parse_args()
    if args.worker:worker(args.worker)
    elif args.owner:worker(args.owner,owner=True)
    else:main()

