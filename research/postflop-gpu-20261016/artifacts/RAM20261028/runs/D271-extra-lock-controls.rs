fn d271_extra_snapshot(b:&observed::GpuSolver,g:&observed::GpuSolver,out:&Path,stage:&str)->Value{
 let(x,bi,bp)=b.d150_snapshot(&out.join(format!("baseline-{stage}.gpu.bin")),1);
 let(y,gi,gp)=g.d150_snapshot(&out.join(format!("clobbered-{stage}.gpu.bin")),1);
 assert_eq!(bi,gi);assert_eq!(x,y);assert_eq!(bp,gp,"entire physical CFV in nonpoisoned extra control");
 json!({"stage":stage,"info":bi,"all66_actual_arrays_and_whole_physical_CFV_exact":true})
}
fn d271_extra_lock_controls(out:&Path){
 let cases=[(Storage::Compressed,Algorithm::Dcfr,true,"Ks7s2d"),
  (Storage::Compressed,Algorithm::CfrPlus,true,"Ks7s2d"),
  (Storage::F32,Algorithm::Dcfr,true,"Ks7s2d"),
  (Storage::Compressed,Algorithm::Dcfr,false,"Ks7s2d"),
  (Storage::Compressed,Algorithm::Dcfr,true,"KsQs2dJd"),
  (Storage::Compressed,Algorithm::Dcfr,true,"Ks7s2dQhTc")];
 let extra=out.join("extra");std::fs::create_dir(&extra).unwrap();let mut all=Vec::new();
 for(id,(storage,algo,iso,board))in cases.into_iter().enumerate(){
  let folder=extra.join(id.to_string());std::fs::create_dir(&folder).unwrap();
  let(mut a,mut c)=scenario(storage,algo,false,iso,false,Some(board));
  let mut b=d271_new(0,&a);let mut g=d271_new(1,&c);
  let plan=d271_cpu_plan(&a);let mut records=Vec::new();let mut evs=Vec::new();
  let bp=folder.join("baseline-constructor.bin");let gp=folder.join("clobbered-constructor.bin");
  assert_eq!(b.d150_validate(&a,&bp,true),g.d150_validate(&c,&gp,true));g.d271_same_constructor(&bp,&gp);
  for _ in 0..3{b.iterate().unwrap();g.iterate().unwrap();}
  for _ in 0..3{let x=b.exploitability(&a).unwrap();let y=g.exploitability(&c).unwrap();assert!(x.is_finite()&&y.is_finite());assert_eq!(x.to_bits(),y.to_bits());evs.push(x.to_bits());}
  records.push(d271_extra_snapshot(&b,&g,&folder,"warm"));
  let mut categories=Vec::new();let mut chosen=Vec::new();
  for category in ["root","active_action","inactive_action","chance","fold","show"]{
   let possible:Vec<usize>=a.spot.tree.nodes.iter().enumerate().filter_map(|(i,n)|{
    let yes=match category{
     "root"=>i==0,
     "active_action"=>i>0&&n.kind==tree::KIND_ACTION&&plan.node_data_off[i]!=u64::MAX,
     "inactive_action"=>i>0&&n.kind==tree::KIND_ACTION&&plan.node_data_off[i]==u64::MAX,
     "chance"=>n.kind==tree::KIND_CHANCE,"fold"=>n.kind==tree::KIND_TERM_FOLD,"show"=>n.kind==tree::KIND_TERM_SHOWDOWN,_=>false};
    yes.then_some(i)
   }).collect();
   let selected=possible.iter().copied().find(|&i|g.forward[i]!=i as u32).or_else(||possible.first().copied());
   categories.push(json!({"category":category,"available":possible.len(),"chosen":selected,"changed_ID":selected.map(|i|g.forward[i]!=i as u32).unwrap_or(false)}));
   if let Some(i)=selected{assert!(!chosen.contains(&i));chosen.push(i);let n=&a.spot.tree.nodes[i];
    let sigma=if n.kind==tree::KIND_ACTION{
     let nh=a.spot.hands[n.player as usize].len();let mut v=vec![0.;n.num_children as usize*nh];v[..nh].fill(1.);v
    }else{[0,0x80000000,0x7fc00123,0x7f800123].into_iter().map(f32::from_bits).collect()};
    a.locks.insert(i as u32,sigma);
   }
  }
  if g.selected{
   assert!(categories.iter().any(|x|x["category"]=="active_action"&&x["changed_ID"]==true));
   assert!(categories.iter().any(|x|["chance","fold","show"].contains(&x["category"].as_str().unwrap())&&x["changed_ID"]==true));
  }
  c.locks=a.locks.clone();
  b.update_locks(&a).unwrap();g.update_locks(&c).unwrap();
  let uploaded=d271_extra_snapshot(&b,&g,&folder,"lock-upload");assert_eq!(uploaded["info"]["graphs_present"],false);assert_eq!(uploaded["info"]["eval_graphs_present"],json!([false,false]));records.push(uploaded);
  for _ in 0..3{b.iterate().unwrap();g.iterate().unwrap();}
  for _ in 0..3{let x=b.exploitability(&a).unwrap();let y=g.exploitability(&c).unwrap();assert!(x.is_finite()&&y.is_finite());assert_eq!(x.to_bits(),y.to_bits());evs.push(x.to_bits());}
  records.push(d271_extra_snapshot(&b,&g,&folder,"locked"));
  a.clear_locks();c.clear_locks();b.update_locks(&a).unwrap();g.update_locks(&c).unwrap();
  let unlocked=d271_extra_snapshot(&b,&g,&folder,"unlock-upload");assert_eq!(unlocked["info"]["graphs_present"],false);assert_eq!(unlocked["info"]["eval_graphs_present"],json!([false,false]));records.push(unlocked);
  for _ in 0..3{b.iterate().unwrap();g.iterate().unwrap();}
  for _ in 0..3{let x=b.exploitability(&a).unwrap();let y=g.exploitability(&c).unwrap();assert!(x.is_finite()&&y.is_finite());assert_eq!(x.to_bits(),y.to_bits());evs.push(x.to_bits());}
  records.push(d271_extra_snapshot(&b,&g,&folder,"unlocked"));
  b.sync_to_cpu(&mut a).unwrap();g.sync_to_cpu(&mut c).unwrap();
  let ap=folder.join("baseline-final.cpu.bin");let cp=folder.join("clobbered-final.cpu.bin");state_frame(&a,&ap);state_frame(&c,&cp);same_files(&ap,&cp);
  assert_eq!(records.len(),5);assert_eq!(evs.len(),9);
  all.push(json!({"case":id,"storage":format!("{storage:?}"),"algorithm":format!("{algo:?}"),"iso":iso,"board":board,"selected":g.selected,"categories":categories,"phases":records,"EV_bits":evs,"CPU_state_exact":true}));
  println!("D271_EXTRA {}",json!({"case":id,"selected":g.selected,"phases":5,"EVs":9,"exact":true}));std::io::stdout().flush().unwrap();
 }
 assert!(all.iter().any(|x|x["selected"]==true));assert!(all.iter().any(|x|x["selected"]==false));
 let mut file=OpenOptions::new().create_new(true).write(true).open(out.join("extra-metadata.json")).unwrap();
 file.write_all(serde_json::to_string_pretty(&all).unwrap().as_bytes()).unwrap();file.sync_all().unwrap();
}
