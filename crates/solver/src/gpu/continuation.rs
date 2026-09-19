//! Restricted, research-only continuation bridge for exact suit symmetries.
//! Keep the GPU private: asymmetric locks or imported policies would invalidate
//! the chance plan even if the next supplied root ranges were symmetric.
use super::GpuSolver;
use crate::{Algorithm, Solver, Spot, store::Store};
use std::sync::Arc;
use cudarc::driver::{CudaFunction, CudaModule, CudaSlice, PushKernelArg};

#[cfg(test)]
#[path = "continuation_replay_tests.rs"]
mod replay_tests;

#[cfg(test)]
#[path = "continuation_host_paging_tests.rs"]
mod host_paging_tests;

#[cfg(test)]
#[path = "continuation_ssd_paging_tests.rs"]
mod ssd_paging_tests;

pub struct SymmetricContinuationGpu {
    gpu: GpuSolver,
    spot: Arc<Spot>,
    future_card_orbits: bool,
    stabilizers: CudaSlice<u32>,
    project: CudaFunction,
    transport: CudaFunction,
    public_orbits: Option<(CudaSlice<u32>,CudaSlice<u32>)>,
    _projection_module: Arc<CudaModule>,
}

impl SymmetricContinuationGpu {
    pub fn new_with_budget(host: &Solver, budget: u64) -> Result<Self, String> {
        Self::build(host,budget,true)
    }

    /// Fully enumerated chance reference with the same internal policy tying.
    pub fn new_explicit_reference(host: &Solver, budget: u64) -> Result<Self, String> {
        Self::build(host,budget,false)
    }

    fn build(host: &Solver, budget: u64, future_card_orbits: bool) -> Result<Self, String> {
        if host.use_isomorphism != future_card_orbits || host.algo != Algorithm::CfrPlus
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
        // Canonical orbit reduction relies on a group, not a loose collection
        // of approximately weight-preserving permutations.
        for a in &host.spot.suit_perms {for b in &host.spot.suit_perms {
            let composed=std::array::from_fn(|i|a[b[i] as usize]);
            if !host.spot.suit_perms.contains(&composed) {return Err("suit permutations are not a closed group".into());}
        }}
        let metadata_bytes=host.spot.tree.nodes.len() as u64*if future_card_orbits {4} else {12};
        let gpu=GpuSolver::new_with_budget(host,budget.checked_sub(metadata_bytes)
            .ok_or("budget too small for symmetry metadata")?)?;
        let mut masks=vec![1u32;host.spot.tree.nodes.len()];
        let mut stack=vec![(0u32,crate::game::Dealt::default())];
        while let Some((i,d))=stack.pop() {
            let n=&host.spot.tree.nodes[i as usize];
            if n.kind==crate::tree::KIND_ACTION {
                masks[i as usize]=host.spot.perms_fixing(&d).iter().fold(0,|m,k|m|(1u32<<k));
                for a in 0..n.num_children as usize {stack.push((host.spot.tree.children[n.children_start as usize+a],d));}
            } else if n.kind==crate::tree::KIND_CHANCE {
                for c in 0..52u8 {
                    let child=host.spot.tree.children[n.children_start as usize+c as usize];
                    if child!=crate::tree::SENTINEL && !d.contains(c) {stack.push((child,d.push(c)));}
                }
            }
        }
        static PTX:std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>=std::sync::OnceLock::new();
        let (major,minor)=gpu._ctx.compute_capability().map_err(super::e)?;
        let ptx=PTX.get_or_init(|| {
            let arch=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
            cudarc::nvrtc::compile_ptx_with_opts(include_str!("continuation_projection.cu"),
                cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(super::e)
        }).clone()?;
        let module=gpu._ctx.load_module(ptx).map_err(super::e)?;
        let project=module.load_function("continuation_project").map_err(super::e)?;
        let transport=module.load_function("continuation_transport").map_err(super::e)?;
        let stabilizers=gpu.stream.clone_htod(&masks).map_err(super::e)?;
        let public_orbits=if future_card_orbits {None} else {
            let sp=&host.spot;let mut sources:Vec<u32>=(0..sp.tree.nodes.len() as u32).collect();
            let mut permutations=vec![0u32;sources.len()];
            for (k,pm) in sp.suit_perms.iter().enumerate() {
                let mut todo=vec![(0u32,0u32,crate::game::Dealt::default())];
                while let Some((i,j,d))=todo.pop() {
                    let n=&sp.tree.nodes[i as usize];let target=&sp.tree.nodes[j as usize];
                    if n.kind==crate::tree::KIND_ACTION {
                        if j<sources[i as usize] {sources[i as usize]=j;permutations[i as usize]=k as u32;}
                        for a in 0..n.num_children as usize {todo.push((sp.tree.children[n.children_start as usize+a],sp.tree.children[target.children_start as usize+a],d));}
                    } else if n.kind==crate::tree::KIND_CHANCE {
                        for c in 0..52u8 {
                            let child=sp.tree.children[n.children_start as usize+c as usize];
                            if child!=crate::tree::SENTINEL && !d.contains(c) {
                                let pc=crate::cards::permute_card(c,pm);
                                todo.push((child,sp.tree.children[target.children_start as usize+pc as usize],d.push(c)));
                            }
                        }
                    }
                }
            }
            if sources.iter().any(|&s|sources[s as usize]!=s) {return Err("public orbit sources are not canonical".into());}
            Some((gpu.stream.clone_htod(&sources).map_err(super::e)?,gpu.stream.clone_htod(&permutations).map_err(super::e)?))
        };
        Ok(Self {gpu,spot:host.spot.clone(),future_card_orbits,stabilizers,project,transport,public_orbits,_projection_module:module})
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
        let values=self.gpu.research_continuation_sweep_impl(p, t, own, opponent, true)?;
        self.project_player(p)?;
        self.transport_player(p)?;
        Ok(values)
    }

    fn transport_player(&mut self,p:usize)->Result<(),String> {
        let Some((sources,permutations))=&self.public_orbits else {return Ok(());};
        let count=self.gpu.d_action_nodes.len() as i32;
        if count==0 || self.spot.suit_perms.len()<2 {return Ok(());}
        unsafe {
            self.gpu.stream.launch_builder(&self.transport)
                .arg(&self.gpu.d_action_nodes).arg(&count)
                .arg(&self.gpu.d_node_player).arg(&self.gpu.d_node_na).arg(&self.gpu.d_node_data_off)
                .arg(sources).arg(permutations).arg(&self.gpu.d_hand_perm[p])
                .arg(&mut self.gpu.d_regrets[p]).arg(&mut self.gpu.d_strat[p])
                .arg(&self.gpu.nh[p]).arg(&(p as i32))
                .launch(GpuSolver::cfg(count as u32,0)).map_err(super::e)?;
        }
        Ok(())
    }

    fn project_player(&mut self,p:usize)->Result<(),String> {
        let count=self.gpu.d_action_nodes.len() as i32;
        if count==0 || self.spot.suit_perms.len()<2 {return Ok(());}
        for broadcast in [0i32,1] {
            unsafe {
                self.gpu.stream.launch_builder(&self.project)
                    .arg(&self.gpu.d_action_nodes).arg(&count)
                    .arg(&self.gpu.d_node_player).arg(&self.gpu.d_node_na).arg(&self.gpu.d_node_data_off)
                    .arg(&self.stabilizers).arg(&self.gpu.d_hand_perm[p])
                    .arg(&mut self.gpu.d_regrets[p]).arg(&mut self.gpu.d_strat[p])
                    .arg(&self.gpu.nh[p]).arg(&(p as i32)).arg(&broadcast)
                    .launch(GpuSolver::cfg(count as u32,0)).map_err(super::e)?;
            }
        }
        Ok(())
    }

    /// Synchronize and materialize orbit siblings for ordinary CPU evaluation.
    /// Do not use fixed-root normalization for externally reached game values.
    pub fn sync_to_cpu(&mut self, host: &mut Solver) -> Result<(), String> {
        if !Arc::ptr_eq(&self.spot, &host.spot) || host.use_isomorphism != self.future_card_orbits || !host.locks.is_empty() {
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{SpotConfig,TreeConfig,StreetSizing,parse_sizes};

    #[test]
    fn projection_matches_independent_cpu_group_average() {
      for board in ["KsQs2s3s", "KsQs2s"] {
        let z=StreetSizing {bet:parse_sizes("50").unwrap(),raise:vec![],donk:vec![]};
        let sp=Arc::new(Spot::new(SpotConfig {board:board.into(),
            range_oop:"AA,AKs,KQo,88,76s".into(),range_ip:"AA,QQ,AKo,QJs,99".into(),
            tree:TreeConfig {starting_pot:20.,effective_stack:40.,max_raises:0,
                oop:[z.clone(),z.clone(),z.clone()],ip:[z.clone(),z.clone(),z],..Default::default()}}).unwrap());
        let mut host=Solver::new(sp.clone());host.use_isomorphism=false;host.algo=Algorithm::CfrPlus;
        let mut g=SymmetricContinuationGpu::new_explicit_reference(&host,u64::MAX).unwrap();
        let originals:[Vec<f32>;4]=std::array::from_fn(|k|(0..sp.tree.data_size[k%2] as usize)
            .map(|i|((i*17+k*31)%101) as f32/50.-if k<2 {1.} else {0.}).collect());
        let mut expected=originals.clone();
        for p in 0..2 {
            g.gpu.stream.memcpy_htod(&originals[p],&mut g.gpu.d_regrets[p]).unwrap();
            g.gpu.stream.memcpy_htod(&originals[p+2],&mut g.gpu.d_strat[p]).unwrap();
        }
        let mut valid_actions=vec![];
        let mut todo=vec![(0u32,crate::game::Dealt::default())];
        while let Some((i,d))=todo.pop() {
            let n=&sp.tree.nodes[i as usize];
            if n.kind==crate::tree::KIND_ACTION {
                valid_actions.push(i);
                let p=n.player as usize;let nh=sp.hands[p].len();let group=sp.perms_fixing(&d);
                for a in 0..n.num_children as usize {for h in 0..nh {
                    let base=n.data_offset as usize+a*nh;
                    // Enumerate distinct orbit images, independently of the
                    // GPU's average over possibly repeated group elements.
                    let mut orbit:Vec<_>=group.iter().map(|&k|sp.hand_perm[p][k][h] as usize).collect();
                    orbit.sort_unstable();orbit.dedup();
                    for k in [p,p+2] {
                        expected[k][base+h]=(orbit.iter().map(|j|originals[k][base+j] as f64).sum::<f64>()/orbit.len() as f64) as f32;
                    }
                }}
                for a in 0..n.num_children as usize {todo.push((sp.tree.children[n.children_start as usize+a],d));}
            } else if n.kind==crate::tree::KIND_CHANCE {
                for c in 0..52u8 {
                    let child=sp.tree.children[n.children_start as usize+c as usize];
                    if child!=crate::tree::SENTINEL && !d.contains(c) {todo.push((child,d.push(c)));}
                }
            }
        }
        g.project_player(0).unwrap();g.project_player(1).unwrap();
        let mut worst=0f32;
        for p in 0..2 {for (k,buffer) in [(p,&g.gpu.d_regrets[p]),(p+2,&g.gpu.d_strat[p])] {
            let actual=g.gpu.stream.clone_dtoh(buffer).unwrap();
            for (a,b) in actual.iter().zip(&expected[k]) {worst=worst.max((a-b).abs());}
        }}
        println!("independent group projection max storage error={worst}");
        assert!(worst<0.000002);
        for p in 0..2 {
            if let Store::F32(a)=&mut host.regrets[p] {a.as_mut_slice().copy_from_slice(&expected[p]);} else {panic!();}
            if let Store::F32(a)=&mut host.strat[p] {a.as_mut_slice().copy_from_slice(&expected[p+2]);} else {panic!();}
        }
        // The CPU materializer recursively chooses public-card representatives;
        // the GPU implementation instead builds a direct root-group map.
        host.use_isomorphism=true;host.mark_sym_dirty();host.ensure_symmetric();
        g.transport_player(0).unwrap();g.transport_player(1).unwrap();
        let actual:[Vec<f32>;4]=std::array::from_fn(|k|g.gpu.stream.clone_dtoh(
            if k<2 {&g.gpu.d_regrets[k]} else {&g.gpu.d_strat[k-2]}).unwrap());
        let mut transport_error=0f32;
        for i in valid_actions {
            let n=&sp.tree.nodes[i as usize];let p=n.player as usize;
            let size=n.num_children as usize*sp.hands[p].len();let start=n.data_offset as usize;
            for (k,store) in [(p,&host.regrets[p]),(p+2,&host.strat[p])] {
                if let Store::F32(a)=store {
                    for j in start..start+size {transport_error=transport_error.max((actual[k][j]-a.as_slice()[j]).abs());}
                } else {panic!();}
            }
        }
        println!("{board} independent public transport max storage error={transport_error}");
        assert!(transport_error<0.000002);
      }
    }
}
