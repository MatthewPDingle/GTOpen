//! Scalar oracle and exact observation keys for the sampled BB experiment.
use std::collections::BTreeMap;
use serde_json::Value;
use solver::{TreeConfig,StreetSizing,parse_sizes};
use super::state::State;

pub type Key=(u64,u64);
pub type Table=BTreeMap<Key,Entry>;
#[derive(Clone,Debug)]
pub struct Entry {pub n:usize,pub regret:[f64;4],pub average:[f64;4]}
impl Entry {
 pub fn policy(&self)->[f64;4]{let mut p=[0.;4];let z:f64=self.regret[..self.n].iter().map(|v|v.max(0.)).sum();
  for a in 0..self.n{p[a]=if z>0.{self.regret[a].max(0.)/z}else{1./self.n as f64};}p}
}
#[derive(Clone,Debug)]
pub struct Record {pub key:Key,pub tag:i32,pub values:[f64;4]}
pub struct Game {pub kinds:Vec<i32>,pub actors:Vec<i32>,pub arities:Vec<i32>,pub children:Vec<i32>,
 pub configs:Vec<TreeConfig>,pub constants:Vec<f64>,pub offsets:Vec<f64>}
impl Game {
 pub fn new(c:&Value)->Self {
  let mut g=Self{kinds:vec![],actors:vec![],arities:vec![],children:vec![],configs:vec![],constants:vec![],offsets:vec![]};
  let sizing=StreetSizing{bet:parse_sizes("50").unwrap(),raise:parse_sizes("100").unwrap(),donk:parse_sizes("50").unwrap()};
  for n in c["nodes"].as_array().unwrap(){
   let leaf=&n["leaf"];let kind=match leaf["type"].as_str(){None=>0,Some("fold")=>1,Some("postflop")=>2,Some("showdown")=>3,_=>panic!()};
   g.kinds.push(kind);g.actors.push(n["actor"].as_i64().unwrap_or(0) as i32);
   let children=n["children"].as_array().unwrap();g.arities.push(children.len() as i32);assert!(children.len()<=4);
   for a in 0..4{g.children.push(children.get(a).and_then(Value::as_i64).unwrap_or(-1) as i32);}
   let cfg=TreeConfig{starting_pot:leaf["starting_pot"].as_f64().unwrap_or(0.),effective_stack:leaf["effective_stack"].as_f64().unwrap_or(0.),
    rake_pct:c["rake_fraction"].as_f64().unwrap(),rake_cap:c["rake_cap"].as_f64().unwrap(),
    oop:[sizing.clone(),sizing.clone(),sizing.clone()],ip:[sizing.clone(),sizing.clone(),sizing.clone()],max_raises:1,..Default::default()};
   g.constants.extend([cfg.starting_pot,cfg.effective_stack,cfg.rake_pct,cfg.rake_cap]);g.configs.push(cfg);
   let values=if kind==1{&leaf["utilities"]}else{&leaf["value_offsets"]};
   for p in 0..2{g.offsets.push(values[p].as_f64().unwrap_or(0.));}
  }g
 }
}
pub fn key(deal:&[u8;9],player:usize,pre:Option<usize>,branch:usize,street:usize,history:u64)->Key {
 let mut own=[deal[player*2],deal[player*2+1]];own.sort();
 let mut board=[63u8;5];
 if pre.is_none(){board[..3].copy_from_slice(&deal[4..7]);board[..3].sort();if street>=1{board[3]=deal[7];}if street>=2{board[4]=deal[8];}}
 let mut lo=0u64;for (i,c)in own.into_iter().chain(board).enumerate(){lo|=(c as u64)<<(6*i);}
 lo|=(player as u64)<<42;
 let hi=if let Some(n)=pre{n as u64+1}else{assert!(branch<16&&history<(1u64<<59));(1u64<<63)|(history<<4)|branch as u64};
 (hi,lo)
}
pub fn uniform(state:&mut u64)->f64 {
 *state=state.wrapping_add(0x9e3779b97f4a7c15);let mut z=*state;
 z=(z^(z>>30)).wrapping_mul(0xbf58476d1ce4e5b9);z=(z^(z>>27)).wrapping_mul(0x94d049bb133111eb);
 ((z^(z>>31))>>11) as f64*(1./9007199254740992.)
}
pub fn sample_seed(seed:u64,sample:usize)->u64 {seed^(sample as u64).wrapping_mul(0xd1342543de82ef95)}
pub struct Walk<'a>{pub game:&'a Game,pub table:&'a Table,pub deal:&'a [u8;9],pub updater:usize,pub rng:u64,pub winner:i32,pub records:Vec<Record>}
impl<'a> Walk<'a> {
 pub fn new(game:&'a Game,table:&'a Table,deal:&'a [u8;9],updater:usize,rng:u64)->Self{
  let mut ranks=[0;2];for p in 0..2{let mut cards=[0;7];cards[..2].copy_from_slice(&deal[p*2..p*2+2]);cards[2..].copy_from_slice(&deal[4..]);ranks[p]=solver::evaluator::evaluate7(&cards);}
  let winner=if ranks[0]==ranks[1]{-1}else{(ranks[1]>ranks[0]) as i32};Self{game,table,deal,updater,rng,winner,records:vec![]}
 }
 fn begin(&mut self,k:Key,actor:usize,n:usize)->(usize,[f64;4],Option<usize>){
  let p=if let Some(e)=self.table.get(&k){assert_eq!(e.n,n);e.policy()}else{let mut p=[0.;4];p[..n].fill(1./n as f64);p};
  let index=self.records.len();self.records.push(Record{key:k,tag:if actor==self.updater{n as i32}else{-(n as i32)},values:[0.;4]});
  let selected=if actor==self.updater{None}else{let x=uniform(&mut self.rng);let mut sum=0.;let mut selected=n-1;for a in 0..n{sum+=p[a];if x<sum{selected=a;break;}}Some(selected)};
  (index,p,selected)
 }
 fn finish(&mut self,index:usize,p:[f64;4],values:[f64;4],n:usize,selected:Option<usize>)->f64 {
  if let Some(a)=selected {self.records[index].values=p;values[a]}else{
   let mut value=0.;for a in 0..n{value+=p[a]*values[a];}
   for a in 0..n{self.records[index].values[a]=values[a]-value;}value
  }
 }
 pub fn pre(&mut self,node:usize)->f64 {
  let kind=self.game.kinds[node];let cfg=&self.game.configs[node];
  if kind==1{return self.game.offsets[node*2+self.updater];}
  if kind==2{return self.post(node,State::root(cfg),1);}
  if kind==3{let amount=cfg.starting_pot/2.;let gross=cfg.rake_pct*2.*amount;let rake=if cfg.rake_cap>0.{gross.min(cfg.rake_cap)}else{gross};
   return (if self.winner<0{-rake/2.}else if self.winner==self.updater as i32{amount-rake}else{-amount})+self.game.offsets[node*2+self.updater];}
  let actor=self.game.actors[node] as usize;let n=self.game.arities[node] as usize;
  let k=key(self.deal,actor,Some(node),0,0,0);let (index,p,selected)=self.begin(k,actor,n);let mut values=[0.;4];
  for a in 0..n{if selected.is_none()||selected==Some(a){values[a]=self.pre(self.game.children[node*4+a] as usize);}}
  self.finish(index,p,values,n,selected)
 }
 fn post(&mut self,branch:usize,s:State,history:u64)->f64 {
  let cfg=&self.game.configs[branch];
  if s.kind==1{return self.post(branch,s.deal(),(history<<3)|5);}
  if s.kind>=2{let v=s.payouts(cfg);let value=if s.kind==2{if self.updater==s.player as usize{v[1]}else{v[0]}}
    else if self.winner<0{v[2]}else if self.updater==self.winner as usize{v[0]}else{v[1]};
   return value+self.game.offsets[branch*2+self.updater];}
  let actions=s.actions(cfg);let n=actions.len();let k=key(self.deal,s.player as usize,None,branch,s.street as usize,history);
  let (index,p,selected)=self.begin(k,s.player as usize,n);let mut values=[0.;4];
  for a in 0..n{if selected.is_none()||selected==Some(a){let child=s.act(&self.game.configs[branch],actions[a]);values[a]=self.post(branch,child,(history<<3)|(a as u64+1));}}
  self.finish(index,p,values,n,selected)
 }
}
