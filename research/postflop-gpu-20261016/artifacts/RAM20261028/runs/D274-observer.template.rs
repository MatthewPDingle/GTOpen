#[cfg(test)]
#[derive(Clone,Copy,Default)]
struct D274Marks {tree_ns:u64,river_ns:u64,symmetry_ns:u64,total_ns:u64,tree_started:bool,river_started:bool,symmetry_started:bool}
#[cfg(test)]
thread_local! { static D274_MARKS: std::cell::Cell<D274Marks> = std::cell::Cell::new(D274Marks::default()); }
#[cfg(test)]
impl Spot {
@PROFILED_METHOD@
}

#[cfg(test)]
mod d274_observer {
use super::*;
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::Path,time::Instant};
use serde_json::{json,Value};
trait Encode {fn size(&self)->u64;fn encode(&self,w:&mut impl Write);}
macro_rules! primitive {($t:ty,$n:expr,$f:expr)=>{impl Encode for $t {fn size(&self)->u64{$n}fn encode(&self,w:&mut impl Write){w.write_all(&($f)(*self)).unwrap();}}};}
primitive!(u8,1,|x:u8|[x]);primitive!(u16,2,|x:u16|x.to_le_bytes());primitive!(u32,4,|x:u32|x.to_le_bytes());primitive!(u64,8,|x:u64|x.to_le_bytes());
primitive!(f32,4,|x:f32|x.to_bits().to_le_bytes());primitive!(f64,8,|x:f64|x.to_bits().to_le_bytes());
impl<T:Encode> Encode for Vec<T>{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(self.len()as u64).encode(w);for x in self{x.encode(w);}}}
impl<T:Encode,const N:usize> Encode for[T;N]{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(N as u64).encode(w);for x in self{x.encode(w);}}}
impl<T:Encode> Encode for Option<T>{fn size(&self)->u64{1+self.as_ref().map(Encode::size).unwrap_or(0)}fn encode(&self,w:&mut impl Write){match self{None=>0u8.encode(w),Some(x)=>{1u8.encode(w);x.encode(w);}}}}
impl<T:Encode> Encode for Box<T>{fn size(&self)->u64{self.as_ref().size()}fn encode(&self,w:&mut impl Write){self.as_ref().encode(w);}}
impl Encode for(u32,u16){fn size(&self)->u64{6}fn encode(&self,w:&mut impl Write){self.0.encode(w);self.1.encode(w);}}
impl Encode for crate::tree::Node{
 fn size(&self)->u64{68}
 fn encode(&self,w:&mut impl Write){self.kind.encode(w);self.player.encode(w);self.street.encode(w);self.num_children.encode(w);self.children_start.encode(w);self.actions_start.encode(w);self.data_offset.encode(w);self.put.encode(w);self.t_win.encode(w);self.t_lose.encode(w);self.t_tie.encode(w);}
}
impl Encode for crate::tree::Action{
 fn size(&self)->u64{match self{Self::Fold|Self::Check=>1,_=>9}}
 fn encode(&self,w:&mut impl Write){use crate::tree::Action::*;match self{Fold=>0u8.encode(w),Check=>1u8.encode(w),Call(x)=>{2u8.encode(w);x.encode(w);},Bet(x)=>{3u8.encode(w);x.encode(w);},Raise(x)=>{4u8.encode(w);x.encode(w);}}}
}
impl Encode for HandInfo{fn size(&self)->u64{14}fn encode(&self,w:&mut impl Write){self.c1.encode(w);self.c2.encode(w);self.weight.encode(w);self.mask.encode(w);}}
impl Encode for RiverBoardEval{fn size(&self)->u64{self.sorted.size()}fn encode(&self,w:&mut impl Write){self.sorted.encode(w);}}
fn field(w:&mut impl Write,name:&str,v:&impl Encode){(name.len()as u32).encode(w);w.write_all(name.as_bytes()).unwrap();v.size().encode(w);v.encode(w);}
fn dump(s:&Spot,path:&Path){
 let mut w=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(path).unwrap());w.write_all(b"D274-SPOT-v1\0\0\0\0").unwrap();
 field(&mut w,"config_json",&serde_json::to_vec(&s.config).unwrap());field(&mut w,"board",&s.board);field(&mut w,"board_mask",&s.board_mask);
 field(&mut w,"tree_config_json",&serde_json::to_vec(&s.tree.config).unwrap());field(&mut w,"tree_root_street",&s.tree.root_street);
 field(&mut w,"tree_nodes",&s.tree.nodes);field(&mut w,"tree_children",&s.tree.children);field(&mut w,"tree_actions",&s.tree.actions);field(&mut w,"tree_data_size",&s.tree.data_size);
 field(&mut w,"hands",&s.hands);field(&mut w,"weights",&s.weights);field(&mut w,"same_combo",&s.same_combo);
 field(&mut w,"river_root_street",&s.river.root_street);field(&mut w,"river_entries",&s.river.entries);field(&mut w,"suit_perms",&s.suit_perms);field(&mut w,"hand_perm",&s.hand_perm);
 let mut capacities=vec![s.board.capacity()as u64,s.tree.nodes.capacity()as u64,s.tree.children.capacity()as u64,s.tree.actions.capacity()as u64,s.river.entries.capacity()as u64,s.suit_perms.capacity()as u64];
 for p in 0..2{capacities.extend([s.hands[p].capacity()as u64,s.weights[p].capacity()as u64,s.same_combo[p].capacity()as u64,s.hand_perm[p].capacity()as u64]);for perm in&s.hand_perm[p]{capacities.push(perm.capacity()as u64);}}
 for entry in&s.river.entries{if let Some(entry)=entry{for p in 0..2{capacities.push(entry.sorted[p].capacity()as u64);}}}
 field(&mut w,"data_vector_capacities",&capacities);w.flush().unwrap();w.get_ref().sync_all().unwrap();
}
fn compare_data(a:&Spot,b:&Spot){
 assert_eq!(serde_json::to_vec(&a.config).unwrap(),serde_json::to_vec(&b.config).unwrap());
 assert_eq!(serde_json::to_vec(&a.tree.config).unwrap(),serde_json::to_vec(&b.tree.config).unwrap());
 assert_eq!(a.tree.nodes.len(),b.tree.nodes.len());assert_eq!(a.tree.children,b.tree.children);assert_eq!(a.tree.data_size,b.tree.data_size);
 for(x,y)in a.tree.nodes.iter().zip(&b.tree.nodes){
  assert_eq!((x.kind,x.player,x.street,x.num_children,x.children_start,x.actions_start,x.data_offset),(y.kind,y.player,y.street,y.num_children,y.children_start,y.actions_start,y.data_offset));
  assert_eq!([x.put[0],x.put[1],x.t_win,x.t_lose,x.t_tie].map(f64::to_bits),[y.put[0],y.put[1],y.t_win,y.t_lose,y.t_tie].map(f64::to_bits));
 }
 assert_eq!(a.tree.actions.len(),b.tree.actions.len());for(x,y)in a.tree.actions.iter().zip(&b.tree.actions){
  use crate::tree::Action::*;match(x,y){(Fold,Fold)|(Check,Check)=>{},(Call(x),Call(y))|(Bet(x),Bet(y))|(Raise(x),Raise(y))=>assert_eq!(x.to_bits(),y.to_bits()),_=>panic!("action variant")}
 }
 assert_eq!(a.board,b.board);assert_eq!(a.board_mask,b.board_mask);assert_eq!(a.tree.root_street,b.tree.root_street);assert_eq!(a.river.root_street,b.river.root_street);assert_eq!(a.suit_perms,b.suit_perms);assert_eq!(a.hand_perm,b.hand_perm);
 for p in 0..2{
  assert_eq!(a.hands[p].len(),b.hands[p].len());for(x,y)in a.hands[p].iter().zip(&b.hands[p]){assert_eq!((x.c1,x.c2,x.weight.to_bits(),x.mask),(y.c1,y.c2,y.weight.to_bits(),y.mask));}
  assert_eq!(a.weights[p].iter().map(|x|x.to_bits()).collect::<Vec<_>>(),b.weights[p].iter().map(|x|x.to_bits()).collect::<Vec<_>>());assert_eq!(a.same_combo[p],b.same_combo[p]);
 }
 assert_eq!(a.river.entries.len(),b.river.entries.len());for(x,y)in a.river.entries.iter().zip(&b.river.entries){match(x,y){(None,None)=>{},(Some(x),Some(y))=>assert_eq!(x.sorted,y.sorted),_=>panic!("river slot")}}
}

#[test]
fn observe(){
 let fixtures:Vec<Value>=serde_json::from_str(include_str!(r"@FIXTURES@")).unwrap();assert_eq!(fixtures.len(),3);
 let output=std::path::PathBuf::from(std::env::var("D274_OUTPUT").unwrap());std::fs::create_dir(&output).unwrap();
 let order=std::env::var("D274_ORDER").unwrap();assert!(order=="BO"||order=="OB");assert_eq!(rayon::current_num_threads(),16);
 for f in&fixtures{
  let id=f["fixture"].as_str().unwrap();let cfg:SpotConfig=serde_json::from_value(f["config"].clone()).unwrap();
  let mut built: [Option<Spot>;2]=[None,None];let mut elapsed=[0u64;2];let mut marks=D274Marks::default();
  for arm in if order=="BO"{[0usize,1]}else{[1usize,0]}{
   D274_MARKS.with(|m|m.set(D274Marks::default()));let start=Instant::now();
   let spot=if arm==0{Spot::new(cfg.clone())}else{Spot::d274_profiled_new_impl(cfg.clone(),None,Strictness::Strict)}.unwrap();
   elapsed[arm]=start.elapsed().as_nanos()as u64;if arm==1{marks=D274_MARKS.with(|m|m.get());}built[arm]=Some(spot);
  }
  let a=built[0].as_ref().unwrap();let b=built[1].as_ref().unwrap();assert_eq!(a.tree.nodes.len()as u64,f["expected_nodes"].as_u64().unwrap());compare_data(a,b);
  assert!(marks.tree_started&&marks.river_started&&marks.symmetry_started);
  assert!(marks.tree_ns+marks.river_ns+marks.symmetry_ns<=marks.total_ns&&marks.total_ns<=elapsed[1]);
  dump(a,&output.join(format!("{id}-baseline.spot.bin")));dump(b,&output.join(format!("{id}-observed.spot.bin")));
  println!("\nD274_SPOT {}",json!({"fixture":id,"order":order,"nodes":a.tree.nodes.len(),"hands":a.hands.each_ref().map(|v|v.len()),"baseline_ns":elapsed[0],"observed_ns":elapsed[1],"tree_ns":marks.tree_ns,"river_ns":marks.river_ns,"symmetry_ns":marks.symmetry_ns,"profiled_constructor_ns":marks.total_ns,"full_data_native_exact":true,"worker_count":rayon::current_num_threads(),"CPU_only":true,"CFR_iterations_GPU_calls":0}));std::io::stdout().flush().unwrap();
 }
 let base:SpotConfig=serde_json::from_value(fixtures[0]["config"].clone()).unwrap();let mut errors=0;
 for tag in["budget0","budget1","budget100","bad_stack","bad_bet","bad_board","empty_range","impossible_ranges"]{
  let mut cfg=base.clone();let limit=match tag{"budget0"=>Some(0),"budget1"=>Some(1),"budget100"=>Some(100),_=>None};
  match tag{"bad_stack"=>cfg.tree.effective_stack=0.,"bad_bet"=>cfg.tree.oop[0].bet=vec![crate::tree::BetSize::PrevMult(2.5)],"bad_board"=>cfg.board="Ks7h".into(),"empty_range"=>cfg.range_oop="".into(),"impossible_ranges"=>{cfg.range_oop="AcKc".into();cfg.range_ip="AcQc".into();},_=>{}}
  let baseline=match Spot::new_with_limit(cfg.clone(),limit){Ok(_)=>panic!("expected error {tag}"),Err(e)=>e};D274_MARKS.with(|m|m.set(D274Marks::default()));
  let observed=match Spot::d274_profiled_new_impl(cfg,limit,Strictness::Strict){Ok(_)=>panic!("expected profiled error {tag}"),Err(e)=>e};let marks=D274_MARKS.with(|m|m.get());
  assert_eq!(baseline,observed);assert!(!marks.river_started&&!marks.symmetry_started);
  println!("D274_ERROR {}",json!({"case":tag,"same_error":baseline,"river_not_started":true,"symmetry_not_started":true}));errors+=1;
 }
 assert_eq!(errors,8);println!("D274_COMPLETE {}",json!({"fixtures":3,"full_Spot_pairs":3,"error_cases":8,"CFR_iterations_GPU_calls":0}));
}
}
