"""Bounded CPU storage screen alongside (not inside) the frozen GPU queue."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
FIXTURES = OUT/'flop-storage-fixtures'
EXE = ROOT/'target/storage-fixture-research/release/examples/continuation_flop_storage_fixture.exe'
SUB = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
LIMIT = 3600


def main():
    started = time.monotonic()
    lock = OUT/'flop-storage.lock'
    with lock.open('x') as f:
        f.write(str(os.getpid()))
    child = None
    error = None
    stages = []
    samples = []
    freeze = {}

    def safe():
        assert time.monotonic()-started < LIMIT, 'One-hour storage-screen deadline'
        assert idle(), 'Production is active or unavailable'
        free = psutil.virtual_memory().available
        disk = shutil.disk_usage(ROOT).free
        assert free > 20_000_000_000, 'Host reserve reached'
        assert disk > 50_000_000_000, 'Disk reserve reached'
        return dict(seconds=time.monotonic()-started, free_host_bytes=free, free_disk_bytes=disk)

    def run(stage, command):
        nonlocal child
        samples.append(safe())
        for path, digest in freeze.items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
        env = os.environ.copy()
        env['RAYON_NUM_THREADS'] = '2'
        with (OUT/(stage+'.log')).open('x') as log:
            child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log,
                                     stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
            print(json.dumps(dict(stage=stage, pid=child.pid)), flush=True)
            while child.poll() is None:
                time.sleep(5)
                samples.append(safe())
                (OUT/'flop-storage-resources.json').write_text(json.dumps(samples, indent=2))
            assert child.returncode == 0, f'{stage} exit {child.returncode}'
            stages.append(dict(stage=stage, exit_code=child.returncode, seconds=time.monotonic()-started))

    try:
        assert not FIXTURES.exists()
        safe()
        files = [EXE, SUB, Path(__file__),
                 ROOT/'crates/solver/examples/continuation_flop_storage_fixture.rs',
                 ROOT/'tools/research/continuation_fast_storage_screen.py',
                 ROOT/'tools/research/continuation_storage_screen.py',
                 ROOT/'tools/research/loopback_research_validation.py',
                 OUT/'FLOP-STORAGE-PROTOCOL.md', OUT/'menu50-75-memory-plan.json',
                 *[ROOT/f'crates/solver/src/{name}.rs' for name in ['cfr','save','store','game','tree']]]
        freeze = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        with (OUT/'flop-storage-freeze.json').open('x') as f:
            json.dump(dict(inputs=freeze, maximum_seconds=LIMIT, threads=2,
                           scope='CPU storage only; no CUDA or live solver writes'), f, indent=2)
        run('flop-storage-generation', [str(EXE), str(SUB), str(FIXTURES)])
        manifest = json.loads((FIXTURES/'fixtures.json').read_text())
        assert manifest['complete'] and len(manifest['rows']) == 6
        run('flop-storage-codecs', [sys.executable, 'tools/research/continuation_fast_storage_screen.py',
                                  str(FIXTURES), str(OUT/'flop-fast-storage-screen.json')])
        assert json.loads((OUT/'flop-fast-storage-screen.json').read_text())['bitwise_roundtrips_passed']
    except Exception as ex:
        error = str(ex)
        raise
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            child.wait(timeout=20)
        result = dict(error=error, passed=error is None, stages=stages, seconds=time.monotonic()-started)
        (OUT/'flop-storage-status.json').write_text(json.dumps(result, indent=2))
        print(json.dumps(result), flush=True)
        lock.unlink()


if __name__ == '__main__':
    main()
