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
