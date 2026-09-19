//! Tree-only memory sizing. No solver arenas, CUDA or server calls.
use solver::{TreeConfig,StreetSizing,parse_sizes,parse_cards,tree::TreeBuilder};
use serde_json::json;
fn main(){
    let mut rows=vec![];
    for menu in ["50 75","50"] {for (pot,stack) in [(39.5,182.),(93.5,155.)] {
        let sizing=StreetSizing{bet:parse_sizes(menu).unwrap(),raise:parse_sizes("100").unwrap(),donk:parse_sizes(menu).unwrap()};
        let cfg=TreeConfig{starting_pot:pot,effective_stack:stack,rake_pct:0.04,rake_cap:6.,max_raises:1,
            oop:[sizing.clone(),sizing.clone(),sizing.clone()],ip:[sizing.clone(),sizing.clone(),sizing],..Default::default()};
        let tree=TreeBuilder::build_with_limit(&cfg,&parse_cards("KhQd9d").unwrap(),[1176,1176],Some(5_000_000)).unwrap();
        let arena=(tree.data_size[0]+tree.data_size[1])*8;
        rows.push(json!({"menu":menu,"pot":pot,"nodes":tree.nodes.len(),"f32_regret_and_strategy_bytes":arena,
            "note":"Lower bound only: excludes GPU reaches/CFVs, tables, metadata and host staging."}));
    }}
    println!("{}",serde_json::to_string_pretty(&rows).unwrap());
}
