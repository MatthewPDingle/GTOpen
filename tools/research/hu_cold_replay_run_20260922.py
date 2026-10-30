"""Freeze and guard the compact GPU eviction/recovery control, one attempt only."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from hu_context_audit_20260922 import ROOT, OUT, sha
from loopback_research_validation import idle


def main():
    label = 'hu-cold-replay-v1'
    evidence = ROOT/'research/preflop-evolution/representative-coverage-20260919'
    destination = Path('S:/GTOpen-research/hu-cold-replay-v1')
    exe = ROOT/'target/release/examples/hu_context_cold_replay.exe'
    registration = OUT/'cold-replay-v1-registration.json'
    assert not registration.exists() and not destination.exists(), 'preserve previous attempt'
    assert idle(), 'production active; do not launch'
    assert psutil.virtual_memory().available > 30*2**30
    assert shutil.disk_usage('S:/').free > 48*2**30
    assert not (evidence/'running.lock').exists()
    inputs = [p for p in (ROOT/'crates/solver/src').rglob('*') if p.suffix in ('.rs', '.cu')]
    inputs += [exe, ROOT/'Cargo.toml', ROOT/'Cargo.lock', ROOT/'crates/solver/Cargo.toml',
               ROOT/'crates/solver/examples/hu_context_cold_replay.rs', Path(__file__),
               ROOT/'tools/research/loopback_research_validation.py',
               ROOT/'tools/research/paged_continuation_validation.py']
    frozen = {str(p.relative_to(ROOT)): sha(p) for p in inputs}
    record = {'inputs': frozen, 'maximum_seconds':900, 'write_cap_bytes':16*2**30,
              'expected_passes':48, 'iterations':8, 'cases':3,
              'purpose':'Exact cold recovery control; compact ranges are not the strategic study',
              'created_at_unix':time.time(), 'runner_pid':os.getpid(),
              'runner_created':psutil.Process().create_time(), 'no_automatic_retry':True}
    with registration.open('x') as f:
        json.dump(record, f, indent=2)
    destination.mkdir()
    env = os.environ.copy()
    env['GTO_SSD_STUDY_DIR'] = str(destination)
    env['GTO_RESEARCH_MAX_SECONDS'] = '900'
    env['GTO_RESEARCH_PROTOCOL'] = str(registration.relative_to(ROOT))
    command = [sys.executable, str(ROOT/'tools/research/loopback_research_validation.py'), str(exe), label,
               'crates/solver/examples/hu_context_cold_replay.rs', 'crates/solver/src/gpu/continuation_storage.rs',
               'crates/solver/src/gpu/continuation_disk_state_tests.rs', 'crates/solver/src/gpu/continuation.rs',
               'crates/solver/Cargo.toml']
    # Extra arguments are provenance inputs for the guard. The example's only
    # runtime input is its dedicated GTO_SSD_STUDY_DIR.
    run = subprocess.run(command, cwd=ROOT, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
    for suffix in ('.log', '-status.json', '-resources.json', '-freeze.json'):
        source = evidence/(label+suffix)
        if source.exists():
            target = OUT/(label+suffix)
            assert not target.exists()
            shutil.copyfile(source, target)
    assert run.returncode == 0, 'control failed; preserve evidence without retry'
    guard = json.loads((evidence/(label+'-status.json')).read_text())
    assert guard['error'] is None and guard['exit_code'] == 0
    for p, expected in frozen.items():
        assert sha(ROOT/p) == expected, p
    result = json.loads((destination/'result.json').read_text())
    assert result['passes'] == 48
    for k in ['all_values_bitwise_equal', 'all_state_arrays_bitwise_equal',
              'candidate_gpu_dropped_after_every_pass', 'includes_zero_reach_and_reentry']:
        assert result[k] is True
    lines = (evidence/(label+'.log')).read_text().splitlines()
    passes = [json.loads(s.split('COLD_PASS ', 1)[1]) for s in lines if s.startswith('COLD_PASS ')]
    assert [(r['case'], r['iteration'], r['player']) for r in passes] == [(c,t,p) for c in range(3) for t in range(1,9) for p in range(2)]
    assert all(r['passed'] for r in passes)
    snapshots = sorted(destination.glob('case-*/entry-0-generation-0.bin'))
    assert len(snapshots) == 48
    assert sum(p.stat().st_size for p in snapshots) == result['bytes_written']
    review = {'passed':True, 'result':result, 'guard':guard,
              'registration_sha256':sha(registration), 'result_sha256':sha(destination/'result.json'),
              'checkpoint_hashes':{str(p):sha(p) for p in snapshots},
              'source_hashes_verified':len(frozen), 'production_modified':False,
              'full_context_or_forest_qualified':False}
    with (OUT/'cold-replay-v1-review.json').open('x') as f:
        json.dump(review, f, indent=2)
    print(json.dumps({k:v for k,v in review.items() if k != 'checkpoint_hashes'}, indent=2))


if __name__ == '__main__':
    main()
