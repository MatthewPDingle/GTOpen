//! Separate research estimator: integrate unseen boards at preflop all-in leaves only.
use super::poker_reference_v1::{Game,Key,Record,key,uniform};
use super::state::State;

pub struct PolicyWalk<'a,F:Fn(Key,usize)->[f64;4]>{
 pub game:&'a Game,pub policy:&'a F,pub deal:&'a [u8;9],pub updater:usize,
 pub rng:u64,pub winner:i32,pub records:Vec<Record>,pub allin_equity:f64,
}
impl<'a,F:Fn(Key,usize)->[f64;4]> PolicyWalk<'a,F>{
 pub fn new(game:&'a Game,policy:&'a F,deal:&'a [u8;9],updater:usize,rng:u64,allin_equity:f64)->Self{
  assert!(allin_equity.is_finite()&&(0. ..=1.).contains(&allin_equity));
  let mut ranks=[0;2];for p in 0..2{let mut c=[0;7];c[..2].copy_from_slice(&deal[p*2..p*2+2]);c[2..].copy_from_slice(&deal[4..]);ranks[p]=solver::evaluator::evaluate7(&c);}
  Self{game,policy,deal,updater,rng,allin_equity,winner:if ranks[0]==ranks[1]{-1}else{(ranks[1]>ranks[0])as i32},records:vec![]}
 }
 fn begin(&mut self,k:Key,actor:usize,n:usize)->(usize,[f64;4],Option<usize>){
  let p=(self.policy)(k,n);assert!((2..=4).contains(&n));
  assert!(p.iter().all(|v|v.is_finite()&&*v>=0.));assert!(p[n..].iter().all(|v|*v==0.));assert!((p[..n].iter().sum::<f64>()-1.).abs()<1e-12);
  let index=self.records.len();self.records.push(Record{key:k,tag:if actor==self.updater{n as i32}else{-(n as i32)},values:[0.;4]});
  let selected=if actor==self.updater{None}else{
   let x=uniform(&mut self.rng);let mut sum=0.;let mut a=n-1;
   for i in 0..n{sum+=p[i];if x<sum{a=i;break;}}Some(a)
  };(index,p,selected)
 }
 fn finish(&mut self,index:usize,p:[f64;4],v:[f64;4],n:usize,selected:Option<usize>)->f64{
  if let Some(a)=selected{self.records[index].values=p;v[a]}else{
   let expected=(0..n).map(|a|p[a]*v[a]).sum::<f64>();
   for a in 0..n{self.records[index].values[a]=v[a]-expected;}expected
  }
 }
 pub fn pre(&mut self,node:usize)->f64{
  let g=self.game;let kind=g.kinds[node];let cfg=&g.configs[node];
  if kind==1{return g.offsets[node*2+self.updater];}
  if kind==2{return self.post(node,State::root(cfg),1);}
  if kind==3{
   let amount=cfg.starting_pot/2.;let gross=cfg.rake_pct*2.*amount;let rake=if cfg.rake_cap>0.{gross.min(cfg.rake_cap)}else{gross};
   let equity=if self.updater==0{self.allin_equity}else{1.-self.allin_equity};
   return equity*(2.*amount-rake)-amount+g.offsets[node*2+self.updater];
  }
  let actor=g.actors[node]as usize;let n=g.arities[node]as usize;
  let k=key(self.deal,actor,Some(node),0,0,0);let(index,p,selected)=self.begin(k,actor,n);let mut values=[0.;4];
  for a in 0..n{if selected.is_none()||selected==Some(a){values[a]=self.pre(g.children[node*4+a]as usize);}}
  self.finish(index,p,values,n,selected)
 }
 fn post(&mut self,branch:usize,state:State,history:u64)->f64{
  let cfg=&self.game.configs[branch];
  if state.kind==1{return self.post(branch,state.deal(),(history<<3)|5);}
  if state.kind>=2{
   let v=state.payouts(cfg);let value=if state.kind==2{if self.updater==state.player as usize{v[1]}else{v[0]}}
    else if self.winner<0{v[2]}else if self.updater==self.winner as usize{v[0]}else{v[1]};
   return value+self.game.offsets[branch*2+self.updater];
  }
  let actions=state.actions(cfg);let n=actions.len();let k=key(self.deal,state.player as usize,None,branch,state.street as usize,history);
  let(index,p,selected)=self.begin(k,state.player as usize,n);let mut values=[0.;4];
  for a in 0..n{if selected.is_none()||selected==Some(a){values[a]=self.post(branch,state.act(cfg,actions[a]),(history<<3)|(a as u64+1));}}
  self.finish(index,p,values,n,selected)
 }
}
