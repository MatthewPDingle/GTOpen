//! Read-only CPU census of river subgames; no solving or CUDA allocation.
//! CONTEXT MANIFEST OUTPUT. Preserves full history and canonical public cards.
use serde_json::{json, Value};
use solver::{Spot, SpotConfig, StreetSizing, TreeConfig, parse_sizes};
use solver::{cards::{card_to_string,permute_card}, game::Dealt};
use solver::preflop::equity::class_label;
use solver::tree::{KIND_ACTION,KIND_CHANCE,KIND_TERM_FOLD,KIND_TERM_SHOWDOWN,SENTINEL};
use std::{collections::BTreeMap, fs::OpenOptions, io::Write};

#[derive(Default)]
struct River {
    state_bytes:u64, actions:u64, terminals:u64, tree_nodes:u64,
    min_rake:f64, max_rake:f64,
}

fn river(spot:&Spot, root:u32)->River {
    let mut out=River{min_rake:f64::INFINITY,..Default::default()};
    let mut todo=vec![root];
    while let Some(i)=todo.pop() {
        let n=&spot.tree.nodes[i as usize];out.tree_nodes+=1;
        assert_eq!(n.street,2);
        match n.kind {
            KIND_ACTION=>{
                out.actions+=1;
                out.state_bytes+=8*n.num_children as u64*spot.hands[n.player as usize].len() as u64;
                for a in 0..n.num_children as usize {todo.push(spot.tree.children[n.children_start as usize+a]);}
            }
            KIND_TERM_FOLD|KIND_TERM_SHOWDOWN=>{
                out.terminals+=1;
                let rake=-(n.t_win+n.t_lose);
                let pot=if n.kind==KIND_TERM_FOLD {2.*n.put[0].min(n.put[1])} else {n.put[0]+n.put[1]};
                let gross=pot*spot.config.tree.rake_pct;
                let expected=if spot.config.tree.rake_cap>0. {gross.min(spot.config.tree.rake_cap)} else {gross};
                assert!((rake-expected).abs()<1e-9,"terminal cashflow/rake mismatch");
                if n.kind==KIND_TERM_SHOWDOWN {assert!((2.*n.t_tie+rake).abs()<1e-9);}
                out.min_rake=out.min_rake.min(rake);out.max_rake=out.max_rake.max(rake);
            }
            _=>panic!("chance or unknown node inside river"),
        }
    }
    assert!(out.terminals>0 && out.min_rake.is_finite());out
}

fn census(spot:&Spot)->Value {
    // A tree-node ID retains betting history; cards alone are never an identity.
    let mut todo=vec![(0u32,Dealt::default())];
    let mut trunk_bytes=[0u64;2];let mut trunk_actions=0u64;
    let mut count=0u64;let mut river_bytes=0u64;let mut river_actions=0u64;
    let mut constant=0u64;let mut variable=0u64;let mut max_state=0u64;
    let mut hist:BTreeMap<(u64,u64,u64,u64,u64,u64,u64),(u64,Value)>=BTreeMap::new();
    let mut max_game=Value::Null;
    while let Some((i,dealt))=todo.pop() {
        let n=&spot.tree.nodes[i as usize];
        if n.kind==KIND_ACTION && dealt.len==2 {
            assert_eq!(n.player,0);assert!((n.put[0]-n.put[1]).abs()<1e-9);
            let r=river(spot,i);count+=1;river_bytes+=r.state_bytes;river_actions+=r.actions;
            let is_constant=(r.max_rake-r.min_rake).abs()<1e-9;
            if is_constant {constant+=1;} else {variable+=1;}
            let pot=n.put[0]+n.put[1];
            let stack=spot.config.tree.starting_pot/2.+spot.config.tree.effective_stack-n.put[0];
            assert!(stack>0.);
            let board=spot.config.board.clone()+&dealt.cards[..2].iter().map(|&c|card_to_string(c)).collect::<String>();
            let key=(pot.to_bits(),stack.to_bits(),r.state_bytes,r.actions,r.tree_nodes,r.min_rake.to_bits(),r.max_rake.to_bits());
            let sample=json!({"original_root_node":i,"board":board,"starting_pot":pot,"remaining_stack":stack,
                "state_bytes":r.state_bytes,"action_nodes":r.actions,"tree_nodes":r.tree_nodes,
                "terminals":r.terminals,"min_terminal_rake":r.min_rake,"max_terminal_rake":r.max_rake,
                "constant_sum_local_subgame":is_constant});
            hist.entry(key).or_insert((0,sample.clone())).0+=1;
            if r.state_bytes>max_state {max_state=r.state_bytes;max_game=sample;}
            continue;
        }
        match n.kind {
            KIND_ACTION=>{
                assert!(n.street<2);trunk_actions+=1;
                trunk_bytes[n.street as usize]+=8*n.num_children as u64*spot.hands[n.player as usize].len() as u64;
                for a in 0..n.num_children as usize {todo.push((spot.tree.children[n.children_start as usize+a],dealt));}
            }
            KIND_CHANCE=>{
                let perms=spot.perms_fixing(&dealt);
                for c in 0..52u8 {
                    let child=spot.tree.children[n.children_start as usize+c as usize];
                    if child==SENTINEL || dealt.contains(c) {continue;}
                    let rep=perms.iter().map(|&k|permute_card(c,&spot.suit_perms[k])).min().unwrap();
                    if c==rep {todo.push((child,dealt.push(c)));}
                }
            }
            _=>{}
        }
    }
    let nh=spot.hands[0].len() as u64+spot.hands[1].len() as u64;
    let entries:Vec<_>=hist.values().map(|(n,s)|{let mut v=s.clone();v["subgames"]=json!(n);v}).collect();
    json!({"trunk_state_bytes":trunk_bytes,"river_state_bytes":river_bytes,
        "trunk_action_nodes":trunk_actions,"river_action_nodes":river_actions,
        "river_subgames":count,"constant_sum_local_subgames":constant,"variable_sum_local_subgames":variable,
        "boundary_f64_values_only_bytes":count*nh*8,
        "boundary_f64_values_and_denominators_plus_headers_bytes":count*(nh*16+64),
        "full_flop_hand_counts":[spot.hands[0].len(),spot.hands[1].len()],
        "max_river_state_bytes":max_state,"max_river":max_game,"histogram":entries,
        "note":"Boundary estimate uses both players' full flop hand vectors, including hands blocked on river. Two f64 vectors per player plus a 64-byte header is a planning allowance, not a validated resolving format."})
}

fn main()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3);
    assert!(!std::path::Path::new(&args[2]).exists(),"preserve evidence");
    let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
    let manifest:Value=serde_json::from_slice(&std::fs::read(&args[1])?)?;
    assert_eq!(context["schema"],"hu-context-v1");
    let ranges:Vec<String>=(0..2).map(|p| {
        let weights:Vec<f64>=(0..169).map(|c|context["incoming_class_mass"][p][c].as_f64().unwrap()/
            if c/13==c%13 {6.} else if c/13>c%13 {4.} else {12.}).collect();
        let max=weights.iter().copied().fold(0.,f64::max);assert!(max>0.);
        (0..169).filter(|&c|weights[c]/max>=1e-5).map(class_label).collect::<Vec<_>>().join(",")
    }).collect();
    let sizing=StreetSizing {bet:parse_sizes(manifest["bet_menu"].as_str().unwrap())?,raise:parse_sizes("100")?,
        donk:parse_sizes(manifest["bet_menu"].as_str().unwrap())?};
    let mut rows=Vec::new();
    for board in manifest["boards"].as_array().unwrap() {
        for (leaf,node) in context["nodes"].as_array().unwrap().iter().enumerate() {
            if node["leaf"]["type"]!="postflop" {continue;}
            let spot=Spot::new_with_limit(SpotConfig {
                board:board["board"].as_str().unwrap().into(),range_oop:ranges[0].clone(),range_ip:ranges[1].clone(),
                tree:TreeConfig {starting_pot:node["leaf"]["starting_pot"].as_f64().unwrap(),
                    effective_stack:node["leaf"]["effective_stack"].as_f64().unwrap(),
                    rake_pct:context["rake_fraction"].as_f64().unwrap(),rake_cap:context["rake_cap"].as_f64().unwrap(),
                    max_raises:1,oop:[sizing.clone(),sizing.clone(),sizing.clone()],
                    ip:[sizing.clone(),sizing.clone(),sizing.clone()],..Default::default()}
            },Some(2_000_000))?;
            let mut row=census(&spot);row["board"]=board["board"].clone();row["preflop_leaf"]=json!(leaf);
            println!("RIVER_FRONTIER {} leaf={} subgames={} boundary_bytes={}",board["board"],leaf,
                row["river_subgames"],row["boundary_f64_values_and_denominators_plus_headers_bytes"]);
            rows.push(row);
        }
    }
    let result=json!({"rows":rows,"manifest":manifest,"device_allocated":false,"strategies_evaluated":false});
    OpenOptions::new().create_new(true).write(true).open(&args[2])?.write_all(&serde_json::to_vec_pretty(&result)?)?;
    Ok(())
}
