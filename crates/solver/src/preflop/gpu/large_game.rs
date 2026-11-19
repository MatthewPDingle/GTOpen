//! Large-game mode: the normal plan's kernels, run over the tree one part at
//! a time, for games whose per-node tables do not fit the card at once.
//!
//! The normal plan holds a reach block for every node and a value block for
//! every terminal at the same time. Here the tree is cut below its first few
//! decisions into parts (runs of whole subtrees). The few nodes above the cut
//! keep their own blocks; every part reuses one shared range of reach and
//! value blocks. The kernels are the normal plan's, unchanged: they read
//! blocks through `reach_src` and `val_slot`, so only those two tables, the
//! launch order and the per-part terminal lists differ. Each node sees the
//! same inputs in the same order, so a solve matches the normal plan bit for
//! bit when both use the same sample batch and equity-cache choice.
//!
//! The first half of this file is the host-side plan (no CUDA); the order
//! of work and the launches follow it.
use super::*;

/// How finely the tree may be cut: a part holds at most 1/k of the nodes.
pub(super) const LADDER: [usize; 12] = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96];

/// Context, launch tables and allocator slack outside the counted arrays.
const SLACK_BYTES: usize = 64_000_000;

/// One part's slot tables, as offsets into the concatenated device arrays.
#[derive(Clone, Debug, Default)]
pub(super) struct Tables {
    /// Reach block -> slot; `nblocks` entries from `slots_at`.
    pub slots_at: usize,
    pub nblocks: usize,
    /// Slot -> reach block; `union` entries from `blocks_at`.
    pub blocks_at: usize,
    pub union: usize,
    /// Per-traverser work lists (and the union as the last span), relative
    /// to `work_at`.
    pub work_at: usize,
    pub work_len: usize,
    pub spans: Vec<(u32, u32)>,
    /// The compact map (traverser x union -> its own slot), when it pays.
    pub compact_at: usize,
    pub compact_len: usize,
    pub compact: bool,
    /// Slots a traverser's CDFs or normalized reaches occupy.
    pub capacity: usize,
}

/// One part of the tree: a run of whole subtrees hanging off the top.
#[derive(Clone, Debug, Default)]
pub(super) struct Chunk {
    /// Level spans into `Plan::act_nodes`, top-down.
    pub spans: Vec<(u32, u32)>,
    /// Ranges (start, count) into the node-ordered terminal lists.
    pub terms: (u32, u32),
    pub hu: (u32, u32),
    pub leaf: (u32, u32),
    pub mw_terms: (u32, u32),
    /// Reach blocks this part writes, from `Plan::chunk_base`.
    pub blocks: u32,
    /// Value slots (start, count) of this part's roots, which the top reads.
    pub frontier: (u32, u32),
    pub nodes: u32,
    pub mw: Tables,
    pub eq: Tables,
}

/// The node-ordered terminal lists the kernels take.
pub(super) struct Lists {
    pub terms: Vec<u32>,
    /// Heads-up single-pot pot-share terminals (blockers reprice them).
    pub hu: Vec<u32>,
    /// Learned flop terminals.
    pub leaf: Vec<u32>,
    /// Coupled multiway terminals.
    pub mw: Vec<u32>,
}

impl Lists {
    pub(super) fn build(s: &PreflopSolver) -> Result<Self, String> {
        let pick = |keep: &dyn Fn(&super::super::PNode) -> bool| -> Vec<u32> {
            s.nodes.iter().enumerate().filter(|(_, nd)| keep(nd)).map(|(i, _)| i as u32).collect()
        };
        let leaf = s.leaf_terminals().map_or(Vec::new(), |(nodes, _, _)| nodes.to_vec());
        if leaf.windows(2).any(|w| w[0] >= w[1]) {
            return Err("learned terminals are not in tree order".into());
        }
        Ok(Self {
            terms: pick(&|nd| nd.kind != KIND_ACTION),
            hu: pick(&|nd| nd.kind == KIND_POT_SHARE && nd.live.count_ones() == 2 && nd.side_pots.is_empty()),
            leaf,
            mw: pick(&|nd| coupled_terminal(s, nd)),
        })
    }
}

pub(super) struct Plan {
    /// The ladder step this plan was cut at.
    pub parts: usize,
    pub reach_src: Vec<u32>,
    pub reach_blocks: usize,
    /// The first reach block the parts share; below it are the roots and the
    /// blocks of the nodes at and just under the top.
    pub chunk_base: usize,
    pub val_slot: Vec<u32>,
    pub value_blocks: usize,
    /// Value slots (start, count) of every part's roots.
    pub frontier: (u32, u32),
    pub act_nodes: Vec<u32>,
    /// Level spans of the top, top-down.
    pub top_spans: Vec<(u32, u32)>,
    pub chunks: Vec<Chunk>,
    pub mw_slots: Vec<u32>,
    pub mw_blocks: Vec<u32>,
    pub mw_work: Vec<u32>,
    pub mw_compact: Vec<u32>,
    pub eq_slots: Vec<u32>,
    pub eq_blocks: Vec<u32>,
    pub eq_work: Vec<u32>,
    /// Scratch sizes: the largest part's.
    pub mw_union_max: usize,
    pub mw_capacity_max: usize,
    pub mw_terms_max: usize,
    pub eq_union_max: usize,
    pub levels_total: usize,
}

/// What a plan takes on the card under a budget.
#[derive(Clone, Debug, PartialEq)]
pub(super) struct Fit {
    /// Samples per multiway CDF batch (0 without multiway terminals).
    pub batch: usize,
    pub eq_cache: bool,
    pub need_bytes: usize,
    /// Kernel launches per traverser sweep, the cost of cutting finer.
    pub launches: usize,
}

/// Nodes in each node's subtree, itself included. Nodes are stored
/// parent-first and depth-first, so a subtree is the index range
/// `i .. i + size[i]`.
fn subtree_sizes(s: &PreflopSolver) -> Result<Vec<u32>, String> {
    let n = s.nodes.len();
    let mut size = vec![1u32; n];
    for i in (0..n).rev() {
        let nd = &s.nodes[i];
        if nd.kind != KIND_ACTION { continue; }
        let mut next = i + 1;
        for a in 0..nd.actions.len() {
            let c = s.child(i, a);
            if c != next {
                return Err("tree is not stored depth-first".into());
            }
            next += size[c] as usize;
        }
        size[i] = (next - i) as u32;
    }
    Ok(size)
}

impl Plan {
    /// Cut the tree so that no part holds more than 1/`parts` of the nodes.
    pub(super) fn build(s: &PreflopSolver, lists: &Lists, parts: usize) -> Result<Self, String> {
        let n = s.nodes.len();
        let np = s.n;
        if n < 2 || s.nodes[0].kind != KIND_ACTION {
            return Err("large-game mode needs a tree with a decision at the root".into());
        }
        let size = subtree_sizes(s)?;
        let target = n.div_ceil(parts.max(1)).max(1);
        // The top: the root and every decision whose subtree is too big for
        // one part. Its children that are not top are the parts' roots.
        let mut top = vec![false; n];
        let mut frontier_of = vec![false; n];
        let mut depth = vec![0u32; n];
        top[0] = true;
        for i in 0..n {
            let nd = &s.nodes[i];
            if nd.kind != KIND_ACTION { continue; }
            for a in 0..nd.actions.len() {
                let c = s.child(i, a);
                depth[c] = depth[i] + 1;
                if top[i] {
                    if s.nodes[c].kind == KIND_ACTION && size[c] as usize > target {
                        top[c] = true;
                    } else {
                        frontier_of[c] = true;
                    }
                }
            }
        }
        // Group consecutive roots into parts of at most `target` nodes.
        let roots: Vec<usize> = (0..n).filter(|&i| frontier_of[i]).collect();
        let mut groups: Vec<(usize, usize)> = Vec::new(); // ranges into `roots`
        let (mut start, mut held) = (0usize, 0usize);
        for (k, &r) in roots.iter().enumerate() {
            let sz = size[r] as usize;
            if held > 0 && held + sz > target {
                groups.push((start, k));
                start = k;
                held = 0;
            }
            held += sz;
        }
        if held > 0 { groups.push((start, roots.len())); }

        // Reach blocks: roots, then the nodes at and just under the top,
        // then one range every part reuses.
        let mut block = vec![u32::MAX; n];
        let mut next = np;
        for i in 1..n {
            if top[i] || frontier_of[i] {
                block[i] = next as u32;
                next += 1;
            }
        }
        let chunk_base = next;
        // Value slots: the root, the other top decisions, the parts' roots
        // (each part's together), then the shared range.
        let mut val_slot = vec![0u32; n];
        let mut next_val = 1usize;
        for i in 1..n {
            if top[i] {
                val_slot[i] = next_val as u32;
                next_val += 1;
            }
        }
        let frontier_start = next_val;
        for &r in &roots {
            val_slot[r] = next_val as u32;
            next_val += 1;
        }
        let shared_val = next_val;

        let max_depth = depth.iter().copied().max().unwrap_or(0) as usize;
        let mut act_nodes: Vec<u32> = Vec::new();
        let mut top_levels = vec![Vec::new(); max_depth + 1];
        for i in 0..n {
            if top[i] { top_levels[depth[i] as usize].push(i as u32); }
        }
        let mut top_spans = Vec::new();
        for level in &top_levels {
            if level.is_empty() { continue; }
            top_spans.push((act_nodes.len() as u32, level.len() as u32));
            act_nodes.extend_from_slice(level);
        }
        let mut levels_total = top_spans.len();

        // Per part: local reach blocks, terminal slots and level lists.
        let mut chunks: Vec<Chunk> = Vec::with_capacity(groups.len());
        let mut inner_action: Vec<Vec<u32>> = Vec::new(); // per part, its inner decisions
        let (mut max_blocks, mut max_terms) = (0usize, 0usize);
        let mut widths = [0usize; 2];
        let range_in = |list: &[u32], lo: usize, hi: usize| -> (u32, u32) {
            let a = list.partition_point(|&x| (x as usize) < lo);
            let b = list.partition_point(|&x| (x as usize) < hi);
            (a as u32, (b - a) as u32)
        };
        let mut frontier_at = frontier_start;
        for &(ga, gb) in &groups {
            let lo = roots[ga];
            let last = roots[gb - 1];
            let hi = last + size[last] as usize;
            let mut chunk = Chunk {
                terms: range_in(&lists.terms, lo, hi),
                hu: range_in(&lists.hu, lo, hi),
                leaf: range_in(&lists.leaf, lo, hi),
                mw_terms: range_in(&lists.mw, lo, hi),
                frontier: (frontier_at as u32, (gb - ga) as u32),
                ..Default::default()
            };
            frontier_at += gb - ga;
            let mut levels = vec![Vec::new(); max_depth + 1];
            let (mut local, mut terms) = (0usize, 0usize);
            let mut inner = Vec::new();
            for &r in &roots[ga..gb] {
                chunk.nodes += size[r];
                for i in r..r + size[r] as usize {
                    let action = s.nodes[i].kind == KIND_ACTION;
                    if action { levels[depth[i] as usize].push(i as u32); }
                    if i == r { continue; }
                    block[i] = (chunk_base + local) as u32;
                    local += 1;
                    if action {
                        inner.push(i as u32);
                    } else {
                        val_slot[i] = (shared_val + terms) as u32;
                        terms += 1;
                    }
                }
            }
            for (d, level) in levels.iter().enumerate() {
                if level.is_empty() { continue; }
                chunk.spans.push((act_nodes.len() as u32, level.len() as u32));
                act_nodes.extend_from_slice(level);
                let inner_count = level.iter().filter(|&&i| !frontier_of[i as usize]).count();
                widths[d % 2] = widths[d % 2].max(inner_count);
            }
            levels_total += chunk.spans.len();
            chunk.blocks = local as u32;
            max_blocks = max_blocks.max(local);
            max_terms = max_terms.max(terms);
            inner_action.push(inner);
            chunks.push(chunk);
        }
        // Inner decisions: scratch that alternate depths share, as ValuePlan.
        let bases = [shared_val + max_terms, shared_val + max_terms + widths[0]];
        for inner in &inner_action {
            let mut offset = vec![0usize; max_depth + 1];
            for &i in inner {
                let d = depth[i as usize] as usize;
                val_slot[i as usize] = (bases[d % 2] + offset[d]) as u32;
                offset[d] += 1;
            }
        }
        let value_blocks = shared_val + max_terms + widths[0] + widths[1];
        let reach_blocks = chunk_base + max_blocks;
        if reach_blocks > u32::MAX as usize || value_blocks > u32::MAX as usize {
            return Err("large-game tables beyond 32-bit block indexing".into());
        }

        // reach_src as reach_sources(), with the blocks above.
        let mut reach_src = vec![0u32; n * np];
        for q in 0..np { reach_src[q] = q as u32; }
        for (i, node) in s.nodes.iter().enumerate() {
            if node.kind != KIND_ACTION { continue; }
            for a in 0..node.actions.len() {
                let c = s.child(i, a);
                reach_src.copy_within(i * np..(i + 1) * np, c * np);
                reach_src[c * np + node.actor as usize] = block[c];
            }
        }

        let mut plan = Self {
            parts, reach_src, reach_blocks, chunk_base, val_slot, value_blocks,
            frontier: (frontier_start as u32, roots.len() as u32),
            act_nodes, top_spans, chunks,
            mw_slots: Vec::new(), mw_blocks: Vec::new(), mw_work: Vec::new(), mw_compact: Vec::new(),
            eq_slots: Vec::new(), eq_blocks: Vec::new(), eq_work: Vec::new(),
            mw_union_max: 0, mw_capacity_max: 0, mw_terms_max: 0, eq_union_max: 0,
            levels_total,
        };
        plan.slot_tables(s, lists)?;
        Ok(plan)
    }

    /// Each part's own multiway CDF and heads-up equity-cache slots: the
    /// distinct opponent reach blocks its terminals read, as
    /// `EquityCachePlan::build_for` over that part alone.
    fn slot_tables(&mut self, s: &PreflopSolver, lists: &Lists) -> Result<(), String> {
        let np = s.n;
        for k in 0..self.chunks.len() {
            let nblocks = self.chunk_base + self.chunks[k].blocks as usize;
            let (t0, tn) = self.chunks[k].terms;
            let terms = &lists.terms[t0 as usize..(t0 + tn) as usize];
            for multiway in [true, false] {
                let mut needed = vec![false; np * nblocks];
                let mut any = false;
                for &i in terms {
                    let node = &s.nodes[i as usize];
                    if node.kind != KIND_POT_SHARE || coupled_terminal(s, node) != multiway { continue; }
                    for p in 0..np {
                        if (node.live >> p) & 1 == 0 { continue; }
                        for q in 0..np {
                            if q != p && (node.live >> q) & 1 != 0 {
                                needed[p * nblocks + self.reach_src[i as usize * np + q] as usize] = true;
                                any = true;
                            }
                        }
                    }
                }
                let mut tables = Tables { nblocks, ..Default::default() };
                let (slots_all, blocks_all, work_all) = if multiway {
                    (&mut self.mw_slots, &mut self.mw_blocks, &mut self.mw_work)
                } else {
                    (&mut self.eq_slots, &mut self.eq_blocks, &mut self.eq_work)
                };
                tables.slots_at = slots_all.len();
                tables.blocks_at = blocks_all.len();
                tables.work_at = work_all.len();
                if !any {
                    // Kernels never read a slot here; keep one entry so the
                    // device slices are not empty.
                    tables.nblocks = 1;
                    slots_all.push(0);
                    blocks_all.push(0);
                    work_all.push(0);
                    tables.work_len = 1;
                    tables.spans = vec![(0, 0); np + 1];
                } else {
                    slots_all.resize(tables.slots_at + nblocks, u32::MAX);
                    let mut blocks: Vec<u32> = Vec::new();
                    for block in 0..nblocks {
                        if (0..np).any(|p| needed[p * nblocks + block]) {
                            slots_all[tables.slots_at + block] = blocks.len() as u32;
                            blocks.push(block as u32);
                        }
                    }
                    let mut work: Vec<u32> = Vec::new();
                    for p in 0..=np {
                        let start = work.len() as u32;
                        for (slot, &block) in blocks.iter().enumerate() {
                            if p == np || needed[p * nblocks + block as usize] {
                                work.push(slot as u32);
                            }
                        }
                        tables.spans.push((start, work.len() as u32 - start));
                    }
                    tables.union = blocks.len();
                    tables.work_len = work.len();
                    tables.capacity = tables.union;
                    if multiway {
                        let view = EquityCachePlan { slots: Vec::new(), blocks: blocks.clone(), work: work.clone(), spans: tables.spans.clone() };
                        let compact = MultiwayCompactPlan::build(&view, np)?;
                        if compact.enabled {
                            tables.compact = true;
                            tables.capacity = compact.capacity;
                            tables.compact_at = self.mw_compact.len();
                            tables.compact_len = compact.map.len();
                            self.mw_compact.extend_from_slice(&compact.map);
                        }
                    }
                    blocks_all.extend_from_slice(&blocks);
                    work_all.extend_from_slice(&work);
                }
                if multiway {
                    self.mw_union_max = self.mw_union_max.max(tables.union);
                    self.mw_capacity_max = self.mw_capacity_max.max(tables.capacity);
                    self.mw_terms_max = self.mw_terms_max.max(self.chunks[k].mw_terms.1 as usize);
                    self.chunks[k].mw = tables;
                } else {
                    self.eq_union_max = self.eq_union_max.max(tables.union);
                    self.chunks[k].eq = tables;
                }
            }
        }
        if self.mw_compact.is_empty() { self.mw_compact.push(0); }
        Ok(())
    }

    /// Device bytes of everything but the multiway CDF scratch and the
    /// optional heads-up equity cache.
    pub(super) fn fixed_bytes(&self, s: &PreflopSolver, lists: &Lists) -> Result<usize, String> {
        let forced = forced_storage_bytes(forced_policy_elements(s)?)?;
        self.tree_bytes(s, lists)?.checked_add(forced).ok_or_else(|| "large-game allocation size overflow".to_string())
    }

    /// `fixed_bytes` without the locked and profiled strategies, which
    /// change with the table and not with the tree.
    fn tree_bytes(&self, s: &PreflopSolver, lists: &Lists) -> Result<usize, String> {
        let (n, np, nc) = (s.nodes.len(), s.n, NUM_CLASSES);
        let eq_channels = if super::super::balanced_family(&s.cfg.realization) { 3usize } else { 1 };
        // every u32/i32/f32 array the constructor uploads or allocates
        let mut words = 0usize;
        words += 11 * n + 3 * n * np; // tree: kind..calib, inv, rw, reach_src
        words += s.children.len() + 3 * n; // children, src, foff, val_slot
        words += self.act_nodes.len() + lists.terms.len().max(1);
        words += 2 * s.arena_len; // regrets and strategy sums
        words += nc + nc; // cbase, cprob
        words += eq_channels * nc * nc; // equity tables
        words += self.reach_blocks * (nc + 1); // reach and its totals
        words += self.value_blocks * nc;
        words += 2 * np * nc; // evaluation roots
        words += 2 * np * (self.frontier.1 as usize).max(1) * nc; // the parts' roots per evaluation pass
        words += self.eq_slots.len() + self.eq_blocks.len() + self.eq_work.len();
        if s.cfg.card_removal {
            words += self.reach_blocks * 13 + eq_channels * nc * nc + lists.hu.len().max(1);
        }
        if !lists.leaf.is_empty() {
            words += lists.leaf.len() * (1 + 2 + 2 * nc);
        }
        if !lists.mw.is_empty() {
            words += 3 * super::super::multiway::SAMPLES * nc; // order, lower, upper
            words += self.mw_slots.len() + self.mw_blocks.len() + self.mw_work.len() + self.mw_compact.len();
            words += lists.mw.len(); // terminal list
            words += self.mw_union_max + self.mw_terms_max; // active flags, terminal probabilities
            words += self.mw_capacity_max * nc; // normalized reaches
        }
        words.checked_mul(4).and_then(|b| b.checked_add(SLACK_BYTES))
            .ok_or_else(|| "large-game allocation size overflow".to_string())
    }

    /// The batch and cache this plan can take in `budget_bytes`, or None
    /// when even its least does not fit. `forced` pins the batch and the
    /// cache choice (tests compare against a normal plan with the same).
    pub(super) fn fit(
        &self, s: &PreflopSolver, lists: &Lists, budget_bytes: usize, forced: Option<(usize, bool)>,
    ) -> Result<Option<Fit>, String> {
        let nc = NUM_CLASSES;
        let eq_channels = if super::super::balanced_family(&s.cfg.realization) { 3usize } else { 1 };
        let fixed = self.fixed_bytes(s, lists)?;
        let one_sample = self.mw_capacity_max * (nc + 1) * 4;
        let eq_cache_bytes = self.eq_union_max * nc * eq_channels * 4;
        let samples = super::super::multiway::SAMPLES;
        let (batch, eq_cache) = match forced {
            Some((batch, eq_cache)) => {
                let batch = if one_sample == 0 { 0 } else { batch.clamp(1, 32.min(samples)) };
                (batch, eq_cache && self.eq_union_max > 0)
            }
            None => {
                if fixed + one_sample > budget_bytes { return Ok(None); }
                let batch = if one_sample == 0 { 0 } else { ((budget_bytes - fixed) / one_sample).min(32).min(samples) };
                let eq_cache = self.eq_union_max > 0 && fixed + batch * one_sample + eq_cache_bytes <= budget_bytes;
                (batch, eq_cache)
            }
        };
        let need_bytes = fixed + batch * one_sample + if eq_cache { eq_cache_bytes } else { 0 };
        if need_bytes > budget_bytes { return Ok(None); }
        // per traverser sweep: every level down and up, a dozen terminal
        // kernels per part, two per multiway batch
        let batches = if batch == 0 { 0 } else { samples.div_ceil(batch) };
        let launches = 2 * self.levels_total + self.chunks.len() * (12 + 2 * batches);
        Ok(Some(Fit { batch, eq_cache, need_bytes, launches }))
    }
}

/// The coarsest cut `choose` picks by itself. Measured on a 32 GB card
/// (5.8M and 11.5M nodes, 8 seats): 16 and 24 parts ran as fast as or faster
/// than 4 to 12, and held far less.
const FIRST_CHOICE: usize = 16;

/// Share of the budget a cut should stay under when a finer one can: a plan
/// that filled the card to the last few hundred MB spilled into shared
/// system memory under Windows and ran two to three times slower.
const ROOMY: f64 = 0.9;

/// The cut for `budget_mb`: from `FIRST_CHOICE` towards finer cuts, the
/// first that affords full 32-sample multiway batches and the heads-up
/// equity cache within `ROOMY` of the budget; failing that, the one with
/// the largest batches (then the cache, then the least memory).
/// `PREFLOP_GPU_LARGE_PARTS` pins the cut for experiments.
pub(super) fn choose(s: &PreflopSolver, lists: &Lists, budget_mb: u64) -> Result<(Plan, Fit), String> {
    let budget = (budget_mb as usize).saturating_mul(1_000_000);
    let roomy = (budget as f64 * ROOMY) as usize;
    let forced_parts = std::env::var("PREFLOP_GPU_LARGE_PARTS").ok().and_then(|v| v.parse::<usize>().ok());
    let mut best: Option<(Plan, Fit)> = None;
    let mut least = usize::MAX;
    for &parts in LADDER.iter() {
        match forced_parts {
            Some(forced) => if forced != parts { continue; },
            None => if parts < FIRST_CHOICE { continue; },
        }
        let plan = Plan::build(s, lists, parts)?;
        least = least.min(plan.fixed_bytes(s, lists)? + plan.mw_capacity_max * (NUM_CLASSES + 1) * 4);
        let Some(fit) = plan.fit(s, lists, budget, None)? else { continue; };
        let full = (fit.batch == 0 || fit.batch >= 32) && (fit.eq_cache || plan.eq_union_max == 0);
        let done = full && fit.need_bytes <= roomy;
        let rank = |f: &Fit| (f.batch, f.eq_cache, std::cmp::Reverse(f.need_bytes));
        if done || best.as_ref().map_or(true, |(_, b)| rank(&fit) > rank(b)) {
            best = Some((plan, fit));
        }
        if done { break; }
    }
    best.ok_or_else(|| format!(
        "needs ~{:.0} MB VRAM even in large-game mode (budget {budget_mb} MB)", least as f64 / 1e6))
}

/// The least GPU memory (MB) large-game mode needs for this built game, or
/// infinity when the mode does not cover it: `large_tree_need_mb` plus
/// `large_policy_need_mb`.
pub fn large_need_mb(s: &PreflopSolver) -> f64 {
    large_tree_need_mb(s) + large_policy_need_mb(s)
}

/// The part of `large_need_mb` fixed by the built tree and its model.
pub fn large_tree_need_mb(s: &PreflopSolver) -> f64 {
    if supported_tree(s).is_err() { return f64::INFINITY; }
    let Ok(lists) = Lists::build(s) else { return f64::INFINITY };
    let mut least = f64::INFINITY;
    // the finest cuts need the least; two steps bound the cost on big trees
    for &parts in LADDER.iter().rev().take(2) {
        let Ok(plan) = Plan::build(s, &lists, parts) else { continue };
        let Ok(fixed) = plan.tree_bytes(s, &lists) else { continue };
        least = least.min((fixed + plan.mw_capacity_max * (NUM_CLASSES + 1) * 4) as f64 / 1e6);
    }
    least
}

/// The part that changes with the table: locked and profiled strategies.
/// Infinite with the trust dial, which the mode does not cover.
pub fn large_policy_need_mb(s: &PreflopSolver) -> f64 {
    if s.rnr_active().is_some() { return f64::INFINITY; }
    match forced_policy_elements(s).and_then(forced_storage_bytes) {
        Ok(bytes) => bytes as f64 / 1e6,
        Err(_) => f64::INFINITY,
    }
}

/// `large_need_mb` for a game that is not built yet, from the counts of the
/// size walk: a fresh game with no locked strategies. Slightly generous (a
/// percent or two), since the cut itself is only known once the tree is built.
pub fn large_need_of(cfg: &super::super::PreflopConfig, est: &super::super::TreeEstimate) -> f64 {
    if cfg.icm.is_some() || cfg.unequal_stacks() { return f64::INFINITY; }
    let (nc, np) = (NUM_CLASSES as f64, cfg.positions.len() as f64);
    let (n, arena, g) = (est.nodes as f64, est.arena_len as f64, &est.gpu);
    if n + np > u32::MAX as f64 || arena > u32::MAX as f64 { return f64::INFINITY; }
    let actions = est.action_nodes as f64;
    let channels = if super::super::balanced_family(&cfg.realization) { 3.0 } else { 1.0 };
    // the blocks one part holds at the finest cuts, with room to spare
    let part = n / 48.0 + 1000.0;
    let hu = g.heads_up_terminals as f64;
    let mut words = 11.0 * n + 3.0 * n * np; // tree
    words += n + 3.0 * n + actions + (n - actions); // children, src, foff, val_slot, level and terminal lists
    words += 2.0 * arena;
    words += 2.0 * nc + channels * nc * nc + 2.0 * np * nc;
    words += part * (nc + 1.0) + part * nc; // reach with totals, values
    words += 2.0 * np * 1000.0 * nc; // the parts' roots per evaluation pass
    // each part's heads-up slot tables: a slot per block, the blocks read, the work lists
    let eq_blocks = n.min(2.0 * hu);
    words += 1.01 * n + eq_blocks + (eq_blocks + 2.0 * hu);
    if cfg.card_removal {
        words += part * 13.0 + channels * nc * nc + hu.max(1.0);
    }
    if cfg.realization == "leafnet" {
        words += g.leaf_terminals as f64 * (3.0 + 2.0 * nc);
    }
    if g.multiway_terminals > 0 {
        let (union, seats) = (1.01 * g.multiway_tables as f64, 1.01 * g.multiway_seat_tables as f64);
        words += 3.0 * super::super::multiway::SAMPLES as f64 * nc;
        words += 1.01 * n + union + (union + seats) + union * np; // slots, blocks, work, compact maps
        words += g.multiway_terminals as f64 + 2.0 * part; // terminal list, flags and probabilities
        words += part * nc + part * (nc + 1.0); // normalized reaches, one sample of CDFs
    }
    (words * 4.0 + 4.0 + SLACK_BYTES as f64) / 1e6
}

/// Large-game mode covers the default model: equal stacks, chip values, the
/// coupled multiway model, blockers, learned flop values, locks and profiles.
pub(super) fn supported(s: &PreflopSolver) -> Result<(), String> {
    if s.rnr_active().is_some() {
        return Err("large-game mode does not cover the trust dial".into());
    }
    supported_tree(s)
}

/// `supported` for what the built tree and its model fix.
fn supported_tree(s: &PreflopSolver) -> Result<(), String> {
    if s.icm.is_some() {
        return Err("large-game mode does not cover tournament payouts (ICM)".into());
    }
    if s.three_way.is_some() {
        return Err("large-game mode does not cover the exact 3-way table".into());
    }
    if s.nodes.iter().any(|nd| !nd.side_pots.is_empty()) {
        return Err("large-game mode does not cover side pots (unequal stacks)".into());
    }
    if s.multiway.is_none() {
        return Err("large-game mode needs the coupled multiway model".into());
    }
    if s.nodes.iter().any(|nd| nd.actions.len() > MAX_NA) {
        return Err("a node has more than 16 actions".into());
    }
    if s.arena_len > u32::MAX as usize {
        return Err("arenas beyond the GPU engine's 32-bit arena indexing".into());
    }
    Ok(())
}


/// What large-game mode would do with `budget_mb` for this built game, one
/// row per cut that fits (diagnostics; no CUDA).
pub fn large_plan_report(s: &PreflopSolver, budget_mb: u64) -> serde_json::Value {
    let mut rows = Vec::new();
    if let Err(reason) = supported(s) {
        return serde_json::json!({ "supported": false, "reason": reason });
    }
    let lists = match Lists::build(s) { Ok(l) => l, Err(reason) => return serde_json::json!({ "supported": false, "reason": reason }) };
    let budget = (budget_mb as usize).saturating_mul(1_000_000);
    for &parts in LADDER.iter() {
        let plan = match Plan::build(s, &lists, parts) { Ok(p) => p, Err(reason) => { rows.push(serde_json::json!({"parts": parts, "error": reason})); continue; } };
        let fixed = plan.fixed_bytes(s, &lists).unwrap_or(usize::MAX);
        let fit = plan.fit(s, &lists, budget, None).ok().flatten();
        rows.push(serde_json::json!({
            "parts": parts, "chunks": plan.chunks.len(),
            "top_nodes": plan.top_spans.iter().map(|x| x.1 as usize).sum::<usize>(),
            "part_roots": plan.frontier.1,
            "largest_part_nodes": plan.chunks.iter().map(|c| c.nodes).max().unwrap_or(0),
            "reach_blocks": plan.reach_blocks, "value_blocks": plan.value_blocks,
            "mw_union_max": plan.mw_union_max, "mw_capacity_max": plan.mw_capacity_max,
            "eq_union_max": plan.eq_union_max, "levels": plan.levels_total,
            "table_words": [plan.eq_slots.len(), plan.eq_blocks.len(), plan.eq_work.len(),
                plan.mw_slots.len(), plan.mw_blocks.len(), plan.mw_work.len(), plan.mw_compact.len()],
            "chunk_base": plan.chunk_base, "mw_terms_max": plan.mw_terms_max, "fixed_mb": fixed as f64 / 1e6,
            "least_mb": (fixed + plan.mw_capacity_max * (NUM_CLASSES + 1) * 4) as f64 / 1e6,
            "fit": fit.map(|f| serde_json::json!({"batch": f.batch, "eq_cache": f.eq_cache, "need_mb": f.need_bytes as f64 / 1e6, "launches": f.launches})),
        }));
    }
    serde_json::json!({ "supported": true, "nodes": s.nodes.len(), "budget_mb": budget_mb,
        "normal_least_mb": minimum_need_mb(s), "rows": rows })
}

// ---- the order of work ------------------------------------------------------

/// The steps a pass is made of. The card runs them (`OnDevice`); the plan
/// tests run the same order on a model of what each step reads and writes.
pub(super) trait Steps {
    fn init_root(&mut self) -> Result<(), String>;
    /// One level of decisions: each writes its children's reach blocks.
    fn down(&mut self, start: u32, count: u32, mode: i32) -> Result<(), String>;
    /// Totals of `count` reach blocks from `first`.
    fn mass(&mut self, first: usize, count: usize) -> Result<(), String>;
    fn eq_cache(&mut self, chunk: &Chunk, which: usize) -> Result<(), String>;
    fn terminals(&mut self, chunk: &Chunk, p: i32, gate: i32) -> Result<(), String>;
    /// One level of decisions: each reads its children's values.
    fn up(&mut self, start: u32, count: u32, p: i32, mode: i32) -> Result<(), String>;
    /// Keep the values of a part's roots for evaluation pass `seat_pass`.
    fn keep_roots(&mut self, plan: &Plan, chunk: &Chunk, seat_pass: usize) -> Result<(), String>;
    /// Put every part's roots of `seat_pass` back before the top runs.
    fn restore_roots(&mut self, plan: &Plan, seat_pass: usize) -> Result<(), String>;
    fn root_copy(&mut self, seat_pass: usize) -> Result<(), String>;
}

/// One full pass for traverser `p`, as `sweep`: the top's reaches, then
/// each part down, priced and back up, then the top's values.
pub(super) fn run_sweep<S: Steps>(plan: &Plan, steps: &mut S, np: usize, p: i32, mode: i32) -> Result<(), String> {
    steps.init_root()?;
    for &(start, count) in &plan.top_spans {
        steps.down(start, count, mode)?;
    }
    steps.mass(0, plan.chunk_base)?;
    let which = if mode == 0 { p as usize } else { np };
    for chunk in &plan.chunks {
        for &(start, count) in &chunk.spans {
            steps.down(start, count, mode)?;
        }
        steps.mass(plan.chunk_base, chunk.blocks as usize)?;
        steps.eq_cache(chunk, which)?;
        steps.terminals(chunk, p, 1)?;
        for &(start, count) in chunk.spans.iter().rev() {
            steps.up(start, count, p, mode)?;
        }
    }
    for &(start, count) in plan.top_spans.iter().rev() {
        steps.up(start, count, p, mode)?;
    }
    Ok(())
}

/// `queue_evaluation` in parts. Reaches of the average strategy are built
/// once per part; every seat's best response (`best[p]`: mode 2 or 3) and
/// average values run on them, and the part's root values wait until the
/// top is finished per seat and pass.
pub(super) fn run_evaluation<S: Steps>(plan: &Plan, steps: &mut S, np: usize, best: &[i32]) -> Result<(), String> {
    steps.init_root()?;
    for &(start, count) in &plan.top_spans {
        steps.down(start, count, 1)?;
    }
    steps.mass(0, plan.chunk_base)?;
    for chunk in &plan.chunks {
        for &(start, count) in &chunk.spans {
            steps.down(start, count, 1)?;
        }
        steps.mass(plan.chunk_base, chunk.blocks as usize)?;
        steps.eq_cache(chunk, np)?;
        for p in 0..np {
            // Average reaches are typically dense: avoid mask atomics here.
            steps.terminals(chunk, p as i32, 0)?;
            for (pass, mode) in [best[p], 1].into_iter().enumerate() {
                for &(start, count) in chunk.spans.iter().rev() {
                    steps.up(start, count, p as i32, mode)?;
                }
                steps.keep_roots(plan, chunk, 2 * p + pass)?;
            }
        }
    }
    for p in 0..np {
        for (pass, mode) in [best[p], 1].into_iter().enumerate() {
            steps.restore_roots(plan, 2 * p + pass)?;
            for &(start, count) in plan.top_spans.iter().rev() {
                steps.up(start, count, p as i32, mode)?;
            }
            steps.root_copy(2 * p + pass)?;
        }
    }
    Ok(())
}

struct OnDevice<'a> {
    gpu: &'a mut PreflopGpu,
    /// The evaluation's kept roots; a learning pass has none.
    stash: Option<&'a mut CudaSlice<f32>>,
}

impl Steps for OnDevice<'_> {
    fn init_root(&mut self) -> Result<(), String> { self.gpu.lg_init_root() }
    fn down(&mut self, start: u32, count: u32, mode: i32) -> Result<(), String> { self.gpu.lg_down(start, count, mode) }
    fn mass(&mut self, first: usize, count: usize) -> Result<(), String> { self.gpu.lg_mass(first, count) }
    fn eq_cache(&mut self, chunk: &Chunk, which: usize) -> Result<(), String> { self.gpu.lg_eq_cache(&chunk.eq, which) }
    fn terminals(&mut self, chunk: &Chunk, p: i32, gate: i32) -> Result<(), String> { self.gpu.lg_terminals(chunk, p, gate) }
    fn up(&mut self, start: u32, count: u32, p: i32, mode: i32) -> Result<(), String> { self.gpu.lg_up(start, count, p, mode) }
    fn keep_roots(&mut self, plan: &Plan, chunk: &Chunk, seat_pass: usize) -> Result<(), String> {
        let stash = self.stash.as_deref_mut().ok_or_else(|| "no stash in a learning pass".to_string())?;
        self.gpu.lg_stash(stash, plan, chunk.frontier.0 as usize, chunk.frontier.1 as usize, seat_pass, false)
    }
    fn restore_roots(&mut self, plan: &Plan, seat_pass: usize) -> Result<(), String> {
        let stash = self.stash.as_deref_mut().ok_or_else(|| "no stash in a learning pass".to_string())?;
        self.gpu.lg_stash(stash, plan, plan.frontier.0 as usize, plan.frontier.1 as usize, seat_pass, true)
    }
    fn root_copy(&mut self, seat_pass: usize) -> Result<(), String> { self.gpu.lg_root_copy(seat_pass) }
}

// ---- device side -----------------------------------------------------------

/// A plan chosen for a budget, handed to the constructor.
pub(super) struct Selected {
    pub plan: Plan,
    pub fit: Fit,
    pub lists: Lists,
}

impl Plan {
    /// The value layout in the normal plan's shape. The level spans are the
    /// top's, then each part's.
    pub(super) fn take_values(&mut self) -> ValuePlan {
        let mut spans = self.top_spans.clone();
        for chunk in &self.chunks { spans.extend_from_slice(&chunk.spans); }
        ValuePlan {
            slots: std::mem::take(&mut self.val_slot),
            blocks: self.value_blocks,
            action_nodes: std::mem::take(&mut self.act_nodes),
            spans,
        }
    }

    /// Every part's heads-up cache and multiway slot tables, one after
    /// another (each part reads its own slice).
    pub(super) fn take_slot_tables(&mut self, np: usize) -> (EquityCachePlan, EquityCachePlan) {
        let eq = EquityCachePlan {
            slots: std::mem::take(&mut self.eq_slots), blocks: std::mem::take(&mut self.eq_blocks),
            work: std::mem::take(&mut self.eq_work), spans: vec![(0, 0); np + 1],
        };
        let mw = EquityCachePlan {
            slots: std::mem::take(&mut self.mw_slots), blocks: std::mem::take(&mut self.mw_blocks),
            work: std::mem::take(&mut self.mw_work), spans: vec![(0, 0); np + 1],
        };
        (eq, mw)
    }
}

/// What a large-game engine keeps beside the normal plan's buffers.
pub(super) struct Device {
    /// The cut: spans, per-part ranges and slot-table offsets. Its big
    /// tables were moved to the card by the constructor.
    pub(super) plan: Plan,
    pub(super) fit: Fit,
    /// The parts' root values per evaluation pass: [2 x seat + pass][root][class].
    d_stash: CudaSlice<f32>,
}

impl Device {
    pub(super) fn new(gpu: &PreflopGpu, selected: Selected) -> Result<Self, String> {
        let roots = (selected.plan.frontier.1 as usize).max(1);
        let d_stash = gpu.stream.alloc_zeros::<f32>(2 * gpu.np as usize * roots * NUM_CLASSES).map_err(e)?;
        Ok(Self { plan: selected.plan, fit: selected.fit, d_stash })
    }
}

/// How a large-game engine was cut, for logs and tests.
#[derive(Debug, Clone, serde::Serialize)]
pub struct LargeGameInfo {
    pub parts: usize,
    pub chunks: usize,
    pub multiway_batch: usize,
    pub hu_equity_cache: bool,
    pub need_mb: f64,
}

impl PreflopGpu {
    /// Large-game mode for a game the normal plan cannot hold in
    /// `budget_mb`: the same kernels, the tree worked through in parts.
    pub fn new_large(s: &PreflopSolver, budget_mb: u64) -> Result<Self, String> {
        Self::new_large_with(s, budget_mb, None, None)
    }

    /// `parts` pins the cut and `forced` the multiway batch and heads-up
    /// cache choice, so a test can compare with a normal plan of the same.
    pub(super) fn new_large_with(
        s: &PreflopSolver, budget_mb: u64, parts: Option<usize>, forced: Option<(usize, bool)>,
    ) -> Result<Self, String> {
        supported(s)?;
        let lists = Lists::build(s)?;
        let (plan, fit) = match parts {
            Some(parts) => {
                let plan = Plan::build(s, &lists, parts)?;
                let budget = (budget_mb as usize).saturating_mul(1_000_000);
                let fit = plan.fit(s, &lists, budget, forced)?
                    .ok_or_else(|| format!("large-game mode in {parts} parts does not fit {budget_mb} MB"))?;
                (plan, fit)
            }
            None => choose(s, &lists, budget_mb)?,
        };
        println!(
            "preflop gpu: large-game mode, tree in {} parts (largest {} of {} nodes), {}-sample multiway batches, HU cache {}, ~{:.0} MB VRAM",
            plan.chunks.len(), plan.chunks.iter().map(|c| c.nodes).max().unwrap_or(0), s.nodes.len(),
            fit.batch, fit.eq_cache, fit.need_bytes as f64 / 1e6
        );
        Self::construct(s, budget_mb, true, false, false, false, None, false, Some(Selected { plan, fit, lists }))
    }

    /// Large-game mode with the cut, the multiway batch and the heads-up
    /// cache choice pinned (benchmarks; like-for-like checks against a
    /// normal plan, whose choices `layout` reports).
    pub fn new_large_pinned(
        s: &PreflopSolver, budget_mb: u64, parts: Option<usize>, pinned: Option<(usize, bool)>,
    ) -> Result<Self, String> {
        Self::new_large_with(s, budget_mb, parts, pinned)
    }

    /// Samples per multiway CDF batch and whether the heads-up equity cache
    /// is on: the two choices that set the rounding of a solve.
    pub fn layout(&self) -> (usize, bool) {
        (self.mw_batch as usize, self.use_eq_cache != 0)
    }

    /// Some when this engine runs in large-game mode.
    pub fn large_game(&self) -> Option<LargeGameInfo> {
        self.large.as_ref().map(|l| LargeGameInfo {
            parts: l.plan.parts, chunks: l.plan.chunks.len(), multiway_batch: l.fit.batch,
            hu_equity_cache: l.fit.eq_cache, need_mb: l.fit.need_bytes as f64 / 1e6,
        })
    }

    /// One full pass for traverser `p`, as `sweep`: the top's reaches, then
    /// each part down, priced and back up, then the top's values.
    pub(super) fn large_sweep(&mut self, p: i32, mode: i32) -> Result<(), String> {
        let large = self.large.take().ok_or_else(|| "large-game state missing".to_string())?;
        let result = self.large_sweep_with(&large, p, mode);
        self.large = Some(large);
        result
    }

    fn large_sweep_with(&mut self, large: &Device, p: i32, mode: i32) -> Result<(), String> {
        let np = self.np as usize;
        run_sweep(&large.plan, &mut OnDevice { gpu: self, stash: None }, np, p, mode)
    }

    /// `queue_evaluation` in parts. Reaches of the average strategy are
    /// built once per part; every seat's best response and average values
    /// run on them, and the part's root values wait in the stash until the
    /// top is finished per seat and pass.
    pub(super) fn large_queue_evaluation(&mut self) -> Result<(), String> {
        let mut large = self.large.take().ok_or_else(|| "large-game state missing".to_string())?;
        let result = self.large_evaluation_with(&mut large);
        self.large = Some(large);
        result
    }

    fn large_evaluation_with(&mut self, large: &mut Device) -> Result<(), String> {
        let np = self.np as usize;
        let best: Vec<i32> = (0..np).map(|p| if self.constrained_br[p] { 3 } else { 2 }).collect();
        let Device { plan, d_stash, .. } = large;
        run_evaluation(plan, &mut OnDevice { gpu: self, stash: Some(d_stash) }, np, &best)
    }

    /// Keep (or put back) the values of `count` part roots from value slot
    /// `first`, for one seat's evaluation pass.
    fn lg_stash(&mut self, stash: &mut CudaSlice<f32>, plan: &Plan, first: usize, count: usize, seat_pass: usize, restore: bool) -> Result<(), String> {
        let nc = NUM_CLASSES;
        let (roots_at, roots) = (plan.frontier.0 as usize, plan.frontier.1 as usize);
        let at = (seat_pass * roots + (first - roots_at)) * nc;
        if restore {
            let kept = stash.slice(at..at + count * nc);
            let mut values = self.d_val.slice_mut(first * nc..(first + count) * nc);
            self.stream.memcpy_dtod(&kept, &mut values).map_err(e)
        } else {
            let values = self.d_val.slice(first * nc..(first + count) * nc);
            let mut keep = stash.slice_mut(at..at + count * nc);
            self.stream.memcpy_dtod(&values, &mut keep).map_err(e)
        }
    }

    fn lg_root_copy(&mut self, seat_pass: usize) -> Result<(), String> {
        let nc = NUM_CLASSES;
        let root = self.d_val.slice(0..nc);
        let mut dst = self.d_eval_roots.slice_mut(seat_pass * nc..(seat_pass + 1) * nc);
        self.stream.memcpy_dtod(&root, &mut dst).map_err(e)
    }

    fn lg_init_root(&mut self) -> Result<(), String> {
        unsafe {
            self.stream.launch_builder(&self.f_init)
                .arg(&self.d_cprob).arg(&mut self.d_reach).arg(&self.np)
                .launch(Self::cfg(4)).map_err(e)?;
        }
        Ok(())
    }

    /// `down` for one level span.
    fn lg_down(&mut self, start: u32, count: u32, mode: i32) -> Result<(), String> {
        if count == 0 { return Ok(()); }
        let (start, count) = (start as i32, count as i32);
        unsafe {
            self.stream.launch_builder(&self.f_down)
                .arg(&self.d_act_nodes).arg(&start).arg(&count)
                .arg(&self.d_actor).arg(&self.d_na).arg(&self.d_off).arg(&self.d_cstart).arg(&self.d_children)
                .arg(&self.d_regrets).arg(&self.d_strat)
                .arg(&self.d_src).arg(&self.d_foff).arg(&self.d_forced)
                .arg(&self.d_reach_src).arg(&mut self.d_reach)
                .arg(&self.np).arg(&mode)
                .launch(Self::cfg(count as u32)).map_err(e)?;
        }
        Ok(())
    }

    /// Reach totals (and the blockers' rank masses) of `count` blocks from
    /// `first`: the top's once per pass, a part's after its down sweep.
    fn lg_mass(&mut self, first: usize, count: usize) -> Result<(), String> {
        if count == 0 { return Ok(()); }
        let nc = NUM_CLASSES;
        let reach = self.d_reach.slice(first * nc..(first + count) * nc);
        let mut mass = self.d_reach_mass.slice_mut(first..first + count);
        unsafe {
            self.stream.launch_builder(&self.f_reach_mass)
                .arg(&reach).arg(&mut mass)
                .launch(LaunchConfig { block_dim: (128, 1, 1), ..Self::cfg(count as u32) }).map_err(e)?;
            if let Some(r) = &mut self.removal {
                let blocks = count as u32;
                let mut rank = r.d_rank_mass.slice_mut(first * 13..(first + count) * 13);
                self.stream.launch_builder(&r.f_rank_mass)
                    .arg(&reach).arg(&blocks).arg(&mut rank)
                    .launch(LaunchConfig { grid_dim: (blocks.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 })
                    .map_err(e)?;
            }
        }
        Ok(())
    }

    /// `refresh_eq_cache` for one part's slots.
    fn lg_eq_cache(&mut self, t: &Tables, which: usize) -> Result<(), String> {
        if self.use_eq_cache == 0 { return Ok(()); }
        let (start, count) = t.spans[which];
        if count == 0 { return Ok(()); }
        let nc = NUM_CLASSES;
        let stride = t.union * nc;
        let work = self.d_eq_work.slice(t.work_at..t.work_at + t.work_len);
        let blocks = self.d_eq_blocks.slice(t.blocks_at..t.blocks_at + t.union);
        unsafe {
            for channel in 0..self.eq_channels {
                let at = channel * nc * nc;
                let tables = self.removal.as_ref().map_or(&self.d_eq, |r| &r.d_eq_w);
                let table = tables.slice(at..at + nc * nc);
                let mut cache = self.d_eq_cache.slice_mut(channel * stride..(channel + 1) * stride);
                self.stream.launch_builder(&self.f_equities)
                    .arg(&work).arg(&start)
                    .arg(&blocks).arg(&table)
                    .arg(&self.d_reach).arg(&self.d_reach_mass)
                    .arg(&mut cache)
                    .launch(Self::cfg(count)).map_err(e)?;
            }
        }
        Ok(())
    }

    /// `terminals_masked` for one part's terminals, in the same order:
    /// plain, blockers' heads-up, learned flop, multiway, blockers' rescale.
    fn lg_terminals(&mut self, chunk: &Chunk, p: i32, gate: i32) -> Result<(), String> {
        let nc = NUM_CLASSES;
        let (t0, tn) = (chunk.terms.0 as usize, chunk.terms.1 as usize);
        if tn == 0 { return Ok(()); }
        let terms = self.d_terms.slice(t0..t0 + tn);
        let tcount = tn as i32;
        let eq_slots = self.d_eq_slots.slice(chunk.eq.slots_at..chunk.eq.slots_at + chunk.eq.nblocks);
        let stride = (chunk.eq.union * nc) as u64;
        unsafe {
            self.stream.launch_builder(&self.f_terminal)
                .arg(&terms).arg(&tcount).arg(&p).arg(&self.np)
                .arg(&self.d_kind).arg(&self.d_live).arg(&self.d_winner)
                .arg(&self.d_potf).arg(&self.d_pots).arg(&self.d_inv).arg(&self.d_rw)
                .arg(&self.d_potg).arg(&self.d_calib).arg(&self.d_cbase)
                .arg(&self.clip_lo).arg(&self.clip_hi)
                .arg(&self.d_eq)
                .arg(&self.d_reach_src).arg(&self.d_reach).arg(&self.d_reach_mass)
                .arg(&eq_slots).arg(&self.d_eq_cache).arg(&self.use_eq_cache).arg(&stride)
                .arg(&self.use_multiway)
                .arg(&self.d_val_slot).arg(&mut self.d_val)
                .launch(Self::cfg(tn as u32)).map_err(e)?;
            if let Some(r) = &self.removal {
                let (h0, hn) = (chunk.hu.0 as usize, chunk.hu.1 as usize);
                if hn > 0 {
                    let hu = r.d_hu_terms.slice(h0..h0 + hn);
                    let count = hn as i32;
                    self.stream.launch_builder(&r.f_heads_up)
                        .arg(&hu).arg(&count).arg(&p).arg(&self.np)
                        .arg(&self.d_live).arg(&self.d_pots).arg(&self.d_inv).arg(&self.d_rw)
                        .arg(&self.d_potg).arg(&self.d_calib).arg(&self.d_cbase)
                        .arg(&self.clip_lo).arg(&self.clip_hi)
                        .arg(&r.d_eq_w)
                        .arg(&self.d_reach_src).arg(&self.d_reach).arg(&self.d_reach_mass).arg(&r.d_rank_mass)
                        .arg(&eq_slots).arg(&self.d_eq_cache).arg(&self.use_eq_cache).arg(&stride)
                        .arg(&self.d_val_slot).arg(&mut self.d_val)
                        .launch(LaunchConfig { grid_dim: (hn as u32, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 })
                        .map_err(e)?;
                }
            }
            let (l0, ln) = (chunk.leaf.0 as usize, chunk.leaf.1 as usize);
            if ln > 0 && self.leaf_nterms > 0 {
                let leaves = self.d_leaf_terms.slice(l0..l0 + ln);
                let seats = self.d_leaf_seats.slice(2 * l0..2 * (l0 + ln));
                let corr = self.d_leaf_corr.slice(l0 * 2 * nc..(l0 + ln) * 2 * nc);
                let count = ln as u32;
                self.stream.launch_builder(&self.f_leaf_terminal)
                    .arg(&leaves).arg(&count).arg(&p).arg(&self.np)
                    .arg(&seats).arg(&self.d_potg)
                    .arg(&self.d_reach_src).arg(&self.d_reach_mass).arg(&corr)
                    .arg(&self.d_val_slot).arg(&mut self.d_val)
                    .launch(LaunchConfig { grid_dim: (count, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 })
                    .map_err(e)?;
            }
        }
        self.lg_multiway(chunk, p, gate)?;
        if let Some(r) = &self.removal {
            let terms = self.d_terms.slice(t0..t0 + tn);
            unsafe {
                self.stream.launch_builder(&r.f_scale)
                    .arg(&terms).arg(&tcount).arg(&p).arg(&self.np)
                    .arg(&self.d_reach_src).arg(&self.d_reach).arg(&self.d_reach_mass).arg(&r.d_rank_mass)
                    .arg(&self.d_val_slot).arg(&mut self.d_val)
                    .launch(LaunchConfig { grid_dim: (tn as u32, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 })
                    .map_err(e)?;
            }
        }
        Ok(())
    }

    /// `multiway_terminals` (prepared, normalized path) for one part: its
    /// own CDF slots, built and read a sample batch at a time.
    fn lg_multiway(&mut self, chunk: &Chunk, p: i32, gate: i32) -> Result<(), String> {
        if self.use_multiway == 0 { return Ok(()); }
        let t = &chunk.mw;
        let (work_start, work_count) = t.spans[p as usize];
        let (m0, mn) = (chunk.mw_terms.0 as usize, chunk.mw_terms.1);
        if work_count == 0 || mn == 0 { return Ok(()); }
        let slot_count = t.union as u32;
        let compact = t.compact as i32;
        let work = self.d_mw_work.slice(t.work_at..t.work_at + t.work_len);
        let blocks = self.d_mw_blocks.slice(t.blocks_at..t.blocks_at + t.union);
        let slots = self.d_mw_slots.slice(t.slots_at..t.slots_at + t.nblocks);
        let map = if t.compact {
            self.d_mw_compact.slice(t.compact_at..t.compact_at + t.compact_len)
        } else {
            self.d_mw_compact.slice(0..1)
        };
        let terms = self.d_mw_terms.slice(m0..m0 + mn as usize);
        let samples = super::super::multiway::SAMPLES as u32;
        unsafe {
            if gate != 0 {
                self.stream.launch_builder(&self.f_multiway_clear_active)
                    .arg(&mut self.d_mw_active).arg(&slot_count)
                    .launch(LaunchConfig { grid_dim: (slot_count.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
            }
            self.stream.launch_builder(&self.f_multiway_prepare)
                .arg(&terms).arg(&mn).arg(&p).arg(&self.np)
                .arg(&self.d_live).arg(&self.d_reach_src).arg(&self.d_reach_mass)
                .arg(&slots).arg(&mut self.d_mw_active).arg(&mut self.d_mw_prob).arg(&gate)
                .launch(LaunchConfig { grid_dim: (mn.div_ceil(256), 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
            self.stream.launch_builder(&self.f_multiway_normalize)
                .arg(&work).arg(&work_start).arg(&blocks)
                .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate).arg(&compact)
                .arg(&mut self.d_mw_normalized)
                .launch(LaunchConfig { grid_dim: (work_count, 1, 1), block_dim: (192, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
            for sample_start in (0..samples).step_by(self.mw_batch as usize) {
                let sample_count = self.mw_batch.min(samples - sample_start);
                self.stream.launch_builder(&self.f_multiway_cdf)
                    .arg(&work).arg(&work_start).arg(&blocks)
                    .arg(&self.d_mw_order)
                    .arg(&self.d_mw_normalized)
                    .arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&gate).arg(&compact)
                    .arg(&mut self.d_mw_cdf).arg(&sample_start).arg(&sample_count).arg(&self.mw_batch)
                    .launch(LaunchConfig { grid_dim: (work_count, sample_count.div_ceil(4), 1), block_dim: (128, 1, 1), shared_mem_bytes: 0 }).map_err(e)?;
                self.stream.launch_builder(&self.f_multiway_terminal)
                    .arg(&terms).arg(&p).arg(&self.np)
                    .arg(&self.d_live).arg(&self.d_pots).arg(&self.d_inv)
                    .arg(&self.d_reach_src).arg(&self.d_mw_prob)
                    .arg(&slots).arg(&map).arg(&slot_count).arg(&compact).arg(&self.d_mw_cdf)
                    .arg(&self.d_mw_lower).arg(&self.d_mw_upper)
                    .arg(&sample_start).arg(&sample_count).arg(&self.mw_batch).arg(&samples)
                    .arg(&self.d_val_slot).arg(&mut self.d_val)
                    .launch(LaunchConfig { block_dim: (192, 1, 1), ..Self::cfg(mn) }).map_err(e)?;
            }
        }
        Ok(())
    }

    /// `up` for one level span.
    fn lg_up(&mut self, start: u32, count: u32, p: i32, mode: i32) -> Result<(), String> {
        if count == 0 { return Ok(()); }
        let (start, count) = (start as i32, count as i32);
        unsafe {
            self.stream.launch_builder(&self.f_up)
                .arg(&self.d_act_nodes).arg(&start).arg(&count)
                .arg(&p).arg(&self.np).arg(&mode)
                .arg(&self.d_actor).arg(&self.d_na).arg(&self.d_off).arg(&self.d_cstart).arg(&self.d_children)
                .arg(&self.d_src).arg(&self.d_foff).arg(&self.d_forced)
                .arg(&self.d_reach_src).arg(&self.d_reach)
                .arg(&mut self.d_regrets).arg(&mut self.d_strat)
                .arg(&self.d_val_slot).arg(&mut self.d_val)
                .launch(Self::cfg(count as u32)).map_err(e)?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests;
