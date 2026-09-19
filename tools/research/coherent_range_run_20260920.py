"""Run the previously compiled coherent-range diagnostic under current guards."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from loopback_research_validation import idle

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'
STUDY = ROOT/'research/preflop-evolution/symmetric-bridge-20260919'
DEADLINE = datetime.fromisoformat('2026-09-20T09:00:00+09:30').timestamp()


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not sys.argv[1:], 'This command executes GPU diagnostics; no arguments accepted'
    assert read(OUT/'overnight-accuracy-status.json')['step'] == 'complete-awaiting-scientific-review'
    if (OUT/'population-supplement-status.json').exists():
        assert read(OUT/'population-supplement-status.json')['step'] == 'complete-awaiting-scientific-review'
    for name in ['running.lock','overnight-accuracy.lock','full-population-supplement.lock']:
        assert not (OUT/name).exists(), name
    assert not (STUDY/'running.lock').exists()
    assert idle() and DEADLINE-time.time() >= 900
    build = read(STUDY/'coherent-build-status.json')
    for path, digest in build['inputs'].items():
        assert sha(ROOT/path) == digest, path
    exe = ROOT/'target/storage-fixture-research/release/deps/continuation_coherent_symmetry-cc5910ba0804f3bc.exe'
    files = [Path(__file__),STUDY/'coherent-build-status.json',
             *[ROOT/p for p in build['inputs']],
             ROOT/'tools/research/loopback_research_validation.py',
             ROOT/'tools/research/paged_continuation_validation.py']
    files += list((ROOT/'crates/solver/src/gpu').rglob('*.rs'))
    files += list((ROOT/'crates/solver/src/gpu').rglob('*.cu'))
    frozen = {str(p.relative_to(ROOT)):sha(p) for p in files}
    with (STUDY/'coherent-runtime-freeze.json').open('x') as f:
        json.dump(dict(inputs=frozen, deadline_adelaide='2026-09-20T09:00:00+09:30',
                       note='Build metadata verifies recorded test, protocol, log and executable. Additional source hashes describe execution-time checkout, not an independently recorded compile-time manifest.'),f,indent=2)
    env = os.environ.copy()
    env['GTO_RESEARCH_PROTOCOL'] = str((STUDY/'COHERENT-RANGE-PROTOCOL.md').relative_to(ROOT))
    env['GTO_RESEARCH_MAX_SECONDS'] = str(min(900, DEADLINE-time.time()))
    result = subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',
                             str(exe),'coherent-range-diagnostic','--nocapture','--test-threads=1'],
                            cwd=ROOT,env=env)
    for path, digest in frozen.items():
        assert sha(ROOT/path) == digest, path
    print(json.dumps(dict(guard_returncode=result.returncode,
                          prior_stress_failure_preserved=True,
                          promotion_allowed=False)),flush=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
