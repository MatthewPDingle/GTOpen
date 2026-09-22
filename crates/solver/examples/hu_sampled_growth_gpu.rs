//! Bounded fresh-deal growth measurement using the qualified poker kernel.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod reference;
#[cfg(not(feature="gpu"))]fn main(){panic!("requires gpu");}
#[cfg(feature="gpu")]
fn main()->Result<(),Box<dyn std::error::Error>>{
 use cudarc::driver::{CudaContext,LaunchConfig,PushKernelArg};use serde_json::{Value,json};
 use reference::*;use std::{time::Instant,io::{Write,BufWriter},collections::BTreeSet};
 fn e(x:impl std::fmt::Debug)->String{format!("{x:?}")}
 fn street(k:Key)->usize{if k.0>>63==0{0}else if (k.1>>30)&63==63{1}else if(k.1>>36)&63==63{2}else{3}}
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),8);
 for p in &args[5..]{assert!(!std::path::Path::new(p).exists());}
 let all_started=Instant::now();let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
 assert_eq!(context["positions"],json!(["BB","BTN"]));let game=Game::new(&context);assert_eq!(game.kinds.len(),15);
 let bytes=std::fs::read(&args[1])?;assert_eq!(&bytes[..8],b"GTDEAL01");let deal_count=u64::from_le_bytes(bytes[8..16].try_into().unwrap())as usize;
 assert_eq!(deal_count,262144);assert_eq!(bytes.len(),16+9*deal_count);
 for cs in bytes[16..].chunks_exact(9){let mut mask=0u64;for &c in cs{assert!(c<52&&mask&(1u64<<c)==0);mask|=1u64<<c;}}
 let source=std::fs::read_to_string(&args[2])?+"\n"+&std::fs::read_to_string(&args[3])?+"\n"+&std::fs::read_to_string(&args[4])?;
 let ctx=CudaContext::new(0).map_err(e)?;let stream=ctx.default_stream();let(ma,mi)=ctx.compute_capability().map_err(e)?;
 let arch:&'static str=Box::leak(format!("compute_{ma}{mi}").into_boxed_str());let compile=Instant::now();
 let ptx=cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),fmad:Some(false),..Default::default()}).map_err(e)?;
 let module=ctx.load_module(ptx).map_err(e)?;let kernel=module.load_function("poker_walk").map_err(e)?;let compile_seconds=compile.elapsed().as_secs_f64();
 let dk=stream.clone_htod(&game.kinds).map_err(e)?;let da=stream.clone_htod(&game.actors).map_err(e)?;let dn=stream.clone_htod(&game.arities).map_err(e)?;
 let dc=stream.clone_htod(&game.children).map_err(e)?;let dcfg=stream.clone_htod(&game.constants).map_err(e)?;let doff=stream.clone_htod(&game.offsets).map_err(e)?;
 let ns=4096i32;let cap=512i32;let slots=(ns*cap)as usize;
 let mut ok=stream.alloc_zeros::<u64>(slots*2).map_err(e)?;let mut ot=stream.alloc_zeros::<i32>(slots).map_err(e)?;
 let mut od=stream.alloc_zeros::<f64>(slots*4).map_err(e)?;let mut oc=stream.alloc_zeros::<i32>(ns as usize).map_err(e)?;let mut ov=stream.alloc_zeros::<f64>(ns as usize).map_err(e)?;
 let mut progress=std::fs::OpenOptions::new().write(true).create_new(true).open(&args[6])?;
 let mut table=Table::new();let mut by_street=[0usize;4];let mut rounds=vec![];let mut completed=0usize;
 let mut accepted_records=0usize;let mut max_error=0f64;let mut stop="sample_budget";let max_entries=8_000_000usize;
 let training_started=Instant::now();let mut rejected:Option<Value>=None;
 for round in 0..128usize{
  if training_started.elapsed().as_secs_f64()>180.{stop="soft_time_budget";break;}
  let started=Instant::now();let before=table.len();let mut keys=Vec::with_capacity((before*2).max(2));let mut policy=Vec::with_capacity((before*4).max(4));
  for(&(hi,lo),v)in &table{keys.extend([hi,lo]);policy.extend(v.policy());}
  if keys.is_empty(){keys.extend([0,0]);policy.extend([0.;4]);}
  let dkeys=stream.clone_htod(&keys).map_err(e)?;let dpolicy=stream.clone_htod(&policy).map_err(e)?;
  let first=16+round*2048*9;let batch=&bytes[first..first+2048*9];let dd=stream.clone_htod(batch).map_err(e)?;
  let nt=before as i32;let seed=2026092204u64+round as u64*1000003;let prepare_seconds=started.elapsed().as_secs_f64();
  let gpu_start=Instant::now();
  unsafe{stream.launch_builder(&kernel).arg(&ns).arg(&cap).arg(&nt).arg(&seed).arg(&dd).arg(&dk).arg(&da).arg(&dn).arg(&dc).arg(&dcfg).arg(&doff)
   .arg(&dkeys).arg(&dpolicy).arg(&mut ok).arg(&mut ot).arg(&mut od).arg(&mut oc).arg(&mut ov).launch(LaunchConfig::for_num_elems(ns as u32)).map_err(e)?;}
  let counts=stream.clone_dtoh(&oc).map_err(e)?;let values=stream.clone_dtoh(&ov).map_err(e)?;let gpu_root_seconds=gpu_start.elapsed().as_secs_f64();
  assert!(counts.iter().all(|&c|c>0&&c<=cap),"hard traversal capacity failure");assert!(values.iter().all(|v|v.is_finite()));
  let outkeys=stream.clone_dtoh(&ok).map_err(e)?;let tags=stream.clone_dtoh(&ot).map_err(e)?;let deltas=stream.clone_dtoh(&od).map_err(e)?;
  let gpu_all_output_seconds=gpu_start.elapsed().as_secs_f64();
  // Kernel and reference are frozen from full six-batch qualification. Retain
  // eight complete scalar traversal checks per new batch as a live control.
  for sample in 0..8usize{let deal:[u8;9]=batch[(sample/2)*9..(sample/2+1)*9].try_into().unwrap();
   let mut walk=Walk::new(&game,&table,&deal,sample%2,sample_seed(seed,sample));let value=walk.pre(0);
   max_error=max_error.max((value-values[sample]).abs());assert_eq!(counts[sample]as usize,walk.records.len());
   for(i,want)in walk.records.iter().enumerate(){let j=sample*cap as usize+i;assert_eq!((outkeys[j*2],outkeys[j*2+1]),want.key);assert_eq!(tags[j],want.tag);
    for a in 0..4{max_error=max_error.max((deltas[j*4+a]-want.values[a]).abs());}}
  }assert!(max_error<1e-9);
  let mut new=BTreeSet::new();let mut record_counts=[0usize;4];let mut hits=[0usize;4];let mut all_keys=BTreeSet::new();
  for sample in 0..ns as usize{for i in 0..counts[sample]as usize{let j=sample*cap as usize+i;let k=(outkeys[j*2],outkeys[j*2+1]);let s=street(k);
   let n=tags[j].unsigned_abs()as usize;assert!((1..=4).contains(&n));assert!(deltas[j*4..j*4+n].iter().all(|v|v.is_finite()));
   record_counts[s]+=1;all_keys.insert(k);
   if let Some(v)=table.get(&k){assert_eq!(v.n,n);hits[s]+=1;}else{new.insert(k);}
  }}
  let nrecords:usize=record_counts.iter().sum();let mut new_counts=[0usize;4];for &k in &new{new_counts[street(k)]+=1;}
  if before+new.len()>max_entries{stop="entry_capacity_before_batch_update";
   rejected=Some(json!({"round":round,"unapplied_deals":2048,"unapplied_records":nrecords,"new_infosets":new.len(),"would_be_infosets":before+new.len()}));break;}
  for sample in 0..ns as usize{for i in 0..counts[sample]as usize{let j=sample*cap as usize+i;let k=(outkeys[j*2],outkeys[j*2+1]);let n=tags[j].unsigned_abs()as usize;
   let v=table.entry(k).or_insert(Entry{n,regret:[0.;4],average:[0.;4]});assert_eq!(v.n,n);
   for a in 0..n{if tags[j]>0{v.regret[a]+=deltas[j*4+a];}else{v.average[a]+=deltas[j*4+a];}}
  }}
  assert_eq!(table.len(),before+new.len());for s in 0..4{by_street[s]+=new_counts[s];}
  completed+=2048;accepted_records+=nrecords;
  let row=json!({"round":round,"completed_deals":completed,"traversals":ns,"records":nrecords,"record_counts_by_street":record_counts,
   "existing_lookup_hits_by_street":hits,"new_infosets_by_street":new_counts,"cumulative_infosets_by_street":by_street,
   "input_infosets":before,"output_infosets":table.len(),"repeated_key_occurrences":nrecords-all_keys.len(),
   "maximum_records_per_traversal":counts.iter().max(),"prepare_and_upload_seconds":prepare_seconds,"gpu_and_root_readback_seconds":gpu_root_seconds,
   "gpu_and_all_output_readback_seconds":gpu_all_output_seconds,"full_batch_seconds":started.elapsed().as_secs_f64(),
   "elapsed_training_seconds":training_started.elapsed().as_secs_f64(),"maximum_live_reference_error":max_error});
  writeln!(progress,"{}",row)?;progress.flush()?;println!("{}",row);rounds.push(row);
 }
 let training_seconds=training_started.elapsed().as_secs_f64();let save_start=Instant::now();
 let cp=std::path::Path::new(&args[7]);std::fs::create_dir_all(cp.parent().unwrap())?;
 let mut writer=BufWriter::with_capacity(16*1024*1024,std::fs::OpenOptions::new().write(true).create_new(true).open(cp)?);
 writer.write_all(b"GTSAMP01")?;for v in [rounds.len()as u64,completed as u64,table.len()as u64]{writer.write_all(&v.to_le_bytes())?;}
 // Complete signed-regret and average state retained, with no row eviction.
 for(&(hi,lo),v)in &table{for x in [hi,lo,v.n as u64]{writer.write_all(&x.to_le_bytes())?;}
  for &x in v.regret.iter().chain(v.average.iter()){assert!(x.is_finite());writer.write_all(&x.to_le_bytes())?;}}
 writer.flush()?;drop(writer);let save_seconds=save_start.elapsed().as_secs_f64();
 let result=json!({"passed":true,"stop_reason":stop,"completed_deals":completed,"completed_traversals":completed*2,"completed_batches":rounds.len(),
  "accepted_records":accepted_records,"final_infosets":table.len(),"infosets_by_street":by_street,"street_order":["preflop","flop","turn","river"],
  "entry_capacity":max_entries,"rejected_batch":rejected,"rounds":rounds,"maximum_live_reference_error":max_error,
  "timing":{"compile_seconds":compile_seconds,"training_seconds":training_seconds,"checkpoint_seconds":save_seconds,"total_process_seconds":all_started.elapsed().as_secs_f64()},
  "state_bytes":std::fs::metadata(cp)?.len(),"checkpoint":args[7],"record_buffer_bytes":slots*52,
  "scope":"Fresh-deal bounded resource test using qualified exact-observation sampled poker kernel. No eviction, no support narrowing. Eight scalar controls per batch, not full independent strategy evaluation.",
  "timing_limits":"Training wall time includes table preparation, transfers, GPU work, scalar spot controls, lookup census and host reduction; excludes separately measured deal generation, compilation and checkpoint. Diagnostic overhead remains.",
  "production_modified":false,"convergence_qualified":false});
 std::fs::write(&args[5],serde_json::to_vec_pretty(&result)?)?;println!("STOP {} entries={} deals={}",stop,table.len(),completed);Ok(())
}
