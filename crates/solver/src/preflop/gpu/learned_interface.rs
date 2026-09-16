//! Offline chance/value interface. The two-player root uses an exact legal-pair
//! prior. Larger games reset that prior on first reaching two live seats; this
//! explicitly ignores folded-card bunching and is not exact multiplayer dealing.
use super::*;
use serde_json::{json, Value};

pub(super) struct Interface {
    prepare: CudaFunction, terminal: CudaFunction,
    entries: CudaSlice<u32>, seats: CudaSlice<i32>, context: CudaSlice<u32>,
    terms: CudaSlice<u32>, spr: CudaSlice<f64>, z: CudaSlice<f64>,
    contexts: u32, count: u32, learned: i32,
}
struct Plan { entries: Vec<u32>, seats: Vec<i32>, context: Vec<u32>, terms: Vec<u32>, spr: Vec<f64> }
impl Plan {
    fn build(s: &PreflopSolver) -> Self {
        let mut p=Self{entries:vec![],seats:vec![],context:vec![u32::MAX;s.nodes.len()],terms:vec![],spr:vec![0.;s.nodes.len()]};
        let order=s.postflop_order(); let mut stack=vec![(0usize,u32::MAX)];
        while let Some((i,mut ctx))=stack.pop(){let n=&s.nodes[i];
            if ctx==u32::MAX && n.live.count_ones()==2 {
                ctx=p.entries.len() as u32;p.entries.push(i as u32);
                p.seats.extend(order.iter().filter(|&&q|n.live&(1<<q)!=0).map(|&q|q as i32));
            }
            p.context[i]=ctx;
            if n.kind==KIND_ACTION {for a in (0..n.actions.len()).rev(){stack.push((s.child(i,a),ctx));}}
            else if ctx!=u32::MAX {
                p.terms.push(i as u32);
                if n.kind==KIND_POT_SHARE {p.spr[i]=(0..s.n).filter(|&q|n.live&(1<<q)!=0).map(|q|(s.cfg.stack-n.invested[q])/n.pot).fold(f64::INFINITY,f64::min).max(0.);}
            }
        } p
    }
    fn summary(&self)->Value{json!({"entries":self.entries,"seats":self.seats,"node_context":self.context,"paired_terminals":self.terms.len(),"contexts":self.entries.len(),"scope":"Legal pair prior anchored at heads-up entry; exact two-player chance, approximate chance reset in larger games. No folded-card bunching or full-game convergence guarantee."})}
}
impl PreflopGpu {
    pub fn seed_interface_sparse_fixture(s:&mut PreflopSolver)->Result<(),String>{
        if s.iteration!=0 || s.nodes.len()>20000 || !s.point_locks.is_empty(){return Err("fresh bounded test fixture required".into());}
        for (i,n) in s.nodes.iter().enumerate().filter(|(_,n)|n.kind==KIND_ACTION){
            let na=n.actions.len();let mut sigma=vec![0.;na*NUM_CLASSES];
            for h in 0..NUM_CLASSES {let a=if i==0 && na>2 {if h%2==0{0}else{na-1}}else{(h+i)%na};sigma[a*NUM_CLASSES+h]=1.;}
            s.point_locks.insert(i as u32,sigma);
        }Ok(())
    }
    pub fn learned_interface_plan(s:&PreflopSolver)->Value{Plan::build(s).summary()}
    pub fn enable_learned_interface_research(&mut self,s:&PreflopSolver,source:&str,learned:bool)->Result<Value,String>{
        if self.warmed || self.eval_warmed || self.interface.is_some() || self.learned.is_some()
            || s.cfg.realization!="balanced" || s.cfg.rake_pct!=0. || s.cfg.ante!=0.
            || self.research.is_some() || self.research_cohorts.is_some() || self.research_exact_reuse.is_some()
            || self.research_cv.is_some() || self.research_behavioral.is_some() || self.research_predictive.is_some()
            || self.research_rm_plus.is_some() || self.research_history_units.is_some() || self.research_root_ranges.is_some(){
            return Err("interface requires fresh ordinary Balanced GPU, zero rake/ante and no other research mode".into());
        }
        let p=Plan::build(s); if p.terms.is_empty(){return Err("no heads-up branches".into());}
        let (major,minor)=self._ctx.compute_capability().map_err(e)?;
        let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        let ptx=cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)?;
        let module=self._ctx.load_module(ptx).map_err(e)?;let summary=p.summary();
        self.interface=Some(Interface{prepare:module.load_function("interface_prepare").map_err(e)?,terminal:module.load_function("interface_terminal").map_err(e)?,
            contexts:p.entries.len() as u32,count:p.terms.len() as u32,learned:learned as i32,
            entries:self.stream.clone_htod(&p.entries).map_err(e)?,seats:self.stream.clone_htod(&p.seats).map_err(e)?,
            context:self.stream.clone_htod(&p.context).map_err(e)?,terms:self.stream.clone_htod(&p.terms).map_err(e)?,
            spr:self.stream.clone_htod(&p.spr).map_err(e)?,z:self.stream.alloc_zeros(p.entries.len()).map_err(e)?});
        Ok(summary)
    }
    pub(super) fn interface_prepare(&mut self)->Result<(),String>{
        let Some(i)=self.interface.as_mut() else{return Ok(());};
        unsafe{self.stream.launch_builder(&i.prepare).arg(&i.entries).arg(&i.seats).arg(&self.np)
            .arg(&self.d_reach_src).arg(&self.d_reach).arg(&self.d_reach_mass).arg(&mut i.z)
            .launch(LaunchConfig{grid_dim:(i.contexts,1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;}Ok(())
    }
    pub(super) fn interface_terminals(&mut self,p:i32)->Result<(),String>{
        let Some(i)=self.interface.as_ref() else{return Ok(());};
        if self.learned.is_some(){return Err("cannot combine learned interface with legacy learned hook".into());}
        unsafe{self.stream.launch_builder(&i.terminal).arg(&i.terms).arg(&i.context).arg(&i.seats).arg(&i.z)
            .arg(&p).arg(&self.np).arg(&i.learned).arg(&self.d_kind).arg(&self.d_winner).arg(&i.spr)
            .arg(&self.d_potg).arg(&self.d_inv).arg(&self.d_rw).arg(&self.d_reach_src)
            .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_eq).arg(&self.d_val_slot).arg(&mut self.d_val)
            .launch(LaunchConfig{grid_dim:(i.count,1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;}Ok(())
    }
}
