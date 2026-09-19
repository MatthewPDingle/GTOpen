"""Registered broader reference and independent transfer; no production writes."""
from datetime import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil
import integrated_coverage_review as review

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
DEV = ROOT/'research/preflop-evolution/integrated-coverage-20260919'
SUB = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
PROTOCOL = OUT/'OVERNIGHT-RUN-PROTOCOL.md'
DEADLINE = datetime.fromisoformat('2026-09-20T09:00:00+09:30').timestamp()


def read(path):
    return json.loads(path.read_text())


def rel(path):
    return str(Path(path).relative_to(ROOT))


def main():
    lock = OUT/'overnight-accuracy.lock'
    with lock.open('x') as f:
        f.write(str(os.getpid()))
    frozen = {}

    def status(step, **extra):
        payload = dict(step=step, updated_utc=datetime.now().astimezone().isoformat(), pid=os.getpid(), **extra)
        (OUT/'overnight-accuracy-status.json').write_text(json.dumps(payload, indent=2))
        print(json.dumps(payload), flush=True)

    def verify():
        for path, digest in frozen.items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path

    def run(step, args, limit=None):
        verify()
        assert time.time() < DEADLINE, 'Overnight compute deadline reached'
        status(step)
        env = os.environ.copy()
        env['GTO_RESEARCH_PROTOCOL'] = rel(PROTOCOL)
        env['GTO_RESEARCH_MAX_SECONDS'] = str(min(limit or 7200, DEADLINE-time.time()))
        subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, env=env, check=True)

    try:
        files = [Path(__file__), PROTOCOL, SUB,
                 ROOT/'target/release/examples/integrated_continuation_paged.exe',
                 ROOT/'target/release/examples/continuation_transfer_streamed.exe',
                 ROOT/'crates/solver/examples/integrated_continuation_paged.rs',
                 ROOT/'crates/solver/examples/continuation_transfer_streamed.rs',
                 ROOT/'crates/solver/src/gpu/continuation_paging.rs',
                 ROOT/'tools/research/paged_continuation_validation.py',
                 ROOT/'tools/research/continuation_transfer_aggregate.py',
                 ROOT/'tools/research/continuation_transfer_review.py',
                 ROOT/'tools/research/integrated_coverage_review.py',
                 ROOT/'tools/research/continuation_transfer_controls.py',
                 OUT/'report-47.json', OUT/'validation-95.json', OUT/'validation-95-freeze.json',
                 OUT/'VALIDATION95-PROTOCOL.md', OUT/'HOLDOUT-PROTOCOL.md',
                 OUT/'STREAMED-TRANSFER-PROTOCOL.md', OUT/'TRANSFER-CONTROLS.md',
                 DEV/'reserved.json', DEV/'panel-ab-result.json']
        frozen = {rel(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
        initial_freeze = OUT/'overnight-accuracy-freeze.json'
        assert not initial_freeze.exists()
        initial_freeze.write_text(json.dumps(dict(inputs=frozen, deadline_adelaide='2026-09-20T09:00:00+09:30'), indent=2))
        status('waiting-for-transfer-controls')
        started = time.monotonic()
        while (OUT/'transfer-controls.lock').exists():
            assert time.monotonic()-started < 7200, 'Transfer controls exceeded bounded wait'
            owner = psutil.Process(int((OUT/'transfer-controls.lock').read_text()))
            assert 'continuation_transfer_controls.py' in ' '.join(owner.cmdline())
            time.sleep(10)
        assert read(OUT/'transfer-controls-status.json')['step'] == 'complete-passed'
        assert read(OUT/'report47-trial-review.json')['passed'] is True
        for path, digest in read(OUT/'validation-95-freeze.json')['inputs'].items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path

        trained = OUT/'report47-full-result.json'
        run('report47-reference-2000', ['tools/research/paged_continuation_validation.py',
            'target/release/examples/integrated_continuation_paged.exe', 'report47-full', rel(SUB),
            rel(OUT/'report-47.json'), rel(trained), '2000'], 39600)
        reference = read(trained)
        assert reference['records'][-1]['iteration'] == 2000
        audit = review.audit_result(reference)
        gap = reference['records'][-1]['evaluation']['gap_total']
        (OUT/'report47-full-review.json').write_text(json.dumps(dict(accounting=audit, gap=gap,
            converged=gap < .01, seconds=reference['records'][-1]['elapsed_seconds']), indent=2))
        assert gap < .01, 'Reference numerical-convergence gate failed'
        frozen[rel(trained)] = hashlib.sha256(trained.read_bytes()).hexdigest()
        (OUT/'transfer-sources-freeze.json').write_text(json.dumps({p: frozen[p] for p in [rel(trained), rel(DEV/'panel-ab-result.json')]}, indent=2))

        comparisons = []
        for panel_name, panel in [('reserved10', DEV/'reserved.json'), ('validation95', OUT/'validation-95.json')]:
            manifest = read(panel)
            for source_name, source in [('ab', DEV/'panel-ab-result.json'), ('report47', trained)]:
                leaves = []
                for index, board in enumerate(manifest['boards']):
                    label = f'held-{panel_name}-{source_name}-{index:03}'
                    one_board = OUT/(label+'-manifest.json')
                    assert not one_board.exists()
                    one_board.write_text(json.dumps({**manifest, 'boards': [board]}, indent=2))
                    output = OUT/(label+'-result.json')
                    run(label, ['tools/research/paged_continuation_validation.py',
                        'target/release/examples/continuation_transfer_streamed.exe', label,
                        rel(SUB), rel(one_board), rel(output), '2000', rel(source)], 900)
                    data = read(output)
                    assert data['records'][-1]['iteration'] == 2000 and data['terminal_values'] is not None
                    packed = output.with_suffix('.json.gz')
                    assert not packed.exists()
                    raw = output.read_bytes()
                    compressed = gzip.compress(raw, mtime=0)
                    assert gzip.decompress(compressed) == raw
                    packed.write_bytes(compressed)
                    leaves.append(packed)
                combined = OUT/f'held-{panel_name}-{source_name}-result.json'
                run(f'aggregate-{panel_name}-{source_name}', ['tools/research/continuation_transfer_aggregate.py',
                    rel(SUB), rel(panel), rel(source), rel(combined), *map(rel, leaves)])
                run(f'review-{panel_name}-{source_name}', ['tools/research/continuation_transfer_review.py',
                    rel(combined), rel(source), 'heldout'])
                e = read(combined)['records'][-1]['evaluation']
                comparisons.append(dict(panel=panel_name, source=source_name,
                    **{k:e[k] for k in ['ev', 'postflop_gaps', 'postflop_gap_total', 'gaps', 'gap_total', 'root_frequencies']}))
                (OUT/'independent-transfer-summary.json').write_text(json.dumps(comparisons, indent=2))
                assert e['postflop_gap_total'] < .01, 'Heldout postflop residual gate failed; retain as incomplete'
        status('complete-awaiting-scientific-review', comparisons=4)
    except Exception as ex:
        status('stopped-for-review', error=str(ex))
        raise
    finally:
        lock.unlink()


if __name__ == '__main__':
    main()
