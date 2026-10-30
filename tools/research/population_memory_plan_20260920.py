"""Bounded CPU-only capacity planning; no solver arenas or CUDA allocations."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import psutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
SUB = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
EXE = ROOT/'target/release/examples/continuation_orbit_memory.exe'
PANEL = OUT/'combined-population-164.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    previous = json.loads((OUT/'menu50-75-planning-freeze.json').read_text())
    # Reuse precisely the already inspected planner and its recorded sources.
    inputs = {str(Path(__file__).relative_to(ROOT)): sha(Path(__file__)),
              str(PANEL.relative_to(ROOT)): sha(PANEL)}
    for rel, digest in previous['inputs'].items():
        if rel.endswith(('report-47.json', 'menu50-75-planning.json')):
            continue
        assert sha(ROOT/rel) == digest, rel
        inputs[rel] = digest
    assert len(json.loads(PANEL.read_text())['boards']) == 164
    output = OUT/'population164-memory-plan.json'
    assert not output.exists()
    assert psutil.virtual_memory().available >= 20_000_000_000
    with (OUT/'population164-memory-freeze.json').open('x') as f:
        json.dump(dict(inputs=inputs, mode='CPU-only plans; no solver arenas or CUDA',
                       threads=2, timeout_seconds=300, free_host_reserve_bytes=20_000_000_000,
                       node_cap=2_000_000), f, indent=2)
    env = os.environ.copy()
    env['RAYON_NUM_THREADS'] = '2'
    started = time.monotonic()
    samples = []
    error = None
    with (OUT/'population164-memory-plan.log').open('x') as log:
        child = subprocess.Popen([str(EXE), str(SUB), str(PANEL), str(output)],
                                 cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                 creationflags=subprocess.CREATE_NO_WINDOW)
        proc = psutil.Process(child.pid)
        while child.poll() is None:
            elapsed = time.monotonic()-started
            available = psutil.virtual_memory().available
            try:
                rss = proc.memory_info().rss
            except psutil.NoSuchProcess:
                break
            samples.append(dict(seconds=elapsed, rss_bytes=rss, free_host_bytes=available))
            if elapsed >= 300 or available < 20_000_000_000:
                error = 'timeout' if elapsed >= 300 else 'host reserve'
                child.terminate()
                break
            time.sleep(2)
        code = child.wait()
    for rel, digest in inputs.items():
        assert sha(ROOT/rel) == digest, rel
    status = dict(exit_code=code, error=error, seconds=time.monotonic()-started,
                  sampled_peak_rss_bytes=max((x['rss_bytes'] for x in samples), default=0),
                  samples=samples)
    if code == 0 and error is None:
        data = json.loads(output.read_text())
        assert data['manifest'] == json.loads(PANEL.read_text())
        assert len(data['rows']) == 164*2*2
        full = [x for x in data['rows'] if not x['future_card_orbits']]
        packed = [x for x in data['rows'] if x['future_card_orbits']]
        assert len({(x['board'], x['pot']) for x in full}) == 328
        status['capacity'] = dict(
            full_host_arena_bytes=sum(x['full_arena_bytes'] for x in full),
            future_orbit_packed_arena_bytes=sum(x['packed_arena_bytes'] for x in packed),
            maximum_full_continuation_plan_bytes=max(x['planned_compact_bytes'] for x in full),
            total_physical_host_bytes=psutil.virtual_memory().total,
            note='Arena totals exclude trees, metadata, scratch and the production app; packed host storage is not implemented or qualified.')
    (OUT/'population164-memory-status.json').write_text(json.dumps(status, indent=2))
    print(json.dumps({k:v for k,v in status.items() if k != 'samples'}), flush=True)
    assert code == 0 and error is None


if __name__ == '__main__':
    main()
