//! Fixed scalar IEEE/native-fallback differential control; no timing score.
use cudarc::{driver::{CudaContext,LaunchConfig,PushKernelArg},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf};
fn save(path:PathBuf,magic:&[u8],x:&[u32]){let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).unwrap());f.write_all(magic).unwrap();f.write_all(&(x.len() as u64).to_le_bytes()).unwrap();for x in x{f.write_all(&x.to_le_bytes()).unwrap();}f.flush().unwrap();}
fn next(s:&mut u64)->u32{*s^=*s<<13;*s^=*s>>7;*s^=*s<<17;(*s>>16)as u32}
fn main(){
 let dir=PathBuf::from(std::env::var_os("E060_SCALAR_DIR").unwrap());std::fs::create_dir(&dir).unwrap();
 let mut r=Vec::<f32>::new();let mut d=Vec::<f32>::new();
 let threshold=1e-12f32;let low=2f32.powi(-60);let high=2f32.powi(60);
 let denominators=[0,0x8000_0000,1,0x007f_ffff,0x0080_0000,low.to_bits(),threshold.to_bits()-2,threshold.to_bits()-1,threshold.to_bits(),threshold.to_bits()+1,threshold.to_bits()+2,0x3eaa_aaaa,0x3eaa_aaab,0x3f00_0000,0x3f00_0001,0x3f7f_ffff,0x3f80_0000,0x3f80_0001,0x4040_0000,0x4b80_0000,high.to_bits()-2,high.to_bits()-1,high.to_bits(),high.to_bits()+1,high.to_bits()+2,0x7f7f_ffff,0x7f80_0000,0x7fc0_1234,0xffc0_5678,0xbf80_0000,0xff80_0000];
 let numerators=[0,0x8000_0000,1,0x8000_0001,0x007f_ffff,0x0080_0000,0x0080_0001,low.to_bits()-2,low.to_bits()-1,low.to_bits(),low.to_bits()+1,low.to_bits()+2,threshold.to_bits()-1,threshold.to_bits(),threshold.to_bits()+1,0x3eaa_aaab,0x3f00_0000,0x3f7f_ffff,0x3f80_0000,0x3f80_0001,high.to_bits(),0x7f7f_ffff,0x7f80_0000,0xff80_0000,0x7fc0_1234,0xffc0_5678];
 for db in denominators{for rb in numerators{let den=f32::from_bits(db);let mut reg=f32::from_bits(rb);if den.is_finite()&&den>0.0&&reg>den{reg=den;}r.push(reg);d.push(den);}}
 // Dense representable neighborhoods at all source guard boundaries.
 for center in [threshold.to_bits(),low.to_bits(),high.to_bits(),0x3f80_0000u32]{for k in -512i32..=512{let den=f32::from_bits((center as i64+k as i64) as u32);for rb in [0,1,low.to_bits()-1,low.to_bits(),low.to_bits()+1,den.to_bits(),den.to_bits()-1,(den*0.5).to_bits()]{let reg=f32::from_bits(rb);r.push(if reg>den {den}else{reg});d.push(den);}}}
 let curated=r.len();let mut rng=0x0600_2026_1017_5090u64;
 for k in 0..2_097_152usize{
  let bits=next(&mut rng);let den=match k%4{
   0=>f32::from_bits((88+(bits%100))<<23 | (next(&mut rng)&0x7f_ffff)),
   1=>f32::from_bits(bits&0x7fff_ffff),
   2=>f32::from_bits(0x3f80_0000|(bits&0x7f_ffff)),
   _=>f32::from_bits(0x5d00_0000|(bits&0x7f_ffff)),
  };
  let reg=match k%11{0=>0.0,1=>f32::from_bits(1),2=>low,3=>f32::from_bits(low.to_bits()-1),4=>den,5=>f32::from_bits(den.to_bits().saturating_sub(1)),_=>{let v=f32::from_bits(next(&mut rng)&0x7fff_ffff);if den.is_finite()&&den>0.0&&v>den{den}else{v}}};
  r.push(reg);d.push(den);
 }
 let n=r.len();assert_eq!(n,d.len());let mut selected=0usize;let mut fallback=0usize;let mut uniform=0usize;let mut input=Vec::with_capacity(2*n);
 for (&reg,&den) in r.iter().zip(&d){let num=if reg>0.0{reg}else{0.0};let eligible=den>threshold&&den<=high&&(num==0.0||num>=low);if eligible{assert!(num<=den && den.is_finite() && num.is_finite());selected+=1;}else if den>threshold{fallback+=1;}else{uniform+=1;}input.push(reg.to_bits());input.push(den.to_bits());}
 save(dir.join("inputs.bin"),b"E060SCALIN1",&input);
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let ptx=compile_ptx_with_opts(include_str!("scalar.cu"),CompileOptions{arch:Some("compute_120"),..Default::default()}).unwrap();std::fs::write(dir.join("scalar.ptx"),ptx.to_src()).unwrap();let module=ctx.load_module(ptx).unwrap();
 let dr=stream.clone_htod(&r).unwrap();let dd=stream.clone_htod(&d).unwrap();let sentinel=0xa55a_06e0u32;let seed=vec![sentinel;n+32];let ni=n as i32;let mut outputs=Vec::new();
 for name in ["scalar_baseline","scalar_candidate"]{let f=module.load_function(name).unwrap();let mut out=stream.clone_htod(&seed).unwrap();unsafe{stream.launch_builder(&f).arg(&dr).arg(&dd).arg(&mut out).arg(&ni).launch(LaunchConfig::for_num_elems(n as u32)).unwrap();}let raw=stream.clone_dtoh(&out).unwrap();stream.synchronize().unwrap();assert_eq!(&raw[..16],&seed[..16]);assert_eq!(&raw[n+16..],&seed[n+16..]);save(dir.join(format!("{name}.bin")),b"E060SCALOUT1",&raw);outputs.push(raw);}
 let rr=stream.clone_dtoh(&dr).unwrap();let rd=stream.clone_dtoh(&dd).unwrap();stream.synchronize().unwrap();assert_eq!(rr.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),r.iter().map(|v|v.to_bits()).collect::<Vec<_>>());assert_eq!(rd.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),d.iter().map(|v|v.to_bits()).collect::<Vec<_>>());let mut after=Vec::with_capacity(2*n);for(i,j)in rr.iter().zip(&rd){after.push(i.to_bits());after.push(j.to_bits());}save(dir.join("inputs-after.bin"),b"E060SCALIN1",&after);
 let mismatches:Vec<_>=(0..n).filter(|&i|outputs[0][i+16]!=outputs[1][i+16]).collect();let examples:Vec<_>=mismatches.iter().take(20).map(|&i|serde_json::json!({"index":i,"regret_bits":r[i].to_bits(),"sum_bits":d[i].to_bits(),"baseline_bits":outputs[0][i+16],"candidate_bits":outputs[1][i+16]})).collect();
 let report=serde_json::json!({"id":"E060-scalar-control","cases":n,"curated":curated,"random":2_097_152,"shared_refinement_cases":selected,"native_fallback_cases":fallback,"uniform_cases":uniform,"mismatches":mismatches.len(),"examples":examples,"immutable_input_words":2*n,"output_guard_words":64,"kernel_launches":2,"solver_executions":0,"performance_measured":false,"candidate_accepted":false});
 let text=serde_json::to_vec_pretty(&report).unwrap();let mut file=OpenOptions::new().write(true).create_new(true).open(dir.join("report.json")).unwrap();file.write_all(&text).unwrap();file.flush().unwrap();println!("E060_SCALAR {}",report);if !mismatches.is_empty(){std::process::exit(20);}
}
