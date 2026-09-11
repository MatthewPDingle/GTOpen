//! Bounded development experiment only: conditional CPU refinement on an owned
//! snapshot. Small and large wrappers share tiny subtree caps and exact restore.
use super::*;
use serde_json::{json, Value};
use std::time::{Duration, Instant};

/// Bridge a local deadline and the caller's cancellation without ever clearing
/// or replacing the caller-owned atomic's value. Completion wakes the timer.
struct CancelBridge {
    previous: Option<Arc<AtomicBool>>,
    done: std::sync::mpsc::Sender<()>,
    worker: Option<std::thread::JoinHandle<()>>,
}

impl CancelBridge {
    fn install(s: &mut PreflopSolver, budget: Duration) -> Self {
        let previous = s.stop_flag.clone();
        let external = previous.clone();
        let local = Arc::new(AtomicBool::new(false));
        s.stop_flag = Some(local.clone());
        let (done, rx) = std::sync::mpsc::channel();
        let deadline = Instant::now() + budget;
        let worker = std::thread::spawn(move || loop {
            let now = Instant::now();
            if external.as_ref().is_some_and(|flag| flag.load(Ordering::Relaxed)) || now >= deadline {
                local.store(true, Ordering::Relaxed);
                break;
            }
            let wait = (deadline - now).min(Duration::from_millis(10));
            match rx.recv_timeout(wait) {
                Err(std::sync::mpsc::RecvTimeoutError::Timeout) => {},
                _ => break,
            }
        });
        Self { previous, done, worker: Some(worker) }
    }

    fn finish(mut self, s: &mut PreflopSolver) {
        let _ = self.done.send(());
        if let Some(worker) = self.worker.take() { let _ = worker.join(); }
        s.stop_flag = self.previous.take(); // Preserve a newly set external flag.
    }
}

impl Drop for CancelBridge {
    fn drop(&mut self) {
        let _ = self.done.send(());
        if let Some(worker) = self.worker.take() { let _ = worker.join(); }
    }
}

fn normalized(rows: &[Vec<f32>]) -> Result<(Vec<Vec<f32>>, Vec<f64>), String> {
    let mut out = Vec::new();
    let mut masses = Vec::new();
    for row in rows {
        if row.len() != NUM_CLASSES || row.iter().any(|x| !x.is_finite() || *x < 0.0) {
            return Err("invalid conditional reach row".into());
        }
        let mass: f64 = row.iter().map(|&x|x as f64).sum();
        if mass <= 0.0 || !mass.is_finite() { return Err("zero/invalid arriving mass; cannot invent a conditional range".into()); }
        out.push(row.iter().map(|&x|(x as f64/mass) as f32).collect());
        masses.push(mass);
    }
    Ok((out, masses))
}

fn descendants(s: &PreflopSolver, root: usize) -> Result<Vec<(usize, Vec<usize>)>, String> {
    let mut pending = vec![(root, vec![])];
    let mut result = Vec::new();
    let (mut actions, mut terminals) = (0,0);
    while let Some((id,path)) = pending.pop() {
        let node = &s.nodes[id];
        if node.kind == KIND_ACTION {
            actions += 1;
            for a in (0..node.actions.len()).rev() {
                let mut child_path=path.clone(); child_path.push(a);
                pending.push((s.child(id,a),child_path));
            }
        } else { terminals += 1; }
        if actions>500 || terminals>1000 { return Err("conditional subtree exceeds500 action/1000 terminal bound".into()); }
        result.push((id,path));
    }
    Ok(result)
}

fn metadata(s: &PreflopSolver) -> Value {
    let mut locks: Vec<_> = s.point_locks.iter().collect(); locks.sort_by_key(|(id,_)|**id);
    json!({"config":s.cfg,"profiles":s.seat_profiles,"frozen":s.seat_frozen,
        "hero":s.hero,"locks":locks,"model":s.multiway_equity_model(),"iteration":s.iteration,
        "equity_samples":s.eq.samples,"realization_fit":format!("{:?}",s.fit)})
}

fn bits_equal(a: &[f32], b: &[f32]) -> bool {
    a.len()==b.len() && a.iter().zip(b).all(|(x,y)|x.to_bits()==y.to_bits())
}

fn full_table_scope(s: &mut PreflopSolver, work: impl FnOnce(&mut PreflopSolver)->Result<Value,String>) -> Result<Value,String> {
    let original=s.multiway.clone();s.multiway=Some(multiway::CoupledDeck::shared());
    let outcome=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||work(s)));
    s.multiway=original;
    match outcome {Ok(result)=>result,Err(panic)=>std::panic::resume_unwind(panic)}
}

fn outside_equal(before: &[f32], after: &[f32], intervals: &[(usize,usize)]) -> bool {
    if before.len()!=after.len() {return false;}
    let mut start=0;
    for &(off,len) in intervals {
        if off<start || off.checked_add(len).is_none_or(|end|end>before.len()) {return false;}
        if !bits_equal(&before[start..off],&after[start..off]) {return false;}
        start=off+len;
    }
    bits_equal(&before[start..],&after[start..])
}

fn conditional_checkpoint(s: &PreflopSolver, node: usize, ranges: &[Vec<f32>], learners: &[bool]) -> Result<Value,String> {
    let mut gaps=vec![0.0;s.n]; let mut evs=vec![None;s.n];
    for p in 0..s.n {
        if !learners[p] {continue;}
        let mut r=ranges.to_vec();
        let value=s.traverse_checkpoint(node,p,&mut r,if s.constrained_br(p){3}else{2},
            CheckpointNeeds{br:true,avg:true},0).ok_or("conditional checkpoint canceled")?;
        let br=value.br.ok_or("missing BR")?; let avg=value.avg.ok_or("missing average")?;
        let mut ev = 0.0;
        for h in 0..NUM_CLASSES {
            gaps[p] += ranges[p][h] as f64*(br[h]-avg[h]) as f64;
            ev += ranges[p][h] as f64*avg[h] as f64;
        }
        evs[p] = Some(ev);
    }
    if gaps.iter().chain(evs.iter().flatten()).any(|x|!x.is_finite()) {return Err("nonfinite conditional values".into());}
    Ok(json!({"gaps_bb":gaps,"learning_gap_bb":gaps.iter().sum::<f64>(),"evs_bb":evs,
        "learning_seats":learners,"ev_evaluated_seats":learners}))
}

fn root_action_values(s: &PreflopSolver, node:usize, ranges:&[Vec<f32>]) -> Result<Vec<Vec<f32>>,String> {
    let actor=s.nodes[node].actor as usize;
    (0..s.nodes[node].actions.len()).map(|a| {
        let mut r=ranges.to_vec();
        // One forced action followed by the frozen source continuation. Own
        // reach is irrelevant to this actor's counterfactual terminal value.
        s.traverse_checkpoint(s.child(node,a),actor,&mut r,2,CheckpointNeeds{br:false,avg:true},0)
            .and_then(|v|v.avg).ok_or_else(||"source action-value audit canceled".into())
    }).collect()
}

fn action_loss(s:&PreflopSolver,node:usize,ranges:&[Vec<f32>],q:&[Vec<f32>])->Value {
    let actor=s.nodes[node].actor as usize; let sigma=s.average_strategy(node);
    let mut weighted=0.0; let mut worst_bad=0.0f64;
    for h in 0..NUM_CLASSES {
        let best=q.iter().map(|v|v[h]).fold(f32::NEG_INFINITY,f32::max);
        let loss: f64=q.iter().enumerate().map(|(a,v)|sigma[a*NUM_CLASSES+h] as f64*(best-v[h]) as f64).sum();
        let bad: f64=q.iter().enumerate().filter(|(_,v)|best-v[h]>0.1).map(|(a,_)|sigma[a*NUM_CLASSES+h] as f64).sum();
        weighted += ranges[actor][h] as f64*loss;
        if ranges[actor][h]>=0.0025 {worst_bad=worst_bad.max(bad);}
    }
    json!({"weighted_action_loss_bb":weighted,"worst_relevant_probability_losing_over_0_1bb":worst_bad,
        "scope":"One selected action followed by original source continuation, fixed normalized source ranges"})
}

/// Conservative output retention, not a changed convergence/quality gate.
/// Selection uses only same-game full-payoff gap. Fixed-source diagnostics are
/// preserved, but cannot veto a better equilibrium with changed continuation.
fn retention_decision(baseline:&Value,baseline_loss:&Value,candidate:Option<&Value>)->Value {
    let mut reasons=Vec::new();let mut comparisons=Vec::new();
    if let Some(candidate)=candidate {
        for (name,old,new) in [
            ("learning_gap_bb",&baseline["learning_gap_bb"],&candidate["conditional"]["learning_gap_bb"]),
            ("weighted_action_loss_bb",&baseline_loss["weighted_action_loss_bb"],&candidate["source_continuation_action_loss"]["weighted_action_loss_bb"]),
            ("worst_relevant_probability_losing_over_0_1bb",&baseline_loss["worst_relevant_probability_losing_over_0_1bb"],&candidate["source_continuation_action_loss"]["worst_relevant_probability_losing_over_0_1bb"]),
        ] {
            let before=old.as_f64().filter(|x|x.is_finite());let after=new.as_f64().filter(|x|x.is_finite());
            let no_worse=matches!((before,after),(Some(a),Some(b)) if b<=a);
            let selects=name=="learning_gap_bb";
            let improves=matches!((before,after),(Some(a),Some(b)) if b<a);
            if selects && !improves {reasons.push("full-payoff conditional gap did not strictly improve or is unavailable/nonfinite".into());}
            comparisons.push(json!({"metric":name,"baseline":old,"candidate":new,"no_worse":no_worse,"used_for_retention":selects}));
        }
    } else {reasons.push("no completed candidate checkpoint".into());}
    json!({"retain_candidate":reasons.is_empty(),"reasons":reasons,"comparisons":comparisons,
        "rule":"Retain last completed finite candidate only if same full-payoff conditional-game summed gap strictly improves; ties keep exact baseline policy",
        "retention_scope":"conditional self-game only",
        "quality_qualified":false,"original_quality_gates_unchanged":true,
        "limitation":"Fixed-source action-loss/tail failures remain separate and are not retention criteria; all original quality gates remain required for promotion; no whole-game or prefix quality claim"})
}

fn conditional_policies(s:&PreflopSolver,nodes:&[(usize,Vec<usize>)])->Vec<Value> {
    nodes.iter().filter(|(id,_)|s.nodes[*id].kind==KIND_ACTION).map(|(id,relative)| {
        json!({"source_node":id,"relative_path":relative,"actor":s.nodes[*id].actor,
            "actions":s.nodes[*id].actions,"policy":s.average_strategy(*id),
            "forced_or_frozen":s.seat_frozen[s.nodes[*id].actor as usize] || s.forced_sigma(*id).is_some()})
    }).collect()
}

impl PreflopSolver {
    /// Development only, not an app operation. Mutates an owned snapshot during
    /// the bounded experiment and restores it before returning success/error.
    pub fn research_refine_conditional(&mut self,path:&[usize],seconds:u64,max_iterations:u32)->Result<Value,String> {
        self.refine_conditional_bounded(path,seconds,max_iterations,20_000,128*1024*1024,"small",None)
    }

    /// Separate research scope: a large owned source, still a tiny selected
    /// subtree. One complete backup; no second/third whole-arena audit copies.
    pub fn research_refine_conditional_large(&mut self,path:&[usize],seconds:u64,max_iterations:u32)->Result<Value,String> {
        self.refine_conditional_bounded(path,seconds,max_iterations,2_000_000,3*1024*1024*1024,"large",None)
    }

    /// Explicit research-only hybrid: freeze preview prefix ranges, evaluate
    /// and learn the selected continuation with full payoffs, restore source.
    pub fn research_refine_conditional_preview_full_large(&mut self,path:&[usize],seconds:u64,max_iterations:u32)->Result<Value,String> {
        let started=Instant::now();
        if ![multiway::PREVIEW64_MODEL,multiway::PREVIEW32_MODEL,multiway::PREVIEW128_MODEL].contains(&self.multiway_equity_model())
            || self.iteration==0 || self.stop_requested() || seconds==0 || seconds>120
            || ![2,10,30,100].contains(&max_iterations) || path.len()>64
            || self.nodes.len()>2_000_000 || self.arena_len.saturating_mul(8)>3*1024*1024*1024 {
            return Err("requires bounded completed preview source and valid research budget".into());
        }
        let source_metadata=metadata(self);let source_model=self.multiway_equity_model();
        let source_view=self.node_view(path)?;
        if source_view.kind!="action" || source_view.history.iter().any(|h|h.strategy_note.is_some()) {
            return Err("preview prefix has terminal/unlearned/unsupported decision".into());
        }
        // Capture all seats, including folded chance factors, BEFORE switching.
        let(root,frozen_reaches)=self.walk(path)?;let(ranges,_)=normalized(&frozen_reaches)?;
        let nodes=descendants(self,root)?;let mut learners=vec![false;self.n];
        for (id,_) in nodes {let nd=&self.nodes[id];
            if nd.kind==KIND_ACTION && !self.seat_frozen[nd.actor as usize] && self.forced_sigma(id).is_none() {
                learners[nd.actor as usize]=true;
            }
        }
        if !learners.iter().any(|x|*x) {return Err("selected subtree has no learning decisions".into());}
        let cancellation=CancelBridge::install(self,Duration::from_secs(seconds));
        let baseline=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||conditional_checkpoint(self,root,&ranges,&learners)));
        cancellation.finish(self);
        let baseline=match baseline {Ok(result)=>result?,Err(panic)=>std::panic::resume_unwind(panic)};
        let source_baseline_seconds=started.elapsed().as_secs_f64();
        let remaining=seconds.saturating_sub(started.elapsed().as_secs());
        if remaining==0 {return Err("budget exhausted evaluating source-model baseline".into());}
        let result=full_table_scope(self,|s|s.refine_conditional_bounded(path,remaining,max_iterations,
            2_000_000,3*1024*1024*1024,"large_preview_prefix_full_local",Some(&frozen_reaches)));
        if metadata(self)!=source_metadata {return Err("preview source metadata restoration failed".into());}
        result.map(|mut row| {
            row["full_evaluation_metadata"]=row["source_metadata"].clone();
            row["source_metadata"]=source_metadata;row["source_model"]=json!(source_model);
            row["baseline_source_model_conditional"]=baseline;
            row["baseline_full_model_conditional"]=row["baseline_conditional"].clone();
            row["prefix_unvalidated"]=json!(true);row["prefix_captured_before_model_switch"]=json!(true);
            row["source_model_restored_exact"]=json!(true);row["source_baseline_seconds"]=json!(source_baseline_seconds);
            row["total_hybrid_method_seconds"]=json!(started.elapsed().as_secs_f64());
            row["scope"]=json!("Full-reference local continuation conditional on unvalidated preview-source prefix ranges; no full-game convergence or quality claim");row
        })
    }

    /// Read-only structural/support inspection. No values, learning, policy
    /// probabilities or gap outcomes are evaluated before path registration.
    pub fn research_inspect_conditional_large(&self,paths:&[Vec<usize>])->Result<Value,String> {
        if self.nodes.len()>2_000_000 || self.arena_len.saturating_mul(8)>3*1024*1024*1024 || paths.is_empty() || paths.len()>3 {
            return Err("large inspection requires <=2Mnodes/3GiBarenas and1..3 registered paths".into());
        }
        let mut rows=Vec::new();
        for path in paths {
            let row=(||->Result<Value,String>{
                if path.len()>64 {return Err("path too long".into());}
                let view=self.node_view(path)?;let(root,raw)=self.walk(path)?;
                if view.kind!="action" {return Err("selected path is terminal".into());}
                let support=normalized(&raw).is_ok() && view.history.iter().all(|h|h.strategy_note.is_none());
                let sub=descendants(self,root)?;
                let action_nodes=sub.iter().filter(|(id,_)|self.nodes[*id].kind==KIND_ACTION).count();
                Ok(json!({"path":path,"source_node":root,"actor":view.actor_pos,"pot":view.pot,
                    "live_positions":view.positions.iter().zip(&view.live).filter(|(_,live)|**live).map(|(p,_)|p).collect::<Vec<_>>(),
                    "actions":self.nodes[root].actions,"has_positive_learned_prefix_support":support,
                    "action_nodes":action_nodes,"terminal_nodes":sub.len()-action_nodes,
                    "source_action_labels":view.history.iter().filter_map(|h|h.chosen.map(|a|h.actions[a].label.clone())).collect::<Vec<_>>() }))
            })();
            rows.push(match row {Ok(row)=>row,Err(error)=>json!({"path":path,"error":error})});
        }
        Ok(json!({"inspection_only":true,"source_iteration":self.iteration,"source_model":self.multiway_equity_model(),
            "source_nodes":self.nodes.len(),"arena_bytes":self.arena_len*8,"config":self.cfg,"paths":rows,
            "quality_values_evaluated":false}))
    }

    fn refine_conditional_bounded(&mut self,path:&[usize],seconds:u64,max_iterations:u32,max_nodes:usize,max_bytes:usize,scope:&str,frozen_prefix:Option<&[Vec<f32>]>)->Result<Value,String> {
        let preparation_started=Instant::now();
        if seconds==0 || seconds>120 || ![2,10,30,100].contains(&max_iterations) || path.len()>64
            || self.nodes.len()>max_nodes || self.arena_len.saturating_mul(8)>max_bytes {
            return Err(format!("requires <=120seconds,2/10/30/100iterations, <={max_nodes}nodes/{max_bytes}arena bytes"));
        }
        if self.multiway_equity_model()!=multiway::MODEL || self.iteration==0 || self.stop_requested() {
            return Err("requires a completed full-reference source snapshot".into());
        }
        let view=self.node_view(path)?;
        if view.kind!="action" || view.history.iter().any(|h|h.strategy_note.is_some()) {
            return Err("selected branch is terminal, unreachable or has an unlearned ancestor".into());
        }
        let (root,walked_ranges)=self.walk(path)?;
        let raw_ranges=if let Some(frozen)=frozen_prefix {
            if frozen.len()!=walked_ranges.len() || !frozen.iter().zip(&walked_ranges).all(|(a,b)|bits_equal(a,b)) {
                return Err("model switch changed frozen prefix probabilities".into());
            }
            frozen.to_vec()
        } else {walked_ranges};
        let (ranges,masses)=normalized(&raw_ranges)?;
        let nodes=descendants(self,root)?;
        let writable:Vec<_>=nodes.iter().filter_map(|(id,_)| {
            let nd=&self.nodes[*id];
            (nd.kind==KIND_ACTION && !self.seat_frozen[nd.actor as usize] && self.forced_sigma(*id).is_none())
                .then_some((*id,nd.data_off,nd.actions.len()*NUM_CLASSES))
        }).collect();
        let mut learners=vec![false;self.n];
        for &(id,_,_) in &writable {learners[self.nodes[id].actor as usize]=true;}
        if !learners.iter().any(|x|*x) {return Err("selected subtree contains no learning decisions".into());}
        let mut intervals:Vec<_>=writable.iter().map(|&(_,off,len)|(off,len)).collect();intervals.sort_unstable();
        let mut end=0;
        for &(off,len) in &intervals {
            if off<end || off.checked_add(len).is_none_or(|x|x>self.arena_len) {return Err("overlapping/invalid local arena interval".into());}
            end=off+len;
        }
        let backup_started=Instant::now();let original=self.arena_snapshot();let backup_seconds=backup_started.elapsed().as_secs_f64();
        let before_meta=metadata(self);let preparation_seconds=preparation_started.elapsed().as_secs_f64();
        let old_iteration=self.iteration; let old_prune=self.prune;
        let cancellation=CancelBridge::install(self,Duration::from_secs(seconds));
        let started=Instant::now();
        let outcome=std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| ->Result<Value,String> {
            let baseline=conditional_checkpoint(self,root,&ranges,&learners)?;
            let q=root_action_values(self,root,&ranges)?;
            let source_action_loss=action_loss(self,root,&ranges,&q);
            let baseline_policies=conditional_policies(self,&nodes);
            self.iteration=0; self.prune=false; // Explicit full local traversal; independent discount clock.
            unsafe {for &(_,off,len) in &writable {
                self.regrets.slice_mut()[off..off+len].fill(0.0);
                self.strat_sum.slice_mut()[off..off+len].fill(0.0);
            }}
            let mut checkpoints=Vec::new(); let mut policies=Vec::new(); let mut published=0;
            let mut canceled=false;
            for iteration in 1..=max_iterations {
                for p in 0..self.n {
                    if !learners[p] {continue;}
                    if self.stop_requested() {canceled=true;break;}
                    self.traverse(root,p,&mut ranges.clone(),0,0);
                }
                if canceled || self.stop_requested() {canceled=true;break;}
                self.iteration=iteration;
                let t=iteration as f64;
                let pos=(t.powf(DCFR_ALPHA)/(t.powf(DCFR_ALPHA)+1.0)) as f32;
                let sd=((t/(t+1.0)).powf(DCFR_GAMMA)) as f32;
                unsafe {for &(_,off,len) in &writable {
                    for r in &mut self.regrets.slice_mut()[off..off+len] {*r *= if *r>0.0 {pos}else{0.5};}
                    for v in &mut self.strat_sum.slice_mut()[off..off+len] {*v *= sd;}
                }}
                if [2,10,30,100].contains(&iteration) {
                    let check=match conditional_checkpoint(self,root,&ranges,&learners) {
                        Ok(check)=>check, Err(_) if self.stop_requested()=>{canceled=true;break;}, Err(e)=>return Err(e)
                    };
                    checkpoints.push(json!({"iteration":iteration,"seconds":started.elapsed().as_secs_f64(),
                        "conditional":check,"source_continuation_action_loss":action_loss(self,root,&ranges,&q)}));
                    policies=conditional_policies(self,&nodes);
                    published=iteration;
                }
            }
            let audit_started=Instant::now();
            if !outside_equal(&original.0,unsafe {self.regrets.slice()},&intervals)
                || !outside_equal(&original.1,unsafe {self.strat_sum.slice()},&intervals) {
                return Err("outside/forced/frozen arena changed".into());
            }
            let outside_audit_seconds=audit_started.elapsed().as_secs_f64();
            let retention=retention_decision(&baseline,&source_action_loss,checkpoints.last());
            let retain_candidate=retention["retain_candidate"]==true;
            let retained_policies=if retain_candidate {policies.clone()} else {baseline_policies};
            let retained_conditional=if retain_candidate {checkpoints.last().unwrap()["conditional"].clone()} else {baseline.clone()};
            let retained_action_loss=if retain_candidate {checkpoints.last().unwrap()["source_continuation_action_loss"].clone()} else {source_action_loss.clone()};
            Ok(json!({"development_only":true,"path":path,"source_node":root,"source_iteration":old_iteration,
                "source_model":multiway::MODEL,"conditional_model":multiway::MODEL,"source_metadata":before_meta,
                "original_reaches":raw_ranges,"normalized_reaches":ranges,"source_seat_masses":masses,
                "conditioning":"Every original seat normalized, including folded chance factors; independent-class model",
                "source_actions":view.history,"descendant_nodes":nodes.len(),"writable_action_nodes":writable.len(),
                "baseline_conditional":baseline,"baseline_source_action_loss":source_action_loss,
                "checkpoints":checkpoints,"published_local_iteration":published,"has_completed_learned_snapshot":published>=2,"quality_qualified":false,
                "canceled":canceled,"seconds":started.elapsed().as_secs_f64(),"policies":policies,
                "policies_role":"Unfiltered last completed candidate, retained for research evidence; use retained_policies for the safeguarded output",
                "retention":retention,"retained_policies":retained_policies,
                "retained_policy_source":if retain_candidate {"last_completed_refinement"} else {"full_evaluated_source_baseline"},
                "retained_local_iteration":if retain_candidate {published} else {0},
                "retained_conditional":retained_conditional,"retained_source_action_loss":retained_action_loss,
                "outside_forced_frozen_arenas_exact":true,"parent_global_convergence_claim":false,
                "source_scope":scope,"source_nodes":self.nodes.len(),"backup_bytes":self.arena_len*8,
                "backup_seconds":backup_seconds,"preparation_seconds":preparation_seconds,"outside_audit_seconds":outside_audit_seconds,
                "scope":"Conditional CPU development experiment; no native save or parent merge; early ranges remain approximate"}))
        }));
        cancellation.finish(self);
        let restore_started=Instant::now();
        unsafe {self.regrets.slice_mut().copy_from_slice(&original.0);self.strat_sum.slice_mut().copy_from_slice(&original.1);}
        self.iteration=old_iteration;self.prune=old_prune;
        let restore_seconds=restore_started.elapsed().as_secs_f64();let audit_started=Instant::now();
        if metadata(self)!=before_meta || !bits_equal(unsafe {self.regrets.slice()},&original.0)
            || !bits_equal(unsafe {self.strat_sum.slice()},&original.1) {return Err("source restore verification failed".into());}
        let restore_audit_seconds=audit_started.elapsed().as_secs_f64();
        match outcome {
            Ok(result)=>result.map(|mut value| {value["source_restored_exact"]=json!(true);
                value["restore_seconds"]=json!(restore_seconds);value["restore_audit_seconds"]=json!(restore_audit_seconds);
                value["total_method_seconds"]=json!(preparation_started.elapsed().as_secs_f64());value}),
            Err(panic)=>std::panic::resume_unwind(panic),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn retention_keeps_better_baseline_without_reclassifying_gate_failures() {
        let baseline=json!({"learning_gap_bb":0.0002749});
        let loss=json!({"weighted_action_loss_bb":0.03,"worst_relevant_probability_losing_over_0_1bb":0.4});
        let mut candidate=json!({"conditional":{"learning_gap_bb":0.0009287},"source_continuation_action_loss":loss});
        let decision=retention_decision(&baseline,&loss,Some(&candidate));
        assert_eq!(decision["retain_candidate"],false);assert_eq!(decision["quality_qualified"],false);
        assert_eq!(decision["original_quality_gates_unchanged"],true);
        candidate["conditional"]["learning_gap_bb"]=json!(0.0001);
        assert_eq!(retention_decision(&baseline,&loss,Some(&candidate))["retain_candidate"],true);
        candidate["source_continuation_action_loss"]["worst_relevant_probability_losing_over_0_1bb"]=json!(0.5);
        assert_eq!(retention_decision(&baseline,&loss,Some(&candidate))["retain_candidate"],true);
        candidate["conditional"]["learning_gap_bb"]=baseline["learning_gap_bb"].clone();
        assert_eq!(retention_decision(&baseline,&loss,Some(&candidate))["retain_candidate"],false);
        assert_eq!(retention_decision(&baseline,&loss,None)["retain_candidate"],false);
        candidate["conditional"]["learning_gap_bb"]=Value::Null;
        assert_eq!(retention_decision(&baseline,&loss,Some(&candidate))["retain_candidate"],false);
    }
    #[test] fn preview_full_scope_restores_arc_on_error_and_panic() {
        let mut s=fixture();s.multiway=Some(multiway::CoupledDeck::preview64());let original=s.multiway.clone().unwrap();
        assert!(full_table_scope(&mut s,|_|Err("expected".into())).is_err());
        assert!(Arc::ptr_eq(s.multiway.as_ref().unwrap(),&original));
        let panic=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||full_table_scope(&mut s,|_|panic!("expected"))));
        assert!(panic.is_err());assert!(Arc::ptr_eq(s.multiway.as_ref().unwrap(),&original));
    }
    #[test] fn preview_prefix_full_local_preserves_source_and_frozen_prefix() {
        let mut s=fixture();s.multiway=Some(multiway::CoupledDeck::preview64());s.seat_frozen[2]=true;
        let before=s.arena_snapshot();let meta=metadata(&s);let original=s.multiway.clone().unwrap();
        let prefix=s.walk(&[0]).unwrap().1;
        let row=s.research_refine_conditional_preview_full_large(&[0],120,2).unwrap();
        assert_eq!(row["original_reaches"],json!(prefix));assert_eq!(row["source_model"],multiway::PREVIEW64_MODEL);
        assert_eq!(row["conditional_model"],multiway::MODEL);assert_eq!(row["quality_qualified"],false);
        assert_eq!(row["source_model_restored_exact"],true);assert_eq!(row["prefix_unvalidated"],true);
        assert_eq!(row["retention"]["comparisons"][0]["baseline"],row["baseline_full_model_conditional"]["learning_gap_bb"]);
        if row["retained_policy_source"]=="full_evaluated_source_baseline" {
            for policy in row["retained_policies"].as_array().unwrap() {
                let id=policy["source_node"].as_u64().unwrap() as usize;
                assert_eq!(policy["policy"],json!(s.average_strategy(id)));
            }
        }
        assert_eq!(s.arena_snapshot(),before);assert_eq!(metadata(&s),meta);
        assert!(Arc::ptr_eq(s.multiway.as_ref().unwrap(),&original));
        assert!(s.research_refine_conditional_preview_full_large(&[usize::MAX],120,2).is_err());
        assert_eq!(s.arena_snapshot(),before);assert_eq!(metadata(&s),meta);
    }
    #[test] fn interval_audit_ignores_only_disjoint_writable_blocks() {
        let original=vec![0.0,1.0,2.0,3.0,4.0];let mut changed=original.clone();changed[2]=8.0;
        assert!(outside_equal(&original,&changed,&[(2,1)]));
        changed[4]=-0.0;assert!(!outside_equal(&original,&changed,&[(2,1)]));
        assert!(!outside_equal(&original,&original,&[(2,2),(3,1)]));
        assert!(!outside_equal(&original,&original,&[(usize::MAX,1)]));
        assert!(!bits_equal(&[0.0],&[-0.0]));
        assert!(bits_equal(&[f32::from_bits(0x7fc00001)],&[f32::from_bits(0x7fc00001)]));
    }
    #[test] fn large_inspector_is_read_only_and_large_wrapper_restores_source() {
        let mut s=fixture();let before=s.arena_snapshot();let meta=metadata(&s);
        let inspection=s.research_inspect_conditional_large(&[vec![0]]).unwrap();
        assert_eq!(inspection["quality_values_evaluated"],false);
        assert!(inspection["paths"][0]["action_nodes"].as_u64().unwrap()>0);
        assert_eq!(s.arena_snapshot(),before);assert_eq!(metadata(&s),meta);
        let result=s.research_refine_conditional_large(&[0],120,2).unwrap();
        assert_eq!(result["source_scope"],"large");assert_eq!(result["source_restored_exact"],true);
        assert_eq!(result["backup_bytes"],json!(s.arena_len*8));
        assert_eq!(s.arena_snapshot(),before);assert_eq!(metadata(&s),meta);
    }
    fn fixture()->PreflopSolver {
        static EQ:std::sync::OnceLock<Arc<equity::EquityTable>>=std::sync::OnceLock::new();
        let cfg=serde_json::from_value(json!({"positions":["BTN","SB","BB"],"posts":[0,0.5,1],"stack":3,
            "limp":true,"open_raises":[2],"raise_mults":[3],"max_raises":1,"add_allin":false,
            "rake_pct":5,"rake_cap":1,"realization":"raw"})).unwrap();
        let mut s=PreflopSolver::new(cfg,EQ.get_or_init(||Arc::new(equity::EquityTable::build(4))).clone()).unwrap();
        s.research_seed_quality_fixture_averages().unwrap();s.iteration=1;s
    }
    #[test] fn conditional_normalization_preserves_support_and_positive_scale() {
        let mut row=vec![0.0;NUM_CLASSES];row[2]=0.125;row[8]=0.375;
        let a=normalized(&[row.clone(),row.iter().map(|x|x*0.25).collect()]).unwrap().0;
        let b=normalized(&[row.iter().map(|x|x*8.0).collect(),row.clone()]).unwrap().0;
        assert_eq!(a,b);assert_eq!(a[0][0],0.0);assert_eq!(a[0][2],0.25);
        assert!(normalized(&[vec![0.0;NUM_CLASSES]]).is_err());
        row[0]=f32::NAN;assert!(normalized(&[row]).is_err());
    }
    #[test] fn conditional_zero_update_matches_dividing_history_mass() {
        let s=fixture();let path=[0];let (node,raw)=s.walk(&path).unwrap();
        let (norm,_)=normalized(&raw).unwrap();
        for p in 0..s.n {
            let a=s.traverse_checkpoint(node,p,&mut raw.clone(),2,CheckpointNeeds{br:false,avg:true},0).unwrap().avg.unwrap();
            let b=s.traverse_checkpoint(node,p,&mut norm.clone(),2,CheckpointNeeds{br:false,avg:true},0).unwrap().avg.unwrap();
            let mass:f64=raw.iter().enumerate().filter(|(q,_)|*q!=p).map(|(_,r)|r.iter().sum::<f32>() as f64).product();
            for h in 0..NUM_CLASSES {assert!((a[h] as f64/mass-b[h] as f64).abs()<2e-5);}
        }
    }
    #[test] fn conditional_refinement_restores_source_and_preserves_frozen_lock_blocks() {
        let mut s=fixture();s.seat_frozen[2]=true;s.lock_point(&[],None).unwrap();s.lock_point(&[1],None).unwrap();
        let before=s.arena_snapshot();let meta=metadata(&s);
        let result=s.research_refine_conditional(&[1],120,2).unwrap();
        assert_eq!(result["source_restored_exact"],true);assert_eq!(result["outside_forced_frozen_arenas_exact"],true);
        assert_eq!(result["published_local_iteration"],2);assert_eq!(s.arena_snapshot(),before);assert_eq!(metadata(&s),meta);
        for p in result["policies"].as_array().unwrap() {
            let id=p["source_node"].as_u64().unwrap() as usize;
            if p["forced_or_frozen"].as_bool().unwrap() {assert_eq!(p["policy"],json!(s.average_strategy(id)));}
        }
        assert!(s.research_refine_conditional(&[usize::MAX],120,2).is_err());
        assert_eq!(s.arena_snapshot(),before);
    }
    #[test] fn cancellation_bridge_propagates_and_restores_new_external_cancel() {
        let mut s=fixture();let original=Arc::new(AtomicBool::new(false));s.set_stop_flag(Some(original.clone()));
        let bridge=CancelBridge::install(&mut s,Duration::from_secs(30));
        let local=s.stop_flag.clone().unwrap();
        assert!(!Arc::ptr_eq(&local,&original));
        original.store(true,Ordering::Relaxed);
        let start=Instant::now();
        while !local.load(Ordering::Relaxed) && start.elapsed()<Duration::from_secs(1) {std::thread::sleep(Duration::from_millis(1));}
        assert!(local.load(Ordering::Relaxed));
        bridge.finish(&mut s);
        assert!(Arc::ptr_eq(s.stop_flag.as_ref().unwrap(),&original));
        assert!(original.load(Ordering::Relaxed));assert!(s.stop_requested());
    }
    #[test] fn cancellation_bridge_deadline_and_completion_restore_absent_flag() {
        let mut s=fixture();
        let bridge=CancelBridge::install(&mut s,Duration::from_millis(10));
        let local=s.stop_flag.clone().unwrap();let start=Instant::now();
        while !local.load(Ordering::Relaxed) && start.elapsed()<Duration::from_secs(1) {std::thread::sleep(Duration::from_millis(1));}
        assert!(local.load(Ordering::Relaxed));bridge.finish(&mut s);assert!(s.stop_flag.is_none());
        let bridge=CancelBridge::install(&mut s,Duration::from_secs(30));
        let start=Instant::now();bridge.finish(&mut s);
        assert!(start.elapsed()<Duration::from_secs(1));assert!(s.stop_flag.is_none());
    }
    #[test] fn conditional_checkpoint_reports_unmeasured_evs_as_null() {
        let s=fixture();let ranges=s.root_reaches();
        let check=conditional_checkpoint(&s,0,&ranges,&[true,false,false]).unwrap();
        assert!(check["evs_bb"][0].is_number());
        assert!(check["evs_bb"][1].is_null());assert!(check["evs_bb"][2].is_null());
        assert_eq!(check["ev_evaluated_seats"],json!([true,false,false]));
    }
}
