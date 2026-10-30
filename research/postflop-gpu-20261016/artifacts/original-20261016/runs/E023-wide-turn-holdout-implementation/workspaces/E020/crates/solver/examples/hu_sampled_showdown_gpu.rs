//! Research GPU showdown verification: native and independent 5-card reference.
#[cfg(not(feature="gpu"))]fn main(){panic!("requires --features gpu");}

#[cfg(feature="gpu")]
fn main()->Result<(),Box<dyn std::error::Error>>{
 use cudarc::driver::{CudaContext,LaunchConfig,PushKernelArg};
 use solver::{parse_cards,evaluator::evaluate7};use serde_json::json;
 fn e(err:impl std::fmt::Debug)->String{format!("{err:?}")}
 fn slow5(cards:&[u8])->u32{
   let mut counts=std::collections::BTreeMap::new();for c in cards{*counts.entry(c/4).or_insert(0u8)+=1;}
   let mut groups:Vec<_>=counts.iter().map(|(&r,&n)|(n,r)).collect();groups.sort_by(|a,b|b.cmp(a));
   let mut ranks:Vec<_>=counts.keys().copied().collect();ranks.sort_by(|a,b|b.cmp(a));
   let flush=cards.iter().all(|c|c%4==cards[0]%4);
   let straight=if ranks.len()==5&&ranks[0]-ranks[4]==4{Some(ranks[0])}else if ranks==[12,3,2,1,0]{Some(3)}else{None};
   let (cat,tie)=if flush&&straight.is_some(){(8,vec![straight.unwrap()])}
     else if groups[0].0==4{(7,vec![groups[0].1,groups[1].1])}
     else if groups[0].0==3&&groups[1].0==2{(6,vec![groups[0].1,groups[1].1])}
     else if flush{(5,ranks)}else if let Some(s)=straight{(4,vec![s])}
     else if groups[0].0==3{(3,groups.iter().map(|g|g.1).collect())}
     else if groups[0].0==2&&groups[1].0==2{(2,groups.iter().map(|g|g.1).collect())}
     else if groups[0].0==2{(1,groups.iter().map(|g|g.1).collect())}else{(0,ranks)};
   let mut value=cat;for i in 0..5{value=(value<<4)|tie.get(i).copied().unwrap_or(0) as u32;}value
 }
 fn slow7(cards:&[u8])->u32{
   let mut best=0;for a in 0..7{for b in a+1..7{let five:Vec<_>=(0..7).filter(|&i|i!=a&&i!=b).map(|i|cards[i]).collect();best=best.max(slow5(&five));}}best
 }
 fn next(seed:&mut u64)->u64{*seed=seed.wrapping_add(0x9e3779b97f4a7c15);let mut z=*seed;z=(z^(z>>30)).wrapping_mul(0xbf58476d1ce4e5b9);z=(z^(z>>27)).wrapping_mul(0x94d049bb133111eb);z^(z>>31)}
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),3);assert!(!std::path::Path::new(&args[2]).exists());
 let known=[("AsKsQsJsTs2d3c",8),("AsAhAdAcKs2c3d",7),("AsAhAdKsKhKd2c",6),
   ("AsQs9s6s2sKdJh",5),("As2d3c4h5sKdQh",4),("AsAhAdKsQhJd2c",3),
   ("AsAhKsKhQsQh2c",2),("AsAhKsQhJd9c2s",1),("AsKdQhJc9s4d2h",0)];
 let mut cases:Vec<Vec<u8>>=vec![];
 for(text,cat)in known{let cards=parse_cards(text)?;assert_eq!(slow7(&cards)>>20,cat);assert_eq!(evaluate7(&cards),slow7(&cards));cases.push(cards);}
 let mut seed=20260922u64;
 for _ in 0..200_000{let mut cards=vec![];let mut mask=0u64;
   while cards.len()<7{let card=(next(&mut seed)%52)as u8;if mask&(1u64<<card)==0{cards.push(card);mask|=1u64<<card;}}
   cases.push(cards);
 }
 // All suit permutations of the named controls and 128 diverse generated cases.
 let originals=cases[..137].to_vec();
 for cards in &originals{for a in 0..4{for b in 0..4{for c in 0..4{for d in 0..4{
   let perm=[a,b,c,d];if (0..4).any(|i|(i+1..4).any(|j|perm[i]==perm[j])){continue;}
   let mut moved:Vec<_>=cards.iter().map(|x|x/4*4+perm[(x%4)as usize]).collect();
   assert_eq!(evaluate7(&moved),evaluate7(cards));moved.reverse();cases.push(moved);
 }}}}}
 let expected:Vec<u32>=cases.iter().map(|c|evaluate7(c)).collect();
 for i in 0..4096{assert_eq!(expected[i],slow7(&cases[i]),"independent 5-card reference");}
 let mut categories=[0u64;9];for &v in &expected{categories[(v>>20)as usize]+=1;}assert!(categories.iter().all(|&n|n>0));
 let cards:Vec<u8>=cases.into_iter().flatten().collect();
 let source=std::fs::read_to_string(&args[0])?+"\n"+&std::fs::read_to_string(&args[1])?;
 let ctx=CudaContext::new(0).map_err(e)?;let stream=ctx.default_stream();let(ma,mi)=ctx.compute_capability().map_err(e)?;
 let arch:&'static str=Box::leak(format!("compute_{ma}{mi}").into_boxed_str());
 let ptx=cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(e)?;
 let module=ctx.load_module(ptx).map_err(e)?;let f=module.load_function("pf_showdown_probe").map_err(e)?;
 let dc=stream.clone_htod(&cards).map_err(e)?;let mut output=stream.alloc_zeros::<u32>(expected.len()).map_err(e)?;
 let n=expected.len()as i32;
 for _ in 0..2{unsafe{stream.launch_builder(&f).arg(&n).arg(&dc).arg(&mut output).launch(LaunchConfig::for_num_elems(n as u32)).map_err(e)?;}
   let actual=stream.clone_dtoh(&output).map_err(e)?;assert_eq!(actual,expected,"GPU rank mismatch");}
 let result=json!({"passed":true,"cases":expected.len(),"native_integer_values_exact":true,"repeat_exact":true,
   "independent_best_of_21_cases":4096,"suit_and_order_variants":137*24,"category_counts":categories,
   "random_seed":20260922,"production_modified":false,"poker_trainer_qualified":false,
   "limits":"Ranking valid 7-card hands only. Random test cards use a deterministic modulo-based generator for coverage, not a qualified game-deal sampler. No equity or training convergence claim."});
 std::fs::write(&args[2],serde_json::to_vec_pretty(&result)?)?;println!("{}",result);Ok(())
}
