import sys, json, math, statistics, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
assert len(sys.argv) == 2
H = ROOT / 'runs/D147-readback-diagnostic'
P = h.read(H / 'protocol.json')
h.pin(H / 'protocol.json', sys.argv[1])
h.custody()
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
done = h.read(H / 'execution/native-complete.json')
assert done['all_native_children_terminal'] and done['protocol_sha256'] == sys.argv[1]
anchor = h.read(h.EPOCH / 'exact-anchor.json')
reports, profiles, pins = {}, {}, {}
checks = 0
def req(value, label):
    global checks
    assert value, label
    checks += 1
last_end = None
geometry = {}
for record in P['sequence']:
    ident = record['id']
    receipt = h.read(H / 'execution' / (ident + '.exit.json'))
    req(receipt['returncode'] == 0 and receipt['error'] is receipt['cleanup'] is None, 'terminal successful child')
    start = datetime.datetime.fromisoformat(receipt['started_at'])
    end = datetime.datetime.fromisoformat(receipt['finished_at'])
    req(start <= end and (last_end is None or last_end <= start), 'serialized native children')
    last_end = end
    wrapper = (H / 'execution' / (ident + '.stdout.log')).read_text(encoding='utf-8')
    env = [json.loads(line.partition('D147_ENV ')[2]) for line in wrapper.splitlines() if 'D147_ENV ' in line]
    req(env == [{'lifecycle_enabled': record['instrumented'], 'RAYON_NUM_THREADS': '16'}], 'actual wrapper environment')
    path = ROOT / 'runs' / ident / 'report.json'
    report = h.read(path)
    req(report['status'] == 'measured' and report['returncode'] == 0 and report['test_pass_count'] == 1, 'native benchmark completed')
    req(h.exact(ident) == anchor, 'all scientific records and checkpoints exact')
    req(report['provenance']['source_sha256'] == P['accepted_source_sha256'], 'accepted checkout source unchanged')
    expected = P['accepted_source_sha256'] | ({'crates/solver/src/gpu/mod.rs': P['instrumented_production_sha256'], 'crates/solver/src/gpu/arena.rs': P['instrumented_arena_sha256']} if record['instrumented'] else {})
    req(report['binary_build_manifest']['data']['source_sha256'] == expected, 'build source identity')
    log = ROOT / 'runs' / ident / 'stdout.log'
    h.pin(log, report['stdout_sha256'])
    pins[str(path)] = h.sha(path)
    pins[str(log)] = h.sha(log)
    current_fixture = None
    traces = []
    for line in log.read_text(encoding='utf-8').splitlines():
        if 'AUTORESEARCH_STAGE ' in line:
            marker = json.loads(line.partition('AUTORESEARCH_STAGE ')[2])
            if marker.get('stage') == 'fixture_start':
                current_fixture = marker['fixture_id']
        if 'LIFECYCLE_PROFILE ' in line:
            traces.append((current_fixture, json.loads(line.partition('LIFECYCLE_PROFILE ')[2])))
    req([fixture for fixture, _ in traces] == (['rainbow', 'two-tone', 'river'] if record['instrumented'] else []), 'exact trace inventory/order')
    parsed = []
    for fixture, trace in traces:
        req(trace['schema_version'] == 1 and trace['phase'] == 'full_readback' and trace['completed'] is True, 'trace identity')
        req(trace['clock'] == 'host_wall' and trace['diagnostic_only'] is True and trace['extra_cuda_synchronizations'] == 0, 'diagnostic timing boundaries')
        spans = trace['spans']
        expected_order = [('initial_stream_wait', None, None)]
        for p in [0, 1]:
            for arena in ['regrets', 'strat']:
                expected_order += [(name, p, arena) for name in ['dtoh_host_call', 'dtoh_stream_wait', 'encode_scatter_restore_cpu']]
        expected_order += [('publish_iteration_and_symmetry_flag_cpu', None, None)]
        req([(x['stage'], x['player'], x['arena']) for x in spans] == expected_order and len(spans) == 14, 'fourteen ordered spans')
        req(all(math.isfinite(x['wall_ms']) and x['wall_ms'] >= 0 for x in spans), 'finite span clocks')
        req(math.isfinite(trace['wall_ms_before_logging']) and sum(x['wall_ms'] for x in spans) <= trace['wall_ms_before_logging'] + 0.001, 'span containment')
        sizes = []
        for index, span in enumerate(spans):
            if index in [0, 13]:
                req(span['bytes'] is None, 'non-arena span bytes')
            else:
                req(type(span['bytes']) is int and span['bytes'] > 0 and span['bytes'] % 4 == 0, 'actual arena byte count')
                sizes.append(span['bytes'])
        req(all(sizes[i] == sizes[i - i % 3] for i in range(12)), 'same arena bytes across copy/wait/encode')
        req(sizes[0] == sizes[3] and sizes[6] == sizes[9], 'regret/strategy arena shapes equal')
        if fixture not in geometry:
            geometry[fixture] = sizes
        req(geometry[fixture] == sizes, 'same actual allocation geometry across instrumented processes')
        result = next(x for x in report['results'] if x['fixture_id'] == fixture)
        req(result['readback_ms'] + 0.001 >= trace['wall_ms_before_logging'], 'outer readback includes all spans')
        totals = {stage: sum(x['wall_ms'] for x in spans if x['stage'] == stage) for stage in ['initial_stream_wait', 'dtoh_host_call', 'dtoh_stream_wait', 'encode_scatter_restore_cpu', 'publish_iteration_and_symmetry_flag_cpu']}
        parsed.append({'fixture_id': fixture, 'span_totals_ms': totals, 'trace_wall_before_logging_ms': trace['wall_ms_before_logging'], 'outer_readback_ms': result['readback_ms'], 'spans': spans})
    reports[ident] = report
    profiles[ident] = parsed
baseline_score = instrumented_score = 0.0
fixtures = []
for fixture in ['rainbow', 'two-tone', 'river']:
    baseline = [next(x for x in reports[pair['baseline']]['results'] if x['fixture_id'] == fixture) for pair in P['pairs']]
    instrumented = [next(x for x in reports[pair['instrumented']]['results'] if x['fixture_id'] == fixture) for pair in P['pairs']]
    trace = [next(x for x in profiles[pair['instrumented']] if x['fixture_id'] == fixture) for pair in P['pairs']]
    b = statistics.median([x['full_cycle_ms'] for x in baseline])
    d = statistics.median([x['full_cycle_ms'] for x in instrumented])
    baseline_score += b
    instrumented_score += d
    fixtures.append({'fixture_id': fixture, 'baseline_full_cycle_ms': [x['full_cycle_ms'] for x in baseline], 'instrumented_full_cycle_ms': [x['full_cycle_ms'] for x in instrumented], 'baseline_full_cycle_median_ms': b, 'instrumented_full_cycle_median_ms': d, 'outer_readback_baseline_ms': [x['readback_ms'] for x in baseline], 'outer_readback_instrumented_ms': [x['readback_ms'] for x in instrumented], 'instrumented_span_medians_ms': {key: statistics.median([x['span_totals_ms'][key] for x in trace]) for key in trace[0]['span_totals_ms']}, 'traces': trace})
perturbation = 100 * (instrumented_score - baseline_score) / baseline_score
useful = abs(perturbation) <= P['usefulness_max_absolute_aggregate_perturbation_pct']
req(sum(len(x) for x in profiles.values()) == 9, 'nine total traces')
D = ROOT / 'comparisons/D147-readback'
D.mkdir(exist_ok=False)
report = {'id': 'D147', 'at': h.now(), 'status': 'pass_scoped_readback_observation' if useful else 'rejected_observer_usefulness', 'protocol_sha256': sys.argv[1], 'reader_checks': checks, 'full_scientific_records_exact': 18, 'convergence_checkpoints_exact': 138, 'traces': 9, 'spans': 126, 'baseline_aggregate_ms': baseline_score, 'instrumented_aggregate_ms': instrumented_score, 'observer_aggregate_perturbation_pct': perturbation, 'observer_usefulness_pass': useful, 'usefulness_limit_pct': 10.0, 'fixtures': fixtures, 'sum_independent_instrumented_cpu_encode_medians_ms': sum(x['instrumented_span_medians_ms']['encode_scatter_restore_cpu'] for x in fixtures), 'sum_independent_instrumented_copy_call_medians_ms': sum(x['instrumented_span_medians_ms']['dtoh_host_call'] for x in fixtures), 'sum_independent_instrumented_copy_wait_medians_ms': sum(x['instrumented_span_medians_ms']['dtoh_stream_wait'] for x in fixtures), 'preserved_reports_and_logs_sha256': pins, 'excluded_samples': [], 'extension_runs': 0, 'historical_samples_scored': 0, 'performance_qualification_samples': 0, 'new_gain_claimed': False, 'current_five_run_baseline_unchanged_ms': 10456.4109, 'candidate_accepted': False, 'scope': 'Finite fixed three-pair observer cohort at current RAM. Ordered host wall spans include CPU scheduling/API overhead; copy-call plus existing waits is not isolated PCIe latency. CPU encode spans include scatter/inactive restoration. Aggregate10% usefulness does not establish unbiased per-component clocks, significance, removable work or speed. Component medians are descriptive and need not sum to median whole wall time. No historical pooling, new baseline or optimization/adoption.'}
h.save(D / 'report.json', report)
h.custody()
print(json.dumps({key: report[key] for key in ['status', 'reader_checks', 'observer_aggregate_perturbation_pct', 'sum_independent_instrumented_cpu_encode_medians_ms', 'sum_independent_instrumented_copy_call_medians_ms', 'sum_independent_instrumented_copy_wait_medians_ms']}), flush=True)
