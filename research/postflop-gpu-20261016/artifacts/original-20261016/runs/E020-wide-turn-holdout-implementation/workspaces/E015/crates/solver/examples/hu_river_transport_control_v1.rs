//! CPU-only qualification of a research river replacement hook.
#![allow(dead_code)]
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[path="research_sampled/policy_walk_allin_v1.rs"] mod baseline;
#[path="research_sampled/policy_walk_river_conditional_v1.rs"] mod candidate;
use poker_reference_v1::{Game,Key};
use observation_v1::Observation;
use serde::Deserialize;
use serde_json::json;
use std::{collections::BTreeMap,cell::RefCell,io::{Read,Write},fs::OpenOptions};

#[derive(Deserialize)] #[serde(deny_unknown_fields)]
struct Row {hi:String,lo:String,n:usize,p:[f64;4]}
#[derive(Deserialize)] #[serde(deny_unknown_fields)]
struct Target {hi:String,lo:String,n:usize,values:[f64;4],policy_id:String}
#[derive(Deserialize)] #[serde(deny_unknown_fields)]
struct Input {format:u32,context_source:String,policy_id:String,rows:Vec<Row>,target:Target,pairs:Vec<[u8;2]>,seeds:Vec<u64>}

fn bounded(path:&str,limit:u64)->Result<String,Box<dyn std::error::Error>> {
 let mut s=String::new();std::fs::File::open(path)?.take(limit+1).read_to_string(&mut s)?;assert!(s.len()as u64<=limit);Ok(s)
}
fn check<F:Fn(Key,usize)->[f64;4],R:Fn(Key,usize)->Option<[f64;4]>,S:Fn(Key,usize)->Option<[f64;4]>>(
 a:&candidate::PolicyWalk<F,R>,b:&candidate::PolicyWalk<F,S>,target:Key,exact:[f64;4])->(f64,usize,f64) {
 assert_eq!(a.rng,b.rng);assert_eq!(a.records.len(),b.records.len());let mut delta=vec![0.;a.records.len()];
 let mut child=vec![[None;4];a.records.len()];let mut error=0f64;let mut replaced=0;
 for(i,f)in a.frames.iter().enumerate(){if let Some((p,action))=f.parent{assert!(p<i);assert!(child[p][action].replace(i).is_none());}}
 for i in (0..a.records.len()).rev() {
  let x=&a.records[i];let y=&b.records[i];let f=&a.frames[i];let g=&b.frames[i];
  assert_eq!(x.key,y.key);assert_eq!(x.tag,y.tag);assert_eq!(f.parent,g.parent);assert_eq!(f.selected,g.selected);assert_eq!(f.probabilities,g.probabilities);
  let n=x.tag.unsigned_abs()as usize;let replace=x.tag>0&&Observation::decode(x.key).key()==target;
  assert_eq!(g.replaced,replace);let mut actions=f.action_values;
  for j in 0..n{if let Some(c)=child[i][j]{actions[j]+=delta[c];}}
  if replace{actions=exact;replaced+=1;}
  let returned=if let Some(j)=f.selected{actions[j]}else{(0..n).map(|j|f.probabilities[j]*actions[j]).sum()};
  for j in 0..4 {
   error=error.max((actions[j]-g.action_values[j]).abs());
   let want=if x.tag<0{f.probabilities[j]}else if j<n{actions[j]-returned}else{0.};
   error=error.max((want-y.values[j]).abs());
  }
  error=error.max((returned-g.returned).abs());delta[i]=returned-f.returned;
 }
 assert!(error<1e-9);(error,replaced,delta.first().copied().unwrap_or(0.))
}

fn main()->Result<(),Box<dyn std::error::Error>> {
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3);assert!(!std::path::Path::new(&args[2]).exists());
 let context=bounded(&args[0],16_000_000)?;let raw=bounded(&args[1],16_000_000)?;let input:Input=serde_json::from_str(&raw)?;
 assert_eq!(input.format,1);assert_eq!(input.context_source,context);assert!(!input.policy_id.is_empty());assert_eq!(input.policy_id,input.target.policy_id);
 let game=Game::new(&serde_json::from_str(&context)?);let mut table=BTreeMap::new();
 assert!(!input.rows.is_empty()&&input.rows.len()<=250_000);
 for row in &input.rows {
  let key=(row.hi.parse()?,row.lo.parse()?);let o=Observation::decode(key);assert_eq!(o.key(),key);assert_eq!(o.legal_actions(&game),row.n);
  assert!((2..=4).contains(&row.n)&&row.p.iter().all(|x|x.is_finite()&&*x>=0.)&&row.p[row.n..].iter().all(|x|*x==0.)&&(row.p.iter().sum::<f64>()-1.).abs()<1e-12);
  assert!(table.insert(key,(row.n,row.p)).is_none());
 }
 let target=(input.target.hi.parse()?,input.target.lo.parse()?);let observation=Observation::decode(target);
 assert_eq!(target,observation.key());assert_eq!(observation.phase,3);assert_eq!(observation.legal_actions(&game),input.target.n);
 assert_eq!(table.get(&target).unwrap().0,input.target.n);
 let exact=input.target.values;assert!(exact.iter().all(|x|x.is_finite())&&exact[input.target.n..].iter().all(|x|*x==0.));
 assert!(!input.pairs.is_empty()&&input.pairs.len()<=16&&!input.seeds.is_empty()&&input.seeds.len()<=16);
 let queries=RefCell::new(Vec::new());
 let policy=|k:Key,n:usize|{queries.borrow_mut().push((k,n));let canonical=Observation::decode(k).key();if let Some(&(arity,p))=table.get(&canonical){assert_eq!(n,arity);p}else{let mut p=[0.;4];p[..n].fill(1./n as f64);p}};
 let disabled=|_:Key,_:usize|None;
 let replacement=|k:Key,n:usize|{if Observation::decode(k).key()==target{assert_eq!(n,input.target.n);Some(exact)}else{None}};
 let mut reports=Vec::new();let mut largest=0f64;let mut original_visits=0usize;let mut full_hits=0;let mut direct_hits=0;
 for pair in &input.pairs {
  assert!(pair[0]<pair[1]&&pair[1]<52&&pair.iter().all(|c|!observation.cards.contains(c)));
  let mut deal=[0;9];let hero=observation.actor;deal[hero*2..hero*2+2].copy_from_slice(&observation.cards[..2]);deal[(1-hero)*2..(1-hero)*2+2].copy_from_slice(pair);deal[4..].copy_from_slice(&observation.cards[2..]);
  for &seed in &input.seeds {for updater in 0..2 {
   // Equity 0.5 is a shared fixed preflop-leaf control, not a new measured equity.
   queries.borrow_mut().clear();let mut old=baseline::PolicyWalk::new(&game,&policy,&deal,updater,seed,0.5);let old_value=old.pre(0);let old_queries=queries.replace(Vec::new());
   let mut no=candidate::PolicyWalk::new(&game,&policy,&disabled,&deal,updater,seed,0.5);let no_value=no.pre(0);let no_queries=queries.replace(Vec::new());
   assert_eq!(old_value,no_value);assert_eq!(old.rng,no.rng);assert_eq!(old.records.len(),no.records.len());assert_eq!(old_queries,no_queries);
   for(a,b)in old.records.iter().zip(&no.records){assert_eq!(a.key,b.key);assert_eq!(a.tag,b.tag);assert_eq!(a.values,b.values);}
   let mut yes=candidate::PolicyWalk::new(&game,&policy,&replacement,&deal,updater,seed,0.5);let value=yes.pre(0);let yes_queries=queries.replace(Vec::new());assert_eq!(old_queries,yes_queries);
   let(error,hits,delta)=check(&no,&yes,target,exact);assert!((value-no_value-delta).abs()<1e-9);assert!(hits<=1);largest=largest.max(error);full_hits+=hits;original_visits+=old.records.len();
   reports.push(json!({"mode":"preflop-root","pair":pair,"seed":seed,"updater":updater,"visits":old.records.len(),"replacements":hits,"original_value":old_value,"new_value":value,"root_delta":delta,"maximum_error":error}));
  }
   let branch=observation.public_id;let cfg=&game.configs[branch];let mut state=state::State::root(cfg);let mut history=1;
   for &token in &observation.history{state=if token==5{state.deal()}else{state.act(cfg,state.actions(cfg)[token as usize-1])};history=(history<<3)|token as u64;}
   let mut no=candidate::PolicyWalk::new(&game,&policy,&disabled,&deal,hero,seed,0.5);let old_value=no.post(branch,state,history);let no_queries=queries.replace(Vec::new());
   let mut yes=candidate::PolicyWalk::new(&game,&policy,&replacement,&deal,hero,seed,0.5);let value=yes.post(branch,state,history);let yes_queries=queries.replace(Vec::new());assert_eq!(no_queries,yes_queries);
   let(error,hits,delta)=check(&no,&yes,target,exact);assert_eq!(hits,1);assert!((value-old_value-delta).abs()<1e-9);largest=largest.max(error);direct_hits+=hits;
   reports.push(json!({"mode":"target-root","pair":pair,"seed":seed,"updater":hero,"visits":no.records.len(),"replacements":hits,"original_value":old_value,"new_value":value,"root_delta":delta,"maximum_error":error,"regrets":yes.records[0].values}));
  }
 }
 let result=json!({"passed":true,"complete":true,"policy_id":input.policy_id,"original_visits":original_visits,"full_root_replacements":full_hits,"direct_replacements":direct_hits,"maximum_error":largest,"reports":reports,"production_modified":false});
 let mut bytes=serde_json::to_vec(&result)?;bytes.push(b'\n');assert!(bytes.len()<8_000_000);let mut f=OpenOptions::new().write(true).create_new(true).open(&args[2])?;f.write_all(&bytes)?;f.sync_all()?;println!("{}",json!({"passed":true,"full_replacements":full_hits,"direct_replacements":direct_hits,"visits":original_visits}));Ok(())
}
