//! C17 research-only terminal scheduling, with unchanged arithmetic helper.
use super::*;
pub(super) fn source(input:&str,name:&str)->Result<String,String>{
    let marker=format!(r#"extern "C" __global__ void {name}("#);
    let (prefix,body)=input.split_once(&marker).ok_or("C17 terminal missing")?;
    let end=body.find("\n}\n").ok_or("C17 terminal end")?+3;
    let mut terminal=body[..end].to_owned();
    for (old,new) in [
        ("const u32* aliases)","const u32* aliases, u32 terminal_count)"),
        ("    u32 nd = terms[blockIdx.x];","    u32 warp = threadIdx.x / 32, lane = threadIdx.x % 32;\n    u32 task = blockIdx.x * 4 + warp;\n    if (task >= terminal_count) return;\n    u32 nd = terms[task];"),
        ("__shared__ float prob;","__shared__ float probabilities[4];\n    float& prob = probabilities[warp];"),
        ("__shared__ u32 opponent_bases[9];","__shared__ u32 all_bases[4][9];\n    u32* opponent_bases = all_bases[warp];"),
        ("__shared__ int nopponents;","__shared__ int counts[4];\n    int& nopponents = counts[warp];"),
        ("if (threadIdx.x == 0)","if (lane == 0)"),
        ("terminal_prob[blockIdx.x]","terminal_prob[task]"),
        ("__syncthreads();","__syncwarp(0xffffffff);"),
        ("for (u32 h = threadIdx.x; h < NC; h += blockDim.x)","for (u32 h = lane; h < NC; h += 32)"),
    ] {
        if terminal.matches(old).count()!=1{return Err(format!("C17 source invariant: {old}"));}
        terminal=terminal.replace(old,new);
    }
    Ok(format!("{prefix}{marker}{terminal}{}",&body[end..]))
}
pub(super) fn launch(terms:u32,packed:bool)->LaunchConfig{
    if packed {LaunchConfig{grid_dim:(terms.div_ceil(4),1,1),block_dim:(128,1,1),shared_mem_bytes:0}}
    else {LaunchConfig{grid_dim:(terms,1,1),block_dim:(192,1,1),shared_mem_bytes:0}}
}
#[cfg(test)]
mod tests;
