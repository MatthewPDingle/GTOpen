//! CPU-only complete-node grouping and unchanged Store codec control.
use solver::{Spot,SpotConfig,store::Store,gpu::plan::GpuPlan,tree::KIND_ACTION};
use serde_json::{json,Value};
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},path::{Path,PathBuf}};
const LIMIT:usize=64*1024*1024/4;
#[derive(Clone,Copy,Debug)]
struct Block{node:u32,host:u64,device:usize,len:usize}
#[derive(Clone,Copy,Debug)]
struct Group{first:usize,end:usize,device:usize,len:usize}
fn next_group(blocks:&[Block],first:usize,capacity:usize)->Result<Option<Group>,String>{
 if first==blocks.len(){return Ok(None)}
 if first>blocks.len(){return Err("first beyond blocks".into())}
 let base=blocks[first].device;let mut len=0usize;let mut end=first;
 while end<blocks.len(){
  let b=blocks[end];
  if b.device!=base.checked_add(len).ok_or("device overflow")?{return Err("device gap/overlap".into())}
  if b.len>capacity{return Err("row exceeds capacity".into())}
  let combined=len.checked_add(b.len).ok_or("length overflow")?;
  if combined>capacity{break}
  len=combined;end+=1;
 }
 if end==first{return Err("no progress".into())}
 Ok(Some(Group{first,end,device:base,len}))
}
fn plan(blocks:&[Block],total:usize,limit:usize)->Result<(usize,Vec<Group>),String>{
 let mut cursor=0usize;
 for b in blocks{if b.device!=cursor{return Err("coverage gap/overlap".into())}cursor=cursor.checked_add(b.len).ok_or("coverage overflow")?;}
 if cursor!=total{return Err("total mismatch".into())}
 let capacity=total.min(limit).max(blocks.iter().map(|b|b.len).max().unwrap_or(0));
 let mut groups=Vec::new();let mut first=0;
 while let Some(g)=next_group(blocks,first,capacity)?{first=g.end;groups.push(g);}
 Ok((capacity,groups))
}
type Out=BufWriter<File>;
fn file(p:&Path,magic:&[u8])->Out{let mut f=BufWriter::new(OpenOptions::new().create_new(true).write(true).open(p).unwrap());f.write_all(magic).unwrap();f}
fn u32w(f:&mut Out,v:u32){f.write_all(&v.to_le_bytes()).unwrap()}
fn u64w(f:&mut Out,v:u64){f.write_all(&v.to_le_bytes()).unwrap()}
fn vecw(f:&mut Out,v:&[u32]){u64w(f,v.len() as u64);for x in v{u32w(f,*x)}}
fn blockw(f:&mut Out,b:&Block){u32w(f,b.node);u64w(f,b.host);u64w(f,b.device as u64);u64w(f,b.len as u64)}
fn emit(v:Value){let mut o=std::io::stdout().lock();writeln!(o,"D138_MODEL {v}").unwrap();o.flush().unwrap()}
fn bits(v:&[f32])->Vec<u32>{v.iter().map(|x|x.to_bits()).collect()}
fn image(s:&Store)->Vec<u32>{
 match s{
  Store::F32(a)=>{let mut v=vec![0,a.len() as u32,0];v.extend(a.as_slice().iter().map(|x|x.to_bits()));v},
  Store::I16{q,scale}=>{let mut v=vec![1,q.len() as u32,scale.len() as u32];v.extend(q.as_slice().iter().map(|x|*x as u16 as u32));v.extend(scale.as_slice().iter().map(|x|x.to_bits()));v},
  Store::U16{q,scale}=>{let mut v=vec![2,q.len() as u32,scale.len() as u32];v.extend(q.as_slice().iter().map(|x|*x as u32));v.extend(scale.as_slice().iter().map(|x|x.to_bits()));v},
 }
}
fn seeded(kind:u32,len:usize,nodes:usize,salt:usize)->Store{
 let mut s=match kind{0=>Store::f32(len as u64),1=>Store::i16(len as u64,nodes),_=>Store::u16(len as u64,nodes)};
 match &mut s{
  Store::F32(a)=>for(i,x)in a.as_mut_slice().iter_mut().enumerate(){*x=f32::from_bits(0x3f00_0000+((i+salt)%1024) as u32)},
  Store::I16{q,scale}=>{for(i,x)in q.as_mut_slice().iter_mut().enumerate(){*x=((i*73+salt)%65536) as u16 as i16}for(i,x)in scale.as_mut_slice().iter_mut().enumerate(){*x=0.125+((i+salt)%13) as f32}},
  Store::U16{q,scale}=>{for(i,x)in q.as_mut_slice().iter_mut().enumerate(){*x=((i*97+salt)%65536) as u16}for(i,x)in scale.as_mut_slice().iter_mut().enumerate(){*x=0.25+((i+salt)%17) as f32}},
 }s
}
fn value(i:usize,mode:usize)->f32{
 match mode{
  0=>[0.,-0.,0.25,-0.75,13.25,-7.125,1e10,-1e10,1e-20,-1e-20][(i*7+i/11)%10],
  1=>f32::from_bits([0u32,0x80000000,1,0x80000001,0x00800000,0x80800000,0x7f800000,0xff800000,0x7fc01234,0xffc05678][i%10]),
  _=>if i%3==0{-f32::MAX}else{f32::MAX},
 }
}
fn codecs(f:&mut Out)->usize{
 let shapes:Vec<Vec<usize>>=vec![vec![0,1,31,0,129,257,17],vec![1,32,33,127,128,129,1023,1326],vec![0,250*1326,1,0,4097],vec![0,0,0]];
 let mut id=0usize;
 for(shape,lens)in shapes.iter().enumerate(){for gaps in [false,true]{for limit in [257usize,4097,LIMIT]{for kind in 0..3u32{for mode in 0..3usize{
  let mut blocks=Vec::new();let(mut host,mut device)=(if gaps{5}else{0},0usize);
  for(i,&len)in lens.iter().enumerate(){blocks.push(Block{node:(3*i+1) as u32,host:host as u64,device,len});host+=len+if gaps{3}else{0};device+=len;}
  let host_len=host+if gaps{7}else{0};let nodes=3*lens.len()+5;
  let(capacity,groups)=plan(&blocks,device,limit).unwrap();
  let source=seeded(kind,host_len,nodes,17);
  for b in &blocks{let data:Vec<f32>=(0..b.len).map(|i|value(i+b.node as usize,mode)).collect();unsafe{source.write_f32(b.node,b.host,b.len,&data)}}
  let before=image(&source);let mut original=vec![f32::NAN;device];
  for b in &blocks{unsafe{source.read_f32(b.node,b.host,b.len,&mut original[b.device..b.device+b.len])}}
  let mut grouped=vec![f32::NAN;device];let mut staging=vec![f32::NAN;capacity];
  for g in &groups{for b in &blocks[g.first..g.end]{let off=b.device-g.device;unsafe{source.read_f32(b.node,b.host,b.len,&mut staging[off..off+b.len])}}grouped[g.device..g.device+g.len].copy_from_slice(&staging[..g.len]);}
  let after=image(&source);assert_eq!(before,after);assert_eq!(bits(&original),bits(&grouped));
  let baseline=seeded(kind,host_len,nodes,101);let candidate=seeded(kind,host_len,nodes,101);let seed=image(&baseline);assert_eq!(seed,image(&candidate));
  for b in &blocks{unsafe{baseline.write_f32(b.node,b.host,b.len,&original[b.device..b.device+b.len])}}
  for g in &groups{staging[..g.len].copy_from_slice(&original[g.device..g.device+g.len]);for b in &blocks[g.first..g.end]{let off=b.device-g.device;unsafe{candidate.write_f32(b.node,b.host,b.len,&staging[off..off+b.len])}}}
  let b=image(&baseline);let c=image(&candidate);assert_eq!(b,c);
  for v in [id as u32,shape as u32,gaps as u32,kind,mode as u32,blocks.len() as u32]{u32w(f,v)}
  for v in [limit,capacity,device,host_len,nodes]{u64w(f,v as u64)}
  for b in &blocks{blockw(f,b)}
  for v in [&before,&after,&seed,&b,&c,&bits(&original),&bits(&grouped)]{vecw(f,v)}
  id+=1;
 }}}}}
 emit(json!({"stage":"codecs_complete","cases":id,"full_source_immutable":true,"full_upload_images_exact":true,"full_Store_images_exact":true,"GPU_contexts":0}));id
}
fn main(){
 let out=PathBuf::from(std::env::args().nth(1).expect("fresh output dir"));std::fs::create_dir(&out).unwrap();
 let mut nodes=file(&out.join("nodes.bin"),b"D138-NODES-v1\0\0\0");
 let mut groups_raw=file(&out.join("groups.bin"),b"D138-GROUP-v1\0\0\0");
 let mut codec=file(&out.join("codecs.bin"),b"D138-CODEC-v1\0\0\0");
 let mut rows=Vec::new();let mut id=0usize;
 for(name,board,rake)in [("rainbow","Ks7h2d",0.0),("two-tone","Ks7s2d",0.05),("river","Ks7h2dQhTc",0.05)]{
  for iso in [false,true]{for full in [false,true]{
   let mut cfg:SpotConfig=serde_json::from_str(include_str!("bench_spot.json")).unwrap();cfg.board=board.into();cfg.tree.rake_pct=rake;cfg.tree.rake_cap=3.;
   let spot=Spot::new(cfg).unwrap();let mut p=GpuPlan::build(&spot,iso);
   if full{p.arena_elements=[spot.tree.data_size[0] as usize,spot.tree.data_size[1] as usize];for(i,n)in spot.tree.nodes.iter().enumerate(){p.node_data_off[i]=n.data_offset;}}
   u32w(&mut nodes,id as u32);u64w(&mut nodes,spot.tree.nodes.len() as u64);
   for(i,n)in spot.tree.nodes.iter().enumerate(){nodes.write_all(&[n.kind,n.player]).unwrap();nodes.write_all(&(n.num_children as u16).to_le_bytes()).unwrap();u64w(&mut nodes,n.data_offset);u64w(&mut nodes,p.node_data_off[i]);}
   let mut player_rows=Vec::new();let mut pinned=0usize;
   for player in 0..2{
    let compact=p.arena_elements[player]!=spot.tree.data_size[player] as usize||spot.tree.nodes.iter().enumerate().any(|(i,n)|n.kind==KIND_ACTION&&n.player as usize==player&&p.node_data_off[i]!=n.data_offset);
    let mut blocks=Vec::new();
    for(i,n)in spot.tree.nodes.iter().enumerate(){if n.kind!=KIND_ACTION||n.player as usize!=player{continue}let off=if compact{p.node_data_off[i]}else{n.data_offset};if off==u64::MAX{continue}blocks.push(Block{node:i as u32,host:n.data_offset,device:off as usize,len:n.num_children as usize*p.nh[player]});}
    let(capacity,gs)=plan(&blocks,p.arena_elements[player],LIMIT).unwrap();pinned=pinned.max(capacity);
    for v in [id as u32,player as u32]{u32w(&mut groups_raw,v)}
    for v in [blocks.len(),capacity]{u64w(&mut groups_raw,v as u64)}
    for b in &blocks{blockw(&mut groups_raw,b)}u64w(&mut groups_raw,gs.len() as u64);
    for g in &gs{for v in [g.first,g.end,g.device,g.len]{u64w(&mut groups_raw,v as u64)}}
    player_rows.push(json!({"nh":p.nh[player],"arena_words":p.arena_elements[player],"host_words":spot.tree.data_size[player],"compact":compact,"active_blocks":blocks.len(),"groups":gs.len(),"window_words":capacity,"max_node_words":blocks.iter().map(|b|b.len).max().unwrap_or(0),"prototype_block_capacity":blocks.capacity(),"extra_full_layout_metadata_capacity_bytes":if !compact&&p.arena_elements[player]>LIMIT{blocks.capacity()*std::mem::size_of::<Block>()}else{0}}));
   }
   let row=json!({"id":id,"fixture":name,"board":board,"iso_requested":iso,"force_full":full,"nodes":spot.tree.nodes.len(),"players":player_rows,"baseline_pinned_request_bytes":4*p.arena_elements.iter().max().unwrap(),"proposed_pinned_request_bytes":4*pinned,"production_limit_bytes":4*LIMIT});
   emit(json!({"stage":"layout_complete","case":&row}));rows.push(row);id+=1;
  }}
 }
 let codec_cases=codecs(&mut codec);
 let invalids=[(vec![Block{node:0,host:0,device:0,len:3},Block{node:1,host:3,device:4,len:1}],4usize),(vec![Block{node:0,host:0,device:0,len:3},Block{node:1,host:3,device:2,len:1}],4),(vec![],1),(vec![Block{node:0,host:0,device:0,len:3}],4),(vec![Block{node:0,host:0,device:0,len:usize::MAX},Block{node:1,host:0,device:usize::MAX,len:1}],0)];
 for(b,t)in &invalids{assert!(plan(b,*t,LIMIT).is_err())}assert!(next_group(&[Block{node:0,host:0,device:0,len:2}],0,1).is_err());
 for f in [&mut nodes,&mut groups_raw,&mut codec]{f.flush().unwrap();f.get_ref().sync_all().unwrap();}
 let meta=json!({"id":"D138-model","cases":rows,"codec_cases":codec_cases,"invalid_controls_rejected":invalids.len()+1,"production_limit_bytes":LIMIT*4,"block_size_bytes":std::mem::size_of::<Block>(),"prototype_only":true,"CUDA_contexts":0,"GPU_kernels":0,"solver_iterations":0,"performance_measurement":false,"candidate_accepted":false});
 let mut m=OpenOptions::new().create_new(true).write(true).open(out.join("metadata.json")).unwrap();m.write_all(serde_json::to_string_pretty(&meta).unwrap().as_bytes()).unwrap();m.sync_all().unwrap();
 emit(json!({"stage":"complete","layouts":id,"codec_cases":codec_cases,"invalid_controls_rejected":invalids.len()+1,"CUDA_contexts":0,"GPU_kernels":0,"solver_iterations":0,"performance_measurement":false}));
}
