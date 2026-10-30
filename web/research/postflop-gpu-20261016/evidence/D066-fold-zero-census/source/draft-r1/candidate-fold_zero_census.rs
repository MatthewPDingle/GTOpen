//! D066: read-only, bounded fold-input incidence diagnostic. No production arithmetic changes.
use super::*;
use crate::{Spot, SpotConfig};
use crate::store::Storage;
use serde_json::{json, Value};
use std::io::{self, Write, BufWriter};
use std::path::Path;

type DiagResult<T> = Result<T, String>;
const CHUNK: usize = 1_048_576;
const GIB: u64 = 1 << 30;

fn emit(value: Value) -> DiagResult<()> {
    let stdout = io::stdout();
    let mut output = stdout.lock();
    writeln!(output, "D066_FOLD_ZERO_CENSUS {value}").map_err(e)?;
    output.flush().map_err(e)
}

fn checked_sum(values: &[u64]) -> DiagResult<u64> {
    values.iter().try_fold(0u64, |a, &b| a.checked_add(b).ok_or("byte-count overflow".into()))
}

fn bytes<T>(values: &[T]) -> DiagResult<u64> {
    (values.len() as u64).checked_mul(std::mem::size_of::<T>() as u64)
        .ok_or("byte-count overflow".into())
}

#[cfg(windows)]
fn available_ram() -> DiagResult<u64> {
    #[repr(C)]
    struct MemoryStatus { length: u32, load: u32, total: u64, available: u64,
        total_page: u64, available_page: u64, total_virtual: u64,
        available_virtual: u64, extended: u64 }
    #[link(name = "kernel32")]
    extern "system" { fn GlobalMemoryStatusEx(status: *mut MemoryStatus) -> i32; }
    let mut status: MemoryStatus = unsafe { std::mem::zeroed() };
    status.length = std::mem::size_of::<MemoryStatus>() as u32;
    if unsafe { GlobalMemoryStatusEx(&mut status) } == 0 {
        return Err(format!("GlobalMemoryStatusEx: {}", io::Error::last_os_error()));
    }
    Ok(status.available)
}

#[cfg(not(windows))]
fn available_ram() -> DiagResult<u64> { Err("D066 admission is registered for Windows only".into()) }

// Count every actual E020 device payload; private admission only, no production changes.
fn planned_device_bytes(spot: &Spot, plan: &GpuPlan) -> DiagResult<u64> {
    let mut sizes = Vec::new();
    macro_rules! push { ($($v:expr),+ $(,)?) => { $(sizes.push(bytes(&$v)?);)+ }; }
    push!(plan.action_nodes, plan.chance_parents, plan.chance_children, plan.chance_cards,
        plan.chance_nodes, plan.fold_nodes, plan.show_nodes, plan.node_player, plan.node_na,
        plan.node_data_off, plan.node_children_start, plan.node_twin, plan.node_tlose,
        plan.node_ttie, plan.node_cdiv, plan.node_river_slot, plan.cc_start, plan.cc_count,
        plan.cc_card, plan.cc_child, plan.cc_perm, plan.cfv_slot, spot.tree.children);
    for p in 0..2 {
        push!(plan.hand_perm_flat[p], plan.reach_slot[p], plan.hand_c1[p], plan.hand_c2[p],
            plan.hand_mask[p], plan.same_combo[p], plan.weights[p], plan.riv_off[p],
            plan.riv_cnt[p], plan.riv_sorted_idx[p], plan.riv_lower[p], plan.riv_upper[p],
            plan.riv_card_off[p], plan.riv_card_pos[p]);
        // Every two-card hand appears in two fold-card lists; 53 offsets per player.
        sizes.push(checked_sum(&[53 * 4, (spot.hands[p].len() as u64).checked_mul(8)
            .ok_or("fold-list overflow")?])?);
        sizes.push((plan.arena_elements[p] as u64).checked_mul(8).ok_or("arena overflow")?);
        sizes.push((plan.reach_blocks[p] as u64).checked_mul(plan.nh[p] as u64)
            .and_then(|x| x.checked_mul(4)).ok_or("reach overflow")?);
    }
    sizes.push((plan.cfv_blocks as u64).checked_mul(plan.nh_max as u64)
        .and_then(|x| x.checked_mul(4)).ok_or("CFV overflow")?);
    sizes.push((plan.num_nodes as u64).checked_mul(8).ok_or("lock overflow")?);
    sizes.extend([4, 12, (plan.nh_max as u64).checked_mul(16).ok_or("eval overflow")?]);
    checked_sum(&sizes)
}


// Drain each ordinary solver before its buffers can drop, including early errors.
struct SolverGuard(GpuSolver);
impl std::ops::Deref for SolverGuard { type Target = GpuSolver; fn deref(&self) -> &GpuSolver { &self.0 } }
impl std::ops::DerefMut for SolverGuard { fn deref_mut(&mut self) -> &mut GpuSolver { &mut self.0 } }
impl Drop for SolverGuard {
    fn drop(&mut self) {
        if let Err(error) = self.0.synchronize() {
            let _ = writeln!(io::stderr().lock(), "D066_SOLVER_CLEANUP_ERROR {error}");
        }
    }
}

#[derive(Clone, Copy)]
struct FoldRow { node: u32, slots: [u32; 2], amount_bits: [u32; 2] }
struct Geometry {
    nh: [usize; 2],
    reach_blocks: [usize; 2],
    spans: Vec<LevelSpan>,
    rows: Vec<FoldRow>,
}

fn verify_metadata(gpu: &GpuSolver, plan: &GpuPlan) -> DiagResult<()> {
    gpu.synchronize()?;
    if gpu.nh != [plan.nh[0] as i32, plan.nh[1] as i32]
        || gpu.fold_spans.len() != plan.fold_spans.len()
        || !gpu.fold_spans.iter().zip(&plan.fold_spans).all(|(a,b)| a.start == b.start && a.count == b.count) {
        return Err("uploaded solver geometry differs from independently finalized plan".into());
    }
    macro_rules! exact {
        ($name:expr, $expected:expr, $actual:expr, $bits:expr) => {{
            let expected = $expected;
            let actual = $actual;
            if expected.len() != actual.len() { return Err(format!("{} metadata length differs", $name)); }
            for offset in (0..actual.len()).step_by(CHUNK) {
                let end = (offset + CHUNK).min(actual.len());
                let values = gpu.stream.clone_dtoh(&actual.slice(offset..end)).map_err(e)?;
                for (i, value) in values.iter().enumerate() {
                    if ($bits)(value) != ($bits)(&expected[offset+i]) {
                        return Err(format!("{} uploaded metadata differs at{}", $name, offset+i));
                    }
                }
            }
        }};
    }
    exact!("fold_nodes", &plan.fold_nodes, &gpu.d_fold_nodes, |x: &u32| *x);
    exact!("node_player", &plan.node_player, &gpu.d_node_player, |x: &i32| *x);
    exact!("node_twin", &plan.node_twin, &gpu.d_node_twin, |x: &f32| x.to_bits());
    exact!("node_tlose", &plan.node_tlose, &gpu.d_node_tlose, |x: &f32| x.to_bits());
    for q in 0..2 {
        exact!("reach_slot", &plan.reach_slot[q], &gpu.d_rsrc[q], |x: &u32| *x);
        if plan.nh[q] == 0 || plan.reach_blocks[q].checked_mul(plan.nh[q]) != Some(gpu.d_reach[q].len()) {
            return Err(format!("reach{q} logical allocation bound differs"));
        }
    }
    Ok(())
}

fn geometry(spot: &Spot, plan: &GpuPlan) -> DiagResult<Geometry> {
    let mut cursor = 0usize;
    for span in &plan.fold_spans {
        if span.start as usize != cursor { return Err("fold spans are not a complete contiguous partition".into()); }
        cursor = cursor.checked_add(span.count as usize).ok_or("fold span overflow")?;
    }
    if cursor != plan.fold_nodes.len() { return Err("fold span coverage differs".into()); }
    let mut rows = Vec::with_capacity(plan.fold_nodes.len());
    for &node in &plan.fold_nodes {
        let n = node as usize;
        if n >= plan.num_nodes || spot.tree.nodes[n].kind != crate::tree::KIND_TERM_FOLD {
            return Err("fold list contains invalid node".into());
        }
        let slots = [plan.reach_slot[0][n], plan.reach_slot[1][n]];
        for q in 0..2 {
            if slots[q] as usize >= plan.reach_blocks[q] { return Err("fold reach slot out of bounds".into()); }
        }
        let amount_bits = std::array::from_fn(|p| {
            (if plan.node_player[n] == p as i32 { plan.node_tlose[n] } else { plan.node_twin[n] }).to_bits()
        });
        rows.push(FoldRow { node, slots, amount_bits });
    }
    Ok(Geometry { nh: plan.nh, reach_blocks: plan.reach_blocks, spans: plan.fold_spans.clone(), rows })
}

fn write_mapping(directory: &Path, fixture: &str, g: &Geometry) -> DiagResult<Value> {
    let name = format!("{fixture}-fold-mapping.u32le");
    let file = std::fs::OpenOptions::new().write(true).create_new(true).open(directory.join(&name)).map_err(e)?;
    let mut out = BufWriter::new(file);
    let mut hash = Fingerprint::new();
    for row in &g.rows {
        for word in [row.node, row.slots[0], row.slots[1], row.amount_bits[0], row.amount_bits[1]] {
            let bytes = word.to_le_bytes();
            out.write_all(&bytes).map_err(e)?;
            hash.bytes(&bytes);
        }
    }
    out.flush().map_err(e)?;
    Ok(json!({"file":name,"bytes":g.rows.len()*20,"fnv1a64":hash.finish(),
        "record":"five little-endian u32: node,slot0,slot1,amount0bits,amount1bits"}))
}

fn fold_counts(g: &Geometry, flags: &[u8], traverser: usize, start: usize, count: usize) -> Value {
    let q = 1-traverser;
    let mut all_zero = 0u64;
    let mut negative_zero = 0u64;
    let mut finite_nonzero = 0u64;
    let mut nonfinite = 0u64;
    let mut finite_amount = 0u64;
    let mut eligible = 0u64;
    for row in &g.rows[start..start+count] {
        let flag = flags[row.slots[q] as usize];
        let finite = row.amount_bits[traverser] & 0x7f80_0000 != 0x7f80_0000;
        all_zero += u64::from(flag == 0);
        negative_zero += u64::from(flag & 1 != 0);
        finite_nonzero += u64::from(flag & 2 != 0);
        nonfinite += u64::from(flag & 4 != 0);
        finite_amount += u64::from(finite);
        eligible += u64::from(flag == 0 && finite);
    }
    json!({"fold_ctas":count,"all_positive_zero":all_zero,"any_negative_zero":negative_zero,
        "any_finite_nonzero":finite_nonzero,"any_nonfinite":nonfinite,
        "finite_selected_amount":finite_amount,"all_positive_zero_and_finite_amount":eligible})
}

fn snapshot(a: &GpuSolver, b: &GpuSolver, g: &Geometry, fixture: &str, iteration: u32, directory: &Path) -> DiagResult<()> {
    a.synchronize()?; b.synchronize()?;
    if a.iteration != iteration || b.iteration != iteration { return Err("snapshot iteration differs".into()); }
    let mut arrays = Vec::new();
    for q in 0..2 {
        let left = &a.d_reach[q];
        let right = &b.d_reach[q];
        if left.len() != right.len() || g.reach_blocks[q].checked_mul(g.nh[q]) != Some(left.len()) {
            return Err("snapshot logical reach dimensions differ".into());
        }
        // Flags persist across chunk boundaries. Exact length equality makes every
        // physical row contain precisely nh[q] logical words; no padding is scanned.
        let mut flags = vec![0u8; g.reach_blocks[q]];
        let mut words = [0u64; 4];
        let mut hash = Fingerprint::new();
        for offset in (0..left.len()).step_by(CHUNK) {
            let end = (offset+CHUNK).min(left.len());
            let x = a.stream.clone_dtoh(&left.slice(offset..end)).map_err(e)?;
            let y = b.stream.clone_dtoh(&right.slice(offset..end)).map_err(e)?;
            for (i, (x, y)) in x.iter().zip(&y).enumerate() {
                let bits = x.to_bits();
                if bits != y.to_bits() { return Err(format!("reach{q}/{} bits differ", offset+i)); }
                let category = if bits == 0 { 0 } else if bits == 0x8000_0000 { 1 }
                    else if bits & 0x7f80_0000 == 0x7f80_0000 { 3 } else { 2 };
                words[category] += 1;
                flags[(offset+i)/g.nh[q]] |= match category { 0=>0,1=>1,2=>2,_=>4 };
                hash.bytes(&bits.to_le_bytes());
            }
        }
        if words.iter().sum::<u64>() != left.len() as u64 { return Err("word classification coverage differs".into()); }
        let name = format!("{fixture}-iteration{iteration}-reach{q}.rowflags");
        let mut file = std::fs::OpenOptions::new().write(true).create_new(true).open(directory.join(&name)).map_err(e)?;
        file.write_all(&flags).map_err(e)?; file.flush().map_err(e)?;
        let mut class_hash = Fingerprint::new(); class_hash.bytes(&flags);
        let p = 1-q;
        let levels: Vec<_> = g.spans.iter().enumerate().map(|(level, span)| json!({
            "level":level,"start":span.start,"count":span.count,
            "counts":fold_counts(g,&flags,p,span.start as usize,span.count as usize)})).collect();
        arrays.push(json!({"opponent":q,"traverser":p,"logical_nh":g.nh[q],"physical_rows":g.reach_blocks[q],
            "entries":left.len(),"reach_fnv1a64":hash.finish(),"paired_bits_exact":true,
            "whole_reach_word_categories":{"positive_zero":words[0],"negative_zero":words[1],"finite_nonzero":words[2],"nonfinite":words[3]},
            "rowclass":{"file":name,"bytes":flags.len(),"fnv1a64":class_hash.finish()},
            "fold_counts":fold_counts(g,&flags,p,0,g.rows.len()),"levels":levels}));
    }
    emit(json!({"stage":"snapshot","fixture_id":fixture,"iteration":iteration,"before_exploitability":true,
        "paired_reach_bits_exact":true,"chunk_floats":CHUNK,"peak_float_snapshot_bytes":CHUNK*8,
        "arrays":arrays,"raw_float_payload_retained":false,"performance_measurement":false}))
}

fn fixture(anchor: &Value, directory: &Path) -> DiagResult<()> {
    let id = anchor["fixture_id"].as_str().ok_or("fixture id")?;
    let final_iteration = anchor["final_iteration"].as_u64().ok_or("final iteration")? as u32;
    let before_spot = available_ram()?;
    if before_spot < 16*GIB { return Err("less than16GiB free host RAM before Spot".into()); }
    let config: SpotConfig = serde_json::from_value(anchor["config"].clone()).map_err(e)?;
    let spot = Arc::new(Spot::new(config)?);
    let plan = GpuPlan::build(&spot,true);
    if plan.num_nodes as u64 != anchor["nodes"].as_u64().ok_or("nodes anchor")?
        || json!(plan.nh) != anchor["nh"] { return Err("frozen fixture geometry differs".into()); }
    let device_per_arm = planned_device_bytes(&spot,&plan)?;
    let dual_device = checked_sum(&[device_per_arm,device_per_arm,2*GIB])?;
    let cpu_per_arm = spot.arena_bytes_for(Storage::Compressed);
    let pinned_per_arm = (plan.arena_elements[0].max(plan.arena_elements[1]) as u64).checked_mul(4).ok_or("pinned overflow")?;
    let geometry_bytes = checked_sum(&[(plan.fold_nodes.len() as u64).checked_mul(20).ok_or("mapping overflow")?,
        (plan.fold_spans.len() as u64).checked_mul(8).ok_or("spans overflow")?,plan.reach_blocks[0].max(plan.reach_blocks[1]) as u64])?;
    let host_additional = checked_sum(&[cpu_per_arm,cpu_per_arm,pinned_per_arm,pinned_per_arm,CHUNK as u64*8,geometry_bytes,8*GIB])?;
    let ram = available_ram()?;
    let ctx = CudaContext::new(0).map_err(e)?;
    let (free,total) = ctx.mem_get_info().map_err(e)?;
    emit(json!({"stage":"admission","fixture_id":id,"device_per_arm_payload_bytes":device_per_arm,
        "dual_device_required_with_reserve":dual_device,"device_reserve_bytes":2*GIB,"device_free_bytes":free,"device_total_bytes":total,
        "host_free_before_spot":before_spot,"host_free_after_spot_and_plan":ram,"host_additional_required":host_additional,
        "host_reserve_bytes":8*GIB,"cpu_arena_bytes_per_arm":cpu_per_arm,"device_arena_elements":plan.arena_elements,
        "pinned_bytes_per_arm":pinned_per_arm,"compact_geometry_and_rowclass_bytes":geometry_bytes,
        "raw_compare_max_bytes":CHUNK*8,"shared_tree_bytes":spot.tree_bytes()}))?;
    if (free as u64) < dual_device || ram < host_additional { return Err("dual solver memory admission refused".into()); }
    let mut host_a = Solver::with_storage(spot.clone(),Storage::Compressed);
    let mut host_b = Solver::with_storage(spot.clone(),Storage::Compressed);
    if host_a.algo != Algorithm::Dcfr || !host_a.use_isomorphism || !host_a.locks.is_empty()
        || host_b.algo != host_a.algo || !host_b.use_isomorphism || !host_b.locks.is_empty() {
        return Err("unexpected ordinary solver defaults".into());
    }
    let mut ordinary = SolverGuard(GpuSolver::new(&host_a)?);
    ordinary.synchronize()?;
    let (remaining,_) = ctx.mem_get_info().map_err(e)?;
    if (remaining as u64) < checked_sum(&[device_per_arm,2*GIB])? { return Err("device memory changed before second solver".into()); }
    let mut observed = SolverGuard(GpuSolver::new(&host_b)?);
    observed.synchronize()?;
    verify_metadata(&ordinary,&plan)?; verify_metadata(&observed,&plan)?;
    let g = geometry(&spot,&plan)?;
    let mapping = write_mapping(directory,id,&g)?;
    let spans: Vec<_> = g.spans.iter().enumerate().map(|(level,s)| json!({"level":level,"start":s.start,"count":s.count})).collect();
    emit(json!({"stage":"geometry","fixture_id":id,"nodes":plan.num_nodes,"nh":g.nh,"reach_blocks":g.reach_blocks,
        "fold_ctas_per_traverser":g.rows.len(),"fold_spans":spans,"mapping":mapping,
        "uploaded_metadata_exact_both_arms":true,"physical_reach_has_padding":false}))?;
    drop(plan);
    let mut last_exploit = 0.0;
    for checkpoint in (20..=final_iteration).step_by(20) {
        for _ in 0..20 { ordinary.iterate()?; }
        for _ in 0..20 { observed.iterate()?; }
        if checkpoint == 20 || checkpoint == final_iteration {
            snapshot(&ordinary,&observed,&g,id,checkpoint,directory)?;
        }
        let x = check_exploit(&mut ordinary,&host_a,&anchor["convergence"])?;
        let y = check_exploit(&mut observed,&host_b,&anchor["convergence"])?;
        if x.to_bits() != y.to_bits() { return Err("checkpoint exploit bits differ".into()); }
        last_exploit = x;
        emit(json!({"stage":"checkpoint","fixture_id":id,"iteration":checkpoint,"exploit_bits":x.to_bits(),
            "ordinary_and_observed_exact":true,"immutable_original_and_E020_anchor_exact":true}))?;
    }
    ordinary.sync_to_cpu(&mut host_a)?;
    observed.sync_to_cpu(&mut host_b)?;
    compare_cpu(&host_a,&host_b)?;
    let first = state_fingerprint(&host_a,last_exploit);
    let second = state_fingerprint(&host_b,last_exploit);
    if first != anchor["state_fingerprint"] || second != first { return Err("full final fingerprint differs from immutable anchor".into()); }
    ordinary.synchronize()?; observed.synchronize()?;
    drop(ordinary); drop(observed);
    ctx.check_err().map_err(e)?;
    emit(json!({"stage":"final_anchor_exact","fixture_id":id,"iteration":final_iteration,
        "complete_cpu_q_and_scale_bits_exact":true,"state_fingerprint":first,"cleanup_complete":true}))
}

fn diagnostic() -> DiagResult<()> {
    let directory = std::env::var_os("D066_CENSUS_DIR").ok_or("D066_CENSUS_DIR is required")?;
    let directory = Path::new(&directory);
    if !directory.is_dir() || std::fs::read_dir(directory).map_err(e)?.next().is_some() {
        return Err("census output directory must already exist and be empty".into());
    }
    let anchors: Value = serde_json::from_str(ANCHORS_JSON).map_err(e)?;
    let anchors = anchors.as_array().ok_or("anchors array")?;
    if anchors.len() != 3 { return Err("fixture count".into()); }
    for (i, (id, final_iteration)) in [("rainbow",200),("two-tone",200),("river",60)].iter().enumerate() {
        if anchors[i]["fixture_id"] != *id || anchors[i]["final_iteration"] != *final_iteration {
            return Err("fixed fixture order differs".into());
        }
        fixture(&anchors[i],directory)?;
    }
    emit(json!({"stage":"complete","fixtures":3,"snapshots":6,"reach_array_snapshots":12,"checkpoints":23,
        "final_full_state_checks":3,"mapping_files":3,"rowclass_files":12,"performance_measurement":false,"candidate_accepted":false}))
}

#[test]
#[ignore = "manual D066 fold positive-zero census; serialized GPU execution only"]
fn fold_zero_reach_census() {
    if let Err(error) = diagnostic() {
        let _ = emit(json!({"stage":"invalid","error":error}));
        panic!("D066 invalid diagnostic: {error}");
    }
}

fn compare_cpu(a: &Solver,b: &Solver) -> DiagResult<()> {
    if a.iteration!=b.iteration { return Err("CPU iteration mismatch".into()); }
    for p in 0..2 {
        for (x,y) in [(&a.regrets[p],&b.regrets[p]),(&a.strat[p],&b.strat[p])] {
            let equal=match (x,y) {
                (Store::I16{q:x,scale:xs},Store::I16{q:y,scale:ys}) => x.as_slice()==y.as_slice()
                    && xs.len()==ys.len() && xs.as_slice().iter().zip(ys.as_slice()).all(|(x,y)|x.to_bits()==y.to_bits()),
                (Store::U16{q:x,scale:xs},Store::U16{q:y,scale:ys}) => x.as_slice()==y.as_slice()
                    && xs.len()==ys.len() && xs.as_slice().iter().zip(ys.as_slice()).all(|(x,y)|x.to_bits()==y.to_bits()),
                _ => false,
            };
            if !equal { return Err(format!("CPU compressed store mismatch player{p}")); }
        }
    }
    Ok(())
}

fn check_exploit(gpu:&mut GpuSolver,host:&Solver,anchors:&Value) -> DiagResult<f64> {
    let exploit=gpu.exploitability(host)?;
    let expected=anchors.as_array().ok_or("anchor array")?.iter()
        .find(|x|x["iteration"].as_u64()==Some(gpu.iteration as u64)).ok_or("missing iteration anchor")?;
    if !exploit.is_finite() || Some(exploit.to_bits())!=expected["exploit_bits"].as_u64() {
        return Err(format!("iteration{} exploit anchor mismatch: {}",gpu.iteration,exploit.to_bits()));
    }
    Ok(exploit)
}

// Stream every byte without allocating a second copy of the multi-GB arenas.
// This is a deterministic equality fingerprint, not a cryptographic digest.
struct Fingerprint(u64);
impl Fingerprint {
    fn new() -> Self {
        Self(0xcbf29ce484222325)
    }

    fn bytes(&mut self, bytes: &[u8]) {
        for &byte in bytes {
            self.0 = (self.0 ^ u64::from(byte)).wrapping_mul(0x100000001b3);
        }
    }

    fn finish(&self) -> String {
        format!("{:016x}", self.0)
    }
}

fn fingerprint_store(store: &Store, combined: &mut Fingerprint) -> Value {
    let mut hash = Fingerprint::new();
    let mut feed = |bytes: &[u8]| {
        hash.bytes(bytes);
        combined.bytes(bytes);
    };
    let (kind, entries, scales) = match store {
        Store::F32(values) => {
            feed(b"f32");
            feed(&(values.len() as u64).to_le_bytes());
            for value in values.as_slice() {
                feed(&value.to_bits().to_le_bytes());
            }
            ("f32", values.len(), 0)
        }
        Store::I16 { q, scale } => {
            feed(b"i16");
            feed(&(q.len() as u64).to_le_bytes());
            feed(&(scale.len() as u64).to_le_bytes());
            for value in q.as_slice() {
                feed(&value.to_le_bytes());
            }
            for value in scale.as_slice() {
                feed(&value.to_bits().to_le_bytes());
            }
            ("i16", q.len(), scale.len())
        }
        Store::U16 { q, scale } => {
            feed(b"u16");
            feed(&(q.len() as u64).to_le_bytes());
            feed(&(scale.len() as u64).to_le_bytes());
            for value in q.as_slice() {
                feed(&value.to_le_bytes());
            }
            for value in scale.as_slice() {
                feed(&value.to_bits().to_le_bytes());
            }
            ("u16", q.len(), scale.len())
        }
    };
    json!({
        "kind": kind, "entries": entries, "scale_entries": scales,
        "bytes": store.bytes(), "hash": hash.finish(),
    })
}

fn state_fingerprint(solver: &Solver, exploit: f64) -> Value {
    let mut combined = Fingerprint::new();
    combined.bytes(b"postflop-autoresearch-state-v1");
    let algorithm = serde_json::to_vec(&solver.algo).unwrap();
    combined.bytes(&(algorithm.len() as u64).to_le_bytes());
    combined.bytes(&algorithm);
    combined.bytes(&solver.iteration.to_le_bytes());
    combined.bytes(&[u8::from(solver.use_isomorphism)]);
    combined.bytes(&exploit.to_bits().to_le_bytes());
    let mut arenas = Vec::new();
    for player in 0..2 {
        for (name, store) in [
            ("regrets", &solver.regrets[player]),
            ("strategy_sums", &solver.strat[player]),
        ] {
            combined.bytes(&(player as u64).to_le_bytes());
            combined.bytes(name.as_bytes());
            let mut arena = fingerprint_store(store, &mut combined);
            arena["player"] = json!(player);
            arena["arena"] = json!(name);
            arenas.push(arena);
        }
    }
    // Root strategy is cheap and does not materialize inactive suit branches.
    let root_strategy_bits: Vec<u32> = solver
        .average_strategy(0, &solver.spot.tree.nodes[0])
        .iter()
        .map(|value| value.to_bits())
        .collect();
    json!({
        "method": "fnv1a64-little-endian-v1", "hash": combined.finish(),
        "algorithm": solver.algo, "iteration": solver.iteration,
        "iteration_le_bytes": solver.iteration.to_le_bytes(),
        "exploit_bits": exploit.to_bits(), "arenas": arenas,
        "root_strategy_bits": root_strategy_bits,
        "scope": "all CPU regret and strategy entries and scales immediately after full GPU readback",
    })
}


const ANCHORS_JSON: &str = r###"[
  {
    "fixture_id": "rainbow",
    "fixture_index": 0,
    "config": {
      "board": "Ks7h2d",
      "range_ip": "22+,A2s+,K6s+,Q8s+,J8s+,T8s+,97s+,87s,76s,65s,A8o+,KTo+,QTo+,JTo",
      "range_oop": "55-22,A8s-A2s,K9s-K6s,Q9s-Q6s,J9s-J7s,T8s-T7s,97s,98s,86s,87s,75s,76s,64s,65s,53s,54s,43s,AJo-A8o,KTo-K9o,QTo,QJo,JTo,T9o,98o",
      "tree": {
        "add_allin": false,
        "allin_threshold": 0.85,
        "carry_aggressor_through_checks": null,
        "effective_stack": 970.0,
        "ip": [
          {
            "bet": [
              {
                "PotPct": 33.0
              },
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "max_raises": 10,
        "oop": [
          {
            "bet": [
              {
                "PotPct": 33.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "rake_cap": 3.0,
        "rake_pct": 0.0,
        "starting_pot": 60.0
      }
    },
    "final_iteration": 200,
    "snapshot_iterations": [
      20,
      200
    ],
    "nodes": 1346813,
    "nh": [
      257,
      319
    ],
    "state_fingerprint": {
      "algorithm": "Dcfr",
      "arenas": [
        {
          "arena": "regrets",
          "bytes": 317428942,
          "entries": 156020845,
          "hash": "af31c4ea5b36e0de",
          "kind": "i16",
          "player": 0,
          "scale_entries": 1346813
        },
        {
          "arena": "strategy_sums",
          "bytes": 317428942,
          "entries": 156020845,
          "hash": "47bb30304cc30491",
          "kind": "u16",
          "player": 0,
          "scale_entries": 1346813
        },
        {
          "arena": "regrets",
          "bytes": 375731578,
          "entries": 185172163,
          "hash": "c0fbb58a97c882ba",
          "kind": "i16",
          "player": 1,
          "scale_entries": 1346813
        },
        {
          "arena": "strategy_sums",
          "bytes": 375731578,
          "entries": 185172163,
          "hash": "b3f701482b98c098",
          "kind": "u16",
          "player": 1,
          "scale_entries": 1346813
        }
      ],
      "exploit_bits": 4595130701932466176,
      "hash": "65fb2853a11f3acc",
      "iteration": 200,
      "iteration_le_bytes": [
        200,
        0,
        0,
        0
      ],
      "method": "fnv1a64-little-endian-v1",
      "root_strategy_bits": [
        1065085704,
        1065070093,
        1065067529,
        1065248517,
        1065228548,
        1065248517,
        1065247491,
        1065256707,
        1065249283,
        1065352448,
        1065352448,
        1065258499,
        1065352448,
        1065229318,
        1065255940,
        1065352448,
        1065258756,
        1065262852,
        1065256964,
        1065352448,
        1065352448,
        1065352448,
        1065322497,
        1065242373,
        1065352448,
        1065245187,
        1065241859,
        1065252611,
        1065352448,
        1065196549,
        1065243139,
        1065253635,
        1065253893,
        1065352448,
        1065352448,
        1065352448,
        1065253635,
        1065352448,
        1065164809,
        1065352448,
        1065213446,
        1065110791,
        1065198597,
        1065155337,
        1065196293,
        1065224454,
        1065224452,
        1065352448,
        1065297410,
        1065026831,
        1065270531,
        1065128711,
        1065313793,
        1065262595,
        1065300994,
        1065352448,
        1065352448,
        1065352448,
        1065352448,
        1065275906,
        1065352448,
        1065201927,
        1065352192,
        1065352448,
        1065352448,
        1065352192,
        1065270786,
        1065352448,
        1065270019,
        1065352448,
        1065352448,
        1065352448,
        1065148934,
        1065299202,
        1065352448,
        1065350656,
        1065351424,
        1065351936,
        1065295875,
        1065245957,
        1065351680,
        1065347584,
        1065350912,
        1065201927,
        1065351680,
        1065343488,
        1065350912,
        1065290242,
        1065234437,
        1065350144,
        1065330433,
        1065336320,
        1065270786,
        1065352192,
        1065352448,
        1065348096,
        1065348096,
        1065341440,
        1065242883,
        1065352192,
        1065147401,
        1065346304,
        1065334529,
        1065317377,
        1065351936,
        1065106696,
        1065348352,
        1065337856,
        1065327105,
        1065240835,
        1065352192,
        1065018895,
        1065342208,
        1065325313,
        1065327105,
        1065351936,
        1065299202,
        1065351936,
        1065351936,
        1065351936,
        1065351936,
        1065351168,
        1065346304,
        1065346048,
        1065346304,
        1065351936,
        1065261827,
        1065351424,
        1065309186,
        1065351680,
        1065350656,
        1065344512,
        1065346048,
        1065341185,
        1065338625,
        1065351936,
        1065351424,
        1065285890,
        1065351936,
        1065350656,
        1065347584,
        1065346048,
        1065340416,
        1065337856,
        1065352192,
        1065251587,
        1065351936,
        1065266435,
        1065351168,
        1065348864,
        1065349632,
        1065346048,
        1065334785,
        1065337857,
        1065263620,
        1065065737,
        1065255171,
        1065256195,
        1065284098,
        1065281026,
        1065264132,
        1065250563,
        1065244419,
        1065246211,
        1065213702,
        1065040654,
        1065218052,
        1065278467,
        1065174792,
        1065285634,
        1065282050,
        1065245443,
        1065244419,
        1065251587,
        1065202949,
        1065201159,
        1065281794,
        1065292547,
        1065157129,
        1065285635,
        1065251333,
        1065258755,
        1065260547,
        1065261572,
        1065340416,
        1065339392,
        1065337857,
        1065337344,
        1065273858,
        1065321729,
        1065318913,
        1065320193,
        1065319170,
        1065302018,
        1065304066,
        1065301506,
        1065287426,
        1065287426,
        1065282818,
        1065310721,
        1065309185,
        1065310977,
        1065268739,
        1065217286,
        1065129735,
        1065295874,
        1065237508,
        1065316610,
        1065236741,
        1065314561,
        1065313281,
        1065295106,
        1065291522,
        1065287170,
        1065273090,
        1065265411,
        1065259780,
        1065306369,
        1065293570,
        1065301250,
        1065204741,
        1065259011,
        1065182469,
        1065262340,
        1065289218,
        1065315841,
        1065311490,
        1065247491,
        1065312258,
        1065293058,
        1065284866,
        1065284611,
        1065270786,
        1065262339,
        1065257987,
        1065306881,
        1065301762,
        1065302018,
        1065215494,
        1065179912,
        1065239301,
        1065160713,
        1065268484,
        1065255171,
        1065314305,
        1065309185,
        1065311234,
        1065203461,
        1065288963,
        1065279491,
        1065284098,
        1065267203,
        1065257988,
        1065261315,
        1065305346,
        1065299970,
        1065298178,
        1015193339,
        1015692897,
        1015774953,
        1003257242,
        1005813273,
        1003257242,
        1003388515,
        1002208903,
        1003159146,
        943718016,
        943718016,
        1001979534,
        943718016,
        1005714730,
        1002307014,
        943718016,
        1001946582,
        1001422318,
        1002175948,
        943718016,
        943718016,
        943718016,
        988806448,
        1004043638,
        943718016,
        1003683418,
        1004109389,
        1002733175,
        943718016,
        1008271054,
        1003945554,
        1002602107,
        1002569146,
        943718016,
        943718016,
        943718016,
        1002602107,
        943718016,
        1010302424,
        943718016,
        1007189606,
        1013759526,
        1008139986,
        1010908604,
        1008287438,
        1006337294,
        1006337545,
        943718016,
        995753548,
        1017077282,
        1000439485,
        1012612682,
        991559372,
        1001455262,
        994835868,
        943718016,
        943718016,
        943718016,
        943718016,
        999751378,
        943718016,
        1007926853,
        947911936,
        943718016,
        943718016,
        947911936,
        1000406718,
        943718016,
        1000505019,
        943718016,
        943718016,
        943718016,
        1011318385,
        995294810,
        943718016,
        958398144,
        954203488,
        950009376,
        996146528,
        1003584908,
        952106432,
        967835120,
        957349456,
        1007926853,
        952106432,
        974650936,
        957349600,
        997588500,
        1005059400,
        960495232,
        984743402,
        981729016,
        1000406718,
        947911936,
        943718016,
        966786752,
        966786592,
        976748176,
        1003978321,
        947912192,
        1011416485,
        970456440,
        982646492,
        990641896,
        950009376,
        1014021662,
        966262480,
        980418080,
        986447464,
        1004240457,
        947912192,
        1017331222,
        975961596,
        987364940,
        986447260,
        950009536,
        995294599,
        950009536,
        950009536,
        950009536,
        950009376,
        956300800,
        970456656,
        970980704,
        970456656,
        950009536,
        1001553563,
        954203488,
        992738812,
        952106624,
        958398144,
        973602544,
        970980704,
        977010124,
        979631444,
        950009376,
        954203488,
        998473465,
        950009536,
        958397984,
        967835296,
        970980704,
        977796720,
        980418080,
        947911936,
        1002864243,
        950009536,
        1000963757,
        956300800,
        965213800,
        962592320,
        970980704,
        982515280,
        980417840,
        1001324019,
        1015832295,
        1002405505,
        1002274437,
        998702834,
        999096038,
        1001258486,
        1002995311,
        1003781719,
        1003552350,
        1007173223,
        1016634934,
        1006894840,
        999423562,
        1009663477,
        998506232,
        998964970,
        1003650651,
        1003781719,
        1002864243,
        1007861466,
        1007976002,
        998997737,
        996998457,
        1010793922,
        998506100,
        1002896811,
        1001946767,
        1001717398,
        1001586151,
        977796720,
        978845264,
        980417840,
        980942352,
        1000013514,
        989199892,
        990248692,
        989921022,
        990183025,
        994573936,
        994049472,
        994705004,
        998276863,
        998276863,
        998866669,
        992345780,
        992738984,
        992280246,
        1000668854,
        1006943858,
        1012547148,
        996146752,
        1004666428,
        990838355,
        1004764502,
        991362770,
        991690440,
        996343354,
        997260830,
        998309630,
        1000111815,
        1001094825,
        1001815516,
        993459858,
        996736558,
        994770538,
        1007746782,
        1001914000,
        1009172146,
        1001487852,
        997850636,
        991035100,
        992149015,
        1003388515,
        991952416,
        996867626,
        998604533,
        998637166,
        1000406718,
        1001488029,
        1002045068,
        993328790,
        994639470,
        994573936,
        1007058540,
        1009335812,
        1004436836,
        1010564556,
        1000701456,
        1002405505,
        991428304,
        992738984,
        992214548,
        1007828700,
        997915919,
        999292496,
        998702834,
        1000865456,
        1002044882,
        1001619097,
        993721807,
        995098000,
        995556731
      ],
      "scope": "all CPU regret and strategy entries and scales immediately after full GPU readback"
    },
    "convergence": [
      {
        "iteration": 20,
        "exploit_bits": 4622293349835068352
      },
      {
        "iteration": 40,
        "exploit_bits": 4615910349596779108
      },
      {
        "iteration": 60,
        "exploit_bits": 4611592466607110480
      },
      {
        "iteration": 80,
        "exploit_bits": 4607812973746629388
      },
      {
        "iteration": 100,
        "exploit_bits": 4604651510606006304
      },
      {
        "iteration": 120,
        "exploit_bits": 4602400871342019424
      },
      {
        "iteration": 140,
        "exploit_bits": 4600062402970321824
      },
      {
        "iteration": 160,
        "exploit_bits": 4598526937924752800
      },
      {
        "iteration": 180,
        "exploit_bits": 4596673615736125952
      },
      {
        "iteration": 200,
        "exploit_bits": 4595130701932466176
      }
    ]
  },
  {
    "fixture_id": "two-tone",
    "fixture_index": 1,
    "config": {
      "board": "Ks7s2d",
      "range_ip": "22+,A2s+,K6s+,Q8s+,J8s+,T8s+,97s+,87s,76s,65s,A8o+,KTo+,QTo+,JTo",
      "range_oop": "55-22,A8s-A2s,K9s-K6s,Q9s-Q6s,J9s-J7s,T8s-T7s,97s,98s,86s,87s,75s,76s,64s,65s,53s,54s,43s,AJo-A8o,KTo-K9o,QTo,QJo,JTo,T9o,98o",
      "tree": {
        "add_allin": false,
        "allin_threshold": 0.85,
        "carry_aggressor_through_checks": null,
        "effective_stack": 970.0,
        "ip": [
          {
            "bet": [
              {
                "PotPct": 33.0
              },
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "max_raises": 10,
        "oop": [
          {
            "bet": [
              {
                "PotPct": 33.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "rake_cap": 3.0,
        "rake_pct": 0.05,
        "starting_pot": 60.0
      }
    },
    "final_iteration": 200,
    "snapshot_iterations": [
      20,
      200
    ],
    "nodes": 1346813,
    "nh": [
      258,
      320
    ],
    "state_fingerprint": {
      "algorithm": "Dcfr",
      "arenas": [
        {
          "arena": "regrets",
          "bytes": 318643112,
          "entries": 156627930,
          "hash": "81e4922faddee8df",
          "kind": "i16",
          "player": 0,
          "scale_entries": 1346813
        },
        {
          "arena": "strategy_sums",
          "bytes": 318643112,
          "entries": 156627930,
          "hash": "9b1305ea75f444cf",
          "kind": "u16",
          "player": 0,
          "scale_entries": 1346813
        },
        {
          "arena": "regrets",
          "bytes": 376892532,
          "entries": 185752640,
          "hash": "112676fa41d0253e",
          "kind": "i16",
          "player": 1,
          "scale_entries": 1346813
        },
        {
          "arena": "strategy_sums",
          "bytes": 376892532,
          "entries": 185752640,
          "hash": "060e1d9bda7dbaa9",
          "kind": "u16",
          "player": 1,
          "scale_entries": 1346813
        }
      ],
      "exploit_bits": 4594601713124613664,
      "hash": "9dd12ac305ce542f",
      "iteration": 200,
      "iteration_le_bytes": [
        200,
        0,
        0,
        0
      ],
      "method": "fnv1a64-little-endian-v1",
      "root_strategy_bits": [
        1064912653,
        1065105931,
        1065106440,
        1065175304,
        1065178885,
        1065175304,
        1065266180,
        1065293571,
        1065266435,
        1065352192,
        1065352192,
        1065182216,
        1065352192,
        1065177096,
        1065182216,
        1065221894,
        1065281283,
        1065289475,
        1065281283,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065173256,
        1065352192,
        1065352192,
        1065169416,
        1065173256,
        1065262851,
        1065227270,
        1065281795,
        1065285635,
        1065281795,
        1065352192,
        1065352192,
        1065352192,
        1065336577,
        1065352192,
        1065352192,
        1065291523,
        1065189127,
        1065013520,
        1065165062,
        1065274372,
        1065290755,
        1065013520,
        1065165318,
        1065352192,
        1065302018,
        1065253125,
        1065285634,
        1065352192,
        1065302018,
        1065245187,
        1065273092,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065300994,
        1065352192,
        1065134858,
        1065352192,
        1065352192,
        1065273092,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065233157,
        1065304833,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065300482,
        1065351936,
        1065352192,
        1065352192,
        1065350912,
        1065304833,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065232389,
        1065341440,
        1065137930,
        1065341440,
        1065297922,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065343488,
        1065281794,
        1065352192,
        1065351680,
        1065352192,
        1065352192,
        1065177864,
        1065297922,
        1065352192,
        1065352192,
        1065352192,
        1065352192,
        1065343488,
        1064968210,
        1065180421,
        1065304834,
        1064780049,
        1065305090,
        1065352192,
        1065303042,
        1065352192,
        1065351936,
        1065351936,
        1065351936,
        1065345024,
        1065351936,
        1065351936,
        1065318914,
        1065352192,
        1065283074,
        1065351936,
        1065351424,
        1065351936,
        1065351936,
        1065319681,
        1065351936,
        1065351936,
        1064806169,
        1065352192,
        1065303042,
        1065352192,
        1065351936,
        1065351936,
        1065351936,
        1065345024,
        1065351936,
        1065351936,
        1065318914,
        1064967954,
        1065140998,
        1065248259,
        1065200645,
        1064459305,
        1065200645,
        1065259267,
        1064655392,
        1065259267,
        1065287938,
        1065019658,
        1065268483,
        1065285123,
        1065298690,
        1065283586,
        1065246981,
        1065261827,
        1065256451,
        1065265412,
        1065226500,
        1065003792,
        1065214212,
        1065294851,
        1065231108,
        1065294851,
        1065256452,
        1065255427,
        1065255427,
        1065262339,
        1065287938,
        1065019407,
        1065268483,
        1065283586,
        1065298690,
        1065285123,
        1065246981,
        1065256451,
        1065261827,
        1065265412,
        1065296387,
        1065349376,
        1065348608,
        1065346816,
        1065347584,
        1065264131,
        1065330433,
        1065328129,
        1065330433,
        1065290755,
        1065293570,
        1065301250,
        1065260548,
        1065271298,
        1065281027,
        1065285891,
        1065277955,
        1065286402,
        1065310977,
        1065302786,
        1065158153,
        1065194247,
        1065332225,
        1065254403,
        1065328641,
        1065265667,
        1065328641,
        1065271812,
        1065291010,
        1065291010,
        1065229828,
        1065262083,
        1065262083,
        1065258499,
        1065273090,
        1065273090,
        1065301250,
        1065296387,
        1065349376,
        1065348608,
        1065346816,
        1065347584,
        1065263876,
        1065330433,
        1065328129,
        1065330433,
        1065290755,
        1065301250,
        1065293570,
        1065260548,
        1065281282,
        1065271298,
        1065285891,
        1065286402,
        1065277955,
        1065310977,
        1065195525,
        1065238533,
        1065164038,
        1065223174,
        1065254404,
        1065174536,
        1065254916,
        1065174536,
        1065275138,
        1065249285,
        1065266436,
        1065249285,
        1065255427,
        1065269763,
        1065255427,
        1065299458,
        1065300738,
        1065299458,
        1020730962,
        1014070572,
        1014038046,
        1009630711,
        1009401516,
        1009630711,
        1000996354,
        996736325,
        1000963757,
        947911936,
        947911936,
        1009188363,
        947911936,
        1009516028,
        1009188363,
        1006648959,
        999063130,
        997784853,
        999063130,
        947911936,
        947911936,
        947911936,
        947911936,
        1009761777,
        947911936,
        947911936,
        1010007526,
        1009761777,
        1001422495,
        1005976862,
        998997598,
        998506100,
        998997598,
        947911936,
        947911936,
        947911936,
        981597818,
        947911936,
        947911936,
        997260589,
        1008746015,
        1017503246,
        1010286224,
        999947826,
        997457188,
        1017503246,
        1010269841,
        947911936,
        994573736,
        1002667446,
        998506232,
        947911936,
        994573736,
        1003683418,
        1000111658,
        947911936,
        947911936,
        947911936,
        947911936,
        994835868,
        947911936,
        1012219264,
        947911936,
        947911936,
        1000111658,
        947911936,
        947911936,
        947911936,
        947911936,
        947911936,
        947911936,
        947911936,
        1005223232,
        993853062,
        947911936,
        947911936,
        947911936,
        947912192,
        994967140,
        950009376,
        947911936,
        947911936,
        957349456,
        993853062,
        947911936,
        947911936,
        947911936,
        947912192,
        1005321532,
        976748176,
        1012022665,
        976748176,
        995622264,
        947911936,
        947911936,
        947911936,
        947911936,
        974651088,
        998997737,
        947911936,
        952106624,
        947911936,
        947911936,
        1009466878,
        995622264,
        947911936,
        947911936,
        947911936,
        947911936,
        974651088,
        1018953164,
        1009303214,
        993852873,
        1024192232,
        993787340,
        947911936,
        994311800,
        947911936,
        950009376,
        950009376,
        950009376,
        973078016,
        950009376,
        950009376,
        990248558,
        947912192,
        998833902,
        950009376,
        954203488,
        950009376,
        950009376,
        990052090,
        950009376,
        950009376,
        1023774319,
        947911936,
        994311800,
        947911936,
        950009376,
        950009376,
        950009376,
        973078016,
        950009376,
        950009376,
        990248558,
        1018961356,
        1011826274,
        1003290214,
        1008008918,
        1029324145,
        1008008918,
        1001881233,
        1026186753,
        1001881233,
        998178306,
        1017306810,
        1000701621,
        998571633,
        995425878,
        998768368,
        1003453842,
        1001553563,
        1002241670,
        1001094654,
        1006075409,
        1017814528,
        1007140592,
        996408660,
        1005485603,
        996408660,
        1002241481,
        1002372738,
        1002372738,
        1001488029,
        998178306,
        1017314839,
        1000701621,
        998768368,
        995425878,
        998571633,
        1003453842,
        1002241670,
        1001553563,
        1001094654,
        996015462,
        963640864,
        965738208,
        969408112,
        967835296,
        1001258660,
        984743402,
        985922996,
        984743402,
        997457188,
        996736558,
        994770538,
        1001717217,
        1000341184,
        999095897,
        998473334,
        999489095,
        998407931,
        992280246,
        994377334,
        1010728388,
        1008418350,
        983826104,
        1002503806,
        985660864,
        1001062058,
        985660864,
        1000275491,
        997391898,
        997391898,
        1005649438,
        1001520796,
        1001520796,
        1001979534,
        1000111815,
        1000111815,
        994770538,
        996015462,
        963640864,
        965738208,
        969408112,
        967835296,
        1001291252,
        984743402,
        985922996,
        984743402,
        997457188,
        994770538,
        996736558,
        1001717217,
        999063271,
        1000341184,
        998473334,
        998407931,
        999489095,
        992280246,
        1008336588,
        1004535136,
        1010351758,
        1006501126,
        1002503613,
        1009679860,
        1002438080,
        1009679860,
        999849679,
        1003158943,
        1000963588,
        1003158943,
        1002372738,
        1000537786,
        1002372738,
        995229066,
        994901401,
        995229066
      ],
      "scope": "all CPU regret and strategy entries and scales immediately after full GPU readback"
    },
    "convergence": [
      {
        "iteration": 20,
        "exploit_bits": 4621471963641686934
      },
      {
        "iteration": 40,
        "exploit_bits": 4614489749950135592
      },
      {
        "iteration": 60,
        "exploit_bits": 4609632359124586068
      },
      {
        "iteration": 80,
        "exploit_bits": 4606308451921813312
      },
      {
        "iteration": 100,
        "exploit_bits": 4603500064677737792
      },
      {
        "iteration": 120,
        "exploit_bits": 4601321529789973376
      },
      {
        "iteration": 140,
        "exploit_bits": 4599374301695986832
      },
      {
        "iteration": 160,
        "exploit_bits": 4597912096953046592
      },
      {
        "iteration": 180,
        "exploit_bits": 4596018308513263808
      },
      {
        "iteration": 200,
        "exploit_bits": 4594601713124613664
      }
    ]
  },
  {
    "fixture_id": "river",
    "fixture_index": 2,
    "config": {
      "board": "Ks7h2dQhTc",
      "range_ip": "22+,A2s+,K6s+,Q8s+,J8s+,T8s+,97s+,87s,76s,65s,A8o+,KTo+,QTo+,JTo",
      "range_oop": "55-22,A8s-A2s,K9s-K6s,Q9s-Q6s,J9s-J7s,T8s-T7s,97s,98s,86s,87s,75s,76s,64s,65s,53s,54s,43s,AJo-A8o,KTo-K9o,QTo,QJo,JTo,T9o,98o",
      "tree": {
        "add_allin": false,
        "allin_threshold": 0.85,
        "carry_aggressor_through_checks": null,
        "effective_stack": 970.0,
        "ip": [
          {
            "bet": [
              {
                "PotPct": 33.0
              },
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "max_raises": 10,
        "oop": [
          {
            "bet": [
              {
                "PotPct": 33.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          },
          {
            "bet": [
              {
                "PotPct": 75.0
              }
            ],
            "donk": [],
            "raise": [
              {
                "PotPct": 60.0
              }
            ]
          }
        ],
        "rake_cap": 3.0,
        "rake_pct": 0.05,
        "starting_pot": 60.0
      }
    },
    "final_iteration": 60,
    "snapshot_iterations": [
      20,
      60
    ],
    "nodes": 33,
    "nh": [
      233,
      280
    ],
    "state_fingerprint": {
      "algorithm": "Dcfr",
      "arenas": [
        {
          "arena": "regrets",
          "bytes": 7588,
          "entries": 3728,
          "hash": "2b9a02ef5184cd83",
          "kind": "i16",
          "player": 0,
          "scale_entries": 33
        },
        {
          "arena": "strategy_sums",
          "bytes": 7588,
          "entries": 3728,
          "hash": "ce97d51d8692bf2b",
          "kind": "u16",
          "player": 0,
          "scale_entries": 33
        },
        {
          "arena": "regrets",
          "bytes": 9092,
          "entries": 4480,
          "hash": "1e48e73f0bd174cf",
          "kind": "i16",
          "player": 1,
          "scale_entries": 33
        },
        {
          "arena": "strategy_sums",
          "bytes": 9092,
          "entries": 4480,
          "hash": "a9e756509a590c79",
          "kind": "u16",
          "player": 1,
          "scale_entries": 33
        }
      ],
      "exploit_bits": 4595002455471455360,
      "hash": "63944e67a4f99157",
      "iteration": 60,
      "iteration_le_bytes": [
        60,
        0,
        0,
        0
      ],
      "method": "fnv1a64-little-endian-v1",
      "root_strategy_bits": [
        1057023871,
        1057038848,
        1057026304,
        1065348352,
        1065348352,
        1065348352,
        1065348352,
        1065348352,
        1065348352,
        1064914695,
        1064914944,
        1065350656,
        1064916743,
        1065350656,
        1065350656,
        1064909319,
        1065350656,
        1065350656,
        1065350656,
        1065123840,
        1065124867,
        1065123584,
        1065124611,
        1065350656,
        1065124099,
        1065125376,
        1065350656,
        1065350656,
        1065121028,
        1065122304,
        1065350656,
        1065350656,
        1065350656,
        1065153539,
        1065152000,
        1065152259,
        1065150720,
        1065003776,
        1065001221,
        1065240578,
        1065239042,
        1065350656,
        1065350656,
        1065350656,
        1065350656,
        1065350656,
        1065350656,
        1065322496,
        1065350656,
        1065338624,
        1065350656,
        1065320960,
        1065349632,
        1065350656,
        1065350656,
        1065333760,
        1065352192,
        1065350912,
        1065352704,
        1065350656,
        1065351680,
        1065352704,
        1065352704,
        1065352704,
        1065350656,
        1065352704,
        1065350912,
        1065352704,
        1065350656,
        1065352704,
        1065352704,
        1065352704,
        1065352704,
        1063165729,
        1065236226,
        1065181440,
        1065185283,
        1065199106,
        1065238018,
        1065181699,
        1065185536,
        1065199362,
        1063233824,
        1065240576,
        1065181184,
        1065184768,
        1065185027,
        1065350656,
        1054933279,
        1061062977,
        1065216258,
        1065216768,
        1065216512,
        1065350656,
        1057668725,
        1061243711,
        1065217026,
        1065216770,
        1053184826,
        1060436992,
        1065215746,
        1065216000,
        1065350656,
        1058830180,
        1061232703,
        1065216768,
        1065217026,
        1065184259,
        1064764416,
        1065173248,
        1065161728,
        1064843784,
        1064842760,
        1064847368,
        1065143811,
        1065143808,
        1065144064,
        1065184256,
        1064775433,
        1065172480,
        1065159939,
        1064850440,
        1064855048,
        1065141763,
        1065143555,
        1065143808,
        1065187840,
        1064765952,
        1065175552,
        1065163523,
        1064851720,
        1064850440,
        1065141763,
        1065143555,
        1065143552,
        1064149010,
        1062484268,
        1063366686,
        1063580955,
        1063608091,
        1063323392,
        1063615003,
        1064199442,
        1064187154,
        1064235281,
        1064109587,
        1062865664,
        1063259424,
        1063520796,
        1063558939,
        1063241504,
        1063563035,
        1064212241,
        1064256000,
        1063972373,
        1062423341,
        1063175457,
        1063221504,
        1062798887,
        1063235360,
        1063801368,
        1063889686,
        1065349632,
        1064473869,
        1064475149,
        1065071620,
        1065060352,
        1065350656,
        1065352704,
        1065352704,
        1065352704,
        1065352704,
        1065352192,
        1065352192,
        1065352704,
        1065222144,
        1065222400,
        1065222400,
        1064450816,
        1064422144,
        1064461326,
        1064239121,
        1064241408,
        1064959750,
        1064980742,
        1065350656,
        1065352704,
        1065352704,
        1065352704,
        1065352704,
        1065351936,
        1065351936,
        1065352448,
        1065223938,
        1065223936,
        1064352000,
        1064253457,
        1064368384,
        1065349632,
        1064354048,
        1064356111,
        1065009664,
        1064440064,
        1065352704,
        1065352704,
        1065352704,
        1065352704,
        1065351936,
        1065351936,
        1065352448,
        1065224192,
        1065224448,
        1064336656,
        1064303120,
        1064348431,
        1065349632,
        1064421902,
        1064423168,
        1065068292,
        1065250562,
        1065350656,
        1065352704,
        1065352704,
        1065352704,
        1065352704,
        1065352192,
        1065352192,
        1065352192,
        1065222402,
        1065222658,
        1064456960,
        1064448014,
        1064408832,
        1056846082,
        1056816128,
        1056841216,
        966262632,
        966262632,
        966262632,
        966262632,
        966262632,
        966262632,
        1020665642,
        1020657664,
        958398304,
        1020600107,
        958398304,
        958398304,
        1020837671,
        958398304,
        958398304,
        958398304,
        1012924416,
        1012858657,
        1012940800,
        1012875041,
        958398304,
        1012907808,
        1012826112,
        958398304,
        958398304,
        1013104413,
        1013022720,
        958398304,
        958398304,
        958398304,
        1011023677,
        1011122176,
        1011105596,
        1011204096,
        1017815040,
        1017896788,
        1004273444,
        1004470049,
        958398304,
        958398304,
        958398304,
        958398304,
        958398304,
        958398304,
        988806928,
        958398304,
        979632128,
        958398304,
        989593348,
        962592768,
        958398304,
        958398304,
        983039848,
        947912448,
        957349744,
        939523840,
        958398304,
        952107008,
        939523840,
        939523840,
        939523840,
        958398464,
        939523840,
        957349744,
        939523840,
        958398304,
        939523840,
        939523840,
        939523840,
        939523840,
        1040548730,
        1004830492,
        1009238016,
        1008992092,
        1008107370,
        1004601119,
        1009221464,
        1008975872,
        1008090986,
        1040276351,
        1004273664,
        1009254400,
        1009025024,
        1009008476,
        958398464,
        1057980272,
        1048767869,
        1007009658,
        1006977024,
        1006993408,
        958398464,
        1055556373,
        1048236805,
        1006960507,
        1006976891,
        1058854499,
        1050019840,
        1007042426,
        1007026176,
        958398464,
        1053233465,
        1048280836,
        1006977024,
        1006960507,
        1009057627,
        1024442368,
        1009762304,
        1010499584,
        1022934791,
        1022967559,
        1022820105,
        1011646260,
        1011646464,
        1011630080,
        1009057792,
        1024266099,
        1009811456,
        1010614083,
        1022721802,
        1022574349,
        1011777330,
        1011662643,
        1011646464,
        1008828416,
        1024417792,
        1009614848,
        1010384711,
        1022680843,
        1022721802,
        1011777330,
        1011662643,
        1011662848,
        1033043821,
        1043274577,
        1039302414,
        1037588264,
        1037371179,
        1039648768,
        1037315884,
        1032640371,
        1032738674,
        1032353656,
        1033359208,
        1041748992,
        1040160512,
        1038069536,
        1037764389,
        1040245631,
        1037731621,
        1032537973,
        1032187904,
        1034456919,
        1043518285,
        1040509819,
        1040325632,
        1042016100,
        1040270207,
        1035824963,
        1035118413,
        962592544,
        1029091113,
        1029070634,
        1015644022,
        1016004608,
        958398304,
        939523840,
        939523840,
        939523840,
        939523840,
        947912448,
        947912704,
        939524096,
        1006632960,
        1006600192,
        1006600192,
        1029459968,
        1029918720,
        1029291814,
        1032322936,
        1032304640,
        1019223872,
        1018552138,
        958398304,
        939523840,
        939523840,
        939523840,
        939523840,
        950009696,
        950009696,
        943718208,
        1006403332,
        1006403584,
        1031041024,
        1032208250,
        1030778880,
        962592544,
        1031008256,
        1030975245,
        1017626624,
        1029632000,
        939523840,
        939523840,
        939523840,
        939523840,
        950009696,
        950009696,
        943718208,
        1006370816,
        1006338048,
        1031286536,
        1031810944,
        1031098123,
        962592544,
        1029922589,
        1029902336,
        1015750517,
        1002995512,
        958398304,
        939523840,
        939523840,
        939523840,
        939523840,
        947912704,
        947912448,
        947912704,
        1006599936,
        1006567169,
        1029361664,
        1029504803,
        1030131712
      ],
      "scope": "all CPU regret and strategy entries and scales immediately after full GPU readback"
    },
    "convergence": [
      {
        "iteration": 20,
        "exploit_bits": 4609920959812084448
      },
      {
        "iteration": 40,
        "exploit_bits": 4600653354794818656
      },
      {
        "iteration": 60,
        "exploit_bits": 4595002455471455360
      }
    ]
  }
]
"###;
