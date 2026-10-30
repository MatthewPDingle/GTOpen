//! Verify bounded batch lookup against on-demand policy evaluation and traversal.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[path="research_sampled/network_v1.rs"] mod network_v1;
#[path="research_sampled/policy_walk_v1.rs"] mod policy_walk_v1;
#[path="research_sampled/batch_queries_v1.rs"] mod batch_queries_v1;
use poker_reference_v1::{Game,Key,key,sample_seed};
use observation_v1::Observation;use network_v1::{Network,regret_policy};
use policy_walk_v1::PolicyWalk;use batch_queries_v1::Queries;
use serde_json::{Value,json};use std::collections::BTreeSet;

fn read(p:&str)->Value{serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap()}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),5);assert!(!std::path::Path::new(&args[4]).exists());
 let began=std::time::Instant::now();let g=Game::new(&read(&args[0]));let data=read(&args[1]);let fixture=read(&args[2]);let trained=read(&args[3]);
 let deals:Vec<[u8;9]>=fixture["deal_indices"].as_array().unwrap().iter().map(|i|data["deals"][i.as_u64().unwrap()as usize].as_array().unwrap().iter().map(|c|c.as_u64().unwrap()as u8).collect::<Vec<_>>().try_into().unwrap()).collect();
 let q=Queries::build(&g,&deals,100000)?;
 // Each raw query must expose exactly its own canonical observation and legal menu.
 for(k,i)in q.rows(){assert_eq!(Observation::decode(k),q.observations[i]);assert_eq!(q.observations[i].legal_actions(&g),q.arities[i]);}
 assert!(Queries::build(&g,&deals,q.raw_len()-1).is_err());assert!(Queries::build(&g,&deals,0).is_err());assert!(Queries::build(&g,&[],100000).is_err());
 let mut bad=deals.clone();bad[0][8]=bad[0][0];assert!(Queries::build(&g,&bad,100000).is_err());
 let mut duplicate=deals.clone();duplicate.extend(&deals);let repeat=Queries::build(&g,&duplicate,100000)?;
 assert_eq!(repeat.raw_len(),q.raw_len());assert_eq!(repeat.observations,q.observations);
 let reverse:Vec<_>=deals.iter().rev().copied().collect();let reordered=Queries::build(&g,&reverse,100000)?;
 for(k,i)in q.rows(){let j=reordered.lookup(k).unwrap();assert_eq!(q.observations[i],reordered.observations[j]);}
 // Changing invisible cards cannot change a preflop policy input or its lookup.
 let mut hidden_checks=0;
 for d in &deals{for n in 0..g.kinds.len(){if g.kinds[n]!=0{continue;}let actor=g.actors[n]as usize;
  let mut changed=*d;changed.swap((1-actor)*2,8);let a=key(d,actor,Some(n),0,0,0);let b=key(&changed,actor,Some(n),0,0,0);
  assert_eq!(a,b);assert_eq!(q.lookup(a),q.lookup(b));hidden_checks+=1;
 }}
 assert_eq!(q.lookup((u64::MAX,u64::MAX)),None);
 let mut maximum_policy_error=0f64;let mut maximum_record_error=0f64;let mut records=0;let mut traversals=0;let mut phases=BTreeSet::new();
 for weights in [&fixture,&trained]{
  let nets=[Network::new(&weights["networks"][0]),Network::new(&weights["networks"][1])];
  for variant in 0..4{
   let policies:Vec<[f64;4]>=q.observations.iter().zip(&q.arities).map(|(o,&n)|{
    let scores=match variant{0=>nets[o.actor].scores(&o.features()),1=>[-1.,-0.7,-0.4,-0.1],2=>[0.;4],3=>[-3.,-2.,-1.,100.],_=>unreachable!()};regret_policy(scores,n)
   }).collect();
   let cached=|k:Key,n:usize|{let i=q.lookup(k).expect("missing batch query must not silently default");assert_eq!(q.arities[i],n);policies[i]};
   let direct=|k:Key,n:usize|nets[((k.1>>42)&1)as usize].policy(&g,k,n,variant);
   for(k,i)in q.rows(){let a=cached(k,q.arities[i]);let b=direct(k,q.arities[i]);for j in 0..4{maximum_policy_error=maximum_policy_error.max((a[j]-b[j]).abs());}}
   for(i,d)in deals.iter().enumerate(){for updater in 0..2{
    let seed=sample_seed(2026092403+variant as u64,i*2+updater);
    let mut a=PolicyWalk::new(&g,&direct,d,updater,seed);let av=a.pre(0);
    let mut b=PolicyWalk::new(&g,&cached,d,updater,seed);let bv=b.pre(0);
    assert_eq!(a.rng,b.rng);assert_eq!(a.records.len(),b.records.len());maximum_record_error=maximum_record_error.max((av-bv).abs());
    for(a,b)in a.records.iter().zip(&b.records){assert_eq!(a.key,b.key);assert_eq!(a.tag,b.tag);phases.insert(Observation::decode(b.key).phase);
     for j in 0..4{maximum_record_error=maximum_record_error.max((a.values[j]-b.values[j]).abs());}records+=1;
    }traversals+=1;
   }}
  }
 }
 assert_eq!(maximum_policy_error,0.);assert_eq!(maximum_record_error,0.);assert_eq!(phases,BTreeSet::from([0,1,2,3]));
 let result=json!({"passed":true,"physical_deals":deals.len(),"raw_queries":q.raw_len(),"canonical_observations":q.observations.len(),
  "dense_feature_payload_bytes":q.observations.len()*269*4,"policy_payload_bytes":q.observations.len()*4*8,
  "query_limit":100000,"maximum_policy_error":maximum_policy_error,"maximum_traversal_record_error":maximum_record_error,
  "traversals":traversals,"records":records,"hidden_card_checks":hidden_checks,"phases":phases,
  "negative_controls":4,"duplicate_batch_identity":true,"reordered_batch_identity":true,"missing_query_is_not_uniform":true,
  "seconds":began.elapsed().as_secs_f64(),"scope":"Bounded per-batch query lookup with synthetic and fixed-data-fitted weights. No GPU timing or physical-poker strength qualification.","production_modified":false});
 std::fs::write(&args[4],serde_json::to_vec_pretty(&result)?)?;println!("{}",result);Ok(())
}
