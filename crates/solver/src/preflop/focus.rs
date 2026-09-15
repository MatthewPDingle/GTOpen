//! Isolated, fresh conditional studies. Never patch their results into the parent.
use super::*;

pub const MAX_NODES: usize = 20_000;

#[derive(Serialize)]
pub struct FocusPlan {
    pub nodes: usize,
    pub source_iteration: u32,
    pub positions: Vec<String>,
    pub live: Vec<bool>,
    pub ranges: Vec<String>,
    pub branch_probability: f64,
    pub model: String,
    pub fixed_decisions: usize,
}

impl PreflopSolver {
    fn focus_nodes(&self, path: &[usize]) -> Result<Vec<usize>, String> {
        if path.is_empty() || path.len() > 64 {
            return Err("Select a decision after an action first".into());
        }
        let (root, _) = self.walk(path)?;
        if self.nodes[root].kind != KIND_ACTION {
            return Err("Select a player decision".into());
        }
        let mut pending = vec![root];
        let mut ids = Vec::new();
        while let Some(i) = pending.pop() {
            ids.push(i);
            if ids.len() > MAX_NODES {
                return Err("This branch exceeds the 20,000-node focused-study limit. Select a later decision.".into());
            }
            pending.extend(
                (0..self.nodes[i].actions.len())
                    .rev()
                    .map(|a| self.child(i, a)),
            );
        }
        Ok(ids)
    }

    pub fn focus_plan(&self, path: &[usize]) -> Result<FocusPlan, String> {
        let ids = self.focus_nodes(path)?;
        let (_, reaches) = self.walk(path)?;
        let root = &self.nodes[ids[0]];
        let ranges = reaches
            .iter()
            .map(|r| {
                let max = (0..NUM_CLASSES)
                    .map(|h| r[h] / class_prob(h))
                    .fold(0f32, f32::max);
                if max == 0.0 {
                    return String::new();
                }
                (0..NUM_CLASSES)
                    .filter_map(|h| {
                        let w = r[h] / class_prob(h) / max;
                        (w > 0.0).then(|| format!("{}:{:.8}", equity::class_label(h), w))
                    })
                    .collect::<Vec<_>>()
                    .join(", ")
            })
            .collect();
        Ok(FocusPlan {
            nodes: ids.len(),
            source_iteration: self.iteration,
            positions: self.cfg.positions.clone(),
            live: (0..self.n).map(|p| root.live & (1 << p) != 0).collect(),
            ranges,
            branch_probability: reaches
                .iter()
                .map(|r| r.iter().map(|&v| v as f64).sum::<f64>())
                .product(),
            model: self.multiway_equity_model().into(),
            fixed_decisions: ids
                .iter()
                .filter(|&&i| {
                    self.nodes[i].kind == KIND_ACTION
                        && (self.seat_frozen[self.nodes[i].actor as usize]
                            || self.forced_sigma(i).is_some())
                })
                .count(),
        })
    }

    pub fn focused(&self, path: &[usize], ranges: &[String]) -> Result<Self, String> {
        let ids = self.focus_nodes(path)?;
        let roots = parse_ranges(self.n, self.nodes[ids[0]].live, &self.cfg.positions, ranges)?;
        let map: std::collections::HashMap<_, _> =
            ids.iter().enumerate().map(|(i, &old)| (old, i)).collect();
        let mut nodes = Vec::new();
        let mut children = Vec::new();
        let mut len = 0;
        let mut locks = std::collections::HashMap::new();
        let mut frozen = vec![true; self.n];
        for (i, &old) in ids.iter().enumerate() {
            let mut nd = self.nodes[old].clone();
            nd.child_start = children.len() as u32;
            nd.data_off = len;
            children.extend((0..nd.actions.len()).map(|a| map[&self.child(old, a)] as u32));
            len += nd.actions.len() * NUM_CLASSES;
            if nd.kind == KIND_ACTION {
                if let Some(sigma) = self.forced_sigma(old) {
                    locks.insert(i as u32, sigma);
                } else if self.seat_frozen[nd.actor as usize] {
                    locks.insert(i as u32, self.average_strategy(old));
                } else {
                    frozen[nd.actor as usize] = false;
                }
            }
            nodes.push(nd);
        }
        if frozen.iter().all(|&x| x) {
            return Err("All decisions in this branch are fixed by models or locks".into());
        }
        Ok(Self {
            cfg: self.cfg.clone(),
            eq: self.eq.clone(),
            nodes,
            children,
            n: self.n,
            regrets: Arena::new(len),
            strat_sum: Arena::new(len),
            arena_len: len,
            iteration: 0,
            prune: false,
            fit: self.fit.clone(),
            seat_frozen: frozen,
            seat_profiles: vec![None; self.n],
            hero: None,
            pre_hero_frozen: None,
            hero_backup: None,
            point_locks: locks,
            realization_note: self.realization_note.clone(),
            multiway: self.multiway.clone(),
            stop_flag: None,
            conditional_roots: Some(roots),
            contextual_cache: Default::default(),
        })
    }

    pub fn set_focus_ranges(&mut self, ranges: &[String]) -> Result<(), String> {
        if self.conditional_roots.is_none() || self.iteration != 0 {
            return Err("Fresh focused study required".into());
        }
        let roots = parse_ranges(self.n, self.nodes[0].live, &self.cfg.positions, ranges)?;
        self.conditional_roots = Some(roots);
        Ok(())
    }
}

fn parse_ranges(
    n: usize,
    live: u32,
    positions: &[String],
    ranges: &[String],
) -> Result<Vec<Vec<f32>>, String> {
    if ranges.len() != n {
        return Err("Supply one incoming range per seat".into());
    }
    let mut roots = Vec::new();
    for (p, text) in ranges.iter().enumerate() {
        if live & (1 << p) == 0 {
            roots.push((0..NUM_CLASSES).map(class_prob).collect());
            continue;
        }
        let parsed = crate::range::Range::parse(text)?;
        let mut r = vec![0f32; NUM_CLASSES];
        for a in 0..52u8 {
            for b in a + 1..52u8 {
                let h = equity::class_index(
                    crate::cards::rank(a),
                    crate::cards::rank(b),
                    crate::cards::suit(a) == crate::cards::suit(b),
                );
                r[h] += parsed.weights[crate::cards::combo_index(a, b)];
            }
        }
        let mass: f64 = r.iter().map(|&x| x as f64).sum();
        if !mass.is_finite() || mass <= 0.0 {
            return Err(format!("{} needs a nonempty incoming range", positions[p]));
        }
        for v in &mut r {
            *v = (*v as f64 / mass) as f32;
        }
        roots.push(r);
    }
    Ok(roots)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture() -> PreflopSolver {
        static EQ: std::sync::OnceLock<Arc<EquityTable>> = std::sync::OnceLock::new();
        let eq = EQ.get_or_init(|| Arc::new(EquityTable::build(256))).clone();
        let cfg=serde_json::from_value(serde_json::json!({"positions":["UTG","UTG1","MP","HJ","CO","BTN","SB","BB"],
            "posts":[2,0,0,0,0,0,0.4,1],"utg_straddle":true,"stack":200,"limp":false,
            "open_raises":[6],"raise_mults":[],"max_raises":1,"add_allin":true,"rake_pct":5,"rake_cap":4.1,"realization":"raw"})).unwrap();
        let mut s = PreflopSolver::new(cfg, eq).unwrap();
        let mut policy = vec![0.; 3 * NUM_CLASSES];
        for h in 0..NUM_CLASSES {
            policy[h] = 1. - 1e-8;
            policy[2 * NUM_CLASSES + h] = 1e-8;
        }
        s.point_locks.insert(0, policy);
        s
    }
    #[test]
    fn rare_branch_warning_and_isolated_geometry() {
        let s = fixture();
        let path = vec![2, 0, 0, 0, 0, 0, 0];
        assert!(!s.node_view(&[]).unwrap().low_reach);
        let v = s.node_view(&path).unwrap();
        assert!(v.low_reach);
        assert!(v.branch_probability < 1e-7);
        assert_eq!(v.actor_pos.as_deref(), Some("UTG"));
        let plan = s.focus_plan(&path).unwrap();
        let mut ranges = plan.ranges;
        ranges[1] = "QQ".into();
        let mut f = s.focused(&path, &ranges).unwrap();
        assert_eq!(f.nodes.len(), 3);
        assert_eq!(f.nodes[0].pot, 203.4);
        assert_eq!(f.nodes[0].invested[0], 2.);
        assert_eq!(f.cfg.rake_cap, 4.1);
        assert!(f
            .root_reaches()
            .iter()
            .all(|r| (r.iter().sum::<f32>() - 1.).abs() < 1e-5));
        assert!(!f.node_view(&[]).unwrap().low_reach);
        for _ in 0..100 {
            f.iterate();
        }
        assert!(
            f.node_view(&[]).unwrap().strategy.unwrap()[NUM_CLASSES + 154] > 0.99,
            "KK should call versus QQ"
        );
        assert_eq!(s.iteration, 0);
        assert_eq!(s.node_view(&path).unwrap().strategy, v.strategy);
        assert!(f.save_game("unused-focus-save").is_err());
        assert!(s.focused(&path, &vec![String::new(); 8]).is_err());
        assert!(s.focus_plan(&[]).is_err());
        assert!(s.focus_plan(&[99]).is_err());
    }
    #[cfg(feature = "gpu")]
    #[test]
    fn focused_gpu_matches_cpu_with_nonuniform_roots() {
        let s = fixture();
        let path = vec![2, 0, 0, 0, 0, 0, 0];
        let mut ranges = s.focus_plan(&path).unwrap().ranges;
        ranges[1] = "QQ,JJ:0.5".into();
        ranges[0] = "KK,AA,AKs".into();
        let mut cpu = s.focused(&path, &ranges).unwrap();
        let mut device = s.focused(&path, &ranges).unwrap();
        let (mut g, _) = gpu::PreflopGpu::new_throughput(&device, 4096).unwrap();
        for _ in 0..100 {
            cpu.iterate();
            g.iterate(&mut device).unwrap();
        }
        let (gg, ge) = g.gaps_and_evs().unwrap();
        g.sync_to_cpu(&mut device).unwrap();
        let (cg, ce) = cpu.gaps_and_evs();
        for p in 0..8 {
            assert!((gg[p] - cg[p]).abs() < 0.003);
            assert!(
                (ge[p] - ce[p]).abs() < 0.003,
                "seat {p}: {} vs {}",
                ge[p],
                ce[p]
            );
        }
        assert!(device.node_view(&[]).unwrap().strategy.unwrap()[NUM_CLASSES + 154] > 0.99);
    }
}
