
#[cfg(test)]
mod e044_discount_control {
    use super::*;
    use crate::{Spot,SpotConfig,StreetSizing,TreeConfig,parse_sizes,LockMode};
    use crate::store::Storage;
    use crate::tree::KIND_ACTION;
    use serde_json::{json,Value};
    use std::io::{BufWriter,Write};
    use std::path::{Path,PathBuf};
    use std::sync::atomic::Ordering;
    type R<T> = Result<T,String>;
    impl GpuSolver {
    fn e044_original_iterate(&mut self) -> Result<(), String> {
        self.iteration += 1;
        let disc = Discounts::for_iteration(self.algo, self.iteration);
        self.stream
            .memcpy_htod(&[disc.pos, disc.neg, disc.strat], &mut self.d_disc)
            .map_err(e)?;
        let _ = &disc;
        if self.graphs.is_none() && self.iteration > 1 {
            // First iteration ran eagerly (JIT warm); capture the two sweeps
            // into CUDA graphs. Kernels read discounts from d_disc, so the
            // captured graphs stay valid for every later iteration.
            let mut captured = Vec::with_capacity(2);
            for p in 0..2 {
                self.stream
                    .begin_capture(
                        sys::CUstreamCaptureMode::CU_STREAM_CAPTURE_MODE_THREAD_LOCAL,
                    )
                    .map_err(e)?;
                let res = self.paired_sweep(p, None, p == 1);
                let graph = self
                    .stream
                    .end_capture(
                        sys::CUgraphInstantiate_flags::CUDA_GRAPH_INSTANTIATE_FLAG_AUTO_FREE_ON_LAUNCH,
                    )
                    .map_err(e)?;
                res?; // surface sweep errors only after capture mode is exited
                captured.push(graph.ok_or_else(|| "graph capture failed".to_string())?);
            }
            let g1 = captured.pop().unwrap();
            let g0 = captured.pop().unwrap();
            self.graphs = Some([g0, g1]);
        }
        if let Some(graphs) = &self.graphs {
            for g in graphs {
                g.launch().map_err(e)?;
            }
        } else {
            for p in 0..2 {
                self.paired_sweep(p, None, p == 1)?;
            }
        }
        Ok(())
    }
    fn e044_original_profiled(&mut self) -> Result<Profile, String> {
        self.iteration += 1;
        let disc = Discounts::for_iteration(self.algo, self.iteration);
        self.stream
            .memcpy_htod(&[disc.pos, disc.neg, disc.strat], &mut self.d_disc)
            .map_err(e)?;
        let mut prof = Profile::default();
        for p in 0..2 {
            self.paired_sweep(p, Some(&mut prof), p == 1)?;
        }
        Ok(prof)
    }
    }
    #[allow(dead_code)]
struct OriginalGpuSolverSize {
    _ctx: Arc<CudaContext>,
    stream: Arc<CudaStream>,
    _module: Arc<CudaModule>,
    f_copy_root: CudaFunction,
    f_down_action: CudaFunction,
    f_down_chance: CudaFunction,
    f_up_fold: CudaFunction,
    f_up_show: CudaFunction,
    f_up_chance: CudaFunction,
    f_up_action: CudaFunction,
    f_up_action_eval: CudaFunction,

    // plan metadata kept host-side
    num_levels: usize,
    nh: [i32; 2],
    nh_max: i32,
    action_spans: Vec<LevelSpan>,
    chance_spans: Vec<LevelSpan>,
    chance_node_spans: Vec<LevelSpan>,
    fold_spans: Vec<LevelSpan>,
    show_spans: Vec<LevelSpan>,
    riv_max_cnt: [usize; 2],

    // device: work lists
    d_action_nodes: CudaSlice<u32>,
    d_chance_parents: CudaSlice<u32>,
    d_chance_children: CudaSlice<u32>,
    d_chance_cards: CudaSlice<u32>,
    d_chance_nodes: CudaSlice<u32>,
    d_fold_nodes: CudaSlice<u32>,
    d_show_nodes: CudaSlice<u32>,
    // device: per-node
    d_node_player: CudaSlice<i32>,
    d_node_na: CudaSlice<i32>,
    d_node_data_off: CudaSlice<u64>,
    d_node_children_start: CudaSlice<u32>,
    d_node_twin: CudaSlice<f32>,
    d_node_tlose: CudaSlice<f32>,
    d_node_ttie: CudaSlice<f32>,
    d_node_cdiv: CudaSlice<f32>,
    d_node_river_slot: CudaSlice<i32>,
    d_cc_start: CudaSlice<u32>,
    d_cc_count: CudaSlice<u32>,
    d_cc_card: CudaSlice<u32>,
    d_cc_child: CudaSlice<u32>,
    d_cc_perm: CudaSlice<u32>,
    d_hand_perm: [CudaSlice<u32>; 2],
    /// Orbit folding active: syncs must mark the CPU solver sym-dirty.
    iso_active: bool,
    d_rsrc: [CudaSlice<u32>; 2],
    d_children: CudaSlice<u32>,
    // device: hands
    d_fold_card_off: [CudaSlice<u32>; 2],
    d_fold_card_idx: [CudaSlice<u32>; 2],
    d_hand_c1: [CudaSlice<u32>; 2],
    d_hand_c2: [CudaSlice<u32>; 2],
    d_hand_mask: [CudaSlice<u64>; 2],
    d_same: [CudaSlice<u32>; 2],
    d_weights: [CudaSlice<f32>; 2],
    // device: river tables
    d_riv_off: [CudaSlice<u32>; 2],
    d_riv_cnt: [CudaSlice<u32>; 2],
    d_riv_idx: [CudaSlice<u32>; 2],
    d_riv_lower: [CudaSlice<u32>; 2],
    d_riv_upper: [CudaSlice<u32>; 2],
    d_riv_card_off: [CudaSlice<u32>; 2],
    d_riv_card_pos: [CudaSlice<u32>; 2],
    // device: locks (rebuilt via update_locks)
    d_lock_off: CudaSlice<i64>,
    d_lock_sigma: CudaSlice<f32>,
    // device: solver state + staging
    d_regrets: [CudaSlice<f32>; 2],
    d_strat: [CudaSlice<f32>; 2],
    d_reach: [CudaSlice<f32>; 2],
    d_cfv_slot: CudaSlice<u32>,
    d_cfv: CudaSlice<f32>,
    d_eval_roots: CudaSlice<f32>,
    eval_graphs: [Option<CudaGraph>; 2],
    eval_warmed: [bool; 2],
    d_disc: CudaSlice<f32>,
    /// Captured iteration sweeps (one per traverser); rebuilt if locks change.
    graphs: Option<[CudaGraph; 2]>,
    /// Cached+page-locked host staging for fast arena transfers.
    h_staging: PinnedBuf,
    arena_layout: [ArenaLayout; 2],

    pub iteration: u32,
    pub algo: Algorithm,
}
    fn u32_word(out: &mut Vec<u8>, v: u32) { out.extend(v.to_le_bytes()); }
    fn u64_word(out: &mut Vec<u8>, v: u64) { out.extend(v.to_le_bytes()); }
    fn host_image(s: &Solver) -> Vec<u8> {
        let mut out = b"E044HOST1".to_vec();
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
        let mut out = b"E044QUERY1".to_vec();
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
        let _ = nonuniform; // Tiny all-check fallback has one legal action.
        out
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
    fn spot(tiny:bool,iso:bool)->R<Arc<Spot>> {
        let size=StreetSizing {bet:if tiny {vec![]}else{parse_sizes("50")?},raise:vec![],donk:vec![]};
        Ok(Arc::new(Spot::new_with_limit(SpotConfig {
            board:if tiny {"Th9h2c3d4s"}else{"KsQs2dJd"}.into(),
            range_oop:if tiny {"AcAd"}else{"AA,KK,QQ,JJ,AKs,AQs,AKo"}.into(),
            range_ip:if tiny {"KcKd"}else{"AA,QQ,TT,77,AQs,KQs,AQo"}.into(),
            tree:TreeConfig {starting_pot:10.0,effective_stack:20.0,
                rake_pct:if iso {0.05}else{0.0},rake_cap:1.0,
                oop:[size.clone(),size.clone(),size.clone()],ip:[size.clone(),size.clone(),size],..Default::default()},
        },Some(20_000))?))
    }
    fn cpu_target(input:&Solver)->Solver {
        let mut s=target(&input.spot,input.storage,input.use_isomorphism);s.algo=input.algo;
        s.locks=input.locks.clone();s.lock_labels=input.lock_labels.clone();s
    }
    fn gpu_image(g:&GpuSolver)->R<Vec<u8>> {
        g.synchronize()?;let mut out=b"E044GPU1".to_vec();u64_word(&mut out,g.iteration as u64);
        for n in [g.nh[0],g.nh[1],g.nh_max] {u32_word(&mut out,n as u32);}
        for d in [&g.d_regrets[0],&g.d_regrets[1],&g.d_strat[0],&g.d_strat[1],
            &g.d_reach[0],&g.d_reach[1],&g.d_cfv,&g.d_eval_roots,&g.d_disc] {
            let v=g.stream.clone_dtoh(d).map_err(e)?;g.synchronize()?;
            u64_word(&mut out,v.len() as u64);for x in v {u32_word(&mut out,x.to_bits());}
        }
        Ok(out)
    }
    fn run_case(dir:&Path,storage:Storage,iso:bool,tight:bool,tiny:bool,algo:Algorithm)->R<Value> {
        let sp=spot(tiny,iso)?;assert!(sp.tree.data_size.iter().sum::<u64>()<=250_000);
        let mut input=Solver::with_storage(sp.clone(),storage);input.use_isomorphism=iso;input.algo=algo;seed(&mut input,1);
        let plan=GpuPlan::build(&sp,iso);
        let budget=if tight {plan.staging_bytes()+(plan.arena_elements[0]+plan.arena_elements[1]) as u64*8+512*1024*1024}else{u64::MAX};
        let mut reference=GpuSolver::new_with_budget(&input,budget)?;let mut candidate=GpuSolver::new_with_budget(&input,budget)?;
        let bg=geometry(&reference);let cg=geometry(&candidate);assert_eq!(bg.1,cg.1);assert_eq!(bg.2,cg.2);
        let eligible=cg.1>=6;assert_eq!(eligible,!tiny);
        let compact=cg.2[0]<(sp.tree.data_size[0] as usize);assert_eq!(compact,iso&&(storage==Storage::Compressed||tight));
        let mut files=Vec::new();retain(dir,"input.host.bin",&host_image(&input),&mut files)?;
        pair(dir,"initial.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        let mut total=0;
        for (k,batch) in [1usize,2,3,5,8].into_iter().enumerate() {
            for _ in 0..batch {reference.e044_original_iterate()?;}
            for _ in 0..batch {candidate.iterate()?;}
            total+=batch;assert_eq!(reference.discount_stage.used,0);
            assert_eq!(candidate.discount_stage.used,if eligible {(total-1)%2+1}else{0});
            pair(dir,&format!("batch{k}.gpu"),gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        }
        assert_eq!(total,19);
        let bp=reference.e044_original_profiled()?;let cp=candidate.iterate_profiled()?;assert_eq!(bp.launches,cp.launches);
        pair(dir,"profiled.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        let mut bh=cpu_target(&input);let mut ch=cpu_target(&input);
        reference.sync_to_cpu(&mut bh)?;candidate.sync_to_cpu(&mut ch)?;assert_eq!(candidate.discount_stage.used,0);
        assert_eq!(bh.algo,ch.algo);assert_eq!(ch.algo,algo);
        pair(dir,"first.host",host_image(&bh),host_image(&ch),&mut files)?;
        pair(dir,"first.query",query_image(&bh),query_image(&ch),&mut files)?;saves(dir,"first",&bh,&ch,&mut files)?;
        bh.ensure_symmetric();ch.ensure_symmetric();
        pair(dir,"materialized.host",host_image(&bh),host_image(&ch),&mut files)?;
        pair(dir,"materialized.query",query_image(&bh),query_image(&ch),&mut files)?;
        let be=reference.exploitability(&bh)?;let ce=candidate.exploitability(&ch)?;assert_eq!(be.to_bits(),ce.to_bits());
        pair(dir,"evaluation.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        // Queue one iteration before lock-table replacement drains and invalidates graphs.
        reference.e044_original_iterate()?;candidate.iterate()?;
        bh.lock_node(&[],LockMode::Freeze,"pipeline-control".into())?;ch.lock_node(&[],LockMode::Freeze,"pipeline-control".into())?;
        reference.update_locks(&bh)?;candidate.update_locks(&ch)?;
        reference.e044_original_iterate()?;candidate.iterate()?;
        pair(dir,"locked.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        reference.sync_strategy(&mut bh)?;candidate.sync_strategy(&mut ch)?;assert_eq!(candidate.discount_stage.used,0);
        pair(dir,"strategy.host",host_image(&bh),host_image(&ch),&mut files)?;
        reference.sync_to_cpu(&mut bh)?;candidate.sync_to_cpu(&mut ch)?;
        pair(dir,"locked_full.host",host_image(&bh),host_image(&ch),&mut files)?;
        pair(dir,"locked_full.query",query_image(&bh),query_image(&ch),&mut files)?;saves(dir,"locked_full",&bh,&ch,&mut files)?;
        assert!(bh.unlock_node(&[])?&&ch.unlock_node(&[])?);reference.update_locks(&bh)?;candidate.update_locks(&ch)?;
        for _ in 0..2 {reference.e044_original_iterate()?;candidate.iterate()?;}
        pair(dir,"continued.gpu",gpu_image(&reference)?,gpu_image(&candidate)?,&mut files)?;
        reference.sync_to_cpu(&mut bh)?;candidate.sync_to_cpu(&mut ch)?;
        assert_eq!(ch.iteration,24);assert_eq!(candidate.discount_stage.used,0);
        pair(dir,"continued.host",host_image(&bh),host_image(&ch),&mut files)?;
        pair(dir,"continued.query",query_image(&bh),query_image(&ch),&mut files)?;saves(dir,"continued",&bh,&ch,&mut files)?;
        assert_eq!(geometry(&reference),bg);assert_eq!(geometry(&candidate),cg);
        let bo=reference._ctx.clone();let co=candidate._ctx.clone();drop(reference);drop(candidate);bo.check_err().map_err(e)?;co.check_err().map_err(e)?;
        let bytes:u64=files.iter().map(|f|f["bytes"].as_u64().unwrap()).sum();assert!(bytes<=64*1024*1024);
        Ok(json!({"storage":format!("{storage:?}"),"algorithm":format!("{algo:?}"),"iso":iso,"compact":compact,"tiny":tiny,"tight":tight,
            "pinned_pipeline_eligible":eligible,"staging_words":cg.1,"arena_words":cg.2,"iterations":24,"profiled_iteration":20,
            "unsynchronized_batch_lengths":[1,2,3,5,8],"gpu_raw_exact":true,"cpu_query_save_exact":true,"ev_bits":ce.to_bits(),
            "locks_resume_exact":true,"full_and_strategy_readback_reset_slots":true,"staging_geometry_unchanged":true,
            "cleanup_complete":true,"files":files,"output_bytes":bytes}))
    }
    fn drop_controls()->R<Vec<Value>> {
        let sp=spot(false,false)?;let mut input=Solver::with_storage(sp,Storage::Compressed);input.use_isomorphism=false;seed(&mut input,1);
        let mut outcomes=Vec::new();
        for mode in 0..3 {
            let gpu=GpuSolver::new(&input)?;assert!(gpu.h_staging.len>=6);
            let stream=gpu.stream.clone();let owner=gpu._ctx.clone();
            let before=DISCOUNT_STAGE_DRAINS.load(Ordering::SeqCst);DISCOUNT_STAGE_LAST_QUERY.store(-7,Ordering::SeqCst);
            let result=std::panic::catch_unwind(std::panic::AssertUnwindSafe(move ||->R<()> {
                let mut g=gpu;
                if mode==1 {
                    DISCOUNT_STAGE_FAIL_NEXT.store(true,Ordering::SeqCst);
                    assert_eq!(g.iterate().unwrap_err(),"injected discount upload error");
                } else {
                    g.iterate()?;g.iterate()?;
                    if mode==2 {panic!("injected discount staging unwind");}
                }
                Ok(())
            }));
            if mode==2 {assert!(result.is_err());}else{result.unwrap()?;}
            assert_eq!(DISCOUNT_STAGE_DRAINS.load(Ordering::SeqCst)-before,1);
            assert_eq!(DISCOUNT_STAGE_LAST_QUERY.load(Ordering::SeqCst),0);
            // The stored query was inside the first-field guard, before CUDA/pinned fields released.
            stream.synchronize().map_err(e)?;owner.check_err().map_err(e)?;
            outcomes.push(json!({"mode":mode,"drain_calls":1,"stream_ready_before_field_release":true,"cleanup_complete":true}));
        }
        Ok(outcomes)
    }
    #[test]
    #[ignore = "root-only E044 pinned discount lifecycle; CUDA and fresh E044_CONTROL_DIR required"]
    fn exact_two_slot_discount_lifecycle()->R<()> {
        let dir=PathBuf::from(std::env::var_os("E044_CONTROL_DIR").ok_or("E044_CONTROL_DIR missing")?);std::fs::create_dir(&dir).map_err(e)?;
        assert!(std::mem::size_of::<GpuSolver>()<=std::mem::size_of::<OriginalGpuSolverSize>()+32);
        let mut cases=Vec::new();
        for (an,algo) in [("dcfr",Algorithm::Dcfr),("cfr-plus",Algorithm::CfrPlus)] {
            for (label,storage,iso,tight,tiny) in [("compressed-full",Storage::Compressed,false,false,false),
                ("compressed-compact",Storage::Compressed,true,false,false),("f32-full",Storage::F32,false,false,false),
                ("f32-iso-full",Storage::F32,true,false,false),("f32-compact",Storage::F32,true,true,false),
                ("tiny-compressed",Storage::Compressed,false,false,true),("tiny-f32",Storage::F32,false,false,true)] {
                let name=format!("{an}-{label}");let path=dir.join(&name);std::fs::create_dir(&path).map_err(e)?;
                let result=run_case(&path,storage,iso,tight,tiny,algo)?;
                println!("E044_DISCOUNT_CONTROL {}",json!({"stage":"case_complete","name":name,"result":result}));cases.push(json!({"name":name,"result":result}));
            }
        }
        let drops=drop_controls()?;
        let summary=json!({"id":"E044-control","stage":"complete","cases":cases,"drop_controls":drops,
            "original_solver_size":std::mem::size_of::<OriginalGpuSolverSize>(),"candidate_solver_size":std::mem::size_of::<GpuSolver>(),
            "discount_stage_size":std::mem::size_of::<DiscountStage>(),"performance_measured":false,"candidate_accepted":false});
        retain(&dir,"evidence.json",&serde_json::to_vec_pretty(&summary).map_err(e)?,&mut Vec::new())?;
        println!("E044_DISCOUNT_CONTROL {summary}");Ok(())
    }
}
