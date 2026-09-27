//! Research-only public topology and visible observations on one fixed runout.
#[allow(dead_code)]
#[path="research_sampled/state.rs"] mod state;
#[allow(dead_code)]
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[allow(dead_code)]
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
use poker_reference_v1::{Game,key};
use observation_v1::Observation;
use serde_json::{Value,json};
use state::State;

fn visit(g:&Game,b:usize,s:State,h:u64,board:&[u8;5],hands:&[Vec<[u8;2]>;2],nodes:&mut Vec<Value>)->usize {
    let id=nodes.len();nodes.push(Value::Null);
    let mut row=json!({"kind":s.kind,"actor":s.player,"street":s.street,"put":s.put});
    if s.kind==0 {
        let actions=s.actions(&g.configs[b]);
        let mut observations=Vec::new();
        for hand in &hands[s.player as usize] {
            // key reads only this actor's cards and the visible board prefix.
            let mut deal=[0u8;9];deal[s.player as usize*2..s.player as usize*2+2].copy_from_slice(hand);
            deal[4..].copy_from_slice(board);
            let o=Observation::decode(key(&deal,s.player as usize,None,b,s.street as usize,h));
            assert_eq!(o.legal_actions(g),actions.len());
            let k=o.key();
            observations.push(json!({"hi":k.0.to_string(),"lo":k.1.to_string(),"actor":o.actor,
                "phase":o.phase,"n":actions.len(),"active_features":o.features().iter().enumerate()
                    .filter(|(_,v)|**v!=0.).map(|(i,_)|i).collect::<Vec<_>>() }));
        }
        row["observations"]=json!(observations);
        row["children"]=json!(actions.into_iter().enumerate().map(|(a,act)|
            visit(g,b,s.act(&g.configs[b],act),(h<<3)|(a as u64+1),board,hands,nodes)).collect::<Vec<_>>());
    } else if s.kind==1 {
        row["children"]=json!([visit(g,b,s.deal(),(h<<3)|5,board,hands,nodes)]);
    } else { row["payouts"]=json!(s.payouts(&g.configs[b])); }
    nodes[id]=row;id
}

fn main()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),2);
    let c:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
    let request:Value=serde_json::from_slice(&std::fs::read(&args[1])?)?;
    let board:[u8;5]=serde_json::from_value(request["board"].clone())?;
    let hands:[Vec<[u8;2]>;2]=serde_json::from_value(request["hands"].clone())?;
    let mut board_mask=0u64;for &card in &board {assert!(card<52&&board_mask&(1<<card)==0);board_mask|=1<<card;}
    let mut ranks=[Vec::new(),Vec::new()];
    for p in 0..2 {
        assert!(!hands[p].is_empty()&&hands[p].len()<=1081);
        let mut unique=std::collections::BTreeSet::new();
        for &hand in &hands[p] {
            assert!(hand[0]<hand[1]&&hand[1]<52&&unique.insert(hand));
            assert_eq!(board_mask&((1u64<<hand[0])|(1u64<<hand[1])),0);
            ranks[p].push(solver::evaluator::evaluate7(&[hand[0],hand[1],board[0],board[1],board[2],board[3],board[4]]));
        }
    }
    let g=Game::new(&c);let mut branches=Vec::new();
    for (b,&kind) in g.kinds.iter().enumerate() {
        if kind!=2 {continue;}
        let mut nodes=Vec::new();assert_eq!(visit(&g,b,State::root(&g.configs[b]),1,&board,&hands,&mut nodes),0);
        branches.push(json!({"branch":b,"offsets":[g.offsets[b*2],g.offsets[b*2+1]],
            "starting_pot":g.configs[b].starting_pot,"nodes":nodes}));
    }
    println!("{}",json!({"format":1,"board":board,"hands":hands,"ranks":ranks,"branches":branches}));Ok(())
}
