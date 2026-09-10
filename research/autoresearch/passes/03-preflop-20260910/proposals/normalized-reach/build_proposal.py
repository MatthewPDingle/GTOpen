from pathlib import Path
import difflib
import hashlib
import json

root = Path(r'T:\Dev\GTOpen')
src = root / 'target/autoresearch/preflop-20260910/crates/solver/src/preflop'
out = Path(__file__).parent
original = {name: (src / name).read_text(encoding='utf-8') for name in ['gpu.rs', 'kernels.cu']}
gpu, cu = original['gpu.rs'], original['kernels.cu']

def replace(text, old, new):
    assert text.count(old) == 1, (old[:100], text.count(old))
    return text.replace(old, new)

gpu = replace(gpu, '    f_multiway_cdf: CudaFunction,', '    f_multiway_cdf: CudaFunction,\n    f_multiway_normalize: CudaFunction,')
gpu = replace(gpu, '    d_mw_cdf: CudaSlice<f32>,', '''    d_mw_cdf: CudaSlice<f32>,
    // One f32 division per needed slot/hand per traverser, reused by all particles.
    d_mw_normalized: CudaSlice<f32>,''')
gpu = replace(gpu, '            + mw.blocks.len() * 4', '            + mw.blocks.len() * (NUM_CLASSES + 1) * 4')
gpu = replace(gpu, '''        let mut mw_cache_len = 1usize;
        if use_multiway {
            let fixed = mw_plan.metadata_bytes() + mw_terms.len() * 8 + mw_plan.blocks.len() * 4''', '''        let mut mw_cache_len = 1usize;
        let mut mw_normalized_len = 1usize;
        if use_multiway {
            mw_normalized_len = mw_plan.blocks.len().checked_mul(NUM_CLASSES)
                .ok_or_else(|| "multiway normalized reach size overflow".to_string())?;
            let normalized_bytes = mw_normalized_len.checked_mul(4)
                .ok_or_else(|| "multiway normalized reach size overflow".to_string())?;
            // Reserve normalized distributions before selecting particle batch size.
            let fixed = mw_plan.metadata_bytes() + mw_terms.len() * 8 + mw_plan.blocks.len() * 4 + normalized_bytes''')
gpu = replace(gpu, '            f_multiway_cdf: func("pf_multiway_cdf")?,', '            f_multiway_cdf: func("pf_multiway_cdf")?,\n            f_multiway_normalize: func("pf_multiway_normalize")?,')
gpu = replace(gpu, '            d_mw_cdf: stream.alloc_zeros::<f32>(mw_cache_len).map_err(e)?,', '''            d_mw_cdf: stream.alloc_zeros::<f32>(mw_cache_len).map_err(e)?,
            d_mw_normalized: stream.alloc_zeros::<f32>(mw_normalized_len).map_err(e)?,''')
gpu = replace(gpu, '''                        .launch(LaunchConfig { grid_dim: (self.mw_nterms.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                }
                let samples''', '''                        .launch(LaunchConfig { grid_dim: (self.mw_nterms.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                    // Rebuild for every terminals call, even when evaluation disables
                    // active gating. Test/manual reach replacement must not reuse stale data.
                    self.stream.launch_builder(&self.f_multiway_normalize)
                        .arg(&self.d_mw_work).arg(&work_start).arg(&self.d_mw_blocks)
                        .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)
                        .arg(&mut self.d_mw_normalized)
                        .launch(LaunchConfig { grid_dim: (work_count, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                }
                let samples''')
gpu = replace(gpu, '                            .arg(&self.d_mw_order).arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)',
    '                            .arg(&self.d_mw_order).arg(&self.d_mw_normalized).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)')

marker = '// Inclusive scan in particle rank order, cached as an exclusive 170-entry'
cu = replace(cu, marker, '''// Keep the original f32 division, but perform it once per needed reach/hand
// rather than once per particle. No approximate reciprocal or fast-divide intrinsic.
extern "C" __global__ void pf_multiway_normalize(
    const u32* __restrict__ work, u32 start, const u32* __restrict__ blocks,
    const float* __restrict__ reach, const float* __restrict__ mass,
    const u32* __restrict__ active, int gate, float* normalized)
{
    u32 slot = work[start + blockIdx.x];
    if (gate && !active[slot]) return;
    u32 block = blocks[slot];
    if (mass[block] <= 0.f) return;
    for (u32 h = threadIdx.x; h < NC; h += blockDim.x) {
        normalized[(size_t)slot * NC + h] = reach[(size_t)block * NC + h] / mass[block];
    }
}

''' + marker)
cu = replace(cu, '''    const u32* __restrict__ blocks, const u32* __restrict__ order,
    const float* __restrict__ reach, const float* __restrict__ mass,''', '''    const u32* __restrict__ blocks, const u32* __restrict__ order,
    const float* __restrict__ normalized, const float* __restrict__ mass,''')
cu = replace(cu, '            ? reach[(size_t)block * NC + order[(size_t)particle * NC + index]] / mass[block] : 0.f;',
    '            ? normalized[(size_t)slot * NC + order[(size_t)particle * NC + index]] : 0.f;')

patch = []
for name, changed in [('gpu.rs', gpu), ('kernels.cu', cu)]:
    (out / name).write_bytes(changed.replace('\n', '\r\n').encode('utf-8'))
    patch.extend(difflib.unified_diff(original[name].splitlines(True), changed.splitlines(True),
        fromfile='a/crates/solver/src/preflop/' + name,
        tofile='b/crates/solver/src/preflop/' + name))
(out / 'normalized-reach.patch').write_bytes(''.join(patch).encode('utf-8'))
(out / 'baseline-sha256.json').write_text(json.dumps({name: hashlib.sha256((src/name).read_bytes()).hexdigest() for name in original}, indent=2), encoding='utf-8')
print('Normalized reach proposal generated from3295571 checkout; no source edits.')
