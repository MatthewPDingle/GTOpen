fn emit(value:Value){let mut o=std::io::stdout().lock();writeln!(o,"E090_CONTROL {value}").unwrap();o.flush().unwrap();}
fn same_files(a:&Path,b:&Path){assert_eq!(std::fs::read(a).unwrap(),std::fs::read(b).unwrap(),"whole files {} {}",a.display(),b.display());}
fn scenario(storage:Storage,algo:Algorithm,reverse:bool,iso:bool,warm:bool)->(Solver,Solver) {
    let sizing=||StreetSizing{bet:parse_sizes("50").unwrap(),raise:vec![],donk:vec![]};
    let mut cfg=SpotConfig{board:"KsQs2dJd".into(),range_oop:"AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo".into(),range_ip:"AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo".into(),
        tree:TreeConfig{starting_pot:10.,effective_stack:20.,oop:std::array::from_fn(|_|sizing()),ip:std::array::from_fn(|_|sizing()),rake_pct:if warm{0.05}else{0.},rake_cap:3.,..Default::default()}};
    if reverse{std::mem::swap(&mut cfg.range_oop,&mut cfg.range_ip);}
    let spot=Arc::new(Spot::new(cfg).unwrap());assert_ne!(spot.hands[0].len(),spot.hands[1].len());
    let mut a=Solver::with_storage(spot.clone(),storage);let mut b=Solver::with_storage(spot,storage);
    a.algo=algo;b.algo=algo;a.use_isomorphism=iso;b.use_isomorphism=iso;
    if warm{a.iterate();b.iterate();}
    (a,b)
}
fn snapshot(b:&baseline::GpuSolver,c:&candidate::GpuSolver,out:&Path,id:usize,stage:&str,p:usize,poisoned:bool,proofs:&mut Vec<Value>){
    let bf=out.join(format!("baseline-{id:02}-{stage}.gpu.bin"));
    let cf=out.join(format!("candidate-{id:02}-{stage}.gpu.bin"));
    let (x,bi)=b.e090_snapshot(&bf,p,poisoned);let(y,ci)=c.e090_snapshot(&cf,p,poisoned);
    assert_eq!(x,y,"all learning/reach/discount/lock/logicalCFV words {id} {stage}");
    for k in ["p","rows","logical_hands","original_width","physical_words","logical_words","poisoned","full_physical_guard_words","wrapper_bytes","pinned_words","arena_words","reach_words","graphs_present","eval_graph_present"]{assert_eq!(bi[k],ci[k],"{k}");}
    proofs.push(json!({"stage":stage,"baseline":bi,"candidate":ci,"all_logical_and_other_full_images_exact":true}));
}
fn cpu_pair(a:&Solver,b:&Solver,out:&Path,id:usize,stage:&str){
    let x=out.join(format!("baseline-{id:02}-{stage}.cpu.bin"));let y=out.join(format!("candidate-{id:02}-{stage}.cpu.bin"));
    state_frame(a,&x);state_frame(b,&y);same_files(&x,&y);
}
fn main(){
    let out=PathBuf::from(std::env::args().nth(1).expect("fresh output"));std::fs::create_dir(&out).unwrap();
    let mut cases=Vec::new();let mut id=0usize;
    for storage in[Storage::Compressed,Storage::F32]{for algo in[Algorithm::Dcfr,Algorithm::CfrPlus]{for reverse in[false,true]{for iso in[false,true]{for warm in[false,true]{
        let(mut a,mut c)=scenario(storage,algo,reverse,iso,warm);
        cpu_pair(&a,&c,&out,id,"input");
        let be=baseline::GpuSolver::new_with_budget(&a,1).err().unwrap();let ce=candidate::GpuSolver::new_with_budget(&c,1).err().unwrap();assert_eq!(be,ce);assert!(be.contains("budget"));
        let mut b=baseline::GpuSolver::new(&a).unwrap();let mut g=candidate::GpuSolver::new(&c).unwrap();
        b.synchronize().unwrap();g.synchronize().unwrap();
        let bc=out.join(format!("baseline-{id:02}-constructor.bin"));let cc=out.join(format!("candidate-{id:02}-constructor.bin"));
        let bp=b.e090_validate(&a,&bc,!warm);let cp=g.e090_validate(&c,&cc,!warm);assert_eq!(bp,cp);same_files(&bc,&cc);
        let mut proofs=Vec::new();let mut exploit=Vec::new();
        for p in 0..2{
            b.e090_force_sweep(p);g.e090_force_sweep(p);
            snapshot(&b,&g,&out,id,&format!("forced-p{p}"),p,true,&mut proofs);
        }
        for i in 0..2{
            b.iterate().unwrap();g.iterate().unwrap();
            snapshot(&b,&g,&out,id,&format!("graph-iteration-{i}"),1,false,&mut proofs);
        }
        for i in 0..2{
            let x=b.exploitability(&a).unwrap().to_bits();let y=g.exploitability(&c).unwrap().to_bits();assert_eq!(x,y);exploit.push(x);
            snapshot(&b,&g,&out,id,&format!("evaluation-{i}"),1,false,&mut proofs);
        }
        b.sync_strategy(&mut a).unwrap();g.sync_strategy(&mut c).unwrap();cpu_pair(&a,&c,&out,id,"strategy");
        b.sync_to_cpu(&mut a).unwrap();g.sync_to_cpu(&mut c).unwrap();cpu_pair(&a,&c,&out,id,"full");
        a.ensure_symmetric();c.ensure_symmetric();
        let aq=serde_json::to_vec(&a.node_view(&[]).unwrap()).unwrap();let cq=serde_json::to_vec(&c.node_view(&[]).unwrap()).unwrap();assert_eq!(aq,cq);
        std::fs::write(out.join(format!("baseline-{id:02}-query.json")),&aq).unwrap();std::fs::write(out.join(format!("candidate-{id:02}-query.json")),&cq).unwrap();
        a.lock_node(&[],LockMode::Freeze,"control".into()).unwrap();c.lock_node(&[],LockMode::Freeze,"control".into()).unwrap();
        b.update_locks(&a).unwrap();g.update_locks(&c).unwrap();b.iterate().unwrap();g.iterate().unwrap();
        for _ in 0..2{let x=b.exploitability(&a).unwrap().to_bits();let y=g.exploitability(&c).unwrap().to_bits();assert_eq!(x,y);exploit.push(x);}
        snapshot(&b,&g,&out,id,"locked-recapture",1,false,&mut proofs);
        a.clear_locks();c.clear_locks();b.update_locks(&a).unwrap();g.update_locks(&c).unwrap();b.iterate().unwrap();g.iterate().unwrap();
        snapshot(&b,&g,&out,id,"unlocked-recapture",1,false,&mut proofs);
        b.sync_to_cpu(&mut a).unwrap();g.sync_to_cpu(&mut c).unwrap();a.ensure_symmetric();c.ensure_symmetric();cpu_pair(&a,&c,&out,id,"before-save");
        let asave=out.join(format!("baseline-{id:02}-state.save"));let csave=out.join(format!("candidate-{id:02}-state.save"));
        a.save(asave.to_str().unwrap()).unwrap();c.save(csave.to_str().unwrap()).unwrap();same_files(&asave,&csave);
        drop(b);drop(g);drop(a);drop(c);
        let mut a=Solver::load_with_storage(asave.to_str().unwrap(),storage).unwrap();let mut c=Solver::load_with_storage(csave.to_str().unwrap(),storage).unwrap();cpu_pair(&a,&c,&out,id,"loaded");
        let mut b=baseline::GpuSolver::new(&a).unwrap();let mut g=candidate::GpuSolver::new(&c).unwrap();b.iterate().unwrap();g.iterate().unwrap();
        snapshot(&b,&g,&out,id,"resumed",1,false,&mut proofs);
        b.sync_to_cpu(&mut a).unwrap();g.sync_to_cpu(&mut c).unwrap();cpu_pair(&a,&c,&out,id,"resumed");
        assert_eq!(proofs.len(),9);assert_eq!(exploit.len(),4);
        cases.push(json!({"case":id,"storage":format!("{storage:?}"),"algorithm":format!("{algo:?}"),"reverse_ranges":reverse,"isomorphism":iso,"warm_CPU_start":warm,"raked":warm,"budget_error":be,"constructor":bp,"snapshots":proofs,"exploit_bits":exploit,"all_CPU_query_save_files_exact":true}));
        emit(json!({"stage":"case_complete","case":id,"snapshots":9,"exact":true}));id+=1;
    }}}}}
    assert_eq!(id,32);
    let meta=json!({"id":"E090-engine-control","cases":cases,"case_count":32,"GPU_snapshot_pairs":288,"constructor_pairs":32,"exploitability_pairs":128,"standard_training_iterations":320,"extra_single_player_sweeps":128,"performance_measurement":false,"candidate_accepted":false});
    let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("metadata.json")).unwrap();f.write_all(serde_json::to_string_pretty(&meta).unwrap().as_bytes()).unwrap();f.sync_all().unwrap();
    emit(json!({"stage":"complete","cases":32,"GPU_snapshot_pairs":288,"performance_measurement":false}));
}
