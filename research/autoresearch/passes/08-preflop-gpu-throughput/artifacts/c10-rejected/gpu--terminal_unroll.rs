//! Opt-in C09: change only the compiler hint on the sample loop.
pub(super) fn source(base:&str,factor:u32)->Result<String,String> {
    if ![0,2,4].contains(&factor) {return Err("unsupported terminal unroll factor".into());}
    let head="    for (u32 local = 0; local < sample_count; local++) {";
    if base.matches(head).count()!=1 {return Err("C09 sample-loop rewrite invariant".into());}
    Ok(if factor!=0{base.replace(head,&format!("    #pragma unroll {factor}\n{head}"))}else{base.to_string()})
}
#[cfg(test)]
mod tests;

#[cfg(test)]
pub(super) fn diagnostic(name:&str,factor:u32,ptx:&cudarc::nvrtc::Ptx,f:&super::CudaFunction)->Result<(),String> {
    let Ok(dir)=std::env::var("PREFLOP_GPU_UNROLL_RUNTIME_DIAGNOSTICS") else{return Ok(());};
    let dir=std::path::Path::new(&dir);std::fs::create_dir_all(dir).map_err(|e|e.to_string())?;
    let stem=format!("{name}-{factor}");let path=dir.join(format!("{stem}.ptx"));
    if path.exists(){return Err("runtime diagnostic output exists".into());}
    std::fs::write(path,ptx.to_src()).map_err(|e|e.to_string())?;
    let r=serde_json::json!({"kernel":name,"factor":factor,"registers":f.num_regs().map_err(super::e)?,"local_bytes":f.local_size_bytes().map_err(super::e)?,"shared_bytes":f.shared_size_bytes().map_err(super::e)?});
    std::fs::write(dir.join(format!("{stem}.json")),serde_json::to_vec_pretty(&r).unwrap()).map_err(|e|e.to_string())?;Ok(())
}
