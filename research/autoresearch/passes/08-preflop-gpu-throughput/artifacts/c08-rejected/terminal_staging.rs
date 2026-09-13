//! Opt-in C08 terminal rewrite. CDF creation and numerical order are unchanged.
pub(super) const HELPER:&str=include_str!("terminal_staging.cu");

pub(super) fn rewrite(source:String)->Result<String,String> {
    let loop_head="    for (u32 h = threadIdx.x; h < NC; h += blockDim.x) {";
    let at="        size_t at = (size_t)val_slot[nd] * NC + h;\n";
    let zero="        if (prob <= 0.f) { if (sample_start == 0) val[at] = 0.f; continue; }\n";
    if source.matches(loop_head).count()!=1 || source.matches(at).count()!=1 || source.matches(zero).count()!=1
        || source.matches("pf_multiway_sum<").count()!=7 || source.matches("sample_count); break;").count()!=7 {
        return Err("C08 terminal rewrite invariant".into());
    }
    Ok(source.replace(loop_head,"    u32 h = threadIdx.x;\n    __shared__ float staged[8 * (NC + 1)];\n    if (prob <= 0.f) {\n        if (h < NC && sample_start == 0) val[(size_t)val_slot[nd] * NC + h] = 0.f;\n        return;\n    }")
        .replace(at,"").replace(zero,"")
        .replace("pf_multiway_sum<","pf_staged_multiway_sum<")
        .replace("sample_count); break;","sample_count, staged); break;")
        .replace("        float increment =","    if (h < NC) {\n        size_t at = (size_t)val_slot[nd] * NC + h;\n        float increment ="))
}
