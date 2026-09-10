from pathlib import Path
import difflib, hashlib, json

src = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910\crates\solver\src\preflop')
out = Path(__file__).parent
original = {n: (src/n).read_text(encoding='utf-8') for n in ['gpu.rs','kernels.cu']}
gpu, cu = original['gpu.rs'], original['kernels.cu']
def rep(t,a,b):
    assert t.count(a)==1,(a[:90],t.count(a))
    return t.replace(a,b)

helper = '''// Compact only if its immutable map plus one CDF particle is no larger
// than the union's minimum cache. This also saves at every larger batch size.
struct MultiwayCompactPlan {
    capacity: usize,
    map: Vec<u32>,
    bytes: usize,
    enabled: bool,
}
impl MultiwayCompactPlan {
    fn union(slots: usize) -> Self {
        Self { capacity: slots, map: vec![0], bytes: 0, enabled: false }
    }
    fn build(plan: &EquityCachePlan, np: usize) -> Result<Self, String> {
        let union = plan.blocks.len();
        if union == 0 { return Ok(Self::union(0)); }
        let capacity = plan.spans[..np].iter().map(|&(_, n)| n as usize).max().unwrap_or(0);
        if capacity == 0 { return Err("multiway compact plan has no traverser slots".into()); }
        let len = union.checked_mul(np).ok_or_else(|| "multiway compact map overflow".to_string())?;
        let bytes = len.checked_mul(4).ok_or_else(|| "multiway compact map overflow".to_string())?;
        let saved_minimum = (union - capacity).checked_mul((NUM_CLASSES + 1) * 4)
            .ok_or_else(|| "multiway compact cache overflow".to_string())?;
        if bytes >= saved_minimum { return Ok(Self::union(union)); }
        let mut map = vec![u32::MAX; len];
        for p in 0..np {
            let (start, count) = plan.spans[p];
            for local in 0..count as usize {
                let global = plan.work[start as usize + local] as usize;
                map[p * union + global] = local as u32;
            }
        }
        Ok(Self { capacity, map, bytes, enabled: true })
    }
}

'''
gpu=rep(gpu,'// Pure byte-budget planner; no CUDA context or allocation is needed to test',helper+'// Pure byte-budget planner; no CUDA context or allocation is needed to test')
gpu=rep(gpu,'    use_mw_normalized: bool,','''    use_mw_normalized: bool,
    d_mw_compact: CudaSlice<u32>,
    mw_union_slots: u32,
    use_mw_compact: i32,''')
gpu=rep(gpu,'''        mw.metadata_bytes() + mw.blocks.len() * (NUM_CLASSES + 1) * 32 * 4
            + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4 + s.nodes.len() * 8
            + mw.blocks.len() * (NUM_CLASSES + 1) * 4''','''        let compact = MultiwayCompactPlan::build(&mw, s.n).unwrap_or_else(|_| MultiwayCompactPlan::union(mw.blocks.len()));
        mw.metadata_bytes() + compact.bytes + compact.capacity * (NUM_CLASSES + 1) * 32 * 4
            + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4 + s.nodes.len() * 8
            + mw.blocks.len() * 4 + compact.capacity * NUM_CLASSES * 4''')
gpu=rep(gpu,'''    pub fn new(s: &PreflopSolver, budget_mb: u64) -> Result<Self, String> {
        let reach_blocks''','''    pub fn new(s: &PreflopSolver, budget_mb: u64) -> Result<Self, String> {
        Self::new_with_layout(s, budget_mb, true)
    }

    // The private switch permits same-batch union/compact regression tests.
    // Public construction always chooses the minimum-fit-safe layout.
    fn new_with_layout(s: &PreflopSolver, budget_mb: u64, allow_compact: bool) -> Result<Self, String> {
        let reach_blocks''')
gpu=rep(gpu,'''        let use_multiway = !mw_terms.is_empty();
        let mut mw_batch''','''        let use_multiway = !mw_terms.is_empty();
        let compact = if use_multiway && allow_compact {
            MultiwayCompactPlan::build(&mw_plan, np)?
        } else { MultiwayCompactPlan::union(mw_plan.blocks.len()) };
        let mut mw_batch''')
gpu=rep(gpu,'''            let fixed = mw_plan.metadata_bytes() + mw_terms.len() * 8 + mw_plan.blocks.len() * 4
                + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4;''','''            let fixed = mw_plan.metadata_bytes() + mw_terms.len() * 8 + mw_plan.blocks.len() * 4
                + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4 + compact.bytes;''')
gpu=rep(gpu,'multiway_batch_plan(remaining, mw_plan.blocks.len())?','multiway_batch_plan(remaining, compact.capacity)?')
gpu=rep(gpu,'let one_particle = mw_plan.blocks.len() * (NUM_CLASSES + 1) * 4;','let one_particle = compact.capacity * (NUM_CLASSES + 1) * 4;')
gpu=rep(gpu,'''            if !use_mw_normalized {
                println!''','''            if compact.enabled {
                println!("preflop gpu: compact CDF slots {} of {}, {:.1} MB immutable map", compact.capacity, mw_plan.blocks.len(), compact.bytes as f64 / 1e6);
            }
            if !use_mw_normalized {
                println!''')
gpu=rep(gpu,'''            use_mw_normalized,
            d_mw_terms:''','''            use_mw_normalized,
            d_mw_compact: stream.clone_htod(&compact.map).map_err(e)?,
            mw_union_slots: mw_plan.blocks.len() as u32,
            use_mw_compact: compact.enabled as i32,
            d_mw_terms:''')
gpu=rep(gpu,'''                            .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)
                            .arg(&mut self.d_mw_normalized)''','''                            .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate).arg(&self.use_mw_compact)
                            .arg(&mut self.d_mw_normalized)''')
gpu=rep(gpu,'''                            .arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)
                            .arg(&mut self.d_mw_cdf)''','''                            .arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate).arg(&self.use_mw_compact)
                            .arg(&mut self.d_mw_cdf)''')
gpu=rep(gpu,'''                            .arg(&self.d_mw_slots).arg(&self.d_mw_cdf)
                            .arg(&self.d_mw_lower)''','''                            .arg(&self.d_mw_slots).arg(&self.d_mw_compact).arg(&self.mw_union_slots).arg(&self.use_mw_compact).arg(&self.d_mw_cdf)
                            .arg(&self.d_mw_lower)''')

# Maintain tests that inspect internal normalized storage or reproduce budgets.
gpu=rep(gpu,'''                let normalized = gpu.stream.clone_dtoh(&gpu.d_mw_normalized).unwrap();
                let (start, count)''','''                let normalized = gpu.stream.clone_dtoh(&gpu.d_mw_normalized).unwrap();
                let compact_slots = gpu.stream.clone_dtoh(&gpu.d_mw_compact).unwrap();
                let (start, count)''')
gpu=rep(gpu,'''                        assert_eq!(normalized[slot * NUM_CLASSES + h].to_bits(), expected.to_bits(),''','''                        let storage_slot = if gpu.use_mw_compact != 0 { compact_slots[p * gpu.mw_union_slots as usize + slot] as usize } else { slot };
                        assert_eq!(normalized[storage_slot * NUM_CLASSES + h].to_bits(), expected.to_bits(),''')
if 'fn coupled_minimum_budget_direct_and_normalized_paths_match' in gpu:
    a=gpu.index('    fn coupled_minimum_budget_direct_and_normalized_paths_match')
    b=gpu.index('\n    #[test]',a)
    boundary=gpu[a:b]
    boundary=rep(boundary,'''            let slots = mw.blocks.len();
            if slots < 3000''','''            let compact = MultiwayCompactPlan::build(&mw, s.n).unwrap();
            let slots = compact.capacity;
            if slots < 3000''')
    boundary=rep(boundary,'let fixed = mw.metadata_bytes() + terms * 8 + slots * 4',
        'let fixed = mw.metadata_bytes() + terms * 8 + mw.blocks.len() * 4 + compact.bytes')
    gpu=gpu[:a]+boundary+gpu[b:]

cu=rep(cu,'const u32* __restrict__ active, int gate, float* normalized)','const u32* __restrict__ active, int gate, int compact, float* normalized)')
cu=rep(cu,'normalized[(size_t)slot * NC + h] = reach','normalized[(size_t)(compact ? blockIdx.x : slot) * NC + h] = reach')
# Both CDF entry points retain their own arithmetic and receive the same uniform layout flag.
assert cu.count('const u32* __restrict__ active, int gate,\n    float* cdf')==2
cu=cu.replace('const u32* __restrict__ active, int gate,\n    float* cdf','const u32* __restrict__ active, int gate, int compact,\n    float* cdf')
assert cu.count('size_t base = ((size_t)slot * batch_capacity + local) * (NC + 1);')==2
cu=cu.replace('size_t base = ((size_t)slot * batch_capacity + local) * (NC + 1);','size_t base = ((size_t)(compact ? blockIdx.x : slot) * batch_capacity + local) * (NC + 1);')
cu=rep(cu,'? normalized[(size_t)slot * NC + order[(size_t)particle * NC + index]] : 0.f;',
    '? normalized[(size_t)(compact ? blockIdx.x : slot) * NC + order[(size_t)particle * NC + index]] : 0.f;')
cu=rep(cu,'''    const u32* __restrict__ slots, const float* __restrict__ cdf,
    const u32* __restrict__ lower''','''    const u32* __restrict__ slots, const u32* __restrict__ compact_slots,
    u32 union_slots, int compact, const float* __restrict__ cdf,
    const u32* __restrict__ lower''')
cu=rep(cu,'                opponent_slots[nopponents++] = slots[source];','''                u32 global_slot = slots[source];
                opponent_slots[nopponents++] = compact
                    ? compact_slots[(size_t)p * union_slots + global_slot] : global_slot;''')

tests=(out/'tests.rs').read_text(encoding='utf-8')
gpu_tests=rep(gpu,'    #[test]\n    fn coupled_terminal_matches_cpu_across_particle_batches() {',tests+'\n    #[test]\n    fn coupled_terminal_matches_cpu_across_particle_batches() {')
def diff(a,b,name):
    return ''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/crates/solver/src/preflop/'+name,tofile='b/crates/solver/src/preflop/'+name))
(out/'implementation.patch').write_bytes((diff(original['gpu.rs'],gpu,'gpu.rs')+diff(original['kernels.cu'],cu,'kernels.cu')).encode())
(out/'tests.patch').write_bytes(diff(gpu,gpu_tests,'gpu.rs').encode())
(out/'combined.patch').write_bytes((diff(original['gpu.rs'],gpu_tests,'gpu.rs')+diff(original['kernels.cu'],cu,'kernels.cu')).encode())
(out/'gpu.rs').write_bytes(gpu_tests.replace('\n','\r\n').encode('utf-8'))
(out/'kernels.cu').write_bytes(cu.replace('\n','\r\n').encode('utf-8'))
(out/'baseline-sha256.json').write_text(json.dumps({n:hashlib.sha256((src/n).read_bytes()).hexdigest() for n in original},indent=2),encoding='utf-8')
print('Compact slot implementation/test proposal generated; no source edits.')
