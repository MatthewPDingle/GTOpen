//! Research file bridge: visible query rows -> external batched policy -> updates.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[path="research_sampled/policy_walk_v1.rs"] mod policy_walk_v1;
#[path="research_sampled/batch_queries_v1.rs"] mod batch_queries_v1;
use poker_reference_v1::{Game,Key,sample_seed};use observation_v1::Observation;
use policy_walk_v1::PolicyWalk;use batch_queries_v1::Queries;
use serde_json::{Value,json};use std::collections::BTreeMap;

fn read(p:&str)->Value{serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap()}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=std::env::args().skip(1).collect();assert_eq!(a.len(),5);assert!(!std::path::Path::new(&a[4]).exists());
 assert!(matches!(a[0].as_str(),"queries"|"walk"|"verify"));
 let context_source=std::fs::read_to_string(&a[1])?;let batch_source=std::fs::read_to_string(&a[2])?;
 let context:Value=serde_json::from_str(&context_source)?;let batch:Value=serde_json::from_str(&batch_source)?;let g=Game::new(&context);
 assert_eq!(batch["format"],2);assert!(!batch["batch_id"].as_str().unwrap().is_empty());
 let limit=batch["query_limit"].as_u64().unwrap()as usize;assert!(limit<=1_000_000);
 let seed=batch["seed"].as_u64().unwrap();
 let deals:Vec<[u8;9]>=batch["deals"].as_array().unwrap().iter().map(|r|r.as_array().unwrap().iter().map(|c|{
  let x=c.as_u64().unwrap();assert!(x<52);x as u8
 }).collect::<Vec<_>>().try_into().unwrap()).collect();
 let q=Queries::build(&g,&deals,limit)?;
 let result=if a[0]=="queries"{
  let rows:Vec<_>=q.observations.iter().zip(&q.arities).map(|(o,&n)|{
   let k=o.key();let x=o.features();json!({"hi":k.0.to_string(),"lo":k.1.to_string(),"actor":o.actor,"phase":o.phase,"n":n,
    "active_features":x.iter().enumerate().filter_map(|(i,v)|if *v==1.{Some(i)}else{None}).collect::<Vec<_>>()})
  }).collect();
  json!({"format":2,"context_source":context_source,"batch_source":batch_source,"raw_queries":q.raw_len(),"observations":rows})
 }else{
  let external=read(&a[3]);assert_eq!(external["format"],2);
  assert!(external["context_source"].as_str()==Some(context_source.as_str()),"stale game context");
  assert!(external["batch_source"].as_str()==Some(batch_source.as_str()),"stale sample batch");
  let rows=external["policies"].as_array().unwrap();assert_eq!(rows.len(),q.observations.len());
  let mut policies=Vec::new();let mut reference=BTreeMap::<Key,(usize,[f64;4])>::new();
  for(i,row)in rows.iter().enumerate(){
   let o=&q.observations[i];let k=o.key();let n=q.arities[i];
   assert_eq!(row["hi"],k.0.to_string());assert_eq!(row["lo"],k.1.to_string());
   assert_eq!(row["actor"].as_u64().unwrap()as usize,o.actor);assert_eq!(row["n"].as_u64().unwrap()as usize,n);
   let p:[f64;4]=row["probabilities"].as_array().unwrap().iter().map(|v|v.as_f64().unwrap()).collect::<Vec<_>>().try_into().unwrap();
   assert!(p.iter().all(|v|v.is_finite()&&*v>=0.));assert!(p[n..].iter().all(|v|*v==0.));assert!((p[..n].iter().sum::<f64>()-1.).abs()<1e-12);
   policies.push(p);assert!(reference.insert(k,(n,p)).is_none());
  }
  let cached=|k:Key,n:usize|{let i=q.lookup(k).expect("missing query");assert_eq!(n,q.arities[i]);policies[i]};
  let direct=|k:Key,n:usize|{let o=Observation::decode(k);assert_eq!(o.legal_actions(&g),n);let &(expected,p)=reference.get(&o.key()).unwrap();assert_eq!(n,expected);p};
  let mut records=Vec::new();let mut roots=Vec::new();let mut verified=0;let mut error=0f64;
  for(i,d)in deals.iter().enumerate(){for updater in 0..2{
   let rng=sample_seed(seed,i*2+updater);let mut walk=PolicyWalk::new(&g,&cached,d,updater,rng);let value=walk.pre(0);
   if a[0]=="verify"{
    let mut independent=PolicyWalk::new(&g,&direct,d,updater,rng);let expected=independent.pre(0);
    error=error.max((value-expected).abs());assert_eq!(walk.rng,independent.rng);assert_eq!(walk.records.len(),independent.records.len());
    for(x,y)in walk.records.iter().zip(&independent.records){assert_eq!(x.key,y.key);assert_eq!(x.tag,y.tag);for a in 0..4{error=error.max((x.values[a]-y.values[a]).abs());}}
    verified+=1;
   }
   for r in walk.records{let id=q.lookup(r.key).unwrap();let o=&q.observations[id];assert_eq!(o.actor,if r.tag>0{updater}else{1-updater});
    records.push(json!([id,updater,r.tag,r.values]));
   }roots.push(json!([i,updater,value]));
  }}
  assert_eq!(error,0.);
  json!({"format":2,"batch_id":batch["batch_id"],"roots":roots,"records":records,"observations":q.observations.len(),
   "verified_traversals":verified,"maximum_reference_error":error,"policies_frozen_across_updater_passes":true})
 };
 std::fs::write(&a[4],serde_json::to_vec(&result)?)?;println!("{}",json!({"mode":a[0],"raw_queries":q.raw_len(),"observations":q.observations.len()}));Ok(())
}
