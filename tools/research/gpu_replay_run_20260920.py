"""Compile and run the single-update GPU replay diagnostic after prior jobs finish."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
STUDY = OUT.parent/'symmetric-bridge-20260919'
DEADLINE = datetime.fromisoformat('2026-09-20T09:00:00+09:30').timestamp()


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not sys.argv[1:]
    q = read(OUT/'paging-candidate-qualification-status.json')
    assert q['step'] in ['complete-passed-research-only', 'correctness-passed-fresh-timing-deferred', 'stopped-for-review']
    parent = read(OUT/'paging-candidate-qualification-freeze.json')
    try:
        assert psutil.Process(parent['pid']).create_time() != parent['process_create_time'], 'Timing parent still alive'
    except psutil.NoSuchProcess:
        pass
    for path in [OUT/'running.lock', STUDY/'running.lock',
                 Path('T:/Dev/GTOpen-paging-research')/OUT.relative_to(ROOT)/'running.lock']:
        assert not path.exists(), path
    assert idle() and DEADLINE-time.time() >= 1200
    assert psutil.virtual_memory().available >= 20_000_000_000
    relative = ['crates/solver/src/gpu/continuation_replay_tests.rs',
                'research/preflop-evolution/symmetric-bridge-20260919/GPU-REPLAY-PROTOCOL.md',
                'crates/solver/src/cfr.rs', 'crates/solver/src/gpu/mod.rs',
                'crates/solver/src/gpu/kernels.cu', 'crates/solver/Cargo.toml', 'Cargo.toml', 'Cargo.lock',
                'tools/research/loopback_research_validation.py', 'tools/research/paged_continuation_validation.py',
                str(Path(__file__).relative_to(ROOT))]
    relative += [str(p.relative_to(ROOT)) for p in (ROOT/'crates/solver/src').rglob('*')
                 if p.is_file() and p.suffix in ['.rs', '.cu']]
    inputs = {p:sha(ROOT/p) for p in relative}
    with (STUDY/'gpu-replay-build-freeze.json').open('x') as f:
        json.dump(dict(inputs=inputs, deadline_adelaide='2026-09-20T09:00:00+09:30',
                       build_timeout_seconds=300, gpu_timeout_seconds=900), f, indent=2)
    def verify():
        for p, digest in inputs.items():
            assert sha(ROOT/p) == digest, p
    env = os.environ.copy()
    env.update(CARGO_BUILD_JOBS='2', RAYON_NUM_THREADS='4', OPENBLAS_NUM_THREADS='1')
    env['PATH'] = str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+';'+env['PATH']
    command = ['cargo', 'test', '--locked', '--release', '-p', 'solver', '--features', 'preflop-research',
               '--lib', '--no-run', '--message-format=json',
               '--target-dir', 'target/storage-fixture-research']
    started = time.monotonic()
    build_error = None
    with (STUDY/'gpu-replay-build.log').open('x') as log:
        child = subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        owned = {child.pid:psutil.Process(child.pid).create_time()}
        while child.poll() is None:
            try:
                for p in psutil.Process(child.pid).children(recursive=True):
                    owned[p.pid] = p.create_time()
            except psutil.NoSuchProcess:
                pass
            if time.monotonic()-started >= 300 or psutil.virtual_memory().available < 20_000_000_000:
                build_error = 'Build time or host-memory reserve exceeded'
                processes = []
                for pid, created in reversed(list(owned.items())):
                    try:
                        p = psutil.Process(pid)
                        if p.create_time() == created:
                            p.terminate()
                            processes.append(p)
                    except psutil.NoSuchProcess:
                        pass
                _, remaining = psutil.wait_procs(processes, timeout=5)
                for p in remaining:
                    try:
                        if p.create_time() == owned[p.pid]:
                            p.kill()
                    except psutil.NoSuchProcess:
                        pass
                break
            time.sleep(1)
        code = child.wait()
    verify()
    build = dict(exit_code=code, error=build_error, seconds=time.monotonic()-started, command=command)
    (STUDY/'gpu-replay-build-status.json').write_text(json.dumps(build, indent=2))
    assert code == 0 and build_error is None, 'Diagnostic compilation failed; preserve output'
    artifacts = []
    for line in (STUDY/'gpu-replay-build.log').read_text().splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get('reason') == 'compiler-artifact' and row.get('target', {}).get('name') == 'solver' and row.get('profile', {}).get('test') is True and row.get('executable'):
            artifacts.append(Path(row['executable']))
    assert len(artifacts) == 1
    exe = artifacts[0]
    assert exe.is_file() and exe.resolve().is_relative_to((ROOT/'target/storage-fixture-research').resolve())
    assert idle() and DEADLINE-time.time() >= 900
    with (STUDY/'gpu-replay-runtime-freeze.json').open('x') as f:
        json.dump(dict(inputs=inputs, executable=str(exe), executable_sha256=sha(exe),
                       build_log_sha256=sha(STUDY/'gpu-replay-build.log')), f, indent=2)
    env['GTO_RESEARCH_PROTOCOL'] = str((STUDY/'GPU-REPLAY-PROTOCOL.md').relative_to(ROOT))
    env['GTO_RESEARCH_MAX_SECONDS'] = str(min(900, DEADLINE-time.time()))
    result = subprocess.run([sys.executable, 'tools/research/loopback_research_validation.py',
                             str(exe), 'gpu-replay-diagnostic', 'gpu::continuation::replay_tests::identical_state_gpu_replay_separates_local_updates_from_trajectory_drift', '--exact', '--nocapture', '--test-threads=1'],
                            cwd=ROOT, env=env)
    verify()
    print(json.dumps(dict(guard_returncode=result.returncode, compact_promotion_allowed=False)), flush=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
