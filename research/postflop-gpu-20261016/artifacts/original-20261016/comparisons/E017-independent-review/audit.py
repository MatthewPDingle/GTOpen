"""Read-only independent E017 terminal audit; writes new audit artifacts only."""
import csv
import hashlib
import json
import math
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r'S:\GTOpen-research\postflop-gpu-20261016')
OUT = Path(__file__).parent
PAIRS = [('B053', 'E017R1'), ('B054', 'E017R2'), ('B055', 'E017R3')]
ORDER = ['B053', 'E017R1', 'E017R2', 'B054', 'B055', 'E017R3']
FIXTURES = ['rainbow', 'two-tone', 'river']
TIMINGS = {'build_ms', 'init_ms', 'solve_ms', 'readback_ms', 'full_cycle_ms', 'fingerprint_ms_excluded'}
SOURCES = {
    'crates/solver/src/gpu/mod.rs': 'e4ab59bf7371531411c1f6d0f9915afdb64c9d71da4e3ff90bfd206cc182a4f5',
    'crates/solver/src/gpu/plan.rs': 'ae6e9ddf667c5a232e66a83b1fbf6f277b5898f0c257192209674943c080149a',
    'crates/solver/src/gpu/continuation_capacity.rs': 'e97a8e025e4ec4b2900685720756fcbaeb61f38b2cd8274149118eec8bb8bf9f',
}
UNIT_NAMES = [
    'gpu::plan::tests::actor0_down_lists_preserve_order_membership_and_uniform_coordinates',
    'gpu::plan::tests::river_bounds_match_strength_comparisons',
    'gpu::tests::paired_reach_reuse_matches_full_sweeps_across_lifecycle',
    'gpu::tests::uniform_actor_levels_reuse_original_list_across_lifecycle',
    'gpu::tests::paired_reach_reuse_preserves_raw_player1_and_standalone_refresh',
    'gpu::tests::shared_evaluation_matches_independent_sweeps',
    'gpu::tests::tight_f32_budget_preserves_warm_and_queried_inactive_state',
]
CAPACITY = 'gpu::continuation_capacity::tests::optional_down_list_matches_observed_metadata_for_mixed_and_uniform_plans'
checked = {}

def sha(path, expected=None):
    path = Path(path)
    value = hashlib.sha256(path.read_bytes()).hexdigest()
    if expected is not None:
        assert value == expected.lower(), f'hash mismatch: {path}'
    checked[str(path)] = value
    return value

def read(path):
    sha(path)
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def source_map(manifest):
    raw = manifest.get('source_sha256', manifest.get('hashes'))
    assert isinstance(raw, dict) and raw
    return {k.replace('\\', '/'): v.lower() for k, v in raw.items()}

def load_run(identity):
    directory = ROOT / 'runs' / identity
    report = read(directory / 'report.json')
    assert report['id'] == identity and report['status'] == 'measured'
    assert report['returncode'] == 0
    raw_path = directory / 'stdout.log'
    sha(raw_path, report['stdout_sha256'])
    raw = raw_path.read_text(encoding='utf-8-sig')
    sha(report['command'][0], report['binary_sha256'])
    manifest_ref = report['binary_build_manifest']
    sha(manifest_ref['path'], manifest_ref['sha256'])
    manifest = read(manifest_ref['path'])
    assert manifest == manifest_ref['data']
    assert manifest_ref['binary_hash_verified'] is True
    assert manifest['binary_sha256'].lower() == report['binary_sha256'].lower()
    summary = re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;', raw)
    assert len(summary) == 1, identity
    counts = list(map(int, summary[0]))
    assert counts[0] == report['test_pass_count'] and counts[1] == 0
    return report, raw, manifest, counts

def named_ok(raw, name):
    match = re.search(r'^test ' + re.escape(name) + r' \.\.\.(.*?)(?=^test [\w:]|^test result:|\Z)', raw, re.M | re.S)
    assert match and re.search(r'\bok\s*$', match.group(1)), name

def stamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))

def close(a, b):
    assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-9), (a, b)

def gain(b, c):
    return 100 * (b - c) / b

def main():
    comparison = read(ROOT / 'comparisons/E017-three-pair-comparison/report.json')
    design = read(ROOT / 'runs/E017-design/manifest.json')
    assert design['candidate_source_sha256'] == SOURCES
    for path, expected in SOURCES.items():
        sha(ROOT / 'runs/E017-design' / ('candidate-' + Path(path).name), expected)
    for path, expected in design['base_source_sha256'].items():
        sha(ROOT / 'runs/E017-design' / ('base-' + Path(path).name), expected)
    sha(ROOT / 'runs/E017-design/candidate.patch', design['patch_sha256'])
    tests = {}
    for identity, names, expected in [('V017-unit', UNIT_NAMES, [86, 0, 4]), ('V017-capacity', [CAPACITY], [1, 0, 0])]:
        report, raw, manifest, counts = load_run(identity)
        assert counts[:3] == expected
        for name in names:
            named_ok(raw, name)
        hashes = source_map(manifest)
        assert all(hashes[k] == v for k, v in SOURCES.items())
        if identity == 'V017-capacity':
            assert 'preflop-research' in manifest['build_command']
            assert report['command'][1] == CAPACITY
            for path_key, hash_key in [('build_log', 'build_log_sha256'), ('build_stderr', 'build_stderr_sha256')]:
                sha(manifest[path_key], manifest[hash_key])
        tests[identity] = {'counts': {'passed': counts[0], 'failed': counts[1], 'ignored': counts[2], 'measured': counts[3], 'filtered': counts[4]}, 'named_passes': names, 'binary_sha256': report['binary_sha256']}
    reports, raws, sources = {}, {}, {}
    for identity in ORDER:
        report, raw, manifest, counts = load_run(identity)
        assert counts[0] == 1
        assert report['command'][1:] == ['postflop_complete_cycle', '--nocapture', '--test-threads=1', '--ignored']
        parsed = [json.loads(line.split('AUTORESEARCH_RESULT ', 1)[1]) for line in raw.splitlines() if 'AUTORESEARCH_RESULT ' in line]
        assert parsed == report['results'], identity
        assert [v['fixture_id'] for v in parsed] == FIXTURES
        for value in parsed:
            assert value['target_met'] and value['target_pct'] == 0.3
            assert value['check_every'] == 20 and value['max_iterations'] == 400
            assert value['storage'] == 'compressed' and value['runtime_nvrtc_jit_included'] and value['flushed_progress_logging_included']
            assert all(math.isfinite(value[k]) and value[k] > 0 for k in TIMINGS)
        reports[identity], raws[identity], sources[identity] = report, parsed, source_map(manifest)
    reference = reports[ORDER[0]]
    env = reference['environment']
    assert env['RAYON_NUM_THREADS'] == '16' and env['POSTFLOP_AUTORESEARCH_STORAGE'] == 'compressed'
    assert env['POSTFLOP_AUTORESEARCH_FIXTURE'] is None and env['POSTFLOP_AUTORESEARCH_PROFILE'] == '0'
    gpu = lambda r: [row[:4] for row in csv.reader(r['telemetry_before']['gpu']['stdout'].splitlines(), skipinitialspace=True)]
    for identity, report in reports.items():
        assert report['environment'] == env and gpu(report) == gpu(reference)
        assert report['telemetry_before']['gpu']['returncode'] == 0
        for index, actual in enumerate(raws[identity]):
            expected = {k: v for k, v in raws[ORDER[0]][index].items() if k not in TIMINGS}
            assert {k: v for k, v in actual.items() if k not in TIMINGS} == expected, (identity, index)
        hashes = sources[identity]
        for filename in ['bench_spot.json', 'crates/solver/tests/postflop_autoresearch.rs']:
            assert hashes[filename] == reference['provenance']['benchmark_sha256'][filename].lower()
            assert hashes[filename] == report['provenance']['benchmark_sha256'][filename].lower()
    for column, cohort in enumerate(['baseline', 'candidate']):
        ids = [pair[column] for pair in PAIRS]
        assert comparison['cohorts'][cohort]['run_ids'] == ids
        assert len({reports[i]['binary_sha256'] for i in ids}) == 1
        assert all(sources[i] == sources[ids[0]] for i in ids)
        expected = design['base_source_sha256'] if column == 0 else SOURCES
        assert all(sources[i][k] == v for i in ids for k, v in expected.items())
    source_changes = sorted(k for k in set(sources['B053']) | set(sources['E017R1']) if k.startswith('crates/solver/src/') and sources['B053'].get(k) != sources['E017R1'].get(k))
    assert source_changes == sorted(SOURCES), source_changes
    chronological = sorted(ORDER, key=lambda i: stamp(reports[i]['started_at']))
    assert chronological == ORDER
    gaps = []
    for before, after in zip(ORDER, ORDER[1:]):
        gap = (stamp(reports[after]['started_at']) - stamp(reports[before]['finished_at'])).total_seconds()
        assert gap >= 0
        gaps.append({'before': before, 'after': after, 'gap_seconds': gap})
    rows = []
    for index, fixture in enumerate(FIXTURES):
        baseline = [raws[b][index]['full_cycle_ms'] for b, _ in PAIRS]
        candidate = [raws[c][index]['full_cycle_ms'] for _, c in PAIRS]
        bm, cm = statistics.median(baseline), statistics.median(candidate)
        regressions = [-gain(b, c) for b, c in zip(baseline, candidate)]
        median_regression = -gain(bm, cm)
        failed = median_regression > 3 and sum(v > 3 for v in regressions) >= 2
        close(comparison['fixtures'][index]['baseline']['full_cycle_ms']['median_ms'], bm)
        close(comparison['fixtures'][index]['candidate']['full_cycle_ms']['median_ms'], cm)
        rows.append({'fixture_id': fixture, 'baseline_raw_ms': baseline, 'candidate_raw_ms': candidate, 'baseline_median_ms': bm, 'candidate_median_ms': cm, 'gain_pct': gain(bm, cm), 'paired_regression_pct': regressions, 'repetitions_over_3pct': sum(v > 3 for v in regressions), 'guard_failed': failed})
    bsum = sum(r['baseline_median_ms'] for r in rows)
    csum = sum(r['candidate_median_ms'] for r in rows)
    improvement = gain(bsum, csum)
    perf = comparison['performance']
    close(perf['baseline_full_cycle_ms'], bsum)
    close(perf['candidate_full_cycle_ms'], csum)
    close(perf['observed_gain_pct'], improvement)
    assert perf['aggregate_gate_met'] == (improvement >= 2)
    assert perf['fixture_regression_guard']['failed'] == any(r['guard_failed'] for r in rows)
    assert improvement < 2 and comparison['decision'] == 'rejected'
    recovery = read(ROOT / 'runs/E017-primary-id-recovery/protocol.json')
    sha(recovery['failed_original_script'], recovery['failed_original_script_sha256'])
    for identity, expected in recovery['completed_unchanged_inputs'].items():
        sha(ROOT / 'runs' / identity / 'report.json', expected['report_sha256'])
        sha(ROOT / 'runs' / identity / 'stdout.log', expected['stdout_sha256'])
    assert recovery['timing_exclusions'] == [] and recovery['input_or_binary_change'] is False
    assert recovery['pairs'] == [{'baseline': b, 'candidate': c} for b, c in PAIRS]
    assert recovery['remaining_order'] == ORDER[1:]
    assert not (ROOT / 'runs/E017').exists()
    adapter = read(ROOT / 'runs/E017-primary-id-recovery/comparison-adapter.json')
    sha(adapter['patch_source'], adapter['patch_sha256'])
    sha(adapter['patch_alias'], adapter['patch_sha256'])
    assert adapter['patch_sha256'] == design['patch_sha256']
    for path in ['runs/E017-primary-resume.py', 'runs/E017-primary-id-recovery/completed.json', 'comparisons/E017-source-review/review.md', 'comparisons/E017-source-review/manifest.json']:
        sha(ROOT / path)
    result = {'candidate': 'E017', 'audit_verdict': 'PASS_rejection_confirmed', 'created_at': datetime.now(timezone.utc).isoformat(), 'tests': tests, 'raw_fixture_records_checked': 18, 'all_complete_nontiming_records_exact': True, 'excluded_record_keys_are_only_timing': sorted(TIMINGS), 'source_changes': source_changes, 'pairs': PAIRS, 'chronological_run_order': ORDER, 'gaps': gaps, 'fixtures': rows, 'performance': {'baseline_ms': bsum, 'candidate_ms': csum, 'gain_pct': improvement, 'aggregate_gate_met': improvement >= 2, 'fixture_guard_failed': any(r['guard_failed'] for r in rows), 'decision': 'rejected'}, 'operational_notes': ['Dashboard ID collision was documented before candidate launch; no runs/E017 directory exists. Original B053 and both validation inputs remain byte-identical to the recovery protocol.', 'The original and resume scripts preserve binary identities and pair ordering. The first pair has an operational pause, reported in gaps; no measured timing was excluded.', 'Comparison adapter changes only actual-run ID and a byte-identical patch alias. Refusal and dry-run error descriptions are operator records; separate stderr transcripts were not supplied.'], 'limits': ['No independent GPU/build/test execution by reviewer.', 'Runtime exactness here covers primary compressed fixture records and specified library tests, not additional broad save/menu/resume controls.', 'Aggregate below 2 percent is sufficient for rejection. No significance or deployment claim.'], 'checked_artifacts': checked}
    destination = OUT / 'validation.json'
    with destination.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps({'verdict': result['audit_verdict'], 'tests': tests, 'performance': result['performance'], 'fixtures': rows, 'first_pair_gap_seconds': gaps[0]['gap_seconds'], 'checked_artifacts': len(checked), 'validation_sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}, indent=2))

if __name__ == '__main__':
    main()
