#[repr(C)]#[derive(Default)]struct D287FileTime{lo:u32,hi:u32}
#[repr(C)]#[derive(Default)]struct D287Memory{cb:u32,faults:u32,peak_ws:usize,ws:usize,peak_paged:usize,paged:usize,peak_nonpaged:usize,nonpaged:usize,pagefile:usize,peak_pagefile:usize,private:usize}
#[link(name="kernel32")]extern "system"{fn GetCurrentProcess()->*mut std::ffi::c_void;fn GetProcessTimes(h:*mut std::ffi::c_void,created:*mut D287FileTime,exited:*mut D287FileTime,kernel:*mut D287FileTime,user:*mut D287FileTime)->i32;fn K32GetProcessMemoryInfo(h:*mut std::ffi::c_void,p:*mut D287Memory,cb:u32)->i32;fn GetTickCount64()->u64;}
fn d287_os()->Value{
 assert_eq!(std::mem::size_of::<D287FileTime>(),8);assert_eq!(std::mem::size_of::<D287Memory>(),80);
 let(mut a,mut b,mut k,mut u)=(D287FileTime::default(),D287FileTime::default(),D287FileTime::default(),D287FileTime::default());let mut m=D287Memory::default();m.cb=80;
 unsafe{assert_ne!(GetProcessTimes(GetCurrentProcess(),&mut a,&mut b,&mut k,&mut u),0);assert_ne!(K32GetProcessMemoryInfo(GetCurrentProcess(),&mut m,80),0);}
 let q=|v:D287FileTime|u64::from(v.lo)|(u64::from(v.hi)<<32);json!({"tick_ms":unsafe{GetTickCount64()},"kernel_ticks100ns":q(k),"user_ticks100ns":q(u),"private_bytes":m.private,"working_set_bytes":m.ws,"reported_lifetime_peak_WS_bytes":m.peak_ws,"reported_lifetime_peak_commit_bytes":m.peak_pagefile})
}
fn d287_after(mut g:GpuSolver,s:Solver,name:&str,exploit:f64){
 let out=std::path::PathBuf::from(std::env::var("D156_OUTPUT").unwrap());let before_cpu=state_fingerprint(&s,exploit);d156_cpu(&out.join(format!("{name}-before.cpu.bin")),&s);let before=g.d166_snapshot(&out.join(format!("{name}-before.gpu.bin")));
 println!("D287_BEFORE {}",json!({"fixture":name,"info":before}));std::io::stdout().flush().unwrap();
 let cohort=[("W0B",false,false,0x4b123456),("W0C",true,false,0x4b123456),("W1C",true,false,0x80000000),("W1B",false,false,0x80000000),("B1",false,true,0x7fc12345),("C1",true,true,0x7fc12345),("C2",true,true,0x7f812345),("B2",false,true,0x7f812345),("B3",false,true,0x4b123456),("C3",true,true,0x4b123456)];
 for player in 0..2{for(tag,candidate,scored,poison)in cohort{
  let id=format!("{name}-p{player}-{tag}");g.d287_poison(poison).unwrap();let os_before=d287_os();println!("D287_CASE_START {}",json!({"id":id,"fixture":name,"player":player,"candidate":candidate,"scored":scored,"OS":os_before}));std::io::stdout().flush().unwrap();
  let replays=s.iteration;let stats=g.d287_component(player,candidate,replays).unwrap();let os_after=d287_os();let info=g.d166_snapshot(&out.join(format!("{id}.gpu.bin")));assert_eq!(info,before);
  println!("D287_CASE {}",json!({"id":id,"fixture":name,"player":player,"candidate":candidate,"scored":scored,"poison_bits":poison,"replays":replays,"stats":stats,"OS_before":os_before,"OS_after":os_after,"info":info}));std::io::stdout().flush().unwrap();
 }}
 let after_cpu=state_fingerprint(&s,exploit);assert_eq!(before_cpu,after_cpu);d156_cpu(&out.join(format!("{name}-after.cpu.bin")),&s);g.synchronize().unwrap();drop(g);drop(s);
 println!("D287_FIXTURE_COMPLETE {}",json!({"fixture":name,"component_cases":20,"CPU_state_fingerprint_unchanged":true,"all_owned_GPU_and_CPU_objects_dropped":true,"solver_accuracy_unchanged":true}));std::io::stdout().flush().unwrap();
}
