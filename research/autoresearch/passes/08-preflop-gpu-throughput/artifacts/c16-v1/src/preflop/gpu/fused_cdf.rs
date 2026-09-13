//! C16 research-only fused local-CDF evaluator.
use super::*;
pub(super) fn requested()->bool {
    std::env::var("PREFLOP_GPU_FUSED_CDF").ok().as_deref()==Some("1")
}
pub(super) fn source(base:&str,kernel:&str,enabled:bool)->Result<String,String> {
    if !enabled{return Ok(base.to_string());}
    let marker=format!("extern \"C\" __global__ void {kernel}(");
    let a=base.find(&marker).ok_or("C16 missing terminal")?;
    let b=a+base[a..].find("\n}\n").ok_or("C16 terminal end")?+3;
    let mut head=base[a..b].split("    __syncthreads();").next().ok_or("C16 terminal barrier")?.to_string();
    for (old,new) in [
        ("float* val, const u32* aliases)","float* val, const u32* aliases, const float* normalized, const u32* order)"),
        ("cdf_slot * batch_capacity * (NC + 1)","cdf_slot * NC"),
    ] {if head.matches(old).count()!=1{return Err(format!("C16 rewrite: {old}"));}head=head.replace(old,new);}
    head.push_str("    __syncthreads();\n    if (prob <= 0.f) {\n        if (sample_start == 0) for (u32 h = threadIdx.x; h < NC; h += blockDim.x) val[(size_t)val_slot[nd] * NC + h] = 0.f;\n        return;\n    }\n    __shared__ float local_norm[8 * NC];\n    __shared__ float local_cdf[8 * (NC + 1)];\n    u32 h = threadIdx.x;\n    float sum;\n    switch (nopponents) {\n");
    for o in 2..=8 {let q=(o+2)/2;let label=if o==8{"default".to_string()}else{format!("case {o}")};
        head+=&format!("        {label}: sum = pf_fused_sum<{q},{o}>(h, opponent_bases, normalized, order, lower, upper, sample_start, sample_count, local_norm, local_cdf); break;\n");}
    head.push_str("    }\n    if (h < NC) {\n        size_t at = (size_t)val_slot[nd] * NC + h;\n        float increment = prob * pots[nd] * sum / (float)samples;\n        if (sample_start == 0) val[at] = increment - prob * invested[(size_t)nd * np + p];\n        else val[at] += increment;\n    }\n}\n");
    Ok(format!("{}\n{}\n{}{}",&base[..a],include_str!("fused_cdf.cu"),head,&base[b..]))
}
#[cfg(test)]
mod tests;
