//! Exact static rank-boundary CDF storage for fresh retained GPU engines.
use super::*;
use super::super::multiway::{CoupledDeck,SAMPLES};
use serde_json::json;
use std::collections::BTreeSet;
struct Maps {prefix:Vec<u32>,hand:Vec<u32>,offsets:Vec<u32>,stride:u32}
impl Maps {
    fn new(d:&CoupledDeck)->Self {
        Self::with_batch(d,32)
    }
    fn with_batch(d:&CoupledDeck,batch:usize)->Self {
        assert!((1..=32).contains(&batch));
        let mut out=Self{prefix:vec![u32::MAX;1024*170],hand:vec![0;1024*169],offsets:vec![0],stride:0};
        for s in 0..1024 {
            let boundaries:Vec<u32>=d.lower[s*169..(s+1)*169].iter().chain(&d.upper[s*169..(s+1)*169]).copied().collect::<BTreeSet<_>>().into_iter().collect();
            for (i,&b) in boundaries.iter().enumerate(){out.prefix[s*170+b as usize]=i as u32;}
            for h in 0..169{out.hand[s*169+h]=out.prefix[s*170+d.lower[s*169+h] as usize];assert_eq!(boundaries[out.hand[s*169+h] as usize+1],d.upper[s*169+h]);}
            out.offsets.push(out.offsets.last().unwrap()+boundaries.len() as u32);
        }
        out.stride=(0..1024).map(|s|out.offsets[(s+batch).min(1024)]-out.offsets[s]).max().unwrap();out
    }
}

fn source(base:&str)->String {
    let start=base.find("extern \"C\" __global__ void pf_exact_reuse_cdf(").unwrap();
    let end=start+base[start..].find("extern \"C\" __global__ void pf_exact_reuse_terminal(").unwrap();
    let mut writer=base[start..end].replace("pf_exact_reuse_cdf(","pf_static_cdf(");
    for (old,new) in [
        ("u32 batch_capacity, const u32* aliases)","u32 batch_capacity, const u32* aliases, u32 row_stride, const u32* prefix_map, const u32* sample_offsets)"),
        ("size_t base = ((size_t)(compact ? blockIdx.x : slot) * batch_capacity + local) * (NC + 1);","size_t base = (size_t)(compact ? blockIdx.x : slot) * row_stride + sample_offsets[particle] - sample_offsets[sample_start];"),
        ("if (index < NC) cdf[base + index + 1] = carry + value;","if (index < NC) { u32 packed = prefix_map[(size_t)particle * (NC + 1) + index + 1]; if (packed != 0xffffffffu) cdf[base + packed] = carry + value; }"),
    ]{assert_eq!(writer.matches(old).count(),1,"{old}");writer=writer.replace(old,new);}
    let begin=base.find("template<int Q, int O>").unwrap();
    let end=base[begin..].find("extern \"C\" __global__ void pf_multiway_terminal(").unwrap()+begin;
    let mut original=base[begin..end].replace("pf_multiway_sum","pf_original_init");
    assert_eq!(original.matches("float sum = 0.f;").count(),1);
    original=original.replace("u32 sample_start, u32 sample_count)","u32 sample_start, u32 sample_count, float initial)").replace("float sum = 0.f;","float sum = initial;");
    let mut reader=original.replace("pf_original_init","pf_static_init");
    for (old,new) in [
        ("u32 sample_start, u32 sample_count, float initial)","u32 sample_start, u32 sample_count, float initial, const u32* sample_offsets)"),
        ("u32 lo = lower[hand], hi = upper[hand];","u32 lo = lower[hand], hi = lo + 1;\n        u32 local_offset = sample_offsets[sample_start + local] - sample_offsets[sample_start];"),
        ("u32 base = opponent_bases[q] + local * (NC + 1);","u32 base = opponent_bases[q] + local_offset;"),
    ] {assert_eq!(reader.matches(old).count(),1,"{old}");reader=reader.replace(old,new);}
    let mut output=base.to_string()+&writer+&original+&reader;
    for o in 2..=8 {for packed in [false,true] {
        let q=(o+2)/2;let name=if packed{"packed"}else{"original"};
        let call=if packed{format!("pf_static_init<{q},{o}>(h,bases,cdf,lo,hi,start,count,initial[h],offsets)")}else{format!("pf_original_init<{q},{o}>(h,bases,cdf,lo,hi,start,count,initial[h])")};
        output+=&format!("\nextern \"C\" __global__ void {name}_{o}(const u32* bases,const float* cdf,const u32* lo,const u32* hi,u32 start,u32 count,const float* initial,const u32* offsets,float* out){{u32 h=threadIdx.x;if(h<NC)out[h]={call};}}\n");
    }}output
}

#[cfg(feature = "preflop-research")]
#[test]
#[ignore="manual guarded static CDF qualification"]
fn static_cdf_matches_required_prefixes_and_hands() {
    let dir=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_STATIC_CDF_OUTPUT").unwrap());assert!(!dir.exists());std::fs::create_dir_all(&dir).unwrap();
    let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();let (major,minor)=ctx.compute_capability().unwrap();
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let control=narrow_offsets::source(&exact_reuse::kernel_source(true).unwrap(),true).unwrap();let candidate=source(&control);
    let opts=cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()};
    let original_ptx=cudarc::nvrtc::compile_ptx_with_opts(&control,opts.clone()).unwrap();let ptx=cudarc::nvrtc::compile_ptx_with_opts(&candidate,opts).unwrap();
    std::fs::write(dir.join("control.cu"),&control).unwrap();std::fs::write(dir.join("candidate.cu"),&candidate).unwrap();
    std::fs::write(dir.join("control.ptx"),original_ptx.to_src()).unwrap();std::fs::write(dir.join("candidate.ptx"),ptx.to_src()).unwrap();
    let module=ctx.load_module(ptx).unwrap();let normal=module.load_function("pf_exact_reuse_cdf").unwrap();let packed=module.load_function("pf_static_cdf").unwrap();
    let mut resources=Vec::new();for name in ["pf_exact_reuse_cdf".to_string(),"pf_static_cdf".to_string()].into_iter().chain((2..=8).flat_map(|o|[format!("original_{o}"),format!("packed_{o}")])) {
        let f=module.load_function(&name).unwrap();resources.push(json!({"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes":f.local_size_bytes().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap()}));
    }
    let work=stream.clone_htod(&[2u32,0,3,1]).unwrap();let start=0u32;let blocks=stream.clone_htod(&[0u32,1,2,3]).unwrap();
    let active=stream.clone_htod(&[1u32,1,0,1]).unwrap();let aliases=stream.clone_htod(&[0u32,0,2,3]).unwrap();let mass=stream.clone_htod(&[1f32,0.,1.,1.]).unwrap();
    let real=CoupledDeck::shared();let sentinel=-937.25f32;let mut cases=Vec::new();let mut hands=0;let mut prefixes=0;let mut unused=0;let mut map_records=Vec::new();
    for kind in 0..5 {
        let synthetic=table(kind);let deck=if kind==4{real.as_ref()}else{&synthetic};let maps=Maps::new(deck);
        let d_order=stream.clone_htod(&deck.order).unwrap();let d_lo=stream.clone_htod(&deck.lower).unwrap();let d_hi=stream.clone_htod(&deck.upper).unwrap();
        let d_prefix=stream.clone_htod(&maps.prefix).unwrap();let d_hand=stream.clone_htod(&maps.hand).unwrap();let d_offsets=stream.clone_htod(&maps.offsets).unwrap();
        map_records.push(json!({"kind":kind,"stride":maps.stride,"prefix":maps.prefix,"hand_group":maps.hand,"sample_offsets":maps.offsets}));
        for pattern in [1u32,0,1,2,3,4,5,6,7,8,9,10] {
            let norm:Vec<f32>=(0..4*169).map(|i|match pattern {
                0=>0.,1=>((i*37+i/169*13)%191) as f32/512.,2=>if i%47==0{0.125}else{0.},
                3=>f32::from_bits((i%17+1) as u32),4=>if i%169==168{1.}else{0.},
                5=>if i%13==0{0.99999994}else{1e-30},6=>1e-20*((i%11+1) as f32),7=>-0.0,
                8=>if i%2==0{-0.0}else{0.0},9=>if i%169==168{f32::from_bits(1)}else{-0.0},
                10=>if i%29==0{1e-30}else{-0.0},_=>unreachable!(),}).collect();
            let normalized=stream.clone_htod(&norm).unwrap();
            for compact in [0i32,1] {for gate in [0i32,1] {for (batch,count) in [(1u32,1u32),(5,1),(5,5),(32,1),(32,7),(32,31),(32,32)] {for sample_start in [0u32,17,237,992] {
                let old_len=4*batch as usize*170;let new_len=4*maps.stride as usize;
                let mut out_old=stream.clone_htod(&vec![sentinel;old_len+32]).unwrap();let mut out_new=stream.clone_htod(&vec![sentinel;new_len+32]).unwrap();
                unsafe {
                    stream.launch_builder(&normal).arg(&work).arg(&start).arg(&blocks).arg(&d_order).arg(&normalized).arg(&mass).arg(&active).arg(&gate).arg(&compact)
                        .arg(&mut out_old).arg(&sample_start).arg(&count).arg(&batch).arg(&aliases).launch(LaunchConfig{grid_dim:(4,count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();
                    stream.launch_builder(&packed).arg(&work).arg(&start).arg(&blocks).arg(&d_order).arg(&normalized).arg(&mass).arg(&active).arg(&gate).arg(&compact)
                        .arg(&mut out_new).arg(&sample_start).arg(&count).arg(&batch).arg(&aliases).arg(&maps.stride).arg(&d_prefix).arg(&d_offsets)
                        .launch(LaunchConfig{grid_dim:(4,count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();
                }
                let old=stream.clone_dtoh(&out_old).unwrap();let new=stream.clone_dtoh(&out_new).unwrap();let mut written=vec![false;new.len()];let mut live_rows=Vec::new();
                for block in 0..4 {let slot=[2usize,0,3,1][block];if block==1 || slot==1 || (gate!=0&&slot==2){continue;}
                    let row=if compact!=0{block}else{slot};live_rows.push(row);
                    for local in 0..count as usize {let sample=sample_start as usize+local;let offset=maps.offsets[sample]-maps.offsets[sample_start as usize];
                        for prefix in 0..170 {let id=maps.prefix[sample*170+prefix];if id==u32::MAX{continue;}
                            let a=(row*batch as usize+local)*170+prefix;let b=row*maps.stride as usize+offset as usize+id as usize;
                            assert!(!written[b]);written[b]=true;assert_eq!(old[a].to_bits(),new[b].to_bits(),"prefix case={} at={prefix}",cases.len());prefixes+=1;
                        }
                    }
                }
                for (i,w) in written.iter().enumerate(){if !w{assert_eq!(new[i].to_bits(),sentinel.to_bits());unused+=1;}}
                assert!(old[old_len..].iter().all(|v|v.to_bits()==sentinel.to_bits()));assert!(!live_rows.is_empty());
                for nonzero in [false,true] {let initial:Vec<f32>=(0..169).map(|h|if nonzero{((h*7919)%2301) as f32/31.-20.}else{0.}).collect();let d_initial=stream.clone_htod(&initial).unwrap();
                    for o in 2..=8 {
                        let bases_old:Vec<u32>=(0..o).map(|q|(live_rows[q%live_rows.len()]*batch as usize*170) as u32).collect();
                        let bases_new:Vec<u32>=(0..o).map(|q|live_rows[q%live_rows.len()] as u32*maps.stride).collect();
                        let mut result=Vec::new();
                        for packed in [false,true] {let bases=stream.clone_htod(if packed{&bases_new}else{&bases_old}).unwrap();let f=module.load_function(&format!("{}_{o}",if packed{"packed"}else{"original"})).unwrap();
                            let mut out=stream.clone_htod(&vec![sentinel;192]).unwrap();
                            unsafe {stream.launch_builder(&f).arg(&bases).arg(if packed{&out_new}else{&out_old}).arg(if packed{&d_hand}else{&d_lo}).arg(&d_hi)
                                .arg(&sample_start).arg(&count).arg(&d_initial).arg(&d_offsets).arg(&mut out).launch(LaunchConfig{grid_dim:(1,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).unwrap();}
                            let values=stream.clone_dtoh(&out).unwrap();assert!(values[..169].iter().all(|v|v.is_finite()));assert!(values[169..].iter().all(|v|*v==sentinel));
                            result.push(values.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                        }
                        assert_eq!(result[0],result[1],"hand case={} o={o},nonzero={nonzero}",cases.len());hands+=1;
                    }
                }
                cases.push(json!({"kind":kind,"pattern":pattern,"compact":compact,"gate":gate,"batch":batch,"count":count,"sample_start":sample_start}));
            }}}}
        }
    }
    assert_eq!(cases.len(),6720);assert_eq!(hands,94080);
    let result=json!({"exact":true,"cases":cases,"prefix_cases":6720,"hand_vector_cases":hands,"required_prefixes_checked":prefixes,"unused_slots_checked":unused,"resources":resources});
    std::fs::write(dir.join("results.json"),serde_json::to_vec_pretty(&result).unwrap()).unwrap();
    std::fs::write(dir.join("maps.json"),serde_json::to_vec(&map_records).unwrap()).unwrap();
    println!("C23_STATIC prefix_cases=6720 hand_vectors={hands} prefixes={prefixes} unused={unused}");
}

#[cfg(feature = "preflop-research")]
#[test]
#[ignore="manual guarded C24 four-sample qualification"]
fn c24_four_sample_prefixes_and_hands() {
    let dir=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_STATIC_CDF_OUTPUT").unwrap());assert!(!dir.exists());std::fs::create_dir_all(&dir).unwrap();
    let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();let (major,minor)=ctx.compute_capability().unwrap();
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let control=narrow_offsets::source(&exact_reuse::kernel_source(true).unwrap(),true).unwrap();let candidate=source(&control);
    let opts=cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()};
    let original_ptx=cudarc::nvrtc::compile_ptx_with_opts(&control,opts.clone()).unwrap();let ptx=cudarc::nvrtc::compile_ptx_with_opts(&candidate,opts).unwrap();
    std::fs::write(dir.join("control.cu"),&control).unwrap();std::fs::write(dir.join("candidate.cu"),&candidate).unwrap();
    std::fs::write(dir.join("control.ptx"),original_ptx.to_src()).unwrap();std::fs::write(dir.join("candidate.ptx"),ptx.to_src()).unwrap();
    let module=ctx.load_module(ptx).unwrap();let normal=module.load_function("pf_exact_reuse_cdf").unwrap();let packed=module.load_function("pf_static_cdf").unwrap();
    let mut resources=Vec::new();for name in ["pf_exact_reuse_cdf".to_string(),"pf_static_cdf".to_string()].into_iter().chain((2..=8).flat_map(|o|[format!("original_{o}"),format!("packed_{o}")])) {
        let f=module.load_function(&name).unwrap();resources.push(json!({"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes":f.local_size_bytes().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap()}));
    }
    let work=stream.clone_htod(&[2u32,0,3,1]).unwrap();let start=0u32;let blocks=stream.clone_htod(&[0u32,1,2,3]).unwrap();
    let active=stream.clone_htod(&[1u32,1,0,1]).unwrap();let aliases=stream.clone_htod(&[0u32,0,2,3]).unwrap();let mass=stream.clone_htod(&[1f32,0.,1.,1.]).unwrap();
    let real=CoupledDeck::shared();let sentinel=-937.25f32;let mut cases=Vec::new();let mut hands=0;let mut prefixes=0;let mut unused=0;let mut map_records=Vec::new();
    for kind in 0..5 {
        let synthetic=table(kind);let deck=if kind==4{real.as_ref()}else{&synthetic};let maps=Maps::with_batch(deck,4);
        let d_order=stream.clone_htod(&deck.order).unwrap();let d_lo=stream.clone_htod(&deck.lower).unwrap();let d_hi=stream.clone_htod(&deck.upper).unwrap();
        let d_prefix=stream.clone_htod(&maps.prefix).unwrap();let d_hand=stream.clone_htod(&maps.hand).unwrap();let d_offsets=stream.clone_htod(&maps.offsets).unwrap();
        map_records.push(json!({"kind":kind,"stride":maps.stride,"prefix":maps.prefix,"hand_group":maps.hand,"sample_offsets":maps.offsets}));
        for pattern in [1u32,0,1,2,3,4,5,6,7,8,9,10] {
            let norm:Vec<f32>=(0..4*169).map(|i|match pattern {
                0=>0.,1=>((i*37+i/169*13)%191) as f32/512.,2=>if i%47==0{0.125}else{0.},
                3=>f32::from_bits((i%17+1) as u32),4=>if i%169==168{1.}else{0.},
                5=>if i%13==0{0.99999994}else{1e-30},6=>1e-20*((i%11+1) as f32),7=>-0.0,
                8=>if i%2==0{-0.0}else{0.0},9=>if i%169==168{f32::from_bits(1)}else{-0.0},
                10=>if i%29==0{1e-30}else{-0.0},_=>unreachable!(),}).collect();
            let normalized=stream.clone_htod(&norm).unwrap();
            for compact in [0i32,1] {for gate in [0i32,1] {for (batch,count) in [(4u32,1u32),(4,2),(4,3),(4,4)] {for sample_start in [0u32,17,237,1020] {
                let old_len=4*batch as usize*170;let new_len=4*maps.stride as usize;
                let mut out_old=stream.clone_htod(&vec![sentinel;old_len+32]).unwrap();let mut out_new=stream.clone_htod(&vec![sentinel;new_len+32]).unwrap();
                unsafe {
                    stream.launch_builder(&normal).arg(&work).arg(&start).arg(&blocks).arg(&d_order).arg(&normalized).arg(&mass).arg(&active).arg(&gate).arg(&compact)
                        .arg(&mut out_old).arg(&sample_start).arg(&count).arg(&batch).arg(&aliases).launch(LaunchConfig{grid_dim:(4,count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();
                    stream.launch_builder(&packed).arg(&work).arg(&start).arg(&blocks).arg(&d_order).arg(&normalized).arg(&mass).arg(&active).arg(&gate).arg(&compact)
                        .arg(&mut out_new).arg(&sample_start).arg(&count).arg(&batch).arg(&aliases).arg(&maps.stride).arg(&d_prefix).arg(&d_offsets)
                        .launch(LaunchConfig{grid_dim:(4,count.div_ceil(4),1),block_dim:(128,1,1),shared_mem_bytes:0}).unwrap();
                }
                let old=stream.clone_dtoh(&out_old).unwrap();let new=stream.clone_dtoh(&out_new).unwrap();let mut written=vec![false;new.len()];let mut live_rows=Vec::new();
                for block in 0..4 {let slot=[2usize,0,3,1][block];if block==1 || slot==1 || (gate!=0&&slot==2){continue;}
                    let row=if compact!=0{block}else{slot};live_rows.push(row);
                    for local in 0..count as usize {let sample=sample_start as usize+local;let offset=maps.offsets[sample]-maps.offsets[sample_start as usize];
                        for prefix in 0..170 {let id=maps.prefix[sample*170+prefix];if id==u32::MAX{continue;}
                            let a=(row*batch as usize+local)*170+prefix;let b=row*maps.stride as usize+offset as usize+id as usize;
                            assert!(!written[b]);written[b]=true;assert_eq!(old[a].to_bits(),new[b].to_bits(),"prefix case={} at={prefix}",cases.len());prefixes+=1;
                        }
                    }
                }
                for (i,w) in written.iter().enumerate(){if !w{assert_eq!(new[i].to_bits(),sentinel.to_bits());unused+=1;}}
                assert!(old[old_len..].iter().all(|v|v.to_bits()==sentinel.to_bits()));assert!(!live_rows.is_empty());
                for nonzero in [false,true] {let initial:Vec<f32>=(0..169).map(|h|if nonzero{((h*7919)%2301) as f32/31.-20.}else{0.}).collect();let d_initial=stream.clone_htod(&initial).unwrap();
                    for o in 2..=8 {
                        let bases_old:Vec<u32>=(0..o).map(|q|(live_rows[q%live_rows.len()]*batch as usize*170) as u32).collect();
                        let bases_new:Vec<u32>=(0..o).map(|q|live_rows[q%live_rows.len()] as u32*maps.stride).collect();
                        let mut result=Vec::new();
                        for packed in [false,true] {let bases=stream.clone_htod(if packed{&bases_new}else{&bases_old}).unwrap();let f=module.load_function(&format!("{}_{o}",if packed{"packed"}else{"original"})).unwrap();
                            let mut out=stream.clone_htod(&vec![sentinel;192]).unwrap();
                            unsafe {stream.launch_builder(&f).arg(&bases).arg(if packed{&out_new}else{&out_old}).arg(if packed{&d_hand}else{&d_lo}).arg(&d_hi)
                                .arg(&sample_start).arg(&count).arg(&d_initial).arg(&d_offsets).arg(&mut out).launch(LaunchConfig{grid_dim:(1,1,1),block_dim:(192,1,1),shared_mem_bytes:0}).unwrap();}
                            let values=stream.clone_dtoh(&out).unwrap();assert!(values[..169].iter().all(|v|v.is_finite()));assert!(values[169..].iter().all(|v|*v==sentinel));
                            result.push(values.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
                        }
                        assert_eq!(result[0],result[1],"hand case={} o={o},nonzero={nonzero}",cases.len());hands+=1;
                    }
                }
                cases.push(json!({"kind":kind,"pattern":pattern,"compact":compact,"gate":gate,"batch":batch,"count":count,"sample_start":sample_start}));
            }}}}
        }
    }
    assert_eq!(cases.len(),3840);assert_eq!(hands,53760);
    let result=json!({"exact":true,"cases":cases,"prefix_cases":3840,"hand_vector_cases":hands,"required_prefixes_checked":prefixes,"unused_slots_checked":unused,"resources":resources});
    std::fs::write(dir.join("results.json"),serde_json::to_vec_pretty(&result).unwrap()).unwrap();
    std::fs::write(dir.join("maps.json"),serde_json::to_vec(&map_records).unwrap()).unwrap();
    println!("C24_STATIC prefix_cases=3840 hand_vectors={hands} prefixes={prefixes} unused={unused}");
}

#[cfg(all(test, feature = "preflop-research"))]
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


pub(super) struct Packed {
    pub prefix:CudaSlice<u32>,pub hand:CudaSlice<u32>,pub offsets:CudaSlice<u32>,
    pub writer:CudaFunction,pub terminal:CudaFunction,pub stride:u32,pub original_bytes:usize,
}
impl Packed {
    pub fn bytes(&self)->usize{(self.prefix.len()+self.hand.len()+self.offsets.len())*4}
    pub fn report(&self)->serde_json::Value{json!({"row_stride":self.stride,"static_bytes":self.bytes(),"original_cdf_bytes":self.original_bytes})}
}
#[cfg(test)]
thread_local! {pub(super) static FAIL_STAGE:std::cell::Cell<u32>=const {std::cell::Cell::new(0)};}
#[cfg(test)]
fn fault(g:&PreflopGpu,stage:u32)->Result<(),String>{
    if FAIL_STAGE.get()!=stage{return Ok(());}FAIL_STAGE.set(0);
    let error=unsafe{g.stream.alloc::<u8>(1usize<<50)}.unwrap_err();
    assert_eq!(error.0,sys::CUresult::CUDA_ERROR_OUT_OF_MEMORY);
    Err(format!("C23 injected allocation stage {stage}: {}",e(error)))
}
fn integrated_source()->Result<String,String>{
    let control=narrow_offsets::source(&exact_reuse::kernel_source(true)?,true)?;
    let mut candidate=source(&control);
    let start=control.find("extern \"C\" __global__ void pf_exact_reuse_terminal(").ok_or("C23 terminal missing")?;
    let end=start+control[start..].find("\n}\n").ok_or("C23 terminal end")?+3;
    let mut terminal=control[start..end].replace("pf_exact_reuse_terminal(","pf_static_terminal(");
    for (old,new) in [
        ("float* val, const u32* aliases)","float* val, const u32* aliases, u32 row_stride, const u32* sample_offsets, int cohort)"),
        ("compact_slots[(size_t)p * union_slots + global_slot]","compact_slots[(cohort ? 0 : (size_t)p * union_slots) + global_slot]"),
        ("cdf_slot * batch_capacity * (NC + 1)","cdf_slot * row_stride"),
    ]{if terminal.matches(old).count()!=1{return Err(format!("C23 terminal rewrite: {old}"));}terminal=terminal.replace(old,new);}
    assert_eq!(terminal.matches("sample_start, sample_count);").count(),7);
    terminal=terminal.replace("pf_multiway_sum<","pf_static_init<").replace("sample_start, sample_count);","sample_start, sample_count, 0.f, sample_offsets);");
    candidate+=&terminal;Ok(candidate)
}
#[cfg(all(test, feature = "preflop-research"))]
pub(super) fn new(s:&PreflopSolver,budget:u64)->Result<PreflopGpu,String>{
    promote(PreflopGpu::new_research_narrow_cohorts(s,budget)?,s,budget)
}
pub(super) fn promote(mut g:PreflopGpu,s:&PreflopSolver,budget:u64)->Result<PreflopGpu,String>{
    if g.warmed || g.eval_warmed || g.static_cdf.is_some() || !g.throughput_narrow {
        return Err("static CDF requires a fresh retained engine with narrow offsets".into());
    }
    let plan=&g.research_cohorts.as_ref().ok_or("C23 requires retained cohorts")?.plan;
    let maps=Maps::new(s.multiway.as_ref().ok_or("C23 missing fixed rank table")?);
    let original_bytes=g.d_mw_cdf.len()*4;
    let elements=plan.capacity.checked_mul(maps.stride as usize).ok_or("C23 capacity overflow")?;
    narrow_offsets::check_elements(elements)?;
    let static_bytes=(maps.prefix.len()+maps.hand.len()+maps.offsets.len())*4;
    if plan.total_bytes-original_bytes+elements*4+static_bytes+256*1024*1024>budget.min(23000) as usize*1_000_000{
        return Err("C23 final allocation exceeds reserved budget".into());
    }
    let prefix=g.stream.clone_htod(&maps.prefix).map_err(e)?;
    let hand=g.stream.clone_htod(&maps.hand).map_err(e)?;
    let offsets=g.stream.clone_htod(&maps.offsets).map_err(e)?;
    #[cfg(test)]
    fault(&g,1)?;
    // g is private: release before allocating so old/new tables never overlap.
    g.stream.synchronize().map_err(e)?;
    let empty=g.stream.null::<f32>().map_err(e)?;
    drop(std::mem::replace(&mut g.d_mw_cdf,empty));
    g.stream.synchronize().map_err(e)?;
    #[cfg(test)]
    fault(&g,2)?;
    g.d_mw_cdf=g.stream.alloc_zeros::<f32>(elements).map_err(e)?;
    #[cfg(test)]
    fault(&g,3)?;
    let (major,minor)=g._ctx.compute_capability().map_err(e)?;
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    static PTX:std::sync::OnceLock<Result<cudarc::nvrtc::Ptx,String>>=std::sync::OnceLock::new();
    let ptx=PTX.get_or_init(||cudarc::nvrtc::compile_ptx_with_opts(integrated_source()?,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)).clone()?;
    let module=g._ctx.load_module(ptx.clone()).map_err(e)?;
    let writer=module.load_function("pf_static_cdf").map_err(e)?;let terminal=module.load_function("pf_static_terminal").map_err(e)?;
    #[cfg(all(test, feature = "preflop-research"))]
    if let Ok(path)=std::env::var("PREFLOP_GPU_STATIC_CDF_INTEGRATED_OUTPUT"){
        let dir=std::path::PathBuf::from(path);std::fs::create_dir_all(&dir).map_err(e)?;
        let file=dir.join("candidate.ptx");
        if file.exists(){assert_eq!(std::fs::read_to_string(file).unwrap(),ptx.to_src());}
        else{
            std::fs::write(file,ptx.to_src()).map_err(e)?;std::fs::write(dir.join("candidate.cu"),integrated_source()?).map_err(e)?;
            let mut resources=Vec::new();for (name,f) in [("writer",&writer),("terminal",&terminal)]{
                resources.push(json!({"kernel":name,"registers":f.num_regs().map_err(e)?,"shared_bytes":f.shared_size_bytes().map_err(e)?,"local_bytes":f.local_size_bytes().map_err(e)?}));
            }
            std::fs::write(dir.join("resources.json"),serde_json::to_vec_pretty(&resources).map_err(e)?).map_err(e)?;
        }
    }
    g.static_cdf=Some(Packed{prefix,hand,offsets,writer,terminal,stride:maps.stride,original_bytes});Ok(g)
}
