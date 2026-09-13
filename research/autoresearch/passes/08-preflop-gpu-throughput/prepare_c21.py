"""Combine exact-zero bypass with shuffle-valid addition; no runtime hook."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
def main():
    root=LAB/'crates/solver/src/preflop/gpu';target=root/'cdf_zero_predicate.rs';assert not target.exists()
    s=(root/'cdf_zero.rs').read_text(encoding='utf-8')
    s=s.replace('C20','C21').replace('zero_writer_matches_retained_prefix','predicate_zero_writer_matches_retained_prefix')
    s=s.replace('PREFLOP_GPU_CDF_ZERO_OUTPUT','PREFLOP_GPU_CDF_ZERO_PREDICATE_OUTPUT')
    s=s.replace('pf_exact_reuse_cdf_sparse','pf_exact_reuse_cdf_sparse_predicate')
    start=s.index('    let new=');end=s.index('\n',start)
    s=s[:start]+r'''    let new=r#"        if (__any_sync(0xffffffff, value != 0.f)) {
            #pragma unroll
            for (int step = 1; step < 32; step <<= 1) {
                asm volatile("{ .reg .f32 other; .reg .pred valid;\n"
                    "shfl.sync.up.b32 other|valid, %0, %1, 0, 0xffffffff;\n"
                    "@valid add.rn.f32 %0, %0, other;\n}"
                    : "+f"(value) : "r"(step));
            }
        }"#;'''+s[end:]
    target.write_text(s,encoding='utf-8',newline='\n')
    parent=LAB/'crates/solver/src/preflop/gpu.rs';raw=parent.read_bytes();assert b'mod cdf_zero_predicate;' not in raw
    parent.write_bytes(raw+b'\n#[cfg(all(test, feature = "preflop-research"))]\nmod cdf_zero_predicate;\n')
    mapping={}
    for p in [target,parent]:
        dest=HERE/'artifacts/c21-v1'/p.relative_to(LAB/'crates/solver');assert not dest.exists()
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        mapping[p.relative_to(LAB).as_posix()]=dict(archive=dest.relative_to(HERE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (HERE/'artifacts/c21-v1-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
    old=(HERE/'run_c20_screen.py').read_text(encoding='utf-8')
    run=old.replace('c20','c21').replace('C20','C21').replace('cdf_zero::zero_writer','cdf_zero_predicate::predicate_zero_writer')
    run=run.replace('PREFLOP_GPU_CDF_ZERO_OUTPUT','PREFLOP_GPU_CDF_ZERO_PREDICATE_OUTPUT')
    dest=HERE/'run_c21_screen.py';assert not dest.exists();dest.write_text(run,encoding='utf-8',newline='\n')
if __name__=='__main__':main()
