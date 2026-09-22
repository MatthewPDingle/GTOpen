//! Compare lazy transitions against every legal native public-tree history.
#[path="research_sampled/state.rs"] mod state;
use state::{State,InfoKey};
use solver::{TreeConfig,StreetSizing,parse_sizes,parse_cards};
use solver::tree::{TreeBuilder,Tree,KIND_ACTION,KIND_CHANCE,KIND_TERM_FOLD,KIND_TERM_SHOWDOWN,SENTINEL};
use serde_json::{json,Value};

#[derive(Default)] struct Counts{nodes:u64,actions:u64,chance:u64,terminals:u64,max_depth:usize,max_actions:usize}

fn compare(tree:&Tree,node:u32,s:State,blocked:u64,depth:usize,count:&mut Counts) {
    let n=&tree.nodes[node as usize];count.nodes+=1;count.max_depth=count.max_depth.max(depth);
    assert_eq!((s.kind,s.player,s.street),(n.kind,n.player,n.street));
    for p in 0..2{assert!((s.put[p]-n.put[p]).abs()<1e-9);}
    match s.kind {
        KIND_ACTION=>{
            count.actions+=1;let actions=s.actions(&tree.config);
            count.max_actions=count.max_actions.max(actions.len());
            assert_eq!(actions,tree.actions[n.actions_start as usize..n.actions_start as usize+n.num_children as usize]);
            for(a,action)in actions.into_iter().enumerate(){
                compare(tree,tree.children[n.children_start as usize+a],s.act(&tree.config,action),blocked,depth+1,count);
            }
        }
        KIND_CHANCE=>{
            count.chance+=1;let next=s.deal();
            for card in 0..52u8{let child=tree.children[n.children_start as usize+card as usize];
                if blocked&(1u64<<card)!=0{continue;}
                assert_ne!(child,SENTINEL);compare(tree,child,next,blocked|(1u64<<card),depth+1,count);
            }
        }
        KIND_TERM_FOLD|KIND_TERM_SHOWDOWN=>{
            count.terminals+=1;let p=s.payouts(&tree.config);
            for(a,b)in p.into_iter().zip([n.t_win,n.t_lose,n.t_tie]){assert!((a-b).abs()<1e-9);}
            let pot=2.*if s.kind==KIND_TERM_FOLD{s.put[s.player as usize]}else{s.put[0]};
            let gross=pot*tree.config.rake_pct;let rake=if tree.config.rake_cap>0.{gross.min(tree.config.rake_cap)}else{gross};
            assert!((p[0]+p[1]+rake).abs()<1e-9);
        }
        _=>panic!("unknown node"),
    }
}

fn main()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3);
    assert!(!std::path::Path::new(&args[2]).exists());
    let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
    let manifest:Value=serde_json::from_slice(&std::fs::read(&args[1])?)?;
    assert_eq!(context["schema"],"hu-context-v1");
    let sizing=StreetSizing{bet:parse_sizes(manifest["bet_menu"].as_str().unwrap())?,raise:parse_sizes("100")?,donk:parse_sizes(manifest["bet_menu"].as_str().unwrap())?};
    let mut rows=vec![];let started=std::time::Instant::now();
    for b in manifest["boards"].as_array().unwrap(){
        let board=parse_cards(b["board"].as_str().unwrap())?;assert_eq!(board.len(),3);
        let mask=board.iter().fold(0u64,|m,&c|m|(1u64<<c));
        for (leaf,n)in context["nodes"].as_array().unwrap().iter().enumerate(){
            if n["leaf"]["type"]!="postflop"{continue;}
            let cfg=TreeConfig{starting_pot:n["leaf"]["starting_pot"].as_f64().unwrap(),
                effective_stack:n["leaf"]["effective_stack"].as_f64().unwrap(),
                rake_pct:context["rake_fraction"].as_f64().unwrap(),rake_cap:context["rake_cap"].as_f64().unwrap(),
                oop:[sizing.clone(),sizing.clone(),sizing.clone()],ip:[sizing.clone(),sizing.clone(),sizing.clone()],
                max_raises:1,..Default::default()};
            // Hand counts only change unused arena offsets, not legal actions.
            // No strategy/private-hand arena is allocated by either path.
            let tree=TreeBuilder::build_with_limit(&cfg,&board,[1,1],Some(2_000_000))?;
            let mut count=Counts::default();compare(&tree,0,State::root(&cfg),mask,0,&mut count);
            assert_eq!(count.nodes,count.actions+count.chance+count.terminals);
            assert!(count.nodes<=tree.nodes.len() as u64);
            let row=json!({"board":b["board"],"preflop_leaf":leaf,"native_nodes_including_invalid_repeat_cards":tree.nodes.len(),
                "legal_nodes_checked":count.nodes,"actions_checked":count.actions,"chance_checked":count.chance,
                "terminals_checked":count.terminals,"max_depth":count.max_depth,"max_actions":count.max_actions,
                "lazy_state_bytes":std::mem::size_of::<State>(),"stack_state_bytes_bound":(count.max_depth+1)*std::mem::size_of::<State>(),
                "reference_tree_bytes":tree.bytes()});
            println!("GEOMETRY {} leaf={} legal_nodes={}",b["board"],leaf,count.nodes);rows.push(row);
        }
    }
    // Full-history/private-card identity controls. No sampled hidden data is accepted.
    let k=InfoKey::new(2,0,[48,49],&[0,5,10],&[0,1,0]);
    assert_eq!(k,InfoKey::new(2,0,[49,48],&[0,5,10],&[0,1,0]));
    assert_ne!(k,InfoKey::new(5,0,[48,49],&[0,5,10],&[0,1,0]));
    assert_ne!(k,InfoKey::new(2,0,[48,49],&[0,5,10],&[1,0,0]));
    assert_ne!(k,InfoKey::new(2,0,[48,50],&[0,5,10],&[0,1,0]));
    assert_ne!(InfoKey::new(2,0,[48,49],&[0,5,10,12,16],&[0,0]),InfoKey::new(2,0,[48,49],&[0,5,10,16,12],&[0,0]));
    let result=json!({"passed":true,"rows":rows,"manifest":manifest,"seconds":started.elapsed().as_secs_f64(),
        "device_allocated":false,"strategy_arenas_allocated":false,"information_key_controls_passed":true,
        "scope":"All native legal public histories for supplied flops/branches; exact transitions, actions and terminal payouts. No private sampling, showdown evaluator, training or performance claim."});
    std::fs::write(&args[2],serde_json::to_vec_pretty(&result)?)?;Ok(())
}
