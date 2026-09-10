from pathlib import Path
import difflib
import hashlib
import json

root = Path(r'T:\Dev\GTOpen')
out = Path(__file__).parent
src = root / 'crates/solver/src/preflop'
original = {name: (src / name).read_text(encoding='utf-8') for name in ['gpu.rs', 'kernels.cu']}
gpu, cu = original['gpu.rs'], original['kernels.cu']

def replace(text, old, new):
    assert text.count(old) == 1, (old[:100], text.count(old))
    return text.replace(old, new)

gpu = replace(gpu, '    f_multiway_cdf: CudaFunction,', '''    f_multiway_cdf: CudaFunction,
    f_multiway_clear_active: CudaFunction,
    f_multiway_prepare: CudaFunction,''')
gpu = replace(gpu, '    d_mw_terms: CudaSlice<u32>,', '''    d_mw_terms: CudaSlice<u32>,
    // One flag per CDF slot and one counterfactual probability per terminal.
    // Rebuilt on device for every traverser, including average/BR evaluation.
    d_mw_active: CudaSlice<u32>,
    d_mw_prob: CudaSlice<f32>,''')
gpu = replace(gpu, '            + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4 + s.nodes.len() * 4',
    '            + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4 + s.nodes.len() * 8\n            + mw.blocks.len() * 4')
gpu = replace(gpu, '            let fixed = mw_plan.metadata_bytes() + mw_terms.len() * 4',
    '            let fixed = mw_plan.metadata_bytes() + mw_terms.len() * 8 + mw_plan.blocks.len() * 4')
gpu = replace(gpu, '            f_multiway_cdf: func("pf_multiway_cdf")?,', '''            f_multiway_cdf: func("pf_multiway_cdf")?,
            f_multiway_clear_active: func("pf_multiway_clear_active")?,
            f_multiway_prepare: func("pf_multiway_prepare")?,''')
gpu = replace(gpu, '            mw_spans: mw_plan.spans,', '''            d_mw_active: stream.alloc_zeros::<u32>(mw_plan.blocks.len()).map_err(e)?,
            d_mw_prob: stream.alloc_zeros::<f32>(mw_terms.len().max(1)).map_err(e)?,
            mw_spans: mw_plan.spans,''')
gpu = replace(gpu, '''            if work_count > 0 {
                let samples = super::multiway::SAMPLES as u32;''', '''            if work_count > 0 {
                let slot_count = self.d_mw_active.len() as u32;
                unsafe {
                    // Fixed grid bounds and device-only state keep graph replay valid.
                    self.stream.launch_builder(&self.f_multiway_clear_active)
                        .arg(&mut self.d_mw_active).arg(&slot_count)
                        .launch(LaunchConfig { grid_dim: (slot_count.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                    self.stream.launch_builder(&self.f_multiway_prepare)
                        .arg(&self.d_mw_terms).arg(&self.mw_nterms).arg(&p).arg(&self.np)
                        .arg(&self.d_live).arg(&self.d_reach_src).arg(&self.d_reach_mass)
                        .arg(&self.d_mw_slots).arg(&mut self.d_mw_active).arg(&mut self.d_mw_prob)
                        .launch(LaunchConfig { grid_dim: (self.mw_nterms.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                }
                let samples = super::multiway::SAMPLES as u32;''')
gpu = replace(gpu, '                            .arg(&self.d_mw_order).arg(&self.d_reach).arg(&self.d_reach_mass)',
    '                            .arg(&self.d_mw_order).arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active)')
gpu = replace(gpu, '                            .arg(&self.d_reach_src).arg(&self.d_reach_mass)',
    '                            .arg(&self.d_reach_src).arg(&self.d_mw_prob)')

marker = '// Inclusive scan in particle rank order, cached as an exclusive 170-entry'
cu = replace(cu, marker, '''// Reset the scratch before each traverser. No host readback or dynamic launch.
extern "C" __global__ void pf_multiway_clear_active(u32* active, u32 count)
{
    u32 slot = blockIdx.x * blockDim.x + threadIdx.x;
    if (slot < count) active[slot] = 0;
}

// Counterfactual probability excludes p, but includes folded opponents.
// Zero own reach MUST NOT prune a counterfactual value/regret update.
extern "C" __global__ void pf_multiway_prepare(
    const u32* __restrict__ terms, u32 count, int p, int np,
    const int* __restrict__ live, const u32* __restrict__ reach_src,
    const float* __restrict__ reach_mass, const u32* __restrict__ slots,
    u32* active, float* terminal_prob)
{
    u32 index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= count) return;
    u32 nd = terms[index];
    int lv = live[nd];
    if (!((lv >> p) & 1)) { terminal_prob[index] = 0.f; return; }
    float prob = 1.f;
    // Identical order and float arithmetic to the former per-batch calculation.
    for (int q = 0; q < np; q++) {
        if (q == p) continue;
        u32 source = reach_src[(size_t)nd * np + q];
        prob *= reach_mass[source];
    }
    terminal_prob[index] = prob;
    if (prob <= 0.f) return;
    for (int q = 0; q < np; q++) {
        if (q == p || !((lv >> q) & 1)) continue;
        u32 source = reach_src[(size_t)nd * np + q];
        // Multiple terminals may need a slot. Atomic writes avoid a data race.
        atomicExch(active + slots[source], 1u);
    }
}

''' + marker)
cu = replace(cu, '''    const float* __restrict__ reach, const float* __restrict__ mass,
    float* cdf, u32 sample_start''', '''    const float* __restrict__ reach, const float* __restrict__ mass,
    const u32* __restrict__ active,
    float* cdf, u32 sample_start''')
cu = replace(cu, '''    u32 slot = work[start + blockIdx.x];
    u32 block = blocks[slot];
    u32 local = blockIdx.y * 4''', '''    u32 slot = work[start + blockIdx.x];
    if (!active[slot]) return;
    u32 block = blocks[slot];
    u32 local = blockIdx.y * 4''')
cu = replace(cu, '''    const float* __restrict__ reach_mass,
    const u32* __restrict__ slots, const float* __restrict__ cdf,
    const u32* __restrict__ lower''', '''    const float* __restrict__ terminal_prob,
    const u32* __restrict__ slots, const float* __restrict__ cdf,
    const u32* __restrict__ lower''')
cu = replace(cu, '''        prob = 1.f;
        nopponents = 0;
        for (int q = 0; q < np; q++) {
            if (q == p) continue;
            u32 source = reach_src[(size_t)nd * np + q];
            prob *= reach_mass[source];
            if ((lv >> q) & 1) opponent_slots[nopponents++] = slots[source];
        }''', '''        prob = terminal_prob[blockIdx.x];
        nopponents = 0;
        if (!(prob <= 0.f)) {
            for (int q = 0; q < np; q++) {
                if (q == p || !((lv >> q) & 1)) continue;
                u32 source = reach_src[(size_t)nd * np + q];
                opponent_slots[nopponents++] = slots[source];
            }
        }''')

patch = []
for name, changed in [('gpu.rs', gpu), ('kernels.cu', cu)]:
    (out / name).write_bytes(changed.replace('\n', '\r\n').encode('utf-8'))
    patch.extend(difflib.unified_diff(original[name].splitlines(True), changed.splitlines(True),
        fromfile='a/crates/solver/src/preflop/' + name,
        tofile='b/crates/solver/src/preflop/' + name))
(out / 'active-slots.patch').write_bytes(''.join(patch).encode('utf-8'))
(out / 'baseline-sha256.json').write_text(json.dumps({name: hashlib.sha256((src/name).read_bytes()).hexdigest() for name in original}, indent=2), encoding='utf-8')
print('Proposal generated; production sources not modified.')
