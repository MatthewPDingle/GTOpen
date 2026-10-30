//! Export visible own-history links and qualify a streamed physical policy bank.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[path="research_sampled/batch_queries_v1.rs"] mod batch_queries_v1;
#[path="research_sampled/policy_bank_v1.rs"] mod policy_bank_v1;
use poker_reference_v1::{Game,Key,key};use observation_v1::Observation;
use batch_queries_v1::Queries;use state::State;
use serde_json::{Value,json};use std::collections::BTreeMap;
type Distribution=BTreeMap<(usize,u64),f64>;

fn post(g:&Game,d:&[u8;9],branch:usize,s:State,h:u64,mass:f64,out:&mut Distribution,p:&impl Fn(Key,usize)->[f64;4]){
 if mass==0.{return;}if s.kind==1{post(g,d,branch,s.deal(),(h<<3)|5,mass,out,p);return;}
 if s.kind>=2{*out.entry((branch,h)).or_default()+=mass;return;}
 let acts=s.actions(&g.configs[branch]);let row=p(key(d,s.player as usize,None,branch,s.street as usize,h),acts.len());
 for(a,act)in acts.into_iter().enumerate(){post(g,d,branch,s.act(&g.configs[branch],act),(h<<3)|(a as u64+1),mass*row[a],out,p);}
}
fn pre(g:&Game,d:&[u8;9],node:usize,mass:f64,out:&mut Distribution,p:&impl Fn(Key,usize)->[f64;4]){
 if mass==0.{return;}match g.kinds[node]{
  0=>{let n=g.arities[node]as usize;let row=p(key(d,g.actors[node]as usize,Some(node),0,0,0),n);
   for a in 0..n{pre(g,d,g.children[node*4+a]as usize,mass*row[a],out,p);}},
  2=>post(g,d,node,State::root(&g.configs[node]),1,mass,out,p),
  _=>{*out.entry((node,0)).or_default()+=mass;}
 }
}
fn difference(a:&Distribution,b:&Distribution)->f64{
 a.keys().chain(b.keys()).map(|k|(a.get(k).copied().unwrap_or(0.)-b.get(k).copied().unwrap_or(0.)).abs()).fold(0.,f64::max)
}
fn probability(row:&Value,n:usize)->[f64;4]{
 let p:[f64;4]=row.as_array().unwrap().iter().map(|v|v.as_f64().unwrap()).collect::<Vec<_>>().try_into().unwrap();
 assert!(p.iter().all(|v|v.is_finite()&&*v>=0.)&&p[n..].iter().all(|v|*v==0.));
 assert!((p[..n].iter().sum::<f64>()-1.).abs()<1e-12);p
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=std::env::args().skip(1).collect();assert_eq!(a.len(),5);assert!(matches!(a[0].as_str(),"queries"|"verify"));
 assert!(!std::path::Path::new(&a[4]).exists());
 let context_source=std::fs::read_to_string(&a[1])?;let batch_source=std::fs::read_to_string(&a[2])?;
 let context:Value=serde_json::from_str(&context_source)?;let batch:Value=serde_json::from_str(&batch_source)?;
 let g=Game::new(&context);assert_eq!(batch["format"],2);
 let limit=batch["query_limit"].as_u64().unwrap()as usize;assert!(limit<=1_000_000);
 let deals:Vec<[u8;9]>=batch["deals"].as_array().unwrap().iter().map(|r|r.as_array().unwrap().iter().map(|c|{
  let x=c.as_u64().unwrap();assert!(x<52);x as u8
 }).collect::<Vec<_>>().try_into().unwrap()).collect();
 let q=Queries::build(&g,&deals,limit)?;
 let ids:BTreeMap<_,_>=q.observations.iter().enumerate().map(|(i,o)|(o.key(),i)).collect();assert_eq!(ids.len(),q.observations.len());
 let id=|k:Key|*ids.get(&Observation::decode(k).key()).expect("ancestor observation missing");
 let result=if a[0]=="queries"{
  let rows:Vec<_>=q.observations.iter().zip(&q.arities).map(|(o,&n)|{
   let k=o.key();let x=o.features();let history:Vec<_>=policy_bank_v1::own_history(&g,k).into_iter().map(|(prior,a,n)|{
    let i=id(prior);assert_eq!(q.observations[i].actor,o.actor);assert_eq!(q.arities[i],n);json!([i,a,n])
   }).collect();
   json!({"hi":k.0.to_string(),"lo":k.1.to_string(),"actor":o.actor,"phase":o.phase,"n":n,
    "active_features":x.iter().enumerate().filter_map(|(i,v)|if *v==1.{Some(i)}else{None}).collect::<Vec<_>>(),"own_history":history})
  }).collect();
  json!({"format":2,"context_source":context_source,"batch_source":batch_source,"observations":rows,"raw_queries":q.raw_len()})
 }else{
  let bank:Value=serde_json::from_slice(&std::fs::read(&a[3])?)?;assert_eq!(bank["format"],1);
  assert!(bank["context_source"].as_str()==Some(context_source.as_str())&&bank["batch_source"].as_str()==Some(batch_source.as_str()));
  let weights:Vec<Vec<f64>>=bank["weights_by_player"].as_array().unwrap().iter().map(|r|r.as_array().unwrap().iter().map(|x|x.as_f64().unwrap()).collect()).collect();
  assert_eq!(weights.len(),2);let count=weights[0].len();assert!((1..=8).contains(&count));assert_eq!(weights[1].len(),count);
  assert!(weights.iter().all(|w|w.iter().all(|v|v.is_finite()&&*v>0.)));
  let policies:Vec<Vec<[f64;4]>>=bank["models"].as_array().unwrap().iter().map(|r|{
   let rows=r.as_array().unwrap();assert_eq!(rows.len(),q.observations.len());rows.iter().zip(&q.arities).map(|(row,&n)|probability(row,n)).collect()
  }).collect();assert_eq!(policies.len(),count);
  let average:Vec<_>=bank["average"].as_array().unwrap().iter().zip(&q.arities).map(|(row,&n)|probability(row,n)).collect();
  assert_eq!(bank["average"].as_array().unwrap().len(),q.observations.len());
  let support:Vec<_>=bank["support"].as_array().unwrap().iter().map(|v|v.as_f64().unwrap()).collect();assert_eq!(support.len(),q.observations.len());
  let model=|m:usize,k:Key,n:usize|{let i=id(k);assert_eq!(n,q.arities[i]);policies[m][i]};
  let mut row_error=0f64;let mut support_error=0f64;let mut naive_error=0f64;
  for(i,o)in q.observations.iter().enumerate(){
   let (p,z)=policy_bank_v1::average(&g,o.key(),q.arities[i],&weights[o.actor],&model);
   support_error=support_error.max((z-support[i]).abs());
   for a in 0..4{row_error=row_error.max((p[a]-average[i][a]).abs());
    let naive=(0..count).map(|m|weights[o.actor][m]*policies[m][i][a]).sum::<f64>()/weights[o.actor].iter().sum::<f64>();
    naive_error=naive_error.max((p[a]-naive).abs());
   }
  }
  let mut terminal_error=0f64;let mut outcomes=0;
  for d in deals.iter().take(4){
   let mut expected=Distribution::new();
   for m0 in 0..count{for m1 in 0..count{
    let selected=|k:Key,n:usize|model(if (k.1>>42)&1==0{m0}else{m1},k,n);
    pre(&g,d,0,weights[0][m0]/weights[0].iter().sum::<f64>()*weights[1][m1]/weights[1].iter().sum::<f64>(),&mut expected,&selected);
   }}
   let mut actual=Distribution::new();let selected=|k:Key,n:usize|{let i=id(k);assert_eq!(n,q.arities[i]);average[i]};
   pre(&g,d,0,1.,&mut actual,&selected);
   assert!((expected.values().sum::<f64>()-1.).abs()<1e-12&&(actual.values().sum::<f64>()-1.).abs()<1e-12);
   terminal_error=terminal_error.max(difference(&expected,&actual));outcomes+=expected.len();
  }
  assert!(row_error<1e-12&&support_error<1e-12&&terminal_error<1e-12);
  json!({"passed":true,"observations":q.observations.len(),"models_per_player":count,"physical_deals":deals.len().min(4),
   "maximum_average_error":row_error,"maximum_own_reach_error":support_error,"maximum_root_mixture_terminal_error":terminal_error,
   "naive_probability_average_error":naive_error,"terminal_outcomes":outcomes,"physical_poker_convergence_qualified":false})
 };
 std::fs::write(&a[4],serde_json::to_vec(&result)?)?;Ok(())
}
