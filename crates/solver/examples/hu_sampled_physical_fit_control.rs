//! Physical observation training-data export and trained-weight reload control.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[path="research_sampled/network_v1.rs"] mod network_v1;
#[path="research_sampled/policy_walk_v1.rs"] mod policy_walk_v1;
use poker_reference_v1::{Game,Key,sample_seed};
use observation_v1::Observation;
use network_v1::Network;
use policy_walk_v1::PolicyWalk;
use serde_json::{Value,json};
use std::collections::{BTreeMap,BTreeSet};

fn read(path:&str)->Value{serde_json::from_slice(&std::fs::read(path).unwrap()).unwrap()}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=std::env::args().skip(1).collect();assert_eq!(a.len(),5);assert!(!std::path::Path::new(&a[4]).exists());
 let g=Game::new(&read(&a[1]));let data=read(&a[2]);let fixture=read(&a[3]);
 let nets=[Network::new(&fixture["networks"][0]),Network::new(&fixture["networks"][1])];
 let result=if a[0]=="export"{
  let mut ids=BTreeMap::<Key,usize>::new();let mut observations=Vec::new();let mut records=Vec::new();
  let mut phases=BTreeSet::new();let mut branches=BTreeSet::new();let mut totals=Vec::new();
  for (i,index)in fixture["deal_indices"].as_array().unwrap().iter().enumerate(){
   let d:[u8;9]=data["deals"][index.as_u64().unwrap()as usize].as_array().unwrap().iter().map(|c|c.as_u64().unwrap()as u8).collect::<Vec<_>>().try_into().unwrap();
   for updater in 0..2{for repeat in 0..4{
    let policy=|k:Key,n:usize|nets[((k.1>>42)&1)as usize].policy(&g,k,n,0);
    let mut walk=PolicyWalk::new(&g,&policy,&d,updater,sample_seed(2026092401,i*8+updater*4+repeat));
    let value=walk.pre(0);totals.push(json!([i,updater,repeat,value]));
    for r in walk.records{
     let o=Observation::decode(r.key);let n=r.tag.unsigned_abs()as usize;assert_eq!(o.legal_actions(&g),n);
     assert_eq!(o.actor,if r.tag>0{updater}else{1-updater});assert!(r.values.iter().all(|v|v.is_finite()));assert!(r.values[n..].iter().all(|v|*v==0.));
     let k=o.key();let id=if let Some(&id)=ids.get(&k){id}else{
      let id=observations.len();ids.insert(k,id);let x=o.features();assert_eq!(Observation::from_features(&x),o);
      observations.push(json!({"hi":k.0.to_string(),"lo":k.1.to_string(),"actor":o.actor,"phase":o.phase,"n":n,
       "active_features":x.iter().enumerate().filter_map(|(i,v)|if *v==1.{Some(i)}else{None}).collect::<Vec<_>>() }));id
     };
     phases.insert(o.phase);if o.phase>0{branches.insert(o.public_id);}
     records.push(json!([id,updater,r.tag,r.values]));
    }
   }}
  }
  assert_eq!(phases,BTreeSet::from([0,1,2,3]));assert_eq!(branches,BTreeSet::from([2,5,8]));
  json!({"observations":observations,"records":records,"traversals":totals,"phases":phases,"postflop_branches":branches,
   "scope":"Physical deals, fixed synthetic behavior, full legal external-sampling updates. Fixed-data fit control, not self-play."})
 }else{
  assert_eq!(a[0],"infer");let mut rows=Vec::new();
  for row in data["observations"].as_array().unwrap(){
   let k=(row["hi"].as_str().unwrap().parse()?,row["lo"].as_str().unwrap().parse()?);let o=Observation::decode(k);
   let n=row["n"].as_u64().unwrap()as usize;assert_eq!(o.legal_actions(&g),n);
   let x=o.features();let active:Vec<_>=x.iter().enumerate().filter_map(|(i,v)|if *v==1.{Some(i)}else{None}).collect();
   assert_eq!(json!(active),row["active_features"]);
   rows.push(json!({"scores":nets[o.actor].scores(&x),"policy":nets[o.actor].policy(&g,k,n,0)}));
  }json!({"rows":rows})
 };
 std::fs::write(&a[4],serde_json::to_vec(&result)?)?;println!("{}",json!({"mode":a[0],"output":a[4]}));Ok(())
}
