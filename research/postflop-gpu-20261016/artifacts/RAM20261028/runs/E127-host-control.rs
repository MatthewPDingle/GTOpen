//! CPU-only observer attached temporarily inside the real GPU module.
use super::*;
use serde_json::{json,Value};
use std::{collections::BTreeMap,fs::{File,OpenOptions},io::{Read,Write},path::{Path,PathBuf},mem::{size_of,align_of}};
fn u32r(f:&mut File)->u32{let mut b=[0;4];f.read_exact(&mut b).unwrap();u32::from_le_bytes(b)}
fn u64r(f:&mut File)->u64{let mut b=[0;8];f.read_exact(&mut b).unwrap();u64::from_le_bytes(b)}
fn input(path:&Path)->BTreeMap<String,(u32,Vec<u8>)>{
 let mut f=File::open(path).unwrap();let mut magic=[0;16];f.read_exact(&mut magic).unwrap();assert_eq!(&magic,b"D267-MODEL-v1\0\0\0");let count=u32r(&mut f);let mut fields=BTreeMap::new();
 for _ in 0..count{let n=u32r(&mut f);assert!(n<256);let mut name=vec![0;n as usize];f.read_exact(&mut name).unwrap();let width=u32r(&mut f);let count=u64r(&mut f);assert!([4,8].contains(&width)&&count<=1<<31);let mut data=vec![0;width as usize*count as usize];f.read_exact(&mut data).unwrap();assert!(fields.insert(String::from_utf8(name).unwrap(),(width,data)).is_none());}let mut tail=[0];assert_eq!(f.read(&mut tail).unwrap(),0);fields
}
fn vec32(fields:&BTreeMap<String,(u32,Vec<u8>)>,name:&str)->Vec<u32>{let(w,b)=&fields[name];assert_eq!(*w,4);b.chunks_exact(4).map(|x|u32::from_le_bytes(x.try_into().unwrap())).collect()}
fn number(fields:&BTreeMap<String,(u32,Vec<u8>)>,name:&str)->usize{let(w,b)=&fields[name];assert_eq!(*w,8);assert_eq!(b.len(),8);usize::try_from(u64::from_le_bytes(b[..].try_into().unwrap())).unwrap()}
fn projection(path:&Path,fields:Vec<(&str,u32,Vec<u8>)>){
 let mut f=OpenOptions::new().create_new(true).write(true).open(path).unwrap();f.write_all(b"D267-MODEL-v1\0\0\0").unwrap();f.write_all(&(fields.len()as u32).to_le_bytes()).unwrap();
 for(name,width,bytes)in fields{assert_eq!(bytes.len()%width as usize,0);f.write_all(&(name.len()as u32).to_le_bytes()).unwrap();f.write_all(name.as_bytes()).unwrap();f.write_all(&width.to_le_bytes()).unwrap();f.write_all(&(bytes.len()as u64/width as u64).to_le_bytes()).unwrap();f.write_all(&bytes).unwrap();}f.sync_all().unwrap();
}
fn bytes32(v:&[u32])->Vec<u8>{v.iter().flat_map(|v|v.to_le_bytes()).collect()}
fn spans(v:&[LevelSpan])->Vec<u8>{v.iter().flat_map(|x|[x.start,x.count]).flat_map(|v|v.to_le_bytes()).collect()}
fn has_head(work:&action_stars::StarWork,n:u32)->bool{work.fused.iter().any(|s|work.nodes[s.start as usize..(s.start+s.count)as usize].contains(&n))}
fn negative_contract(){
 let ids=[0,1,2,3,5,9];let phases=[LevelSpan{start:0,count:1},LevelSpan{start:1,count:2},LevelSpan{start:3,count:2},LevelSpan{start:5,count:1},LevelSpan{start:6,count:0}];
 let na=[2,2,2,2,0,2,0,0,0,2,0,0,0];let start=[0,2,4,6,0,8,0,0,0,10,0,0,0];let kids=[1,2,3,4,5,6,7,8,9,10,11,12];
 let mut slot=[0,2,3,0,4,1,5,6,7,2,8,9,10];let kind=|i:usize|if ids.contains(&(i as u32)){0}else{3};
 let unsafe_case=action_stars::build(13,5,11,&ids,&phases,&na,&start,&kids,&[],&slot,kind).unwrap();assert!(!has_head(&unsafe_case,1),"foreign reader must reject parent1");
 slot[9]=3;let safe_case=action_stars::build(13,5,11,&ids,&phases,&na,&start,&kids,&[],&slot,kind).unwrap();assert!(has_head(&safe_case,1),"same metadata with foreign row removed admits parent1");
 let no_child=action_stars::build(3,2,3,&[0],&[LevelSpan{start:0,count:1},LevelSpan{start:1,count:0}],&[2,0,0],&[0,0,0],&[1,2],&[],&[0,1,2],|i|if i==0{0}else{3});assert!(no_child.is_none());
 let chance_child=action_stars::build(3,2,3,&[0],&[LevelSpan{start:0,count:1},LevelSpan{start:1,count:0}],&[2,52,0],&[0,0,0],&[1,2],&[],&[0,1,2],|i|[0,1,3][i]);assert!(chance_child.is_none());
 println!("E127_HOST_NEGATIVE {}",json!({"foreign_reader_rejected":true,"row_hazard_removed_admits_original_parent":true,"no_action_children_uses_original":true,"chance_child_uses_original":true}));
}
#[test]
#[ignore="manual CPU-only E127 metadata/source/type control"]
fn e127_host_mapping(){
 assert_eq!(size_of::<LevelSpan>(),8);assert_eq!(align_of::<LevelSpan>(),4);
 assert!(size_of::<GpuSolver>()<=4448+16);assert!(size_of::<ActionStarGpu>()<=256);assert_eq!(size_of::<Option<Box<ActionStarGpu>>>(),8);
 println!("E127_HOST_TYPES {}",json!({"GpuSolver_bytes":size_of::<GpuSolver>(),"baseline_GpuSolver_bytes":4448,"ActionStarGpu_bytes":size_of::<ActionStarGpu>(),"StarWork_bytes":size_of::<action_stars::StarWork>(),"LevelSpan_bytes":size_of::<LevelSpan>(),"LevelSpan_alignment":align_of::<LevelSpan>(),"OptionBox_bytes":8,"CUDA_contexts_or_kernels":0}));
 negative_contract();let config=PathBuf::from(std::env::var_os("E127_HOST_INPUTS").unwrap());let output=PathBuf::from(std::env::var_os("E127_HOST_OUTPUT").unwrap());std::fs::create_dir(&output).unwrap();
 let cases:Vec<Value>=serde_json::from_slice(&std::fs::read(config).unwrap()).unwrap();assert_eq!(cases.len(),6);
 for case in cases{let fields=input(Path::new(case["path"].as_str().unwrap()));assert_eq!(fields.len(),11);
  let ids=vec32(&fields,"action_nodes");let phase=vec32(&fields,"action_spans");assert_eq!(phase.len()%2,0);let phase:Vec<_>=phase.chunks_exact(2).map(|p|LevelSpan{start:p[0],count:p[1]}).collect();let na:Vec<_>=vec32(&fields,"node_na").into_iter().map(|v|i32::try_from(v).unwrap()).collect();let start=vec32(&fields,"node_children_start");let kids=vec32(&fields,"children");let chance=vec32(&fields,"cc_child");let slot=vec32(&fields,"cfv_slot");let kinds=vec32(&fields,"kinds");assert!(kinds.iter().all(|&v|v<=3));
  let work=action_stars::build(number(&fields,"num_nodes"),number(&fields,"num_levels"),number(&fields,"cfv_blocks"),&ids,&phase,&na,&start,&kids,&chance,&slot,|i|kinds[i]as u8).unwrap();
  let file=output.join(case["output"].as_str().unwrap());projection(&file,vec![("nodes",4,bytes32(&work.nodes)),("regular_spans",4,spans(&work.regular)),("fused_spans",4,spans(&work.fused)),("counts",8,[work.heads as u64,work.children as u64].into_iter().flat_map(|x|x.to_le_bytes()).collect())]);
  println!("E127_HOST_CASE {}",json!({"fixture":case["fixture"],"constructor":case["constructor"],"heads":work.heads,"children":work.children,"nodes":work.nodes.len(),"nodes_capacity":work.nodes.capacity(),"regular_spans":work.regular.len(),"regular_capacity":work.regular.capacity(),"fused_spans":work.fused.len(),"fused_capacity":work.fused.capacity(),"source_type":"actual production action_stars::build compiled inside real gpu module","CUDA_contexts_or_kernels":0}));std::io::stdout().flush().unwrap();
 }
 println!("E127_HOST_COMPLETE {}",json!({"cases":6,"CUDA_contexts":0,"application_kernel_launches":0,"solver_or_speed_samples":0}));
}
