"""Once-only independent authentication of conditioning qualification evidence.

This does not sample deals, fit models, execute native code or admit a diagnostic.
"""
import hashlib
import json
import os
from pathlib import Path
import time
import psutil

ROOT = Path('T:/Dev/GTOpen')
OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE = Path('S:/GTOpen-research/stack-context-matched-learning-v1')
NAME = 'stack-context-teacher-conditioning-readback-v1-result.json'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_bytes())


def main():
    target = OUT/NAME
    if target.exists():raise RuntimeError('Readback already recorded; do not replace it')
    result_path = OUT/'stack-context-teacher-conditioning-check-v1-result.json'
    attempt_path = OUT/'stack-context-teacher-conditioning-check-v1-attempt.json'
    result, attempt = read(result_path), read(attempt_path)
    assert not (OUT/'stack-context-teacher-conditioning-check-v1-failure.json').exists()
    assert result['complete'] is True and result['passed'] is True
    assert result['inputs'] == attempt['inputs']
    for name, identity in result['inputs'].items():assert sha(name) == identity, name
    assert result['qualification_only'] is True and result['synthetic_action_values'] is True
    assert result['scientific_samples'] == result['fits'] == result['native_calls'] == 0
    assert result['gpu'] is False and result['production_modified'] is False
    for key in ('actual_fixed64_teacher_available', 'native_integrated_targets_complete',
                'actual_diagnostic_registered', 'actual_diagnostic_complete'):
        assert result[key] is False
    rows = result['actual_cpu_two_model_fixture_records']
    assert len(rows) == 32
    expected = {(d, p, a, w) for d in (20, 60) for p in range(4) for a in range(2) for w in (362, 387)}
    assert {(r['depth'], r['phase'], r['actor'], r['width']) for r in rows} == expected
    assert all(r['hidden_pairs'] == (1225, 1081, 1035, 990)[r['phase']] for r in rows)
    assert max(r['maximum_fixture_policy_error'] for r in rows) < 1e-10
    assert all(r['teacher_state_supported'] is True for r in rows)
    assert result['actual_native_both_player_paths'] == 1980
    native = result['native_history_posterior_records']
    assert len(native) == 2 and all(r['hidden_pairs'] == 990 for r in native)
    assert all(r['maximum_posterior_error'] < 1e-14 and r['exact_opponent_mass']
               and r['exact_own_likelihood'] for r in native)
    assert result['conditional_sampler_restart_checks'] == 32
    assert result['chance_plan_replay_authenticated'] is True
    assert result['retained_draw_multiplicity'] is True
    assert result['global_numpy_torch_rng_preserved'] is True
    assert result['incorrect_double_weighting_error'] > 1e-6
    assert (result['physical_preflop_flops_checked'], result['ordered_flop_runouts_checked'],
            result['turn_runouts_checked']) == (17296, 1980, 44)
    domains = result['future_domains']
    assert len(domains) == 64
    for r in domains:
        assert r['remaining'] == (48, 45, 44, 43)[r['phase']]
        assert r['runouts'] == (34246080, 1980, 44, 1)[r['phase']]
    assert len(result['negative_cases']) == len(set(result['negative_cases'])) == 27
    reg = OUT/'stack-context-matched-learning-v1-registration.json'
    assert sha(reg) == 'ea0665fcb2ae2888a0aca0fd8ee282d06656d013fa41d98e8981cdc3f52c25e3'
    actual = []
    for pid, created, parent, marker in (
        (84788, 1790752536.9318762, 2980, 'stack_context_durable_recovery_entry_v1.py'),
        (94544, 1790753443.077002, 84788, 'stack_context_parallel_continuation_v2.py'),
        (100604, 1790753511.1853917, 94544, 'multiprocessing.spawn'),
        (93416, 1790753512.997676, 94544, 'multiprocessing.spawn'),
        (104568, 1790753514.8583736, 94544, 'multiprocessing.spawn'),
        (81788, 1790753516.7905183, 94544, 'multiprocessing.spawn')):
        p = psutil.Process(pid)
        assert abs(p.create_time()-created) < .01 and p.ppid() == parent
        command = p.cmdline();assert marker in ' '.join(command)
        actual.append(dict(pid=pid, created=p.create_time(), parent=p.ppid(), command=command))
    status_path = OUT/'stack-context-parallel-continuation-v2-status.json'
    status = read(status_path)
    assert time.time()-status_path.stat().st_mtime < 60
    assert status['stage'] == 'parallel-training' and status['pid'] == 94544
    assert not list(OUT.glob('stack-context-parallel-continuation-v2*failure.json'))
    lock = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
    assert lock.read_text().strip() == '94544'
    counts = {arm:read(STORE/arm/'progress.json')['completed_cycles']
              for arm in ('A-baseline', 'A-relative', 'B-baseline', 'B-relative')}
    answer = dict(complete=True, passed=True, unix=time.time(),
        consumed_inputs=result['inputs'], input_count=len(result['inputs']),
        qualification_receipts={str(p):sha(p) for p in (result_path, attempt_path)},
        reader_source_sha256=sha(__file__), registration_sha256=sha(reg),
        observed_processes=actual, live_stage=status['stage'], published_cycles=counts,
        free_ram_bytes=psutil.virtual_memory().available,
        fixture_posteriors=32, original_native_history_paths=1980,
        restart_checks=32, corruption_rejections=27,
        maximum_fixture_policy_error=max(r['maximum_fixture_policy_error'] for r in rows),
        maximum_river_posterior_error=max(r['maximum_posterior_error'] for r in native),
        incorrect_double_weighting_error=result['incorrect_double_weighting_error'],
        qualification_only=True, actual_fixed64_teacher_available=False,
        native_integrated_targets_complete=False, actual_diagnostic_registered=False,
        actual_diagnostic_complete=False, new_scientific_experiment=False,
        scientific_samples=0, native_calls=0, fits=0, gpu=False, production_modified=False)
    with target.open('xb') as stream:
        stream.write(json.dumps(answer, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())
        stream.flush();os.fsync(stream.fileno())
    print(json.dumps({k:answer[k] for k in ('passed','input_count','published_cycles',
        'fixture_posteriors','maximum_fixture_policy_error','incorrect_double_weighting_error')}))


if __name__ == '__main__':main()
