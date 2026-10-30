"""Validate published import paths with independent small software fixtures."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

TOOLS = Path(r'T:\Dev\GTOpen\tools\research')
ROOT = Path(__file__).resolve().parent / 'preflop-expected-published-controls-v1'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(job):
    label, name, extra = job
    folder = ROOT / label
    folder.mkdir(exist_ok=False)
    source = TOOLS / name
    argv = [sys.executable, '-B', str(source)] + ([str(folder / 'artifacts')] if extra else [])
    started = time.time()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='')
    with (folder / 'stdout.txt').open('xb') as out, (folder / 'stderr.txt').open('xb') as err:
        process = subprocess.Popen(argv, stdout=out, stderr=err, env=env,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        code = process.wait(timeout=120)
    lines = (folder / 'stdout.txt').read_text(encoding='utf-8').splitlines()
    payload = json.loads(lines[-1]) if lines else None
    result = dict(label=label, argv=argv, child_pid=process.pid, started_unix=started,
                  seconds=time.time()-started, exit_code=code, payload=payload,
                  source_sha256=sha(source), stdout_sha256=sha(folder/'stdout.txt'),
                  stderr_sha256=sha(folder/'stderr.txt'))
    (folder/'invocation.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    if code != 0 or payload is None or payload.get('passed') is not True:
        raise RuntimeError('Published software fixture failed: '+label)
    return result

def main():
    ROOT.mkdir(exist_ok=False)
    jobs = [
        ('native-execution', 'preflop_expected_native_execution_check_v1.py', True),
        ('river-source', 'preflop_expected_river_workers_source_check_v1.py', False),
        ('river-cancellation', 'preflop_expected_river_cancellation_check_v1.py', False),
        ('board-cancellation', 'preflop_expected_board_cancellation_check_v1.py', True),
        ('resource-cancellation', 'preflop_expected_profile_resource_check_v1.py', True),
    ]
    began=time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        results=list(pool.map(run,jobs))
    result=dict(passed=True, scope='Published-path software fixtures; no poker native, training or scientific run',
                started_unix=began, seconds=time.time()-began, checks=results, source_sha256=sha(__file__))
    (ROOT/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,checks=len(results),seconds=result['seconds'],result=str(ROOT/'result.json'))))

if __name__=='__main__': main()
