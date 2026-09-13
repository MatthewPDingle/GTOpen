"""Create the bounded test-only C19 writer screen; refuse overwrite."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;LAB=HERE.parents[3]
PREFIX=r'''//! C19 test-only interleaved CDF scan; no runtime selection hook.
use super::*;
use serde_json::json;

fn candidate(base:&str)->String {
    let start=base.find("extern \"C\" __global__ void pf_exact_reuse_cdf(").unwrap();
    let end=start+base[start..].find("extern \"C\" __global__ void pf_exact_reuse_terminal(").unwrap();
    let writer=&base[start..end];
    let loop_start=writer.find("    float carry = 0.f;").unwrap();
    let loop_end=writer.rfind("\n}").unwrap();
    assert_eq!(writer.matches("for (u32 tile = 0; tile < NC; tile += 32)").count(),1);
    let mut scan=String::new();
    for tile in 0..6 {
        let offset=tile*32;
        scan.push_str(&format!("    u32 i{tile} = {offset}u + lane;\n    float v{tile} = i{tile} < NC ? normalized[(size_t)(compact ? blockIdx.x : slot) * NC + order[(size_t)particle * NC + i{tile}]] : 0.f;\n"));
    }
    for step in [1,2,4,8,16] {
        for tile in 0..6 {
            scan.push_str(&format!("    {{ float add = __shfl_up_sync(0xffffffff, v{tile}, {step}); if (lane >= {step}u) v{tile} += add; }}\n"));
        }
    }
    scan.push_str("    float carry = 0.f;\n");
    for tile in 0..6 {
        scan.push_str(&format!("    if (i{tile} < NC) cdf[base + i{tile} + 1] = carry + v{tile};\n    carry += __shfl_sync(0xffffffff, v{tile}, 31);\n"));
    }
    format!("{}{}{}{}{}",&base[..start],&writer[..loop_start],scan,&writer[loop_end..],&base[end..])
}

'''
def main():
    target=LAB/'crates/solver/src/preflop/gpu/cdf_interleave.rs'
    assert not target.exists()
    original=(target.parent/'narrow_cdf.rs').read_text(encoding='utf-8')
    tests=original[original.index('#[test]'):]
    tests=tests.replace('bounded_writer_matches_retained_prefix','interleaved_writer_matches_retained_prefix')
    tests=tests.replace('PREFLOP_GPU_CDF_WRITER_OUTPUT','PREFLOP_GPU_CDF_INTERLEAVE_OUTPUT')
    tests=tests.replace('D09_WRITER','C19_WRITER')
    tests=tests.replace('for zero in [false,true,false] {','for pattern in [1u32,0,1,2,3,4,5,6] {\n            let zero=pattern==0;')
    old='let norm:Vec<f32>=(0..4*169).map(|i|if zero{0.}else{((i*37+i/169*13)%191) as f32/512.}).collect();'
    new='''let norm:Vec<f32>=(0..4*169).map(|i|match pattern {
                0=>0.,
                1=>((i*37+i/169*13)%191) as f32/512.,
                2=>if i%47==0 {0.125}else{0.},
                3=>f32::from_bits((i%17+1) as u32),
                4=>if i%169==168 {1.}else{0.},
                5=>if i%13==0 {0.99999994}else{1e-30},
                6=>1e-20*((i%11+1) as f32),
                _=>unreachable!(),
            }).collect();'''
    assert tests.count(old)==1
    tests=tests.replace(old,new).replace('json!({"zero":zero,','json!({"pattern":pattern,"zero":zero,')
    target.write_text(PREFIX+tests,encoding='utf-8',newline='\n')
    parent=LAB/'crates/solver/src/preflop/gpu.rs'
    raw=parent.read_bytes();assert b'mod cdf_interleave;' not in raw
    parent.write_bytes(raw+b'\n#[cfg(all(test, feature = "preflop-research"))]\nmod cdf_interleave;\n')
    mapping={}
    for p in (parent,target):
        dest=HERE/'artifacts/c19-v1'/p.relative_to(LAB/'crates/solver')
        assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
        mapping[p.relative_to(LAB).as_posix()]=dict(archive=dest.relative_to(HERE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    (HERE/'artifacts/c19-v1-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
    print('Created and archived C19 test-only source')
if __name__=='__main__':main()
