fn emit(value: Value) { let mut o = std::io::stdout().lock(); writeln!(o, "D149_CONTROL {value}").unwrap(); o.flush().unwrap(); }
fn same_files(a: &Path, b: &Path) { assert_eq!(std::fs::read(a).unwrap(), std::fs::read(b).unwrap(), "{} {}", a.display(), b.display()); }
fn scenario(storage: Storage, algo: Algorithm, reverse: bool, iso: bool, warm: bool, extra_board: Option<&str>) -> (Solver, Solver) {
    let sizing = || StreetSizing { bet: parse_sizes("50").unwrap(), raise: vec![], donk: vec![] };
    let mut cfg = SpotConfig { board: extra_board.unwrap_or("KsQs2dJd").into(),
        range_oop: if extra_board.is_some() { "AA,AKs" } else { "AA,KK,QQ,JJ,TT,99,AKs,AQs,JTs,87s,AKo" }.into(),
        range_ip: if extra_board.is_some() { "QQ,QJs" } else { "AA,QQ,TT,77,55,AQs,KQs,QJs,98s,AQo" }.into(),
        tree: TreeConfig { starting_pot: 10., effective_stack: if extra_board.is_some() { 4. } else { 20. },
            oop: std::array::from_fn(|_| sizing()), ip: std::array::from_fn(|_| sizing()),
            rake_pct: if warm || (extra_board.is_some() && algo == Algorithm::CfrPlus) { 0.05 } else { 0. },
            rake_cap: 3., ..Default::default() } };
    if reverse { std::mem::swap(&mut cfg.range_oop, &mut cfg.range_ip); }
    let spot = Arc::new(Spot::new(cfg).unwrap());
    assert_ne!(spot.hands[0].len(), spot.hands[1].len());
    let mut a = Solver::with_storage(spot.clone(), storage);
    let mut b = Solver::with_storage(spot, storage);
    a.algo = algo; b.algo = algo; a.use_isomorphism = iso; b.use_isomorphism = iso;
    if warm { a.iterate(); b.iterate(); }
    (a, b)
}
fn poison(g: &mut observed::GpuSolver, out: &Path, id: usize, stage: &str, p: usize, epoch: &mut usize, witnesses: &mut Vec<Value>) {
    *epoch += 1;
    let before = out.join(format!("clobber-{id:02}-{stage}-before.gpu.bin"));
    let after = out.join(format!("clobber-{id:02}-{stage}-after.gpu.bin"));
    let proof = g.d149_clobber(&before, &after, p, *epoch);
    witnesses.push(json!({"stage": stage, "proof": proof}));
}
fn snapshot(b: &observed::GpuSolver, g: &observed::GpuSolver, out: &Path, id: usize, stage: &str, p: usize, cfv_regenerated: bool, records: &mut Vec<Value>) {
    let (x, bi, _) = b.d149_snapshot(&out.join(format!("baseline-{id:02}-{stage}.gpu.bin")), p);
    let (y, gi, _) = g.d149_snapshot(&out.join(format!("clobbered-{id:02}-{stage}.gpu.bin")), p);
    assert_eq!(bi, gi);
    if cfv_regenerated { assert_eq!(x, y, "all state and logical CFV {id}/{stage}"); }
    else { assert_eq!(x[..x.len() - 1], y[..y.len() - 1], "all persistent and nonCFV state {id}/{stage}"); }
    records.push(json!({"stage": stage, "CFV_regenerated": cfv_regenerated, "info": bi, "all65other_device_arrays_exact": true}));
}
fn train(b: &mut observed::GpuSolver, g: &mut observed::GpuSolver, out: &Path, id: usize, stage: &str, epoch: &mut usize, witnesses: &mut Vec<Value>, records: &mut Vec<Value>) {
    poison(g, out, id, stage, 1, epoch, witnesses);
    b.iterate().unwrap(); g.iterate().unwrap();
    snapshot(b, g, out, id, stage, 1, true, records);
}
fn evaluate(b: &mut observed::GpuSolver, g: &mut observed::GpuSolver, a: &Solver, c: &Solver, out: &Path, id: usize, stage: &str, epoch: &mut usize, witnesses: &mut Vec<Value>, records: &mut Vec<Value>, evs: &mut Vec<u64>) {
    poison(g, out, id, stage, 1, epoch, witnesses);
    let bx = b.exploitability(a).unwrap(); let gy = g.exploitability(c).unwrap();
    assert!(bx.is_finite() && gy.is_finite()); let x = bx.to_bits(); let y = gy.to_bits();
    assert_eq!(x, y); evs.push(x);
    snapshot(b, g, out, id, stage, 1, true, records);
}
fn cpu_pair(a: &Solver, c: &Solver, out: &Path, id: usize, stage: &str) {
    let x = out.join(format!("baseline-{id:02}-{stage}.cpu.bin")); let y = out.join(format!("clobbered-{id:02}-{stage}.cpu.bin"));
    state_frame(a, &x); state_frame(c, &y); same_files(&x, &y);
}
fn full_sync(b: &mut observed::GpuSolver, g: &mut observed::GpuSolver, a: &mut Solver, c: &mut Solver, out: &Path, id: usize, stage: &str, epoch: &mut usize, witnesses: &mut Vec<Value>, records: &mut Vec<Value>) {
    poison(g, out, id, stage, 1, epoch, witnesses);
    b.sync_to_cpu(a).unwrap(); g.sync_to_cpu(c).unwrap();
    cpu_pair(a, c, out, id, stage);
    snapshot(b, g, out, id, stage, 1, false, records);
}
fn main() {
    let out = PathBuf::from(std::env::args().nth(1).expect("fresh output")); std::fs::create_dir(&out).unwrap();
    let mut configs = Vec::new();
    for storage in [Storage::Compressed, Storage::F32] { for algo in [Algorithm::Dcfr, Algorithm::CfrPlus] { for reverse in [false, true] { for iso in [false, true] { for warm in [false, true] {
        configs.push((storage, algo, reverse, iso, warm, None));
    } } } } }
    for board in ["Ks7s2d", "Ks7s2dQhTc"] { for (algo, iso) in [(Algorithm::Dcfr, false), (Algorithm::CfrPlus, true)] {
        configs.push((Storage::Compressed, algo, false, iso, false, Some(board)));
    } }
    assert_eq!(configs.len(), 36);
    let mut all = Vec::new(); let mut epoch = 0usize; let mut phase_pairs = 0usize; let mut root_pairs = 0usize;
    for (id, (storage, algo, reverse, iso, warm, extra_board)) in configs.into_iter().enumerate() {
        let (mut a, mut c) = scenario(storage, algo, reverse, iso, warm, extra_board);
        cpu_pair(&a, &c, &out, id, "input");
        let mut b = observed::GpuSolver::new(&a).unwrap(); let mut g = observed::GpuSolver::new(&c).unwrap();
        let bp = out.join(format!("baseline-{id:02}-constructor.bin")); let gp = out.join(format!("clobbered-{id:02}-constructor.bin"));
        let bc = b.d149_validate(&a, &bp, !warm); let gc = g.d149_validate(&c, &gp, !warm); assert_eq!(bc, gc); same_files(&bp, &gp);
        let mut witnesses = Vec::new(); let mut records = Vec::new(); let mut evs = Vec::new(); let mut roots = Vec::new();
        for stage in ["train-first", "train-capture", "train-replay"] { train(&mut b, &mut g, &out, id, stage, &mut epoch, &mut witnesses, &mut records); }
        poison(&mut g, &out, id, "strategy-sync", 1, &mut epoch, &mut witnesses);
        b.sync_strategy(&mut a).unwrap(); g.sync_strategy(&mut c).unwrap(); cpu_pair(&a, &c, &out, id, "strategy-sync"); snapshot(&b, &g, &out, id, "strategy-sync", 1, false, &mut records);
        for stage in ["eval-eager", "eval-capture", "eval-replay"] { evaluate(&mut b, &mut g, &a, &c, &out, id, stage, &mut epoch, &mut witnesses, &mut records, &mut evs); }
        full_sync(&mut b, &mut g, &mut a, &mut c, &out, id, "full-sync", &mut epoch, &mut witnesses, &mut records);
        train(&mut b, &mut g, &out, id, "train-after-sync", &mut epoch, &mut witnesses, &mut records);
        b.sync_to_cpu(&mut a).unwrap(); g.sync_to_cpu(&mut c).unwrap(); a.ensure_symmetric(); c.ensure_symmetric();
        a.lock_node(&[], LockMode::Freeze, "control".into()).unwrap(); c.lock_node(&[], LockMode::Freeze, "control".into()).unwrap();
        b.update_locks(&a).unwrap(); g.update_locks(&c).unwrap();
        train(&mut b, &mut g, &out, id, "locked-train", &mut epoch, &mut witnesses, &mut records);
        for stage in ["locked-eval-eager", "locked-eval-capture"] { evaluate(&mut b, &mut g, &a, &c, &out, id, stage, &mut epoch, &mut witnesses, &mut records, &mut evs); }
        a.clear_locks(); c.clear_locks(); b.update_locks(&a).unwrap(); g.update_locks(&c).unwrap();
        train(&mut b, &mut g, &out, id, "unlocked-train", &mut epoch, &mut witnesses, &mut records);
        evaluate(&mut b, &mut g, &a, &c, &out, id, "unlocked-eval", &mut epoch, &mut witnesses, &mut records, &mut evs);
        full_sync(&mut b, &mut g, &mut a, &mut c, &out, id, "before-save", &mut epoch, &mut witnesses, &mut records);
        a.ensure_symmetric(); c.ensure_symmetric();
        let aq = serde_json::to_vec(&a.node_view(&[]).unwrap()).unwrap(); let cq = serde_json::to_vec(&c.node_view(&[]).unwrap()).unwrap(); assert_eq!(aq, cq);
        std::fs::write(out.join(format!("baseline-{id:02}-query.json")), &aq).unwrap(); std::fs::write(out.join(format!("clobbered-{id:02}-query.json")), &cq).unwrap();
        let sa = out.join(format!("baseline-{id:02}-state.save")); let sc = out.join(format!("clobbered-{id:02}-state.save")); a.save(sa.to_str().unwrap()).unwrap(); c.save(sc.to_str().unwrap()).unwrap(); same_files(&sa, &sc);
        drop(b); drop(g); drop(a); drop(c);
        let mut a = Solver::load_with_storage(sa.to_str().unwrap(), storage).unwrap(); let mut c = Solver::load_with_storage(sc.to_str().unwrap(), storage).unwrap(); cpu_pair(&a, &c, &out, id, "loaded");
        let mut b = observed::GpuSolver::new(&a).unwrap(); let mut g = observed::GpuSolver::new(&c).unwrap();
        train(&mut b, &mut g, &out, id, "resumed-train", &mut epoch, &mut witnesses, &mut records);
        for stage in ["resumed-eval-eager", "resumed-eval-capture", "resumed-eval-replay"] { evaluate(&mut b, &mut g, &a, &c, &out, id, stage, &mut epoch, &mut witnesses, &mut records, &mut evs); }
        full_sync(&mut b, &mut g, &mut a, &mut c, &out, id, "resumed-full-sync", &mut epoch, &mut witnesses, &mut records);
        assert_eq!(records.len(), 20); assert_eq!(evs.len(), 9);
        if algo == Algorithm::CfrPlus && !iso {
            for (i, p) in [0usize, 1, 0, 1].into_iter().enumerate() {
                let stage = format!("continuation-{i}-p{p}");
                let own: Vec<f32> = (0..a.spot.hands[p].len()).map(|j| if j % 4 == 0 { 0. } else { (j % 7 + 1) as f32 / 8. }).collect();
                let opp: Vec<f32> = (0..a.spot.hands[1-p].len()).map(|j| if j % 5 == 0 { 0. } else { (j % 5 + 1) as f32 / 6. }).collect();
                poison(&mut g, &out, id, &stage, p, &mut epoch, &mut witnesses);
                let x = b.research_continuation_sweep(p, 100 + (i / 2) as u32, &own, &opp).unwrap(); let y = g.research_continuation_sweep(p, 100 + (i / 2) as u32, &own, &opp).unwrap();
                assert!(x.iter().all(|v| v.is_finite()) && y.iter().all(|v| v.is_finite()));
                let xb: Vec<u32> = x.iter().map(|v| v.to_bits()).collect(); let yb: Vec<u32> = y.iter().map(|v| v.to_bits()).collect(); assert_eq!(xb, yb); roots.push(xb); root_pairs += 1;
                snapshot(&b, &g, &out, id, &stage, p, true, &mut records);
            }
            b.sync_to_cpu(&mut a).unwrap(); g.sync_to_cpu(&mut c).unwrap(); cpu_pair(&a, &c, &out, id, "continuation-final");
        }
        assert_eq!(witnesses.len(), records.len()); phase_pairs += records.len();
        all.push(json!({"case": id, "storage": format!("{storage:?}"), "algorithm": format!("{algo:?}"), "reverse_ranges": reverse, "isomorphism": iso, "warm_CPU_start": warm, "extra_board": extra_board, "constructor": bc, "clobbers": witnesses, "phases": records, "exploit_bits": evs, "continuation_root_bits": roots, "all_CPU_query_save_files_exact": true}));
        emit(json!({"stage": "case_complete", "case": id, "phases": all.last().unwrap()["phases"].as_array().unwrap().len(), "exact": true}));
    }
    assert_eq!(phase_pairs, 752); assert_eq!(epoch, 752); assert_eq!(root_pairs, 32);
    let metadata = json!({"id": "D149", "cases": all, "case_count": 36, "clobbers": epoch, "phase_pairs": phase_pairs, "constructor_pairs": 36, "exploitability_pairs": 324, "continuation_root_pairs": root_pairs, "performance_measurement": false, "packing_implementation_created": false});
    let mut f = OpenOptions::new().create_new(true).write(true).open(out.join("metadata.json")).unwrap(); f.write_all(serde_json::to_string_pretty(&metadata).unwrap().as_bytes()).unwrap(); f.sync_all().unwrap();
    emit(json!({"stage": "complete", "cases": 36, "clobbers": epoch, "phase_pairs": phase_pairs, "continuation_root_pairs": root_pairs}));
}
