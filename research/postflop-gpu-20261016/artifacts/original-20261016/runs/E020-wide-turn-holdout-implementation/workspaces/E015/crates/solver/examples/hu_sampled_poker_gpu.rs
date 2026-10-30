//! Integrated research-only poker sampling/traversal/table-update qualification.
#[path="research_sampled/state.rs"] mod state;
#[path="research_sampled/poker_reference_v1.rs"] mod reference;
#[cfg(not(feature="gpu"))]fn main(){panic!("requires gpu");}
#[cfg(feature="gpu")]
fn main()->Result<(),Box<dyn std::error::Error>>{
 use cudarc::driver::{CudaContext,LaunchConfig,PushKernelArg};
 use serde_json::{Value,json};use reference::*;use std::time::Instant;
 fn e(x:impl std::fmt::Debug)->String{format!("{x:?}")}
 fn accumulate(table:&mut Table,record:&Record){
  let n=record.tag.unsigned_abs() as usize;let entry=table.entry(record.key).or_insert(Entry{n,regret:[0.;4],average:[0.;4]});assert_eq!(entry.n,n);
  for a in 0..n{if record.tag>0{entry.regret[a]+=record.values[a];}else{entry.average[a]+=record.values[a];}}
 }
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),6);assert!(!std::path::Path::new(&args[5]).exists());
 let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;let game=Game::new(&context);
 assert_eq!(game.kinds.len(),15);assert_eq!(context["positions"],json!(["BB","BTN"]));
 let fixture:Value=serde_json::from_slice(&std::fs::read(&args[1])?)?;
 let deals:Vec<[u8;9]>=fixture["deals"].as_array().unwrap().iter().map(|v|{
  let a:Vec<_>=v.as_array().unwrap().iter().map(|c|c.as_u64().unwrap() as u8).collect();let x:[u8;9]=a.try_into().unwrap();
  let mut mask=0u64;for c in x{assert!(c<52&&mask&(1u64<<c)==0);mask|=1u64<<c;}x}).collect();assert_eq!(deals.len(),8192);
 // Observation identity controls: hidden opponent/future cards and flop listing
 // order cannot split a strategy. Own cards, branch and action history must.
 let d=deals[0];let mut other=d;other.swap(2,7);other.swap(3,8);
 assert_eq!(key(&d,0,Some(0),0,0,0),key(&other,0,Some(0),0,0,0));
 assert_eq!(key(&d,0,None,2,0,1),key(&other,0,None,2,0,1));
 other=d;other.swap(4,6);assert_eq!(key(&d,0,None,2,0,1),key(&other,0,None,2,0,1));
 other=d;other.swap(0,1);assert_eq!(key(&d,0,None,2,0,1),key(&other,0,None,2,0,1));
 other=d;other.swap(0,2);assert_ne!(key(&d,0,None,2,0,1),key(&other,0,None,2,0,1));
 assert_ne!(key(&d,0,None,2,0,1),key(&d,0,None,5,0,1));
 assert_ne!(key(&d,0,None,2,0,1),key(&d,0,None,2,0,9));
 assert_ne!(key(&d,0,None,2,0,1),key(&d,0,None,2,1,1));
 let source=std::fs::read_to_string(&args[2])?+"\n"+&std::fs::read_to_string(&args[3])?+"\n"+&std::fs::read_to_string(&args[4])?;
 let ctx=CudaContext::new(0).map_err(e)?;let stream=ctx.default_stream();let(ma,mi)=ctx.compute_capability().map_err(e)?;
 let arch:&'static str=Box::leak(format!("compute_{ma}{mi}").into_boxed_str());let compile_start=Instant::now();
 let ptx=cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),fmad:Some(false),..Default::default()}).map_err(e)?;
 let module=ctx.load_module(ptx).map_err(e)?;let kernel=module.load_function("poker_walk").map_err(e)?;let compile_seconds=compile_start.elapsed().as_secs_f64();
 let dk=stream.clone_htod(&game.kinds).map_err(e)?;let da=stream.clone_htod(&game.actors).map_err(e)?;let dn=stream.clone_htod(&game.arities).map_err(e)?;
 let dc=stream.clone_htod(&game.children).map_err(e)?;let dcfg=stream.clone_htod(&game.constants).map_err(e)?;let doff=stream.clone_htod(&game.offsets).map_err(e)?;
 let ns=4096i32;let cap=512i32;let slots=(ns*cap)as usize;
 let mut ok=stream.alloc_zeros::<u64>(slots*2).map_err(e)?;let mut ot=stream.alloc_zeros::<i32>(slots).map_err(e)?;
 let mut od=stream.alloc_zeros::<f64>(slots*4).map_err(e)?;let mut oc=stream.alloc_zeros::<i32>(ns as usize).map_err(e)?;let mut ov=stream.alloc_zeros::<f64>(ns as usize).map_err(e)?;
 let mut table=Table::new();let mut oracle=Table::new();let mut rounds=vec![];let mut branches=std::collections::BTreeSet::new();
 let mut capacity_control=false;let mut repeated_exact=false;let mut total_records=0usize;let mut max_error=0f64;
 for (round,&start)in [0usize,0,2048,4096,6144,6144].iter().enumerate(){
  let started=Instant::now();assert!(table.len()<1_000_000);let input_count=table.len();
  let mut keys=vec![];let mut policy=vec![];let mut zero_entries=0;
  for(&(hi,lo),entry)in &table{keys.extend([hi,lo]);let p=entry.policy();zero_entries+=p[..entry.n].iter().filter(|&&v|v==0.).count();policy.extend(p);}
  if keys.is_empty(){keys.extend([0,0]);policy.extend([0.;4]);}
  let dkeys=stream.clone_htod(&keys).map_err(e)?;let dpolicy=stream.clone_htod(&policy).map_err(e)?;
  let flat:Vec<_>=deals[start..start+2048].iter().flatten().copied().collect();let dd=stream.clone_htod(&flat).map_err(e)?;
  let nt=table.len()as i32;let seed=2026092202u64+round as u64*1000003;
  let gpu_start=Instant::now();
  unsafe{stream.launch_builder(&kernel).arg(&ns).arg(&cap).arg(&nt).arg(&seed).arg(&dd).arg(&dk).arg(&da).arg(&dn).arg(&dc).arg(&dcfg).arg(&doff)
   .arg(&dkeys).arg(&dpolicy).arg(&mut ok).arg(&mut ot).arg(&mut od).arg(&mut oc).arg(&mut ov).launch(LaunchConfig::for_num_elems(ns as u32)).map_err(e)?;}
  let counts=stream.clone_dtoh(&oc).map_err(e)?;let values=stream.clone_dtoh(&ov).map_err(e)?;let gpu_seconds=gpu_start.elapsed().as_secs_f64();
  assert!(counts.iter().all(|&c|c>0&&c<=cap),"hard traversal capacity failure");
  let outkeys=stream.clone_dtoh(&ok).map_err(e)?;let tags=stream.clone_dtoh(&ot).map_err(e)?;let deltas=stream.clone_dtoh(&od).map_err(e)?;
  assert_eq!(stream.clone_dtoh(&dpolicy).map_err(e)?,policy);assert_eq!(stream.clone_dtoh(&dkeys).map_err(e)?,keys);
  if round==0{
   unsafe{stream.launch_builder(&kernel).arg(&ns).arg(&cap).arg(&nt).arg(&seed).arg(&dd).arg(&dk).arg(&da).arg(&dn).arg(&dc).arg(&dcfg).arg(&doff)
    .arg(&dkeys).arg(&dpolicy).arg(&mut ok).arg(&mut ot).arg(&mut od).arg(&mut oc).arg(&mut ov).launch(LaunchConfig::for_num_elems(ns as u32)).map_err(e)?;}
   assert_eq!(counts,stream.clone_dtoh(&oc).map_err(e)?);assert_eq!(outkeys,stream.clone_dtoh(&ok).map_err(e)?);assert_eq!(tags,stream.clone_dtoh(&ot).map_err(e)?);
   for(a,b)in deltas.iter().zip(stream.clone_dtoh(&od).map_err(e)?){assert_eq!(a.to_bits(),b.to_bits());}
   for(a,b)in values.iter().zip(stream.clone_dtoh(&ov).map_err(e)?){assert_eq!(a.to_bits(),b.to_bits());}repeated_exact=true;
   let tiny=1i32;
   unsafe{stream.launch_builder(&kernel).arg(&ns).arg(&tiny).arg(&nt).arg(&seed).arg(&dd).arg(&dk).arg(&da).arg(&dn).arg(&dc).arg(&dcfg).arg(&doff)
    .arg(&dkeys).arg(&dpolicy).arg(&mut ok).arg(&mut ot).arg(&mut od).arg(&mut oc).arg(&mut ov).launch(LaunchConfig::for_num_elems(ns as u32)).map_err(e)?;}
   assert!(stream.clone_dtoh(&oc).map_err(e)?.contains(&-1));assert_eq!(stream.clone_dtoh(&dpolicy).map_err(e)?,policy);capacity_control=true;
  }
  let mut additions=Vec::new();let mut oracle_additions=Vec::new();let mut unique=std::collections::BTreeSet::new();let mut lookup_hits=0;
  let mut visited_pre=std::collections::BTreeSet::new();
  for sample in 0..ns as usize{
   let mut walk=Walk::new(&game,&oracle,&deals[start+sample/2],sample%2,sample_seed(seed,sample));let value=walk.pre(0);
   max_error=max_error.max((value-values[sample]).abs());assert_eq!(walk.records.len(),counts[sample] as usize);
   for(i,want)in walk.records.iter().enumerate(){let j=sample*cap as usize+i;let got=Record{key:(outkeys[j*2],outkeys[j*2+1]),tag:tags[j],values:deltas[j*4..j*4+4].try_into().unwrap()};
    assert_eq!(got.key,want.key);assert_eq!(got.tag,want.tag);
    for(a,b)in got.values.iter().zip(want.values){assert!(a.is_finite());max_error=max_error.max((a-b).abs());}
    if got.key.0>>63!=0{branches.insert(got.key.0&15);}else{visited_pre.insert(got.key.0-1);}
    lookup_hits+=table.contains_key(&got.key) as usize;unique.insert(got.key);additions.push(got);
   }oracle_additions.extend(walk.records);
  }
  assert!(max_error<1e-9,"GPU/reference error {max_error}");
  let nrecords=additions.len();total_records+=nrecords;
  // Both players see the same frozen snapshot. Deterministic sample/preorder
  // reduction applies only after the complete batch; never clip signed regret.
  for record in &additions{accumulate(&mut table,record);}for record in &oracle_additions{accumulate(&mut oracle,record);}
  assert_eq!(table.len(),oracle.len());
  for(k,v)in &table{let w=&oracle[k];assert_eq!(v.n,w.n);for(a,b)in v.regret.iter().chain(v.average.iter()).zip(w.regret.iter().chain(w.average.iter())){assert!((a-b).abs()<1e-8);}}
  let output=json!({"round":round,"deal_start":start,"traversals":ns,"records":nrecords,"maximum_records_per_traversal":counts.iter().max(),
   "input_infosets":input_count,"output_infosets":table.len(),"unique_batch_infosets":unique.len(),"repeated_key_occurrences":nrecords-unique.len(),
   "lookup_hits":lookup_hits,"zero_probability_input_actions":zero_entries,"visited_preflop_nodes":visited_pre,"gpu_launch_and_root_readback_seconds":gpu_seconds,
   "full_validation_round_seconds":started.elapsed().as_secs_f64(),"maximum_record_or_root_error":max_error});println!("{}",output);rounds.push(output);
 }
 assert_eq!(branches.into_iter().collect::<Vec<_>>(),vec![2,5,8]);assert!(rounds[1]["lookup_hits"].as_u64().unwrap()>0);
 assert!(rounds[1]["zero_probability_input_actions"].as_u64().unwrap()>0);
 let result=json!({"passed":true,"rounds":rounds,"total_traversals":6*ns,"total_records":total_records,"final_infosets":table.len(),
  "frozen_repeat_bit_exact":repeated_exact,"hard_capacity_negative_control":capacity_control,"exact_observation_key_controls":true,
  "maximum_record_or_root_error":max_error,"compile_seconds":compile_seconds,"record_buffer_bytes":slots*52,
  "packed_strategy_payload_bytes":table.len()*(std::mem::size_of::<Key>()+std::mem::size_of::<Entry>()),
  "scope":"Complete 15-node preflop subtree and all three postflop branches. 8192 physical deals, two repeated batches, six frozen update rounds. Scalar/GPU agreement; not convergence or full-memory feasibility.",
  "limits":"CPU deal generation, sorted table upload, output readback and host deterministic reduction are included in validation round time; kernel timing alone is not training throughput. Full private-card keys can grow without bound until explicit resource stop. Earlier folded cards omitted; fixed incoming ranges and 112-flop panel.",
  "production_modified":false,"strategy_accuracy_claim":false});
 std::fs::write(&args[5],serde_json::to_vec_pretty(&result)?)?;println!("{}",result);Ok(())
}
