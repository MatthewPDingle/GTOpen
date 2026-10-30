import sys, json, math, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
assert len(sys.argv) == 2
H = ROOT / 'runs/D147-readback-diagnostic'
P = h.read(H / 'protocol.json')
h.pin(H / 'protocol.json', sys.argv[1])
for p, digest in P['input_sha256'].items():
    h.pin(p, digest)
qpath = ROOT / 'comparisons/D147-readback/report.json'
q = h.read(qpath)
assert q['observer_usefulness_pass'] and q['full_scientific_records_exact'] == 18 and q['convergence_checkpoints_exact'] == 138
checks = 0
def req(value, label):
    global checks
    assert value, label
    checks += 1
profiles = {}
geometry = {}
inventory = 0
for record in P['sequence']:
    ident = record['id']
    r = h.read(ROOT / 'runs' / ident / 'report.json')
    log = ROOT / 'runs' / ident / 'stdout.log'
    h.pin(log, r['stdout_sha256'])
    fixture = None
    arenas = []
    for line in log.read_text(encoding='utf-8').splitlines():
        if 'AUTORESEARCH_STAGE ' in line:
            stage = json.loads(line.partition('AUTORESEARCH_STAGE ')[2])
            if stage.get('stage') == 'fixture_start':
                fixture = stage['fixture_id']
        if 'CPU_ARENA_PROFILE ' in line:
            arenas.append((fixture, json.loads(line.partition('CPU_ARENA_PROFILE ')[2])))
    expected = [(f, p, which) for f in ['rainbow', 'two-tone', 'river'] for p in [0, 1] for which in [0, 1]] if record['instrumented'] else []
    req([(f, x['player'], x['which']) for f, x in arenas] == expected, 'twelve ordered CPU arena records')
    if not record['instrumented']:
        continue
    pair_index = [p['instrumented'] for p in P['pairs']].index(ident)
    per_fixture = []
    for f in ['rainbow', 'two-tone', 'river']:
        records = [x for name, x in arenas if name == f]
        req(len(records) == 4, 'four writes per fixture')
        parent = next(x for x in q['fixtures'] if x['fixture_id'] == f)['traces'][pair_index]
        active = inactive = full = 0.0
        for x in records:
            req(x['schema_version'] == 1 and x['diagnostic_only'] is True and x['extra_gpu_operations'] == 0, 'diagnostic only')
            req(x['mode'] in ['full', 'compact_compressed'], 'compressed storage branch')
            wall = x['full_wall_ms_before_logging']
            req(math.isfinite(wall) and wall >= 0, 'finite CPU wall')
            req(all(type(x[k]) is int and x[k] >= 0 for k in ['active_blocks', 'inactive_blocks', 'copy_spans', 'device_f32_elements']), 'actual layout lengths')
            req(x['device_f32_elements'] > 0, 'nonempty device arena')
            key = (f, x['player'], x['which'])
            shape = {k: x[k] for k in ['mode', 'active_blocks', 'inactive_blocks', 'copy_spans', 'device_f32_elements']}
            if key not in geometry:
                geometry[key] = shape
            req(geometry[key] == shape, 'stable layout shape across three processes')
            arena = 'regrets' if x['which'] == 0 else 'strat'
            span = next(s for s in parent['spans'] if s['stage'] == 'encode_scatter_restore_cpu' and s['player'] == x['player'] and s['arena'] == arena)
            req(span['bytes'] == 4 * x['device_f32_elements'], 'actual parent/child byte geometry')
            req(wall <= span['wall_ms'] + 0.001, 'child CPU wall enclosed by parent')
            if x['mode'] == 'full':
                req(x['active_wall_ms'] is x['inactive_wall_ms'] is None, 'unsplit full write')
                req(x['active_blocks'] == x['inactive_blocks'] == x['copy_spans'] == 0, 'full layout does not populate compact descriptors')
                full += wall
            else:
                a, b = x['active_wall_ms'], x['inactive_wall_ms']
                req(all(math.isfinite(v) and v >= 0 for v in [a, b]), 'finite active/inactive clocks')
                req(abs(a + b - wall) <= 0.000001, 'complete split endpoint')
                req(x['active_blocks'] > 0 and x['copy_spans'] > 0, 'compact active descriptors')
                active += a
                inactive += b
            inventory += 1
        per_fixture.append({'fixture_id': f, 'full_write_ms': full, 'compact_active_ms': active, 'compact_inactive_ms': inactive, 'records': records})
    profiles[ident] = per_fixture
req(inventory == 36, 'all thirty-six records')
fixtures = []
for f in ['rainbow', 'two-tone', 'river']:
    rows = [next(x for x in profiles[p['instrumented']] if x['fixture_id'] == f) for p in P['pairs']]
    fixtures.append({'fixture_id': f, 'samples': rows, 'medians_ms': {k: statistics.median([x[k] for x in rows]) for k in ['full_write_ms', 'compact_active_ms', 'compact_inactive_ms']}})
inactive_sums = [sum(x['compact_inactive_ms'] for x in profiles[p['instrumented']]) for p in P['pairs']]
required = q['baseline_aggregate_ms'] * 0.01
optimistic_proxy = max(inactive_sums)
admit = optimistic_proxy >= required
D = ROOT / 'comparisons/D147-arena-substages'
D.mkdir(exist_ok=False)
report = {'id': 'D147-arena-substages', 'at': h.now(), 'status': 'pass_finite_CPU_substage_observation', 'protocol_sha256': sys.argv[1], 'parent_observation_sha256': h.sha(qpath), 'reader_checks': checks, 'CPU_arena_records': inventory, 'fixtures': fixtures, 'per_instrumented_process_inactive_wall_sum_ms': inactive_sums, 'prospective_component_admission_proxy': {'threshold_definition': '1% of the fresh ordinary sum of fixture medians', 'required_ms': required, 'optimistic_observed_proxy_ms': optimistic_proxy, 'proxy_definition': 'Maximum of the three per-process sums of all observed compact inactive-stage wall spans. Removing the entire stage is more than E011 can do; no other work is assumed changed.', 'passes': admit}, 'E011_design_decision': 'may_prepare_exact_component_controls_only' if admit else 'declined_insufficient_observed_component_headroom', 'E011_optimization_source_created': False, 'full_scientific_records_exact': 18, 'convergence_checkpoints_exact': 138, 'performance_gain_claimed': False, 'candidate_accepted': False, 'scope': 'Fixed finite matched observer cohort. CPU wall includes scheduling, memory traffic and original encoder work. Component proxy is an explicitly optimistic admission heuristic, not an achievable saving, rigorous universal bound, statistical significance or causal full-solve speed. No sample exclusion, extension, historical pooling, quality change or adoption. All observed layout branches retained, including full writes; child clocks exclude their final logging while parent clocks include it.'}
h.save(D / 'report.json', report)
h.custody()
print(json.dumps({'status': report['status'], 'checks': checks, 'inactive_ms': inactive_sums, 'required_ms': required, 'E011_decision': report['E011_design_decision'], 'fixture_medians': [{x['fixture_id']: x['medians_ms']} for x in fixtures]}), flush=True)
