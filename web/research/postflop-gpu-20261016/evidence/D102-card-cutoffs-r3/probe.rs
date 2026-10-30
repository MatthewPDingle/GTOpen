use std::{collections::{BTreeMap,HashSet},fs,io::Write};
struct GpuPlan {num_slots:usize,hand_c1:[Vec<u32>;2],hand_c2:[Vec<u32>;2],riv_off:[Vec<u32>;2],riv_cnt:[Vec<u32>;2],riv_sorted_idx:[Vec<u32>;2],riv_lower:[Vec<u32>;2],riv_upper:[Vec<u32>;2],riv_card_off:[Vec<u32>;2],riv_card_pos:[Vec<u32>;2]}
include!("helper.rs");
fn u32le(b:&[u8],at:&mut usize)->u32 {let x=u32::from_le_bytes(b[*at..*at+4].try_into().unwrap());*at+=4;x}
fn u64le(b:&[u8],at:&mut usize)->u64 {let x=u64::from_le_bytes(b[*at..*at+8].try_into().unwrap());*at+=8;x}
fn arr(v:&[u64])->[Vec<u32>;2] {assert_eq!(v[0],2);let mut at=1;let a=std::array::from_fn(|_|{let n=v[at] as usize;at+=1;let q=v[at..at+n].iter().map(|&x|u32::try_from(x).unwrap()).collect();at+=n;q});assert_eq!(at,v.len());a}
fn main(){let a:Vec<String>=std::env::args().collect();assert_eq!(a.len(),3);let id:u32=a[1].parse().unwrap();let raw=fs::read(&a[2]).unwrap();assert_eq!(&raw[..16],b"D092-PLAN-RAW1\0\0");let mut at=16;assert_eq!(u32le(&raw,&mut at),id);assert_eq!(u32le(&raw,&mut at),53);assert_eq!(u64le(&raw,&mut at),u64le(&raw,&mut at));
let wanted=[38u32,39,43,44,45,46,47,48,49,50,51];let mut fields=BTreeMap::new();
for f in 0..53 {assert_eq!(u32le(&raw,&mut at),f);for v in 0..4 {let n=u64le(&raw,&mut at) as usize;if v==2 && wanted.contains(&f){let mut w=Vec::with_capacity(n);for _ in 0..n {w.push(u64le(&raw,&mut at));}assert!(fields.insert(f,w).is_none());}else{at+=8*n;assert!(at<=raw.len());}}}
// Consume the complete two trailing encoded vectors, even though they are unrelated.
for _ in 0..2 {let n=u64le(&raw,&mut at) as usize;at+=8*n;}assert_eq!(at,raw.len());drop(raw);
let p=GpuPlan{num_slots:fields[&43][0] as usize,hand_c1:arr(&fields[&38]),hand_c2:arr(&fields[&39]),riv_off:arr(&fields[&44]),riv_cnt:arr(&fields[&45]),riv_sorted_idx:arr(&fields[&46]),riv_lower:arr(&fields[&48]),riv_upper:arr(&fields[&49]),riv_card_off:arr(&fields[&50]),riv_card_pos:arr(&fields[&51])};
let strengths=arr(&fields[&47]);drop(fields);let (lo,hi)=pack_show_bounds(&p);
let(mut checks,mut rows,mut positions,mut maxcard,mut maxcount)=(0u64,0u64,0u64,0usize,0u32);let mut caps=0usize;
for s in [&lo,&hi] {for v in s {caps+=v.capacity()*4;}}
for player in 0..2 {
 assert_eq!(lo[player].len(),p.riv_lower[player].len());assert_eq!(hi[player].len(),p.riv_upper[player].len());assert_eq!(p.hand_c1[player].len(),p.hand_c2[player].len());
 let mut hands=HashSet::new();for (&c,&d) in p.hand_c1[player].iter().zip(&p.hand_c2[player]) {assert!(c<52&&d<52&&c!=d);assert!(hands.insert((c.min(d),c.max(d))));checks+=2;}
 let o=1-player;let mut covered=0;
 for slot in 0..p.num_slots {
  let b=p.riv_off[player][slot] as usize;let e=b+p.riv_cnt[player][slot] as usize;assert_eq!(b,covered);covered=e;
  let ob=p.riv_off[o][slot] as usize;let oe=ob+p.riv_cnt[o][slot] as usize;let os=&strengths[o][ob..oe];assert!(os.windows(2).all(|w|w[0]<=w[1]));maxcount=maxcount.max(p.riv_cnt[o][slot]);
  // Rebuild all52opponent card lists from independent hand membership.
  let mut lists:Vec<Vec<u32>>=vec![Vec::new();52];for (pos,&h) in p.riv_sorted_idx[o][ob..oe].iter().enumerate(){lists[p.hand_c1[o][h as usize] as usize].push(pos as u32);lists[p.hand_c2[o][h as usize] as usize].push(pos as u32);}
  for c in 0..52 {let k=slot*53+c;let aa=p.riv_card_off[o][k] as usize;let bb=p.riv_card_off[o][k+1] as usize;assert_eq!(lists[c].as_slice(),&p.riv_card_pos[o][aa..bb]);assert!(bb-aa<=51);maxcard=maxcard.max(bb-aa);checks+=2;}
  for j in b..e {
   let lb=p.riv_lower[player][j];let ub=p.riv_upper[player][j];let strength=strengths[player][j];assert!(lb<=ub&&ub<=p.riv_cnt[o][slot]&&ub<=1326);
   // Independent linear rank classification validates the retained global bounds.
   assert_eq!(os.iter().filter(|&&v|v<strength).count(),lb as usize);assert_eq!(os.iter().filter(|&&v|v<=strength).count(),ub as usize);
   assert_eq!(lo[player][j]&2047,lb);assert_eq!(hi[player][j]&2047,ub);assert_eq!(lo[player][j]>>23,0);assert_eq!(hi[player][j]>>23,0);checks+=7;rows+=1;
   let h=p.riv_sorted_idx[player][j] as usize;
   for (x,c) in [p.hand_c1[player][h],p.hand_c2[player][h]].into_iter().enumerate(){let v=&lists[c as usize];let w=if x==0{lo[player][j]}else{hi[player][j]};let l=((w>>11)&63) as usize;let u=((w>>17)&63) as usize;assert!(l<=u&&u<=v.len());
    assert_eq!(l,v.iter().filter(|&&pos|pos<lb).count());assert_eq!(u,v.iter().filter(|&&pos|pos<ub).count());checks+=3;
    // Per-accumulator ordered selector equality, including empty/tie segments.
    let joined=v[..l].iter().chain(&v[l..u]).chain(&v[u..]);assert!(joined.eq(v.iter()));checks+=1;
    for (t,&pos) in v.iter().enumerate(){assert_eq!(t<l,pos<lb);assert_eq!(t>=u,pos>=ub);checks+=2;positions+=1;}
   }
  }
 }
 assert_eq!(covered,p.riv_lower[player].len());checks+=1;
}
let mut field_tests=0u64;
if id==0 {for g in 0..=1326u32 {for l in 0..=51u32 {for u in l..=51u32 {let w=g|(l<<11)|(u<<17);assert_eq!(w&2047,g);assert_eq!((w>>11)&63,l);assert_eq!((w>>17)&63,u);assert_eq!(w>>23,0);field_tests+=1;}}}
 // Every lower/upper threshold for each conservative card-list length. Sparse deterministic positions include all global endpoints.
 for n in 0..=51u32 {let v:Vec<u32>=(0..n).map(|t|if n<=1{0}else{t*1325/(n-1)}).collect();for lb in 0..=1326u32 {for ub in [lb,(lb+17).min(1326),1326] {let l=v.partition_point(|&pos|pos<lb);let u=v.partition_point(|&pos|pos<ub);for (t,&pos) in v.iter().enumerate(){assert_eq!(t<l,pos<lb);assert_eq!(t>=u,pos>=ub);checks+=2;}}}}
}
let host_payload_bytes=(p.riv_lower[0].len()+p.riv_lower[1].len())*8;assert_eq!(caps,host_payload_bytes);assert!(caps<=20*1024*1024);
let report=serde_json::json!({"case_id":id,"status":"pass_exact_integer_selectors","slots":p.num_slots,"rows":rows,"selected_card_positions":positions,"checks":checks,"exhaustive_disjoint_field_values":field_tests,"max_card_list":maxcard,"max_global_count":maxcount,"extra_host_payload_bytes":host_payload_bytes,"extra_host_capacity_bytes":caps,"extra_gpu_bytes":0,"gpu_executions":0,"floating_results_compared":false,"performance_measured":false,"candidate_accepted":false});let mut out=std::io::stdout().lock();writeln!(out,"D102_RESULT {report}").unwrap();out.flush().unwrap();}
