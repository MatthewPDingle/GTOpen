
// E041 test-only accepted-writer versus candidate GPU lifecycle control.
#[cfg(test)]
mod e041_zero_restore_control {
    use super::*;
    use super::super::GpuSolver;
    use crate::{Spot, SpotConfig, StreetSizing, TreeConfig, parse_sizes};
    use crate::store::Storage;
    use serde_json::{json, Value};
    use std::io::{BufWriter, Write};
    use std::path::{Path, PathBuf};
    use std::sync::atomic::Ordering;
    type R<T> = Result<T, String>;
    struct DrainOnDrop(GpuSolver);
    impl std::ops::Deref for DrainOnDrop {
        type Target = GpuSolver;
        fn deref(&self) -> &GpuSolver { &self.0 }
    }
    impl std::ops::DerefMut for DrainOnDrop {
        fn deref_mut(&mut self) -> &mut GpuSolver { &mut self.0 }
    }
    impl Drop for DrainOnDrop {
        fn drop(&mut self) {
            if let Err(error) = self.0.synchronize() {
                let _ = writeln!(std::io::stderr().lock(), "E041_CONTROL_CLEANUP_ERROR {error}");
            }
        }
    }

    impl ArenaLayout {
    fn e041_original_write(&self, solver: &Solver, p: usize, which: usize, data: &[f32]) {
        if !self.compact {
            write_arena(solver, which != 0, p, data);
            return;
        }
        let store = if which == 0 { &solver.regrets[p] } else { &solver.strat[p] };
        if let Store::F32(buf) = store {
            // Host spans are disjoint, just like parallel CPU CFR arenas.
            self.copies.par_iter().for_each(|span| {
                unsafe { buf.slice(span.host, span.len) }
                    .copy_from_slice(&data[span.device..span.device + span.len]);
            });
            self.inactive.par_iter().for_each(|block| {
                let dst = unsafe { buf.slice(block.host, block.len) };
                let start = block.initial[which];
                if start == usize::MAX { dst.fill(0.0); }
                else { dst.copy_from_slice(&self.initial[which][start..start + block.len]); }
            });
            return;
        }
        self.active.par_iter().for_each(|block| {
            unsafe {
                store.write_f32(block.node, block.host, block.len,
                    &data[block.device..block.device + block.len]);
            }
        });
        self.inactive.par_iter().for_each(|block| {
            let start = block.initial[which];
            let values = if start == usize::MAX { &self.zeros[..block.len] }
                else { &self.initial[which][start..start + block.len] };
            unsafe { store.write_f32(block.node, block.host, block.len, values); }
        });
    }
    }
    fn legacy_sync(gpu: &mut GpuSolver, solver: &mut Solver) -> Result<(), String> {
        gpu.stream.synchronize().map_err(e)?;
        for p in 0..2 {
            let len = gpu.d_regrets[p].len();
            gpu.stream
                .memcpy_dtoh(&gpu.d_regrets[p], &mut gpu.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            gpu.stream.synchronize().map_err(e)?;
            gpu.arena_layout[p].e041_original_write(solver, p, 0, &gpu.h_staging.as_slice()[..len]);
            gpu.stream
                .memcpy_dtoh(&gpu.d_strat[p], &mut gpu.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            gpu.stream.synchronize().map_err(e)?;
            gpu.arena_layout[p].e041_original_write(solver, p, 1, &gpu.h_staging.as_slice()[..len]);
        }
        solver.iteration = gpu.iteration;
        if gpu.iso_active {
            // only representative branches hold fresh data; queries/saves
            // re-materialize siblings via Solver::ensure_symmetric
            solver.mark_sym_dirty();
        }
        Ok(())
    }

    fn legacy_strategy(gpu: &mut GpuSolver, solver: &mut Solver) -> Result<(), String> {
        gpu.stream.synchronize().map_err(e)?;
        for p in 0..2 {
            let len = gpu.d_strat[p].len();
            gpu.stream
                .memcpy_dtoh(&gpu.d_strat[p], &mut gpu.h_staging.as_mut_slice()[..len])
                .map_err(e)?;
            gpu.stream.synchronize().map_err(e)?;
            gpu.arena_layout[p].e041_original_write(solver, p, 1, &gpu.h_staging.as_slice()[..len]);
        }
        solver.iteration = gpu.iteration;
        if gpu.iso_active {
            solver.mark_sym_dirty();
        }
        Ok(())
    }
    fn u32_word(out: &mut Vec<u8>, v: u32) { out.extend(v.to_le_bytes()); }
    fn u64_word(out: &mut Vec<u8>, v: u64) { out.extend(v.to_le_bytes()); }
    fn host_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E041HOST1".to_vec();
        u64_word(&mut out, s.iteration as u64);
        out.push(u8::from(s.use_isomorphism));
        for store in [&s.regrets[0], &s.regrets[1], &s.strat[0], &s.strat[1]] {
            match store {
                Store::F32(b) => {
                    u32_word(&mut out, 0); u64_word(&mut out, b.len() as u64);
                    for v in b.as_slice() { u32_word(&mut out, v.to_bits()); }
                }
                Store::I16 { q, scale } => {
                    u32_word(&mut out, 1); u64_word(&mut out, q.len() as u64);
                    for v in q.as_slice() { out.extend(v.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for v in scale.as_slice() { u32_word(&mut out, v.to_bits()); }
                }
                Store::U16 { q, scale } => {
                    u32_word(&mut out, 2); u64_word(&mut out, q.len() as u64);
                    for v in q.as_slice() { out.extend(v.to_le_bytes()); }
                    u64_word(&mut out, scale.len() as u64);
                    for v in scale.as_slice() { u32_word(&mut out, v.to_bits()); }
                }
            }
        }
        out
    }
    fn seed(s: &mut Solver, salt: usize) {
        for (which, store) in s.regrets.iter_mut().chain(&mut s.strat).enumerate() {
            match store {
                Store::F32(b) => {
                    for (i,v) in b.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i * 73 + which * 997 + salt) % 1009 + 1) as f32 / 32.0;
                        if which < 2 && i % 3 == 0 { *v = -*v; }
                    }
                }
                Store::I16 { q, scale } => {
                    for (i,v) in q.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i * 73 + which * 997 + salt) % 60001) as i32 as i16;
                    }
                    for (i,v) in scale.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i + which * 7 + salt) % 127 + 1) as f32 / 32.0;
                    }
                }
                Store::U16 { q, scale } => {
                    for (i,v) in q.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i * 71 + which * 991 + salt) % 65535 + 1) as u16;
                    }
                    for (i,v) in scale.as_mut_slice().iter_mut().enumerate() {
                        *v = ((i + which * 11 + salt) % 131 + 1) as f32 / 128.0;
                    }
                }
            }
        }
        s.iteration = if salt == 1 { 0 } else { 999 };
    }
    fn target(spot: &Arc<Spot>, storage: Storage, iso: bool) -> Solver {
        let mut s = Solver::with_storage(spot.clone(), storage);
        s.use_isomorphism = iso;
        seed(&mut s, 37);
        s
    }
    fn query_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E041QUERY1".to_vec();
        let mut nonuniform = false;
        for (id,node) in s.spot.tree.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            let nh = s.spot.hands[node.player as usize].len();
            let mut sigma = vec![f32::NAN; nh * node.num_children as usize];
            s.solved_strategy_into(node, &mut sigma);
            u32_word(&mut out, id as u32);
            u64_word(&mut out, sigma.len() as u64);
            if node.num_children > 1 {
                nonuniform |= (0..nh).any(|i| sigma[i].to_bits() != sigma[nh+i].to_bits());
            }
            assert!(sigma.iter().all(|x| x.is_finite()));
            for v in sigma { u32_word(&mut out, v.to_bits()); }
        }
        assert!(nonuniform, "query must exercise nonuniform strategy");
        out
    }
    fn device_image(gpu: &GpuSolver) -> R<Vec<u8>> {
        gpu.synchronize()?;
        let mut out = b"E041GPU1".to_vec();
        for d in [&gpu.d_regrets[0],&gpu.d_regrets[1],&gpu.d_strat[0],&gpu.d_strat[1]] {
            let v = gpu.stream.clone_dtoh(d).map_err(e)?;
            assert!(v.iter().all(|x| x.is_finite()));
            assert!(v.windows(2).any(|x| x[0].to_bits() != x[1].to_bits()));
            u64_word(&mut out, v.len() as u64);
            for x in v { u32_word(&mut out, x.to_bits()); }
        }
        Ok(out)
    }
    fn retain(dir: &Path, name: &str, bytes: &[u8], files: &mut Vec<Value>) -> R<()> {
        let file = std::fs::OpenOptions::new().write(true).create_new(true).open(dir.join(name)).map_err(e)?;
        let mut w = BufWriter::new(file);
        w.write_all(bytes).map_err(e)?; w.flush().map_err(e)?; w.get_ref().sync_all().map_err(e)?;
        files.push(json!({"file":name,"bytes":bytes.len()})); Ok(())
    }
    fn pair(dir: &Path, label: &str, a: Vec<u8>, b: Vec<u8>, files: &mut Vec<Value>) -> R<()> {
        retain(dir,&format!("{label}.reference.bin"),&a,files)?;
        retain(dir,&format!("{label}.candidate.bin"),&b,files)?;
        assert_eq!(a,b,"{label}"); Ok(())
    }
    fn saves(dir: &Path, label: &str, a: &Solver, b: &Solver, files: &mut Vec<Value>) -> R<()> {
        let mut bytes = Vec::new();
        for (arm,s) in [("reference",a),("candidate",b)] {
            let name = format!("{label}.{arm}.save");
            let path = dir.join(&name);
            assert!(!path.exists() && !path.with_extension("save.tmp").exists());
            s.save(path.to_str().ok_or("output encoding")?)?;
            let raw = std::fs::read(path).map_err(e)?;
            files.push(json!({"file":name,"bytes":raw.len()})); bytes.push(raw);
        }
        assert_eq!(bytes[0],bytes[1]); Ok(())
    }
    fn geometry(g: &GpuSolver) -> (usize,usize,[usize;4]) {
        (g.h_staging.ptr as usize,g.h_staging.len,
         [g.d_regrets[0].len(),g.d_regrets[1].len(),g.d_strat[0].len(),g.d_strat[1].len()])
    }
    fn run_case(dir: &Path, storage: Storage, iso: bool) -> R<Value> {
        let size = StreetSizing { bet:parse_sizes("50")?,raise:vec![],donk:vec![] };
        let spot = Arc::new(Spot::new_with_limit(SpotConfig {
            board:"KsQs2dJd".into(),range_oop:"AA,KK,QQ,JJ,AKs,AQs,AKo".into(),
            range_ip:"AA,QQ,TT,77,AQs,KQs,AQo".into(),
            tree:TreeConfig { starting_pot:10.0,effective_stack:20.0,
                oop:[size.clone(),size.clone(),size.clone()],ip:[size.clone(),size.clone(),size],
                ..Default::default() },
        },Some(20_000))?);
        assert!(spot.tree.data_size.iter().sum::<u64>() <= 250_000);
        let mut input = Solver::with_storage(spot.clone(),storage);
        input.use_isomorphism = iso; seed(&mut input,1);
        let plan = GpuPlan::build(&spot,iso);
        if iso {
            let mut inactive_ordinal = [0usize;2];
            for (i,node) in spot.tree.nodes.iter().enumerate() {
                if node.kind == KIND_ACTION && plan.node_data_off[i] == u64::MAX {
                    let p = node.player as usize;
                    inactive_ordinal[p] += 1;
                    if inactive_ordinal[p] % 2 != 0 { continue; }
                    let count = node.num_children as usize * spot.hands[p].len();
                    for store in [&input.regrets[p],&input.strat[p]] {
                        unsafe { store.write_f32(i as u32,node.data_offset,count,&vec![0.0;count]); }
                    }
                    if let Store::F32(b) = &input.regrets[p] {
                        unsafe { b.write_at(node.data_offset as usize,-0.0); }
                    }
                }
            }
        }
        let budget = if storage == Storage::F32 && iso {
            plan.staging_bytes() + (plan.arena_elements[0]+plan.arena_elements[1]) as u64 * 8 + 512*1024*1024
        } else { u64::MAX };
        let mut gpu = DrainOnDrop(GpuSolver::new_with_budget(&input,budget)?);
        let owner = gpu._ctx.clone();
        for p in 0..2 {
            assert_eq!(gpu.arena_layout[p].compact,iso);
            if iso {
                assert!(!gpu.arena_layout[p].inactive.is_empty());
                assert!(!gpu.arena_layout[p].initial[0].is_empty());
                assert!(!gpu.arena_layout[p].initial[1].is_empty());
                assert!(gpu.arena_layout[p].inactive.iter().any(|b| b.initial[1] == usize::MAX));
            }
        }
        let shape = geometry(&gpu);
        let mut files = Vec::new();
        retain(dir,"input.host.bin",&host_image(&input),&mut files)?;
        for _ in 0..4 { gpu.iterate()?; }
        let before = device_image(&gpu)?;
        retain(dir,"trained.gpu.bin",&before,&mut files)?;
        let zero_blocks: [[usize;2];2] = std::array::from_fn(|p|
            std::array::from_fn(|which| gpu.arena_layout[p].inactive.iter()
                .filter(|b|b.initial[which]==usize::MAX).count()));
        let explicit_blocks: [[usize;2];2] = std::array::from_fn(|p|
            std::array::from_fn(|which| gpu.arena_layout[p].inactive.iter()
                .filter(|b|b.initial[which]!=usize::MAX).count()));
        let full_calls = if storage==Storage::Compressed {zero_blocks.iter().flatten().sum()} else {0};
        let strategy_calls = if storage==Storage::Compressed {zero_blocks[0][1]+zero_blocks[1][1]} else {0};
        if storage==Storage::Compressed && iso {
            assert!(zero_blocks.iter().flatten().all(|n|*n>0));
            assert!(explicit_blocks.iter().flatten().all(|n|*n>0));
        }
        let sync_full = |g:&mut GpuSolver,s:&mut Solver| -> R<()> {
            let n=E041_ZERO_RESTORES.load(Ordering::SeqCst);
            g.sync_to_cpu(s)?;
            assert_eq!(E041_ZERO_RESTORES.load(Ordering::SeqCst)-n,full_calls);
            Ok(())
        };
        let mut reference = target(&spot,storage,iso);
        let mut candidate = target(&spot,storage,iso);
        let poisoned = host_image(&candidate);
        retain(dir,"poisoned.host.bin",&poisoned,&mut files)?;
        assert_eq!(poisoned,host_image(&reference));
        let count_before=E041_ZERO_RESTORES.load(Ordering::SeqCst);
        legacy_sync(&mut gpu,&mut reference)?;
        assert_eq!(E041_ZERO_RESTORES.load(Ordering::SeqCst),count_before);
        sync_full(&mut gpu,&mut candidate)?;
        let first=host_image(&reference);
        pair(dir,"first.host",first.clone(),host_image(&candidate),&mut files)?;
        pair(dir,"first.query",query_image(&reference),query_image(&candidate),&mut files)?;
        saves(dir,"first",&reference,&candidate,&mut files)?;
        assert_eq!(host_image(&reference),first);assert_eq!(host_image(&candidate),first);
        reference.ensure_symmetric();candidate.ensure_symmetric();
        let materialized=host_image(&reference);
        pair(dir,"materialized.host",materialized.clone(),host_image(&candidate),&mut files)?;
        if iso {assert_ne!(materialized,first);}
        pair(dir,"materialized.query",query_image(&reference),query_image(&candidate),&mut files)?;
        saves(dir,"materialized",&reference,&candidate,&mut files)?;
        legacy_sync(&mut gpu,&mut reference)?;sync_full(&mut gpu,&mut candidate)?;
        pair(dir,"repeat.host",host_image(&reference),host_image(&candidate),&mut files)?;
        assert_eq!(host_image(&candidate),first);
        // Strategy-only readback uses the same inactive writer and must preserve regrets.
        let mut sr=target(&spot,storage,iso);let mut sc=target(&spot,storage,iso);
        let raw_regrets = |s:&Solver| -> Vec<u32> {
            let mut out=Vec::new();
            for store in &s.regrets {
                match store {
                    Store::F32(b) => out.extend(b.as_slice().iter().map(|v|v.to_bits())),
                    Store::I16 {q,scale} => {
                        out.extend(q.as_slice().iter().map(|v|*v as u16 as u32));
                        out.extend(scale.as_slice().iter().map(|v|v.to_bits()));
                    }
                    Store::U16 {q,scale} => {
                        out.extend(q.as_slice().iter().map(|v|*v as u32));
                        out.extend(scale.as_slice().iter().map(|v|v.to_bits()));
                    }
                }
            }
            out
        };
        let regret_before=raw_regrets(&sc);
        let n=E041_ZERO_RESTORES.load(Ordering::SeqCst);
        legacy_strategy(&mut gpu,&mut sr)?;
        assert_eq!(E041_ZERO_RESTORES.load(Ordering::SeqCst),n);
        gpu.sync_strategy(&mut sc)?;
        assert_eq!(E041_ZERO_RESTORES.load(Ordering::SeqCst)-n,strategy_calls);
        assert_eq!(regret_before,raw_regrets(&sc));
        pair(dir,"strategy.host",host_image(&sr),host_image(&sc),&mut files)?;
        pair(dir,"strategy.query",query_image(&sr),query_image(&sc),&mut files)?;
        saves(dir,"strategy",&sr,&sc,&mut files)?;
        sr.ensure_symmetric();sc.ensure_symmetric();
        pair(dir,"strategy_materialized.host",host_image(&sr),host_image(&sc),&mut files)?;
        pair(dir,"strategy_materialized.query",query_image(&sr),query_image(&sc),&mut files)?;
        saves(dir,"strategy_materialized",&sr,&sc,&mut files)?;
        legacy_sync(&mut gpu,&mut sr)?;sync_full(&mut gpu,&mut sc)?;
        pair(dir,"after_strategy_full.host",host_image(&sr),host_image(&sc),&mut files)?;
        assert_eq!(host_image(&sc),first);
        let after=device_image(&gpu)?;
        retain(dir,"final.gpu.bin",&after,&mut files)?;assert_eq!(before,after);
        // Continue the same live GPU learner; readback must also match the fresh later state.
        for _ in 0..2 {gpu.iterate()?;}
        let continued=device_image(&gpu)?;
        retain(dir,"continued_trained.gpu.bin",&continued,&mut files)?;
        assert_ne!(continued,before);
        legacy_sync(&mut gpu,&mut reference)?;sync_full(&mut gpu,&mut candidate)?;
        assert_eq!(candidate.iteration,6);
        pair(dir,"continued.host",host_image(&reference),host_image(&candidate),&mut files)?;
        pair(dir,"continued.query",query_image(&reference),query_image(&candidate),&mut files)?;
        saves(dir,"continued",&reference,&candidate,&mut files)?;
        let continued_after=device_image(&gpu)?;
        retain(dir,"continued_after.gpu.bin",&continued_after,&mut files)?;
        assert_eq!(continued,continued_after);assert_eq!(geometry(&gpu),shape);
        gpu.synchronize()?;drop(gpu);owner.check_err().map_err(e)?;
        let bytes:u64=files.iter().map(|v|v["bytes"].as_u64().unwrap()).sum();
        assert!(bytes<=32*1024*1024);
        Ok(json!({"storage":format!("{storage:?}"),"compact":iso,"nodes":spot.tree.nodes.len(),
            "host_elements":spot.tree.data_size,"device_elements":shape.2,"staging_words":shape.1,
            "zero_blocks":zero_blocks,"explicit_blocks":explicit_blocks,
            "observed_zero_calls_per_full_sync":full_calls,"observed_zero_calls_per_strategy_sync":strategy_calls,
            "training_iterations":[4,6],"full_raw_equality":true,"query_save_exact":true,
            "materialization_changed_host":materialized!=first,"repeat_restores_first":true,
            "strategy_only_preserves_regrets":true,"gpu_learning_unchanged_by_readbacks":true,
            "staging_identity_and_device_lengths_unchanged":true,"cleanup_complete":true,
            "files":files,"output_bytes":bytes}))
    }

    #[test]
    #[ignore = "root-only E041 accepted-writer GPU control; CUDA and fresh E041_CONTROL_DIR required"]
    fn exact_zero_restore_gpu_lifecycle() -> R<()> {
        let dir=PathBuf::from(std::env::var_os("E041_CONTROL_DIR").ok_or("E041_CONTROL_DIR missing")?);
        std::fs::create_dir(&dir).map_err(e)?;let mut cases=Vec::new();
        for (name,storage,iso) in [("compressed-full",Storage::Compressed,false),
            ("compressed-compact",Storage::Compressed,true),("f32-full",Storage::F32,false),
            ("f32-compact",Storage::F32,true)] {
            let path=dir.join(name);std::fs::create_dir(&path).map_err(e)?;
            let result=run_case(&path,storage,iso)?;
            println!("E041_ZERO_CONTROL {}",json!({"stage":"case_complete","name":name,"result":result}));
            cases.push(result);
        }
        let summary=json!({"id":"E041-control","stage":"complete","cases":cases,
            "performance_measured":false,"candidate_accepted":false});
        retain(&dir,"evidence.json",&serde_json::to_vec_pretty(&summary).map_err(e)?,&mut Vec::new())?;
        println!("E041_ZERO_CONTROL {summary}");Ok(())
    }
}
