use super::*;
use serde_json::json;
#[test]
#[ignore = "manual C17 compiler/terminal evidence; requires fresh output path"]
fn packed_terminal_guards_and_partial_blocks(){
    let dir=std::path::PathBuf::from(std::env::var("PREFLOP_GPU_WARP_AUDIT").expect("fresh compiler evidence directory"));
    assert!(!dir.exists());std::fs::create_dir_all(&dir).unwrap();
    let ctx=CudaContext::new(0).unwrap();let stream=ctx.default_stream();
    let (major,minor)=ctx.compute_capability().unwrap();
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let mut resources=Vec::new();let mut cases=0;
    let slots:Vec<u32>=(0..9).collect();let aliases=vec![0u32,1,1,3,4,5,5,7,8];
    let d_slots=stream.clone_htod(&slots).unwrap();let d_aliases=stream.clone_htod(&aliases).unwrap();
    let lower:Vec<u32>=(0..1024*169).map(|i|((i%169*7+i/169)%169) as u32).collect();
    let upper:Vec<u32>=lower.iter().enumerate().map(|(i,&lo)|(lo+1+(i%3) as u32).min(169)).collect();
    let d_lo=stream.clone_htod(&lower).unwrap();let d_hi=stream.clone_htod(&upper).unwrap();
    for (kind,name,base) in [("exact","pf_exact_reuse_terminal",super::super::exact_reuse::kernel_source(true).unwrap()),
        ("cohort","pf_cohort_terminal",super::super::cohort_reuse::kernel_source(true).unwrap())]{
        let base=super::super::narrow_offsets::source(&base,true).unwrap();let mut funcs=Vec::new();
        for packed in [false,true]{
            let src=if packed{source(&base,name).unwrap()}else{base.clone()};
            let ptx=cudarc::nvrtc::compile_ptx_with_opts(&src,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
            let tag=if packed{"candidate"}else{"control"};
            std::fs::write(dir.join(format!("{kind}-{tag}.cu")),&src).unwrap();
            std::fs::write(dir.join(format!("{kind}-{tag}.ptx")),ptx.to_src()).unwrap();
            let module=ctx.load_module(ptx).unwrap();let f=module.load_function(name).unwrap();
            resources.push(json!({"kind":kind,"packed":packed,"registers":f.num_regs().unwrap(),"shared_bytes":f.shared_size_bytes().unwrap(),"local_bytes":f.local_size_bytes().unwrap()}));funcs.push(f);
        }
        for n in [1u32,2,3,4,5,7,8,9]{for roll in 0..7u32{for (batch,count) in [(5u32,1u32),(5,4),(5,5),(32,7),(32,31),(32,32)]{
            let terms:Vec<u32>=(0..n).collect();let vals:Vec<u32>=(1..=n).collect();
            let live:Vec<i32>=(0..n).map(|t|{let o=2+(t+roll)%7;let lv=(1i32<<(o+1))-1;if t%5==1{lv&!1}else{lv}}).collect();
            let pots:Vec<f32>=(0..n).map(|t|10.+t as f32).collect();let inv:Vec<f32>=(0..n*9).map(|i|0.5+(i%5) as f32).collect();
            let reach_src:Vec<u32>=(0..n*9).map(|i|i%9).collect();
            let d_terms=stream.clone_htod(&terms).unwrap();let d_vals=stream.clone_htod(&vals).unwrap();
            let d_live=stream.clone_htod(&live).unwrap();let d_pots=stream.clone_htod(&pots).unwrap();let d_inv=stream.clone_htod(&inv).unwrap();let d_src=stream.clone_htod(&reach_src).unwrap();
            let guard=f32::from_bits(0x4b123456);let initial=vec![guard;(n as usize+2)*169];let mut outputs:Vec<_>=(0..2).map(|_|stream.clone_htod(&initial).unwrap()).collect();
            for phase in 0..3{
                let prob:Vec<f32>=(0..n).map(|t|if phase==1||t%4==2{0.}else{0.25+t as f32*0.02}).collect();let d_prob=stream.clone_htod(&prob).unwrap();
                let cdf:Vec<f32>=(0..9*batch as usize*170).map(|i|if phase==1{0.}else{(i%170) as f32/169.*(0.5+(i/170%3) as f32*0.2)}).collect();let d_cdf=stream.clone_htod(&cdf).unwrap();
                for start in [0u32,992]{
                    for packed in [false,true]{let f=&funcs[packed as usize];let out=&mut outputs[packed as usize];
                        unsafe{let mut args=stream.launch_builder(f);
                            args.arg(&d_terms).arg(&0i32).arg(&9i32).arg(&d_live).arg(&d_pots).arg(&d_inv).arg(&d_src).arg(&d_prob).arg(&d_slots).arg(&d_slots)
                                .arg(&9u32).arg(&1i32).arg(&d_cdf).arg(&d_lo).arg(&d_hi).arg(&start).arg(&count).arg(&batch).arg(&1024u32).arg(&d_vals).arg(out).arg(&d_aliases);
                            if packed{args.arg(&n);}args.launch(launch(n,packed)).unwrap();}
                    }
                    let a=stream.clone_dtoh(&outputs[0]).unwrap();let b=stream.clone_dtoh(&outputs[1]).unwrap();
                    assert_eq!(a.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),b.iter().map(|x|x.to_bits()).collect::<Vec<_>>(),"{kind} tasks={n} roll={roll} batch={batch} count={count} phase={phase} start={start}");
                    for (i,&v) in b.iter().enumerate(){let slot=i/169;if slot==0||slot==n as usize+1||live[slot-1]&1==0{assert_eq!(v.to_bits(),guard.to_bits());}else{assert!(v.is_finite());}}
                    cases+=1;
                }
            }
        }}}
    }
    let out=json!({"exact":true,"cases":cases,"guarded":true,"task_counts":[1,2,3,4,5,7,8,9],"opponents":[2,3,4,5,6,7,8],"zero_recovery":true,"resources":resources});
    std::fs::write(dir.join("results.json"),serde_json::to_vec_pretty(&out).unwrap()).unwrap();println!("C17_KERNEL {out}");
}
