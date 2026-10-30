//! Opt-in C09: change only the compiler hint on the sample loop.
pub(super) fn source(base:&str,enabled:bool)->Result<String,String> {
    let head="    for (u32 local = 0; local < sample_count; local++) {";
    if base.matches(head).count()!=1 {return Err("C09 sample-loop rewrite invariant".into());}
    Ok(if enabled{base.replace(head,&format!("    #pragma unroll 2\n{head}"))}else{base.to_string()})
}
#[cfg(all(test, feature = "preflop-research"))]
mod tests;
