//! Read-only orbit census of the exact-observation sparse checkpoint.
use rayon::prelude::*;
use serde_json::json;
use std::time::Instant;
fn street(hi:u64,lo:u64)->usize{if hi>>63==0{0}else if(lo>>30)&63==63{1}else if(lo>>36)&63==63{2}else{3}}
fn permutations()->Vec<[u8;4]>{let mut out=vec![];for a in 0..4{for b in 0..4{for c in 0..4{for d in 0..4{
 let p=[a,b,c,d];if (0..4).all(|i|(i+1..4).all(|j|p[i]!=p[j])){out.push(p);}
}}}}assert_eq!(out.len(),24);out}
fn transform(lo:u64,p:[u8;4])->u64{
 let mut cs=[0u8;7];for i in 0..7{let c=((lo>>(i*6))&63)as u8;assert!(c<52||c==63);cs[i]=if c==63{63}else{(c/4)*4+p[(c%4)as usize]};}
 cs[..2].sort_unstable();cs[2..5].sort_unstable();let mut out=lo&(1u64<<42);for i in 0..7{out|=(cs[i]as u64)<<(6*i);}out
}
fn canonical(lo:u64,ps:&[[u8;4]])->u64{ps.iter().map(|&p|transform(lo,p)).min().unwrap()}
fn main()->Result<(),Box<dyn std::error::Error>>{
 let args:Vec<_>=std::env::args().skip(1).collect();assert_eq!(args.len(),2);assert!(!std::path::Path::new(&args[1]).exists());
 rayon::ThreadPoolBuilder::new().num_threads(4).build_global()?;
 let started=Instant::now();let bytes=std::fs::read(&args[0])?;assert_eq!(&bytes[..8],b"GTSAMP01");
 let n=u64::from_le_bytes(bytes[24..32].try_into().unwrap())as usize;assert!(n<=8_000_000&&bytes.len()==32+88*n);
 let ps=permutations();let mut original=[0usize;4];let mut covered=std::collections::BTreeSet::new();
 for row in bytes[32..].chunks_exact(88){let hi=u64::from_le_bytes(row[..8].try_into().unwrap());let lo=u64::from_le_bytes(row[8..16].try_into().unwrap());original[street(hi,lo)]+=1;}
 // Orbit invariance controls across all streets, without examining values.
 for stage in 0..4{let mut controls=0;for row in bytes[32..].chunks_exact(88){let hi=u64::from_le_bytes(row[..8].try_into().unwrap());let lo=u64::from_le_bytes(row[8..16].try_into().unwrap());
  if street(hi,lo)!=stage{continue;}
  let k=canonical(lo,&ps);for &p in &ps{let x=transform(lo,p);assert_eq!(canonical(x,&ps),k);assert_eq!(street(hi,x),stage);}
  assert_eq!(canonical(k,&ps),k);covered.insert(stage);controls+=1;if controls==64{break;}
 }}assert_eq!(covered.len(),4);
 let mut keys:Vec<(u64,u64)>=bytes[32..].par_chunks_exact(88).map(|row|{
  let hi=u64::from_le_bytes(row[..8].try_into().unwrap());let lo=u64::from_le_bytes(row[8..16].try_into().unwrap());(hi,canonical(lo,&ps))}).collect();
 keys.par_sort_unstable();let mut unique=[0usize;4];let mut duplicates=[0usize;4];let mut previous=None;
 for key in keys{let s=street(key.0,key.1);if previous==Some(key){duplicates[s]+=1;}else{unique[s]+=1;}previous=Some(key);}
 let total:usize=unique.iter().sum();assert_eq!(original.iter().sum::<usize>(),n);for i in 0..4{assert_eq!(unique[i]+duplicates[i],original[i]);}
 let result=json!({"passed":true,"source_entries":n,"original_by_street":original,"suit_orbits_by_street":unique,
  "suit_orbits":total,"reduction_factor":n as f64/total as f64,"orbit_invariance_controls":256*24,
  "seconds":started.elapsed().as_secs_f64(),"scope":"Read-only exact observation suit-orbit occupancy census. No state values combined, no policy trained, no claim about changed trajectories or convergence.",
  "limits":"Preserves actor, rank, own cards versus board roles, ordered turn/river and full action history. Canonicalizes only suit names, with private pair and flop listing-order normalization. Counts occupied keys in this checkpoint; eventual orbit-size bounds are not measured training gains.",
  "production_modified":false});std::fs::write(&args[1],serde_json::to_vec_pretty(&result)?)?;println!("{}",result);Ok(())
}
