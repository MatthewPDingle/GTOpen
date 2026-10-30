#![allow(dead_code,unused_imports)]
pub use solver::*;
#[path="observed-plan.rs"]mod observed;
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::Path,time::Instant};
use serde_json::{json,Value};
trait Encode {fn size(&self)->u64;fn encode(&self,w:&mut impl Write);}
macro_rules! primitive{($t:ty,$n:expr,$f:expr)=>{impl Encode for $t{fn size(&self)->u64{$n}fn encode(&self,w:&mut impl Write){w.write_all(&($f)(*self)).unwrap();}}};}
primitive!(u32,4,|x:u32|x.to_le_bytes());primitive!(i32,4,|x:i32|x.to_le_bytes());primitive!(f32,4,|x:f32|x.to_bits().to_le_bytes());primitive!(u64,8,|x:u64|x.to_le_bytes());primitive!(usize,8,|x:usize|(x as u64).to_le_bytes());primitive!(bool,1,|x:bool|[x as u8]);
impl<T:Encode> Encode for Vec<T>{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(self.len() as u64).encode(w);for x in self{x.encode(w);}}}
impl<T:Encode,const N:usize> Encode for [T;N]{fn size(&self)->u64{8+self.iter().map(Encode::size).sum::<u64>()}fn encode(&self,w:&mut impl Write){(N as u64).encode(w);for x in self{x.encode(w);}}}
impl Encode for solver::gpu::plan::LevelSpan{fn size(&self)->u64{8}fn encode(&self,w:&mut impl Write){self.start.encode(w);self.count.encode(w);}}
impl Encode for observed::LevelSpan{fn size(&self)->u64{8}fn encode(&self,w:&mut impl Write){self.start.encode(w);self.count.encode(w);}}
fn field(w:&mut impl Write,name:&str,v:&impl Encode){assert!(name.len()<256);(name.len() as u32).encode(w);w.write_all(name.as_bytes()).unwrap();let bytes=v.size();assert!(bytes<=2*1024*1024*1024);bytes.encode(w);v.encode(w);}
fn dump_baseline(p:&solver::gpu::plan::GpuPlan,path:&Path){let mut w=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).unwrap());w.write_all(b"D183_PLAN_RAW1\0\0\0").unwrap();
 field(&mut w,"num_levels",&p.num_levels);
 field(&mut w,"nh",&p.nh);
 field(&mut w,"nh_max",&p.nh_max);
 field(&mut w,"num_nodes",&p.num_nodes);
 field(&mut w,"iso_active",&p.iso_active);
 field(&mut w,"action_nodes",&p.action_nodes);
 field(&mut w,"action_spans",&p.action_spans);
 field(&mut w,"chance_parents",&p.chance_parents);
 field(&mut w,"chance_children",&p.chance_children);
 field(&mut w,"chance_cards",&p.chance_cards);
 field(&mut w,"chance_spans",&p.chance_spans);
 field(&mut w,"chance_nodes",&p.chance_nodes);
 field(&mut w,"chance_node_spans",&p.chance_node_spans);
 field(&mut w,"fold_nodes",&p.fold_nodes);
 field(&mut w,"fold_spans",&p.fold_spans);
 field(&mut w,"show_nodes",&p.show_nodes);
 field(&mut w,"show_spans",&p.show_spans);
 field(&mut w,"cc_start",&p.cc_start);
 field(&mut w,"cc_count",&p.cc_count);
 field(&mut w,"cc_card",&p.cc_card);
 field(&mut w,"cc_child",&p.cc_child);
 field(&mut w,"cc_perm",&p.cc_perm);
 field(&mut w,"hand_perm_flat",&p.hand_perm_flat);
 field(&mut w,"node_player",&p.node_player);
 field(&mut w,"node_na",&p.node_na);
 field(&mut w,"node_data_off",&p.node_data_off);
 field(&mut w,"arena_elements",&p.arena_elements);
 field(&mut w,"node_children_start",&p.node_children_start);
 field(&mut w,"node_twin",&p.node_twin);
 field(&mut w,"node_tlose",&p.node_tlose);
 field(&mut w,"node_ttie",&p.node_ttie);
 field(&mut w,"node_cdiv",&p.node_cdiv);
 field(&mut w,"node_river_slot",&p.node_river_slot);
 field(&mut w,"reach_src",&p.reach_src);
 field(&mut w,"reach_slot",&p.reach_slot);
 field(&mut w,"reach_blocks",&p.reach_blocks);
 field(&mut w,"cfv_slot",&p.cfv_slot);
 field(&mut w,"cfv_blocks",&p.cfv_blocks);
 field(&mut w,"hand_c1",&p.hand_c1);
 field(&mut w,"hand_c2",&p.hand_c2);
 field(&mut w,"hand_mask",&p.hand_mask);
 field(&mut w,"same_combo",&p.same_combo);
 field(&mut w,"weights",&p.weights);
 field(&mut w,"num_slots",&p.num_slots);
 field(&mut w,"riv_off",&p.riv_off);
 field(&mut w,"riv_cnt",&p.riv_cnt);
 field(&mut w,"riv_sorted_idx",&p.riv_sorted_idx);
 field(&mut w,"riv_sorted_str",&p.riv_sorted_str);
 field(&mut w,"riv_lower",&p.riv_lower);
 field(&mut w,"riv_upper",&p.riv_upper);
 field(&mut w,"riv_card_off",&p.riv_card_off);
 field(&mut w,"riv_card_pos",&p.riv_card_pos);
 field(&mut w,"riv_max_cnt",&p.riv_max_cnt);
w.flush().unwrap();w.get_ref().sync_all().unwrap();assert!(w.get_ref().metadata().unwrap().len()<=2*1024*1024*1024);}
fn dump_observed(p:&observed::GpuPlan,path:&Path){let mut w=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).unwrap());w.write_all(b"D183_PLAN_RAW1\0\0\0").unwrap();
 field(&mut w,"num_levels",&p.num_levels);
 field(&mut w,"nh",&p.nh);
 field(&mut w,"nh_max",&p.nh_max);
 field(&mut w,"num_nodes",&p.num_nodes);
 field(&mut w,"iso_active",&p.iso_active);
 field(&mut w,"action_nodes",&p.action_nodes);
 field(&mut w,"action_spans",&p.action_spans);
 field(&mut w,"chance_parents",&p.chance_parents);
 field(&mut w,"chance_children",&p.chance_children);
 field(&mut w,"chance_cards",&p.chance_cards);
 field(&mut w,"chance_spans",&p.chance_spans);
 field(&mut w,"chance_nodes",&p.chance_nodes);
 field(&mut w,"chance_node_spans",&p.chance_node_spans);
 field(&mut w,"fold_nodes",&p.fold_nodes);
 field(&mut w,"fold_spans",&p.fold_spans);
 field(&mut w,"show_nodes",&p.show_nodes);
 field(&mut w,"show_spans",&p.show_spans);
 field(&mut w,"cc_start",&p.cc_start);
 field(&mut w,"cc_count",&p.cc_count);
 field(&mut w,"cc_card",&p.cc_card);
 field(&mut w,"cc_child",&p.cc_child);
 field(&mut w,"cc_perm",&p.cc_perm);
 field(&mut w,"hand_perm_flat",&p.hand_perm_flat);
 field(&mut w,"node_player",&p.node_player);
 field(&mut w,"node_na",&p.node_na);
 field(&mut w,"node_data_off",&p.node_data_off);
 field(&mut w,"arena_elements",&p.arena_elements);
 field(&mut w,"node_children_start",&p.node_children_start);
 field(&mut w,"node_twin",&p.node_twin);
 field(&mut w,"node_tlose",&p.node_tlose);
 field(&mut w,"node_ttie",&p.node_ttie);
 field(&mut w,"node_cdiv",&p.node_cdiv);
 field(&mut w,"node_river_slot",&p.node_river_slot);
 field(&mut w,"reach_src",&p.reach_src);
 field(&mut w,"reach_slot",&p.reach_slot);
 field(&mut w,"reach_blocks",&p.reach_blocks);
 field(&mut w,"cfv_slot",&p.cfv_slot);
 field(&mut w,"cfv_blocks",&p.cfv_blocks);
 field(&mut w,"hand_c1",&p.hand_c1);
 field(&mut w,"hand_c2",&p.hand_c2);
 field(&mut w,"hand_mask",&p.hand_mask);
 field(&mut w,"same_combo",&p.same_combo);
 field(&mut w,"weights",&p.weights);
 field(&mut w,"num_slots",&p.num_slots);
 field(&mut w,"riv_off",&p.riv_off);
 field(&mut w,"riv_cnt",&p.riv_cnt);
 field(&mut w,"riv_sorted_idx",&p.riv_sorted_idx);
 field(&mut w,"riv_sorted_str",&p.riv_sorted_str);
 field(&mut w,"riv_lower",&p.riv_lower);
 field(&mut w,"riv_upper",&p.riv_upper);
 field(&mut w,"riv_card_off",&p.riv_card_off);
 field(&mut w,"riv_card_pos",&p.riv_card_pos);
 field(&mut w,"riv_max_cnt",&p.riv_max_cnt);
w.flush().unwrap();w.get_ref().sync_all().unwrap();assert!(w.get_ref().metadata().unwrap().len()<=2*1024*1024*1024);}

fn main(){
 let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),3);let out=Path::new(&args[1]);let order=&args[2];assert!(order=="BO"||order=="OB");let fixtures:Vec<Value>=serde_json::from_str(include_str!("fixtures.json")).unwrap();assert_eq!(fixtures.len(),6);
 for f in fixtures{
  let id=f["id"].as_str().unwrap();let cfg:SpotConfig=serde_json::from_value(f["config"].clone()).unwrap();let spot=Spot::new(cfg).unwrap();assert_eq!(spot.tree.nodes.len() as u64,f["expected_nodes"].as_u64().unwrap());let iso=f["use_iso"].as_bool().unwrap();
  let (b,o,bms,oms)=if order=="BO"{let t=Instant::now();let b=solver::gpu::plan::GpuPlan::build(&spot,iso);let bm=t.elapsed().as_secs_f64()*1000.;let t=Instant::now();let o=observed::GpuPlan::build(&spot,iso);let om=t.elapsed().as_secs_f64()*1000.;(b,o,bm,om)}else{let t=Instant::now();let o=observed::GpuPlan::build(&spot,iso);let om=t.elapsed().as_secs_f64()*1000.;let t=Instant::now();let b=solver::gpu::plan::GpuPlan::build(&spot,iso);let bm=t.elapsed().as_secs_f64()*1000.;(b,o,bm,om)};
  let marks=observed::d183_marks();assert_eq!(marks.iter().map(|x|x.0).collect::<Vec<_>>(),vec!["preamble", "DFS_buffers", "representative_DFS", "CFV_width_count", "CFV_slots", "classify_nodes", "flatten_node_lists", "chance_edge_lists", "river_slot_assignment", "river_tables", "scalar_arrays", "full_or_compact_selection", "hand_tables", "reach_compaction"]);assert!(marks.iter().all(|x|x.1.is_finite()&&x.1>=0.));assert!(marks.iter().map(|x|x.1).sum::<f64>()<=oms);assert!(bms.is_finite()&&bms>=0.&&oms.is_finite()&&oms>=0.);
  dump_baseline(&b,&out.join(format!("{id}-baseline.plan.bin")));dump_observed(&o,&out.join(format!("{id}-observed.plan.bin")));
  println!("D183_PLAN {}",json!({"stage":"fixture","id":id,"fixture":f["fixture"],"config":f["config"],"use_iso":iso,"nodes":spot.tree.nodes.len(),"hands":spot.hands.each_ref().map(|x|x.len()),"order":order,"baseline_plan_ms":bms,"observed_plan_ms":oms,"phase_ms":marks,"all_fields_retained":53,"GPU_context_or_kernel_calls":0,"solver_runs":0,"performance_candidate":false}));std::io::stdout().flush().unwrap();
 }
 println!("D183_PLAN {}",json!({"stage":"complete","cases":6,"GPU_context_or_kernel_calls":0,"solver_runs":0,"candidate_accepted":false}));
}
