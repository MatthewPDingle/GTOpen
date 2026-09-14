//! C24 ordinary-path prototype. Only compiled in opt-in research tests.
use super::*;

pub(crate) fn kernel_source()->Result<String,String>{
    let original=super::integrated_source()?;
    let mut output=original.clone();
    for (old_name,new_name) in [("pf_static_cdf","pf_ordinary_static_cdf"),("pf_static_terminal","pf_ordinary_static_terminal")] {
        let start=original.find(&format!("extern \"C\" __global__ void {old_name}(")).ok_or("C24 source start")?;
        let end=start+original[start..].find("\n}\n").ok_or("C24 source end")?+3;
        let mut function=original[start..end].replace(old_name,new_name);
        let alias=if old_name=="pf_static_cdf" {"    if (aliases[blockIdx.x] != blockIdx.x) return;\n"}else{"                cdf_slot = aliases[cdf_slot];\n"};
        if function.matches(alias).count()!=1 || function.matches("const u32* aliases, ").count()!=1{return Err("C24 alias removal invariant".into());}
        function=function.replace(alias,"").replace("const u32* aliases, ","");
        if function.contains("aliases"){return Err("C24 must not depend on duplicate aliases".into());}
        output+=&function;
    }
    Ok(output)
}

thread_local!{static FAIL_STAGE:std::cell::Cell<u32>=const{std::cell::Cell::new(0)};}
fn fault(g:&PreflopGpu,stage:u32)->Result<(),String>{
    if FAIL_STAGE.get()!=stage{return Ok(());}FAIL_STAGE.set(0);
    let err=unsafe{g.stream.alloc::<u8>(1usize<<50)}.unwrap_err();
    assert_eq!(err.0,sys::CUresult::CUDA_ERROR_OUT_OF_MEMORY);
    Err(format!("C24 allocation stage {stage}: {}",e(err)))
}

pub(crate) fn promote(mut g:PreflopGpu,s:&PreflopSolver,budget:u64)->Result<PreflopGpu,String>{
    if g.warmed || g.eval_warmed || g.static_cdf.is_some() || g.research_exact_reuse.is_some()
        || g.research_cohorts.is_some() || !g.exact_reuse_compatible() || g.research_unit_probability
        || g.research_samples!=SAMPLES as u32 || !(1..=32).contains(&g.mw_batch) {
        return Err("C24 requires a fresh ordinary compact normalized full-sample engine".into());
    }
    let capacity=g.d_mw_normalized.len()/NUM_CLASSES;
    let expected=capacity.checked_mul(g.mw_batch as usize).and_then(|x|x.checked_mul(170)).ok_or("C24 original capacity overflow")?;
    if g.d_mw_cdf.len()!=expected{return Err("C24 CDF allocation must match its unchanged batch".into());}
    let maps=Maps::with_batch(s.multiway.as_ref().ok_or("C24 fixed ranks missing")?,g.mw_batch as usize);
    let elements=capacity.checked_mul(maps.stride as usize).ok_or("C24 packed capacity overflow")?;
    narrow_offsets::check_elements(elements)?;
    let original_bytes=g.d_mw_cdf.len()*4;
    let metadata=(maps.prefix.len()+maps.hand.len()+maps.offsets.len())*4;
    let before:usize=super::super::cross_player_inventory::device_buffer_bytes(&g).values().sum();
    let final_bytes=before.checked_sub(original_bytes).and_then(|x|x.checked_add(elements*4)).and_then(|x|x.checked_add(metadata)).ok_or("C24 budget overflow")?;
    let reserve=256*1024*1024;
    if final_bytes as u128+reserve as u128>budget as u128*1_000_000{return Err("C24 final allocation exceeds reserved budget".into());}
    let (free,_)=g._ctx.mem_get_info().map_err(e)?;
    if metadata+reserve>free{return Err("C24 metadata construction lacks free-memory reserve".into());}
    let prefix=g.stream.clone_htod(&maps.prefix).map_err(e)?;
    let hand=g.stream.clone_htod(&maps.hand).map_err(e)?;
    let offsets=g.stream.clone_htod(&maps.offsets).map_err(e)?;
    fault(&g,1)?;
    g.stream.synchronize().map_err(e)?;
    let empty=g.stream.null::<f32>().map_err(e)?;
    drop(std::mem::replace(&mut g.d_mw_cdf,empty));g.stream.synchronize().map_err(e)?;
    fault(&g,2)?;
    g.d_mw_cdf=g.stream.alloc_zeros::<f32>(elements).map_err(e)?;
    fault(&g,3)?;
    let (major,minor)=g._ctx.compute_capability().map_err(e)?;
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    static PTX:std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>=std::sync::OnceLock::new();
    let ptx=PTX.get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(kernel_source()?,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
    let module=g._ctx.load_module(ptx.clone()).map_err(e)?;
    let writer=module.load_function("pf_ordinary_static_cdf").map_err(e)?;
    let terminal=module.load_function("pf_ordinary_static_terminal").map_err(e)?;
    let folder=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_ORDINARY_STATIC_OUTPUT").map_err(e)?);
    std::fs::create_dir_all(&folder).map_err(e)?;
    let file=folder.join("candidate.ptx");
    if file.exists(){assert_eq!(std::fs::read_to_string(file).unwrap(),ptx.to_src());}else{
        std::fs::write(file,ptx.to_src()).map_err(e)?;
        std::fs::write(folder.join("candidate.cu"),kernel_source()?).map_err(e)?;
        let mut resources=Vec::new();for (name,f) in [("writer",&writer),("terminal",&terminal)]{
            resources.push(json!({"kernel":name,"registers":f.num_regs().map_err(e)?,"shared_bytes":f.shared_size_bytes().map_err(e)?,"local_bytes":f.local_size_bytes().map_err(e)?}));
        }
        std::fs::write(folder.join("resources.json"),serde_json::to_vec_pretty(&resources).map_err(e)?).map_err(e)?;
    }
    g.static_cdf=Some(Packed{prefix,hand,offsets,writer,terminal,stride:maps.stride,original_bytes});
    assert_eq!(super::super::cross_player_inventory::device_buffer_bytes(&g).values().sum::<usize>()+g.static_cdf.as_ref().unwrap().bytes(),final_bytes);
    Ok(g)
}

pub(crate) fn launch(g:&mut PreflopGpu,p:i32,gate:i32,start:u32,count:u32,sample_start:u32,sample_count:u32,samples:u32)->Result<(),String>{
    unsafe{
        g.phase_mark("cdf",p)?;
        let k=g.static_cdf.as_ref().ok_or("C24 tables missing")?;
        g.stream.launch_builder(&k.writer).arg(&g.d_mw_work).arg(&start).arg(&g.d_mw_blocks).arg(&g.d_mw_order)
            .arg(&g.d_mw_normalized).arg(&g.d_reach_mass).arg(&g.d_mw_active).arg(&gate).arg(&g.use_mw_compact)
            .arg(&mut g.d_mw_cdf).arg(&sample_start).arg(&sample_count).arg(&g.mw_batch)
            .arg(&k.stride).arg(&k.prefix).arg(&k.offsets)
            .launch(LaunchConfig{grid_dim:(count,sample_count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).map_err(e)?;
        g.phase_mark("coupled_terminals",p)?;
        let k=g.static_cdf.as_ref().ok_or("C24 tables missing")?;
        g.stream.launch_builder(&k.terminal).arg(&g.d_mw_terms).arg(&p).arg(&g.np)
            .arg(&g.d_live).arg(&g.d_pots).arg(&g.d_inv).arg(&g.d_reach_src).arg(&g.d_mw_prob)
            .arg(&g.d_mw_slots).arg(&g.d_mw_compact).arg(&g.mw_union_slots).arg(&g.use_mw_compact).arg(&g.d_mw_cdf)
            .arg(&k.hand).arg(&g.d_mw_upper).arg(&sample_start).arg(&sample_count).arg(&g.mw_batch).arg(&samples)
            .arg(&g.d_val_slot).arg(&mut g.d_val).arg(&k.stride).arg(&k.offsets).arg(&0i32)
            .launch(LaunchConfig{block_dim:(192,1,1),..PreflopGpu::cfg(g.mw_nterms)}).map_err(e)?;
    }Ok(())
}

#[cfg(test)]
mod tests;
