//! Fixed-policy physical-deal expectations. No best-response action selection.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation_v1;
#[path="research_sampled/batch_queries_v1.rs"] mod batch_queries_v1;
use poker_reference_v1::{Game,Key,key};
use batch_queries_v1::Queries;
use state::State;
use serde_json::{Value,json};

fn winner(d:&[u8;9])->i32{
 let ranks:[u32;2]=std::array::from_fn(|p|{let mut c=[0;7];c[..2].copy_from_slice(&d[p*2..p*2+2]);c[2..].copy_from_slice(&d[4..]);solver::evaluator::evaluate7(&c)});
 if ranks[0]==ranks[1]{-1}else{(ranks[1]>ranks[0])as i32}
}
fn post(g:&Game,d:&[u8;9],b:usize,s:State,h:u64,w:i32,p:&impl Fn(Key,usize)->[f64;4])->[f64;2]{
 let cfg=&g.configs[b];
 if s.kind==1{return post(g,d,b,s.deal(),(h<<3)|5,w,p);}
 if s.kind>=2{let v=s.payouts(cfg);return std::array::from_fn(|i|g.offsets[b*2+i]+
  if s.kind==2{if i==s.player as usize{v[1]}else{v[0]}}else if w<0{v[2]}else if i==w as usize{v[0]}else{v[1]});}
 let acts=s.actions(cfg);let row=p(key(d,s.player as usize,None,b,s.street as usize,h),acts.len());let mut out=[0.;2];
 for(a,act)in acts.into_iter().enumerate(){let v=post(g,d,b,s.act(cfg,act),(h<<3)|(a as u64+1),w,p);for i in 0..2{out[i]+=row[a]*v[i];}}
 out
}
fn pre(g:&Game,d:&[u8;9],n:usize,w:i32,p:&impl Fn(Key,usize)->[f64;4])->[f64;2]{
 match g.kinds[n]{
  1=>[g.offsets[n*2],g.offsets[n*2+1]],
  2=>post(g,d,n,State::root(&g.configs[n]),1,w,p),
  3=>{let cfg=&g.configs[n];let amount=cfg.starting_pot/2.;let gross=cfg.rake_pct*2.*amount;let rake=if cfg.rake_cap>0.{gross.min(cfg.rake_cap)}else{gross};
   std::array::from_fn(|i|g.offsets[n*2+i]+if w<0{-rake/2.}else if i==w as usize{amount-rake}else{-amount})},
  0=>{let na=g.arities[n]as usize;let row=p(key(d,g.actors[n]as usize,Some(n),0,0,0),na);let mut out=[0.;2];
   for a in 0..na{let v=pre(g,d,g.children[n*4+a]as usize,w,p);for i in 0..2{out[i]+=row[a]*v[i];}}out},
  _=>panic!("invalid node")
 }
}
// Separate forward mass propagation and actual-investment accounting. No use of
// State::payouts, Game::offsets, or the reverse expectation recursion above.
fn forward(g:&Game,c:&Value,d:&[u8;9],w:i32,p:&impl Fn(Key,usize)->[f64;4])->([f64;2],f64,f64,usize){
 let mut stack=vec![(0usize,None,0u64,1f64)];let mut value=[0.;2];let mut mass=0.;let mut expected_rake=0.;let mut terminals=0;
 let dead=c["dead_money"].as_f64().unwrap();
 while let Some((n,state,h,reach))=stack.pop(){
  let node=&c["nodes"][n];
  if let Some(s)=state{
   let s:State=s;let cfg=&g.configs[n];
   if s.kind==1{stack.push((n,Some(s.deal()),(h<<3)|5,reach));continue;}
   if s.kind==0{let acts=s.actions(cfg);let row=p(key(d,s.player as usize,None,n,s.street as usize,h),acts.len());
    for(a,act)in acts.into_iter().enumerate(){stack.push((n,Some(s.act(cfg,act)),(h<<3)|(a as u64+1),reach*row[a]));}continue;}
   let invested:[f64;2]=std::array::from_fn(|i|node["invested"][i].as_f64().unwrap()+s.put[i]-cfg.starting_pot/2.);
   let matched=invested[0].min(invested[1]);let pot=2.*matched+dead;
   let gross=pot*c["rake_fraction"].as_f64().unwrap();let cap=c["rake_cap"].as_f64().unwrap();let rake=if cap>0.{gross.min(cap)}else{gross};
   let winning=if s.kind==2{1-s.player as i32}else{w};
   for i in 0..2{value[i]+=reach*(-matched+if winning<0{(pot-rake)/2.}else if winning==i as i32{pot-rake}else{0.});}
   expected_rake+=reach*rake;mass+=reach;terminals+=1;
  }else{
   match g.kinds[n]{
    0=>{let na=g.arities[n]as usize;let row=p(key(d,g.actors[n]as usize,Some(n),0,0,0),na);
     for a in 0..na{stack.push((g.children[n*4+a]as usize,None,0,reach*row[a]));}},
    2=>stack.push((n,Some(State::root(&g.configs[n])),1,reach)),
    kind=>{let invested:[f64;2]=std::array::from_fn(|i|node["invested"][i].as_f64().unwrap());
     let pot=node["pot"].as_f64().unwrap();let winning=if kind==1{node["winner"].as_i64().unwrap()as i32}else{w};
     let gross=pot*c["rake_fraction"].as_f64().unwrap();let cap=c["rake_cap"].as_f64().unwrap();let rake=if kind==1{0.}else if cap>0.{gross.min(cap)}else{gross};
     for i in 0..2{value[i]+=reach*(-invested[i]+if winning<0{(pot-rake)/2.}else if winning==i as i32{pot-rake}else{0.});}
     expected_rake+=reach*rake;mass+=reach;terminals+=1;
    }
   }
  }
 }
 (value,mass,expected_rake,terminals)
}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let a:Vec<_>=std::env::args().skip(1).collect();assert_eq!(a.len(),4);assert!(!std::path::Path::new(&a[3]).exists());
 let cs=std::fs::read_to_string(&a[0])?;let bs=std::fs::read_to_string(&a[1])?;
 let c:Value=serde_json::from_str(&cs)?;let b:Value=serde_json::from_str(&bs)?;let g=Game::new(&c);
 assert_eq!(b["format"],2);let limit=b["query_limit"].as_u64().unwrap()as usize;assert!(limit<=1_000_000);
 let deals:Vec<[u8;9]>=b["deals"].as_array().unwrap().iter().map(|r|r.as_array().unwrap().iter().map(|v|{let x=v.as_u64().unwrap();assert!(x<52);x as u8}).collect::<Vec<_>>().try_into().unwrap()).collect();
 let q=Queries::build(&g,&deals,limit)?;let transport:Value=serde_json::from_slice(&std::fs::read(&a[2])?)?;
 assert_eq!(transport["format"],1);assert_eq!(transport["context_source"].as_str(),Some(cs.as_str()));assert_eq!(transport["batch_source"].as_str(),Some(bs.as_str()));
 let profiles=transport["profiles"].as_array().unwrap();assert!(!profiles.is_empty()&&profiles.len()<=32);
 let mut out=vec![];let mut names=std::collections::BTreeSet::new();let mut maximum_error=0f64;let mut conservation_error=0f64;
 for profile in profiles{
  let name=profile["name"].as_str().unwrap();assert!(!name.is_empty()&&names.insert(name));
  let rows=profile["policies"].as_array().unwrap();assert_eq!(rows.len(),q.observations.len());let mut policies=vec![];
  for(i,row)in rows.iter().enumerate(){let o=&q.observations[i];let k=o.key();let n=q.arities[i];
   assert_eq!(row["hi"],k.0.to_string());assert_eq!(row["lo"],k.1.to_string());assert_eq!(row["actor"].as_u64().unwrap()as usize,o.actor);assert_eq!(row["n"].as_u64().unwrap()as usize,n);
   let p:[f64;4]=row["probabilities"].as_array().unwrap().iter().map(|v|v.as_f64().unwrap()).collect::<Vec<_>>().try_into().unwrap();
   assert!(p.iter().all(|v|v.is_finite()&&*v>=0.)&&p[n..].iter().all(|v|*v==0.)&&(p[..n].iter().sum::<f64>()-1.).abs()<1e-12);policies.push(p);
  }
  let policy=|k:Key,n:usize|{let i=q.lookup(k).expect("missing visible observation");assert_eq!(n,q.arities[i]);policies[i]};let mut values=vec![];
  for(did,d)in deals.iter().enumerate(){let w=winner(d);let value=pre(&g,d,0,w,&policy);let(expected,mass,rake,terminals)=forward(&g,&c,d,w,&policy);
   for i in 0..2{maximum_error=maximum_error.max((value[i]-expected[i]).abs());assert!(value[i].is_finite());}
   assert!((mass-1.).abs()<1e-12);conservation_error=conservation_error.max((value[0]+value[1]+rake-c["dead_money"].as_f64().unwrap()).abs());
   values.push(json!({"deal_index":did,"values":value,"expected_rake":rake,"terminal_mass":mass,"terminal_templates":terminals}));
  }
  out.push(json!({"name":name,"deals":values}));
 }
 assert!(maximum_error<1e-10&&conservation_error<1e-10);
 std::fs::write(&a[3],serde_json::to_vec(&json!({"format":1,"profiles":out,"maximum_forward_cashflow_error":maximum_error,
  "maximum_conservation_error":conservation_error,"fixed_policy_evaluation_only":true,"bounds_best_response_above":false}))?)?;Ok(())
}
