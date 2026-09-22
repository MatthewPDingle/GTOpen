//! Physical-poker neural adapter qualification against the frozen scalar traversal.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[path="research_sampled/network_v1.rs"] mod network_v1;
#[path="research_sampled/policy_walk_v1.rs"] mod policy_walk_v1;
use poker_reference_v1::{Game,Key,Table,Entry,Walk,key,sample_seed};
use observation_v1::Observation;
use network_v1::Network;
use policy_walk_v1::PolicyWalk;
use state::State;
use serde_json::{Value,json};
use std::collections::BTreeSet;

fn add(table:&mut Table,key:Key,p:[f64;4],n:usize){
 if let Some(e)=table.get(&key){assert_eq!(e.n,n);for a in 0..n{assert!((e.policy()[a]-p[a]).abs()<1e-12);}}
 else{table.insert(key,Entry{n,regret:p,average:[0.;4]});}
}
fn enumerate(g:&Game,d:&[u8;9],branch:usize,s:State,h:u64,table:&mut Table,policy:&impl Fn(Key,usize)->[f64;4]){
 if s.kind==1{enumerate(g,d,branch,s.deal(),(h<<3)|5,table,policy);return;}if s.kind>=2{return;}
 let acts=s.actions(&g.configs[branch]);let k=key(d,s.player as usize,None,branch,s.street as usize,h);
 add(table,k,policy(k,acts.len()),acts.len());
 for(a,act)in acts.into_iter().enumerate(){enumerate(g,d,branch,s.act(&g.configs[branch],act),(h<<3)|(a as u64+1),table,policy);}
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),4);assert!(!std::path::Path::new(&args[3]).exists());
 let began=std::time::Instant::now();
 let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;let g=Game::new(&context);
 assert_eq!(context["positions"],json!(["BB","BTN"]));assert_eq!(g.kinds.len(),15);
 let input:Value=serde_json::from_slice(&std::fs::read(&args[1])?)?;
 let fixture:Value=serde_json::from_slice(&std::fs::read(&args[2])?)?;
 let networks=[Network::new(&fixture["networks"][0]),Network::new(&fixture["networks"][1])];
 let mut golden_error=0f64;let mut golden_policy_error=0f64;let mut golden_count=0;
 for row in fixture["golden"].as_array().unwrap(){
  let k=(row["hi"].as_str().unwrap().parse()?,row["lo"].as_str().unwrap().parse()?);
  let o=Observation::decode(k);let net=&networks[o.actor];let values=net.scores(&o.features());let n=row["n"].as_u64().unwrap()as usize;
  let p=net.policy(&g,k,n,0);
  for a in 0..4{golden_error=golden_error.max((values[a]-row["scores"][a].as_f64().unwrap()).abs());golden_policy_error=golden_policy_error.max((p[a]-row["policy"][a].as_f64().unwrap()).abs());}
  golden_count+=1;
 }assert!(golden_error<2e-6&&golden_policy_error<2e-6);
 let deals:Vec<[u8;9]>=fixture["deal_indices"].as_array().unwrap().iter().map(|i|input["deals"][i.as_u64().unwrap()as usize].as_array().unwrap().iter().map(|v|v.as_u64().unwrap()as u8).collect::<Vec<_>>().try_into().unwrap()).collect();
 let mut results=Vec::new();let mut phases=BTreeSet::new();let mut branches=BTreeSet::new();let mut arities=BTreeSet::new();let mut signs=BTreeSet::new();
 let mut max_error=0f64;let mut total_records=0;let mut total_traversals=0;
 for variant in 0..4{
  let policy=|k:Key,n:usize|networks[((k.1>>42)&1)as usize].policy(&g,k,n,variant);
  let mut table=Table::new();
  for d in &deals{for node in 0..g.kinds.len(){match g.kinds[node]{
   0=>{let n=g.arities[node]as usize;let k=key(d,g.actors[node]as usize,Some(node),0,0,0);add(&mut table,k,policy(k,n),n);},
   2=>enumerate(&g,d,node,State::root(&g.configs[node]),1,&mut table,&policy),_=>{}}}}
  let mut records=0;let mut zero_actions=0;
  for (i,d)in deals.iter().enumerate(){for updater in 0..2{
   let seed=sample_seed(2026092301+variant as u64,i*2+updater);
   let mut baseline=Walk::new(&g,&table,d,updater,seed);let expected=baseline.pre(0);
   let mut neural=PolicyWalk::new(&g,&policy,d,updater,seed);let actual=neural.pre(0);
   assert_eq!(baseline.rng,neural.rng);assert_eq!(baseline.records.len(),neural.records.len());
   max_error=max_error.max((expected-actual).abs());
   for(a,b)in baseline.records.iter().zip(&neural.records){
    assert_eq!(a.key,b.key);assert_eq!(a.tag,b.tag);let n=b.tag.unsigned_abs()as usize;
    let o=Observation::decode(b.key);assert_eq!(o.legal_actions(&g),n);assert_eq!(Observation::from_features(&o.features()),o);
    assert_eq!(o.actor,if b.tag>0{updater}else{1-updater});assert!(b.values.iter().all(|v|v.is_finite()));assert!(b.values[n..].iter().all(|&v|v==0.));
    phases.insert(o.phase);arities.insert(n);signs.insert(b.tag.signum());if o.phase>0{branches.insert(o.public_id);}
    let p=policy(b.key,n);zero_actions+=p[..n].iter().filter(|&&v|v==0.).count();
    for j in 0..4{max_error=max_error.max((a.values[j]-b.values[j]).abs());}records+=1;
   }total_traversals+=1;
  }}total_records+=records;
  results.push(json!({"variant":variant,"materialized_oracle_entries":table.len(),"records":records,"zero_probability_actions_at_visited_observations":zero_actions}));
 }
 assert!(max_error<1e-10);assert_eq!(phases,BTreeSet::from([0,1,2,3]));assert_eq!(branches,BTreeSet::from([2,5,8]));assert_eq!(arities,BTreeSet::from([2,3,4]));assert_eq!(signs,BTreeSet::from([-1,1]));
 let result=json!({"passed":true,"golden_observations":golden_count,"maximum_numpy_score_error":golden_error,"maximum_numpy_policy_error":golden_policy_error,
  "maximum_traversal_record_or_value_error":max_error,"physical_deals":deals.len(),"traversals":total_traversals,"records":total_records,"phases":phases,"postflop_branches":branches,"legal_arities":arities,"variants":results,"seconds":began.elapsed().as_secs_f64(),
  "scope":"Synthetic neural weights only. Observable policy callback, legal masking, sampling and update-label equivalence; not trained poker strength or GPU inference qualification.","production_modified":false});
 std::fs::write(&args[3],serde_json::to_vec_pretty(&result)?)?;println!("{}",json!({"passed":true,"records":total_records,"traversals":total_traversals,"maximum_error":max_error,"seconds":began.elapsed().as_secs_f64()}));Ok(())
}
