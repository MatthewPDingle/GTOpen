//! Public chip state for a fixed, equal-stack HU research context. No policy or cards.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
use state::State;
use poker_reference_v1::Game;
use serde_json::{Value,json};
use solver::tree::Action;
use std::collections::BTreeMap;
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3);
 assert!(!std::path::Path::new(&args[2]).exists());
 let source=std::fs::read_to_string(&args[0])?;let c:Value=serde_json::from_str(&source)?;
 let queries:Value=serde_json::from_slice(&std::fs::read(&args[1])?)?;
 assert_eq!(queries["context_source"].as_str().unwrap(),source);
 let g=Game::new(&c);let total=c["config"]["stack"].as_f64().unwrap();
 let dead=c["dead_money"].as_f64().unwrap();let mut rows:BTreeMap<u64,Value>=BTreeMap::new();
 for o in queries["observations"].as_array().unwrap(){
  let hi:u64=o["hi"].as_str().unwrap().parse()?;
  let actor=o["actor"].as_u64().unwrap() as usize;assert!(actor<2);
  let phase=o["phase"].as_u64().unwrap() as usize;
  if let Some(prior)=rows.get(&hi){assert_eq!(prior["actor"],o["actor"]);assert_eq!(prior["phase"],o["phase"]);assert_eq!(prior["actions"].as_array().unwrap().len(),o["n"].as_u64().unwrap() as usize);continue;}
  let mut invested:[f64;2];let mut actions=vec![];let pot;let facing;
  if hi>>63==0{
   assert!(hi>0);let n=&c["nodes"][(hi-1)as usize];assert!(n["leaf"].is_null());
   assert_eq!(n["actor"].as_u64().unwrap() as usize,actor);assert_eq!(phase,0);
   invested=std::array::from_fn(|p|n["invested"][p].as_f64().unwrap());
   pot=n["pot"].as_f64().unwrap();facing=(invested[1-actor]-invested[actor]).max(0.);
   for(a,child)in n["actions"].as_array().unwrap().iter().zip(n["children"].as_array().unwrap()){
    let next=&c["nodes"][child.as_u64().unwrap()as usize];
    let inc=next["invested"][actor].as_f64().unwrap()-invested[actor];
    actions.push(json!({"kind":a["kind"],"increment":inc,"all_in":inc>0.&&(total-invested[actor]-inc).abs()<1e-8}));
   }
  }else{
   let branch=(hi&15)as usize;let n=&c["nodes"][branch];let cfg=&g.configs[branch];
   assert_eq!(n["leaf"]["type"],"postflop");
   let base:[f64;2]=std::array::from_fn(|p|n["invested"][p].as_f64().unwrap());
   assert!((base[0]-base[1]).abs()<1e-9,"Unequal-stack/side-pot contexts not admitted");
   assert!((cfg.effective_stack-(total-base[0])).abs()<1e-9);
   let mut encoded=(hi&!(1u64<<63))>>4;let mut history=vec![];
   while encoded>1{history.push((encoded&7)as usize);encoded>>=3;}assert_eq!(encoded,1);history.reverse();
   let mut s=State::root(cfg);
   for token in history{if token==5{s=s.deal();}else{assert!((1..=4).contains(&token));let acts=s.actions(cfg);s=s.act(cfg,acts[token-1]);}}
   assert_eq!(s.kind,0);assert_eq!(s.player as usize,actor);assert_eq!(s.street as usize+1,phase);
   invested=std::array::from_fn(|p|base[p]+s.put[p]-cfg.starting_pot/2.);
   pot=s.put.iter().sum();facing=(s.put[1-actor]-s.put[actor]).max(0.);
   for a in s.actions(cfg){
    let next=s.act(cfg,a);let inc=next.put[actor]-s.put[actor];
    let kind=match a{Action::Fold=>"fold",Action::Check=>"check",Action::Call(_)=>"call",Action::Bet(_)=>"bet",Action::Raise(_)=>"raise"};
    actions.push(json!({"kind":kind,"increment":inc,"all_in":inc>0.&&(total-invested[actor]-inc).abs()<1e-8}));
   }
  }
  assert!((invested.iter().sum::<f64>()+dead-pot).abs()<1e-8);
  assert_eq!(actions.len(),o["n"].as_u64().unwrap()as usize);
  for x in &mut invested{assert!(*x>=-1e-8&&*x<=total+1e-8);*x=x.max(0.).min(total);}
  rows.insert(hi,json!({"hi":hi.to_string(),"actor":actor,"phase":phase,"starting_stacks":[total,total],
   "invested":invested,"remaining":[total-invested[0],total-invested[1]],"dead_money":dead,"pot":pot,
   "call_cost":facing,"rake_fraction":c["rake_fraction"],"rake_cap":c["rake_cap"],"actions":actions}));
 }
 let result=json!({"format":1,"context_source":source,"public_states":rows.values().collect::<Vec<_>>(),
  "scope":"Public ledger extraction for fixed equal-stack HU context; no private-card inputs, trained model or cross-stack qualification."});
 std::fs::write(&args[2],serde_json::to_vec(&result)?)?;println!("{} public states",rows.len());Ok(())
}
