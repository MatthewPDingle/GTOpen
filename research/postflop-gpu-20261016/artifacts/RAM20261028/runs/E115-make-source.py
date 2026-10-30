"""One isolated metadata-row relabeling form, with no CUDA/FP/worklist reordering."""
import ast, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists()
assert all(h.read(ROOT / 'runs/D268-record-layout/report.json')['gates'].values())
assert h.read(ROOT / 'runs/D267b-node-order-model/root-report.json')['status'] == 'pass_full_inverse_CPU_model_replay'
H = ROOT / 'runs/E115-source'
(H / 'baseline').mkdir(parents=True, exist_ok=False)
(H / 'candidate').mkdir()
names = ['arena.rs', 'mod.rs', 'continuation.rs', 'continuation_paging.rs']
texts = {name: (h.REPO / 'crates/solver/src/gpu' / name).read_text(encoding='utf-8') for name in names}
originals = dict(texts)
def replace(name, old, new, count=1):
    assert texts[name].count(old) == count, (name, old[:100], texts[name].count(old))
    texts[name] = texts[name].replace(old, new)

replace('arena.rs', '    node: u32,\n', '    node: u32,\n    device_node: u32,\n', 2)
replace('arena.rs', '                        node: i as u32, host:', '                        node: i as u32, device_node: i as u32, host:', 2)
# Existing local test literals also initialize the new private padding field.
replace('arena.rs', 'ActiveBlock { node: 0,', 'ActiveBlock { node: 0, device_node: 0,') if 'ActiveBlock { node: 0,' in texts['arena.rs'] else None
replace('arena.rs', 'InactiveBlock { node: 1,', 'InactiveBlock { node: 1, device_node: 1,') if 'InactiveBlock { node: 1,' in texts['arena.rs'] else None
replace('arena.rs', 'impl ArenaLayout {\n', '''impl ArenaLayout {
    pub(super) fn is_compact(&self) -> bool { self.compact }

    pub(super) fn set_device_nodes(&mut self, forward: &[u32]) {
        for block in &mut self.active { block.device_node = forward[block.node as usize]; }
        for block in &mut self.inactive { block.device_node = forward[block.node as usize]; }
    }

    pub(super) fn device_node(&self, node: u32) -> Option<u32> {
        if let Ok(i) = self.active.binary_search_by_key(&node, |b| b.node) {
            return Some(self.active[i].device_node);
        }
        self.inactive.binary_search_by_key(&node, |b| b.node).ok()
            .map(|i| self.inactive[i].device_node)
    }

''')
replace('mod.rs', 'mod arena;', 'mod arena;\nmod metadata;')
replace('mod.rs', '    iso_active: bool,', '    iso_active: bool,\n    metadata_ordered: bool,')
replace('mod.rs', '''    pub fn new_with_budget(solver: &Solver, budget_bytes: u64) -> Result<GpuSolver, String> {
''', '''    pub fn new_with_budget(solver: &Solver, budget_bytes: u64) -> Result<GpuSolver, String> {
        Self::new_with_budget_layout(solver, budget_bytes, true)
    }

    // Extra continuation projection arrays retain CPU node indexing.
    fn new_original_layout(solver: &Solver, budget_bytes: u64) -> Result<GpuSolver, String> {
        Self::new_with_budget_layout(solver, budget_bytes, false)
    }

    fn new_with_budget_layout(solver: &Solver, budget_bytes: u64, allow_order: bool) -> Result<GpuSolver, String> {
''')
replace('mod.rs', '''        let (lock_off, lock_sigma) = build_lock_table(solver);

        let n = plan.num_nodes;''', '''        let (mut lock_off, lock_sigma) = build_lock_table(solver);
        let metadata_ordered = allow_order && metadata::eligible(
            &plan, &arena_layout, h_staging.as_mut_slice(), solver.spot.tree.children.len());
        let d_children = if metadata_ordered {
            metadata::prepare(&mut plan, &mut arena_layout, &mut lock_off, h_staging.as_mut_slice());
            let children = metadata::children_image(
                &solver.spot.tree.children, &plan.reach_src[0], h_staging.as_mut_slice());
            let device = stream.clone_htod(children).map_err(e)?;
            // The pinned scratch is reused below and for all later readback.
            stream.synchronize().map_err(e)?;
            device
        } else {
            stream.clone_htod(&solver.spot.tree.children).map_err(e)?
        };

        let n = plan.num_nodes;''')
replace('mod.rs', '            iso_active: plan.iso_active,', '            iso_active: plan.iso_active,\n            metadata_ordered,')
replace('mod.rs', '            d_children: up32(&solver.spot.tree.children)?,', '            d_children,')
replace('mod.rs', '''        let (lock_off, lock_sigma) = build_lock_table(solver);
        self.d_lock_off =''', '''        let mut nonaction_plan = None;
        let (lock_off, lock_sigma) = build_lock_table_mapped(solver, |node| {
            if !self.metadata_ordered { return node; }
            if let Some(device) = self.arena_layout[0].device_node(node)
                .or_else(|| self.arena_layout[1].device_node(node)) { return device; }
            // Public lock APIs accept action nodes only. Preserve even manual
            // library nonaction entries without retaining a full mapping.
            let plan = nonaction_plan.get_or_insert_with(|| {
                let mut plan = GpuPlan::build(&solver.spot, self.iso_active);
                metadata::build_map(&mut plan);
                plan
            });
            plan.reach_src[0][node as usize]
        });
        self.d_lock_off =''')
replace('mod.rs', '''fn build_lock_table(solver: &Solver) -> (Vec<i64>, Vec<f32>) {
    let n''', '''fn build_lock_table(solver: &Solver) -> (Vec<i64>, Vec<f32>) {
    build_lock_table_mapped(solver, |node| node)
}

fn build_lock_table_mapped(solver: &Solver, mut node: impl FnMut(u32) -> u32) -> (Vec<i64>, Vec<f32>) {
    let n''')
replace('mod.rs', '        off[node_idx as usize] = sigma.len() as i64;', '        off[node(node_idx) as usize] = sigma.len() as i64;')
replace('continuation.rs', 'GpuSolver::new_with_budget(host,budget.checked_sub(metadata_bytes)', 'GpuSolver::new_original_layout(host,budget.checked_sub(metadata_bytes)')
replace('continuation_paging.rs', '        let mut gpu = GpuSolver::new(host)?;', '        let mut gpu = GpuSolver::new_original_layout(host, u64::MAX)?;')

texts['metadata.rs'] = '''//! Private GPU metadata row projection; CPU tree and physical arenas stay fixed.
use super::{arena::ArenaLayout, plan::GpuPlan};

pub(super) fn eligible(plan: &GpuPlan, layouts: &[ArenaLayout; 2], scratch: &mut [f32], children: usize) -> bool {
    let Some(node_bytes) = plan.num_nodes.checked_mul(8) else { return false; };
    let Some(child_bytes) = children.checked_mul(4) else { return false; };
    let Some(scratch_bytes) = scratch.len().checked_mul(4) else { return false; };
    layouts.iter().all(ArenaLayout::is_compact)
        && plan.reach_src.iter().all(|v| v.len() == plan.num_nodes)
        && node_bytes.max(child_bytes) <= scratch_bytes
        && (scratch.as_mut_ptr() as usize) % 8 == 0
}

// These CPU-only reach-owner vectors are dead after the original plan builder
// creates dense reach_slot. Reuse them as constructor-local forward/inverse maps.
pub(super) fn build_map(plan: &mut GpuPlan) {
    let [forward, inverse] = &mut plan.reach_src;
    forward.fill(u32::MAX);
    let mut next = 0;
    for level in 0..plan.num_levels {
        for (nodes, spans) in [(&plan.action_nodes, &plan.action_spans),
            (&plan.chance_nodes, &plan.chance_node_spans),
            (&plan.fold_nodes, &plan.fold_spans), (&plan.show_nodes, &plan.show_spans)] {
            let span = spans[level];
            for &old in &nodes[span.start as usize..(span.start + span.count) as usize] {
                assert_eq!(forward[old as usize], u32::MAX);
                forward[old as usize] = next as u32;
                inverse[next] = old;
                next += 1;
            }
        }
    }
    for old in 0..plan.num_nodes {
        if forward[old] == u32::MAX {
            forward[old] = next as u32;
            inverse[next] = old as u32;
            next += 1;
        }
    }
    assert_eq!(next, plan.num_nodes);
    assert_eq!(forward[0], 0);
}

// Private calls use only u32/i32/u64/i64/f32, each admitting all bit patterns.
// Scratch is disjoint pinned memory with checked length and 8-byte alignment.
fn rows<T: Copy>(values: &mut [T], inverse: &[u32], scratch: &mut [f32]) {
    assert_eq!(values.len(), inverse.len());
    assert!(values.len().checked_mul(std::mem::size_of::<T>()).unwrap() <= scratch.len() * 4);
    assert_eq!((scratch.as_mut_ptr() as usize) % std::mem::align_of::<T>(), 0);
    unsafe {
        let ptr = scratch.as_mut_ptr().cast::<T>();
        for (new, &old) in inverse.iter().enumerate() {
            ptr.add(new).write(values[old as usize]);
        }
        std::ptr::copy_nonoverlapping(ptr, values.as_mut_ptr(), values.len());
    }
}

pub(super) fn prepare(plan: &mut GpuPlan, layouts: &mut [ArenaLayout; 2], lock_off: &mut [i64], scratch: &mut [f32]) {
    build_map(plan);
    let [forward, inverse] = &plan.reach_src;
    for layout in layouts { layout.set_device_nodes(forward); }
    rows(&mut plan.node_player, inverse, scratch);
    rows(&mut plan.node_na, inverse, scratch);
    rows(&mut plan.node_data_off, inverse, scratch);
    rows(&mut plan.node_children_start, inverse, scratch);
    rows(&mut plan.node_twin, inverse, scratch);
    rows(&mut plan.node_tlose, inverse, scratch);
    rows(&mut plan.node_ttie, inverse, scratch);
    rows(&mut plan.node_cdiv, inverse, scratch);
    rows(&mut plan.node_river_slot, inverse, scratch);
    rows(&mut plan.cc_start, inverse, scratch);
    rows(&mut plan.cc_count, inverse, scratch);
    rows(&mut plan.cfv_slot, inverse, scratch);
    rows(&mut plan.reach_slot[0], inverse, scratch);
    rows(&mut plan.reach_slot[1], inverse, scratch);
    rows(lock_off, inverse, scratch);
    for values in [&mut plan.action_nodes, &mut plan.chance_nodes, &mut plan.fold_nodes,
        &mut plan.show_nodes, &mut plan.chance_parents, &mut plan.chance_children, &mut plan.cc_child] {
        for old in values {
            if *old != u32::MAX { *old = forward[*old as usize]; }
        }
    }
}

pub(super) fn children_image<'a>(children: &[u32], forward: &[u32], scratch: &'a mut [f32]) -> &'a [u32] {
    assert!(children.len() <= scratch.len());
    unsafe {
        let ptr = scratch.as_mut_ptr().cast::<u32>();
        for (i, &old) in children.iter().enumerate() {
            ptr.add(i).write(if old == u32::MAX { old } else { forward[old as usize] });
        }
        std::slice::from_raw_parts(ptr, children.len())
    }
}
'''

owned = {}
for name, text in texts.items():
    relative = 'crates/solver/src/gpu/' + name
    base = H / 'baseline' / name
    candidate = H / 'candidate' / name
    if name in originals:
        base.write_bytes((h.REPO / relative).read_bytes())
        assert base.read_bytes() == originals[name].encode('utf-8')
    else:
        assert not (h.REPO / relative).exists()
    assert '\r' not in text
    with candidate.open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)
    owned[relative] = {'base': str(base) if name in originals else None,
                       'base_sha256': h.sha(base) if name in originals else None,
                       'candidate': str(candidate), 'candidate_sha256': h.sha(candidate)}
h.save(H / 'manifest.json', {
    'id': 'E115', 'at': h.now(), 'status': 'OFF_TREE_UNCOMPILED_NOT_ADMITTED',
    'owned': owned, 'generator_sha256': h.sha(__file__),
    'accepted_source_sha256': h.custody(),
    'prerequisite_sha256': {str(p): h.sha(p) for p in [ROOT / 'runs/D266-metadata-order-history/report.json',
                                                    ROOT / 'runs/D267b-node-order-model/root-report.json',
                                                    ROOT / 'runs/D268-record-layout/report.json']},
    'change': 'Same D267 total N-to-N per-level action/chance/fold/show row permutation and inactive numeric tail. All CPU IDs, worklist/CTA order and spans, floating arithmetic, precision, physical reach/CFV/data offsets, lengths, CUDA/PTX/ABI unchanged. Original plan build and arena uploads precede relabeling. Reuse both dead reach_src vectors and original aligned pinned staging. Retain only action device IDs in existing ActiveBlock/InactiveBlock padding and one GpuSolver bool.',
    'selection': 'Fixed before compiling or GPU outcomes: ordinary constructor only, both original ArenaLayouts compact, checked existing staging bytes >= max(8*N,4*children), both dead reach_src lengths N, staging 8-byte aligned. Otherwise original layout. Symmetric projection and paging constructors explicitly request original layout. No tree/size/fixture/timing threshold.',
    'locks': 'Original HashMap/sigma order and dummy preserved. Initial offsets fully row-permuted. Valid future action locks binary-search original sorted active/inactive host records for mapped IDs. Even manual nonaction library entries retain exact mapping through lazy full original GpuPlan rebuild using GPU iso_active, solely on that rare compatibility path; transient CPU/memory costs real and unqualified. No full map retained between calls. Preserve original stream drain and all graph invalidation.',
    'prospective_layout_gate': 'Actual compiled GpuSolver growth <=8 bytes versus original4448, same alignment8; original ActiveBlock32/InactiveBlock40 and ArenaLayout size/alignment unchanged. Added device_node must not grow records. No retained N-map or larger CPU/pinned/GPU array lengths/capacity plan. Type sizes alone do not prove material neutrality.',
    'remaining': 'Actual full-host typecheck/layout, source/caller/inverse/raw metadata proof, capability/fallback/direct compatibility controls, original engine/full canonical CPU/all66device physical state and every lock/save/resume/graph path. Fresh ordinary builds/86 units, fixed3pairs >=1% and strict fixture gate, separately frozen fresh16/broad/material/holdout/fresh-original/app gates unchanged. No source variants or extra samples after genuine resource/numerical/performance failure.',
    'no_candidate_activation_compiler_CUDA_solver_or_timing': True,
})
print(json.dumps({'owned_files': len(owned), 'manifest_sha256': h.sha(H / 'manifest.json'), 'status': 'off_tree_uncompiled'}), flush=True)
