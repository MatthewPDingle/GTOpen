"""Close CPU/source/layout checkpoint, preserving original rejected experiments."""
import json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
S = ROOT / 'runs/E115-source-v2'
paths = {
    'history': ROOT / 'runs/D266-metadata-order-history/report.json',
    'model': ROOT / 'runs/D267b-node-order-model/model-report.json',
    'model_inverse': ROOT / 'runs/D267b-node-order-model/root-report.json',
    'record_layout': ROOT / 'runs/D268-record-layout/report.json',
    'actual_host_layout': ROOT / 'runs/D269-host-layout/report.json',
    'source_manifest': S / 'manifest.json',
    'source_review': S / 'source-review.json',
}
q = {name: h.read(path) for name, path in paths.items()}
assert q['history']['literal_mapping_hits_for_review'] == []
assert q['model_inverse']['projection_words_replayed'] == 114255649
assert len(q['model_inverse']['cases']) == 6 and len(q['model_inverse']['negative_reader_fixtures']) == 18
assert all(x['all_projection_words_exactly_reversed'] for x in q['model_inverse']['cases'])
assert all(q['record_layout']['gates'].values()) and all(q['actual_host_layout']['gates'].values())
assert q['actual_host_layout']['rows']['baseline'] == q['actual_host_layout']['rows']['candidate'] == [4448, 8, 32, 8, 40, 8, 160, 8]
assert q['source_review']['status'] == 'pass_literal_inverse_and_static_scope_only'
for name, v in q['source_manifest']['owned'].items():
    h.pin(v['candidate'], v['candidate_sha256'])
    if v['base']: h.pin(h.REPO / name, v['base_sha256'])
    else: assert not (h.REPO / name).exists()
receipts = []
for folder in ['D267-node-order-model/execution', 'D267b-node-order-model/execution',
               'D268-record-layout/execution', 'D269-host-layout/execution']:
    for p in (ROOT / 'runs' / folder).rglob('*.exit.json'):
        r = h.read(p)
        expected = 1 if folder.startswith('D267-node-order-model/') else 0
        assert r['returncode'] == expected and r.get('error') is None and r.get('cleanup') is None
        receipts.append({'path': str(p), 'sha256': h.sha(p), 'returncode': expected})
assert len(receipts) == 10 and sum(r['returncode'] == 0 for r in receipts) == 9
H = ROOT / 'runs/E115-prerequisite-checkpoint'
H.mkdir(exist_ok=False)
next_step = 'D270: freeze actual production metadata helper CPU replay against all six complete original plan/payload inputs, full inverse-word readers, capability/identity fallback and action-record mapping controls before any GPU solver or speed qualification. Then actual selected/fallback/locks/all projection callers, original full engine/canonical raw physical state and lifecycle controls. All original speed/material/holdout/cumulative/app gates remain.'
h.save(H / 'report.json', {
    'id': 'E115-prerequisite-checkpoint', 'at': h.now(), 'status': 'source_and_CPU_model_and_actual_host_types_pass_only',
    'measurement_epoch': 'RAM20261028',
    'previous_goal_turn_classification': 'Progress: E114 original direct/engine/fullcanonical exactness passed but primary0.39068960395271185% and rainbow slowdown guard rejected it. That exact mechanism remains closed, as do E112 fresh16 and E113 compiled no-op.',
    'history_scope': {k: q['history'][k] for k in ['local_ref_revisions', 'retained_scoped_Rust_files', 'unique_scoped_Rust_hashes']},
    'no_matching_literals_in_bounded_history_not_exhaustive_semantic_novelty_proof': True,
    'declined_or_absent_previous_leads': q['history']['closed_or_absent_leads'],
    'evidence_sha256': {k: h.sha(v) for k, v in paths.items()},
    'CPU_model': {'cases': 6, 'projected_arrays_per_case': 24, 'whole_projection_words_replayed': 114255649,
                  'writer_checks': q['model']['checks'], 'root_checks': q['model_inverse']['checks'],
                  'negative_reader_fixtures': 18, 'raw_bytes': q['model']['raw_bytes'],
                  'includes_original_complete_metadata_and_actual_captured_locks_plus_declared_synthetic_locks': True,
                  'relative_address_footprints_are_not_measured_misses_transactions_time_or_gain': True},
    'source_form': q['source_manifest']['change'],
    'fixed_capability_and_explicit_caller_fallback': q['source_manifest']['selection'],
    'locks_and_cost_limit': q['source_manifest']['locks'],
    'actual_host_sizes': q['actual_host_layout']['rows'],
    'host_layout_result': 'Actual full crate baseline and candidate compile with continuation-transfer-research. Both GpuSolver4448/align8, ActiveBlock32/align8, InactiveBlock40/align8, ArenaLayout160/align8. Only two exact filtered CPU size tests ran; no ordinary unit suite or constructor/GPU coverage claim.',
    'compiler_and_native_scope': {'standalone_record_compilers': 1, 'full_crate_compilers': 2,
                                 'compiler_identity_queries': 1, 'CPU_layout_helpers': 3, 'CPU_model_readers': 2,
                                 'candidate_GpuSolver_constructors_CUDA_APIs_kernels_solves_speed_samples': 0},
    'preserved_pre_science_tool_failures': [
        'D267 helper SyntaxError at import (else8) before reading inputs or creating model output; failed receipt retained. D267b corrected helper additively with same mapping/cases/gates, writer and reader each once.',
        'E115 generator byte assertion found mixed CRLF/LF in original continuation.rs before source manifest/compilation/activation. Partial output and failure record retained; v2 preserves every original newline byte via exact one-call byte replacement. Same optimizer form.',
        'D269 initial command supplied wrong protocol digest; pin rejected before execution directory/source activation/compiler. Correct frozen digest then ran each baseline/candidate compiler and CPU layout helper once. Original protocol/parser preflight revisions retained.',
    ],
    'successful_and_failed_child_receipts': receipts,
    'all_owned_compilers_native_helpers_and_readers_terminal': True,
    'accepted_research_sources_main_live_protected_two_PTX_unchanged': True,
    'live_app_keeps_E080': True, 'candidate_adopted_or_deployed': False,
    'new_qualified_gain_pct': 0, 'no_universal_or_no_tradeoff_claim': True,
    'best_qualified_config': 'E080/GPU/compressed/16workers/defaultaffinity',
    'hardware_epoch_baseline_ms': 10456.4109,
    'last_primary_baseline': 'B359', 'next_unused_baseline': 'B360',
    'historical_or_RAM_reference_timing_samples_scored': 0,
    'genuine_failure_closure_rule': 'No field/helper/width/placement/selection/scope/source/flags/quality/sample rescue after genuine resource/numerical/performance failure. Model/source/type feasibility admits no GPU gain.',
    'next': next_step, 'remaining_original_gates': q['source_manifest']['remaining'],
    'all_new_bulk_X_S_read_only_no_T_access': True,
    'X_free_bytes': shutil.disk_usage(ROOT).free,
    'goal_active': True,
})
sources = list(paths.values()) + [
    ROOT / 'runs/D267-node-order-model/protocol.json', ROOT / 'runs/D267-node-order-model/execution/model.stderr.log',
    ROOT / 'runs/D267-node-order-model/execution/model.exit.json',
    ROOT / 'runs/D267b-node-order-model/protocol.json', ROOT / 'runs/D267b-node-order-model/execution/complete.json',
    ROOT / 'runs/D268-record-layout/protocol.json',
    ROOT / 'runs/D269-host-layout/protocol.json', ROOT / 'runs/D269-host-layout/protocol.v2.json',
    ROOT / 'runs/D269-host-layout/execution/baseline/build-manifest.json',
    ROOT / 'runs/D269-host-layout/execution/baseline/layout.stdout.log',
    ROOT / 'runs/D269-host-layout/execution/candidate/build-manifest.json',
    ROOT / 'runs/D269-host-layout/execution/candidate/layout.stdout.log',
    ROOT / 'runs/E115-source/generation-failure.json', S / 'source.diff', H / 'report.json']
published = []
for p in sources:
    key = p.parent.name + '/' + p.name
    if p.parent.name == 'execution': key = p.parent.parent.name + '/' + p.name
    if p.parent.name in ['baseline', 'candidate'] and p.parent.parent.name == 'execution': key = 'D269-host-layout/' + p.parent.name + '-' + p.name
    dest = h.ar.DASHBOARD / 'evidence' / key
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists(): assert dest.read_bytes() == p.read_bytes()
    else: shutil.copyfile(p, dest)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as z:
        assert z.read() == p.read_bytes()
    published.append({'url': 'evidence/' + key, 'sha256': h.sha(p)})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    s = h.read(h.ar.STATUS)
    e = next(e for e in s['experiments'] if e['id'] == 'E115')
    e.update(updated_at=h.now(), status='running', accepted=False,
             stage='CPU model/source/full-host types pass; actual metadata replay pending',
             correctness='Feasibility only: six inverse models and actual full-host types pass; GPU numerical proof pending',
             reason='All24 CPU model arrays/114255649 words inverse-exact across6 original variants;18 reader negative fixtures pass.5-file isolated form compiles in actual crate; wrapper4448/records32,40/ArenaLayout160 unchanged. Original CUDA/FP/worklist order/physical buffers preserved. Actual production helper replay, selected/fallback/lock lifecycle and every full GPU/complete-solve/material gate remain. Zero candidate GPU/speed samples; E080 remains best qualified/live.')
    e['evidence'] += [
        {'label': 'Actual full crate host type sizes', 'url': 'evidence/D269-host-layout/report.json'},
        {'label': 'Byte inverse and caller review', 'url': 'evidence/E115-source-v2/source-review.json'},
        {'label': 'Reviewed source diff', 'url': 'evidence/E115-source-v2/source.diff'},
        {'label': 'Prerequisites, limits and next gate', 'url': 'evidence/E115-prerequisite-checkpoint/report.json'}]
    s.update(updated_at=h.now(), state='running', goal_status='active', active_experiment='E115',
             stage='Metadata layout: actual production helper replay next',
             activity='E115 CPU model/source/actual full crate types pass; no candidate GPU or speed samples yet. E080/GPU/compressed/16/default affinity remains live; new-RAM baseline10456.4109ms. All original1%/fixture/fresh16/material/holdout/cumulative/application gates retained. All owned jobs terminal; new bulk X, S archive read-only, no T access.')
    h.ar.atomic_json(h.ar.STATUS, s)
with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/status.json', timeout=20) as z:
    assert z.read() == h.ar.STATUS.read_bytes()
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
prefix = ledger.read_bytes()
assert b'\n## E115 metadata rows in original execution order' not in prefix
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
entry = f'''

## E115 metadata rows in original execution order - CPU/source/actual type prerequisites only

Previous goal turn made progress: E114 full exactness passed, then fixed primary0.39068960395271185% and rainbow majority slowdown rejected that mechanism. It remains closed, as do E112 fresh16/E113 compiled no-op. This distinct lead keeps CTA/worklist order, all N rows/inactive tail, original CUDA/FP/ABI/width/precision/physical reach-CFV-action offsets and every payload length. D266 bounded56 local revisions/624 retained scoped Rust files/188 unique hashes finds no matching mapping literals, not exhaustive semantic novelty proof. Old first-card total cache matches closed E084 and is declined; fmax is already emitted, allocator/implicit-wait routes absent. No closed source form composed or rescued.

D267 import SyntaxError occurred before inputs/output; failed receipt retained. D267b same frozen total N-to-N map (existing level/action/chance/fold/show spans, preserve each order, append numeric inactive tail) projects all24 arrays including complete children, actual captured locks and one explicitly synthetic CPU lock fixture. Six full original iso on/off plan variants,113066926 writerchecks and114256513 rootchecks/114255649 32-bit words exactly reversed;18 negative fixtures reject. All500125664 raw bytes retained X. Relative32-byte footprint is descriptive, not misses/transactions/scheduling/speed. No GPU or timing sample.

D268 one standalone Rust record layout compiler/helper confirms added u32 device_node fits existing32/40-byte records at offsets28/36; no field movement/growth, align8. E115 off-tree5-file source form reuses dead plan.reach_src forward/inverse and checked preexisting aligned pinned scratch after original arena uploads. Four existing sources inverse byte-exact; onlynew metadata.rs, original CUDA/plan/core eager/graph/FP/sync methods unchanged. Original continuation.rs mixed newline assertion preserved partial generation; v2 exact single-call byte patch preserves all original newline bytes, same optimizer form/no compiler before repair.

Selection frozen before outcomes: ordinary constructor, both ArenaLayouts compact, checked scratch >=max(8N,4children), original N-length reach_src and8-byte alignment, otherwise original-layout fallback. Symmetric and paging explicitly request original layout; StoredContinuationGpu uses symmetry constructor, protecting CPU-ID masks/orbit/pack/copy bindings. Initial full lock-offset rows permuted. Future valid action locks binary-search mapped IDs in original sorted active/inactive records, unchanged sigma ordering/dummy/drain/graph invalidation. Even manual nonaction entries use lazy full original-plan/map rebuild; that transient memory/CPU latency cost remains real/unqualified, not no-tradeoff proof. Metadata children staging adds an explicit upload fence, included in future full-cycle init.

D269 freezes actual full crate baseline/candidate release/offline/locked continuation-transfer-research compilers, each once, then exact CPU-only type helper each once after full restoration. Initial wrong argv digest pinned out before execution/source/compiler; corrected frozen pin executes original schedule. Actual sizes both [GpuSolver4448/align8,ActiveBlock32/align8,InactiveBlock40/align8,ArenaLayout160/align8], within prospective wrapper<=8 growth and zero record/layout growth (actual all0). All full crate paths typecheck, not ordinary-unit/GPU/numerical coverage. D267,D268,D269 combined9 successful child receipts plus one pre-model helper import failure terminal; no candidate GpuSolver constructor/CUDA API/kernel/solve/performance samples. Same-agent byte/parser/root reviews not external/formal audit.

Next: {next_step} Exact source closes without source/helper/field/selection/scope/flags/quality/sample rescue after genuine resource/numerical/performance failure. New gain0 adopted; E080/GPU/compressed/16/defaultaffinity bestqualified/live, RAM reference10456.4109ms unchanged, lastprimaryB359/nextB360. All owned compilers/native/helpers/readers terminal, locks absent, accepted/main/live/protected2PTX unchanged; allnewbulkX,Sarchive readonly,noT. {len(published)} evidence artifacts/status HTTPbyteverified; checkpoint `{H}`. Ledger prefix byteexact, goal active.
'''
ledger.write_bytes(prefix + entry.encode('utf-8'))
assert ledger.read_bytes()[:len(prefix)] == prefix
h.custody()
subprocess.run(['git', 'add', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
assert subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).splitlines() == ['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '-m', 'research: qualify metadata ordering source and host types'], cwd=h.REPO, check=True)
h.save(H / 'publication.json', {'at': h.now(), 'local_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip(),
                                 'HTTP_byte_verified_artifacts': published, 'report_sha256': h.sha(H / 'report.json'),
                                 'all_owned_children_terminal': True, 'candidate_adopted': False, 'goal_active': True})
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
print(json.dumps({'status': 'metadata_source_CPU_model_actual_types_pass_GPU_pending', 'HTTP_byte_verified_artifacts': len(published), 'next': 'D270 actual production metadata CPU replay', 'candidate_adopted': False, 'goal_active': True}), flush=True)
