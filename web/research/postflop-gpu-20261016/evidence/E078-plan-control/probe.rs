#![allow(dead_code)]
pub use solver::{cards,cfr,evaluator,range,store,tree,parse_sizes,StreetSizing,TreeConfig};
pub use game::SpotConfig;
#[path="game.rs"] pub mod game;
#[path="accepted-plan.rs"] mod accepted;
#[path="candidate-plan.rs"] mod candidate;
use std::{fs::{File,OpenOptions},io::{BufWriter,Write}};
use candidate::GpuPlan;
include!("mark-fold.rs");
trait Encode {fn encode(&self,v:&mut Vec<u64>);fn caps(&self,_v:&mut Vec<u64>) {}}
macro_rules! prim {($($t:ty),*)=>{$(impl Encode for $t {fn encode(&self,v:&mut Vec<u64>){v.push(*self as u64);}})*};}
prim!(usize,u64,u32,i32,u8,bool);
impl Encode for f32 {fn encode(&self,v:&mut Vec<u64>){v.push(self.to_bits() as u64);}}
impl<T:Encode> Encode for Vec<T>{fn encode(&self,v:&mut Vec<u64>){v.push(self.len() as u64);for x in self{x.encode(v);}}fn caps(&self,v:&mut Vec<u64>){v.push(self.capacity() as u64);for x in self{x.caps(v);}}}
impl<T:Encode,const N:usize> Encode for [T;N]{fn encode(&self,v:&mut Vec<u64>){v.push(N as u64);for x in self{x.encode(v);}}fn caps(&self,v:&mut Vec<u64>){v.push(N as u64);for x in self{x.caps(v);}}}
impl Encode for accepted::LevelSpan {fn encode(&self,v:&mut Vec<u64>){v.extend([self.start as u64,self.count as u64]);}}
impl Encode for candidate::LevelSpan {fn encode(&self,v:&mut Vec<u64>){v.extend([self.start as u64,self.count as u64]);}}
fn words<T:Encode>(v:&T)->Vec<u64>{let mut w=Vec::new();v.encode(&mut w);w}
fn caps<T:Encode>(v:&T)->Vec<u64>{let mut w=Vec::new();v.caps(&mut w);w}
fn dump(f:&mut BufWriter<File>,v:&[u64]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();let mut b=Vec::with_capacity(65536);for c in v.chunks(8192){b.clear();for x in c{b.extend(x.to_le_bytes());}f.write_all(&b).unwrap();}}
fn field<A:Encode,B:Encode>(f:&mut BufWriter<File>,id:u32,name:&str,a:&A,b:&B,permute:bool)->u64{let ca=caps(a);let cb=caps(b);assert_eq!(ca,cb,"capacity {name}");let wa=words(a);let wb=words(b);if !permute{assert_eq!(wa,wb,"field {name}");}f.write_all(&id.to_le_bytes()).unwrap();for v in [&ca,&cb,&wa,&wb]{dump(f,v);}wa.len() as u64}
fn main(){let args:Vec<String>=std::env::args().collect();assert_eq!(args.len(),3);let id:usize=args[1].parse().unwrap();assert!(id<12);let fixtures=[include_str!("fixture-0.json"),include_str!("fixture-1.json"),include_str!("fixture-2.json")];let config:game::SpotConfig=serde_json::from_str(fixtures[id/4]).unwrap();let spot=game::Spot::new(config).unwrap();let iso=(id%4)>=2;let full=id%2==1;
let(mut a,mut b) = if id%2==0 {(Some(accepted::GpuPlan::build(&spot,iso)),Some(candidate::GpuPlan::build(&spot,iso)))}else{let b=candidate::GpuPlan::build(&spot,iso);(Some(accepted::GpuPlan::build(&spot,iso)),Some(b))};
if full {a.as_mut().unwrap().use_full_action_arenas(&spot);b.as_mut().unwrap().use_full_action_arenas(&spot);}
let a=a.unwrap();let mut b=b.unwrap();assert_eq!(a.node_na,b.node_na,"public unmarked plan values");mark_fold_producers(&mut b);let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(&args[2]).unwrap());f.write_all(b"E078-PLAN-RAW1\0\0").unwrap();f.write_all(&(id as u32).to_le_bytes()).unwrap();f.write_all(&(53u32).to_le_bytes()).unwrap();for n in [std::mem::size_of::<accepted::GpuPlan>(),std::mem::size_of::<candidate::GpuPlan>()]{f.write_all(&(n as u64).to_le_bytes()).unwrap();}assert_eq!(std::mem::size_of::<accepted::GpuPlan>(),std::mem::size_of::<candidate::GpuPlan>());
let mut count=0u64;
count+=field(&mut f,0,"num_levels",&a.num_levels,&b.num_levels,false);
count+=field(&mut f,1,"nh",&a.nh,&b.nh,false);
count+=field(&mut f,2,"nh_max",&a.nh_max,&b.nh_max,false);
count+=field(&mut f,3,"num_nodes",&a.num_nodes,&b.num_nodes,false);
count+=field(&mut f,4,"iso_active",&a.iso_active,&b.iso_active,false);
count+=field(&mut f,5,"action_nodes",&a.action_nodes,&b.action_nodes,false);
count+=field(&mut f,6,"action_spans",&a.action_spans,&b.action_spans,false);
count+=field(&mut f,7,"chance_parents",&a.chance_parents,&b.chance_parents,false);
count+=field(&mut f,8,"chance_children",&a.chance_children,&b.chance_children,false);
count+=field(&mut f,9,"chance_cards",&a.chance_cards,&b.chance_cards,false);
count+=field(&mut f,10,"chance_spans",&a.chance_spans,&b.chance_spans,false);
count+=field(&mut f,11,"chance_nodes",&a.chance_nodes,&b.chance_nodes,false);
count+=field(&mut f,12,"chance_node_spans",&a.chance_node_spans,&b.chance_node_spans,false);
count+=field(&mut f,13,"fold_nodes",&a.fold_nodes,&b.fold_nodes,false);
count+=field(&mut f,14,"fold_spans",&a.fold_spans,&b.fold_spans,false);
count+=field(&mut f,15,"show_nodes",&a.show_nodes,&b.show_nodes,false);
count+=field(&mut f,16,"show_spans",&a.show_spans,&b.show_spans,false);
count+=field(&mut f,17,"cc_start",&a.cc_start,&b.cc_start,false);
count+=field(&mut f,18,"cc_count",&a.cc_count,&b.cc_count,false);
count+=field(&mut f,19,"cc_card",&a.cc_card,&b.cc_card,false);
count+=field(&mut f,20,"cc_child",&a.cc_child,&b.cc_child,false);
count+=field(&mut f,21,"cc_perm",&a.cc_perm,&b.cc_perm,false);
count+=field(&mut f,22,"hand_perm_flat",&a.hand_perm_flat,&b.hand_perm_flat,false);
count+=field(&mut f,23,"node_player",&a.node_player,&b.node_player,false);
count+=field(&mut f,24,"node_na",&a.node_na,&b.node_na,true);
count+=field(&mut f,25,"node_data_off",&a.node_data_off,&b.node_data_off,false);
count+=field(&mut f,26,"arena_elements",&a.arena_elements,&b.arena_elements,false);
count+=field(&mut f,27,"node_children_start",&a.node_children_start,&b.node_children_start,false);
count+=field(&mut f,28,"node_twin",&a.node_twin,&b.node_twin,false);
count+=field(&mut f,29,"node_tlose",&a.node_tlose,&b.node_tlose,false);
count+=field(&mut f,30,"node_ttie",&a.node_ttie,&b.node_ttie,false);
count+=field(&mut f,31,"node_cdiv",&a.node_cdiv,&b.node_cdiv,false);
count+=field(&mut f,32,"node_river_slot",&a.node_river_slot,&b.node_river_slot,false);
count+=field(&mut f,33,"reach_src",&a.reach_src,&b.reach_src,false);
count+=field(&mut f,34,"reach_slot",&a.reach_slot,&b.reach_slot,false);
count+=field(&mut f,35,"reach_blocks",&a.reach_blocks,&b.reach_blocks,false);
count+=field(&mut f,36,"cfv_slot",&a.cfv_slot,&b.cfv_slot,false);
count+=field(&mut f,37,"cfv_blocks",&a.cfv_blocks,&b.cfv_blocks,false);
count+=field(&mut f,38,"hand_c1",&a.hand_c1,&b.hand_c1,false);
count+=field(&mut f,39,"hand_c2",&a.hand_c2,&b.hand_c2,false);
count+=field(&mut f,40,"hand_mask",&a.hand_mask,&b.hand_mask,false);
count+=field(&mut f,41,"same_combo",&a.same_combo,&b.same_combo,false);
count+=field(&mut f,42,"weights",&a.weights,&b.weights,false);
count+=field(&mut f,43,"num_slots",&a.num_slots,&b.num_slots,false);
count+=field(&mut f,44,"riv_off",&a.riv_off,&b.riv_off,false);
count+=field(&mut f,45,"riv_cnt",&a.riv_cnt,&b.riv_cnt,false);
count+=field(&mut f,46,"riv_sorted_idx",&a.riv_sorted_idx,&b.riv_sorted_idx,false);
count+=field(&mut f,47,"riv_sorted_str",&a.riv_sorted_str,&b.riv_sorted_str,false);
count+=field(&mut f,48,"riv_lower",&a.riv_lower,&b.riv_lower,false);
count+=field(&mut f,49,"riv_upper",&a.riv_upper,&b.riv_upper,false);
count+=field(&mut f,50,"riv_card_off",&a.riv_card_off,&b.riv_card_off,false);
count+=field(&mut f,51,"riv_card_pos",&a.riv_card_pos,&b.riv_card_pos,false);
count+=field(&mut f,52,"riv_max_cnt",&a.riv_max_cnt,&b.riv_max_cnt,false);
let kinds:Vec<u8>=spot.tree.nodes.iter().map(|n|n.kind).collect();dump(&mut f,&words(&kinds));dump(&mut f,&words(&spot.tree.children));f.flush().unwrap();f.get_ref().sync_all().unwrap();
let v=serde_json::json!({"id":id,"fixture_index":id/4,"board":spot.config.board,"iso_requested":iso,"iso_active":a.iso_active,"full_arenas":full,"first":if id%2==1{"candidate"}else{"baseline"},"fields":53,"baseline_words":count,"nodes":spot.tree.nodes.len(),"action_nodes":a.action_nodes.len(),"all_non_marker_fields_bitwise_equal":true,"all_vec_capacities_equal":true,"struct_size_equal":true,"gpu_executions":0,"full_cycle_performance_measured":false});println!("E078 {v}");}

#[cfg(test)]mod marker_controls {use super::*;use game::Spot;
    #[test]
    fn fold_producer_markers_are_private_and_exact() {
        for board in ["KsQs2d", "Qs7h2dKh", "AsKsQsJsTs"] {
            let spot = Spot::new(SpotConfig {
                board: board.into(), range_oop: "AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
                range_ip: "AA,QQ,TT,77,AQs,KQs,AQo".into(),
                tree: TreeConfig { starting_pot: 10.0, effective_stack: 20.0, ..Default::default() },
            }).unwrap();
            for iso in [false, true] { for full in [false, true] {
                let mut plan = GpuPlan::build(&spot, iso);
                if full { plan.use_full_action_arenas(&spot); }
                let original = plan.node_na.clone(); let capacity = plan.node_na.capacity();
                mark_fold_producers(&mut plan);
                let folds: std::collections::HashSet<_> = plan.fold_nodes.iter().copied().collect();
                assert!(!folds.is_empty());
                for (n, (&a, &b)) in original.iter().zip(&plan.node_na).enumerate() {
                    if folds.contains(&(n as u32)) {
                        assert_eq!(spot.tree.nodes[n].kind, crate::tree::KIND_TERM_FOLD);
                        assert_eq!(a, 0); assert_eq!(b, -1);
                    } else { assert_eq!(a, b); }
                }
                assert_eq!(plan.node_na.capacity(), capacity);
                assert_eq!(plan.node_na.len(), original.len());
                for &n in &plan.action_nodes { assert!(plan.node_na[n as usize] > 0); }
                let once = plan.node_na.clone(); mark_fold_producers(&mut plan);
                assert_eq!(plan.node_na, once);
                let mut fresh = GpuPlan::build(&spot, iso);
                if full { fresh.use_full_action_arenas(&spot); }
                assert_eq!(fresh.node_na, original);
            }}
        }
    }

}
