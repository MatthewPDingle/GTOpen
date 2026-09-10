from pathlib import Path
import difflib
p=Path(__file__).parent
old=(p.parent/'compatibility-minimal/gpu.rs').read_text(encoding='utf-8-sig')
s=old

def replace(a,b):
 global s
 assert s.count(a)==1,(a[:100],s.count(a))
 s=s.replace(a,b)
replace('// physical scratch layout. This reproduces the original union CDF planner\n// after the common forced-policy accounting correction, without allocating it.', '// physical scratch layout. Reproduce the original union CDF planner for the\n// explicitly supplied literal or corrected base, without allocating its scratch.')
replace('fn compatible_multiway_plan(', '#[cfg(test)]\nfn compatible_multiway_plan(')
replace('#[derive(Debug, PartialEq, Eq)]\nstruct ReferenceMultiwayPlan', '#[derive(Clone, Copy, Debug, PartialEq, Eq)]\nstruct ReferenceMultiwayPlan')
replace('''    let reference = reference_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
        union_slots, eq_cache_bytes, has_eq_cache)?;
    if physical_slots == 0''','''    let reference = reference_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
        union_slots, eq_cache_bytes, has_eq_cache)?;
    fit_compatible_multiway_plan(budget_mb, base_mb, reference_fixed_bytes,
        optimized_fixed_bytes, union_slots, physical_slots, eq_cache_bytes, reference)
}

// Physical fit is independent of how the numerical reference was chosen.
// An unsupported target returns None; allocation overflow remains an error.
fn fit_compatible_multiway_plan(
    budget_mb:u64, base_mb:f64, reference_fixed_bytes:usize, optimized_fixed_bytes:usize,
    union_slots:usize, physical_slots:usize, eq_cache_bytes:usize,
    reference:Option<ReferenceMultiwayPlan>,
) -> Result<Option<CompatibleMultiwayPlan>,String> {
    if physical_slots == 0''')
replace('''    if need > budget_mb as f64 { return Err("original compatibility layout exceeds its supplied budget".into()); }''','''    if need > budget_mb as f64 { return Ok(None); }''')
marker='// Include the one-float placeholder allocated when no policies are forced.'
helper='''struct DeployedCompatibilityPlan {
    plan: CompatibleMultiwayPlan,
    reference_source: &'static str,
    literal_reference: Option<ReferenceMultiwayPlan>,
}

// Literal pre-pass grouping is a numerical target, never a memory allowance.
// Accurate base includes forced policies; literal base is captured beforehand,
// not recovered by subtracting bytes from an already-rounded f64 total.
fn deployed_compatible_multiway_plan(
    budget_mb:u64, accurate_base_mb:f64, literal_base_mb:f64,
    reference_fixed_bytes:usize, optimized_fixed_bytes:usize,
    union_slots:usize, physical_slots:usize, eq_cache_bytes:usize, has_eq_cache:bool,
    force_minimal:bool,
) -> Result<Option<DeployedCompatibilityPlan>,String> {
    if !accurate_base_mb.is_finite() || accurate_base_mb < literal_base_mb {
        return Err("invalid accurately accounted multiway base".into());
    }
    let literal = reference_multiway_plan(budget_mb,literal_base_mb,reference_fixed_bytes,
        union_slots,eq_cache_bytes,has_eq_cache)?;
    let fit = |target:Option<ReferenceMultiwayPlan>| {
        if force_minimal {
            original_layout_multiway_plan(budget_mb,accurate_base_mb,reference_fixed_bytes,
                union_slots,eq_cache_bytes,target)
        } else {
            fit_compatible_multiway_plan(budget_mb,accurate_base_mb,reference_fixed_bytes,
                optimized_fixed_bytes,union_slots,physical_slots,eq_cache_bytes,target)
        }
    };
    // None means no original GPU grouping, not permission to prefer an
    // arbitrary capacity-extension batch before trying a corrected reference.
    if literal.is_some() {
        if let Some(plan)=fit(literal)? {
            return Ok(Some(DeployedCompatibilityPlan {
                plan,reference_source:"deployed_prepass",literal_reference:literal,
            }));
        }
    }
    let corrected=reference_multiway_plan(budget_mb,accurate_base_mb,reference_fixed_bytes,
        union_slots,eq_cache_bytes,has_eq_cache)?;
    Ok(fit(corrected)?.map(|plan| DeployedCompatibilityPlan {
        reference_source:if plan.reference.is_some() {"corrected_budget_fallback"} else {"capacity_extension"},
        plan,literal_reference:literal,
    }))
}

'''
replace(marker,helper+marker)
replace('''        need = reserve_forced_vram_mb(need, forced.len(), budget_mb)?;''','''        let literal_reference_base_mb = need;
        need = reserve_forced_vram_mb(need, forced.len(), budget_mb)?;''')
replace('''        let mut mw_reference = None;
        if use_multiway {''','''        let mut mw_reference = None;
        let mut mw_reference_source = "not_applicable";
        let mut mw_literal_reference = None;
        if use_multiway {''')
a='''            let selected = if force_minimal {
                let reference = reference_multiway_plan(budget_mb, need, reference_fixed,
                    mw_plan.blocks.len(), eq_plan.bytes(), !eq_plan.blocks.is_empty())?;
                original_layout_multiway_plan(budget_mb, need, reference_fixed,
                    mw_plan.blocks.len(), eq_plan.bytes(), reference)?
            } else {
                compatible_multiway_plan(budget_mb, need, reference_fixed,
                    fixed, mw_plan.blocks.len(), compact.capacity, eq_plan.bytes(), !eq_plan.blocks.is_empty())?
            };
            let Some(selected) = selected else {'''
b='''            let selected = deployed_compatible_multiway_plan(budget_mb, need, literal_reference_base_mb,
                reference_fixed, fixed, mw_plan.blocks.len(), compact.capacity,
                eq_plan.bytes(), !eq_plan.blocks.is_empty(), force_minimal)?;
            let Some(selected) = selected else {'''
replace(a,b)
replace('''            use_mw_prepared = !selected.minimal_metadata;''','''            mw_reference_source = selected.reference_source;
            mw_literal_reference = selected.literal_reference;
            let selected = selected.plan;
            use_mw_prepared = !selected.minimal_metadata;''')
replace('''                println!("preflop gpu: original union {}-particle grouping and HU-cache={} preserved with optimized storage",
                    reference.batch, reference.use_eq_cache);''','''                println!("preflop gpu: {} reference, {}-particle grouping and HU-cache={} with accurately budgeted storage",
                    mw_reference_source, reference.batch, reference.use_eq_cache);
                if mw_reference_source == "corrected_budget_fallback" {
                    println!("preflop gpu: deployed grouping could not fit safely; using corrected-budget grouping");
                }''')
replace('''                println!("preflop gpu: optimized capacity extension; original union CDF could not fit one particle");''','''                println!("preflop gpu: optimized capacity extension; no safely fitting reference grouping");''')
replace('''                "batch_policy": if !use_multiway { "not_applicable" } else if mw_reference.is_some() { "original_union_compatible" } else { "capacity_extension" },''','''                "batch_policy": mw_reference_source,
                "literal_reference_multiway_batch": mw_literal_reference.map(|r|r.batch),
                "literal_reference_hu_cache_enabled": mw_literal_reference.map(|r|r.use_eq_cache),''')
replace('''            let base=minimum_vram_mb(&s,ValuePlan::build(&s).blocks)+forced_storage_bytes(0).unwrap() as f64/1e6;''','''            let literal_base=minimum_vram_mb(&s,ValuePlan::build(&s).blocks);
            let base=literal_base+forced_storage_bytes(0).unwrap() as f64/1e6;''')
replace('''                let union=compatible_multiway_plan(budget,base,fixed,fixed+extra,mw.blocks.len(),mw.blocks.len(),hu.bytes(),!hu.blocks.is_empty()).unwrap();
                let Some(union)=union else {continue;};''','''                let union=deployed_compatible_multiway_plan(budget,base,literal_base,fixed,fixed+extra,mw.blocks.len(),mw.blocks.len(),hu.bytes(),!hu.blocks.is_empty(),false).unwrap();
                let Some(union)=union else {continue;};let union=union.plan;''')
replace('''                let compact_plan=compatible_multiway_plan(budget,base,fixed,fixed+extra+compact.bytes,mw.blocks.len(),compact.capacity,hu.bytes(),!hu.blocks.is_empty()).unwrap().unwrap();''','''                let compact_plan=deployed_compatible_multiway_plan(budget,base,literal_base,fixed,fixed+extra+compact.bytes,mw.blocks.len(),compact.capacity,hu.bytes(),!hu.blocks.is_empty(),false).unwrap().unwrap().plan;''')
s+='\n'+(p/'tests.rs').read_text(encoding='utf-8-sig')
(p/'gpu.rs').write_bytes(s.replace('\n','\r\n').encode())
(p/'deployed.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='a/crates/solver/src/preflop/gpu.rs',tofile='b/crates/solver/src/preflop/gpu.rs')),encoding='utf-8',newline='\n')
print('generated',len(s)-len(old),'added bytes')
