//! C18 standalone qualification; no production constructor selects this helper.
use super::*;
use super::super::multiway::{CoupledDeck,SAMPLES};
use std::collections::BTreeMap;
use serde_json::json;

struct RankMaps {lower:Vec<u32>,upper:Vec<u32>,hand:Vec<u32>,count:Vec<u32>}
impl RankMaps {
    fn new(deck:&CoupledDeck)->Self {
        let mut out=Self{lower:vec![0;SAMPLES*169],upper:vec![0;SAMPLES*169],hand:vec![0;SAMPLES*169],count:vec![0;SAMPLES]};
        for s in 0..SAMPLES {
            let base=s*169;let mut groups=BTreeMap::new();
            for h in 0..169 {groups.insert((deck.lower[base+h],deck.upper[base+h]),0u32);}
            for (i,(&(lo,hi),id)) in groups.iter_mut().enumerate() {
                *id=i as u32;out.lower[base+i]=lo;out.upper[base+i]=hi;
            }
            out.count[s]=groups.len() as u32;
            for h in 0..169 {out.hand[base+h]=groups[&(deck.lower[base+h],deck.upper[base+h])];}
        }
        out
    }
}

fn table(kind:usize)->CoupledDeck {
    let mut d=CoupledDeck{order:vec![0;SAMPLES*169],lower:vec![0;SAMPLES*169],upper:vec![0;SAMPLES*169]};
    for s in 0..SAMPLES {
        let mut lo=0;
        while lo<169 {
            let size=match kind {0=>169,1=>1,2=>if lo==30{5}else{1},_=>1+(lo*7+s*3)%19};
            let hi=(lo+size).min(169);
            for rank in lo..hi {
                let h=(rank*37+s*11)%169;d.order[s*169+rank]=h as u32;
                d.lower[s*169+h]=lo as u32;d.upper[s*169+h]=hi as u32;
            }
            lo=hi;
        }
    }
    d
}

#[test]
fn compact_products_preserve_hand_histories() {
    let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();
    let (major,minor)=ctx.compute_capability().unwrap();
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let dir=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_RANK_DIAGNOSTICS").unwrap());
    assert!(!dir.exists());std::fs::create_dir_all(&dir).unwrap();
    let base=narrow_offsets::source(&cohort_reuse::kernel_source(true).unwrap(),true).unwrap();
    let begin=base.find("template<int Q, int O>").unwrap();
    let end=base[begin..].find("extern \"C\" __global__ void pf_multiway_terminal(").unwrap()+begin;
    let original=base[begin..end].to_string();
    assert_eq!(original.matches("float sum = 0.f;").count(),1);
    assert_eq!(original.matches("u32 sample_start, u32 sample_count)").count(),1);
    let original=original.replace("pf_multiway_sum","pf_original_init")
        .replace("u32 sample_start, u32 sample_count)","u32 sample_start, u32 sample_count, float initial)")
        .replace("float sum = 0.f;","float sum = initial;");
    let mut modules=Vec::new();let mut resources=Vec::new();
    for compact in [false,true] {
        let mut src=base.clone()+&original+include_str!("rank_compact.cu");
        for o in 2..=8 {
            let q=(o+2)/2;
            let body=if compact {format!("__shared__ float scratch[NC*{q}];float v=pf_rank_compact_sum<{q},{o}>(h,bases,cdf,gl,gu,hg,gc,start,count,h<NC?initial[h]:0.f,scratch);if(h<NC)out[h]=v;")}
                else {format!("if(h<NC)out[h]=pf_original_init<{q},{o}>(h,bases,cdf,lo,hi,start,count,initial[h]);")};
            src+=&format!("\nextern \"C\" __global__ void audit_{o}(const u32* bases,const float* cdf,const u32* lo,const u32* hi,const u32* gl,const u32* gu,const u32* hg,const u32* gc,u32 start,u32 count,const float* initial,float* out){{u32 h=threadIdx.x;{body}}}\n");
        }
        let ptx=cudarc::nvrtc::compile_ptx_with_opts(&src,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
        let label=if compact{"candidate"}else{"control"};std::fs::write(dir.join(format!("{label}.ptx")),ptx.to_src()).unwrap();
        std::fs::write(dir.join(format!("{label}.cu")),&src).unwrap();
        let module=ctx.load_module(ptx).unwrap();
        for o in 2..=8 {let f=module.load_function(&format!("audit_{o}")).unwrap();
            resources.push(json!({"compact":compact,"opponents":o,"registers":f.num_regs().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap(),"local_bytes":f.local_size_bytes().unwrap()}));
        }
        modules.push(module);
    }
    let bases:Vec<u32>=(0..8).map(|o|o*32*170).collect();let d_bases=stream.clone_htod(&bases).unwrap();
    let mut cases=0;
    let real=CoupledDeck::shared();
    for kind in 0..5 {
        let synthetic=table(kind);let deck=if kind==4{real.as_ref()}else{&synthetic};let m=RankMaps::new(deck);
        for s in 0..SAMPLES {for h in 0..169 {let i=s*169+m.hand[s*169+h] as usize;assert_eq!((m.lower[i],m.upper[i]),(deck.lower[s*169+h],deck.upper[s*169+h]));}}
        let d_lo=stream.clone_htod(&deck.lower).unwrap();let d_hi=stream.clone_htod(&deck.upper).unwrap();
        let d_gl=stream.clone_htod(&m.lower).unwrap();let d_gu=stream.clone_htod(&m.upper).unwrap();
        let d_hg=stream.clone_htod(&m.hand).unwrap();let d_gc=stream.clone_htod(&m.count).unwrap();
        for density in 0..3 {
            let cdf:Vec<f32>=(0..8*32*170).map(|i|match density {0=>0.,1=>(i%170) as f32/169.,_=>((i%170)/((i/170)%7+1)*((i/170)%7+1)) as f32/169.}).collect();
            let d_cdf=stream.clone_htod(&cdf).unwrap();
            for nonzero in [false,true] {
                let initial:Vec<f32>=(0..169).map(|h|if nonzero{((h*7919)%2301) as f32/31.-20.}else{0.}).collect();
                let d_initial=stream.clone_htod(&initial).unwrap();
                for o in 2..=8 {for start in [0u32,1,37,992] {for count in [1u32,5,7,23,31,32] {
                    assert!(start+count<=1024);let mut outputs=Vec::new();
                    for module in &modules {
                        let f=module.load_function(&format!("audit_{o}")).unwrap();
                        let mut out=stream.clone_htod(&vec![f32::from_bits(0x7fc01234);192]).unwrap();
                        unsafe {stream.launch_builder(&f).arg(&d_bases).arg(&d_cdf).arg(&d_lo).arg(&d_hi)
                            .arg(&d_gl).arg(&d_gu).arg(&d_hg).arg(&d_gc).arg(&start).arg(&count).arg(&d_initial).arg(&mut out)
                            .launch(LaunchConfig{grid_dim:(1,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).unwrap();}
                        let values=stream.clone_dtoh(&out).unwrap();assert!(values[..169].iter().all(|v|v.is_finite()));
                        assert!(values[169..].iter().all(|v|v.to_bits()==0x7fc01234));
                        if density==0{assert_eq!(values[..169],initial);}
                        outputs.push(values.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                    }
                    assert_eq!(outputs[0],outputs[1],"kind={kind},density={density},initial={nonzero},o={o},start={start},count={count}");cases+=1;
                }}}
            }
        }
    }
    let result=json!({"exact":true,"cases":cases,"hand_values":169,"guard_values":23,"mapping_bytes":(3*SAMPLES*169+SAMPLES)*4,"resources":resources});
    std::fs::write(dir.join("resources.json"),serde_json::to_vec_pretty(&result).unwrap()).unwrap();
    println!("C18_COMPACT {result}");
}


pub(super) struct RankDevice {
    pub lower:CudaSlice<u32>, pub upper:CudaSlice<u32>, pub hand:CudaSlice<u32>, pub count:CudaSlice<u32>,
}
impl RankDevice {pub fn bytes(&self)->usize{(self.lower.len()+self.upper.len()+self.hand.len()+self.count.len())*4}}

fn integrated_source(input:&str,name:&str)->Result<String,String> {
    let marker=format!("extern \"C\" __global__ void {name}(");
    let start=input.find(&marker).ok_or("C18 target missing")?;
    let end=start+input[start..].find("\n}\n").ok_or("C18 target end missing")?+3;
    let mut body=input[start..end].to_string();
    for (old,new,count) in [
        ("float* val, const u32* aliases)","float* val, const u32* aliases, const u32* group_lower, const u32* group_upper, const u32* hand_group, const u32* group_count)",1),
        ("for (u32 h = threadIdx.x; h < NC; h += blockDim.x) {","{ u32 h = threadIdx.x; __shared__ float rank_products[NC * 5];",1),
        ("if (prob <= 0.f) { if (sample_start == 0) val[at] = 0.f; continue; }","if (prob <= 0.f) { if (h < NC && sample_start == 0) val[at] = 0.f; return; }",1),
        ("pf_multiway_sum<","pf_rank_compact_sum<",7),
        ("lower, upper, sample_start, sample_count)","group_lower, group_upper, hand_group, group_count, sample_start, sample_count, 0.f, rank_products)",7),
        ("        float increment =","        if (h < NC) { float increment =",1),
        ("            val[at] += increment;\n    }","            val[at] += increment;\n        }\n    }",1),
    ] {
        if body.matches(old).count()!=count{return Err(format!("C18 rewrite invariant: {old}"));}body=body.replace(old,new);
    }
    Ok(format!("{}\n{}\n{}{}",&input[..start],include_str!("rank_compact.cu"),body,&input[end..]))
}

impl PreflopGpu {
    pub(super) fn enable_rank_compact(&mut self,s:&PreflopSolver,budget_mb:u64)->Result<(),String> {
        if self.warmed || self.eval_warmed || self.rank_compact.is_some() || !self.throughput_narrow || !self.exact_reuse_compatible(){return Err("C18 requires fresh narrow native cohorts".into());}
        let plan=&self.research_cohorts.as_ref().ok_or("C18 missing cohorts")?.plan;
        let bytes=(3*SAMPLES*169+SAMPLES)*4;
        if plan.peak_bytes+bytes>budget_mb.min(23000) as usize*1_000_000{return Err("C18 maps exceed budget".into());}
        let deck=s.multiway.as_ref().ok_or("C18 missing fixed deck")?;let maps=RankMaps::new(deck);
        let (major,minor)=self._ctx.compute_capability().map_err(e)?;
        let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
        static PTX:[std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>;2]=[std::sync::OnceLock::new(),std::sync::OnceLock::new()];
        let mut functions=Vec::new();
        for (i,name) in ["pf_exact_reuse_terminal","pf_cohort_terminal"].iter().enumerate() {
            let source=if i==0{exact_reuse::kernel_source(true)?}else{cohort_reuse::kernel_source(true)?};
            let source=integrated_source(&narrow_offsets::source(&source,true)?,name)?;
            let ptx=PTX[i].get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(&source,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
            let function=self._ctx.load_module(ptx.clone()).map_err(e)?.load_function(name).map_err(e)?;
            if let Ok(path)=std::env::var("PREFLOP_GPU_RANK_INTEGRATED_DIAGNOSTICS") {
                let folder=std::path::PathBuf::from(path);std::fs::create_dir_all(&folder).map_err(e)?;
                let target=folder.join(format!("{name}-candidate.ptx"));
                if target.exists(){assert_eq!(std::fs::read_to_string(&target).unwrap(),ptx.to_src());}
                else {
                    let control=if i==0{exact_reuse::kernel_source(true)?}else{cohort_reuse::kernel_source(true)?};
                    let control=narrow_offsets::source(&control,true)?;
                    let control_ptx=cudarc::nvrtc::compile_ptx_with_opts(&control,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)?;
                    std::fs::write(&target,ptx.to_src()).map_err(e)?;
                    std::fs::write(folder.join(format!("{name}-candidate.cu")),&source).map_err(e)?;
                    std::fs::write(folder.join(format!("{name}-control.cu")),control).map_err(e)?;
                    std::fs::write(folder.join(format!("{name}-control.ptx")),control_ptx.to_src()).map_err(e)?;
                    let resources=json!({"function":name,"registers":function.num_regs().map_err(e)?,"shared_bytes":function.shared_size_bytes().map_err(e)?,"local_bytes":function.local_size_bytes().map_err(e)?});
                    std::fs::write(folder.join(format!("{name}-resources.json")),serde_json::to_vec_pretty(&resources).map_err(e)?).map_err(e)?;
                }
            }
            functions.push(function);
        }
        let device=RankDevice{lower:self.stream.clone_htod(&maps.lower).map_err(e)?,upper:self.stream.clone_htod(&maps.upper).map_err(e)?,hand:self.stream.clone_htod(&maps.hand).map_err(e)?,count:self.stream.clone_htod(&maps.count).map_err(e)?};
        assert_eq!(device.bytes(),bytes);
        self.research_cohorts.as_mut().unwrap().terminal=functions.pop().unwrap();
        self.research_exact_reuse.as_mut().unwrap().terminal=functions.pop().unwrap();
        self.rank_compact=Some(device);Ok(())
    }
}
