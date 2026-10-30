//! Research-only observable-input qualification; no training or production access.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod poker_reference_v1;
#[path="research_sampled/observation_v1.rs"] mod observation;
use poker_reference_v1::{Game,Key,key};
use observation::{Observation,WIDTH};
use state::State;
use serde_json::{Value,json};
use std::collections::{BTreeSet,BTreeMap};

#[derive(Clone,Copy)]
struct Query {actor:usize,pre:Option<usize>,branch:usize,street:usize,history:u64,n:usize}
impl Query {
 fn key(self,d:&[u8;9])->Key{key(d,self.actor,self.pre,self.branch,self.street,self.history)}
 fn visible(self,i:usize)->bool{
  i/2==self.actor&&i<4 || self.pre.is_none()&&i>=4&&i<=6+self.street
 }
}
fn enumerate(g:&Game,branch:usize,s:State,h:u64,q:&mut Vec<Query>,term:&mut Vec<Query>){
 if s.kind==1{enumerate(g,branch,s.deal(),(h<<3)|5,q,term);return;}
 let item=Query{actor:s.player as usize,pre:None,branch,street:s.street as usize,history:h,n:0};
 if s.kind>=2{term.push(item);return;}
 let acts=s.actions(&g.configs[branch]);q.push(Query{n:acts.len(),..item});
 for(a,act)in acts.into_iter().enumerate(){enumerate(g,branch,s.act(&g.configs[branch],act),(h<<3)|(a as u64+1),q,term);}
}
fn rejected(f:impl FnOnce()+std::panic::UnwindSafe){assert!(std::panic::catch_unwind(f).is_err(),"invalid observation was accepted");}
fn pack(cards:[u8;7],actor:usize)->u64{cards.iter().enumerate().fold((actor as u64)<<42,|v,(i,&c)|v|((c as u64)<<(6*i)))}

fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3);assert!(!std::path::Path::new(&args[2]).exists());
 let started=std::time::Instant::now();
 let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;let g=Game::new(&context);
 assert_eq!(context["positions"],json!(["BB","BTN"]));assert_eq!(g.kinds.len(),15);
 let fixture:Value=serde_json::from_slice(&std::fs::read(&args[1])?)?;
 let deals:Vec<[u8;9]>=fixture["deals"].as_array().unwrap().iter().map(|v|v.as_array().unwrap().iter().map(|c|c.as_u64().unwrap()as u8).collect::<Vec<_>>().try_into().unwrap()).collect();
 assert_eq!(deals.len(),8192);
 let mut queries=Vec::new();let mut terminals=Vec::new();
 for n in 0..g.kinds.len(){match g.kinds[n]{
  0=>queries.push(Query{actor:g.actors[n]as usize,pre:Some(n),branch:0,street:0,history:0,n:g.arities[n]as usize}),
  2=>enumerate(&g,n,State::root(&g.configs[n]),1,&mut queries,&mut terminals),_=>{}}}
 let mut permutations=Vec::new();
 for a in 0..4{for b in 0..4{for c in 0..4{for d in 0..4{let p=[a,b,c,d];if p.into_iter().collect::<BTreeSet<_>>().len()==4{permutations.push(p);}}}}}
 assert_eq!(permutations.len(),24);
 let mut checked=0;let mut suits=0;let mut hidden=0;let mut order=0;let mut timeline=0;
 let mut phases=BTreeMap::<usize,usize>::new();let mut golden=Vec::new();let mut golden_groups=BTreeSet::new();
 let mut seen_features=BTreeMap::<Vec<usize>,Key>::new();
 for &q in &queries{for sample in 0..16{
  let d=deals[sample*503%deals.len()];let input=q.key(&d);let o=Observation::decode(input);let x=o.features();
  assert_eq!(Observation::from_features(&x),o);assert_eq!(o.legal_actions(&g),q.n);
  let active:Vec<_>=x.iter().enumerate().filter_map(|(i,&v)|(v==1.).then_some(i)).collect();
  if let Some(previous)=seen_features.insert(active.clone(),o.key()){assert_eq!(previous,o.key());}
  checked+=1;*phases.entry(o.phase).or_default()+=1;
  if golden_groups.insert((o.phase,q.actor,q.branch,q.n)) {golden.push(json!({"input_hi":input.0.to_string(),"input_lo":input.1.to_string(),"canonical_hi":o.key().0.to_string(),"canonical_lo":o.key().1.to_string(),"active_features":active,"legal_actions":q.n}));}
  let mut changed=d;let mut used=0u64;for i in 0..9{if q.visible(i){used|=1u64<<d[i];}}
  for i in 0..9{if !q.visible(i){let c=(0..52).rev().find(|&c|used&(1u64<<c)==0&&c!=d[i]).unwrap();changed[i]=c;used|=1u64<<c;}}
  assert_eq!(Observation::decode(q.key(&changed)).features(),x);hidden+=1;
  changed=d;changed.swap(q.actor*2,q.actor*2+1);assert_eq!(Observation::decode(q.key(&changed)).features(),x);
  if q.pre.is_none(){changed=d;changed.swap(4,6);assert_eq!(Observation::decode(q.key(&changed)).features(),x);}order+=1;
  if o.phase==3&&d[7]/4!=d[8]/4{changed=d;changed.swap(7,8);assert_ne!(Observation::decode(q.key(&changed)).features(),x);timeline+=1;}
  for p in &permutations {let renamed=d.map(|c|c/4*4+p[(c%4)as usize]);assert_eq!(Observation::decode(q.key(&renamed)).features(),x);suits+=1;}
 }}
 let mut classes=BTreeSet::new();let mut pairs=0;
 for a in 0..52{for b in a+1..52{let mut d=deals[0];d[0]=a;d[1]=b;let o=Observation::decode(key(&d,0,Some(0),0,0,0));assert_eq!(Observation::from_features(&o.features()),o);classes.insert(o.key());pairs+=1;}}
 assert_eq!(pairs,1326);assert_eq!(classes.len(),169);
 // Explicit malformed/illegal observation controls. Temporarily silence expected panics.
 let hook=std::panic::take_hook();std::panic::set_hook(Box::new(|_|{}));
 let root=Observation::decode(key(&deals[0],0,Some(0),0,0,0));let mut negatives=0;
 rejected(||{let mut c=root.cards;c[0]=53;Observation::decode((1,pack(c,0)));});negatives+=1;
 rejected(||{let mut c=root.cards;c[1]=c[0];Observation::decode((1,pack(c,0)));});negatives+=1;
 rejected(||{let mut c=root.cards;c[2]=(0..52).find(|v|!c[..2].contains(v)).unwrap();Observation::decode((1,pack(c,0)));});negatives+=1;
 rejected(||{Observation::decode((1,root.key().1|(1u64<<44)));});negatives+=1;
 rejected(||{let mut o=root.clone();o.actor=1;o.legal_actions(&g);});negatives+=1;
 let post=queries.iter().find(|q|q.pre.is_none()&&q.history==1).copied().unwrap();let p=Observation::decode(post.key(&deals[0]));
 rejected(||{Observation::decode(((1u64<<63)|post.branch as u64,p.key().1));});negatives+=1;
 rejected(||{Observation::decode(((1u64<<63)|((8|6)<<4)|post.branch as u64,p.key().1));});negatives+=1;
 rejected(||{let mut x=p.features();x[155]=0.;x[156]=1.;x[155+12]=0.;x[155+13]=1.;Observation::from_features(&x);});negatives+=1;
 rejected(||{let mut x=root.features();x[0]=0.5;Observation::from_features(&x);});negatives+=1;
 for t in &terminals{rejected(||{Observation::decode(t.key(&deals[0])).legal_actions(&g);});negatives+=1;}
 std::panic::set_hook(hook);
 assert!(timeline>0&&hidden==checked&&phases.len()==4);
 let result=json!({"passed":true,"feature_width":WIDTH,"public_decision_templates":queries.len(),"terminal_templates_rejected":terminals.len(),"observations_checked":checked,"phase_counts":phases,"suit_relabel_checks":suits,"hidden_information_checks":hidden,"listing_order_checks":order,"turn_river_order_checks":timeline,"physical_starting_hands":pairs,"canonical_starting_classes":classes.len(),"negative_controls":negatives,"golden":golden,"seconds":started.elapsed().as_secs_f64(),"scope":"Fixed context; exact visible observation modulo global suit relabeling. No strategic training or convergence claim.","production_modified":false});
 std::fs::write(&args[2],serde_json::to_vec_pretty(&result)?)?;
 println!("{}",json!({"passed":true,"observations":checked,"suit_checks":suits,"negative_controls":negatives,"seconds":started.elapsed().as_secs_f64()}));Ok(())
}
