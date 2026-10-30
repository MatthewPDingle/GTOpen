//! Read-only CPU planning for future-card suit folding. No CUDA allocation.
//! Does not assert that the external-reach research bridge supports folding.
use serde_json::{json,Value};
use solver::{Spot,SpotConfig,TreeConfig,StreetSizing,parse_sizes,gpu::plan::GpuPlan};
use solver::preflop::equity::class_label;
fn main() {
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3,"SUBTREE MANIFEST OUTPUT");
    assert!(!std::path::Path::new(&args[2]).exists());
    let read=|p:&str|->Value{serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap()};
    let d=read(&args[0]);let m=read(&args[1]);
    let ranges:Vec<String>=(0..2).map(|p| {
        let w:Vec<f64>=(0..169).map(|c| {
            d["incoming_class_mass"][p][c].as_f64().unwrap()/if c/13==c%13{6.}else if c/13>c%13{4.}else{12.}
        }).collect();let max=w.iter().copied().fold(0.,f64::max);
        (0..169).filter(|&c|w[c]/max>=1e-5).map(class_label).collect::<Vec<_>>().join(",")
    }).collect();
    let menu=m["bet_menu"].as_str().unwrap();let mut rows=vec![];
    let sizing=StreetSizing{bet:parse_sizes(menu).unwrap(),raise:parse_sizes("100").unwrap(),donk:parse_sizes(menu).unwrap()};
    for b in m["boards"].as_array().unwrap() {
        let board=b["board"].as_str().unwrap();
        for (pot,stack) in [(39.5,182.),(93.5,155.)] {
            let spot=Spot::new_with_limit(SpotConfig{board:board.into(),range_oop:ranges[0].clone(),range_ip:ranges[1].clone(),
                tree:TreeConfig{starting_pot:pot,effective_stack:stack,rake_pct:0.04,rake_cap:6.,max_raises:1,
                    oop:[sizing.clone(),sizing.clone(),sizing.clone()],ip:[sizing.clone(),sizing.clone(),sizing.clone()],..Default::default()}},Some(2_000_000)).unwrap();
            let full_arenas=(spot.tree.data_size[0]+spot.tree.data_size[1])*8;
            for iso in [false,true] {
                let plan=GpuPlan::build(&spot,iso);
                let packed_arenas=(plan.arena_elements[0]+plan.arena_elements[1]) as u64*8;
                rows.push(json!({"board":board,"pot":pot,"future_card_orbits":iso,"suit_permutations":spot.suit_perms.len(),
                    "staging_bytes":plan.staging_bytes(),"packed_arena_bytes":packed_arenas,"full_arena_bytes":full_arenas,
                    "planned_compact_bytes":plan.staging_bytes()+packed_arenas}));
            }
        }
    }
    std::fs::write(&args[2],serde_json::to_vec_pretty(&json!({"manifest":m,"rows":rows,
        "note":"CPU planning only. No CUDA allocations or strategy evaluation. Excludes per-context overhead. Packed arenas require an appropriate GPU budget; current F32 constructor prefers full arenas if the budget permits."})).unwrap()).unwrap();
}
