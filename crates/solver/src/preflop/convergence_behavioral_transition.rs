//! Bounded offline warm-start preparation; does not claim history equivalence.
use super::*;
use serde_json::{json,Value};
impl PreflopSolver {
    /// Call on a downloaded offline state before constructing a NEW native GPU
    /// engine. Retains regrets as an initializer and retains the global age.
    /// This is not a coordinate conversion of past behavioral-game regrets.
    pub fn research_reset_learning_averages(&mut self)->Result<Value,String>{
        if self.stop_requested() || self.iteration==0 || self.nodes.is_empty() || self.nodes.len()>50_000
            || !(2..=9).contains(&self.n) || self.seat_frozen.len()!=self.n || self.seat_profiles.len()!=self.n
            || self.arena_len.checked_mul(8).map_or(true,|bytes|bytes>256*1024*1024){
            return Err("bounded unstopped learned state required for offline average reset".into());
        }
        for nd in &self.nodes{if nd.kind==KIND_ACTION && (nd.actor as usize>=self.n || nd.actions.is_empty()
            || nd.actions.len().checked_mul(NUM_CLASSES).and_then(|len|nd.data_off.checked_add(len)).map_or(true,|end|end>self.arena_len)){
            return Err("invalid action arena geometry".into());
        }}
        let sums=unsafe{self.strat_sum.slice()};let regrets=unsafe{self.regrets.slice()};
        if regrets.iter().any(|v|!v.is_finite()) || sums.iter().any(|v|!v.is_finite() || *v<0.0){return Err("finite valid arenas required".into())}
        let ranges:Vec<_>=self.nodes.iter().enumerate().filter(|(i,nd)|nd.kind==KIND_ACTION
            && !self.seat_frozen[nd.actor as usize] && self.forced_sigma(*i).is_none())
            .map(|(_,nd)|nd.data_off..nd.data_off+nd.actions.len()*NUM_CLASSES).collect();
        if ranges.is_empty() || self.stop_requested(){return Err("uncanceled learning nodes required".into())}
        let entries:usize=ranges.iter().map(|r|r.len()).sum();let count=ranges.len();
        let sums=unsafe{self.strat_sum.slice_mut()};for range in ranges{sums[range].fill(0.0);}
        Ok(json!({"reset_learning_nodes":count,"reset_entries":entries,"iteration":self.iteration,
            "scope":"Offline native warm-start initializer; retained regrets are not transformed historical native regrets"}))
    }
}
