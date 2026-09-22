//! GPU transition check for every betting-history template of the BB study.
#[path="research_sampled/state.rs"] mod state;
#[cfg(not(feature="gpu"))] fn main(){panic!("requires --features gpu");}

#[cfg(feature="gpu")]
fn main()->Result<(),Box<dyn std::error::Error>> {
 use cudarc::driver::{CudaContext,LaunchConfig,PushKernelArg};
 use solver::{TreeConfig,StreetSizing,parse_sizes};use solver::tree::Action;
 use serde_json::{json,Value};use state::State;
 fn e(err:impl std::fmt::Debug)->String{format!("{err:?}")}
 fn encode(a:Action)->(i32,f64){match a {Action::Fold=>(0,0.),Action::Check=>(1,0.),Action::Call(x)=>(2,x),Action::Bet(x)=>(3,x),Action::Raise(x)=>(4,x)}}
 struct Row{branch:i32,path:Vec<i32>,ints:[i32;8],nums:[f64;8]}
 fn collect(s:State,c:&TreeConfig,branch:i32,path:&mut Vec<i32>,rows:&mut Vec<Row>){
   assert!(path.len()<=16);let mut ints=[0;8];let mut nums=[0.;8];
   ints[0]=s.kind as i32;ints[1]=s.player as i32;ints[2]=s.street as i32;nums[..2].copy_from_slice(&s.put);
   let actions=if s.kind==0{s.actions(c)}else{vec![]};assert!(actions.len()<=3);ints[3]=actions.len() as i32;
   for (a,&action)in actions.iter().enumerate(){let(k,to)=encode(action);ints[4+a]=k;nums[5+a]=to;}
   if s.kind==2||s.kind==3{nums[2..5].copy_from_slice(&s.payouts(c));}
   rows.push(Row{branch,path:path.clone(),ints,nums});
   if s.kind==1{path.push(-1);collect(s.deal(),c,branch,path,rows);path.pop();}
   for(a,action)in actions.into_iter().enumerate(){path.push(a as i32);collect(s.act(c,action),c,branch,path,rows);path.pop();}
 }
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),4);
 assert!(!std::path::Path::new(&args[3]).exists());
 let context:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
 assert_eq!(context["schema"],"hu-context-v1");
 let mut configs=vec![];let mut rows=vec![];let mut branches=vec![];
 let sizing=StreetSizing{bet:parse_sizes("50")?,raise:parse_sizes("100")?,donk:parse_sizes("50")?};
 for (leaf,n)in context["nodes"].as_array().unwrap().iter().enumerate(){
   if n["leaf"]["type"]!="postflop"{continue;}
   let cfg=TreeConfig{starting_pot:n["leaf"]["starting_pot"].as_f64().unwrap(),effective_stack:n["leaf"]["effective_stack"].as_f64().unwrap(),
     rake_pct:context["rake_fraction"].as_f64().unwrap(),rake_cap:context["rake_cap"].as_f64().unwrap(),
     oop:[sizing.clone(),sizing.clone(),sizing.clone()],ip:[sizing.clone(),sizing.clone(),sizing.clone()],max_raises:1,..Default::default()};
   let branch=branches.len() as i32;configs.extend([cfg.starting_pot,cfg.effective_stack,cfg.rake_pct,cfg.rake_cap]);
   let before=rows.len();collect(State::root(&cfg),&cfg,branch,&mut vec![],&mut rows);
   branches.push(json!({"preflop_leaf":leaf,"betting_history_templates":rows.len()-before}));
 }
 assert_eq!(branches.len(),3);assert!(rows.len()<10000);
 let branch:Vec<_>=rows.iter().map(|r|r.branch).collect();let lengths:Vec<_>=rows.iter().map(|r|r.path.len() as i32).collect();
 let paths:Vec<_>=rows.iter().flat_map(|r|{let mut x=r.path.clone();x.resize(16,-2);x}).collect();
 let source=std::fs::read_to_string(&args[1])?+"\n"+&std::fs::read_to_string(&args[2])?;
 let ctx=CudaContext::new(0).map_err(e)?;let stream=ctx.default_stream();let(ma,mi)=ctx.compute_capability().map_err(e)?;
 let arch:&'static str=Box::leak(format!("compute_{ma}{mi}").into_boxed_str());
 let ptx=cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),fmad:Some(false),..Default::default()}).map_err(e)?;
 let module=ctx.load_module(ptx).map_err(e)?;let kernel=module.load_function("pf_geometry_probe").map_err(e)?;
 let dc=stream.clone_htod(&configs).map_err(e)?;let db=stream.clone_htod(&branch).map_err(e)?;
 let dl=stream.clone_htod(&lengths).map_err(e)?;let dp=stream.clone_htod(&paths).map_err(e)?;
 let mut di=stream.alloc_zeros::<i32>(rows.len()*8).map_err(e)?;let mut dn=stream.alloc_zeros::<f64>(rows.len()*8).map_err(e)?;
 let count=rows.len() as i32;let mut first:Option<(Vec<i32>,Vec<f64>)>=None;let mut max_error=0f64;
 for repeat in 0..2{
   unsafe{stream.launch_builder(&kernel).arg(&count).arg(&dc).arg(&db).arg(&dl).arg(&dp).arg(&mut di).arg(&mut dn)
      .launch(LaunchConfig::for_num_elems(count as u32)).map_err(e)?;}
   let ints=stream.clone_dtoh(&di).map_err(e)?;let nums=stream.clone_dtoh(&dn).map_err(e)?;
   for(i,row)in rows.iter().enumerate(){assert_eq!(&ints[i*8..(i+1)*8],&row.ints,"path {:?}",row.path);
     for (a,b)in nums[i*8..(i+1)*8].iter().zip(row.nums){assert!(a.is_finite());max_error=max_error.max((a-b).abs());}}
   if repeat==0{first=Some((ints,nums));}else{let old=first.as_ref().unwrap();assert_eq!(ints,old.0);
     for(a,b)in nums.iter().zip(&old.1){assert_eq!(a.to_bits(),b.to_bits());}}
 }
 assert!(max_error<1e-10);
 let result=json!({"passed":true,"branches":branches,"templates":rows.len(),"maximum_depth":lengths.iter().max(),
   "integer_fields_exact":true,"max_numeric_error":max_error,"repeat_bit_exact":true,
   "scope":"All distinct betting histories with chance-card identities factored out only for transition testing. 50% bet/donk, pot raise, max one raise, threshold .85. Not general menus, showdown ranking, private sampling, or training.",
   "production_modified":false,"poker_trainer_qualified":false});
 std::fs::write(&args[3],serde_json::to_vec_pretty(&result)?)?;println!("{}",result);Ok(())
}
