"""Resume frozen GPU experiments only while the production solver is idle.

This is a manual, foreground research runner, not a scheduled automation.
It never stops, rebuilds or modifies the production server.
"""
import os
import time
import json
import hashlib
import subprocess
import urllib.request
import integrated_coverage as c

OUT=c.OUT
PANELS=['old-two-orbits','panel-a','panel-b','panel-ab','old-two-literal-half','old-two-orbits-two-sizes']
def idle():
    for route in ['preflop/status','status','reports/status']:
        with urllib.request.urlopen('http://localhost:56708/api/'+route,timeout=5) as response:
            d=json.load(response)
        if route=='reports/status':
            if d.get('running') is not False:return False
        elif d.get('state') not in ['idle','done','stopped','ready','empty','error']:
            return False
    return True

def archive_partial(path):
    if not path.exists():return
    data=json.loads(path.read_text());iteration=data['records'][-1]['iteration']
    target=path.with_name(path.stem+f'-interrupted-{iteration}-{time.time_ns()}.json')
    assert not target.exists();path.rename(target)

def run():
    upstream=json.loads((c.s.OUT.parent/'conditional-hu-20260919/freeze.json').read_text())['inputs']
    for path in ['research/preflop-evolution/conditional-hu-20260919/subtree.json',
                 'saves/preflop/wizard-nl25-baseline-20260919-refined.gtop']:
        assert hashlib.sha256((c.s.ROOT/path).read_bytes()).hexdigest()==upstream[path],path
    for name in ['freeze.json','control-freeze.json']:
        for path,digest in json.loads((OUT/name).read_text())['inputs'].items():
            assert hashlib.sha256((c.s.ROOT/path).read_bytes()).hexdigest()==digest,path
    if not idle():raise SystemExit('Production solve is active; research remains paused.')
    env=os.environ.copy();env['RAYON_NUM_THREADS']='4'
    env['PATH']=str(c.s.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
    skipped=[]
    for panel in PANELS:
        output=OUT/(panel+'-result.json')
        if output.exists() and json.loads(output.read_text())['records'][-1]['iteration']==2000:
            continue
        if not idle():raise SystemExit('Production solve started; remaining research paused.')
        # Conservative preflight, including CUDA overhead. Keep the app's
        # resident allocation, even when its solve is idle.
        required_gb=20.5 if panel=='panel-ab' else 10.5 if panel in ['panel-a','panel-b','old-two-orbits-two-sizes'] else 4.5
        free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip().splitlines()[0])*1024**2
        if free<required_gb*1e9:
            print(f'{panel}: skipped; needs {required_gb:.1f} GB free research budget, has {free/1e9:.1f} GB.',flush=True)
            skipped.append(panel);continue
        archive_partial(output)
        args=[str(c.EXE),str(c.s.OUT.parent/'conditional-hu-20260919/subtree.json'),str(OUT/(panel+'.json')),str(output),'2000']
        with (OUT/(panel+'-run.log')).open('a',encoding='utf8') as log:
            child=subprocess.Popen(args,cwd=c.s.ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
            try:
                while child.poll() is None:
                    time.sleep(2)
                    if not idle():
                        child.terminate();child.wait(timeout=15);archive_partial(output)
                        raise SystemExit('Production solve started; stopped only the research child and preserved its checkpoint.')
                if child.returncode:raise RuntimeError(f'{panel} exited {child.returncode}; see its log.')
            finally:
                if child.poll() is None:child.terminate();child.wait(timeout=15)
        print(f'{panel}: completed 2,000 iterations.',flush=True)
    if skipped:raise SystemExit('Memory-limited panels remain: '+', '.join(skipped))
    print('All registered development runs completed. Run the independent audits before interpreting results.')

if __name__=='__main__':run()
