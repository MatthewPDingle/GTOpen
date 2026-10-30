//! Private serial integer-OR probe, no production source or GPU execution.
use solver::{Solver,Spot,SpotConfig,Storage};
use solver::store::Store;
use std::{fs::File,io::{BufWriter,Write},sync::Arc,time::Instant,hint::black_box};
#[inline(never)] fn portable_i16(q:&[i16])->u16{q.iter().fold(0u16,|bits,&v|bits|v as u16)}
#[inline(never)] fn portable_u16(q:&[u16])->u16{q.iter().fold(0u16,|bits,&v|bits|v)}
#[target_feature(enable="avx2")]
#[inline(never)] unsafe fn wide_i16(q:&[i16])->u16{q.iter().fold(0u16,|bits,&v|bits|v as u16)}
#[target_feature(enable="avx2")]
#[inline(never)] unsafe fn wide_u16(q:&[u16])->u16{q.iter().fold(0u16,|bits,&v|bits|v)}
fn emit(v:serde_json::Value){let mut f=std::io::stdout().lock();writeln!(f,"D090 {v}").unwrap();f.flush().unwrap();}
fn word(f:&mut BufWriter<File>,x:u32){f.write_all(&x.to_le_bytes()).unwrap();}
fn vector(f:&mut BufWriter<File>,v:&[u16]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();for x in v{f.write_all(&x.to_le_bytes()).unwrap();}}
fn control(path:&str){
 let mut f=BufWriter::new(std::fs::OpenOptions::new().write(true).create_new(true).open(path).unwrap());f.write_all(b"D090-OR-RAW-v1\0\0").unwrap();let mut id=0u32;
 let mut check=|n:usize,off:usize,pattern:u32,value:u16|{
  let mut raw=vec![0xb1a5u16;off+n+3];
  for i in 0..n {raw[off+i]=match pattern{0=>value,1=>0,2=>if i==n/2{1u16<<((i+off)%16)}else{0},3=>if i+1==n{0x8000}else{0},_=>((i*1337+i/7+off*79)%65536) as u16};}
  let input=raw.clone();let signed:Vec<i16>=raw.iter().map(|v|*v as i16).collect();let expected=raw[off..off+n].iter().copied().fold(0,|a,b|a|b);
  let u=black_box(&raw[off..off+n]);let s=black_box(&signed[off..off+n]);let results=[portable_i16(s),portable_u16(u),unsafe{wide_i16(s)},unsafe{wide_u16(u)}];assert!(results.iter().all(|v|*v==expected));assert_eq!(raw,input);assert!(signed.iter().zip(&input).all(|(a,b)|*a as u16==*b));
  for x in [id,n as u32,off as u32,pattern,expected as u32,results[0] as u32,results[1] as u32,results[2] as u32,results[3] as u32]{word(&mut f,x);}
  vector(&mut f,&input);vector(&mut f,&raw);vector(&mut f,&signed.iter().map(|x|*x as u16).collect::<Vec<_>>());id+=1;
 };
 for v in 0..=u16::MAX{check(1,1,0,v);}
 for n in [0,1,7,8,15,16,17,31,32,33,63,64,65,127,128,129,257,513,4097]{for off in 0..4 {for pattern in 1..=4{check(n,off,pattern,0);}}}
 drop(check);f.flush().unwrap();f.get_ref().sync_all().unwrap();emit(serde_json::json!({"stage":"control_complete","cases":id,"all_result_bits_exact":true,"all_actual_inputs_guards_unchanged":true,"gpu_executions":0,"performance_measured":false}));
}
fn scan(s:&Solver,wide:bool)->[u16;4]{
 let mut result=[0u16;4];let mut j=0;
 for which in 0..2 {for p in 0..2 {
  let store=if which==0 {&s.regrets[p]}else{&s.strat[p]};
  result[j]=match store{
   Store::I16{q,scale}=>{assert!(black_box(scale.as_slice()).iter().all(|v|v.to_bits()==0));let q=black_box(q.as_slice());if wide{unsafe{wide_i16(q)}}else{portable_i16(q)}},
   Store::U16{q,scale}=>{assert!(black_box(scale.as_slice()).iter().all(|v|v.to_bits()==0));let q=black_box(q.as_slice());if wide{unsafe{wide_u16(q)}}else{portable_u16(q)}},
   _=>panic!("compressed probe expected")};j+=1;
 }}result
}
fn benchmark(arm:&str){
 let config:SpotConfig=serde_json::from_str(include_str!("fixture.json")).unwrap();let host=Solver::with_storage(Arc::new(Spot::new(config).unwrap()),Storage::Compressed);
 assert_eq!(host.spot.tree.nodes.len(),1346813);assert_eq!(host.arena_bytes(),1386321040);assert!(host.use_isomorphism);
 let mut shapes=Vec::new();for which in 0..2{for p in 0..2{let store=if which==0{&host.regrets[p]}else{&host.strat[p]};match store{Store::I16{q,scale}=>shapes.push((which,p,q.len(),scale.len())),Store::U16{q,scale}=>shapes.push((which,p,q.len(),scale.len())),_=>unreachable!()}}}
 let wide=arm=="avx2";let start=Instant::now();let first=scan(black_box(&host),wide);let fresh=start.elapsed().as_secs_f64()*1000.0;assert_eq!(first,[0;4]);
 // Explicit pre-touch outside the second timer. Fresh and pre-touched results are separate.
 assert_eq!(scan(black_box(&host),false),[0;4]);let start=Instant::now();let second=scan(black_box(&host),wide);let touched=start.elapsed().as_secs_f64()*1000.0;assert_eq!(second,[0;4]);
 emit(serde_json::json!({"stage":"benchmark","arm":arm,"fresh_ms":fresh,"pretouched_ms":touched,"fresh_results":first,"pretouched_results":second,"shapes":shapes,"cpu_arena_bytes":host.arena_bytes(),"nodes":host.spot.tree.nodes.len(),"avx2_detected":true,"gpu_executions":0,"scope":"Four exact full q OR scans plus original positive-zero scale checks. No GPU, snapshot metadata guard or full constructor/solve timing. No q pre-touch before fresh timer; one independent native process per arm."}));
}
fn main(){assert!(std::is_x86_feature_detected!("avx2"),"AVX2 unavailable; do not execute targeted helper");let args:Vec<String>=std::env::args().collect();match args.get(1).map(String::as_str){Some("control")=>control(&args[2]),Some("baseline")=>benchmark("baseline"),Some("avx2")=>benchmark("avx2"),_=>panic!("mode required")}}
