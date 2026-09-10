from pathlib import Path
import subprocess,difflib,hashlib
out=Path(__file__).parent
root=Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
rel='crates/solver/src/preflop/gpu.rs'
old=subprocess.check_output(['git','show','739c68d:'+rel],cwd=root).decode('utf-8').replace('\r\n','\n')
new=old
planner=(out/'planner.rs').read_text(encoding='utf-8-sig')
new=new.replace('// Include the one-float placeholder allocated when no policies are forced.',planner+'// Include the one-float placeholder allocated when no policies are forced.',1)
needle='''        let mut use_mw_normalized = false;
        if use_multiway {'''
assert new.count(needle)==1
new=new.replace(needle,'''        let mut use_mw_normalized = false;
        let mut mw_reference = None;
        if use_multiway {''')
needle='''            let remaining = (budget_mb as f64 * 1e6 - need * 1e6 - fixed as f64).max(0.0) as usize;
            let Some(plan) = multiway_batch_plan(remaining, compact.capacity)? else {'''
assert new.count(needle)==1
new=new.replace(needle,'''            let reference_fixed = mw_plan.metadata_bytes() + mw_terms.len() * 4
                + 3 * super::multiway::SAMPLES * NUM_CLASSES * 4;
            let Some(selected) = compatible_multiway_plan(budget_mb, need, reference_fixed,
                fixed, mw_plan.blocks.len(), compact.capacity, eq_plan.bytes(), !eq_plan.blocks.is_empty())? else {''')
needle='''            mw_batch = plan.batch;
            mw_cache_len = plan.cache_len;'''
assert new.count(needle)==1
new=new.replace(needle,'''            mw_reference = selected.reference;
            let plan = selected.storage;
            mw_batch = plan.batch;
            mw_cache_len = plan.cache_len;''')
needle='''        let use_eq_cache = !eq_plan.blocks.is_empty()
            && need + eq_plan.bytes() as f64 / 1e6 <= budget_mb as f64;
        if use_eq_cache {'''
assert new.count(needle)==1
new=new.replace(needle,'''        let eq_cache_fits = !eq_plan.blocks.is_empty()
            && need + eq_plan.bytes() as f64 / 1e6 <= budget_mb as f64;
        let use_eq_cache = mw_reference.as_ref().map_or(eq_cache_fits, |r| r.use_eq_cache);
        if use_eq_cache && !eq_cache_fits {
            return Err("reference HU equity cache does not fit the optimized layout; solving on CPU".into());
        }
        if use_eq_cache {''')
needle='''            if !use_mw_normalized {
                println!("preflop gpu: direct CDF normalization to preserve minimum-VRAM fit");
            }'''
assert new.count(needle)==1
new=new.replace(needle,'''            if !use_mw_normalized {
                println!("preflop gpu: direct CDF normalization to preserve reference grouping or minimum-VRAM fit");
            }
            if let Some(reference) = &mw_reference {
                println!("preflop gpu: original union {}-particle grouping and HU-cache={} preserved with optimized storage",
                    reference.batch, reference.use_eq_cache);
            } else {
                println!("preflop gpu: optimized capacity extension; original union CDF could not fit one particle");
            }''')
needle='''                "compact_cdf": compact.enabled, "normalized_cdf": use_mw_normalized,'''
assert new.count(needle)==1
new=new.replace(needle,needle+'''
                "batch_policy": if !use_multiway { "not_applicable" } else if mw_reference.is_some() { "original_union_compatible" } else { "capacity_extension" },
                "reference_multiway_batch": mw_reference.as_ref().map(|r| r.batch),
                "reference_hu_cache_enabled": mw_reference.as_ref().map(|r| r.use_eq_cache),''')
new+='\n'+(out/'tests.rs').read_text(encoding='utf-8-sig')
(out/'gpu.rs').write_bytes(new.replace('\n','\r\n').encode())
(out/'compatibility.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)),encoding='utf-8',newline='\n')
(out/'base.txt').write_text('739c68d\n'+hashlib.sha256(old.encode()).hexdigest()+' normalized-LF GPU source SHA256\n')
print('Generated',len(new)-len(old),'added source bytes')
