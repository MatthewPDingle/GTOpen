//! Bounded observable-query cache for one batch of sampled physical deals.
//! The cache contains no values, regrets, opponent cards or future-card features.
use std::collections::BTreeMap;
use super::poker_reference_v1::{Game,Key,key};
use super::observation_v1::Observation;
use super::state::State;

pub struct Queries {
 pub observations:Vec<Observation>,pub arities:Vec<usize>,
 raw:BTreeMap<Key,usize>,canonical:BTreeMap<Key,usize>,limit:usize,
}
impl Queries {
 pub fn build(g:&Game,deals:&[[u8;9]],limit:usize)->Result<Self,&'static str>{
  if deals.is_empty()||limit==0{return Err("empty batch or zero query budget");}
  let mut q=Self{observations:vec![],arities:vec![],raw:BTreeMap::new(),canonical:BTreeMap::new(),limit};
  for d in deals{
   let mut seen=0u64;for &c in d{if c>=52||seen&(1u64<<c)!=0{return Err("invalid physical deal");}seen|=1u64<<c;}
   for n in 0..g.kinds.len(){match g.kinds[n]{
    0=>q.add(g,key(d,g.actors[n]as usize,Some(n),0,0,0),g.arities[n]as usize)?,
    2=>q.post(g,d,n,State::root(&g.configs[n]),1)?,_=>{}
   }}
  }Ok(q)
 }
 fn add(&mut self,g:&Game,k:Key,n:usize)->Result<(),&'static str>{
  if let Some(&i)=self.raw.get(&k){assert_eq!(self.arities[i],n);return Ok(());}
  if self.raw.len()>=self.limit{return Err("registered raw-query budget exceeded");}
  let o=Observation::decode(k);assert_eq!(o.legal_actions(g),n);let canonical=o.key();
  let i=if let Some(&i)=self.canonical.get(&canonical){assert_eq!(self.arities[i],n);i}else{
   let i=self.observations.len();self.observations.push(o);self.arities.push(n);self.canonical.insert(canonical,i);i
  };self.raw.insert(k,i);Ok(())
 }
 fn post(&mut self,g:&Game,d:&[u8;9],b:usize,s:State,h:u64)->Result<(),&'static str>{
  if s.kind==1{return self.post(g,d,b,s.deal(),(h<<3)|5);}if s.kind>=2{return Ok(());}
  let actions=s.actions(&g.configs[b]);self.add(g,key(d,s.player as usize,None,b,s.street as usize,h),actions.len())?;
  for(a,action)in actions.into_iter().enumerate(){self.post(g,d,b,s.act(&g.configs[b],action),(h<<3)|(a as u64+1))?;}
  Ok(())
 }
 pub fn lookup(&self,k:Key)->Option<usize>{self.raw.get(&k).copied()}
 pub fn raw_len(&self)->usize{self.raw.len()}
 pub fn rows(&self)->impl Iterator<Item=(Key,usize)>+'_ {self.raw.iter().map(|(&k,&i)|(k,i))}
}
