#![cfg(all(target_os="windows",target_pointer_width="64"))]
use solver::{Solver,Spot,SpotConfig,store::{Store,Storage},gpu::plan::GpuPlan};
use std::{ffi::c_void,io::{self,Write,BufWriter},sync::Arc,time::Instant};
use rayon::prelude::*;
use serde_json::{json,Value};
#[repr(C)]#[derive(Default)]struct SystemInfo{architecture:u32,page_size:u32,min:*mut c_void,max:*mut c_void,mask:usize,processors:u32,processor_type:u32,allocation_granularity:u32,processor_level:u16,processor_revision:u16}
#[repr(C)]#[derive(Default)]struct FileTime{low:u32,high:u32}
#[repr(C)]#[derive(Default)]struct MemoryCounters{cb:u32,faults:u32,peak_ws:usize,ws:usize,quota_peak_paged:usize,quota_paged:usize,quota_peak_nonpaged:usize,quota_nonpaged:usize,commit:usize,peak_commit:usize}
#[link(name="kernel32")]extern "system"{
 fn GetCurrentProcess()->*mut c_void;
 fn GetSystemInfo(info:*mut SystemInfo);
 fn GetProcessTimes(process:*mut c_void,creation:*mut FileTime,exit:*mut FileTime,kernel:*mut FileTime,user:*mut FileTime)->i32;
 fn K32GetProcessMemoryInfo(process:*mut c_void,counters:*mut MemoryCounters,bytes:u32)->i32;
}
fn emit(value:Value){let mut out=io::stdout().lock();writeln!(out,"D127 {value}").unwrap();out.flush().unwrap();}
fn page_size()->usize{let mut info=SystemInfo::default();unsafe{GetSystemInfo(&mut info)};let p=info.page_size as usize;assert!(p>=2&&p.is_power_of_two()&&p%2==0);p}
fn cpu_ticks()->u64{let(mut creation,mut exit,mut kernel,mut user)=(FileTime::default(),FileTime::default(),FileTime::default(),FileTime::default());assert_ne!(unsafe{GetProcessTimes(GetCurrentProcess(),&mut creation,&mut exit,&mut kernel,&mut user)},0);let cvt=|v:FileTime|((v.high as u64)<<32)|v.low as u64;cvt(kernel).checked_add(cvt(user)).unwrap()}
fn counters()->MemoryCounters{let mut m=MemoryCounters::default();m.cb=std::mem::size_of::<MemoryCounters>()as u32;assert_ne!(unsafe{K32GetProcessMemoryInfo(GetCurrentProcess(),&mut m,m.cb)},0);assert_eq!(m.cb,72);assert!(m.ws>0&&m.peak_ws>=m.ws);m}
fn counter_json(m:&MemoryCounters)->Value{json!({"page_faults":m.faults,"working_set_bytes":m.ws,"peak_working_set_bytes":m.peak_ws,"commit_bytes":m.commit,"peak_commit_bytes":m.peak_commit})}
#[inline(never)]fn original_zero_predicate(store:&Store)->bool{match store {
            Store::I16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v as u16) == 0
            }
            Store::U16 { q, scale } => {
                scale.as_slice().iter().all(|v| v.to_bits() == 0)
                    && q.as_slice().iter().fold(0u16, |bits, &v| bits | v) == 0
            }
            Store::F32(_) => false,
        }}
fn positive_zero_scales(stores:[&Store;4])->bool{stores.into_iter().all(|store|match store{Store::I16{scale,..}|Store::U16{scale,..}=>scale.as_slice().iter().all(|v|v.to_bits()==0),Store::F32(_)=>false})}
fn quantized_bytes(stores:[&Store;4])->Option<usize>{let mut total=0usize;for store in stores{let n=match store{Store::I16{q,..}=>q.len(),Store::U16{q,..}=>q.len(),Store::F32(_)=>return None};if n==0{return None;}total=total.checked_add(n.checked_mul(2).unwrap()).unwrap();}Some(total)}
fn touch_pages<T:Copy+Sync+Send>(data:&[T],page:usize)->usize{
 assert_eq!(std::mem::size_of::<T>(),2);assert!(page>=2&&page.is_power_of_two());if data.is_empty(){return 0;}
 let start=data.as_ptr()as usize;let end=start.checked_add(data.len().checked_mul(2).unwrap()).unwrap();let first=start/page;let count=(end-1)/page-first+1;
 (0..count).into_par_iter().with_min_len(64).for_each(|p|{let address=if p==0{start}else{(first+p).checked_mul(page).unwrap()};let index=(address-start)/2;assert!(index<data.len());std::hint::black_box(unsafe{std::ptr::read_volatile(data.as_ptr().add(index))});});count
}
fn touch_if_eligible(stores:[&Store;4])->(usize,usize){let Some(bytes)=quantized_bytes(stores)else{return(0,0);};if bytes<64*1024*1024||!positive_zero_scales(stores){return(0,0);}let page=page_size();let mut pages=0;for store in stores{pages+=match store{Store::I16{q,..}=>touch_pages(q.as_slice(),page),Store::U16{q,..}=>touch_pages(q.as_slice(),page),Store::F32(_)=>unreachable!()};}(pages,bytes)}
fn write_words(out:&mut impl Write,values:&[u16]){out.write_all(&(values.len()as u64).to_le_bytes()).unwrap();for x in values{out.write_all(&x.to_le_bytes()).unwrap();}}
fn ability(){
 assert_eq!(std::mem::size_of::<SystemInfo>(),48);assert_eq!(std::mem::align_of::<SystemInfo>(),8);assert_eq!(std::mem::size_of::<FileTime>(),8);assert_eq!(std::mem::size_of::<MemoryCounters>(),72);let page=page_size();let cpu_before=cpu_ticks();let before=counters();
 let raw=std::path::Path::new(r"S:\GTOpen-research\postflop-gpu-20261016\runs\D127-sparse-page-read\execution\ability-images.bin");let mut out=BufWriter::new(std::fs::File::create_new(raw).unwrap());out.write_all(b"D127-PAGE-RAW1\0\0").unwrap();let mut case=0u32;let mut total_pages=0usize;
 for signed in [false,true]{for length in [0usize,1,2,2047,2048,2049,4095,4096,4097,8192,8193]{for offset in [0usize,1,15,2047]{let n=offset+length+17;let input:Vec<u16>=(0..n).map(|i|((i*73+17)&65535)as u16).collect();
  let(after,pages,start)=if signed{let v:Vec<i16>=input.iter().map(|&x|x as i16).collect();let data=&v[offset..offset+length];let start=data.as_ptr()as usize;let p=touch_pages(data,page);(v.iter().map(|&x|x as u16).collect::<Vec<_>>(),p,start)}else{let v=input.clone();let data=&v[offset..offset+length];let start=data.as_ptr()as usize;let p=touch_pages(data,page);(v,p,start)};
  let expected=if length==0{0}else{(start+length*2-1)/page-start/page+1};assert_eq!(pages,expected);assert_eq!(after,input);total_pages+=pages;
  for x in [case,signed as u32,offset as u32,length as u32,page as u32,pages as u32]{out.write_all(&x.to_le_bytes()).unwrap();}out.write_all(&(start as u64).to_le_bytes()).unwrap();write_words(&mut out,&input);write_words(&mut out,&after);case+=1;
 }}}
 out.flush().unwrap();let mut controls=0;
 for signed in [false,true]{let mut s=if signed{Store::i16(257,4)}else{Store::u16(257,4)};assert!(original_zero_predicate(&s));assert!(positive_zero_scales([&s;4]));assert_eq!(touch_if_eligible([&s;4]),(0,0));controls+=1;
  match &mut s{Store::I16{q,..}=>q.as_mut_slice()[256]=-1,Store::U16{q,..}=>q.as_mut_slice()[256]=1,_=>unreachable!()};assert!(!original_zero_predicate(&s));controls+=1;
  match &mut s{Store::I16{q,..}=>q.as_mut_slice()[256]=0,Store::U16{q,..}=>q.as_mut_slice()[256]=0,_=>unreachable!()};
  for bits in [0x8000_0000,0x7f80_0000,0xff80_0000,0x7fc0_1234,1]{match &mut s{Store::I16{scale,..}|Store::U16{scale,..}=>scale.as_mut_slice()[3]=f32::from_bits(bits),_=>unreachable!()};assert!(!original_zero_predicate(&s));assert!(!positive_zero_scales([&s;4]));controls+=1;}
 }
 let s=Store::f32(257);assert!(!original_zero_predicate(&s));assert!(!positive_zero_scales([&s;4]));assert_eq!(quantized_bytes([&s;4]),None);assert_eq!(touch_if_eligible([&s;4]),(0,0));controls+=1;
 let after=counters();let cpu_after=cpu_ticks();assert!(cpu_after>=cpu_before);emit(json!({"stage":"ability","raw_path":raw,"native_cases":case,"touched_pages":total_pages,"all_full_owned_words_and_guards_exact":true,"predicate_eligibility_controls":controls,"system_info_bytes":48,"filetime_bytes":8,"memory_counter_bytes":72,"page_size":page,"rayon_threads":rayon::current_num_threads(),"cpu_before_ticks100ns":cpu_before,"cpu_after_ticks100ns":cpu_after,"before":counter_json(&before),"after":counter_json(&after),"GPU_executions":0}));
}
fn run(arm:&str){
 let fixtures=[include_str!("fixture-0.json"),include_str!("fixture-1.json"),include_str!("fixture-2.json")];
 for(case,config)in fixtures.iter().enumerate(){let cfg:SpotConfig=serde_json::from_str(config).unwrap();let mut s=Solver::with_storage(Arc::new(Spot::new(cfg).unwrap()),Storage::Compressed);s.use_isomorphism=true;let plan=GpuPlan::build(&s.spot,s.use_isomorphism);std::hint::black_box(&plan);
  let stores=[&s.regrets[0],&s.regrets[1],&s.strat[0],&s.strat[1]];let q_bytes=quantized_bytes(stores).unwrap();assert!(q_bytes<4*1024*1024*1024usize);let before=counters();let cpu_before=cpu_ticks();let t=Instant::now();let mut pages=0;let mut touched_bytes=0;
  if arm=="touch"{(pages,touched_bytes)=touch_if_eligible(stores);}let mid=counters();let checked=stores.map(original_zero_predicate);std::hint::black_box(checked);let elapsed=t.elapsed().as_secs_f64()*1000.0;let after=counters();let cpu_after=cpu_ticks();assert!(cpu_after>=cpu_before);assert_eq!(checked,[true;4]);
  emit(json!({"stage":"CPU_zero_scan","fixture_index":case,"board":s.spot.config.board,"arm":arm,"q_bytes":q_bytes,"cpu_arena_bytes":s.arena_bytes(),"nodes":s.spot.tree.nodes.len(),"plan_levels":plan.num_levels,"component_ms":elapsed,"process_cpu_ms":(cpu_after-cpu_before)as f64/10000.0,"cpu_before_ticks100ns":cpu_before,"cpu_after_ticks100ns":cpu_after,"page_size":page_size(),"rayon_threads":rayon::current_num_threads(),"touched_pages":pages,"touched_q_bytes":touched_bytes,"all4_original_full_checks_pass":checked,"before":counter_json(&before),"mid":counter_json(&mid),"after":counter_json(&after),"process_page_fault_delta":after.faults.wrapping_sub(before.faults),"pre_scan_page_fault_delta":mid.faults.wrapping_sub(before.faults),"original_scan_page_fault_delta":after.faults.wrapping_sub(mid.faults),"GPU_executions":0,"full_solve_performance_measured":false}));
 }
 emit(json!({"stage":"complete","arm":arm,"fixtures":3,"GPU_executions":0,"full_solve_performance_measured":false}));
}
fn main(){let args:Vec<_>=std::env::args().collect();assert_eq!(args.len(),2);match args[1].as_str(){"ability"=>ability(),"baseline"=>run("baseline"),"touch"=>run("touch"),_=>panic!("invalid mode")}}
