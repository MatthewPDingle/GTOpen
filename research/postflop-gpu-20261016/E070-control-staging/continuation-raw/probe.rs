//! E070 three continuation helper comparisons; full raw words, no timing score.
use cudarc::{driver::{CudaContext,CudaSlice,CudaStream,DevicePtr,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::PathBuf,sync::Arc};
type Out=BufWriter<File>;
fn file(p:PathBuf,magic:&[u8])->Out{let mut f=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(p).unwrap());f.write_all(magic).unwrap();f}
fn words(f:&mut Out,v:&[u32]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();let b:Vec<u8>=v.iter().flat_map(|x|x.to_le_bytes()).collect();f.write_all(&b).unwrap();}
fn id(f:&mut Out,n:usize){f.write_all(&(n as u32).to_le_bytes()).unwrap();}
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E070_HELPER_RAW {v}").unwrap();o.flush().unwrap();}
fn u(c:&serde_json::Value,k:&str)->usize{c[k].as_u64().unwrap() as usize}
fn fb(v:&[f32])->Vec<u32>{v.iter().map(|x|x.to_bits()).collect()}
fn floats(v:&[u32])->Vec<f32>{v.iter().copied().map(f32::from_bits).collect()}
fn split(v:&[u64])->Vec<u32>{v.iter().flat_map(|&x|[x as u32,(x>>32) as u32]).collect()}
fn readf(s:&Arc<CudaStream>,v:&CudaSlice<f32>)->Vec<u32>{let r=s.clone_dtoh(v).unwrap();s.synchronize().unwrap();fb(&r)}
fn value(i:usize,mode:usize)->u32{
 match mode{
  1=>[0u32,0x80000000][i%2],
  2=>[0x7f800000,0xff800000,0x7fc01234,0xffc05678,0x3e800000,0xbf400000,0x3f800000][i%7],
  3=>[f32::MAX.to_bits(),(-f32::MAX).to_bits(),1f32.to_bits(),(-1f32).to_bits()][i%4],
  4=>[1u32,0x80000001,0,0x80000000,0x00800000,0x80800000,0x00800001][i%7],
  _=>[0.0f32,-0.0,0.25,-0.75,13.25,-7.125,1e10,-1e10,1e-20,-1e-20][(i*5+i/11)%10].to_bits()
 }
}
fn ranges(s:&Arc<CudaStream>,buffers:[&CudaSlice<f32>;4])->Vec<[u64;2]>{
 let r:Vec<_>=buffers.iter().map(|b|{let(p,_g)=b.device_ptr(s);[p,b.len() as u64*4]}).collect();
 for i in 0..4{for j in i+1..4{assert!(r[i][0]+r[i][1]<=r[j][0]||r[j][0]+r[j][1]<=r[i][0],"actual device buffers overlap");}}r
}
fn main(){
 let dir=PathBuf::from(std::env::var_os("E070_HELPER_RAW_DIR").expect("fresh raw S: directory required"));
 let ptxdir=PathBuf::from(std::env::var_os("E070_HELPER_PTX_DIR").expect("sealed helper PTX directory required"));
 let storage=PathBuf::from(r"S:\GTOpen-research\postflop-gpu-20261016");assert!(dir.starts_with(&storage)&&ptxdir.starts_with(&storage));std::fs::create_dir(&dir).unwrap();
 let mut input=file(dir.join("inputs.bin"),b"E070_HELPER_IN1");let mut baseline=file(dir.join("baseline.bin"),b"E070_HELPER_OUT1");let mut candidate=file(dir.join("candidate.bin"),b"E070_HELPER_OUT1");
 let mut bi=file(dir.join("baseline-inputs.bin"),b"E070_HELPER_IM1");let mut ci=file(dir.join("candidate-inputs.bin"),b"E070_HELPER_IM1");
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let mut modules=Vec::new();
 for module in ["projection","storage-copy"]{for arm in ["baseline","candidate"]{
  let path=ptxdir.join(format!("{module}-{arm}-compute_120.ptx"));let text=std::fs::read_to_string(&path).unwrap();
  emit(serde_json::json!({"stage":"PTX_input","module":module,"arm":arm,"path":path,"bytes":text.len(),"parent_SHA256_pinning_required":true}));
  modules.push(ctx.load_module(Ptx::from_src(text)).unwrap());
 }}
 let bf=[modules[0].load_function("continuation_project").unwrap(),modules[0].load_function("continuation_transport").unwrap(),modules[2].load_function("continuation_storage_copy").unwrap()];
 let cf=[modules[1].load_function("continuation_project").unwrap(),modules[1].load_function("continuation_transport").unwrap(),modules[3].load_function("continuation_storage_copy").unwrap()];
 let corpus:serde_json::Value=serde_json::from_str(include_str!("corpus.json")).unwrap();let cases=corpus["cases"].as_array().unwrap();assert_eq!(cases.len(),u(&corpus,"case_count"));
 let mut output_words=0u64;let mut immutable_words=0u64;let mut guard_words=0u64;let mut oracle_words=0u64;
 for(index,c) in cases.iter().enumerate(){
  assert_eq!(index,u(c,"id"));let kind=u(c,"kind");let nh=u(c,"hands");let na=u(c,"actions");let block=u(c,"threads") as u32;let p=u(c,"p") as i32;let op=u(c,"operation") as i32;let count=u(c,"count") as i32;let mode=u(c,"value_mode");assert!(kind<3&&count<=3&&na<=255);
  let nodes=vec![2u32,1,3,0xdeadbeef,0xdeadbeef];let players=vec![0i32,1,0,1,255];let arity=vec![na as i32,na as i32,na as i32,na as i32,255];let attrs:Vec<u16>=players.iter().zip(&arity).map(|(&p,&a)|((p as u16)<<8)|(a as u16)).collect();
  let offset:Vec<u64>=(0..5).map(|n|(13+n*(na*nh+7)) as u64).collect();let packed:Vec<u64>=(0..5).map(|n|(11+n*(na*nh+5)) as u64).collect();
  let masks=vec![3u32,1,3,3,1];let sources=vec![0u32,1,0,1,4];let source_pm=vec![0u32,0,1,1,0];
  let perm:Vec<u32>=if nh==0{vec![0xdeadbeef]}else{(0..nh).chain((0..nh).rev()).map(|x|x as u32).collect()};
  let seeds:Vec<Vec<u32>>=(0..4).map(|k|{
   let len=if k<2{offset[4] as usize+na*nh+17}else{packed[4] as usize+na*nh+17};
   (0..len).map(|i|value(i+index*7+k*31,mode)).collect()
  }).collect();
  let immutable=vec![nodes.clone(),players.iter().map(|&x|x as u32).collect(),arity.iter().map(|&x|x as u32).collect(),attrs.iter().map(|&x|x as u32).collect(),split(&offset),masks.clone(),perm.clone(),sources.clone(),source_pm.clone(),split(&packed)];
  id(&mut input,index);words(&mut input,&[kind as u32,nh as u32,na as u32,block,p as u32,op as u32,count as u32,mode as u32,5,13,11]);for v in &immutable{words(&mut input,v);}for v in &seeds{words(&mut input,v);}input.flush().unwrap();
  let dn=stream.clone_htod(&nodes).unwrap();let dp=stream.clone_htod(&players).unwrap();let da=stream.clone_htod(&arity).unwrap();let dattrs=stream.clone_htod(&attrs).unwrap();let doff=stream.clone_htod(&offset).unwrap();let dm=stream.clone_htod(&masks).unwrap();let dpm=stream.clone_htod(&perm).unwrap();let dsrc=stream.clone_htod(&sources).unwrap();let dspm=stream.clone_htod(&source_pm).unwrap();let dpacked=stream.clone_htod(&packed).unwrap();
  let mut owned:Vec<Vec<bool>>=seeds.iter().map(|v|vec![false;v.len()]).collect();let mut oracle=seeds.clone();let mut oracle_valid=owned.clone();
  for b in 0..count as usize{
   let n=nodes[b] as usize;if players[n]!=p{continue;}
   if kind==0{
    if masks[n]==1{continue;}
    for i in 0..nh{let canonical=i.min(nh-1-i);if (op!=0&&canonical==i)||(op==0&&canonical!=i){continue;}
     for a in 0..na{let at=offset[n] as usize+a*nh+i;
      for k in 0..2{assert!(!owned[k][at]);owned[k][at]=true;
       if op!=0{oracle[k][at]=seeds[k][offset[n] as usize+a*nh+canonical];oracle_valid[k][at]=true;}
       else{let x=f32::from_bits(seeds[k][offset[n] as usize+a*nh+i]);let y=f32::from_bits(seeds[k][offset[n] as usize+a*nh+nh-1-i]);if x.is_finite()&&y.is_finite(){let mut sum=0f64;sum+=x as f64;sum+=y as f64;oracle[k][at]=((sum/2.0) as f32).to_bits();oracle_valid[k][at]=true;}}
      }
     }
    }
   }else if kind==1{
    let source=sources[n] as usize;if source==n{continue;}assert_eq!(sources[source] as usize,source);
    for a in 0..na{for i in 0..nh{let at=offset[n] as usize+a*nh+i;let src=offset[source] as usize+a*nh+nh-1-i;
     for k in 0..2{assert!(!owned[k][at]);owned[k][at]=true;oracle[k][at]=seeds[k][src];oracle_valid[k][at]=true;}
    }}
   }else{
    for i in 0..na*nh{for k in 0..2{
     let(dst,at,src,from)=if op!=0{(k+2,packed[b] as usize+i,k,offset[n] as usize+i)}else{(k,offset[n] as usize+i,k+2,packed[b] as usize+i)};
     assert!(!owned[dst][at]);owned[dst][at]=true;oracle[dst][at]=seeds[src][from];oracle_valid[dst][at]=true;
    }}
   }
  }
  let mut expected:Option<Vec<Vec<u32>>>=None;let mut witnesses=Vec::new();
  for(label,f) in [("baseline",&bf[kind]),("candidate",&cf[kind])]{
   let mut dr=stream.clone_htod(&floats(&seeds[0])).unwrap();let mut ds=stream.clone_htod(&floats(&seeds[1])).unwrap();let mut dpr=stream.clone_htod(&floats(&seeds[2])).unwrap();let mut dps=stream.clone_htod(&floats(&seeds[3])).unwrap();let nharg=nh as i32;
   witnesses.push(serde_json::json!({"arm":label,"regions":ranges(&stream,[&dr,&ds,&dpr,&dps])}));
   unsafe{let mut launch=stream.launch_builder(f);launch.arg(&dn).arg(&count);if label=="baseline"{launch.arg(&dp).arg(&da);}else{launch.arg(&dattrs);}
    if kind==0{launch.arg(&doff).arg(&dm).arg(&dpm).arg(&mut dr).arg(&mut ds).arg(&nharg).arg(&p).arg(&op);}
    else if kind==1{launch.arg(&doff).arg(&dsrc).arg(&dspm).arg(&dpm).arg(&mut dr).arg(&mut ds).arg(&nharg).arg(&p);}
    else{launch.arg(&doff).arg(&dpacked).arg(&mut dr).arg(&mut ds).arg(&mut dpr).arg(&mut dps).arg(&nharg).arg(&p).arg(&op);}
    launch.launch(LaunchConfig{grid_dim:(count as u32+2,1,1),block_dim:(block,1,1),shared_mem_bytes:0}).unwrap();
   }
   stream.synchronize().unwrap();let result=vec![readf(&stream,&dr),readf(&stream,&ds),readf(&stream,&dpr),readf(&stream,&dps)];
   let out=if label=="baseline"{&mut baseline}else{&mut candidate};id(out,index);for v in &result{words(out,v);}out.flush().unwrap();
   let post=vec![stream.clone_dtoh(&dn).unwrap(),stream.clone_dtoh(&dp).unwrap().iter().map(|&x|x as u32).collect(),stream.clone_dtoh(&da).unwrap().iter().map(|&x|x as u32).collect(),stream.clone_dtoh(&dattrs).unwrap().iter().map(|&x|x as u32).collect(),split(&stream.clone_dtoh(&doff).unwrap()),stream.clone_dtoh(&dm).unwrap(),stream.clone_dtoh(&dpm).unwrap(),stream.clone_dtoh(&dsrc).unwrap(),stream.clone_dtoh(&dspm).unwrap(),split(&stream.clone_dtoh(&dpacked).unwrap())];stream.synchronize().unwrap();
   let image=if label=="baseline"{&mut bi}else{&mut ci};id(image,index);for v in &post{words(image,v);}image.flush().unwrap();assert_eq!(post,immutable,"immutable{index}/{label}");
   for k in 0..4{for at in 0..result[k].len(){if !owned[k][at]{assert_eq!(result[k][at],seeds[k][at],"guard{index}/{label}/{k}/{at}");guard_words+=1;}else if oracle_valid[k][at]{assert_eq!(result[k][at],oracle[k][at],"CPU oracle{index}/{label}/{k}/{at}");oracle_words+=1;}}}
   if let Some(ref prior)=expected{assert_eq!(&result,prior,"baseline/candidate{index}, including nonfinite outputs");}else{expected=Some(result.clone());}
   output_words+=result.iter().map(|v|v.len() as u64).sum::<u64>();immutable_words+=post.iter().map(|v|v.len() as u64).sum::<u64>();
  }
  emit(serde_json::json!({"stage":"case","id":index,"kind":kind,"hands":nh,"actions":na,"threads":block,"p":p,"operation":op,"count":count,"value_mode":mode,"all_raw_exact":true,"guards_exact":true,"disjoint_device_ranges":witnesses}));
 }
 stream.synchronize().unwrap();drop(bf);drop(cf);drop(modules);drop(stream);ctx.check_err().unwrap();
 for f in [&mut input,&mut baseline,&mut candidate,&mut bi,&mut ci]{f.flush().unwrap();f.get_ref().sync_all().unwrap();}
 emit(serde_json::json!({"stage":"complete","cases":cases.len(),"kernel_launches":2*cases.len(),"output_words_both_arms":output_words,"immutable_words_both_arms":immutable_words,"guard_words_both_arms":guard_words,"CPU_oracle_words_both_arms":oracle_words,"all_raw_exact":true,"all_inputs_and_guards_exact":true,"performance_measurement":false,"solver_executions":0,"candidate_accepted":false}));
}
