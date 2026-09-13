//! D07: static scheduling proxy. No CUDA allocation, launch or solver mutation.
use super::*;
use serde_json::json;
use std::collections::{BTreeSet,HashMap,HashSet,VecDeque};
use std::io::Write;
const NONE:u32=u32::MAX;
#[derive(Clone,Debug)]
struct Leaf {node:u32,live:u32,value:u32,sources:[u32;9]}
fn validate(rows:&[Leaf],np:usize,nodes:usize)->Result<(),String> {
    if !(3..=9).contains(&np)||rows.is_empty(){return Err("invalid dimensions".into());}
    let mut ids=HashSet::new();let mut values=HashSet::new();
    for r in rows {
        if r.node as usize>=nodes||!ids.insert(r.node)||!values.insert(r.value)||r.value==0||r.live.count_ones()<3||r.live>=(1<<np) {
            return Err("invalid or duplicate terminal/value".into());
        }
        let mut sources=HashSet::new();
        for q in 0..9 {
            if q<np && r.live&(1<<q)!=0 {
                if r.sources[q] as usize>=nodes+np-1||!sources.insert(r.sources[q]){return Err("invalid live source".into());}
            }else if r.sources[q]!=NONE {return Err("non-live source must be sentinel".into());}
        }
    }Ok(())
}
fn order(rows:&[Leaf])->Vec<usize> {
    let mut ids:Vec<_>=(0..rows.len()).collect();ids.sort_unstable_by_key(|&i|(rows[i].live,rows[i].sources,rows[i].node));ids
}
struct Lru {capacity:usize,tick:u64,last:HashMap<u32,u64>,age:BTreeSet<(u64,u32)>,misses:u64}
impl Lru {
    fn new(capacity:usize)->Self {assert!(capacity>0);Self{capacity,tick:0,last:HashMap::new(),age:BTreeSet::new(),misses:0}}
    fn touch(&mut self,id:u32) {
        self.tick+=1;
        if let Some(old)=self.last.remove(&id){assert!(self.age.remove(&(old,id)));}
        else {self.misses+=1;if self.last.len()==self.capacity {let (age,id)=self.age.pop_first().unwrap();assert_eq!(self.last.remove(&id),Some(age));}}
        self.last.insert(id,self.tick);self.age.insert((self.tick,id));
    }
}
fn stats(rows:&[Leaf],ids:&[usize],np:usize)->serde_json::Value {
    let mut seats=Vec::new();
    for p in 0..np {
        let mut caches=[Lru::new(64),Lru::new(256)];let mut refs=0u64;let mut terms=0usize;
        let mut previous=[NONE;9];let mut adjacent_shared=0u64;let mut adjacent_equal=0u64;
        let mut distinct=HashSet::new();let mut keys=HashSet::new();
        for &i in ids {let r=&rows[i];if r.live&(1<<p)==0{continue;}
            let mut key=r.sources;key[p]=NONE;
            for q in 0..np {let id=key[q];if id==NONE{continue;}
                refs+=1;distinct.insert(id);if previous.contains(&id){adjacent_shared+=1;}
                for c in &mut caches {c.touch(id);}
            }
            if terms>0&&key==previous{adjacent_equal+=1;}
            keys.insert(key);previous=key;terms+=1;
        }
        seats.push(json!({"seat":p,"terminals":terms,"references":refs,"distinct_sources":distinct.len(),"distinct_full_keys":keys.len(),
            "adjacent_shared_rows":adjacent_shared,"adjacent_equal_keys":adjacent_equal,"misses":caches.iter().map(|c|c.misses).collect::<Vec<_>>()}));
    }
    let total:Vec<u64>=(0..2).map(|k|seats.iter().map(|s|s["misses"][k].as_u64().unwrap()).sum()).collect();
    json!({"seats":seats,"total_misses":total})
}
#[test]
fn terminal_locality_lru_and_permutation_invariants() {
    for capacity in [1,2,4,64,256] {
        let mut lru=Lru::new(capacity);let mut oracle=VecDeque::new();let mut misses=0;let mut state=42u32;
        for _ in 0..4000 {state=state.wrapping_mul(1664525).wrapping_add(1013904223);let id=(state>>10)%311;
            if let Some(at)=oracle.iter().position(|x|*x==id){oracle.remove(at);}else{misses+=1;if oracle.len()==capacity{oracle.pop_front();}}
            oracle.push_back(id);lru.touch(id);assert_eq!(lru.misses,misses);
            assert_eq!(lru.age.iter().map(|(_,id)|*id).collect::<Vec<_>>(),oracle.iter().copied().collect::<Vec<_>>());
        }
    }
    let make=|node,source|Leaf{node,live:7,value:node,sources:[source,1,2,NONE,NONE,NONE,NONE,NONE,NONE]};
    let rows=vec![make(3,8),make(4,0),make(5,8)];validate(&rows,3,10).unwrap();assert_eq!(order(&rows),vec![1,0,2]);
    let mut bad=rows.clone();bad[1].value=bad[0].value;assert!(validate(&bad,3,10).is_err());
    bad=rows.clone();bad[1].sources[3]=3;assert!(validate(&bad,3,10).is_err());
    bad=rows.clone();bad[1].node=bad[0].node;assert!(validate(&bad,3,10).is_err());
    let a=stats(&rows,&[0,1,2],3);let b=stats(&rows,&order(&rows),3);
    assert_eq!(a["total_misses"],b["total_misses"]);
    assert_eq!(b["seats"][1]["adjacent_equal_keys"],1);
}
#[test]
#[ignore = "read-only saved-game structural inventory; requires immutable input"]
fn terminal_locality_inventory_from_save() {
    let input=std::env::var("PREFLOP_GPU_LOCALITY_INPUT").unwrap();let output=std::env::var("PREFLOP_GPU_LOCALITY_OUTPUT").unwrap();
    let witness=std::env::var("PREFLOP_GPU_LOCALITY_WITNESS").unwrap();assert!(!std::path::Path::new(&output).exists());
    let path=concat!(env!("CARGO_MANIFEST_DIR"),"/../../cache/preflop_eq169.bin");let b=std::fs::read(path).unwrap();
    let eq=Arc::new(crate::preflop::equity::EquityTable::load_or_build(path,u32::from_le_bytes(b[..4].try_into().unwrap())));
    let s=PreflopSolver::load_game(&input,eq).unwrap();assert!(s.multiway.is_some());
    let sources=reach_sources(&s);let values=ValuePlan::build(&s);
    let rows:Vec<_>=s.nodes.iter().enumerate().filter(|(_,n)|n.kind==KIND_POT_SHARE&&n.live.count_ones()>=3).map(|(i,n)|{
        let mut src=[NONE;9];for q in 0..s.n{if n.live&(1<<q)!=0{src[q]=sources[i*s.n+q];}}
        Leaf{node:i as u32,live:n.live as u32,value:values.slots[i],sources:src}
    }).collect();validate(&rows,s.n,s.nodes.len()).unwrap();
    let ids=order(&rows);let mut coverage=ids.clone();coverage.sort_unstable();assert_eq!(coverage,(0..rows.len()).collect::<Vec<_>>());
    let mut out=std::fs::OpenOptions::new().write(true).create_new(true).open(witness).unwrap();
    out.write_all(b"D07V1\0\0\0").unwrap();for v in [s.n as u32,s.nodes.len() as u32,rows.len() as u32]{out.write_all(&v.to_le_bytes()).unwrap();}
    let mut out=std::io::BufWriter::new(out);
    for r in &rows {for v in [r.node,r.live,r.value].into_iter().chain(r.sources){out.write_all(&v.to_le_bytes()).unwrap();}}
    out.flush().unwrap();
    let result=json!({"input":input,"players":s.n,"nodes":s.nodes.len(),"iteration":s.iteration,"terminals":rows.len(),
        "capacities":[64,256],"candidate_key":"live_mask, ordered_sources_with_sentinels, node_id","changed_positions":ids.iter().enumerate().filter(|(i,id)|*i!=**id).count(),
        "exact_coverage":true,"unique_terminal_values":true,"baseline":stats(&rows,&(0..rows.len()).collect::<Vec<_>>(),s.n),"candidate":stats(&rows,&ids,s.n),
        "scope":"Host scheduling proxy only; not measured GPU cache hits, speed or convergence. No solver mutation or CUDA launch."});
    std::fs::write(output,serde_json::to_vec_pretty(&result).unwrap()).unwrap();println!("D07_LOCALITY {}",result);
}
