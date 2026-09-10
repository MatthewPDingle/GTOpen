from pathlib import Path
import subprocess
import difflib
import hashlib
import json

out = Path(__file__).parent
repo = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
baseline = '1b8fc3f04fe2bc3c000346368f8da346738d1c45'
gpu_path = 'crates/solver/src/preflop/gpu.rs'
kernel_path = 'crates/solver/src/preflop/kernels.cu'
original_raw = subprocess.check_output(['git', 'show', f'{baseline}:{gpu_path}'], cwd=repo)
kernel_raw = subprocess.check_output(['git', 'show', f'{baseline}:{kernel_path}'], cwd=repo)
current_raw = (repo / gpu_path).read_bytes()
old = original_raw.decode('utf-8').replace('\r\n', '\n')
current = current_raw.decode('utf-8').replace('\r\n', '\n')
helper_start = current.index('// Include the one-float placeholder allocated when no policies are forced.\n')
helper_end = current.index('/// Preferred VRAM including the exact-equity cache, in MB.', helper_start)
helpers = current[helper_start:helper_end]
for name in ['forced_storage_bytes', 'forced_policy_elements', 'reserve_forced_vram_mb']:
    assert f'fn {name}(' in helpers
anchor = '/// Preferred VRAM including the exact-equity cache, in MB.'
assert old.count(anchor) == 1
fixed = old.replace(anchor, helpers + anchor)
before = '''    minimum_vram_mb(s, ValuePlan::build(s).blocks)
        + (EquityCachePlan::build(s, &sources).bytes() + mw_bytes) as f64 / 1e6'''
after = '''    let forced_bytes = match forced_policy_elements(s).and_then(forced_storage_bytes) {
        Ok(bytes) => bytes,
        Err(_) => return f64::INFINITY,
    };
    minimum_vram_mb(s, ValuePlan::build(s).blocks)
        + (EquityCachePlan::build(s, &sources).bytes() + mw_bytes + forced_bytes) as f64 / 1e6'''
assert fixed.count(before) == 1
fixed = fixed.replace(before, after)
reserve_anchor = '        let static_seats: Vec<bool> = (0..np).map(|p| s.seat_static(p)).collect();'
assert fixed.count(reserve_anchor) == 1
reserve = '''        // Reserve actual forced allocation before CDF and optional caches,
        // including the legacy path without CDF storage.
        need = reserve_forced_vram_mb(need, forced.len(), budget_mb)?;
'''
fixed = fixed.replace(reserve_anchor, reserve + reserve_anchor)
diag = '''        if std::env::var("PREFLOP_GPU_LAYOUT_STATS").as_deref() == Ok("1") {
            println!("preflop gpu layout: {}", serde_json::json!({
                "baseline": "1b8fc3f_forced_budget_only",
                "model": s.multiway_equity_model(), "nodes": n, "seats": np,
                "budget_mb": budget_mb, "planned_need_mb": need,
                "forced_nodes": n_forced, "frozen_nodes": n_frozen,
                "forced_elements": forced.len(), "forced_bytes": forced_storage_bytes(forced.len())?,
                "multiway_enabled": use_multiway, "multiway_batch": mw_batch,
                "multiway_particles": super::multiway::SAMPLES,
                "cdf_slots": if use_multiway { mw_plan.blocks.len() } else { 0 },
                "cdf_allocated_bytes": mw_cache_len * std::mem::size_of::<f32>(),
                "compact_cdf": false, "normalized_cdf": false,
                "hu_equity_cache_enabled": use_eq_cache,
                "hu_equity_cache_slots": if use_eq_cache { eq_plan.blocks.len() } else { 0 },
                "hu_equity_cache_allocated_bytes": eq_cache_len * std::mem::size_of::<f32>(),
            }));
        }

'''
diag_anchor = '        Ok(PreflopGpu {\n'
assert fixed.count(diag_anchor) == 1
instrumented = fixed.replace(diag_anchor, diag + diag_anchor)
def patch(a, b, name):
    value = ''.join(difflib.unified_diff(a.splitlines(True), b.splitlines(True),
        fromfile=f'a/{gpu_path}', tofile=f'b/{gpu_path}'))
    (out / name).write_text(value, encoding='utf-8', newline='\n')
patch(old, fixed, 'forced-budget-only.patch')
patch(fixed, instrumented, 'layout-diagnostic.patch')
patch(old, instrumented, 'combined.patch')
(out / 'gpu.rs').write_text(instrumented, encoding='utf-8', newline='\n')
(out / 'gpu-budget-only.rs').write_text(fixed, encoding='utf-8', newline='\n')
(out / 'kernels.cu').write_bytes(kernel_raw)

# Ensure the policy construction and all code after GPU field initialization
# are precisely baseline text, apart from the documented accounting/diagnostic.
policy_start = '        // seat modes and locks, resolved on the host exactly as the CPU'
policy_end = '        let static_seats: Vec<bool>'
assert instrumented[instrumented.index(policy_start):instrumented.index(policy_end)].replace(reserve, '') == old[old.index(policy_start):old.index(policy_end)]
tail = '        Ok(PreflopGpu {\n'
assert instrumented[instrumented.index(tail):] == old[old.index(tail):]
assert (repo / gpu_path).read_bytes() == current_raw, 'Active source changed; regenerate the helper snapshot.'
manifest = {
    'baseline_commit': baseline,
    'helper_source_sha256': hashlib.sha256(current_raw).hexdigest(),
    'original_gpu_sha256': hashlib.sha256(original_raw).hexdigest(),
    'original_kernel_sha256': hashlib.sha256(kernel_raw).hexdigest(),
    'files': {name: hashlib.sha256((out / name).read_bytes()).hexdigest()
              for name in ['gpu.rs', 'gpu-budget-only.rs', 'kernels.cu', 'combined.patch', 'forced-budget-only.patch', 'layout-diagnostic.patch']},
    'verified': ['Original kernels preserved byte-for-byte',
                 'Forced-policy construction unchanged apart from accounting reserve',
                 'All GPU allocations/launch methods/tests after initialization expression remain original',
                 'No active source edits, builds or hardware jobs'],
}
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
print('Original GPU baseline plus forced-budget-only correction prepared; active source untouched.')
