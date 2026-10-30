import sys, json, statistics, hashlib, shutil, subprocess, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
h.ar.refuse_active(h.ar.live_status())
assert h.read(ROOT / 'runs/E091-initial-decision/decision.json')['decision'] == 'rejected'
H = ROOT / 'runs/D145-readback-review'
H.mkdir(exist_ok=False)
ids = ['B296', 'B297', 'B298']
records = [h.read(ROOT / 'runs' / ident / 'report.json') for ident in ids]
anchor = h.read(h.EPOCH / 'exact-anchor.json')
for ident in ids:
    assert h.exact(ident) == anchor
rows = []
base_score = hypothetical_without_readback = 0.0
for fixture in ['rainbow', 'two-tone', 'river']:
    samples = [next(x for x in report['results'] if x['fixture_id'] == fixture) for report in records]
    medians = {key: statistics.median([x[key] for x in samples]) for key in ['build_ms', 'init_ms', 'solve_ms', 'readback_ms', 'full_cycle_ms']}
    rows.append({'fixture_id': fixture, 'phase_medians_ms': medians, 'raw_phase_samples': [{key: x[key] for key in medians} for x in samples]})
    base_score += medians['full_cycle_ms']
    hypothetical_without_readback += statistics.median([x['full_cycle_ms'] - x['readback_ms'] for x in samples])
archive = Path(r'S:\GTOpen-research\postflop-gpu-20261016')
reference = H / 'reference'
reference.mkdir()
references = [(archive / 'runs/D065-readback-diagnostic/source/base/mod.rs', 'D065-base.rs'), (archive / 'runs/D065-readback-diagnostic/source/candidate/mod.rs', 'D065-instrumented.rs'), (archive / 'runs/D065-readback-diagnostic/source/candidate.patch', 'D065.patch'), (archive / 'runs/D065-readback-diagnostic/source/schema.json', 'D065-schema.json'), (archive / 'runs/E011-zero-design/README.md', 'E011-unimplemented-design.md')]
for source, name in references:
    shutil.copyfile(source, reference / name)
    h.pin(reference / name, h.sha(source))
def method(text, marker):
    start = text.index(marker)
    at = text.index('{', start)
    depth = 0
    for i in range(at, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise AssertionError('unterminated method')
production = (h.REPO / 'crates/solver/src/gpu/mod.rs').read_text(encoding='utf-8')
old_base = (reference / 'D065-base.rs').read_text(encoding='utf-8')
instrumented = (reference / 'D065-instrumented.rs').read_text(encoding='utf-8')
marker = '    pub fn sync_to_cpu('
current_method = method(production, marker)
assert current_method == method(old_base, marker)
instrumented_method = method(instrumented, marker)
start = instrumented.index('// Diagnostic-only host wall timers.')
helper = instrumented[start:instrumented.index('\npub struct GpuSolver', start)]
assert 'LifecycleTrace' not in production
diagnostic = production.replace('\npub struct GpuSolver', '\n' + helper + '\npub struct GpuSolver', 1).replace(current_method, instrumented_method, 1)
assert diagnostic.replace('\n' + helper + '\npub struct GpuSolver', '\npub struct GpuSolver', 1).replace(instrumented_method, current_method, 1) == production
S = ROOT / 'runs/D146-readback-source'
S.mkdir(exist_ok=False)
original_bytes = (h.REPO / 'crates/solver/src/gpu/mod.rs').read_bytes()
newline = '\r\n' if b'\r\n' in original_bytes else '\n'
(S / 'baseline.rs').write_bytes(original_bytes)
(S / 'diagnostic.rs').write_bytes(diagnostic.replace('\n', newline).encode())
review = {'id': 'D145', 'at': h.now(), 'status': 'source_and_retained_measurement_review_only', 'control_ids': ids, 'control_score_ms': base_score, 'sum_independent_readback_medians_ms': sum(row['phase_medians_ms']['readback_ms'] for row in rows), 'phase_observations': rows, 'hypothetical_score_if_each_observed_readback_were_removed_ms': hypothetical_without_readback, 'hypothetical_fixed_other_work_removed_ms': base_score - hypothetical_without_readback, 'scope_of_hypothetical': 'Algebra on each retained full cycle minus its own measured readback, then the same median aggregation. This is not achievable saving, causal speed, isolated transfer time or proof that other work stays fixed.', 'new_RAM_five_run_baseline_unchanged_ms': 10456.4109, 'historical_measurements_scored': 0, 'source_identity_matches_D065_sync_to_cpu': True, 'duplicate_lead_declined': 'Pointer no-alias hints overlap the closed E003 mechanism (historical0.6185% under its original2% gate); no source or compiler variation created. This decline does not regrade or resample it.', 'E011_status': 'Original direct inactive-zero restoration is an unimplemented design, not a passed or failed timed candidate. Not activated or admitted here. Fresh substage evidence would be needed before considering it under the current1% rule.', 'next_action': 'Prepare and freeze a diagnostic-only fresh readback breakdown using the exact retained14-span host timer helper on accepted E080. Preserve all work/copies/waits and exact solve records; matched observer controls must bound overhead. No optimization is chosen from stage medians alone.', 'native_or_compiler_children_started': 0}
h.save(H / 'report.json', review)
h.save(S / 'source-review.json', {'at': h.now(), 'kind': 'diagnostic_only_not_performance_candidate', 'baseline_sync_method_exactly_D065': True, 'helper_and_instrumented_sync_method_exactly_D065': True, 'source_reversal_exact': True, 'scope': 'Only retained LifecycleTrace and14 ordered host-wall readback spans applied to accepted E080; no new CUDA event, synchronization, work omission, kernel, numerical/quality/layout/save change. No source activation, compilation, measurement or claim of saving. This instrumentation can perturb CPU scheduling/logging and needs a frozen fresh matched usefulness screen.', 'next_stage': 'Freeze build and cohort protocol before any execution.'})
h.save(S / 'manifest.json', {'id': 'D146', 'at': h.now(), 'baseline_sha256': h.sha(S / 'baseline.rs'), 'diagnostic_sha256': h.sha(S / 'diagnostic.rs'), 'reference_sha256': {str(p): h.sha(p) for p in reference.iterdir()}, 'source_review_sha256': h.sha(S / 'source-review.json'), 'production_source_activated': False, 'performance_candidate': False, 'accepted_source_sha256': h.custody()})
pub = []
for folder in [H, S]:
    for p in folder.rglob('*'):
        if not p.is_file():
            continue
        key = folder.name + '/' + p.relative_to(folder).as_posix()
        dst = h.ar.DASHBOARD / 'evidence' / key
        dst.parent.mkdir(parents=True, exist_ok=True)
        assert not dst.exists()
        shutil.copyfile(p, dst)
        with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
            assert response.read() == p.read_bytes()
        pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    s = h.read(h.ar.STATUS)
    assert not any(x['id'] in ['D145', 'D146'] for x in s['experiments'])
    s['experiments'].extend([{'id': 'D145', 'title': 'Readback stage review after E091 rejection', 'kind': 'diagnostic', 'status': 'measured', 'accepted': False, 'correctness': 'source_only', 'stage': 'Retained observation and source review complete', 'reason': 'The latest control readback medians total about0.600s. Substage profiling is needed before selecting a change. Closed alias-hint work remains closed; no optimization or new timing here.', 'measurement_epoch': 'RAM20261028', 'evidence': [{'label': 'Retained phase observations and scope', 'url': 'evidence/D145-readback-review/report.json'}]}, {'id': 'D146', 'title': 'Fresh readback copy and encode observation', 'kind': 'diagnostic', 'status': 'staged', 'accepted': False, 'correctness': 'not_run', 'stage': 'Freeze diagnostic build and matched controls next', 'reason': 'Staged the retained14-span host-wall helper on byte-matched accepted sync_to_cpu. No CUDA/numerical/work changes, source activation, compile or measurements yet. Timings will be diagnostic only.', 'measurement_epoch': 'RAM20261028', 'evidence': [{'label': 'Exact diagnostic scope', 'url': 'evidence/D146-readback-source/source-review.json'}, {'label': 'Staged instrumentation identity', 'url': 'evidence/D146-readback-source/manifest.json'}]}])
    s.update(updated_at=h.now(), active_experiment='D146', stage='Prepare fresh CPU readback observations', activity='E091 was exact but0.513% slower and is rejected. E080 stays live. Next observe CPU encoding/scatter and copy/wait costs with the current RAM settings; no new gain claimed.')
    h.ar.atomic_json(h.ar.STATUS, s)
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
raw = ledger.read_bytes()
assert b'### D145 readback review and D146 observation staging' not in raw
entry = f"""

### D145 readback review and D146 observation staging

E091 remains closed after its complete-solve/fixture failures. No predicate, width, action subset or added-sample rescue. Read-only scout declined no-alias hints as the closed E003 mechanism; no new alias source or compiler work. The E011 inactive-zero design remains unimplemented and unadmitted, with its original insufficient2% stage-bound rationale preserved; no old result is regraded or pooled.

New-RAM E080 controls B296/B297/B298 retain full exact records. Descriptive readback medians total {review['sum_independent_readback_medians_ms']} ms; component medians are not additive wall time. Per-observation algebraic removal of the entire measured readback would change the same aggregate by {review['hypothetical_fixed_other_work_removed_ms']} ms, assuming all other work fixed; this is not achievable saving, device time, causal attribution or a measured optimization. These observations justify fresh substage profiling rather than a new implementation.

Accepted sync_to_cpu is byte-equal after line-ending normalization to the retained D065 baseline method. Stage D146 diagnostic mod.rs SHA {h.sha(S/'diagnostic.rs')} using exactly its LifecycleTrace and instrumented14-span method, with exact source reversal. No CUDA events, extra waits, work omission, arithmetic/quality/layout/persistence or production changes. It measures host-copy calls, existing waits and CPU encode/scatter/restore; none is isolated PCIe latency. Source-only stage, no compiler/native/measurements yet. Next freeze fresh build/cohort, require exact records/checkpoints and matched observer-usefulness bounds before interpreting its clocks. All inputs copied/hash-verified to X; S archive read-only.

All current owned children terminal, GPU/sequence locks absent, accepted/main/live/protected PTX custody passed. One D144 pre-solve adapter compiler failure remains preserved; final native controls/solves succeeded. {len(pub)} new small source/review artifacts HTTP byte-verified. E080 stays live at the five-run current baseline10.4564109s; historical14.7414% gain remains prior-RAM only. No push/adoption; last primaryB298; goal active.
"""
nl = b'\r\n' if b'\r\n' in raw else b'\n'
ledger.write_bytes(raw + entry.encode().replace(b'\n', nl))
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '--only', '-m', 'research: stage current-RAM readback observations after E091', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
h.custody()
h.save(H / 'checkpoint.json', {'at': h.now(), 'research_git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip(), 'current_E080_baseline_ms': 10456.4109, 'E091_status': 'rejected', 'E091_aggregate_gain_pct': -0.5134802765321737, 'next': 'D146 diagnostic protocol preparation; no candidate optimization activated', 'owned_native_and_compiler_children_terminal': True, 'GPU_and_sequence_locks_absent': True, 'source_main_live_PTX_custody_pass': True, 'all_new_artifacts_physical_X': True, 'goal_status': 'active', 'HTTP_verified_artifacts': pub})
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/status.json', timeout=20) as response:
    served = json.load(response)
assert served['active_experiment'] == 'D146' and served['current_hardware_baseline']['aggregate_ms'] == 10456.4109
print(json.dumps({'review': review['status'], 'readback_median_sum_ms': review['sum_independent_readback_medians_ms'], 'D146_source_only': True, 'checkpoint': str(H / 'checkpoint.json')}), flush=True)
