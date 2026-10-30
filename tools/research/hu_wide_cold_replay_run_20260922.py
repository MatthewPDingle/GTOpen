"""One guarded full-support cold recovery control, with sequential GPU residency."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from hu_context_audit_20260922 import ROOT, OUT, audit, sha
from loopback_research_validation import idle


def main():
    label = 'hu-wide-cold-replay-v1'
    evidence = ROOT/'research/preflop-evolution/representative-coverage-20260919'
    destination = Path('S:/GTOpen-research/hu-wide-cold-replay-v1')
    exe = ROOT/'target/release/examples/hu_context_wide_cold_replay.exe'
    context = OUT/'bb-context-candidate.json'
    plan_path = OUT/'capacity-texture-result.json'
    registration = OUT/'wide-cold-replay-v1-registration.json'
    assert not registration.exists() and not destination.exists(), 'preserve prior attempt'
    audit(json.loads(context.read_text()))
    plan = json.loads(plan_path.read_text())
    row = next(r for r in plan['rows'] if r['board'] == 'KsQd9d' and r['preflop_leaf'] == 2)
    single_gpu = row['retained_gpu_payload_bytes'] + sum(row['workspace_components_bytes'])
    expected_write_bytes = 16*(row['canonical_state_bytes']+72)
    assert expected_write_bytes <= 64*2**30
    assert idle(), 'production active; not starting'
    assert psutil.virtual_memory().available > 40*2**30
    assert shutil.disk_usage('S:/').free > 96*2**30
    vram = int(subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True).splitlines()[0])*2**20
    assert single_gpu <= vram-3*2**30, 'single continuation fails VRAM admission'
    assert not (evidence/'running.lock').exists()
    inputs = [p for p in (ROOT/'crates/solver/src').rglob('*') if p.suffix in ('.rs', '.cu')]
    inputs += [exe, context, plan_path, ROOT/'Cargo.toml', ROOT/'Cargo.lock', ROOT/'crates/solver/Cargo.toml',
               ROOT/'crates/solver/examples/hu_context_wide_cold_replay.rs', Path(__file__),
               ROOT/'tools/research/hu_context_audit_20260922.py',
               ROOT/'tools/research/loopback_research_validation.py', ROOT/'tools/research/paged_continuation_validation.py']
    frozen = {str(p.relative_to(ROOT)):sha(p) for p in inputs}
    record = {'inputs':frozen, 'maximum_seconds':900, 'write_cap_bytes':64*2**30,
              'expected_write_bytes':expected_write_bytes, 'single_gpu_payload_bytes':single_gpu,
              'free_gpu_bytes_at_admission':vram, 'expected_passes':8, 'iterations':4,
              'board':'KsQd9d', 'preflop_leaf':2, 'entry_support':[169,96],
              'purpose':'Full-support exact recovery, unchanged postflop action menu; not a strategic solve',
              'created_at_unix':time.time(), 'runner_pid':os.getpid(),
              'runner_created':psutil.Process().create_time(), 'no_automatic_retry':True}
    with registration.open('x') as f:
        json.dump(record, f, indent=2)
    destination.mkdir()
    env = os.environ.copy()
    env['GTO_RESEARCH_MAX_SECONDS'] = '900'
    env['GTO_RESEARCH_PROTOCOL'] = str(registration.relative_to(ROOT))
    command = [sys.executable, str(ROOT/'tools/research/loopback_research_validation.py'), str(exe), label,
               str(context.relative_to(ROOT)), 'KsQd9d', str(destination),
               'crates/solver/examples/hu_context_wide_cold_replay.rs',
               'crates/solver/src/gpu/continuation_storage.rs', 'crates/solver/src/gpu/continuation_disk_state_tests.rs',
               'crates/solver/src/gpu/continuation.rs', 'crates/solver/Cargo.toml']
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
    assert result['passes'] == 8 and result['entry_support'] == [169,96]
    assert result['postflop_tree']['max_raises'] == 1
    for k in ['all_values_bitwise_equal', 'all_checkpoint_bytes_equal',
              'reference_and_candidate_gpu_sequential', 'includes_zero_reach_and_reentry']:
        assert result[k] is True
    assert result['bytes_written'] == expected_write_bytes
    lines = (evidence/(label+'.log')).read_text().splitlines()
    passes = [json.loads(s.split('WIDE_COLD_PASS ',1)[1]) for s in lines if s.startswith('WIDE_COLD_PASS ')]
    assert [(r['step'],r['iteration'],r['player']) for r in passes] == [(2*(t-1)+p,t,p) for t in range(1,5) for p in range(2)]
    assert all(r['passed'] for r in passes)
    snapshots = sorted(destination.glob('*-step-*/entry-0-generation-0.bin'))
    assert len(snapshots) == 16 and sum(p.stat().st_size for p in snapshots) == expected_write_bytes
    hashes = {str(p):sha(p) for p in snapshots}
    for step in range(8):
        assert hashes[str(destination/f'reference-step-{step:02}/entry-0-generation-0.bin')] == hashes[str(destination/f'candidate-step-{step:02}/entry-0-generation-0.bin')]
    review = {'passed':True, 'result':result, 'guard':guard, 'registration_sha256':sha(registration),
              'result_sha256':sha(destination/'result.json'), 'checkpoint_hashes':hashes,
              'source_hashes_verified':len(frozen), 'production_modified':False,
              'full_forest_qualified':False, 'strategic_accuracy_claim':False}
    with (OUT/'wide-cold-replay-v1-review.json').open('x') as f:
        json.dump(review, f, indent=2)
    print(json.dumps({k:v for k,v in review.items() if k != 'checkpoint_hashes'}, indent=2))


if __name__ == '__main__':
    main()
