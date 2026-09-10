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
    assert text.count(old) == 1, (old[:80], text.count(old))
    return text.replace(old, new)

gpu = replace(gpu, '    d_mw_normalized: CudaSlice<f32>,', '    d_mw_normalized: CudaSlice<f32>,\n    use_mw_normalized: bool,')
anchor = '/// Preferred VRAM including the exact-equity cache, in MB.'
planner = '''// Pure byte-budget planner; no CUDA context or allocation is needed to test
// the boundary. Optional normalization must not remove the one-particle path.
#[derive(Debug, PartialEq, Eq)]
struct MultiwayBatchPlan {
    batch: usize,
    cache_len: usize,
    normalized_bytes: usize,
}
fn multiway_batch_plan(available_bytes: usize, slots: usize) -> Result<Option<MultiwayBatchPlan>, String> {
    if slots == 0 { return Err("multiway cache requires at least one slot".into()); }
    let one_particle = slots.checked_mul((NUM_CLASSES + 1) * 4)
        .ok_or_else(|| "multiway CDF scratch size overflow".to_string())?;
    if available_bytes < one_particle { return Ok(None); }
    let preferred_normalized = slots.checked_mul(NUM_CLASSES * 4)
        .ok_or_else(|| "multiway normalized reach size overflow".to_string())?;
    // Retain the preferred normalized path even if direct division could fit
    // a larger batch. Fall back only if normalized+one particle cannot fit.
    let normalized_bytes = if available_bytes - one_particle >= preferred_normalized {
        preferred_normalized
    } else { 0 };
    let batch = ((available_bytes - normalized_bytes) / one_particle)
        .min(32).min(super::multiway::SAMPLES);
    let cache_len = slots.checked_mul(NUM_CLASSES + 1)
        .and_then(|n| n.checked_mul(batch))
        .ok_or_else(|| "multiway CDF scratch size overflow".to_string())?;
    Ok(Some(MultiwayBatchPlan { batch, cache_len, normalized_bytes }))
}

'''
gpu = replace(gpu, anchor, planner + anchor)
start = gpu.index('        let mut mw_normalized_len = 1usize;')
end = gpu.index('        } else {\n            mw_plan = EquityCachePlan::disabled(np);', start)
gpu = gpu[:start] + '''        let mut mw_normalized_len = 1usize;
        let mut use_mw_normalized = false;
        if use_multiway {
            let fixed = mw_plan.metadata_bytes() + mw_terms.len() * 8 + mw_plan.blocks.len() * 4
                + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4;
            let remaining = (budget_mb as f64 * 1e6 - need * 1e6 - fixed as f64).max(0.0) as usize;
            let Some(plan) = multiway_batch_plan(remaining, mw_plan.blocks.len())? else {
                let one_particle = mw_plan.blocks.len() * (NUM_CLASSES + 1) * 4;
                return Err(format!("coupled multiway model needs at least ~{:.0} MB VRAM (budget {budget_mb} MB); solving the same model on CPU",
                    need + (fixed + one_particle) as f64 / 1e6));
            };
            mw_batch = plan.batch;
            mw_cache_len = plan.cache_len;
            use_mw_normalized = plan.normalized_bytes != 0;
            mw_normalized_len = (plan.normalized_bytes / 4).max(1);
            need += (fixed + plan.normalized_bytes + mw_cache_len * 4) as f64 / 1e6;
''' + gpu[end:]
gpu = replace(gpu, '            f_multiway_cdf: func("pf_multiway_cdf")?,', '''            f_multiway_cdf: func(if use_mw_normalized { "pf_multiway_cdf" } else { "pf_multiway_cdf_direct" })?,''')
gpu = replace(gpu, '            d_mw_normalized: stream.alloc_zeros::<f32>(mw_normalized_len).map_err(e)?,', '''            d_mw_normalized: stream.alloc_zeros::<f32>(mw_normalized_len).map_err(e)?,
            use_mw_normalized,''')
gpu = replace(gpu, '''                    self.stream.launch_builder(&self.f_multiway_normalize)
                        .arg(&self.d_mw_work).arg(&work_start).arg(&self.d_mw_blocks)
                        .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)
                        .arg(&mut self.d_mw_normalized)
                        .launch(LaunchConfig { grid_dim: (work_count, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;''', '''                    if self.use_mw_normalized {
                        self.stream.launch_builder(&self.f_multiway_normalize)
                            .arg(&self.d_mw_work).arg(&work_start).arg(&self.d_mw_blocks)
                            .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)
                            .arg(&mut self.d_mw_normalized)
                            .launch(LaunchConfig { grid_dim: (work_count, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                    }''')
gpu = replace(gpu, '                            .arg(&self.d_mw_order).arg(&self.d_mw_normalized).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)', '''                            .arg(&self.d_mw_order)
                            .arg(if self.use_mw_normalized { &self.d_mw_normalized } else { &self.d_reach })
                            .arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate)''')
gpu = replace(gpu, '''                super::multiway::SAMPLES, mw_plan.blocks.len(), mw_batch, mw_cache_len as f64 * 4.0 / 1e6);
        }''', '''                super::multiway::SAMPLES, mw_plan.blocks.len(), mw_batch, mw_cache_len as f64 * 4.0 / 1e6);
            if !use_mw_normalized {
                println!("preflop gpu: direct CDF normalization to preserve minimum-VRAM fit");
            }
        }''')

start = cu.index('extern "C" __global__ void pf_multiway_cdf(')
end = cu.index('\n// Five-point Gauss-Legendre integration', start)
direct = cu[start:end].replace('pf_multiway_cdf(', 'pf_multiway_cdf_direct(')
direct = direct.replace('const float* __restrict__ normalized,', 'const float* __restrict__ reach,')
direct = direct.replace('? normalized[(size_t)slot * NC + order[(size_t)particle * NC + index]] : 0.f;',
    '? reach[(size_t)block * NC + order[(size_t)particle * NC + index]] / mass[block] : 0.f;')
cu = cu[:end] + '''
// Memory-constrained fallback. Keep a separate entry point so the preferred
// normalized kernel pays no runtime branch/register cost for the fallback.
''' + direct + cu[end:]

tests = (out / 'tests.rs').read_text(encoding='utf-8')
test_anchor = '    #[test]\n    fn coupled_terminal_matches_cpu_across_particle_batches() {'
with_tests = replace(gpu, test_anchor, tests + '\n' + test_anchor)
def make_patch(a, b, name):
    return ''.join(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
        fromfile='a/crates/solver/src/preflop/' + name,
        tofile='b/crates/solver/src/preflop/' + name))
implementation = make_patch(original['gpu.rs'], gpu, 'gpu.rs') + make_patch(original['kernels.cu'], cu, 'kernels.cu')
test_patch = make_patch(gpu, with_tests, 'gpu.rs')
(out / 'fallback.patch').write_bytes(implementation.encode('utf-8'))
(out / 'tests.patch').write_bytes(test_patch.encode('utf-8'))
(out / 'combined.patch').write_bytes((make_patch(original['gpu.rs'], with_tests, 'gpu.rs') + make_patch(original['kernels.cu'], cu, 'kernels.cu')).encode('utf-8'))
(out / 'gpu.rs').write_bytes(with_tests.replace('\n', '\r\n').encode('utf-8'))
(out / 'kernels.cu').write_bytes(cu.replace('\n', '\r\n').encode('utf-8'))
(out / 'baseline-sha256.json').write_text(json.dumps({name: hashlib.sha256((src/name).read_bytes()).hexdigest() for name in original}, indent=2), encoding='utf-8')
print('Optional normalization fallback generated; no source edits.')
