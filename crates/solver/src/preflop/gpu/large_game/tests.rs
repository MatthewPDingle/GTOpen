//! Large-game mode. The plan tests need no card: they run the mode's own
//! order of work (`run_sweep`, `run_evaluation`) on a model of what every
//! kernel reads and writes, and check that each read finds exactly what the
//! normal plan would have there. The CUDA tests then hold the mode to the
//! normal plan's bits on the card.
use super::*;
use crate::preflop::equity::EquityTable;
use crate::preflop::leafnet::constant_net;
use crate::preflop::PreflopConfig;
use std::collections::HashSet;

fn table() -> Arc<EquityTable> {
    static T: std::sync::OnceLock<Arc<EquityTable>> = std::sync::OnceLock::new();
    T.get_or_init(|| Arc::new(EquityTable::build(300))).clone()
}

fn game(n: usize, realization: &str, opens: &[f64], max_raises: u8, blockers: bool) -> PreflopSolver {
    let mut posts = vec![0.0; n];
    posts[n - 2] = 0.5;
    posts[n - 1] = 1.0;
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": (0..n).map(|p| format!("P{p}")).collect::<Vec<_>>(), "stack": 30.0,
        "posts": posts, "limp": true, "open_raises": opens, "raise_mults": [3.0], "max_raises": max_raises,
        "add_allin": true, "rake_pct": 5.0, "rake_cap": 2.0, "realization": realization,
        "card_removal": blockers,
    })).unwrap();
    let mut s = PreflopSolver::new(cfg, table()).unwrap();
    if realization == "leafnet" {
        let pattern: Vec<f32> = (0..2 * NUM_CLASSES).map(|k| 0.04 * (((k * 7) % 11) as f32 - 5.0) / 5.0).collect();
        s.install_leaf_net(Arc::new(constant_net(&pattern))).unwrap();
        s.set_leaf_schedule(u32::MAX, Some(0.3));
    }
    s
}

const NONE: (u32, u32) = (u32::MAX, u32::MAX);
const TERMINAL: i32 = 9;

/// What each buffer holds: for a reach block the normal plan's block it
/// stands for, for a value slot the node whose value it is; each with a
/// stamp of when it was written.
struct Model<'a> {
    s: &'a PreflopSolver,
    plan: &'a Plan,
    lists: &'a Lists,
    normal_src: Vec<u32>,
    reach: Vec<(u32, u32)>,
    mass: Vec<(u32, u32)>,
    val: Vec<(u32, u32)>,
    stash: Vec<Vec<(u32, u32)>>,
    roots_out: Vec<(u32, u32)>,
    epoch: u32,
    /// (first root slot of the part, which) of the last equity-cache fill.
    eq_filled: Option<(u32, usize)>,
    downs: Vec<u32>,
    ups: Vec<u32>,
    priced: Vec<u32>,
}

impl<'a> Model<'a> {
    fn new(s: &'a PreflopSolver, plan: &'a Plan, lists: &'a Lists) -> Self {
        let n = s.nodes.len();
        Self {
            s, plan, lists, normal_src: reach_sources(s),
            reach: vec![NONE; plan.reach_blocks], mass: vec![NONE; plan.reach_blocks],
            val: vec![NONE; plan.value_blocks],
            stash: vec![vec![NONE; plan.frontier.1 as usize]; 2 * s.n],
            roots_out: vec![NONE; 2 * s.n],
            epoch: 0, eq_filled: None,
            downs: vec![0; n], ups: vec![0; n], priced: vec![0; n],
        }
    }
    fn stamp(&self, p: i32, mode: i32) -> u32 {
        self.epoch * 1000 + p as u32 * 10 + mode as u32
    }
    fn lean(&self, node: usize, q: usize) -> usize {
        self.plan.reach_src[node * self.s.n + q] as usize
    }
    fn reach_ok(&self, node: usize, q: usize, what: &str) -> Result<(), String> {
        let want = (self.normal_src[node * self.s.n + q], self.epoch);
        let block = self.lean(node, q);
        if self.reach[block] != want {
            return Err(format!("{what}: node {node} seat {q} reads block {block} holding {:?}, wants {want:?}", self.reach[block]));
        }
        Ok(())
    }
    fn clear_counts(&mut self) {
        self.downs.fill(0);
        self.ups.fill(0);
        self.priced.fill(0);
    }
}

impl<'a> Steps for Model<'a> {
    fn init_root(&mut self) -> Result<(), String> {
        self.epoch += 1;
        for q in 0..self.s.n { self.reach[q] = (q as u32, self.epoch); }
        Ok(())
    }

    fn down(&mut self, start: u32, count: u32, _mode: i32) -> Result<(), String> {
        let nodes = &self.plan.act_nodes[start as usize..(start + count) as usize];
        let mut written = HashSet::new();
        let mut read = HashSet::new();
        for &nd in nodes {
            let nd = nd as usize;
            let node = &self.s.nodes[nd];
            if node.kind != KIND_ACTION { return Err(format!("down: node {nd} is not a decision")); }
            let act = node.actor as usize;
            self.reach_ok(nd, act, "down")?;
            read.insert(self.lean(nd, act));
            self.downs[nd] += 1;
        }
        for &nd in nodes {
            let nd = nd as usize;
            let act = self.s.nodes[nd].actor as usize;
            for a in 0..self.s.nodes[nd].actions.len() {
                let c = self.s.child(nd, a);
                let block = self.lean(c, act);
                if !written.insert(block) { return Err(format!("down: block {block} written twice in one launch")); }
                self.reach[block] = (self.normal_src[c * self.s.n + act], self.epoch);
            }
        }
        if let Some(block) = read.intersection(&written).next() {
            return Err(format!("down: block {block} read and written in one launch"));
        }
        Ok(())
    }

    fn mass(&mut self, first: usize, count: usize) -> Result<(), String> {
        for block in first..first + count {
            if self.reach[block].1 != self.epoch {
                return Err(format!("mass: block {block} was not written this pass"));
            }
            self.mass[block] = self.reach[block];
        }
        Ok(())
    }

    fn eq_cache(&mut self, chunk: &Chunk, which: usize) -> Result<(), String> {
        let t = &chunk.eq;
        let (start, count) = t.spans[which];
        for k in start..start + count {
            let slot = self.plan.eq_work[t.work_at + k as usize] as usize;
            let block = self.plan.eq_blocks[t.blocks_at + slot] as usize;
            if self.mass[block].1 != self.epoch || self.mass[block] != self.reach[block] {
                return Err(format!("equity cache: block {block} has no fresh total"));
            }
        }
        self.eq_filled = Some((chunk.frontier.0, which));
        Ok(())
    }

    fn terminals(&mut self, chunk: &Chunk, p: i32, _gate: i32) -> Result<(), String> {
        let (s, plan, np) = (self.s, self.plan, self.s.n);
        let pu = p as usize;
        let (t0, tn) = chunk.terms;
        let slice = |list: &'a [u32], range: (u32, u32)| &list[range.0 as usize..(range.0 + range.1) as usize];
        let terms = slice(&self.lists.terms, (t0, tn));
        // the per-kind lists are exactly this part's terminals of that kind
        let kind_ok = |list: &[u32], keep: &dyn Fn(usize) -> bool| -> bool {
            list.iter().copied().eq(terms.iter().copied().filter(|&i| keep(i as usize)))
        };
        if !kind_ok(slice(&self.lists.mw, chunk.mw_terms), &|i| coupled_terminal(s, &s.nodes[i])) {
            return Err("multiway list is not this part's".into());
        }
        if !kind_ok(slice(&self.lists.hu, chunk.hu), &|i| s.nodes[i].kind == KIND_POT_SHARE && s.nodes[i].live.count_ones() == 2) {
            return Err("heads-up list is not this part's".into());
        }
        let leaves: HashSet<u32> = self.lists.leaf.iter().copied().collect();
        if !kind_ok(slice(&self.lists.leaf, chunk.leaf), &|i| leaves.contains(&(i as u32))) {
            return Err("learned list is not this part's".into());
        }
        if chunk.mw.union > plan.mw_union_max || chunk.mw.capacity > plan.mw_capacity_max
            || chunk.mw_terms.1 as usize > plan.mw_terms_max || chunk.eq.union > plan.eq_union_max {
            return Err("a part's scratch is larger than the plan's".into());
        }
        for &nd in terms {
            let nd = nd as usize;
            let node = &s.nodes[nd];
            for q in 0..np {
                self.reach_ok(nd, q, "terminal")?;
                let block = self.lean(nd, q);
                if self.mass[block] != self.reach[block] {
                    return Err(format!("terminal {nd}: seat {q}'s total is stale"));
                }
            }
            if node.kind == KIND_POT_SHARE && (node.live >> pu) & 1 != 0 {
                let multiway = coupled_terminal(s, node);
                let (t, slots, blocks, work) = if multiway {
                    (&chunk.mw, &plan.mw_slots, &plan.mw_blocks, &plan.mw_work)
                } else {
                    (&chunk.eq, &plan.eq_slots, &plan.eq_blocks, &plan.eq_work)
                };
                if !multiway {
                    match self.eq_filled {
                        Some((part, which)) if part == chunk.frontier.0 && (which == pu || which == np) => {}
                        other => return Err(format!("terminal {nd}: equity cache filled for {other:?}")),
                    }
                }
                let (w0, wn) = t.spans[pu];
                let mine = &work[t.work_at + w0 as usize..t.work_at + (w0 + wn) as usize];
                for q in (0..np).filter(|&q| q != pu && (node.live >> q) & 1 != 0) {
                    let block = self.lean(nd, q);
                    if block >= t.nblocks { return Err(format!("terminal {nd}: block {block} beyond the part's slot table")); }
                    let slot = slots[t.slots_at + block];
                    if slot as usize >= t.union || blocks[t.blocks_at + slot as usize] as usize != block {
                        return Err(format!("terminal {nd}: block {block} has no slot"));
                    }
                    let Some(local) = mine.iter().position(|&x| x == slot) else {
                        return Err(format!("terminal {nd}: slot {slot} is not in seat {pu}'s work"));
                    };
                    if multiway && t.compact {
                        let mapped = plan.mw_compact[t.compact_at + pu * t.union + slot as usize] as usize;
                        if mapped != local || mapped >= t.capacity {
                            return Err(format!("terminal {nd}: compact slot {mapped}, wants {local}"));
                        }
                    }
                }
            }
            self.val[plan.val_slot[nd] as usize] = (nd as u32, self.stamp(p, TERMINAL));
            self.priced[nd] += 1;
        }
        Ok(())
    }

    fn up(&mut self, start: u32, count: u32, p: i32, mode: i32) -> Result<(), String> {
        let nodes = &self.plan.act_nodes[start as usize..(start + count) as usize];
        let mut read = HashSet::new();
        for &nd in nodes {
            let nd = nd as usize;
            let node = &self.s.nodes[nd];
            if node.actor as i32 == p { self.reach_ok(nd, p as usize, "up")?; }
            for a in 0..node.actions.len() {
                let c = self.s.child(nd, a);
                let slot = self.plan.val_slot[c] as usize;
                let want = (c as u32, self.stamp(p, if self.s.nodes[c].kind == KIND_ACTION { mode } else { TERMINAL }));
                if self.val[slot] != want {
                    return Err(format!("up: node {nd} reads child {c} in slot {slot} holding {:?}, wants {want:?}", self.val[slot]));
                }
                read.insert(slot);
            }
        }
        let mut written = HashSet::new();
        for &nd in nodes {
            let slot = self.plan.val_slot[nd as usize] as usize;
            if !written.insert(slot) { return Err(format!("up: slot {slot} written twice in one launch")); }
            self.val[slot] = (nd, self.stamp(p, mode));
            self.ups[nd as usize] += 1;
        }
        if let Some(slot) = read.intersection(&written).next() {
            return Err(format!("up: slot {slot} read and written in one launch"));
        }
        Ok(())
    }

    fn keep_roots(&mut self, plan: &Plan, chunk: &Chunk, seat_pass: usize) -> Result<(), String> {
        let (first, count) = (chunk.frontier.0 as usize, chunk.frontier.1 as usize);
        for i in first..first + count {
            self.stash[seat_pass][i - plan.frontier.0 as usize] = self.val[i];
        }
        Ok(())
    }

    fn restore_roots(&mut self, plan: &Plan, seat_pass: usize) -> Result<(), String> {
        let (first, count) = (plan.frontier.0 as usize, plan.frontier.1 as usize);
        self.val[first..first + count].copy_from_slice(&self.stash[seat_pass]);
        Ok(())
    }

    fn root_copy(&mut self, seat_pass: usize) -> Result<(), String> {
        self.roots_out[seat_pass] = self.val[0];
        Ok(())
    }
}

fn fixtures() -> Vec<(&'static str, PreflopSolver)> {
    vec![
        ("heads-up", game(2, "static", &[2.5], 3, false)),
        ("3 seats", game(3, "static", &[2.5], 3, true)),
        ("3 seats learned", game(3, "leafnet", &[2.5], 3, true)),
        ("4 seats two opens", game(4, "static", &[2.5, 4.0], 3, true)),
        ("6 seats", game(6, "static", &[2.5], 2, false)),
    ]
}

#[test]
fn every_read_finds_what_the_normal_plan_holds_there() {
    for (name, s) in fixtures() {
        let lists = Lists::build(&s).unwrap();
        let np = s.n;
        let actions = s.nodes.iter().filter(|nd| nd.kind == KIND_ACTION).count();
        for parts in LADDER {
            let plan = Plan::build(&s, &lists, parts).unwrap();
            let at = format!("{name}, {parts} parts ({} chunks)", plan.chunks.len());
            // every decision is in exactly one level span, every terminal in one part
            let mut seen = vec![0u32; s.nodes.len()];
            for &nd in &plan.act_nodes { seen[nd as usize] += 1; }
            assert!(s.nodes.iter().enumerate().all(|(i, nd)| seen[i] == (nd.kind == KIND_ACTION) as u32), "{at}: level spans");
            assert_eq!(plan.act_nodes.len(), actions, "{at}");
            let spans: usize = plan.top_spans.iter().chain(plan.chunks.iter().flat_map(|c| c.spans.iter())).map(|x| x.1 as usize).sum();
            assert_eq!(spans, actions, "{at}");
            let mut next = [0u32; 4];
            for c in &plan.chunks {
                for (k, range) in [c.terms, c.hu, c.leaf, c.mw_terms].into_iter().enumerate() {
                    assert_eq!(range.0, next[k], "{at}: terminal ranges follow on");
                    next[k] += range.1;
                }
                assert!(c.nodes as usize <= s.nodes.len().div_ceil(parts), "{at}: part too large");
            }
            assert_eq!(next.map(|x| x as usize), [lists.terms.len(), lists.hu.len(), lists.leaf.len(), lists.mw.len()], "{at}");
            assert!(plan.reach_blocks <= s.nodes.len() + np - 1 && plan.value_blocks <= s.nodes.len(), "{at}");

            let mut model = Model::new(&s, &plan, &lists);
            // two passes each, so a value left from the pass before cannot pass for fresh
            for round in 0..2 {
                for p in 0..np as i32 {
                    model.clear_counts();
                    run_sweep(&plan, &mut model, np, p, 0).unwrap_or_else(|err| panic!("{at}, seat {p}, round {round}: {err}"));
                    assert_eq!(model.val[0], (0, model.stamp(p, 0)), "{at}: root value");
                    for (i, nd) in s.nodes.iter().enumerate() {
                        let action = (nd.kind == KIND_ACTION) as u32;
                        assert_eq!((model.downs[i], model.ups[i], model.priced[i]), (action, action, 1 - action), "{at}: node {i}");
                    }
                }
                let best: Vec<i32> = (0..np).map(|p| if p % 2 == 0 { 2 } else { 3 }).collect();
                model.clear_counts();
                run_evaluation(&plan, &mut model, np, &best).unwrap_or_else(|err| panic!("{at}, evaluation, round {round}: {err}"));
                for p in 0..np {
                    assert_eq!(model.roots_out[2 * p], (0, model.stamp(p as i32, best[p])), "{at}: best-response root");
                    assert_eq!(model.roots_out[2 * p + 1], (0, model.stamp(p as i32, 1)), "{at}: average root");
                }
                for (i, nd) in s.nodes.iter().enumerate() {
                    let action = (nd.kind == KIND_ACTION) as u32;
                    assert_eq!((model.downs[i], model.ups[i], model.priced[i]),
                        (action, action * 2 * np as u32, (1 - action) * np as u32), "{at}: node {i} in evaluation");
                }
            }
        }
    }
}

#[test]
fn the_model_catches_a_wrong_block_or_slot() {
    let s = game(4, "static", &[2.5, 4.0], 3, true);
    let lists = Lists::build(&s).unwrap();
    let np = s.n;
    let good = Plan::build(&s, &lists, 4).unwrap();
    assert!(good.chunks.len() >= 3);
    // a value slot shared by two inner terminals of one part
    let mut plan = Plan::build(&s, &lists, 4).unwrap();
    let c = &plan.chunks[1];
    let inner: Vec<u32> = lists.terms[c.terms.0 as usize..(c.terms.0 + c.terms.1) as usize].iter().copied()
        .filter(|&i| plan.val_slot[i as usize] >= plan.frontier.0 + plan.frontier.1).collect();
    plan.val_slot[inner[1] as usize] = plan.val_slot[inner[0] as usize];
    let mut model = Model::new(&s, &plan, &lists);
    assert!(run_sweep(&plan, &mut model, np, 0, 0).is_err());
    // a part's root reach block moved into the shared range
    let mut plan = Plan::build(&s, &lists, 4).unwrap();
    let root = plan.act_nodes[plan.chunks[0].spans[0].0 as usize] as usize;
    let parent_actor = (0..np).find(|&q| plan.reach_src[root * np + q] as usize >= np && (plan.reach_src[root * np + q] as usize) < plan.chunk_base
        && good.reach_src[root * np + q] != good.reach_src[q]).unwrap();
    let moved = plan.reach_src[root * np + parent_actor];
    for x in plan.reach_src.iter_mut() { if *x == moved { *x = plan.chunk_base as u32; } }
    let mut model = Model::new(&s, &plan, &lists);
    let failed = (0..np as i32).any(|p| run_sweep(&plan, &mut model, np, p, 0).is_err());
    assert!(failed);
}

#[test]
fn the_cut_shrinks_what_the_card_holds_and_budgets_decide_the_rest() {
    let s = game(6, "static", &[2.5, 4.0], 3, true);
    let lists = Lists::build(&s).unwrap();
    let normal = minimum_need_mb(&s);
    let mut last = usize::MAX;
    for parts in [2usize, 8, 32] {
        let plan = Plan::build(&s, &lists, parts).unwrap();
        let fixed = plan.fixed_bytes(&s, &lists).unwrap();
        assert!(fixed < last, "{parts} parts: {fixed} vs {last}");
        last = fixed;
        // too little: no fit; enough for one sample: batch 1 and no cache; plenty: all of it
        let one = plan.mw_capacity_max * (NUM_CLASSES + 1) * 4;
        assert_eq!(plan.fit(&s, &lists, fixed + one - 1, None).unwrap(), None);
        let least = plan.fit(&s, &lists, fixed + one, None).unwrap().unwrap();
        assert_eq!((least.batch, least.eq_cache, least.need_bytes), (1, false, fixed + one));
        let full = plan.fit(&s, &lists, usize::MAX / 2, None).unwrap().unwrap();
        assert_eq!((full.batch, full.eq_cache), (32, true));
        assert!(full.launches < least.launches);
        // pinned for a like-for-like comparison with a normal plan
        let pinned = plan.fit(&s, &lists, usize::MAX / 2, Some((7, false))).unwrap().unwrap();
        assert_eq!((pinned.batch, pinned.eq_cache), (7, false));
        assert_eq!(plan.fit(&s, &lists, fixed, Some((32, true))).unwrap(), None);
    }
    let large = large_need_mb(&s);
    assert!(large.is_finite());
    println!("6 seats, {} nodes: normal plan {normal:.0} MB, large-game mode {large:.0} MB", s.nodes.len());
    assert_eq!(large, large_tree_need_mb(&s) + large_policy_need_mb(&s));
    // room to spare: the coarsest cut, with full batches and the cache
    let (plan, fit) = choose(&s, &lists, 100_000).unwrap();
    assert_eq!((plan.parts, fit.batch, fit.eq_cache), (2, 32, true));
    // room for the large-game mode only: a fine cut that still fits
    let (plan, fit) = choose(&s, &lists, large.ceil() as u64 + 1).unwrap();
    assert!(fit.need_bytes as f64 / 1e6 <= large.ceil() + 1.0 && plan.chunks.len() > 2);
    assert!(choose(&s, &lists, (large - 2.0).max(0.0) as u64).is_err());
}

#[test]
fn the_size_walk_estimate_is_close_and_never_under() {
    for (name, s) in fixtures() {
        let est = crate::preflop::estimate_tree(&s.cfg).unwrap();
        let (before, built) = (large_need_of(&s.cfg, &est), large_need_mb(&s));
        assert!(before >= built, "{name}: estimate {before} under the built game's {built}");
        assert!(before <= built * 1.05 + 25.0, "{name}: estimate {before} far over the built game's {built}");
    }
}

#[test]
fn games_outside_the_mode_are_declined() {
    let cfg: PreflopConfig = serde_json::from_value(serde_json::json!({
        "positions": ["A", "B", "C", "D"], "stack": 30.0, "stacks": [12.0, 30.0, 6.0, 20.0],
        "posts": [0.0, 0.0, 0.5, 1.0], "limp": true, "open_raises": [2.5], "raise_mults": [3.0], "max_raises": 3,
        "add_allin": true, "rake_pct": 5.0, "rake_cap": 2.0, "realization": "static",
    })).unwrap();
    let s = PreflopSolver::new(cfg, table()).unwrap();
    assert!(supported(&s).unwrap_err().contains("side pots"));
    assert!(large_need_mb(&s).is_infinite());
    assert!(supported(&game(3, "static", &[2.5], 3, true)).is_ok());
}

/// These need a CUDA card: `cargo test --release --features gpu -p solver --lib on_the_card -- --test-threads=1`.
mod on_the_card {
    use super::*;

    fn bits(g: &PreflopGpu) -> (Vec<u32>, Vec<u32>, Vec<u32>) {
        (g.stream.clone_dtoh(&g.d_regrets).unwrap().iter().map(|v| v.to_bits()).collect(),
         g.stream.clone_dtoh(&g.d_strat).unwrap().iter().map(|v| v.to_bits()).collect(),
         g.stream.clone_dtoh(&g.d_eval_roots).unwrap().iter().map(|v| v.to_bits()).collect())
    }

    fn close(a: &(Vec<f64>, Vec<f64>), b: &(Vec<f64>, Vec<f64>), tolerance: f64) -> bool {
        a.0.iter().chain(&a.1).zip(b.0.iter().chain(&b.1)).all(|(x, y)| (x - y).abs() < tolerance)
    }

    fn used_bytes(ctx: &Arc<CudaContext>) -> u64 {
        ctx.synchronize().unwrap();
        ctx.bind_to_thread().unwrap();
        let mut bytes = 0u64;
        unsafe {
            let pool = cudarc::driver::result::device::get_mem_pool(ctx.cu_device()).unwrap();
            cudarc::driver::result::mem_pool::get_attribute(
                pool, sys::CUmemPool_attribute::CU_MEMPOOL_ATTR_USED_MEM_CURRENT, (&mut bytes as *mut u64).cast()).unwrap();
        }
        bytes
    }

    /// A normal engine and large-game engines at several cuts, all from one
    /// start and with the normal engine's batch and cache choice, stepped
    /// together. Every table must agree bit for bit after every step:
    /// eager launches first, then the captured graphs, an evaluation each
    /// round, and for learned flop values a refresh and re-upload midway.
    fn step_for_step(name: &str, mut s: PreflopSolver, prepare: impl Fn(&mut PreflopSolver)) {
        for _ in 0..12 { s.iterate(); }
        prepare(&mut s);
        let learned = s.leaf_terminals().is_some();
        if learned { s.refresh_leaf_values().unwrap(); }
        let mut normal = PreflopGpu::new(&s, 4000).expect("test requires CUDA");
        assert!(normal.large_game().is_none());
        let pinned = normal.layout();
        let cuts = [2usize, 4, 16, 96];
        let mut large: Vec<PreflopGpu> = cuts.iter()
            .map(|&parts| PreflopGpu::new_large_pinned(&s, 4000, Some(parts), Some(pinned)).unwrap()).collect();
        for (g, &parts) in large.iter().zip(&cuts) {
            let info = g.large_game().unwrap();
            assert_eq!(info.parts, parts, "{name}");
            if g.use_multiway != 0 && normal.mw_nterms > 0 { assert_eq!(g.layout(), pinned, "{name}"); }
            assert_eq!(bits(g).0, bits(&normal).0, "{name}: uploaded tables");
        }
        let start = s.iteration;
        let mut clocks = vec![start; cuts.len()];
        let mut clock = start;
        for round in 0..6 {
            assert!(normal.try_iterate_counter(&mut clock, None).unwrap());
            let want = normal.gaps_and_evs().unwrap();
            let want_bits = bits(&normal);
            for (k, g) in large.iter_mut().enumerate() {
                assert!(g.try_iterate_counter(&mut clocks[k], None).unwrap());
                let got = g.gaps_and_evs().unwrap();
                let at = format!("{name}, {} parts, round {round}", cuts[k]);
                let got_bits = bits(g);
                assert!(got_bits.0 == want_bits.0, "{at}: regrets differ");
                assert!(got_bits.1 == want_bits.1, "{at}: strategy sums differ");
                assert!(got_bits.2 == want_bits.2, "{at}: evaluation roots differ");
                assert_eq!(got.0.iter().map(|v| v.to_bits()).collect::<Vec<_>>(), want.0.iter().map(|v| v.to_bits()).collect::<Vec<_>>(), "{at}: gaps");
                assert_eq!(got.1.iter().map(|v| v.to_bits()).collect::<Vec<_>>(), want.1.iter().map(|v| v.to_bits()).collect::<Vec<_>>(), "{at}: values");
                assert_eq!(clocks[k], clock);
            }
            if round >= 2 {
                assert!(large.iter().all(|g| g.eval_graph.is_some() && g.learning_graphs.iter().any(|x| x.is_some())), "{name}: graphs captured");
            }
            if learned && round == 2 {
                // the host refreshes the corrections from the device's averages
                normal.sync_to_cpu(&mut s).unwrap();
                s.refresh_leaf_values().unwrap();
                normal.upload_leaf_corr(&s).unwrap();
                for g in large.iter_mut() { g.upload_leaf_corr(&s).unwrap(); }
            }
        }
        // an interrupted pass leaves the same state behind, and the download matches
        let stop = AtomicBool::new(true);
        for (k, g) in large.iter_mut().enumerate() {
            let before = bits(g);
            assert!(!g.try_iterate_counter(&mut clocks[k], Some(&stop)).unwrap());
            assert!(bits(g) == before && clocks[k] == clock, "{name}: stopped pass");
        }
        normal.sync_to_cpu(&mut s).unwrap();
        let from_normal = s.arena_snapshot();
        large[1].sync_to_cpu(&mut s).unwrap();
        let from_large = s.arena_snapshot();
        assert!(from_normal.0.iter().zip(&from_large.0).all(|(a, b)| a.to_bits() == b.to_bits())
            && from_normal.1.iter().zip(&from_large.1).all(|(a, b)| a.to_bits() == b.to_bits()), "{name}: download");
        // and the device agrees with the CPU's own evaluation of that state
        let (cpu, gpu) = (s.gaps_and_evs(), large[1].gaps_and_evs().unwrap());
        assert!(close(&cpu, &gpu, 5e-3), "{name}: cpu {cpu:?} gpu {gpu:?}");
    }

    #[test]
    fn large_game_mode_matches_the_normal_plan_bit_for_bit() {
        for (name, s) in fixtures() {
            step_for_step(name, s, |_| {});
        }
    }

    #[test]
    fn large_game_mode_matches_with_a_frozen_seat_and_a_locked_spot() {
        let s = game(4, "static", &[2.5, 4.0], 3, true);
        step_for_step("4 seats, frozen and locked", s, |s| {
            let n = s.n;
            s.seat_frozen[n - 2] = true;
            let node = s.child(0, 1);
            let mut lock = vec![0.0; s.nodes[node].actions.len() * NUM_CLASSES];
            lock[..NUM_CLASSES].fill(1.0);
            s.point_locks.insert(node as u32, lock);
        });
    }

    #[test]
    fn large_game_mode_matches_without_the_heads_up_cache_and_with_short_batches() {
        // the choices a squeezed budget makes: pin them on both sides
        let mut s = game(4, "leafnet", &[2.5, 4.0], 3, true);
        for _ in 0..12 { s.iterate(); }
        s.refresh_leaf_values().unwrap();
        let budget_for = |s: &PreflopSolver| -> u64 {
            // just under the heads-up cache, so the normal plan leaves it out
            let mut budget = minimum_need_mb(s).ceil() as u64 + 1;
            while PreflopGpu::new(s, budget).is_err() { budget += 1; }
            budget
        };
        let budget = budget_for(&s);
        let mut normal = PreflopGpu::new(&s, budget).expect("test requires CUDA");
        let pinned = normal.layout();
        println!("squeezed normal plan: budget {budget} MB, batch {}, heads-up cache {}", pinned.0, pinned.1);
        let mut large = PreflopGpu::new_large_pinned(&s, 4000, Some(8), Some(pinned)).unwrap();
        assert_eq!(large.layout(), pinned);
        let (mut a, mut b) = (s.iteration, s.iteration);
        for round in 0..4 {
            normal.try_iterate_counter(&mut a, None).unwrap();
            large.try_iterate_counter(&mut b, None).unwrap();
            let (want, got) = (normal.gaps_and_evs().unwrap(), large.gaps_and_evs().unwrap());
            assert!(bits(&normal) == bits(&large), "round {round}");
            assert_eq!(format!("{want:?}"), format!("{got:?}"), "round {round}");
        }
    }

    #[test]
    fn a_game_too_big_for_the_normal_plan_solves_in_large_game_mode() {
        let mut s = game(6, "static", &[2.5, 4.0], 3, true);
        for _ in 0..4 { s.iterate(); }
        let (normal_need, large_need) = (minimum_need_mb(&s), large_need_mb(&s));
        println!("{} nodes: normal plan {normal_need:.0} MB, large-game mode {large_need:.0} MB", s.nodes.len());
        assert!(large_need + 4.0 < normal_need, "the fixture must leave a gap between the two modes");
        // plenty of room: the fast plans, never the large-game mode
        let (mut roomy, selection) = PreflopGpu::new_throughput(&s, 4000).expect("test requires CUDA");
        assert!(selection.mode != "large_game" && roomy.large_game().is_none());
        // room for the large-game mode only
        let budget = ((normal_need + large_need) / 2.0) as u64;
        assert!(PreflopGpu::new(&s, budget).is_err());
        let ctx = CudaContext::new(0).unwrap();
        let before = used_bytes(&ctx);
        let (mut g, selection) = PreflopGpu::new_throughput(&s, budget).unwrap();
        assert_eq!(selection.mode, "large_game");
        assert!(selection.fallback_reason.unwrap().contains("VRAM"));
        let info = g.large_game().unwrap();
        // what it allocated is what it planned, within the slack it reserves
        let used = (used_bytes(&ctx) - before) as f64 / 1e6;
        println!("large-game mode in {budget} MB: {info:?}, {used:.1} MB allocated");
        assert!(used <= info.need_mb && info.need_mb <= budget as f64, "allocated {used} MB, planned {} MB", info.need_mb);
        assert!(used >= info.need_mb - 64.0 - 8.0, "allocated {used} MB, planned {} MB", info.need_mb);
        // same solve as the roomy engine, to the rounding of their batch choices
        let (mut a, mut b) = (s.iteration, s.iteration);
        for round in 0..5 {
            roomy.try_iterate_counter(&mut a, None).unwrap();
            g.try_iterate_counter(&mut b, None).unwrap();
            let (want, got) = (roomy.gaps_and_evs().unwrap(), g.gaps_and_evs().unwrap());
            assert!(close(&want, &got, 2e-4), "round {round}: {want:?} vs {got:?}");
        }
        g.sync_to_cpu(&mut s).unwrap();
        let (cpu, gpu) = (s.gaps_and_evs(), g.gaps_and_evs().unwrap());
        assert!(close(&cpu, &gpu, 5e-3), "cpu {cpu:?} gpu {gpu:?}");
        // a budget below even the large-game mode still declines, naming both
        let error = PreflopGpu::new_throughput(&s, (large_need - 3.0).max(1.0) as u64).err().unwrap();
        assert!(error.contains("large-game mode"), "{error}");
    }
}
