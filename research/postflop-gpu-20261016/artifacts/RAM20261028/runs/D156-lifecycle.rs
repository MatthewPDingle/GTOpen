fn d156_cpu(path:&std::path::Path,s:&Solver) {
    let mut f=std::io::BufWriter::new(std::fs::OpenOptions::new().create_new(true).write(true).open(path).unwrap());
    f.write_all(b"D156-CPU-RAW1\0\0\0").unwrap();
    for v in [s.iteration,s.use_isomorphism as u32,s.locks.len()as u32,s.preds.is_some()as u32] {f.write_all(&v.to_le_bytes()).unwrap();}
    for stores in [&s.regrets,&s.strat] {for store in stores {
        match store {
            Store::I16{q,scale}=>{f.write_all(&1u32.to_le_bytes()).unwrap();f.write_all(&(q.len()as u64).to_le_bytes()).unwrap();f.write_all(&(scale.len()as u64).to_le_bytes()).unwrap();for v in q.as_slice(){f.write_all(&v.to_le_bytes()).unwrap();}for v in scale.as_slice(){f.write_all(&v.to_bits().to_le_bytes()).unwrap();}},
            Store::U16{q,scale}=>{f.write_all(&2u32.to_le_bytes()).unwrap();f.write_all(&(q.len()as u64).to_le_bytes()).unwrap();f.write_all(&(scale.len()as u64).to_le_bytes()).unwrap();for v in q.as_slice(){f.write_all(&v.to_le_bytes()).unwrap();}for v in scale.as_slice(){f.write_all(&v.to_bits().to_le_bytes()).unwrap();}},
            Store::F32(_)=>panic!("fixed compressed primary control"),
        }
    }}
    f.flush().unwrap();f.get_ref().sync_all().unwrap();
}
fn d156_stage(g:&GpuSolver,s:&Solver,out:&std::path::Path,name:&str,stage:&str,ev:Option<u64>) -> Value {
    d156_cpu(&out.join(format!("{name}-{stage}.cpu.bin")),s);
    let info=g.d156_snapshot(&out.join(format!("{name}-{stage}.cfv.u32")));
    json!({"stage":stage,"iteration":s.iteration,"ev_bits":ev,"info":info})
}
fn d156_query(out:&std::path::Path,name:&str,stage:&str,s:&mut Solver) {
    s.ensure_symmetric();let q=serde_json::to_vec(&s.node_view(&[]).unwrap()).unwrap();
    let mut f=std::fs::OpenOptions::new().create_new(true).write(true).open(out.join(format!("{name}-{stage}.query.json"))).unwrap();f.write_all(&q).unwrap();f.sync_all().unwrap();
}
fn d156_after(mut g:GpuSolver,mut s:Solver,name:&str) {
    let out=std::path::PathBuf::from(std::env::var("D156_OUTPUT").unwrap());
    assert_eq!(s.algo,Algorithm::Dcfr);assert!(s.use_isomorphism);
    let mut stages=vec![d156_stage(&g,&s,&out,name,"converged",None)];
    g.iterate().unwrap();let e=g.exploitability(&s).unwrap();assert!(e.is_finite());g.sync_to_cpu(&mut s).unwrap();
    stages.push(d156_stage(&g,&s,&out,name,"continued",Some(e.to_bits())));
    s.ensure_symmetric();s.lock_node(&[],solver::LockMode::Freeze,"D156".into()).unwrap();g.update_locks(&s).unwrap();
    g.iterate().unwrap();let e=g.exploitability(&s).unwrap();assert!(e.is_finite());g.sync_to_cpu(&mut s).unwrap();
    stages.push(d156_stage(&g,&s,&out,name,"locked",Some(e.to_bits())));d156_query(&out,name,"locked",&mut s);
    let save=out.join(format!("{name}.save"));s.save(save.to_str().unwrap()).unwrap();drop(g);drop(s);
    let mut s=Solver::load_with_storage(save.to_str().unwrap(),Storage::Compressed).unwrap();assert_eq!(s.algo,Algorithm::Dcfr);assert!(s.use_isomorphism);
    let mut g=GpuSolver::new(&s).unwrap();g.iterate().unwrap();let e=g.exploitability(&s).unwrap();assert!(e.is_finite());g.sync_to_cpu(&mut s).unwrap();
    stages.push(d156_stage(&g,&s,&out,name,"resumed",Some(e.to_bits())));d156_query(&out,name,"resumed",&mut s);
    drop(g);drop(s);
    println!("D156_CONTROL {}",json!({"fixture_id":name,"stages":stages,"all_GPU_and_CPU_objects_dropped":true,"performance_measurement":false}));std::io::stdout().flush().unwrap();
}
