"""Assess the whole fixed diagnostic cohort; never accept a performance candidate."""
import hashlib, json, math, statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8'))
seal = read(HERE / 'scripts-manifest.json')
authorization = read(HERE / 'authorization.json')
assert authorization['candidate'] == 'D042'
assert authorization['independent_source_review_pass'] is True
assert authorization['independent_script_review_pass'] is True
assert authorization['evidence_sha256'][str(HERE / 'scripts-manifest.json')] == sha(HERE / 'scripts-manifest.json')
for name, digest in seal['script_sha256'].items(): assert sha(HERE / name) == digest, name
for path, digest in seal['reference_sha256'].items(): assert sha(path) == digest, path
for path, digest in authorization['evidence_sha256'].items(): assert sha(path) == digest, path
plan = read(HERE / 'protocol.json')
assert plan['candidate'] == 'D042' and plan['performance_acceptance'] is False
assert not (ROOT / 'gpu-run.lock').exists()
assert read(ROOT / 'runs/D042-execution/complete.json')['order'] == plan['order']
timing = {'build_ms', 'init_ms', 'solve_ms', 'readback_ms', 'full_cycle_ms', 'fingerprint_ms_excluded'}
reference_results = reference_checks = None
runs = {}
all_profiles = []
candidate_ids = [pair['candidate'] for pair in plan['pairs']]
baseline_ids = [pair['baseline'] for pair in plan['pairs']]
accepted_manifest = read(ROOT / 'binaries/E020-postflop_autoresearch.manifest.json')
candidate_manifest = read(ROOT / 'binaries/D042-postflop_autoresearch.manifest.json')
assert sha(ROOT / 'binaries/D042-postflop_autoresearch.exe') == candidate_manifest['binary_sha256']
assert sha(ROOT / 'binaries/E020-postflop_autoresearch.exe') == plan['reference_binary_sha256']
assert sha(ROOT / 'binaries/E020-postflop_autoresearch.manifest.json') == plan['reference_manifest_sha256']
assert candidate_manifest['primary_protocol_sha256'] == sha(HERE / 'protocol.json')
assert candidate_manifest['probe_authorization_sha256'] == sha(HERE / 'authorization.json')

for identity in plan['order']:
    directory = ROOT / 'runs' / identity
    report = read(directory / 'report.json')
    assert report['id'] == identity and report['kind'] == 'diagnostic'
    assert report['status'] == 'measured' and report['returncode'] == 0
    assert report['test_pass_count'] == 1
    instrumented = identity in candidate_ids
    binary_name = 'D042-postflop_autoresearch' if instrumented else 'E020-postflop_autoresearch'
    expected_manifest = candidate_manifest if instrumented else accepted_manifest
    assert report['binary_sha256'] == expected_manifest['binary_sha256']
    assert report['binary_build_manifest']['sha256'] == sha(ROOT / 'binaries' / (binary_name + '.manifest.json'))
    assert report['binary_build_manifest']['data'] == expected_manifest
    assert report['binary_build_manifest']['binary_hash_verified'] is True
    assert report['stdout_sha256'] == sha(directory / 'stdout.log')
    assert report['command'] == [str(ROOT / 'binaries' / (binary_name + '.exe')), 'postflop_complete_cycle', '--nocapture', '--test-threads=1', '--ignored']
    for key, value in {'RAYON_NUM_THREADS': '16', 'POSTFLOP_AUTORESEARCH_FIXTURE': None,
                       'POSTFLOP_AUTORESEARCH_STORAGE': 'compressed', 'POSTFLOP_AUTORESEARCH_PROFILE': '0'}.items():
        assert report['environment'][key] == value
    results, checks, profiles = [], [], []
    fixture = stage = None
    for line in (directory / 'stdout.log').read_text(encoding='utf-8').splitlines():
        if 'AUTORESEARCH_STAGE ' in line:
            record = json.loads(line.split('AUTORESEARCH_STAGE ', 1)[1])
            stage = record['stage']
            if stage == 'fixture_start': fixture = record['fixture_id']
            if stage == 'convergence_check':
                checks.append({key: record[key] for key in ['fixture_id', 'iteration', 'exploit_bits', 'exploit_pct_pot', 'exploit_chips']})
        if 'AUTORESEARCH_RESULT ' in line:
            results.append(json.loads(line.split('AUTORESEARCH_RESULT ', 1)[1]))
        if 'ZERO_UPLOAD_PROFILE ' in line:
            assert stage == 'build_complete' and fixture in plan['expected_fixtures']
            record = json.loads(line.split('ZERO_UPLOAD_PROFILE ', 1)[1])
            assert record['schema_version'] == 1 and record['diagnostic_only'] is True
            assert record['zero'] is True and record['zero_path_executed'] is True
            assert record['extra_cuda_synchronizations'] == 0 and record['predicate_calls'] == 1
            assert set(record['stage_us']) == {'predicate', 'alloc_zeros_host_call', 'existing_stream_wait'}
            assert all(isinstance(v, (int, float)) and math.isfinite(v) and v >= 0 for v in record['stage_us'].values())
            assert record['device_bytes'] == 4 * record['device_elements']
            assert record['q_bytes'] == 2 * record['q_words']
            assert record['scale_bytes'] == 4 * record['scale_words']
            profiles.append({'run_id': identity, 'fixture_id': fixture, **record})
    assert results == report['results']
    assert len(results) == 3 and [v['fixture_id'] for v in results] == plan['expected_fixtures']
    assert len(checks) == plan['expected_convergence_records_per_run'] == 23
    for result in results:
        fixture = result['fixture_id']
        assert result['iteration'] == plan['expected_stops'][fixture] and result['target_met'] is True
        assert result['storage'] == 'compressed'
        assert [c['iteration'] for c in checks if c['fixture_id'] == fixture] == list(range(20, result['iteration'] + 1, 20))
    exact = [{k: v for k, v in result.items() if k not in timing} for result in results]
    if reference_results is None: reference_results, reference_checks = exact, checks
    else: assert exact == reference_results and checks == reference_checks, identity
    if identity in candidate_ids:
        assert len(profiles) == plan['expected_profile_records_per_run'] == 12
        for result in results:
            fixture = result['fixture_id']
            records = [v for v in profiles if v['fixture_id'] == fixture]
            assert [[v['player'], v['which']] for v in records] == plan['profile_order_per_fixture']
            for value in records:
                expected_name = 'regrets' if value['which'] == 0 else 'strategy_sums'
                arena = next(a for a in result['state_fingerprint']['arenas'] if a['player'] == value['player'] and a['arena'] == expected_name)
                assert value['variant'] == arena['kind'] == ('i16' if value['which'] == 0 else 'u16')
                assert value['q_words'] == arena['entries'] and value['scale_words'] == arena['scale_entries']
                assert value['q_bytes'] + value['scale_bytes'] == arena['bytes']
                assert 0 < value['device_elements'] <= value['q_words']
            for player in [0, 1]:
                assert len({v['device_elements'] for v in records if v['player'] == player}) == 1
        all_profiles.extend(profiles)
    else:
        assert identity in baseline_ids and not profiles
    runs[identity] = {'results': results, 'profiles': profiles,
                      'process_wall_ms': report['process_wall_ms'],
                      'report_sha256': sha(directory / 'report.json'), 'stdout_sha256': sha(directory / 'stdout.log')}

fixtures = []
for index, fixture in enumerate(plan['expected_fixtures']):
    base_values = [runs[name]['results'][index]['full_cycle_ms'] for name in baseline_ids]
    prof_values = [runs[name]['results'][index]['full_cycle_ms'] for name in candidate_ids]
    b, p = statistics.median(base_values), statistics.median(prof_values)
    components = []
    for variant in ['i16', 'u16']:
        for stage_name in ['predicate', 'alloc_zeros_host_call', 'existing_stream_wait']:
            values = [sum(v['stage_us'][stage_name] for v in runs[name]['profiles'] if v['fixture_id'] == fixture and v['variant'] == variant) / 1000 for name in candidate_ids]
            components.append({'variant': variant, 'stage': stage_name, 'all_profiled_ms': values,
                               'median_ms': statistics.median(values), 'range_ms': [min(values), max(values)]})
    counts = [{key: v[key] for key in ['player', 'which', 'variant', 'q_words', 'q_bytes', 'scale_words', 'scale_bytes', 'device_elements', 'device_bytes']}
              for v in runs[candidate_ids[0]]['profiles'] if v['fixture_id'] == fixture]
    for name in candidate_ids[1:]:
        assert [{key: v[key] for key in counts[0]} for v in runs[name]['profiles'] if v['fixture_id'] == fixture] == counts
    fixtures.append({'fixture_id': fixture, 'ordinary_full_cycles_ms': base_values, 'instrumented_full_cycles_ms': prof_values,
                     'ordinary_median_ms': b, 'instrumented_median_ms': p, 'median_change_pct': 100 * (p / b - 1),
                     'paired_change_pct': [100 * (q / a - 1) for a, q in zip(base_values, prof_values)],
                     'counts': counts, 'components': components})
baseline_total = sum(f['ordinary_median_ms'] for f in fixtures)
profiled_total = sum(f['instrumented_median_ms'] for f in fixtures)
change = 100 * (profiled_total / baseline_total - 1)
useful = abs(change) <= plan['usefulness_guard']['maximum_percent']
u16_upper = sum(next(c['median_ms'] for c in f['components'] if c['variant'] == 'u16' and c['stage'] == 'predicate') for f in fixtures)
result = {'id': 'D042-zero-proof-diagnostic', 'status': 'pass' if useful else 'inconclusive',
          'scope': 'Diagnostic host spans only; predicate includes scales/snapshot checks. No performance acceptance.',
          'protocol_sha256': sha(HERE / 'protocol.json'), 'all_complete_states_exact': 18, 'convergence_checks_exact': 138,
          'profile_records': len(all_profiles), 'uninstrumented_records': 0, 'fixtures': fixtures, 'raw_profiles': all_profiles,
          'ordinary_sum_fixture_medians_ms': baseline_total, 'instrumented_sum_fixture_medians_ms': profiled_total,
          'observed_outer_change_pct': change, 'absolute_change_limit_pct': 10.0, 'diagnostic_usefulness_guard_pass': useful,
          'U16_predicate_upper_sum_fixture_medians_ms': u16_upper,
          'U16_predicate_upper_fraction_of_ordinary_pct': 100 * u16_upper / baseline_total,
          'possible_2pct_headroom_established': False,
          'upper_bound_exceeds_2pct': u16_upper > baseline_total * .02,
          'interpretation': 'Below2pct does not justify a candidate from measured direct-scan headroom; whole-cycle/cache effects are not bounded by these host spans. Above2pct is not a projected gain or authorization. The10pct outer check does not bound component bias.',
          'candidate_accepted': False, 'deployment_changed': False,
          'native_process_wall_ms_including_teardown': {name: runs[name]['process_wall_ms'] for name in plan['order']},
          'evidence': {name: {'report_sha256': runs[name]['report_sha256'], 'stdout_sha256': runs[name]['stdout_sha256']} for name in plan['order']},
          'binary_manifests': {'ordinary': sha(ROOT / 'binaries/E020-postflop_autoresearch.manifest.json'),
                               'instrumented': sha(ROOT / 'binaries/D042-postflop_autoresearch.manifest.json')}}
destination = ROOT / 'comparisons/D042-zero-proof-diagnostic'
destination.mkdir(exist_ok=False)
(destination / 'report.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({key: result[key] for key in ['status', 'observed_outer_change_pct', 'U16_predicate_upper_sum_fixture_medians_ms', 'upper_bound_exceeds_2pct', 'candidate_accepted']}, indent=2))
