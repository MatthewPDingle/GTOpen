"""Create isolated sparse writer test and archive it before compilation."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
PREFIX=r'''//! C20 test-only exact-zero scan bypass; original writer remains unchanged.
use super::*;
use serde_json::json;

fn candidate(base:&str)->String {
    let start=base.find("extern \"C\" __global__ void pf_exact_reuse_cdf(").unwrap();
    let end=start+base[start..].find("extern \"C\" __global__ void pf_exact_reuse_terminal(").unwrap();
    let writer=&base[start..end];
    let old="        #pragma unroll\n        for (int step = 1; step < 32; step <<= 1) {\n            float add = __shfl_up_sync(0xffffffff, value, step);\n            if (lane >= (u32)step) value += add;\n        }";
    let new="        if (__any_sync(0xffffffff, value != 0.f)) {\n            #pragma unroll\n            for (int step = 1; step < 32; step <<= 1) {\n                float add = __shfl_up_sync(0xffffffff, value, step);\n                if (lane >= (u32)step) value += add;\n            }\n        }";
    assert_eq!(writer.matches(old).count(),1);
    let sparse=writer.replace("pf_exact_reuse_cdf(","pf_exact_reuse_cdf_sparse(").replace(old,new);
    format!("{base}\n{sparse}")
}

'''
def main():
    target=LAB/'crates/solver/src/preflop/gpu/cdf_zero.rs';assert not target.exists()
    original=(target.parent/'cdf_interleave.rs').read_text(encoding='utf-8');tests=original[original.index('#[test]'):]
    tests=tests.replace('interleaved_writer_matches_retained_prefix','zero_writer_matches_retained_prefix')
    tests=tests.replace('PREFLOP_GPU_CDF_INTERLEAVE_OUTPUT','PREFLOP_GPU_CDF_ZERO_OUTPUT').replace('C19_WRITER','C20_WRITER')
    tests=tests.replace('module.load_function("pf_exact_reuse_cdf")','module.load_function(if enabled{"pf_exact_reuse_cdf_sparse"}else{"pf_exact_reuse_cdf"})')
    tests=tests.replace('[1u32,0,1,2,3,4,5,6]','[1u32,0,1,2,3,4,5,6,7,8,9,10]').replace('let zero=pattern==0;','let zero=matches!(pattern,0|7|8);')
    anchor='                _=>unreachable!(),'
    assert tests.count(anchor)==1
    tests=tests.replace(anchor,'''                7=>-0.0,
                8=>if i%2==0 {-0.0}else{0.0},
                9=>if i%169==168 {f32::from_bits(1)}else{-0.0},
                10=>if i%29==0 {1e-30}else{-0.0},
'''+anchor)
    target.write_text(PREFIX+tests,encoding='utf-8',newline='\n')
    parent=LAB/'crates/solver/src/preflop/gpu.rs';raw=parent.read_bytes();assert b'mod cdf_zero;' not in raw
    parent.write_bytes(raw+b'\n#[cfg(all(test, feature = "preflop-research"))]\nmod cdf_zero;\n')
    mapping={}
    for p in [target,parent]:
        dest=HERE/'artifacts/c20-v1'/p.relative_to(LAB/'crates/solver');assert not dest.exists()
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        mapping[p.relative_to(LAB).as_posix()]=dict(archive=dest.relative_to(HERE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (HERE/'artifacts/c20-v1-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
