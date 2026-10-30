//! Observable own-reach reconstruction for the fixed physical-poker subtree.
use super::poker_reference_v1::{Game,Key};
use super::observation_v1::Observation;
use super::state::State;

/// Prior decisions belonging to the queried player, in chronological order.
pub fn own_history(game:&Game,key:Key)->Vec<(Key,usize,usize)>{
 let o=Observation::decode(key);o.legal_actions(game);
 let mut parents=vec![None;game.kinds.len()];
 for node in 0..game.kinds.len(){if game.kinds[node]==0{
  for a in 0..game.arities[node]as usize{let child=game.children[node*4+a]as usize;assert!(parents[child].replace((node,a)).is_none(),"context must be a tree");}
 }}assert!(parents[0].is_none());
 let mut path=Vec::new();let mut node=o.public_id;
 while let Some((parent,a))=parents[node]{path.push((parent,a));node=parent;assert!(path.len()<game.kinds.len());}
 assert_eq!(node,0);path.reverse();let mut out=Vec::new();
 for (node,a)in path{if game.actors[node]as usize==o.actor{
  let mut prior=o.clone();prior.phase=0;prior.public_id=node;prior.history.clear();prior.cards[2..].fill(63);
  let k=Observation::decode(prior.key()).key();out.push((k,a,game.arities[node]as usize));
 }}
 if o.phase>0{
  let cfg=&game.configs[o.public_id];let mut state=State::root(cfg);let mut prefix=Vec::new();
  for &token in &o.history{
   if token==5{assert_eq!(state.kind,1);state=state.deal();}
   else{
    assert_eq!(state.kind,0);let acts=state.actions(cfg);let a=token as usize-1;assert!(a<acts.len());
    if state.player as usize==o.actor{
     let mut prior=o.clone();prior.phase=state.street as usize+1;prior.history=prefix.clone();
     if prior.phase<3{prior.cards[6]=63;}if prior.phase<2{prior.cards[5]=63;}
     let k=Observation::decode(prior.key()).key();assert_eq!(Observation::decode(k).legal_actions(game),acts.len());out.push((k,a,acts.len()));
    }state=state.act(cfg,acts[a]);
   }prefix.push(token);
  }
 }out
}

/// Average policies weighted by iteration weight and each model's own prior reach.
pub fn average(game:&Game,key:Key,n:usize,weights:&[f64],policy:&impl Fn(usize,Key,usize)->[f64;4])->([f64;4],f64){
 assert!(!weights.is_empty()&&weights.iter().all(|w|w.is_finite()&&*w>=0.)&&weights.iter().sum::<f64>()>0.);
 let history=own_history(game,key);let mut numerator=[0.;4];let mut total=0.;
 for(model,&weight)in weights.iter().enumerate(){
  let mut reach=weight;for &(prior,action,arity)in &history{reach*=policy(model,prior,arity)[action];}
  if reach>0.{let p=policy(model,key,n);for a in 0..n{numerator[a]+=reach*p[a];}total+=reach;}
 }
 if total>0.{for a in 0..n{numerator[a]/=total;}}else{numerator[..n].fill(1./n as f64);}
 (numerator,total)
}
