//! Independent-gap stopping for finite sampled CFR, never used by production.
#[cfg(not(feature="gpu"))]fn main(){panic!("requires gpu");}
#[cfg(feature="gpu")]
fn main()->Result<(),Box<dyn std::error::Error>>{
 use cudarc::driver::{CudaContext,LaunchConfig,PushKernelArg};use serde_json::{Value,json};use std::time::Instant;
 fn e(x:impl std::fmt::Debug)->String{format!("{x:?}")}
 struct Game{actor:Vec<i32>,arity:Vec<i32>,child:Vec<i32>,info:Vec<i32>,offset:Vec<i32>,chance:Vec<f64>,utility:Vec<f64>}
 fn eval(g:&Game,policy:&[f64])->([f64;2],[f64;2]){
  let p=|d:usize,n:usize,a:usize|policy[g.offset[g.info[d*19+n]as usize]as usize+a];
  let mut ev=[0.;2];let mut br=[0.;2];
  for player in 0..2usize{
   let mut value=[[0.;19];24];let mut best=[[0.;19];24];let mut reach=[[0.;19];24];
   for d in 0..24{reach[d][0]=g.chance[d];}
   for n in 0..19{for d in 0..24{for a in 0..g.arity[n]as usize{let c=g.child[n*3+a]as usize;
    reach[d][c]=reach[d][n]*if g.actor[n]==player as i32{1.}else{p(d,n,a)};}}}
   for n in (0..19).rev(){let k=g.arity[n]as usize;
    if k==0{for d in 0..24{value[d][n]=g.utility[(d*19+n)*2+player];best[d][n]=value[d][n];}continue;}
    for d in 0..24{for a in 0..k{value[d][n]+=p(d,n,a)*value[d][g.child[n*3+a]as usize];}}
    if g.actor[n]==player as i32{
     for info in 0..60{let ds:Vec<_>=(0..24).filter(|&d|g.info[d*19+n]==info as i32).collect();if ds.is_empty(){continue;}
      let mut action=0;let mut highest=f64::NEG_INFINITY;
      for a in 0..k{let mut q=0.;for &d in &ds{q+=reach[d][n]*best[d][g.child[n*3+a]as usize];}if q>highest{highest=q;action=a;}}
      for d in ds{best[d][n]=best[d][g.child[n*3+action]as usize];}
     }
    }else{for d in 0..24{for a in 0..k{best[d][n]+=p(d,n,a)*best[d][g.child[n*3+a]as usize];}}}
   }
   for d in 0..24{ev[player]+=g.chance[d]*value[d][0];br[player]+=g.chance[d]*best[d][0];}
   assert!(br[player]>=ev[player]-1e-10);
  }(ev,br)
 }
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3);assert!(!std::path::Path::new(&args[2]).exists());
 let data:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
 let ints=|v:&Value|->Vec<i32>{v.as_array().unwrap().iter().map(|x|x.as_i64().unwrap()as i32).collect()};
 let mut game=Game{actor:ints(&data["actors"]),arity:ints(&data["arity"]),child:data["children"].as_array().unwrap().iter().flat_map(&ints).collect(),
  info:data["deal_infos"].as_array().unwrap().iter().flat_map(&ints).collect(),offset:ints(&data["offsets"]),
  chance:data["probabilities"].as_array().unwrap().iter().map(|x|x.as_f64().unwrap()).collect(),utility:vec![]};
 assert_eq!(game.offset.len(),61);assert_eq!(game.offset[60],128);assert!((game.chance.iter().sum::<f64>()-1.).abs()<1e-12);
 let mut initial=vec![0.;128];for o in game.offset.windows(2){for a in o[0]..o[1]{initial[a as usize]=1./(o[1]-o[0])as f64;}}
 let ctx=CudaContext::new(0).map_err(e)?;let stream=ctx.default_stream();let(ma,mi)=ctx.compute_capability().map_err(e)?;
 let arch:&'static str=Box::leak(format!("compute_{ma}{mi}").into_boxed_str());
 let ptx=cudarc::nvrtc::compile_ptx_with_opts(std::fs::read_to_string(&args[1])?,cudarc::nvrtc::CompileOptions{arch:Some(arch),fmad:Some(false),..Default::default()}).map_err(e)?;
 let module=ctx.load_module(ptx).map_err(e)?;let full=module.load_function("conv_full").map_err(e)?;
 let sampled=module.load_function("conv_sample").map_err(e)?;let reduce=module.load_function("conv_reduce").map_err(e)?;
 let da=stream.clone_htod(&game.actor).map_err(e)?;let dn=stream.clone_htod(&game.arity).map_err(e)?;let dc=stream.clone_htod(&game.child).map_err(e)?;
 let di=stream.clone_htod(&game.info).map_err(e)?;let doff=stream.clone_htod(&game.offset).map_err(e)?;let dq=stream.clone_htod(&game.chance).map_err(e)?;
 let mut runs=vec![];
 for case in 0..2usize{
  game.utility=data["cases"][case]["utilities"].as_array().unwrap().iter().flat_map(|d|d.as_array().unwrap().iter().flat_map(|n|n.as_array().unwrap().iter().map(|x|x.as_f64().unwrap()))).collect();
  let du=stream.clone_htod(&game.utility).map_err(e)?;
  let(initial_ev,initial_br)=eval(&game,&initial);
  for player in 0..2{assert!((initial_ev[player]-data["uniform_evaluation"][case]["ev"][player].as_f64().unwrap()).abs()<1e-11);
   assert!((initial_br[player]-data["uniform_evaluation"][case]["best_response"][player].as_f64().unwrap()).abs()<1e-11);}
  for seed in [0u64,17,31,47,71]{
   let ns=if seed==0{24i32}else{512i32};let scale=if seed==0{1.}else{2./ns as f64};
   let mut policy=stream.clone_htod(&initial).map_err(e)?;let mut regret=stream.alloc_zeros::<f64>(128).map_err(e)?;let mut average=stream.alloc_zeros::<f64>(128).map_err(e)?;
   let mut delta=stream.alloc_zeros::<f64>(ns as usize*128).map_err(e)?;let mut increment=stream.alloc_zeros::<f64>(ns as usize*128).map_err(e)?;
   let started=Instant::now();let mut checkpoints=vec![];let mut streak=0;let mut stopped=false;
   for t in 1..=16000u64{
    let round_seed=seed.wrapping_add(t.wrapping_mul(0x9e3779b97f4a7c15));
    unsafe{
     if seed==0{stream.launch_builder(&full).arg(&da).arg(&dn).arg(&dc).arg(&di).arg(&doff).arg(&policy).arg(&du).arg(&dq).arg(&mut delta).arg(&mut increment)
      .launch(LaunchConfig::for_num_elems(24)).map_err(e)?;}
     else{stream.launch_builder(&sampled).arg(&ns).arg(&round_seed).arg(&da).arg(&dn).arg(&dc).arg(&di).arg(&doff).arg(&policy).arg(&du).arg(&dq).arg(&mut delta).arg(&mut increment)
      .launch(LaunchConfig::for_num_elems(ns as u32)).map_err(e)?;}
     stream.launch_builder(&reduce).arg(&ns).arg(&scale).arg(&doff).arg(&delta).arg(&increment).arg(&mut regret).arg(&mut average).arg(&mut policy)
      .launch(LaunchConfig::for_num_elems(60)).map_err(e)?;
    }
    if ![1,10,50,100,250,500,1000,2000,4000,8000,16000].contains(&t){continue;}
    let av=stream.clone_dtoh(&average).map_err(e)?;let mut normalized=initial.clone();
    for o in game.offset.windows(2){let lo=o[0]as usize;let hi=o[1]as usize;let sum:f64=av[lo..hi].iter().sum();if sum>0.{for a in lo..hi{normalized[a]=av[a]/sum;}}}
    assert!(normalized.iter().all(|x|x.is_finite()&&*x>=0.&&*x<=1.+1e-12));
    let(ev,br)=eval(&game,&normalized);let gap=br[0]+br[1]-ev[0]-ev[1];if gap<=0.01{streak+=1;}else{streak=0;}
    let state=if t==1||(seed==0&&t==10){json!({"regret":stream.clone_dtoh(&regret).map_err(e)?,"average":av,"policy":stream.clone_dtoh(&policy).map_err(e)?})}else{Value::Null};
    let checkpoint=json!({"iteration":t,"elapsed_seconds":started.elapsed().as_secs_f64(),"ev":ev,"best_response":br,"gap":gap,"average_policy":normalized,
     "target_streak":streak,"state_control":state});println!("case={} seed={} iteration={} gap={:.9}",case,seed,t,gap);checkpoints.push(checkpoint);
    if streak>=2{stopped=true;break;}
   }
   runs.push(json!({"rake":case==1,"case":case,"seed":seed,"method":if seed==0{"full_chance_and_actions"}else{"external_sampling"},
    "batch_traversals":if seed==0{0}else{ns},"target_reached_twice":stopped,"seconds":started.elapsed().as_secs_f64(),"checkpoints":checkpoints}));
  }
 }
 let result=json!({"passed":true,"runs":runs,"target_gap":0.01,"consecutive_target_checks":2,"max_iterations":16000,
  "arithmetic":"f64 with fmad disabled; signed regret matching; fixed strategy in each batch; opponent-pass sampled averages",
  "scope":"Finite nonphysical oracle game, exact full-chance best responses grouped by observable information. Not real-poker convergence or speed claims.",
  "production_modified":false});std::fs::write(&args[2],serde_json::to_vec_pretty(&result)?)?;Ok(())
}
