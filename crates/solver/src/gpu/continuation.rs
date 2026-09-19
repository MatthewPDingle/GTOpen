//! Restricted, research-only continuation bridge for exact suit symmetries.
//! Keep the GPU private: asymmetric locks or imported policies would invalidate
//! the chance plan even if the next supplied root ranges were symmetric.
use super::GpuSolver;
use crate::{Algorithm, Solver, Spot, store::Store};
use std::sync::Arc;

pub struct SymmetricContinuationGpu {
    gpu: GpuSolver,
    spot: Arc<Spot>,
}

impl SymmetricContinuationGpu {
    pub fn new_with_budget(host: &Solver, budget: u64) -> Result<Self, String> {
        if !host.use_isomorphism || host.algo != Algorithm::CfrPlus
            || host.iteration != 0 || !host.locks.is_empty() || host.preds.is_some()
        {
            return Err("symmetric continuation requires fresh unlocked CFR+ with isomorphism".into());
        }
        for store in host.regrets.iter().chain(&host.strat) {
            match store {
                Store::F32(a) if a.as_slice().iter().all(|&v| v == 0.) => {},
                _ => return Err("symmetric continuation requires zero F32 arenas".into()),
            }
        }
        Ok(Self { gpu: GpuSolver::new_with_budget(host, budget)?, spot: host.spot.clone() })
    }

    /// Raw CFVs before the traverser's update. The caller owns sweep order,
    /// iteration number, and chance/utility conventions, as in the plain bridge.
    pub fn sweep(&mut self, p: usize, t: u32, own: &[f32], opponent: &[f32]) -> Result<Vec<f32>, String> {
        if p > 1 || t == 0 { return Err("invalid continuation player or iteration".into()); }
        for (q, reach) in [(p, own), (1-p, opponent)] {
            if reach.len() != self.spot.hands[q].len()
                || reach.iter().any(|x| !x.is_finite() || *x < 0.)
            { return Err("invalid continuation reaches".into()); }
            for permutation in &self.spot.hand_perm[q] {
                if permutation.iter().enumerate().any(|(i, &j)| reach[i] != reach[j as usize]) {
                    return Err(format!("continuation reach for player {q} breaks suit symmetry"));
                }
            }
        }
        self.gpu.research_continuation_sweep_impl(p, t, own, opponent, true)
    }

    /// Synchronize and materialize orbit siblings for ordinary CPU evaluation.
    /// Do not use fixed-root normalization for externally reached game values.
    pub fn sync_to_cpu(&mut self, host: &mut Solver) -> Result<(), String> {
        if !Arc::ptr_eq(&self.spot, &host.spot) || !host.use_isomorphism || !host.locks.is_empty() {
            return Err("symmetric continuation sync requires original unlocked isomorphic spot".into());
        }
        self.gpu.sync_to_cpu(host)?;
        host.ensure_symmetric();
        Ok(())
    }

    /// Actual allocated device regret/average storage, excluding staging.
    pub fn arena_bytes(&self) -> u64 {
        self.gpu.d_regrets.iter().chain(&self.gpu.d_strat).map(|a| a.len() as u64 * 4).sum()
    }
}
