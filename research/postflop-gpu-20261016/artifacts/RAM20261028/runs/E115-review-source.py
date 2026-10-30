"""Root same-agent byte inversion and bounded caller/source review, not GPU proof."""
import ast, difflib, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
H = ROOT / 'runs/E115-source-v2'
M = h.read(H / 'manifest.json')
generator = ROOT / 'runs/E115-make-source-v2.py'
tree = ast.parse(generator.read_text(encoding='utf-8'))
edits = []
for call in sorted((n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'replace'), key=lambda n: n.lineno):
    args = [ast.literal_eval(arg) for arg in call.args]
    assert len(args) in [3, 4]
    edits.append((*args[:3], args[3] if len(args) == 4 else 1))
rows = []
diffs = []
for name, v in M['owned'].items():
    h.pin(v['candidate'], v['candidate_sha256'])
    proposed_bytes = Path(v['candidate']).read_bytes()
    if v['base'] is None:
        assert name.endswith('/metadata.rs') and not (h.REPO / name).exists()
        continue
    h.pin(v['base'], v['base_sha256'])
    h.pin(h.REPO / name, v['base_sha256'])
    original_bytes = Path(v['base']).read_bytes()
    original = original_bytes.decode().replace('\r\n', '\n')
    proposed = proposed_bytes.decode().replace('\r\n', '\n')
    actual = original
    applied = []
    for file, before, after, count in edits:
        if file != Path(name).name:
            continue
        if not actual.count(before):
            assert before == 'ActiveBlock { node: 0,'  # absent original local test literal
            continue
        assert actual.count(before) == count, before
        actual = actual.replace(before, after)
        applied.append((before, after, count))
    assert actual == proposed, name
    inverse = proposed
    for before, after, count in reversed(applied):
        assert inverse.count(after) == count, after
        inverse = inverse.replace(after, before)
    assert inverse == original, name
    if name.endswith('/continuation.rs'):
        before = b'GpuSolver::new_with_budget(host,budget.checked_sub(metadata_bytes)'
        after = b'GpuSolver::new_original_layout(host,budget.checked_sub(metadata_bytes)'
        assert proposed_bytes.replace(after, before) == original_bytes
    else:
        assert inverse.encode() == original_bytes and b'\r' not in proposed_bytes
    diffs.extend(difflib.unified_diff(original.splitlines(True), proposed.splitlines(True), fromfile='baseline/' + name, tofile='candidate/' + name))
    rows.append({'path': name, 'literal_edits_replayed_and_inverted': len(applied),
                 'full_original_byte_reversal': True, 'original_sha256': v['base_sha256'],
                 'candidate_sha256': v['candidate_sha256']})
module = Path(M['owned']['crates/solver/src/gpu/metadata.rs']['candidate']).read_text(encoding='utf-8')
projected_rows = re.findall(r'rows\(&mut plan\.([^,]+), inverse, scratch\);', module)
assert set(projected_rows) == {'node_player', 'node_na', 'node_data_off', 'node_children_start',
    'node_twin', 'node_tlose', 'node_ttie', 'node_cdiv', 'node_river_slot', 'cc_start', 'cc_count',
    'cfv_slot', 'reach_slot[0]', 'reach_slot[1]'} and len(projected_rows) == 14
assert module.count('rows(lock_off, inverse, scratch);') == 1
assert module.count('if *old != u32::MAX') == 1 and module.count('if old == u32::MAX') == 1
host = Path(M['owned']['crates/solver/src/gpu/mod.rs']['candidate']).read_text(encoding='utf-8')
basehost = Path(M['owned']['crates/solver/src/gpu/mod.rs']['base']).read_text(encoding='utf-8')
start = '    fn cfg(blocks: u32, shared: u32) -> LaunchConfig {'
stop = '    /// Re-upload the lock table after `solver.locks` changed.'
assert host.split(start, 1)[1].split(stop, 1)[0] == basehost.split(start, 1)[1].split(stop, 1)[0]
assert host.count('        let mut nonaction_plan = None;') == 1
assert 'GpuPlan::build(&solver.spot, self.iso_active)' in host
assert 'stream.synchronize().map_err(e)?;\n            device' in host
assert all(h.read(ROOT / 'runs/D269-host-layout/report.json')['gates'].values())
with (H / 'source.diff').open('x', encoding='utf-8', newline='\n') as f:
    f.write(''.join(diffs))
h.save(H / 'source-review.json', {
    'id': 'E115-source-review', 'at': h.now(), 'status': 'pass_literal_inverse_and_static_scope_only',
    'manifest_sha256': h.sha(H / 'manifest.json'), 'reviewer_sha256': h.sha(__file__),
    'generator_sha256': h.sha(generator), 'four_existing_sources': rows,
    'only_new_module': M['owned']['crates/solver/src/gpu/metadata.rs'],
    'CUDA_plan_workloads_all_other_accepted_sources_byte_exact': True,
    'all_existing_eager_graph_training_evaluation_continuation_bridge_sync_methods_byte_exact': True,
    '14_per_node_fields_plus_full_lock_offsets': projected_rows,
    'node_value_arrays': ['action_nodes', 'chance_nodes', 'fold_nodes', 'show_nodes', 'chance_parents', 'chance_children', 'cc_child', 'tree.children'],
    'physical_reach_CFV_arena_children_start_values_not_relabelled': True,
    'no_CTA_worklist_span_count_or_within_frontier_order_changes': True,
    'caller_review': {
        'ordinary': 'new/new_with_budget allow fixed capability predicate; both compact/checked aligned preexisting scratch. No fixture/quality/timing threshold.',
        'symmetric': 'Explicit original-layout private constructor protects stabilizer masks/public_orbits/projection/transport arrays indexed by CPU node ID, including tight budgets.',
        'stored': 'StoredContinuationGpu::new constructs SymmetricContinuationGpu::new_explicit_reference, therefore keeps original CPU IDs for pack_nodes/pack_offsets/source checks/copy kernel.',
        'paged': 'Explicit original-layout private constructor; parked F32 upload and seven-buffer workspace unchanged.',
        'capacity': 'All device array lengths and original capacity planners unchanged by inspection, not actual measured capacity or graph proof.',
        'future_action_locks': 'Same sigma order; binary search both actual sorted action active/inactive records. Device ID additions fit record padding and actual wrapper4448/record32,40/ArenaLayout160 all unchanged in D269.',
        'manual_nonaction_locks': 'Lazy original plan/map rebuild instead of retained N-map. Compatibility, transient CPU/memory/latency cost remain unqualified; no no-tradeoff claim.',
    },
    'new_pinned_metadata_upload_fence': 'Explicit stream drain before children scratch can be reused or dropped. Included in future full-cycle initialization and material cost.',
    'source_diff_sha256': h.sha(H / 'source.diff'),
    'same_agent_shared_generator_literal_replay_not_external_or_formal_audit': True,
    'new_compilers_or_native_runs_in_this_review': 0,
    'remaining': 'Actual production metadata helper CPU replay against frozen complete originals, actual selected/fallback paths and all lock/projection callers; original engine/fullcanonical CPU/all66device physical and lifecycle numerical checks; full ordinary builds/units and all frozen complete-solve qualification/material/holdout/cumulative/application gates. Source feasibility only; zero candidate GPU or speed samples.',
})
h.custody()
print('Four original files fully byte-inverted; unchanged CUDA/FP/eager/graph core; actual host type sizes unchanged. GPU and speed proof pending.', flush=True)
