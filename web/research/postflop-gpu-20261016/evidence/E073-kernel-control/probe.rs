//! E073: originalu32/privateu16boundaries, same full raw controls; no timing.
use cudarc::{driver::{CudaContext, CudaFunction, CudaSlice, CudaStream, LaunchConfig, PushKernelArg},
    nvrtc::{compile_ptx_with_opts, CompileOptions}};
use serde_json::{json,Value};
use std::{fs::OpenOptions,io::{BufWriter,Write},sync::Arc};
mod cards { pub type Card=u8; }
#[path="accepted-evaluator.rs"] mod accepted_evaluator;

#[derive(Debug)] struct ProbeError(String);
impl std::fmt::Display for ProbeError { fn fmt(&self,f:&mut std::fmt::Formatter<'_>)->std::fmt::Result {f.write_str(&self.0)} }
impl std::error::Error for ProbeError {}
impl From<cudarc::driver::DriverError> for ProbeError {fn from(v:cudarc::driver::DriverError)->Self {Self(format!("CUDA: {v:?}"))}}
impl From<cudarc::nvrtc::CompileError> for ProbeError {fn from(v:cudarc::nvrtc::CompileError)->Self {Self(format!("NVRTC: {v:?}"))}}
impl From<std::io::Error> for ProbeError {fn from(v:std::io::Error)->Self {Self(format!("I/O: {v}"))}}
impl From<serde_json::Error> for ProbeError {fn from(v:serde_json::Error)->Self {Self(format!("JSON: {v}"))}}
impl From<String> for ProbeError {fn from(v:String)->Self {Self(v)}}
impl From<&str> for ProbeError {fn from(v:&str)->Self {Self(v.to_owned())}}
type Result<T>=std::result::Result<T,ProbeError>;
const GUARD:u32=0x4b123456;
const BASELINE:&str=include_str!("baseline.cu");
const CANDIDATE:&str=include_str!("candidate.cu");
const CORPUS:&str=include_str!("corpus.json");
fn fnv(bytes:impl IntoIterator<Item=u8>)->String {let mut h=0xcbf29ce484222325u64;for b in bytes {h=(h^u64::from(b)).wrapping_mul(0x100000001b3);}format!("{h:016x}")}
fn hash(v:&[u32])->String {fnv(v.iter().flat_map(|v|v.to_le_bytes()))}
fn words(v:&Value)->Vec<u32>{v.as_array().unwrap().iter().map(|v|u32::try_from(v.as_u64().unwrap()).unwrap()).collect()}
fn bits(v:&[f32])->Vec<u32>{v.iter().map(|v|v.to_bits()).collect()}
fn floats(v:&[u32])->Vec<f32>{v.iter().copied().map(f32::from_bits).collect()}
fn n(v:&Value,k:&str)->usize {usize::try_from(v[k].as_u64().unwrap()).unwrap()}
fn emit(v:Value)->Result<()> {let mut out=std::io::stdout().lock();writeln!(out,"E073_EXACT {v}")?;out.flush()?;Ok(())}
fn save(v:&Value,file:&mut BufWriter<std::fs::File>)->Result<()> {serde_json::to_writer(&mut *file,v)?;file.write_all(b"\n")?;file.flush()?;Ok(())}
fn exact(a:&[u32],b:&[u32],label:&str)->Result<()> {if a.len()!=b.len(){return Err(format!("{label}:length").into());}if let Some(i)=a.iter().zip(b).position(|(a,b)|a!=b){return Err(format!("{label}:{i}:{:08x}!={:08x}",a[i],b[i]).into());}Ok(())}
fn guards(initial:&[u32],out:&[u32],active:&[bool])->Result<()> {if initial.len()!=out.len()||out.len()!=active.len(){return Err("guard length".into());}for i in 0..out.len(){if !active[i]&&out[i]!=initial[i]{return Err(format!("output guard {i}").into());}}Ok(())}
fn nonfinite(v:&[u32])->Value {let all:Vec<_>=v.iter().enumerate().filter(|(_,x)|**x&0x7f800000==0x7f800000).map(|(i,x)|json!({"index":i,"bits":x})).collect();json!({"count":all.len(),"words":all})}
fn validate_geometry(g:&Value)->Result<()> {
 let board=words(&g["board"]);assert_eq!(board.len(),5);
 let hp:Vec<Vec<u32>>=g["hands_p"].as_array().unwrap().iter().map(words).collect();
 let ho:Vec<Vec<u32>>=g["hands_o"].as_array().unwrap().iter().map(words).collect();
 let mut sorted=Vec::new();
 for (hands,key) in [(&hp,"strengths_p"),(&ho,"strengths_o")] {
  let strengths=words(&g[key]);assert_eq!(hands.len(),strengths.len());let mut rows=Vec::new();
  let mut unique=std::collections::BTreeSet::new();
  for (i,h) in hands.iter().enumerate(){assert_eq!(h.len(),2);assert!(h[0]<h[1]&&h[1]<52);assert!(unique.insert(h.clone()));assert!(!h.iter().any(|c|board[..3].contains(c)));
   if h.iter().any(|c|board.contains(c)){assert_eq!(strengths[i],u32::MAX);}else{let cards:Vec<u8>=board.iter().chain(h).map(|x|*x as u8).collect();let r=accepted_evaluator::evaluate7(&cards);assert_eq!(strengths[i],r,"frozen independent rank differs from accepted evaluate7");rows.push((r,i as u32));}
  }rows.sort();sorted.push(rows);
 }
 let a=&g["arrays"];let sp=&sorted[0];let so=&sorted[1];assert_eq!(sp.len(),n(g,"m_p"));assert_eq!(so.len(),n(g,"m_o"));assert!(so.len()<=1081);
 assert_eq!(hp.len(),n(g,"nh_p"));assert_eq!(ho.len(),n(g,"nh_o"));assert!(n(g,"nh_max")>hp.len().max(ho.len()));
 let pb=words(&a["p_off"])[1] as usize;let ob=words(&a["o_off"])[1] as usize;let pi=words(&a["p_idx"]);let oi=words(&a["o_idx"]);let lo=words(&a["p_lower"]);let up=words(&a["p_upper"]);
 assert_eq!(&pi[pb..pb+sp.len()],sp.iter().map(|x|x.1).collect::<Vec<_>>());assert_eq!(&oi[ob..ob+so.len()],so.iter().map(|x|x.1).collect::<Vec<_>>());
 for (k,(r,_)) in sp.iter().enumerate(){assert_eq!(lo[pb+k] as usize,so.partition_point(|x|x.0<*r));assert_eq!(up[pb+k] as usize,so.partition_point(|x|x.0<=*r));}
 let co=words(&a["o_card_off"]);let cp=words(&a["o_card_pos"]);let base=co[53] as usize;assert!(base>0);assert_eq!(co[105] as usize-base,2*so.len());
 for c in 0..52 {let expected:Vec<_>=so.iter().enumerate().filter(|(_,(_,i))|ho[*i as usize].contains(&(c as u32))).map(|(pos,_)|pos as u32).collect();assert_eq!(&cp[co[53+c] as usize..co[54+c] as usize],expected);}
 let same=words(&a["same_p"]);let c1=words(&a["pc1"]);let c2=words(&a["pc2"]);
 for (i,h) in hp.iter().enumerate(){assert_eq!(same[i],ho.iter().position(|x|x==h).map_or(u32::MAX,|i|i as u32));assert_eq!(c1[i],h[0]);assert_eq!(c2[i],h[1]);}
 assert_eq!(n(g,"dynamic_shared_bytes"),4*ho.len()+16*so.len());
 let initial=words(&g["output_initial"]);assert!(initial.iter().all(|x|*x==GUARD));
 let mask:Vec<_>=g["output_active"].as_array().unwrap().iter().map(|x|x.as_bool().unwrap()).collect();let mut expected=vec![false;initial.len()];let slots=words(&a["cfv_slot"]);
 for node in [2usize,5]{let start=slots[node] as usize*n(g,"nh_max");expected[start..start+hp.len()].fill(true);}assert_eq!(mask,expected);
 if g["board_text"]=="AsKsQsJsTs"&&n(g,"target_m")==257 {let i=n(g,"rounding_witness_own_index");assert!(sp.iter().any(|(_,j)|*j as usize==i));for (_,j) in so.iter().take(4){assert!(!hp[i].iter().any(|c|ho[*j as usize].contains(c)));}}
 Ok(())
}
enum Bounds { Wide(CudaSlice<u32>), Narrow(CudaSlice<u16>) }
fn upload_bounds(s:&Arc<CudaStream>,a:&Value,key:&str,narrow:bool)->Result<(Vec<u32>,Bounds)> {
 let h=words(&a[key]);
 let device=if narrow {
  let mut values=Vec::with_capacity(h.len());
  for &value in &h {values.push(u16::try_from(value).map_err(|_| "river rank boundary exceeds u16".to_string())?);}
  let device=s.clone_htod(&values)?;s.synchronize()?;Bounds::Narrow(device)
 } else {Bounds::Wide(s.clone_htod(&h)?)};
 Ok((h,device))
}
fn upload_u32(s:&Arc<CudaStream>,a:&Value,key:&str)->Result<(Vec<u32>,CudaSlice<u32>)>{let h=words(&a[key]);let d=s.clone_htod(&h)?;Ok((h,d))}
fn upload_f32(s:&Arc<CudaStream>,a:&Value,key:&str)->Result<(Vec<f32>,CudaSlice<f32>)>{let h=floats(&words(&a[key]));let d=s.clone_htod(&h)?;Ok((h,d))}
fn run_variant(s:&Arc<CudaStream>,f:&CudaFunction,g:&Value,c:&Value,width:u32,active:&[bool],narrow:bool)->Result<(Vec<u32>,usize,usize,Vec<Value>)> {
 let a=&g["arrays"];
 let (nodes,d_nodes)=upload_u32(s,a,"nodes")?;
 let (win,d_win)=upload_f32(s,a,"node_twin")?;let (lose,d_lose)=upload_f32(s,a,"node_tlose")?;let (tie,d_tie)=upload_f32(s,a,"node_ttie")?;
 let (river,d_river)=upload_u32(s,a,"node_river_slot")?;let (rsrc,d_rsrc)=upload_u32(s,a,"rsrc_o")?;
 let reach=floats(&words(&c["reach_o_bits"]));let d_reach=s.clone_htod(&reach)?;
 let (po,d_po)=upload_u32(s,a,"p_off")?;let (pc,d_pc)=upload_u32(s,a,"p_cnt")?;let (pi,d_pi)=upload_u32(s,a,"p_idx")?;
 let (pl,d_pl)=upload_bounds(s,a,"p_lower",narrow)?;let (pu,d_pu)=upload_bounds(s,a,"p_upper",narrow)?;
 let (oo,d_oo)=upload_u32(s,a,"o_off")?;let (oc,d_oc)=upload_u32(s,a,"o_cnt")?;let (oi,d_oi)=upload_u32(s,a,"o_idx")?;
 let (co,d_co)=upload_u32(s,a,"o_card_off")?;let (cp,d_cp)=upload_u32(s,a,"o_card_pos")?;
 let (same,d_same)=upload_u32(s,a,"same_p")?;let (c1,d_c1)=upload_u32(s,a,"pc1")?;let (c2,d_c2)=upload_u32(s,a,"pc2")?;let (slots,d_slots)=upload_u32(s,a,"cfv_slot")?;
 let initial=words(&g["output_initial"]);let mut d_out=s.clone_htod(&floats(&initial))?;
 let start=n(g,"start") as i32;let count=n(c,"count") as i32;let nhp=n(g,"nh_p") as i32;let nho=n(g,"nh_o") as i32;let nhmax=n(g,"nh_max") as i32;
 let mut launch=s.launch_builder(f);
 launch.arg(&d_nodes).arg(&start).arg(&count).arg(&d_win).arg(&d_lose).arg(&d_tie).arg(&d_river).arg(&d_rsrc).arg(&d_reach)
 .arg(&d_po).arg(&d_pc).arg(&d_pi);
 match &d_pl {Bounds::Wide(d)=>{launch.arg(d);},Bounds::Narrow(d)=>{launch.arg(d);}}
 match &d_pu {Bounds::Wide(d)=>{launch.arg(d);},Bounds::Narrow(d)=>{launch.arg(d);}}
 launch.arg(&d_oo).arg(&d_oc).arg(&d_oi).arg(&d_co).arg(&d_cp)
 .arg(&d_same).arg(&d_c1).arg(&d_c2).arg(&d_slots).arg(&mut d_out).arg(&nhp).arg(&nho).arg(&nhmax);
 unsafe{launch.launch(LaunchConfig{grid_dim:(n(g,"grid_blocks") as u32,1,1),block_dim:(width,1,1),shared_mem_bytes:n(g,"dynamic_shared_bytes") as u32})?;}
 s.synchronize()?;
 let out=bits(&s.clone_dtoh(&d_out)?);guards(&initial,&out,active)?;
 let mut checks=0;let mut input_words=0;let mut snapshots=Vec::new();
 macro_rules! check_u {($h:ident,$d:ident)=>{{let got=s.clone_dtoh(&$d)?;exact(&$h,&got,stringify!($h))?;snapshots.push(json!({"buffer":stringify!($h),"actual_device_words":got}));checks+=1;input_words+=$h.len();}}}
 macro_rules! check_f {($h:ident,$d:ident)=>{{let got=s.clone_dtoh(&$d)?;exact(&bits(&$h),&bits(&got),stringify!($h))?;snapshots.push(json!({"buffer":stringify!($h),"actual_device_words":bits(&got)}));checks+=1;input_words+=$h.len();}}}
 macro_rules! check_bounds {($h:ident,$d:ident)=>{{
  let(got,raw,width):(Vec<u32>,Vec<u8>,u32)=match &$d {
   Bounds::Wide(d)=>{let v=s.clone_dtoh(d)?;let raw=v.iter().flat_map(|x|x.to_le_bytes()).collect();(v,raw,32)},
   Bounds::Narrow(d)=>{let v=s.clone_dtoh(d)?;let raw=v.iter().flat_map(|x|x.to_le_bytes()).collect();(v.into_iter().map(u32::from).collect(),raw,16)}
  };
  exact(&$h,&got,stringify!($h))?;snapshots.push(json!({"buffer":stringify!($h),"actual_device_words":got,"actual_storage_bits":width,"actual_device_bytes":raw}));checks+=1;input_words+=$h.len();
 }}}
 check_u!(nodes,d_nodes);check_f!(win,d_win);check_f!(lose,d_lose);check_f!(tie,d_tie);check_u!(river,d_river);check_u!(rsrc,d_rsrc);check_f!(reach,d_reach);
 check_u!(po,d_po);check_u!(pc,d_pc);check_u!(pi,d_pi);check_bounds!(pl,d_pl);check_bounds!(pu,d_pu);check_u!(oo,d_oo);check_u!(oc,d_oc);check_u!(oi,d_oi);check_u!(co,d_co);check_u!(cp,d_cp);check_u!(same,d_same);check_u!(c1,d_c1);check_u!(c2,d_c2);check_u!(slots,d_slots);
 assert_eq!(checks,21);s.synchronize()?;Ok((out,checks,input_words,snapshots))
}
fn run()->Result<()> {
 // Host verifier injections are not GPU case passes.
 assert!(exact(&[0],&[1],"injection").is_err());assert!(guards(&[GUARD],&[0],&[false]).is_err());
 let corpus:Value=serde_json::from_str(CORPUS)?;let gs=corpus["geometries"].as_array().unwrap();let cs=corpus["cases"].as_array().unwrap();assert_eq!(gs.len(),36);assert_eq!(cs.len(),364);
 for g in gs{validate_geometry(g)?;}
 for c in cs {if c["profile"].as_str().unwrap().starts_with("stress_"){continue;}for b in words(&c["reach_o_bits"]){let f=f32::from_bits(b);assert!(f.is_finite()&&f>=0.0);}}
 emit(json!({"stage":"corpus_validated","geometries":36,"comparison_pairs":364,"accepted_rank_oracle":true,"host_verifier_injections_rejected":2,"host_injections_are_gpu_cases":false}))?;
 let ctx=CudaContext::new(0)?;let s=ctx.default_stream();let major=ctx.attribute(cudarc::driver::sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR)?;let minor=ctx.attribute(cudarc::driver::sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR)?;
 let device=ctx.name()?;assert_eq!(device,"NVIDIA GeForce RTX 5090");let arch=format!("compute_{major}{minor}");assert_eq!(arch,"compute_120");
 let load_ptx=|src:&str,name:&str|->Result<_>{let mut out=OpenOptions::new().write(true).create_new(true).open(format!("{name}.ptx"))?;out.write_all(src.as_bytes())?;out.flush()?;Ok(ctx.load_module(cudarc::nvrtc::Ptx::from_src(src))?)};
 let bm=load_ptx(include_str!("baseline.ptx"),"baseline")?;let cm=load_ptx(include_str!("candidate.ptx"),"candidate")?;let bf=bm.load_function("up_show")?;let cf=cm.load_function("up_show")?;
 let shared_limit=ctx.attribute(cudarc::driver::sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK)?;
 let thread_limit=ctx.attribute(cudarc::driver::sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK)?;
 for (f,width) in [(&bf,128),(&cf,128)]{assert!(f.max_threads_per_block()?>=width&&thread_limit>=width);for g in gs{assert!(f.shared_size_bytes()? as usize+n(g,"dynamic_shared_bytes")<=shared_limit as usize);}}
 emit(json!({"stage":"device","max_shared_bytes_per_block_default":shared_limit,"max_threads_per_block":thread_limit,"device":device,"architecture":arch,"baseline_source_fnv1a64":fnv(BASELINE.bytes()),"candidate_source_fnv1a64":fnv(CANDIDATE.bytes()),"baseline_physical_threads":128,"candidate_physical_threads":128,"logical_scan_threads":128,"compile_options":"No NVRTC rerun: same sealedcompute120PTX from the sole resource probe, originally arch-only production defaults"}))?;
 let mut file=BufWriter::new(OpenOptions::new().write(true).create_new(true).open("raw-results.jsonl")?);
 let mut active_words=0;let mut guard_checks=0;let mut input_checks=0;let mut input_words=0;let mut overwritten=0;let mut nonzero=0;let mut launches=0;let mut nonfinite_words=0;let mut witness_checks=0;
 for c in cs {
  let g=gs.iter().find(|g|g["id"]==c["geometry"]).unwrap();let count=n(c,"count");assert!(count==0||count==2);
  let active:Vec<bool>=g["output_active"].as_array().unwrap().iter().map(|v|count>0&&v.as_bool().unwrap()).collect();
  let (before,bc,bw,bs)=run_variant(&s,&bf,g,c,128,&active,false)?;launches+=1;
  let (after,cc,cw,csnap)=run_variant(&s,&cf,g,c,128,&active,true)?;launches+=1;
  exact(&before,&after,c["id"].as_str().unwrap())?;
  let actual:Vec<u32>=before.iter().zip(&active).filter(|(_,a)|**a).map(|(v,_)|*v).collect();let changed=actual.iter().filter(|v|**v!=GUARD).count();assert_eq!(changed,actual.len(),"active stale guard remains");
  if c["profile"]=="all_zero"||n(g,"m_p")==0||n(g,"m_o")==0 {assert!(actual.iter().all(|v|*v==0),"expected zero CFV");}
  let nz=actual.iter().filter(|v|**v!=GUARD&&(**v&0x7fffffff)!=0).count();
  if count>0&&n(g,"target_m")>=127&&c["profile"]!="all_zero"&&c["profile"]!="stress_signed_zero" {assert!(nz>0,"nonzero payoff anti-vacuity");}
  if count>0&&g["board_text"]=="AsKsQsJsTs"&&n(g,"target_m")==257&&c["profile"]=="sparse_rounding_witness" {
   let i=n(g,"rounding_witness_own_index");let slot=words(&g["arrays"]["cfv_slot"])[5] as usize;assert_eq!(before[slot*n(g,"nh_max")+i],(-0.25f32).to_bits(),"frozen sparse total witness");witness_checks+=1;
  }
  let nf=nonfinite(&actual);nonfinite_words+=n(&nf,"count");let ac=actual.len();let gc=2*(before.len()-ac);active_words+=ac;guard_checks+=gc;input_checks+=bc+cc;input_words+=bw+cw;overwritten+=changed;nonzero+=nz;
  let row=json!({"stage":"full_show_exact","case_id":c["id"],"geometry":g["id"],"board":g["board_text"],"target_m":g["target_m"],"player":g["player"],"profile":c["profile"],"count":count,"m_p":g["m_p"],"m_o":g["m_o"],"nh_p":g["nh_p"],"nh_o":g["nh_o"],"baseline_dynamic_shared_bytes":g["dynamic_shared_bytes"],"candidate_dynamic_shared_bytes":g["dynamic_shared_bytes"],"active_words":ac,"guard_word_checks":gc,"device_input_buffer_checks":bc+cc,"device_input_word_checks":bw+cw,"active_overwritten_words":changed,"nonzero_active_words":nz,"all_output_bits_exact":true,"input_bits_unchanged":true,"nonfinite_active":nf,"baseline_output_fnv1a64":hash(&before),"candidate_output_fnv1a64":hash(&after)});
  save(&json!({"record":row,"baseline_output_bits":before,"candidate_output_bits":after,"baseline_actual_device_inputs":bs,"candidate_actual_device_inputs":csnap}),&mut file)?;emit(row)?;
 }
 assert_eq!(launches,728);assert_eq!(active_words,197240);assert_eq!(guard_checks,1292824);assert_eq!(input_checks,15288);assert_eq!(witness_checks,2);assert!(overwritten>0&&nonzero>0);
 file.flush()?;file.get_ref().sync_all()?;s.synchronize()?;ctx.check_err()?;
 emit(json!({"stage":"complete","comparison_pairs":364,"kernel_launches":launches,"active_words_compared":active_words,"output_guard_word_checks":guard_checks,"device_input_buffer_checks":input_checks,"device_input_word_checks":input_words,"active_overwritten_words":overwritten,"nonzero_active_words":nonzero,"nonfinite_active_words":nonfinite_words,"rounding_witness_checks":witness_checks,"all_output_bits_exact":true,"all_inputs_unchanged":true,"performance_measurement":false,"solver_executions":0,"candidate_accepted":false}))?;Ok(())
}
fn main(){if let Err(error)=run(){let _=emit(json!({"stage":"invalid","error":error.to_string(),"candidate_accepted":false}));eprintln!("{error}");std::process::exit(1);}}
