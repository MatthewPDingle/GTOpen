//! Complete physical-holding observations for each preflop decision.
#[allow(dead_code)]
#[path="research_sampled/state.rs"] mod state;
#[allow(dead_code)]
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[allow(dead_code)]
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
use poker_reference_v1::{Game,key};
use observation_v1::Observation;
use serde_json::{Value,json};
fn main()->Result<(),Box<dyn std::error::Error>> {
    let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),1);
    let source=std::fs::read_to_string(&args[0])?;
    let c:Value=serde_json::from_str(&source)?;let game=Game::new(&c);let mut rows=Vec::new();
    for (node,&kind) in game.kinds.iter().enumerate() {
        if kind!=0 {continue;}
        let actor=game.actors[node] as usize;
        for a in 0u8..52 {for b in a+1..52 {
            let mut deal=[0u8;9];deal[actor*2]=a;deal[actor*2+1]=b;
            let o=Observation::decode(key(&deal,actor,Some(node),0,0,0));let k=o.key();
            let n=o.legal_actions(&game);
            rows.push(json!({"node":node,"hand":[a,b],"observation":{
                "hi":k.0.to_string(),"lo":k.1.to_string(),"actor":actor,"phase":0,"n":n,
                "active_features":o.features().iter().enumerate().filter(|(_,v)|**v!=0.)
                    .map(|(i,_)|i).collect::<Vec<_>>()}}));
        }}
    }
    println!("{}",json!({"format":1,"context_source":source,"rows":rows}));Ok(())
}
