"""Registered transfer controls only. No reserved-board training in this queue."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import numpy as np
import continuation_transfer_aggregate as aggregate

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
DEV = ROOT/'research/preflop-evolution/integrated-coverage-20260919'
SUB = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
PAGED = ROOT/'target/release/examples/continuation_transfer.exe'
STREAM = ROOT/'target/release/examples/continuation_transfer_streamed.exe'
PREFIX = 'transfer-v3'


def rel(path):
    return str(Path(path).relative_to(ROOT))


def main():
    lock = OUT/'transfer-controls.lock'
    with lock.open('x') as f:
        f.write(str(os.getpid()))
    try:
        assert not (OUT/'validation-queue.lock').exists()
        files = [Path(__file__), SUB, PAGED, STREAM,
                 ROOT/'crates/solver/Cargo.toml', ROOT/'crates/solver/tests/continuation_policy_json.rs',
                 ROOT/'crates/solver/examples/continuation_transfer.rs',
                 ROOT/'crates/solver/examples/continuation_transfer_streamed.rs',
                 ROOT/'tools/research/continuation_transfer_aggregate.py',
                 ROOT/'tools/research/continuation_transfer_review.py',
                 ROOT/'tools/research/paged_continuation_validation.py',
                 OUT/'TRANSFER-CONTROLS.md', OUT/'STREAMED-TRANSFER-PROTOCOL.md',
                 DEV/'old-two-orbits-result.json', DEV/'old-two-orbits.json', DEV/'orbit-river.json']
        files += [OUT/f'transfer-control-{kind}.json' for kind in ['fold', 'call', 'fourbet', 'jam']]
        frozen = {rel(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        registration = OUT/'transfer-controls-v3-freeze.json'
        assert not registration.exists()
        registration.write_text(json.dumps(dict(inputs=frozen, registered_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())), indent=2))

        def status(step, **extra):
            (OUT/'transfer-controls-status.json').write_text(json.dumps(dict(step=step, **extra), indent=2))
            print(step, flush=True)

        def run(step, *args):
            for path, digest in frozen.items():
                assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
            status(step)
            subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, check=True)

        def worker(exe, label, panel, source, count):
            result = OUT/(label+'-result.json')
            run(label, 'tools/research/paged_continuation_validation.py', rel(exe), label,
                rel(SUB), rel(panel), rel(result), str(count), rel(source))
            return result

        # Nontrivial probabilities must survive decimal JSON import exactly.
        # Test both binaries cheaply before spending time on the flop runs.
        for exe, mode in [(PAGED, 'paged'), (STREAM, 'streamed')]:
            source = DEV/'old-two-orbits-result.json'
            result = worker(exe, f'{PREFIX}-{mode}-import', DEV/'orbit-river.json', source, 100)
            run(f'review-{mode}-import', 'tools/research/continuation_transfer_review.py', rel(result), rel(source), 'import')
        for kind in ['fold', 'call', 'fourbet', 'jam']:
            source = OUT/f'transfer-control-{kind}.json'
            for exe, mode in [(PAGED, 'paged'), (STREAM, 'streamed')]:
                result = worker(exe, f'{PREFIX}-{mode}-{kind}', DEV/'orbit-river.json', source, 100)
                run(f'review-{mode}-{kind}', 'tools/research/continuation_transfer_review.py', rel(result), rel(source), kind)
                if mode == 'streamed':
                    # One-board aggregation must reproduce the worker too.
                    combined = OUT/f'{PREFIX}-aggregate-{kind}-result.json'
                    run(f'aggregate-{kind}', 'tools/research/continuation_transfer_aggregate.py', rel(SUB), rel(DEV/'orbit-river.json'), rel(source), rel(combined), rel(result))
                    a = aggregate.read(result)['records'][-1]['evaluation']
                    b = aggregate.read(combined)['records'][-1]['evaluation']
                    for field in ['ev', 'gaps', 'postflop_gaps', 'root_frequencies']:
                        assert np.max(abs(np.array(a[field])-b[field])) < 1e-7, (kind, field)
        source = DEV/'old-two-orbits-result.json'
        paged = worker(PAGED, f'{PREFIX}-paged-two', DEV/'old-two-orbits.json', source, 2000)
        run('review-paged-two', 'tools/research/continuation_transfer_review.py', rel(paged), rel(source), 'development-two')
        manifest = aggregate.read(DEV/'old-two-orbits.json')
        results = []
        for index, board in enumerate(manifest['boards']):
            panel = OUT/f'{PREFIX}-development-board-{index}.json'
            assert not panel.exists()
            panel.write_text(json.dumps({**manifest, 'boards': [board]}, indent=2))
            results.append(worker(STREAM, f'{PREFIX}-streamed-two-{index}', panel, source, 2000))
        combined = OUT/f'{PREFIX}-streamed-two-result.json'
        run('aggregate-two', 'tools/research/continuation_transfer_aggregate.py', rel(SUB), rel(DEV/'old-two-orbits.json'), rel(source), rel(combined), *map(rel, results))
        run('review-streamed-two', 'tools/research/continuation_transfer_review.py', rel(combined), rel(source), 'development-two')
        a = aggregate.read(paged)['records'][-1]['evaluation']
        b = aggregate.read(combined)['records'][-1]['evaluation']
        errors = {field: float(np.max(abs(np.array(a[field])-b[field]))) for field in ['ev', 'gaps', 'postflop_gaps', 'root_frequencies']}
        assert max(errors[k] for k in ['ev', 'gaps', 'postflop_gaps']) < 1e-4
        assert errors['root_frequencies'] < 1e-7
        status('complete-passed', errors=errors)
    except Exception as ex:
        (OUT/'transfer-controls-status.json').write_text(json.dumps(dict(step='failed', error=str(ex)), indent=2))
        raise
    finally:
        lock.unlink()


if __name__ == '__main__':
    main()
