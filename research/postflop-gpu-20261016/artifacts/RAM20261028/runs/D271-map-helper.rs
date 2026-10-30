// Diagnostic CPU oracle and inverse of actual retained GPU metadata images.
const D271_ROW_FIELDS: &[&str] = &["d_node_player","d_node_na","d_node_data_off","d_node_children_start",
 "d_node_twin","d_node_tlose","d_node_ttie","d_node_cdiv","d_node_river_slot","d_cc_start","d_cc_count",
 "d_rsrc[0]","d_rsrc[1]","d_cfv_slot","d_lock_off"];
const D271_ID_FIELDS: &[&str] = &["d_action_nodes","d_chance_parents","d_chance_children","d_chance_nodes",
 "d_fold_nodes","d_show_nodes","d_cc_child","d_children"];
const D271_INVENTORY: &[&str] = &@INVENTORY@;
static D271_OUTPUT:std::sync::OnceLock<PathBuf>=std::sync::OnceLock::new();

fn d271_cpu_plan(s:&Solver)->solver::gpu::plan::GpuPlan {
 let mut p=solver::gpu::plan::GpuPlan::build(&s.spot,s.use_isomorphism);
 if s.storage==Storage::F32 {
  p.arena_elements=[s.spot.tree.data_size[0]as usize,s.spot.tree.data_size[1]as usize];
  for(i,n)in s.spot.tree.nodes.iter().enumerate(){p.node_data_off[i]=n.data_offset;}
 }
 p
}
fn d271_permutation(p:&solver::gpu::plan::GpuPlan,ordered:bool)->(Vec<u32>,Vec<u32>){
 if !ordered {let v:Vec<u32>=(0..p.num_nodes as u32).collect();return(v.clone(),v);}
 // Separate sort-based oracle, not a call to production metadata::build_map.
 let mut tagged=Vec::new();
 for(level,_)in p.action_spans.iter().enumerate(){
  for(kind,(nodes,spans))in[(&p.action_nodes,&p.action_spans),(&p.chance_nodes,&p.chance_node_spans),
    (&p.fold_nodes,&p.fold_spans),(&p.show_nodes,&p.show_spans)].into_iter().enumerate(){
   let span=spans[level];for ordinal in 0..span.count as usize{
    tagged.push((level,kind,ordinal,nodes[span.start as usize+ordinal]));
   }
  }
 }
 tagged.sort_unstable_by_key(|x|(x.0,x.1,x.2));
 let mut seen=vec![false;p.num_nodes];let mut inverse=Vec::with_capacity(p.num_nodes);
 for(_,_,_,old)in tagged {assert!(!seen[old as usize]);seen[old as usize]=true;inverse.push(old);}
 inverse.extend((0..p.num_nodes).filter(|&n|!seen[n]).map(|n|n as u32));
 assert_eq!(inverse.len(),p.num_nodes);
 let mut forward=vec![u32::MAX;p.num_nodes];for(new,&old)in inverse.iter().enumerate(){forward[old as usize]=new as u32;}
 assert_eq!(forward[0],0);assert_eq!(inverse[0],0);(forward,inverse)
}
fn d271_expected_rows<T:Clone>(v:&[T],inverse:&[u32])->Vec<T>{
 assert_eq!(v.len(),inverse.len());inverse.iter().map(|&old|v[old as usize].clone()).collect()
}
fn d271_expected_ids(v:&[u32],forward:&[u32])->Vec<u32>{
 v.iter().map(|&old|if old==u32::MAX{old}else{forward[old as usize]}).collect()
}
fn d271_normalize(name:&str,v:&[u32],forward:&[u32],inverse:&[u32])->Vec<u32>{
 if D271_ROW_FIELDS.contains(&name){
  let width=if name=="d_node_data_off"||name=="d_lock_off"{2}else{1};
  assert_eq!(v.len(),forward.len()*width);let mut out=vec![0;v.len()];
  for(old,&new)in forward.iter().enumerate(){out[old*width..(old+1)*width].copy_from_slice(&v[new as usize*width..(new as usize+1)*width]);}out
 }else if D271_ID_FIELDS.contains(&name){
  v.iter().map(|&new|if new==u32::MAX{new}else{inverse[new as usize]}).collect()
 }else{v.to_vec()}
}
fn d271_normalize_image(v:&mut[Vec<u32>],forward:&[u32],inverse:&[u32]){
 assert_eq!(v.len(),69);let mut at=3;
 for &name in D271_INVENTORY{if name!="d_cfv"{v[at]=d271_normalize(name,&v[at],forward,inverse);at+=1;}}
 assert_eq!(at,68); // index68 is unchanged current-player physical-layout logical CFV
}
fn d271_normalize_frame(mut bytes:Vec<u8>,forward:&[u32],inverse:&[u32])->Vec<u8>{
 assert_eq!(&bytes[..16],b"D150-FRAME-v1\0\0\0");let mut at=16;
 while at<bytes.len(){
  let kind=u32::from_le_bytes(bytes[at..at+4].try_into().unwrap());let n=u32::from_le_bytes(bytes[at+4..at+8].try_into().unwrap())as usize;at+=8;
  let name=std::str::from_utf8(&bytes[at..at+n]).unwrap().to_string();at+=n;
  let count=u64::from_le_bytes(bytes[at..at+8].try_into().unwrap())as usize;at+=8;
  if kind==0{assert_eq!(&bytes[at..at+4],&[0;4]);at+=4;}
  else{assert_eq!(kind,1);for _ in 0..2{
   let end=at+count*4;let v:Vec<u32>=bytes[at..end].chunks_exact(4).map(|x|u32::from_le_bytes(x.try_into().unwrap())).collect();
   let normalized=d271_normalize(&name,&v,forward,inverse);assert_eq!(normalized.len(),count);
   for(i,value)in normalized.iter().enumerate(){bytes[at+i*4..at+(i+1)*4].copy_from_slice(&value.to_le_bytes());}at=end;
  }}
 }
 assert_eq!(at,bytes.len());bytes
}
fn d271_dump_maps(path:&Path,forward:&[u32],inverse:&[u32]){
 let mut w=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(path).unwrap());
 w.write_all(b"D267-MODEL-v1\0\0\0").unwrap();w.write_all(&2u32.to_le_bytes()).unwrap();
 for(name,values)in[("old_to_new",forward),("new_to_old",inverse)]{
  w.write_all(&(name.len()as u32).to_le_bytes()).unwrap();w.write_all(name.as_bytes()).unwrap();
  w.write_all(&4u32.to_le_bytes()).unwrap();w.write_all(&(values.len()as u64).to_le_bytes()).unwrap();
  for v in values{w.write_all(&v.to_le_bytes()).unwrap();}
 }w.flush().unwrap();w.get_ref().sync_all().unwrap();
}
