from pathlib import Path
import subprocess,difflib
p=Path(__file__).parent
root=Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
rg='crates/solver/src/preflop/gpu.rs';rk='crates/solver/src/preflop/kernels.cu'
old=(p.parent/'compatibility-batch/gpu.rs').read_text(encoding='utf-8-sig')
kold=subprocess.check_output(['git','show','739c68d:'+rk],cwd=root).decode().replace('\r\n','\n')
s=old

def replace(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b)
replace('    use_mw_normalized: bool,','    use_mw_normalized: bool,\n    use_mw_prepared: bool,')
replace('struct CompatibleMultiwayPlan {\n    storage: MultiwayBatchPlan,','struct CompatibleMultiwayPlan {\n    storage: MultiwayBatchPlan,\n    minimal_metadata: bool,')
replace('CompatibleMultiwayPlan { storage, reference: None }','CompatibleMultiwayPlan { storage, reference: None, minimal_metadata: false }')
replace('''        return Err(format!("optimized multiway metadata cannot retain original {}-particle grouping and HU-cache={} within {budget_mb} MB; compatibility layout unsupported, solving on CPU",
            target.batch, target.use_eq_cache));''','''        return original_layout_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
            union_slots, eq_cache_bytes, reference);''')
replace('''        return Err("reference multiway grouping/cache does not fit the optimized physical allocation".into());''','''        return original_layout_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
            union_slots, eq_cache_bytes, reference);''')
replace('''        storage: MultiwayBatchPlan { batch: target.batch, cache_len, normalized_bytes }, reference,''','''        storage: MultiwayBatchPlan { batch: target.batch, cache_len, normalized_bytes }, reference,
        minimal_metadata: false,''')
marker='// Include the one-float placeholder allocated when no policies are forced.'
helper='''// Exact original union/direct layout: no active flags, probability table,
// normalized reaches or compact map. Preserve reference batch AND HU cache.
fn original_layout_multiway_plan(
    budget_mb: u64, base_mb: f64, reference_fixed_bytes: usize, union_slots: usize,
    eq_cache_bytes: usize, reference: Option<ReferenceMultiwayPlan>,
) -> Result<Option<CompatibleMultiwayPlan>, String> {
    let Some(target) = reference else { return Ok(None); };
    let cache_len = union_slots.checked_mul(NUM_CLASSES + 1)
        .and_then(|n|n.checked_mul(target.batch)).ok_or_else(|| "original CDF allocation overflow".to_string())?;
    let bytes = cache_len.checked_mul(4).and_then(|n|n.checked_add(reference_fixed_bytes))
        .ok_or_else(|| "original total allocation overflow".to_string())?;
    let need = base_mb + bytes as f64 / 1e6
        + if target.use_eq_cache {eq_cache_bytes as f64 / 1e6} else {0.0};
    if need > budget_mb as f64 { return Err("original compatibility layout exceeds its supplied budget".into()); }
    Ok(Some(CompatibleMultiwayPlan {
        storage: MultiwayBatchPlan {batch:target.batch,cache_len,normalized_bytes:0},
        reference:Some(target),minimal_metadata:true,
    }))
}

'''
replace(marker,helper+marker)
replace('''    fn new_with_layout(s: &PreflopSolver, budget_mb: u64, allow_compact: bool) -> Result<Self, String> {''','''    fn new_with_layout(s: &PreflopSolver, budget_mb: u64, allow_compact: bool) -> Result<Self, String> {
        Self::new_with_layout_mode(s, budget_mb, allow_compact, false)
    }

    // The true value is used only by internal parity tests. Public construction
    // selects minimal metadata solely when the normal compatible plan needs it.
    fn new_with_layout_mode(s: &PreflopSolver, budget_mb: u64, allow_compact: bool, force_minimal: bool) -> Result<Self, String> {''')
replace('''        let compact = if use_multiway && allow_compact {''','''        let mut compact = if use_multiway && allow_compact {''')
replace('''        let mut use_mw_normalized = false;
        let mut mw_reference = None;''','''        let mut use_mw_normalized = false;
        let mut use_mw_prepared = true;
        let mut mw_reference = None;''')
replace('''            let fixed = mw_plan.metadata_bytes() + mw_terms.len() * 8 + mw_plan.blocks.len() * 4''','''            let mut fixed = mw_plan.metadata_bytes() + mw_terms.len() * 8 + mw_plan.blocks.len() * 4''')
replace('''            let Some(selected) = compatible_multiway_plan(budget_mb, need, reference_fixed,
                fixed, mw_plan.blocks.len(), compact.capacity, eq_plan.bytes(), !eq_plan.blocks.is_empty())? else {''','''            let selected = if force_minimal {
                let reference = reference_multiway_plan(budget_mb, need, reference_fixed,
                    mw_plan.blocks.len(), eq_plan.bytes(), !eq_plan.blocks.is_empty())?;
                original_layout_multiway_plan(budget_mb, need, reference_fixed,
                    mw_plan.blocks.len(), eq_plan.bytes(), reference)?
            } else {
                compatible_multiway_plan(budget_mb, need, reference_fixed,
                    fixed, mw_plan.blocks.len(), compact.capacity, eq_plan.bytes(), !eq_plan.blocks.is_empty())?
            };
            let Some(selected) = selected else {''')
replace('''            mw_reference = selected.reference;
            let plan = selected.storage;''','''            use_mw_prepared = !selected.minimal_metadata;
            if selected.minimal_metadata {
                compact = MultiwayCompactPlan::union(mw_plan.blocks.len());
                fixed = reference_fixed;
            }
            mw_reference = selected.reference;
            let plan = selected.storage;''')
replace('''            if !use_mw_normalized {
                println!("preflop gpu: direct CDF normalization to preserve reference grouping or minimum-VRAM fit");
            }''','''            if !use_mw_normalized {
                println!("preflop gpu: direct CDF normalization to preserve reference grouping or minimum-VRAM fit");
            }
            if !use_mw_prepared {
                println!("preflop gpu: original union/direct metadata fallback, no active/probability scratch");
            }''')
replace('''                "compact_cdf": compact.enabled, "normalized_cdf": use_mw_normalized,''','''                "compact_cdf": compact.enabled, "normalized_cdf": use_mw_normalized,
                "minimal_multiway_metadata": use_multiway && !use_mw_prepared,''')
replace('''            f_multiway_terminal: func("pf_multiway_terminal")?,''','''            f_multiway_terminal: func(if use_mw_prepared { "pf_multiway_terminal" } else { "pf_multiway_terminal_minimal" })?,''')
replace('''            d_mw_normalized: stream.alloc_zeros::<f32>(mw_normalized_len).map_err(e)?,
            use_mw_normalized,''','''            d_mw_normalized: if use_mw_prepared { stream.alloc_zeros::<f32>(mw_normalized_len).map_err(e)? } else { stream.null::<f32>().map_err(e)? },
            use_mw_normalized,
            use_mw_prepared,''')
replace('''            d_mw_compact: stream.clone_htod(&compact.map).map_err(e)?,''','''            d_mw_compact: if use_mw_prepared { stream.clone_htod(&compact.map).map_err(e)? } else { stream.null::<u32>().map_err(e)? },''')
replace('''            d_mw_active: stream.alloc_zeros::<u32>(mw_plan.blocks.len()).map_err(e)?,
            d_mw_prob: stream.alloc_zeros::<f32>(mw_terms.len().max(1)).map_err(e)?,''','''            d_mw_active: if use_mw_prepared { stream.alloc_zeros::<u32>(mw_plan.blocks.len()).map_err(e)? } else { stream.null::<u32>().map_err(e)? },
            d_mw_prob: if use_mw_prepared { stream.alloc_zeros::<f32>(mw_terms.len().max(1)).map_err(e)? } else { stream.null::<f32>().map_err(e)? },''')
replace('''                let slot_count = self.d_mw_active.len() as u32;
                unsafe {''','''                // Minimal metadata has neither active flags nor prepared probabilities.
                // Force gate=0 so direct CDF never reads the null active pointer.
                let gate = if self.use_mw_prepared {gate} else {0};
                let slot_count = self.d_mw_active.len() as u32;
                unsafe {''')
replace('''                    // Fixed grid bounds and device-only state keep graph replay valid.
                    if gate != 0 {''','''                    // Fixed grid bounds and device-only state keep graph replay valid.
                    if self.use_mw_prepared {
                    if gate != 0 {''')
replace('''                        .launch(LaunchConfig { grid_dim: (self.mw_nterms.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                    // Rebuild for every terminals call''','''                        .launch(LaunchConfig { grid_dim: (self.mw_nterms.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                    }
                    // Rebuild for every terminals call''')
replace('''                            .arg(&self.d_reach_src).arg(&self.d_mw_prob)''','''                            .arg(&self.d_reach_src).arg(if self.use_mw_prepared { &self.d_mw_prob } else { &self.d_reach_mass })''')
replace('''        assert!(compatible_multiway_plan(3,0.5,0,100_000,1000,1000,400_000,true).is_err());
        // Direct CDF itself cannot fit at reference B: do not silently choose B-1.
        assert!(compatible_multiway_plan(3,0.5,0,500_000,1000,1000,0,false).is_err());''','''        let p=compatible_multiway_plan(3,0.5,0,100_000,1000,1000,400_000,true).unwrap().unwrap();
        assert!(p.minimal_metadata);assert_eq!(p.storage.batch,3);assert!(p.reference.unwrap().use_eq_cache);
        // Extra direct-CDF metadata cannot fit at B: keep B with original layout.
        let p=compatible_multiway_plan(3,0.5,0,500_000,1000,1000,0,false).unwrap().unwrap();
        assert!(p.minimal_metadata);assert_eq!(p.storage.batch,3);assert_eq!(p.storage.normalized_bytes,0);''')
begin=kold.index('extern "C" __global__ void pf_multiway_terminal(')
end=kold.index('// Terminal values for traverser p.',begin)
minimal=kold[begin:end].replace('pf_multiway_terminal(', 'pf_multiway_terminal_minimal(',1).replace('const float* __restrict__ terminal_prob,','const float* __restrict__ reach_mass,',1).replace('''        prob = terminal_prob[blockIdx.x];''','''        // Same ascending opponent order as original/prepared probability.
        // Includes folded opponents, never own reach; refreshed every batch.
        prob = 1.f;
        for (int q = 0; q < np; q++) {
            if (q == p) continue;
            prob *= reach_mass[reach_src[(size_t)nd * np + q]];
        }''',1)
k=kold[:end]+'// Minimum-memory compatibility entry: no active/probability/normalization metadata.\n'+minimal+kold[end:]
if (p/'tests.rs').exists():
 s=s.replace('    fn phase_test_equity()', (p/'tests.rs').read_text(encoding='utf-8-sig')+'\n    fn phase_test_equity()',1)
patch=''
for rel,a,b,name in [(rg,old,s,'gpu.rs'),(rk,kold,k,'kernels.cu')]:
 (p/name).write_bytes(b.replace('\n','\r\n').encode())
 patch+=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(p/'minimal.patch').write_text(patch,encoding='utf-8',newline='\n')
print('generated',len(s)-len(old),len(k)-len(kold),'added bytes')

