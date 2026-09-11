//! Bounded research initializer. Creates a new full-payoff solver, never resumes
//! approximate regrets or transfers approximate iteration/learning averages.
use super::*;
use serde_json::{json, Value};

impl PreflopSolver {
    /// Seed a fresh full-model regret policy from a completed preview average.
    /// Current non-HERO constraints are retained. HERO sessions and undo state
    /// are rejected rather than returning incomplete saveable session state.
    /// No app action or continuation of the input is implemented.
    pub fn research_full_policy_warmstart(&self, scale: f32) -> Result<(Self, Value), String> {
        self.research_policy_warmstart_bounded(scale, 20_000, 128 * 1024 * 1024, "small_cpu")
    }

    /// Separate large research gate; does not loosen the small CPU initializer.
    /// Caller owns GPU scheduling and external wall-clock limits.
    pub fn research_large_full_policy_warmstart(
        &self,
        scale: f32,
    ) -> Result<(Self, Value), String> {
        self.research_policy_warmstart_bounded(
            scale,
            2_000_000,
            3 * 1024 * 1024 * 1024,
            "large_gpu",
        )
    }

    fn research_policy_warmstart_bounded(
        &self,
        scale: f32,
        max_nodes: usize,
        max_arena_bytes: usize,
        scope: &str,
    ) -> Result<(Self, Value), String> {
        if ![0.01f32, 0.1, 1.0].contains(&scale) {
            return Err("research warmstart scale must be exactly0.01,0.1 or1".into());
        }
        if ![multiway::PREVIEW32_MODEL, multiway::PREVIEW64_MODEL]
            .contains(&self.multiway_equity_model())
            || self.iteration == 0
        {
            return Err("warmstart source must be a completed versioned preview model".into());
        }
        if self.hero.is_some() || self.pre_hero_frozen.is_some() || self.hero_backup.is_some() {
            return Err(
                "research warmstart does not support HERO sessions or HERO undo history".into(),
            );
        }
        if self.nodes.len() > max_nodes || self.arena_len.saturating_mul(8) > max_arena_bytes {
            return Err(format!(
                "{scope} warmstart exceeds {max_nodes} nodes or {max_arena_bytes} arena bytes"
            ));
        }
        if self.stop_requested() {
            return Err("warmstart source is canceled".into());
        }
        if self.cfg.realization == "calibrated" && self.fit.is_none() {
            return Err("warmstart requires the source calibrated realization fit".into());
        }
        // Check source sums only. Approximate regrets are neither read nor
        // copied, including any hero backup regret arena.
        unsafe {
            if self
                .strat_sum
                .slice()
                .iter()
                .any(|v| !v.is_finite() || *v < 0.0)
            {
                return Err("warmstart source has invalid average sums".into());
            }
        }
        let mut fresh = Self::new(self.cfg.clone(), self.eq.clone())?;
        if fresh.nodes.len() != self.nodes.len()
            || fresh.arena_len != self.arena_len
            || fresh.children != self.children
        {
            return Err("warmstart rebuild changed tree layout".into());
        }
        fresh.fit = self.fit.clone();
        fresh.realization_note = self.realization_note.clone();
        fresh.seat_profiles = self.seat_profiles.clone();
        fresh.seat_frozen = self.seat_frozen.clone();
        fresh.hero = self.hero;
        fresh.pre_hero_frozen = self.pre_hero_frozen.clone();
        fresh.point_locks = self.point_locks.clone();
        fresh.prune = self.prune;
        fresh.stop_flag = self.stop_flag.clone();
        let mut seeded_nodes = 0usize;
        let mut frozen_nodes = 0usize;
        let mut constrained_nodes = 0usize;
        for (node, nd) in self
            .nodes
            .iter()
            .enumerate()
            .filter(|(_, nd)| nd.kind == KIND_ACTION)
        {
            let n = &fresh.nodes[node];
            if n.data_off != nd.data_off
                || n.actor != nd.actor
                || n.actions.len() != nd.actions.len()
            {
                return Err(format!("warmstart action layout differs at node {node}"));
            }
            let span = nd.data_off..nd.data_off + nd.actions.len() * NUM_CLASSES;
            if self.seat_frozen[nd.actor as usize] {
                // Raw frozen averages preserve the actual fixed policy and its
                // floating-point normalization exactly. Frozen regrets stay0.
                unsafe {
                    fresh.strat_sum.slice_mut()[span.clone()]
                        .copy_from_slice(&self.strat_sum.slice()[span]);
                }
                frozen_nodes += 1;
                continue;
            }
            if fresh.forced_sigma(node).is_some() {
                constrained_nodes += 1;
                continue;
            }
            let policy = self.average_strategy(node);
            if policy.len() != nd.actions.len() * NUM_CLASSES
                || policy.iter().any(|v| !v.is_finite() || *v < 0.0)
            {
                return Err(format!("invalid source policy at node {node}"));
            }
            for h in 0..NUM_CLASSES {
                let mass: f32 = (0..nd.actions.len())
                    .map(|a| policy[a * NUM_CLASSES + h])
                    .sum();
                if !mass.is_finite() || (mass - 1.0).abs() > 1e-5 {
                    return Err(format!(
                        "unnormalized source policy at node {node}, hand {h}"
                    ));
                }
            }
            unsafe {
                for (to, p) in fresh.regrets.slice_mut()[span].iter_mut().zip(policy) {
                    *to = p * scale;
                }
            }
            seeded_nodes += 1;
        }
        if self.stop_requested() {
            return Err("warmstart canceled before return".into());
        }
        assert_eq!(fresh.iteration, 0);
        assert_eq!(fresh.multiway_equity_model(), multiway::MODEL);
        let provenance = json!({"initializer":"preview_average_to_fresh_full_regrets_v1",
            "research_scope":scope,"max_nodes":max_nodes,"max_arena_bytes":max_arena_bytes,
            "source_model":self.multiway_equity_model(),"source_iteration":self.iteration,
            "target_model":multiway::MODEL,"target_initial_iteration":0,"positive_regret_scale":scale,
            "source_regrets_copied":false,"source_learning_averages_copied":false,
            "learning_average_initialization":"zero","frozen_averages":"exact raw copy",
            "seeded_learning_nodes":seeded_nodes,"frozen_nodes":frozen_nodes,"forced_nodes":constrained_nodes,
            "current_constraints_preserved":true,"hero_undo_history_copied":false,"hero_sources_supported":false,
            "scope":"Research workspace from non-HERO source only. Evaluate against full reference after full-model iterations.",
            "initial_average_warning":"Before the first full iteration, unconstrained averages remain untrained; the seed is a current regret policy."});
        Ok((fresh, provenance))
    }

    /// Bounded research native-roundtrip check without allocating arena copies.
    pub fn research_warmstart_roundtrip_matches(&self, other: &Self) -> Result<bool, String> {
        for input in [self, other] {
            if input.nodes.len() > 2_000_000
                || input.arena_len.saturating_mul(8) > 3 * 1024 * 1024 * 1024
            {
                return Err("research roundtrip comparison exceeds large warmstart bounds".into());
            }
        }
        let metadata = |s: &Self| -> Value {
            json!({"config":s.cfg,"model":s.multiway_equity_model(),"iteration":s.iteration,
                "frozen":s.seat_frozen,"profiles":s.seat_profiles,"hero":s.hero,
                "pre_hero":s.pre_hero_frozen,"backup":s.hero_backup_meta()})
        };
        if metadata(self) != metadata(other)
            || self.point_locks != other.point_locks
            || self.arena_len != other.arena_len
            || self.nodes.len() != other.nodes.len()
            || self.children != other.children
            || !Arc::ptr_eq(&self.eq, &other.eq)
            || format!("{:?}", self.fit) != format!("{:?}", other.fit)
        {
            return Ok(false);
        }
        if self.hero_backup.is_some() || other.hero_backup.is_some() {
            return Ok(false);
        }
        unsafe {
            Ok(self
                .regrets
                .slice()
                .iter()
                .zip(other.regrets.slice())
                .all(|(a, b)| a.to_bits() == b.to_bits())
                && self
                    .strat_sum
                    .slice()
                    .iter()
                    .zip(other.strat_sum.slice())
                    .all(|(a, b)| a.to_bits() == b.to_bits()))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn warmstart_rejects_hero_and_undo_state_without_mutating_source() {
        let cfg = serde_json::from_value(
            json!({"positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":3,
            "limp":true,"open_raises":[2],"raise_mults":[3],"max_raises":1,"add_allin":false,
            "rake_pct":0,"rake_cap":0,"realization":"raw"}),
        )
        .unwrap();
        let mut source = PreflopSolver::new(cfg, Arc::new(equity::EquityTable::build(8))).unwrap();
        source
            .set_multiway_equity_model(multiway::PREVIEW32_MODEL)
            .unwrap();
        source.research_seed_quality_fixture_averages().unwrap();
        source.iteration = 50;
        let before = source.arena_snapshot();
        // Each field independently implies HERO session state. Also guard
        // older/partial headers with undo metadata but no active hero seat.
        for state in 0..3 {
            source.hero = (state == 0).then_some(0);
            source.pre_hero_frozen = (state == 1).then(|| vec![false; source.n]);
            source.hero_backup = (state == 2).then(|| HeroBackup {
                seat: 0,
                iteration: 17,
                regrets: vec![-123.0],
                sums: vec![7.0],
            });
            let frozen = source.seat_frozen.clone();
            let pre = source.pre_hero_frozen.clone();
            let backup = source.hero_backup.clone();
            let error = source
                .research_full_policy_warmstart(0.1)
                .err()
                .expect("HERO state must be rejected");
            assert!(error.contains("HERO"));
            assert_eq!(source.arena_snapshot(), before);
            assert_eq!(source.iteration, 50);
            assert_eq!(source.multiway_equity_model(), multiway::PREVIEW32_MODEL);
            assert_eq!(source.hero, (state == 0).then_some(0));
            assert_eq!(source.seat_frozen, frozen);
            assert_eq!(source.pre_hero_frozen, pre);
            match (&source.hero_backup, &backup) {
                (Some(a), Some(b)) => {
                    assert_eq!((a.seat, a.iteration), (b.seat, b.iteration));
                    assert_eq!(a.regrets, b.regrets);
                    assert_eq!(a.sums, b.sums);
                }
                (None, None) => {}
                _ => panic!("HERO backup changed"),
            }
        }
    }

    #[test]
    fn warmstart_resets_learning_state_and_retains_fixed_policies() {
        let cfg = serde_json::from_value(
            json!({"positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":3,
            "limp":true,"open_raises":[2],"raise_mults":[3],"max_raises":1,"add_allin":false,
            "rake_pct":0,"rake_cap":0,"realization":"raw"}),
        )
        .unwrap();
        let mut source = PreflopSolver::new(cfg, Arc::new(equity::EquityTable::build(8))).unwrap();
        source
            .set_multiway_equity_model(multiway::PREVIEW32_MODEL)
            .unwrap();
        source.research_seed_quality_fixture_averages().unwrap();
        source.seat_frozen[1] = true;
        source.iteration = 500;
        unsafe {
            source.regrets.slice_mut().fill(-123.0);
        }
        let root_na = source.nodes[0].actions.len();
        source
            .point_locks
            .insert(0, vec![1.0 / root_na as f32; root_na * NUM_CLASSES]);
        let before = source.arena_snapshot();
        for scale in [0.01f32, 0.1, 1.0] {
            let (fresh, metadata) = source.research_full_policy_warmstart(scale).unwrap();
            let (large, large_metadata) =
                source.research_large_full_policy_warmstart(scale).unwrap();
            assert!(fresh.research_warmstart_roundtrip_matches(&large).unwrap());
            assert_eq!(metadata["max_nodes"], 20_000);
            assert_eq!(large_metadata["max_nodes"], 2_000_000);
            assert_eq!(fresh.iteration, 0);
            assert_eq!(fresh.multiway_equity_model(), multiway::MODEL);
            assert_eq!(fresh.point_locks, source.point_locks);
            assert_eq!(fresh.seat_frozen, source.seat_frozen);
            assert_eq!(metadata["source_regrets_copied"], false);
            let mut checked = 0;
            for (node, nd) in source
                .nodes
                .iter()
                .enumerate()
                .filter(|(_, nd)| nd.kind == KIND_ACTION)
            {
                let span = nd.data_off..nd.data_off + nd.actions.len() * NUM_CLASSES;
                unsafe {
                    if source.seat_frozen[nd.actor as usize] {
                        assert_eq!(
                            fresh.strat_sum.slice()[span.clone()],
                            source.strat_sum.slice()[span.clone()]
                        );
                        assert!(fresh.regrets.slice()[span].iter().all(|v| *v == 0.0));
                    } else {
                        assert!(fresh.strat_sum.slice()[span.clone()]
                            .iter()
                            .all(|v| *v == 0.0));
                        if fresh.forced_sigma(node).is_some() {
                            assert!(fresh.regrets.slice()[span].iter().all(|v| *v == 0.0));
                        } else {
                            let policy = source.average_strategy(node);
                            for (r, p) in fresh.regrets.slice()[span].iter().zip(policy) {
                                assert_eq!(*r, p * scale);
                            }
                            checked += 1;
                        }
                    }
                }
            }
            assert!(checked > 0);
        }
        assert_eq!(before, source.arena_snapshot());
        for scale in [0.0, -1.0, f32::NAN, 0.2] {
            assert!(source.research_full_policy_warmstart(scale).is_err());
        }
        source.stop_flag = Some(Arc::new(AtomicBool::new(true)));
        assert!(source.research_full_policy_warmstart(0.1).is_err());
    }
}
