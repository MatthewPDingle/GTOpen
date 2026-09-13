//! C07: immutable average-check CDF sharing, never used for learning.
use super::*;
use serde_json::json;

pub(super) struct Plan {
    pub capacity:usize, pub peak_bytes:usize, pub total_bytes:usize,
    pub original_cdf_bytes:usize, pub base_bytes:usize,
    pub groups:Vec<Vec<i32>>, pub masks:Vec<usize>, pub spans:Vec<(u32,u32)>,
    pub work:Vec<u32>, pub maps:Vec<u32>, pub extra_bytes:usize,
}
fn partitions(mask:usize)->Vec<Vec<usize>> {
    if mask==0{return vec![vec![]];}
    let first=1<<mask.trailing_zeros();let rest=mask^first;let mut sub=rest;let mut out=Vec::new();
    loop {
        if sub.count_ones()<3 {for mut tail in partitions(rest^sub) {tail.insert(0,first|sub);out.push(tail);}}
        if sub==0{break;}sub=(sub-1)&rest;
    }out
}
impl Plan {
    pub fn build(np:usize,mw:&EquityCachePlan,old_capacity:usize,base_bytes:usize,value_bytes:usize,prob_bytes:usize,budget_mb:u64)->Result<Self,String> {
        if !(2..=9).contains(&np) || mw.blocks.is_empty() || old_capacity==0 {return Err("invalid cohort topology".into());}
        let budget=(budget_mb.min(20_500) as u128)*1_000_000;
        let mut membership=vec![0usize;mw.blocks.len()];
        for p in 0..np {let (start,count)=mw.spans[p];
            for &slot in &mw.work[start as usize..(start+count) as usize] {membership[slot as usize]|=1<<p;}
        }
        let mut hist=vec![0usize;1<<np];for &m in &membership {if m!=0{hist[m]+=1;}}
        let unions:Vec<usize>=(0..1<<np).map(|s|hist.iter().enumerate().filter(|(m,_)|m&s!=0).map(|(_,v)|v).sum()).collect();
        let mut best=None;
        for masks in partitions((1<<np)-1) {
            let largest=masks.iter().map(|m|m.count_ones() as usize).max().unwrap();
            let cap=old_capacity.max(masks.iter().map(|&m|unions[m]).max().unwrap());
            let table=cap.checked_mul(2).and_then(|x|x.checked_next_power_of_two()).ok_or("cohort table overflow")?;
            let rows=masks.iter().map(|&m|unions[m]).sum::<usize>();
            let cdf=(cap as u128)*32*170*4;let norm=(cap as u128)*169*4;
            let scratch=(cap as u128+table as u128)*4;
            let maps=masks.len() as u128*mw.blocks.len() as u128*4;let work=rows as u128*4;
            let extra=(largest as u128-1)*(value_bytes as u128+prob_bytes as u128)+maps+work+scratch;
            let old=(old_capacity as u128)*(32*170+169)*4;
            let total=(base_bytes as u128).checked_sub(old).ok_or("cohort base budget inconsistent")?+cdf+norm+extra;
            let peak=total+256*1024*1024;
            if peak>budget || peak>usize::MAX as u128 || cap>u32::MAX as usize {continue;}
            let key=(rows,total,serde_json::to_string(&masks).unwrap());
            if best.as_ref().map_or(true,|(old_key,_,_,_,_)|key<*old_key) {
                best=Some((key,masks,cap,total as usize,extra as usize));
            }
        }
        let (_,masks,capacity,total_bytes,extra_bytes)=best.ok_or("no cohort plan fits the unchanged-cache budget")?;
        let groups=masks.iter().map(|m|(0..np).filter(|p|m&(1<<p)!=0).map(|p|p as i32).collect()).collect();
        let mut work=Vec::new();let mut spans=Vec::new();let mut maps=vec![u32::MAX;masks.len()*mw.blocks.len()];
        for (group,&mask) in masks.iter().enumerate() {
            let start=u32::try_from(work.len()).map_err(|_|"cohort work offset overflow")?;
            for (slot,&members) in membership.iter().enumerate() {if members&mask!=0 {
                maps[group*mw.blocks.len()+slot]=u32::try_from(work.len()-start as usize).map_err(|_|"cohort map overflow")?;
                work.push(slot as u32);
            }}
            spans.push((start,u32::try_from(work.len()-start as usize).map_err(|_|"cohort count overflow")?));
        }
        Ok(Self{capacity,peak_bytes:total_bytes+256*1024*1024,total_bytes,original_cdf_bytes:old_capacity*32*170*4,
            base_bytes,groups,masks,spans,work,maps,extra_bytes})
    }
    pub fn report(&self)->serde_json::Value {
        json!({"group_masks":self.masks,"groups":self.groups,"capacity":self.capacity,"total_bytes":self.total_bytes,
            "peak_bytes":self.peak_bytes,"base_bytes":self.base_bytes,"extra_bytes":self.extra_bytes,
            "original_cdf_bytes":self.original_cdf_bytes,"static_rows":self.work.len()})
    }
}
pub(super) struct CohortReuse {
    pub plan:Plan, work:CudaSlice<u32>,maps:CudaSlice<u32>,
    values:Vec<CudaSlice<f32>>,prob:Vec<CudaSlice<f32>>,pub(super) terminal:CudaFunction,
    #[cfg(all(test, feature = "preflop-research"))]
    audit_terminals:bool,
    #[cfg(all(test, feature = "preflop-research"))]
    terminal_audits:Vec<(i32,Vec<u32>)>,
}
pub(super) fn kernel_source(unrolled:bool)->Result<String,String> {
    let base=include_str!("../kernels.cu");
    let original=base.split("extern \"C\" __global__ void pf_multiway_terminal(").nth(1).ok_or("cohort terminal source")?
        .split("// Minimum-memory compatibility entry:").next().ok_or("cohort terminal end")?;
    let terminal=format!("extern \"C\" __global__ void pf_cohort_terminal({original}")
        .replace("float* val)","float* val, const u32* aliases)")
        .replace("compact_slots[(size_t)p * union_slots + global_slot]","compact_slots[global_slot]")
        .replace("                // Cast before multiplying:","                cdf_slot = aliases[cdf_slot];\n                // Cast before multiplying:");
    if !terminal.contains("const u32* aliases)") || !terminal.contains("compact_slots[global_slot]") || !terminal.contains("cdf_slot = aliases[cdf_slot]") {
        return Err("cohort source rewrite invariant".into());
    }
    let base=super::terminal_unroll::source(base,unrolled)?;
    Ok([base.as_str(),&terminal].join("\n"))
}
impl CohortReuse {
    pub fn allocate_variant(g:&PreflopGpu,plan:Plan,unrolled:bool,narrow:bool)->Result<Self,String> {
        if narrow {super::narrow_offsets::check_elements(g.d_mw_cdf.len())?;}
        let source=kernel_source(unrolled)?;
        let source=if narrow {super::narrow_offsets::source(&source,true)?}else{source};
        let (major,minor)=g._ctx.compute_capability().map_err(e)?;
        let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        static PTX:[std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>;4]=[std::sync::OnceLock::new(),std::sync::OnceLock::new(),std::sync::OnceLock::new(),std::sync::OnceLock::new()];
        let ptx=PTX[2*unrolled as usize+narrow as usize].get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(source,
            cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
        let module=g._ctx.load_module(ptx).map_err(e)?;
        let terminal=module.load_function("pf_cohort_terminal").map_err(e)?;
        let work=g.stream.clone_htod(&plan.work).map_err(e)?;let maps=g.stream.clone_htod(&plan.maps).map_err(e)?;
        let mut values=Vec::new();let mut prob=Vec::new();
        for _ in 1..plan.groups.iter().map(|s|s.len()).max().unwrap() {
            values.push(g.stream.alloc_zeros::<f32>(g.d_val.len()).map_err(e)?);
            #[cfg(all(test, feature = "preflop-research"))]
            super::adaptive_throughput::allocation_recovery::after_partial_allocation(g,work.len(),maps.len(),values.len(),narrow)?;
            prob.push(g.stream.alloc_zeros::<f32>(g.d_mw_prob.len()).map_err(e)?);
        }
        let r=g.research_exact_reuse.as_ref().ok_or("cohort requires exact reuse")?;
        let extra=(work.len()+maps.len()+r.table.len()+r.aliases.len()+values.iter().map(|v|v.len()).sum::<usize>()+prob.iter().map(|v|v.len()).sum::<usize>())*4;
        if extra!=plan.extra_bytes || g.d_mw_cdf.len()*4!=plan.capacity*32*170*4 {return Err("cohort allocation differs from plan".into());}
        println!("COHORT_PLAN {}",plan.report());
        Ok(Self{plan,work,maps,values,prob,terminal,
            #[cfg(all(test, feature = "preflop-research"))] audit_terminals:false,
            #[cfg(all(test, feature = "preflop-research"))] terminal_audits:Vec::new()})
    }
}
impl PreflopGpu {
    fn with_cohort_buffer(&mut self,values:&mut [CudaSlice<f32>],probs:&mut [CudaSlice<f32>],index:usize,
        f:impl FnOnce(&mut Self)->Result<(),String>)->Result<(),String> {
        if index>0 {std::mem::swap(&mut self.d_val,&mut values[index-1]);std::mem::swap(&mut self.d_mw_prob,&mut probs[index-1]);}
        let result=f(self);
        // Restore pointer identity on every normal/error path, also during capture.
        if index>0 {std::mem::swap(&mut self.d_val,&mut values[index-1]);std::mem::swap(&mut self.d_mw_prob,&mut probs[index-1]);}
        result
    }
    pub(super) fn queue_cohort_evaluation(&mut self)->Result<(),String> {
        let mut c=self.research_cohorts.take().ok_or("cohorts disabled")?;
        let result=(|| {
            if !self.exact_reuse_compatible() {return Err("cohorts require unchanged native evaluation".into());}
            #[cfg(feature = "preflop-research")]
            if self.research_samples!=super::super::multiway::SAMPLES as u32 {
                return Err("cohorts require unchanged native evaluation".into());
            }
            let mut order:Vec<_>=(0..c.plan.groups.len()).collect();
            order.sort_by_key(|&group|c.plan.groups[group].contains(&(self.np-1)));
            for &group in &order {
                let players=&c.plan.groups[group];
                for (index,&p) in players.iter().enumerate() {
                    self.with_cohort_buffer(&mut c.values,&mut c.prob,index,|g| {
                        g.ordinary_terminals(p)?;
                        #[cfg(all(test, feature = "preflop-research"))]
                        g.phase_mark("prepare",p)?;
                        unsafe {g.stream.launch_builder(&g.f_multiway_prepare)
                            .arg(&g.d_mw_terms).arg(&g.mw_nterms).arg(&p).arg(&g.np).arg(&g.d_live)
                            .arg(&g.d_reach_src).arg(&g.d_reach_mass).arg(&g.d_mw_slots)
                            .arg(&mut g.d_mw_active).arg(&mut g.d_mw_prob).arg(&0i32)
                            .launch(LaunchConfig{grid_dim:(g.mw_nterms.div_ceil(256),1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;}
                        Ok(())
                    })?;
                }
                let (start,count)=c.plan.spans[group];
                if count>0 {
                    let r=self.research_exact_reuse.as_mut().ok_or("cohort reuse missing")?;
                    let table_count=r.table.len() as u32;let mask=table_count-1;
                    unsafe {
                        #[cfg(all(test, feature = "preflop-research"))]
                        super::PhaseEventTrace::mark(&mut self.phase_trace,&self.stream,"normalize",group as i32)?;
                        self.stream.launch_builder(&self.f_multiway_normalize).arg(&c.work).arg(&start).arg(&self.d_mw_blocks)
                            .arg(&self.d_reach).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&0i32).arg(&1i32)
                            .arg(&mut self.d_mw_normalized).launch(LaunchConfig{grid_dim:(count,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).map_err(e)?;
                        #[cfg(all(test, feature = "preflop-research"))]
                        super::PhaseEventTrace::mark(&mut self.phase_trace,&self.stream,"classify",group as i32)?;
                        self.stream.launch_builder(&self.f_multiway_clear_active).arg(&mut r.table).arg(&table_count)
                            .launch(LaunchConfig{grid_dim:(table_count.div_ceil(256),1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(e)?;
                        self.stream.launch_builder(&r.classify).arg(&c.work).arg(&start).arg(&self.d_mw_blocks).arg(&self.d_reach_mass)
                            .arg(&self.d_mw_active).arg(&0i32).arg(&self.d_mw_normalized).arg(&mut r.table).arg(&mask).arg(&mut r.aliases)
                            .launch(LaunchConfig{grid_dim:(count,1,1),block_dim:(32,1,1),shared_mem_bytes:0}).map_err(e)?;
                    }
                    let samples=super::super::multiway::SAMPLES as u32;
                    let map=c.maps.slice(group*self.mw_union_slots as usize..(group+1)*self.mw_union_slots as usize);
                    for sample_start in (0..samples).step_by(self.mw_batch as usize) {
                        let sample_count=self.mw_batch.min(samples-sample_start);
                        let r=self.research_exact_reuse.as_ref().unwrap();
                        #[cfg(all(test, feature = "preflop-research"))]
                        super::PhaseEventTrace::mark(&mut self.phase_trace,&self.stream,"cdf",group as i32)?;
                        unsafe {self.stream.launch_builder(&r.cdf).arg(&c.work).arg(&start).arg(&self.d_mw_blocks).arg(&self.d_mw_order)
                            .arg(&self.d_mw_normalized).arg(&self.d_reach_mass).arg(&self.d_mw_active).arg(&0i32).arg(&1i32)
                            .arg(&mut self.d_mw_cdf).arg(&sample_start).arg(&sample_count).arg(&self.mw_batch).arg(&r.aliases)
                            .launch(LaunchConfig{grid_dim:(count,sample_count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).map_err(e)?;}
                        for (index,&p) in players.iter().enumerate() {
                            self.with_cohort_buffer(&mut c.values,&mut c.prob,index,|g| {
                                #[cfg(all(test, feature = "preflop-research"))]
                                g.phase_mark("coupled_terminals",p)?;
                                let r=g.research_exact_reuse.as_ref().unwrap();
                                unsafe {g.stream.launch_builder(&c.terminal).arg(&g.d_mw_terms).arg(&p).arg(&g.np).arg(&g.d_live)
                                    .arg(&g.d_pots).arg(&g.d_inv).arg(&g.d_reach_src).arg(&g.d_mw_prob).arg(&g.d_mw_slots).arg(&map)
                                    .arg(&g.mw_union_slots).arg(&1i32).arg(&g.d_mw_cdf).arg(&g.d_mw_lower).arg(&g.d_mw_upper)
                                    .arg(&sample_start).arg(&sample_count).arg(&g.mw_batch).arg(&samples).arg(&g.d_val_slot)
                                    .arg(&mut g.d_val).arg(&r.aliases).launch(LaunchConfig{block_dim:(192,1,1),..Self::cfg(g.mw_nterms)}).map_err(e)?;}
                                Ok(())
                            })?;
                        }
                    }
                }
                for (index,&p) in players.iter().enumerate() {
                    self.with_cohort_buffer(&mut c.values,&mut c.prob,index,|g| {
                        #[cfg(all(test, feature = "preflop-research"))]
                        if c.audit_terminals {
                            let slots=g.stream.clone_dtoh(&g.d_val_slot).map_err(e)?;
                            let terms=g.stream.clone_dtoh(&g.d_terms).map_err(e)?;
                            let values=g.stream.clone_dtoh(&g.d_val).map_err(e)?;
                            c.terminal_audits.push((p,terms.iter().flat_map(|nd|{
                                let start=slots[*nd as usize] as usize*NUM_CLASSES;
                                values[start..start+NUM_CLASSES].iter().map(|x|x.to_bits())
                            }).collect()));
                        }
                        for (slot,mode) in [if g.constrained_br[p as usize]{3}else{2},1].into_iter().enumerate() {
                            g.up(p,mode)?;
                            #[cfg(all(test, feature = "preflop-research"))]
                            g.phase_mark("root_copy",p)?;
                            let off=(2*p as usize+slot)*NUM_CLASSES;
                            let root=g.d_val.slice(0..NUM_CLASSES);let mut dst=g.d_eval_roots.slice_mut(off..off+NUM_CLASSES);
                            g.stream.memcpy_dtod(&root,&mut dst).map_err(e)?;
                        }Ok(())
                    })?;
                }
            }
            // Preserve the original final scratch contents as well as pointer
            // identity: queue_evaluation leaves the final player's values here.
            let last=c.plan.groups[*order.last().unwrap()].len()-1;
            if last>0 {
                #[cfg(all(test, feature = "preflop-research"))]
                self.phase_mark("scratch_restore",self.np-1)?;
                self.stream.memcpy_dtod(&c.values[last-1],&mut self.d_val).map_err(e)?;
            }
            Ok(())
        })();
        self.research_cohorts=Some(c);result
    }
}

#[cfg(all(test, feature = "preflop-research"))]
mod tests;
