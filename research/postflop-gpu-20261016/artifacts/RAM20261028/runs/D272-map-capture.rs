fn d272_map_capture(g:&GpuSolver,s:&Solver,name:&str,constructor:&str){
 let(p,forward,inverse,info)=g.d272_map_data(s);
 let out=std::path::PathBuf::from(std::env::var("D156_OUTPUT").unwrap());
 let stem=format!("{name}-{constructor}.map");
 dump_baseline(&p,&out.join(format!("{stem}.plan.bin")));
 d272_dump_maps(&out.join(format!("{stem}.maps.bin")),&forward,&inverse);
 {let mut file=OpenOptions::new().create_new(true).write(true).open(out.join(format!("{stem}.kinds.bin"))).unwrap();
  for n in &s.spot.tree.nodes{file.write_all(&[n.kind]).unwrap();}file.sync_all().unwrap();}
 println!("D272_METADATA {}",json!({"arm":"@ARM@","fixture":name,"constructor":constructor,"plan_file":format!("{stem}.plan.bin"),"maps_file":format!("{stem}.maps.bin"),"kinds_file":format!("{stem}.kinds.bin"),"info":info}));
 std::io::stdout().flush().unwrap();
}
