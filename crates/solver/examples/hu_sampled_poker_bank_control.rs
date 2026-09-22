//! Verify physical-poker behavioral model averaging by independent root-model draws.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[path="research_sampled/network_v1.rs"] mod network_v1;
#[path="research_sampled/policy_bank_v1.rs"] mod policy_bank_v1;
use poker_reference_v1::{Game,Key,key};use observation_v1::Observation;use network_v1::Network;
use state::State;use serde_json::{Value,json};use std::collections::BTreeMap;
type Distribution=BTreeMap<(usize,u64),f64>;

fn post(g:&Game,d:&[u8;9],branch:usize,s:State,h:u64,mass:f64,out:&mut Distribution,policy:&impl Fn(Key,usize)->[f64;4]){
 if mass==0.{return;}if s.kind==1{post(g,d,branch,s.deal(),(h<<3)|5,mass,out,policy);return;}
 if s.kind>=2{*out.entry((branch,h)).or_default()+=mass;return;}
 let acts=s.actions(&g.configs[branch]);let p=policy(key(d,s.player as usize,None,branch,s.street as usize,h),acts.len());
 for(a,act)in acts.into_iter().enumerate(){post(g,d,branch,s.act(&g.configs[branch],act),(h<<3)|(a as u64+1),mass*p[a],out,policy);}
}
fn pre(g:&Game,d:&[u8;9],node:usize,mass:f64,out:&mut Distribution,policy:&impl Fn(Key,usize)->[f64;4]){
 if mass==0.{return;}match g.kinds[node]{
  0=>{let n=g.arities[node]as usize;let p=policy(key(d,g.actors[node]as usize,Some(node),0,0,0),n);
   for a in 0..n{pre(g,d,g.children[node*4+a]as usize,mass*p[a],out,policy);}},
  2=>post(g,d,node,State::root(&g.configs[node]),1,mass,out,policy),
  _=>{*out.entry((node,0)).or_default()+=mass;}
 }
}
fn difference(a:&Distribution,b:&Distribution)->f64{
 a.keys().chain(b.keys()).map(|k|(a.get(k).copied().unwrap_or(0.)-b.get(k).copied().unwrap_or(0.)).abs()).fold(0.,f64::max)
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),4);assert!(!std::path::Path::new(&args[3]).exists());let started=std::time::Instant::now();
 let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;let g=Game::new(&context);assert_eq!(g.kinds.len(),15);
 let cards:Value=serde_json::from_slice(&std::fs::read(&args[1])?)?;let fixture:Value=serde_json::from_slice(&std::fs::read(&args[2])?)?;
 let networks=[Network::new(&fixture["networks"][0]),Network::new(&fixture["networks"][1])];let weights=[[1.,2.,4.],[3.,2.,1.]];
 let model=|index:usize,k:Key,n:usize|{
  if index==0{let mut p=[0.;4];p[..n].fill(1./n as f64);p}
  else{networks[((k.1>>42)&1)as usize].policy(&g,k,n,index-1)}
 };
 let mut maximum_error=0f64;let mut naive_error=0f64;let mut outcomes=0;let mut prefix_queries=0;
 for id in fixture["deal_indices"].as_array().unwrap().iter().take(4){
  let d:[u8;9]=cards["deals"][id.as_u64().unwrap()as usize].as_array().unwrap().iter().map(|c|c.as_u64().unwrap()as u8).collect::<Vec<_>>().try_into().unwrap();
  let mut expected=Distribution::new();
  for m0 in 0..3{for m1 in 0..3{
   let conditional=|k:Key,n:usize|model(if(k.1>>42)&1==0{m0}else{m1},k,n);
   pre(&g,&d,0,weights[0][m0]/7.*weights[1][m1]/6.,&mut expected,&conditional);
  }}
  let mut actual=Distribution::new();let averaged=|k:Key,n:usize|policy_bank_v1::average(&g,k,n,&weights[((k.1>>42)&1)as usize],&model).0;
  pre(&g,&d,0,1.,&mut actual,&averaged);
  let mut naive=Distribution::new();let incorrect=|k:Key,n:usize|{
   let w=weights[((k.1>>42)&1)as usize];let mut p=[0.;4];for m in 0..3{let q=model(m,k,n);for a in 0..n{p[a]+=w[m]/w.iter().sum::<f64>()*q[a];}}p
  };pre(&g,&d,0,1.,&mut naive,&incorrect);
  assert!((expected.values().sum::<f64>()-1.).abs()<1e-12&&(actual.values().sum::<f64>()-1.).abs()<1e-12);
  maximum_error=maximum_error.max(difference(&expected,&actual));naive_error=naive_error.max(difference(&expected,&naive));outcomes+=expected.len();
  // Every history reconstruction sees the same player's cards and only earlier board cards.
  for node in 0..g.kinds.len(){if g.kinds[node]==0{
   let k=key(&d,g.actors[node]as usize,Some(node),0,0,0);let o=Observation::decode(k);
   for(prior,a,n)in policy_bank_v1::own_history(&g,k){let p=Observation::decode(prior);assert_eq!(p.actor,o.actor);assert_eq!(p.phase,0);assert!(a<n);prefix_queries+=1;}
  }}
 }
 assert!(maximum_error<1e-12&&naive_error>1e-4&&prefix_queries>0);
 // An unreachable branch cannot gain support from a model that always folds at entry.
 let first=fixture["deal_indices"][0].as_u64().unwrap()as usize;
 let d:[u8;9]=cards["deals"][first].as_array().unwrap().iter().map(|c|c.as_u64().unwrap()as u8).collect::<Vec<_>>().try_into().unwrap();
 let k=key(&d,0,None,2,0,1);let n=State::root(&g.configs[2]).actions(&g.configs[2]).len();
 let fold=|_:usize,_:Key,_:usize|[1.,0.,0.,0.];let(p,support)=policy_bank_v1::average(&g,k,n,&[100.],&fold);
 assert_eq!(support,0.);assert!(p[..n].iter().all(|v|(*v-1./n as f64).abs()<1e-15));
 let result=json!({"passed":true,"physical_deals":4,"model_pairs_per_deal":9,"distinct_terminal_outcomes_summed":outcomes,
  "maximum_root_mixture_terminal_probability_error":maximum_error,"naive_probability_average_negative_control_error":naive_error,
  "preflop_own_history_checks":prefix_queries,"zero_own_reach_support_control":true,"seconds":started.elapsed().as_secs_f64(),
  "scope":"Physical-observation model-bank averaging with synthetic models. No learned poker accuracy or GPU inference qualification.","production_modified":false});
 std::fs::write(&args[3],serde_json::to_vec_pretty(&result)?)?;println!("{}",result);Ok(())
}
