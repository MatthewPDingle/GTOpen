"""Prepare full-buffer actual up_chance comparator with a checked read contract."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
source=(ROOT/'runs/E048-kernel-control/probe.rs').read_text()
prefix=source[:source.index('fn main(){')];a=prefix.index('struct Down{');b=prefix.index('struct Up{');prefix=prefix[:a]+prefix[b:]
prefix=prefix.replace('E048','E068').replace('//! E068 original-mask/new-card direct GPU comparator, no timing score.','//! E068 exact original/new bit-selected up_chance comparator, no timing score.')
prefix=prefix.replace('struct Case{d:Vec<u32>}','struct Case{d:Vec<u32>,inv_bits:u32,mask_style:u32}').replace('fn n1(&self)->usize','fn pad(&self)->usize')
prefix=prefix.replace('2=>((j*17+13)%52) as u32,_=>','2=>((j*17+13)%52) as u32,4=>0,5=>51,_=>')
old='inv[2]=1.0/46.0;let(a,b,mask)=hands(n,c.salt());'
new='inv[2]=f32::from_bits(c.inv_bits);let(mut a,mut b,mut mask)=hands(n,c.salt());if c.mask_style!=0{for i in 0..a.len(){a[i]=0;b[i]=if c.mask_style==1{1+(i%51) as u32}else{1};mask[i]=(1u64<<a[i])|(1u64<<b[i]);}}'
assert prefix.count(old)==1;prefix=prefix.replace(old,new).replace('(w+12)*(n+5)+17','(w+12)*(n+c.pad())+17').replace('let stride=nh+5;','let stride=nh+c.pad() as i32;').replace('2*(c.n0()+5)','2*(c.n0()+c.pad())')
prefix=prefix.replace(',new:bool)->',')->')
a=prefix.index('  unsafe{if new{');b=prefix.index('\n  s.synchronize()',a)
prefix=prefix[:a]+'''  unsafe{s.launch_builder(f).arg(&nodes).arg(&start).arg(&count).arg(&cs).arg(&cc).arg(&card).arg(&child).arg(&perm).arg(&inv).arg(&mask).arg(&hp).arg(&slot).arg(&mut cfv).arg(&nh).arg(&stride).launch(cfg).unwrap();}'''+prefix[b:]
needle=' fn inputs(&self)->Vec<Vec<u32>>'
assert prefix.count(needle)==1
contract=r''' fn read_contract(&self,c:&Case)->u64{
  let n=c.n0();let stride=n+c.pad();let parent=self.slot[self.nodes[1] as usize] as usize;let lo=parent*stride;let hi=lo+n;assert!(hi<=self.seed.len());let mut checks=0;
  for j in 0..c.width(){let t=3+j;assert!(self.card[t]<52);let k=self.perm[t] as usize;assert!(k<4);let child=self.child[t] as usize;assert!(child<self.slot.len());
   for i in 0..n{let index=if k==0{i}else{let at=k*n+i;assert!(at<self.hp.len());self.hp[at] as usize};assert!(index<n);let address=self.slot[child] as usize*stride+index;assert!(address<self.seed.len() && (address<lo||address>=hi));checks+=1;}
  }checks
 }
'''
prefix=prefix.replace(needle,contract+needle)
main=r'''fn main(){
 let dir=PathBuf::from(std::env::var_os("E068_CONTROL_DIR").expect("fresh output required"));std::fs::create_dir(&dir).unwrap();
 let corpus:Value=serde_json::from_str(include_str!("corpus.json")).unwrap();let cases=corpus["cases"].as_array().unwrap();assert_eq!(cases.len(),1788);
 let mut input=file(dir.join("inputs.bin"),b"E068_IN1");let mut baseline=file(dir.join("baseline.bin"),b"E068_OUT1");let mut candidate=file(dir.join("candidate.bin"),b"E068_OUT1");
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));let stream=ctx.new_stream().unwrap();unsafe{ctx.disable_event_tracking();}
 let bm=ctx.load_module(Ptx::from_src(include_str!("baseline.ptx"))).unwrap();let cm=ctx.load_module(Ptx::from_src(include_str!("candidate.ptx"))).unwrap();
 let bf=bm.load_function("up_chance").unwrap();let cf=cm.load_function("up_chance").unwrap();
 let mut launches=0usize;let mut output_words=0u64;let mut immutable_words=0u64;let mut guards=0u64;let mut read_addresses=0u64;
 for (id,row) in cases.iter().enumerate(){
  assert_eq!(row["id"].as_u64().unwrap(),id as u64);let c=Case{d:row["descriptor"].as_array().unwrap().iter().map(|x|x.as_u64().unwrap() as u32).collect(),inv_bits:row["inv_bits"].as_u64().unwrap() as u32,mask_style:row["mask_style"].as_u64().unwrap() as u32};assert_eq!(c.d.len(),10);assert_eq!(c.family(),1);
  let up=Up::new(&c);let checked=up.read_contract(&c);read_addresses+=checked;let im=up.inputs();let seeds=up.seeds();u32w(&mut input,id as u32);vecw(&mut input,&c.d);vecs(&mut input,&im);vecs(&mut input,&seeds);
  let mut expected:Option<Vec<Vec<u32>>>=None;
  for (f,outfile) in [(&bf,&mut baseline),(&cf,&mut candidate)]{
   let (post,out)=up.run(&c,&stream,f);launches+=1;assert_eq!(post,im,"immutable case{id}");assert_eq!(out.iter().map(Vec::len).collect::<Vec<_>>(),seeds.iter().map(Vec::len).collect::<Vec<_>>());guards+=up.guards(&c,&out);
   if let Some(e)=&expected{assert_eq!(&out,e,"original/candidate raw case{id}");}else{expected=Some(out.clone());}
   u32w(outfile,id as u32);vecs(outfile,&post);vecs(outfile,&out);output_words+=out.iter().map(|v|v.len() as u64).sum::<u64>();immutable_words+=post.iter().map(|v|v.len() as u64).sum::<u64>();
  }
  emit(json!({"stage":"case","id":id,"descriptor":c.d,"inv_bits":c.inv_bits,"mask_style":c.mask_style,"read_addresses_prechecked":checked,"full_outputs_exact":true,"actual_immutable_inputs_exact":true,"guards_exact":true}));
 }
 stream.synchronize().unwrap();drop(bf);drop(cf);drop(bm);drop(cm);drop(stream);ctx.check_err().unwrap();
 for f in [&mut input,&mut baseline,&mut candidate]{f.flush().unwrap();f.get_ref().sync_all().unwrap();}
 assert_eq!(launches,2*cases.len());emit(json!({"stage":"complete","cases":cases.len(),"kernel_launches":launches,"output_words_both_arms":output_words,"immutable_words_both_arms":immutable_words,"guard_words_both_arms":guards,"all_ignored_and_used_read_addresses_prechecked":read_addresses,"full_outputs_exact":true,"actual_immutable_inputs_exact":true,"solver_executions":0,"performance_measured":false,"candidate_accepted":false}));
}
'''
main=main.replace('\\"','"')
probe=prefix+main;assert 'if new' not in probe and 'Down' not in probe and 'n0()+5' not in probe and 'n+5' not in probe
p=ROOT/'runs/E068-raw-probe.rs'
with p.open('x',encoding='utf-8',newline='\n') as f:f.write(probe)
print(p)