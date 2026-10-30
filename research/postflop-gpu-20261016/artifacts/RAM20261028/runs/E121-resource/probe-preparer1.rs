use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions,Ptx}};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
fn emit(v:serde_json::Value){println!("E121_RESOURCE {v}");std::io::stdout().flush().unwrap();}

include!("host-encode.rs");
fn host_check(out: &std::path::Path) -> (u64,usize) {
    let mut file=std::io::BufWriter::new(OpenOptions::new().create_new(true).write(true).open(out.join("host-hand-words.bin")).unwrap());
    file.write_all(b"E121_HAND_WORDS_V1
").unwrap();
    let expected=1_759_602u64+3*1326;
    file.write_all(&expected.to_le_bytes()).unwrap();
    let mut count=0u64;let mut maximum_capacity=0usize;
    let write=|file:&mut std::io::BufWriter<std::fs::File>,a:u32,b:u32,s:u32,w:u32| {
        assert!(a<b&&b<52&&w<0x800000);
        assert_eq!(w&63,a);assert_eq!((w>>6)&63,b);
        assert_eq!(if w>>12==2047 {u32::MAX}else{w>>12},s);
        for x in [a,b,s,w] {file.write_all(&x.to_le_bytes()).unwrap();}
    };
    let same:Vec<u32>=(0..1326).collect();
    for a in 0u32..52 {for b in a+1..52 {
        let c1=vec![a;1326];let c2=vec![b;1326];let words=terminal_hand_words(&c1,&c2,&same);assert_eq!(words.len(),1326);maximum_capacity=maximum_capacity.max(words.capacity());
        for i in 0..1326 {write(&mut file,a,b,same[i],words[i]);count+=1;}
        let sentinel=terminal_hand_words(&[a],&[b],&[u32::MAX]);write(&mut file,a,b,u32::MAX,sentinel[0]);count+=1;
    }}
    let mut c1=Vec::with_capacity(1326);let mut c2=Vec::with_capacity(1326);
    for a in 0u32..52 {for b in a+1..52 {c1.push(a);c2.push(b);}}
    for mode in 0..3 {
        let s:Vec<u32>=(0u32..1326).map(|i|match mode {0=>i,1=>1325-i,_=>if i%7==0{u32::MAX}else{i*73%1326}}).collect();
        let words=terminal_hand_words(&c1,&c2,&s);assert_eq!(words.len(),1326);maximum_capacity=maximum_capacity.max(words.capacity());
        for i in 0..1326 {write(&mut file,c1[i],c2[i],s[i],words[i]);count+=1;}
    }
    assert_eq!(count,expected);assert_eq!(maximum_capacity,1326);file.flush().unwrap();file.get_ref().sync_all().unwrap();(count,maximum_capacity)
}

fn main(){
 let out=PathBuf::from(std::env::args().nth(1).unwrap());let (host_records,host_capacity)=host_check(&out);let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
 let names=["copy_root","down_action","down_chance","up_fold","up_show","up_chance","up_action","copy_span","up_action_eval"];
 for variant in ["baseline","candidate"]{
  let ptx=if variant=="baseline"{Ptx::from_src(include_str!("baseline-compute_120.ptx"))}else{let p=compile_ptx_with_opts(include_str!("candidate.cu"),CompileOptions{arch:Some("compute_120"),..Default::default()}).unwrap();let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("candidate-compute_120.ptx")).unwrap();f.write_all(p.to_src().as_bytes()).unwrap();f.sync_all().unwrap();p};
  let before=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let m=ctx.load_module(ptx).unwrap();let after=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
  for name in names{let f=m.load_function(name).unwrap();let dynamic=match name{"up_fold"=>1326*4,"up_show"=>1326*20,_=>0};let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|t|(t,f.occupancy_max_active_blocks_per_multiprocessor(t,dynamic,None).unwrap())).collect();emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes_per_thread":f.local_size_bytes().unwrap(),"constant_bytes":f.const_size_bytes().unwrap(),"static_shared_bytes":f.shared_size_bytes().unwrap(),"dynamic_shared_bytes":dynamic,"max_threads":f.max_threads_per_block().unwrap(),"occupancy_by_threads":occupancy,"device_shared_limit":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap(),"device_thread_limit":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap(),"context_stack_before":before,"context_stack_after":after,"application_kernels":0}));}drop(m);ctx.check_err().unwrap();
 }
 let p=compile_ptx_with_opts(include_str!("candidate.cu"),CompileOptions{arch:Some("compute_75"),..Default::default()}).unwrap();let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("candidate-compute_75.ptx")).unwrap();f.write_all(p.to_src().as_bytes()).unwrap();f.sync_all().unwrap();drop(f);ctx.check_err().unwrap();drop(ctx);emit(serde_json::json!({"stage":"complete","candidate_NVRTC_compiles":2,"baseline_PTX_reused":true,"resource_rows":18,"application_kernels":0,"solver_or_speed_runs":0,"host_encode_records":host_records,"host_maximum_words_capacity":host_capacity}));
}
