impl GpuSolver {
 pub fn d271_map_data(&self,s:&Solver)->(plan::GpuPlan,Vec<u32>,Vec<u32>,serde_json::Value){
  let p=crate::d271_cpu_plan(s);
  let mut compact=[false;2];
  for player in 0..2{
   compact[player]=p.arena_elements[player]!=s.spot.tree.data_size[player]as usize
    || s.spot.tree.nodes.iter().enumerate().any(|(i,n)|n.kind==crate::tree::KIND_ACTION&&n.player as usize==player&&p.node_data_off[i]!=n.data_offset);
  }
  assert_eq!(compact,[self.arena_layout[0].d271_compact(),self.arena_layout[1].d271_compact()]);
  let staging_bytes=self.h_staging.len.checked_mul(4).unwrap();
  let aligned=self.h_staging.ptr as usize%8==0;
  let capable=compact.into_iter().all(|x|x)
   &&p.num_nodes.checked_mul(8).unwrap().max(s.spot.tree.children.len().checked_mul(4).unwrap())<=staging_bytes
   &&p.reach_src.iter().all(|x|x.len()==p.num_nodes)&&aligned;
  let ordered=@ORDERED@;
  @ASSERT@
  assert_eq!(self.h_staging.len,p.arena_elements[0].max(p.arena_elements[1]));
  assert_eq!(std::mem::size_of::<Self>(),4448);
  let(forward,inverse)=crate::d271_permutation(&p,ordered);
  let info=serde_json::json!({"ordered":ordered,"independently_expected_capability":capable,"compact":compact,
   "pinned_words":self.h_staging.len,"pinned_alignment8":aligned,"wrapper_bytes":std::mem::size_of::<Self>(),
   "nodes":p.num_nodes,"hands":p.nh,"CPU_data_size":s.spot.tree.data_size,"children":s.spot.tree.children.len(),"storage":format!("{:?}",s.storage)});
  (p,forward,inverse,info)
 }
}
