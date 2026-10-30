"""Prepare CPU-only work-list permutation controls; no source activation."""
import difflib, html, json, re, shutil, sys, urllib.request
from pathlib import Path
ROOT = Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0, str(ROOT/'runs/accepted-E051'))
import common_e051 as old
old.custody()
H = ROOT/'runs/D092-action-arity-order'
assert not H.exists()
assert shutil.disk_usage(ROOT).free >= 82*1024**3
H.mkdir()
old.save(H/'preparation-receipt.json', {'at':old.now(), 'prior_preparation':'PowerShell-fed Python wrapper failed parsing nested triple quotes before any file creation, compilation, native execution or source activation. Corrected delivery of the preparation script only; no experiment outputs existed.'})
source = old.REPO/'crates/solver/src/gpu/plan.rs'
raw = source.read_bytes()
old.pin(source, 'aca00f163db77af01960cd55cb5484226f25c7c58bae325d4c50ebc44672b680')
needle = b'        let (action_nodes, action_spans) = flatten_nodes(action_by_level);'
assert raw.count(needle) == 1
change = (b'        // Group independent blocks by action count within each existing level.\r\n'
          b'        for nodes in &mut action_by_level {\r\n'
          b'            nodes.sort_unstable_by_key(|&n| spot.tree.nodes[n as usize].num_children);\r\n'
          b'        }\r\n')
(H/'accepted-plan.rs').write_bytes(raw)
(H/'candidate-plan.rs').write_bytes(raw.replace(needle, change+needle))
(H/'game.rs').write_bytes((old.REPO/'crates/solver/src/game.rs').read_bytes())
(H/'candidate.patch').write_text(''.join(difflib.unified_diff(raw.decode().splitlines(True), raw.replace(needle,change+needle).decode().splitlines(True), fromfile='a/crates/solver/src/gpu/plan.rs', tofile='b/crates/solver/src/gpu/plan.rs')), encoding='utf-8', newline='')
fields = []
for line in raw.decode().split('pub struct GpuPlan {',1)[1].split('\n}',1)[0].splitlines():
    m = re.match(r'    pub (\w+): (.+),\s*$', line)
    if m: fields.append({'name':m[1], 'type':m[2]})
assert len(fields) >= 45 and len({f['name'] for f in fields}) == len(fields)
old.save(H/'field-schema.json', {'fields':fields, 'encoding':'Each primitive is one little-endian u64; f32 uses to_bits; i32 uses Rust as u64. Vec encodes length then items. Array encodes constant length then items. LevelSpan is start,count. Separate capacities encode Vec capacity and recursive array length. Four vectors per field: baseline capacities,candidate capacities,baseline words,candidate words. Final extras are length-prefixed encoded __node_kind and __children from shared immutable Spot.'})
configs = [v['config'] for v in old.read(ROOT/'runs/B182/report.json')['results']]
assert len(configs) == 3
for i,c in enumerate(configs):
    (H/f'fixture-{i}.json').write_text(json.dumps(c,indent=2)+'\n', encoding='utf-8')
url = 'https://doc.rust-lang.org/std/primitive.slice.html'
page = urllib.request.urlopen(url, timeout=20).read().decode()
at = page.index('id="method.sort_unstable_by_key"')
end = page.find('<h5',at)
section = page[at:end if end >= 0 else at+18000]
excerpt = ' '.join(html.unescape(re.sub('<[^>]+>', ' ', section)).split())
assert 'does not allocate' in excerpt
old.save(H/'rust-sort-reference.json', {'url':url+'#method.sort_unstable_by_key', 'retrieved_at':old.now(), 'excerpt':excerpt[:2800], 'use':'In-place unstable sort may reorder equal keys. All per-level multisets and actual data ownership must be checked.'})
old.save(H/'proposal.json', {
    'id':'D092-action-arity-order', 'at':old.now(), 'status':'CPU_CONTROL_ONLY_NOT_COMPILED', 'prospective_candidate':'E056',
    'hypothesis':'Group existing per-level action CTAs by actual arity with one CPU list permutation. Existing dispatchers, node IDs, child order, offsets, arenas, spans, CUDA source and launch structure stay unchanged. Possible inter-CTA instruction/data coherence is unproven; individual CTAs are already arity-uniform. No hardware cache bottleneck or speedup established. Sorting and locality costs remain inside future complete-cycle timing.',
    'history_review':{'E005':'Already reordered shared work lists with two-action prefixes plus new direct kernel, spans, dispatch and 4096 threshold.', 'E014':'Already reordered three-action prefixes plus direct3 launches/count metadata and 4096 threshold.', 'new_intervention':'Ordering alone across all actual arities using unchanged dispatch and one launch per span. No direct entrypoint, threshold, new metadata/span or scratch Vec. This decomposes earlier composites, not their retest or resource rescue. No key/arity/threshold sweep.'},
    'source_review':['Block index selects node through nodes[start+blockIdx.x]. Persistent addressing uses node/child IDs or explicit slots.', 'Down action writes child actor reach. For every level, (actor,slot) writes must be unique and disjoint from all corresponding input rows. Player buffers are separate.', 'Up action/eval writes node CFV and reads child CFVs. All current-level writes must be unique and disjoint from child inputs, including terminal/parity caches.', 'Regret/strategy intervals use node_data_off,na,nh and must be disjoint per actor and within arena bounds.', 'Within-node FP order, child order, terminal/chance phases and stream boundaries are unchanged. Action kernels have no cross-node atomics.'],
    'controls':'12 separate CPU-only processes: 3 frozen primary configurations x iso off/on x compact/full arenas. Compile exact accepted/candidate Plan modules plus exact local game.rs, retaining crate-private RiverTable access without edits. Dump all fields/capacities/struct sizes, floats by bits; only action_nodes order may differ. Root replays complete raw fields and concrete ownership. Diagnostic CPU timings only.',
    'future_acceptance':'Unrounded >=1% complete-cycle gain, exact full states/stops/checkpoints, no repeatable fixture slowdown, separate fresh16 confirmation and broader/capacity/F32/save/continuation/holdout/cumulative gates. No adoption from this CPU control.',
    'reviewer':'Root source/history review; not external independent review', 'production_source_activated':False, 'gpu_executions':0, 'optimization_accepted':False})
probe = r'''#![allow(dead_code)]
pub use solver::{cards,cfr,evaluator,range,store,tree};
#[path="game.rs"] pub mod game;
#[path="accepted-plan.rs"] mod accepted;
#[path="candidate-plan.rs"] mod candidate;
use std::{fs::{File,OpenOptions},io::{BufWriter,Write},time::Instant};
trait Encode {fn encode(&self,v:&mut Vec<u64>);fn caps(&self,_v:&mut Vec<u64>) {}}
macro_rules! prim {($($t:ty),*)=>{$(impl Encode for $t {fn encode(&self,v:&mut Vec<u64>){v.push(*self as u64);}})*};}
prim!(usize,u64,u32,i32,u8,bool);
impl Encode for f32 {fn encode(&self,v:&mut Vec<u64>){v.push(self.to_bits() as u64);}}
impl<T:Encode> Encode for Vec<T>{fn encode(&self,v:&mut Vec<u64>){v.push(self.len() as u64);for x in self{x.encode(v);}}fn caps(&self,v:&mut Vec<u64>){v.push(self.capacity() as u64);for x in self{x.caps(v);}}}
impl<T:Encode,const N:usize> Encode for [T;N]{fn encode(&self,v:&mut Vec<u64>){v.push(N as u64);for x in self{x.encode(v);}}fn caps(&self,v:&mut Vec<u64>){v.push(N as u64);for x in self{x.caps(v);}}}
impl Encode for accepted::LevelSpan {fn encode(&self,v:&mut Vec<u64>){v.extend([self.start as u64,self.count as u64]);}}
impl Encode for candidate::LevelSpan {fn encode(&self,v:&mut Vec<u64>){v.extend([self.start as u64,self.count as u64]);}}
fn words<T:Encode>(v:&T)->Vec<u64>{let mut w=Vec::new();v.encode(&mut w);w}
fn caps<T:Encode>(v:&T)->Vec<u64>{let mut w=Vec::new();v.caps(&mut w);w}
fn dump(f:&mut BufWriter<File>,v:&[u64]){f.write_all(&(v.len() as u64).to_le_bytes()).unwrap();let mut b=Vec::with_capacity(65536);for c in v.chunks(8192){b.clear();for x in c{b.extend(x.to_le_bytes());}f.write_all(&b).unwrap();}}
fn field<A:Encode,B:Encode>(f:&mut BufWriter<File>,id:u32,name:&str,a:&A,b:&B,permute:bool)->u64{let ca=caps(a);let cb=caps(b);assert_eq!(ca,cb,"capacity {name}");let wa=words(a);let wb=words(b);if !permute{assert_eq!(wa,wb,"field {name}");}f.write_all(&id.to_le_bytes()).unwrap();for v in [&ca,&cb,&wa,&wb]{dump(f,v);}wa.len() as u64}
fn main(){let args:Vec<String>=std::env::args().collect();assert_eq!(args.len(),3);let id:usize=args[1].parse().unwrap();assert!(id<12);let fixtures=[include_str!("fixture-0.json"),include_str!("fixture-1.json"),include_str!("fixture-2.json")];let config:game::SpotConfig=serde_json::from_str(fixtures[id/4]).unwrap();let spot=game::Spot::new(config).unwrap();let iso=(id%4)>=2;let full=id%2==1;
let mut a:Option<accepted::GpuPlan>=None;let mut b:Option<candidate::GpuPlan>=None;let(mut ams,mut bms)=(0.0,0.0);
for candidate_first in [id%2==1,id%2!=1]{let t=Instant::now();if candidate_first{let mut p=candidate::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}bms=t.elapsed().as_secs_f64()*1000.0;b=Some(p);}else{let mut p=accepted::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}ams=t.elapsed().as_secs_f64()*1000.0;a=Some(p);}}
let a=a.unwrap();let b=b.unwrap();let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(&args[2]).unwrap());f.write_all(b"D092-PLAN-RAW1\0\0").unwrap();f.write_all(&(id as u32).to_le_bytes()).unwrap();f.write_all(&(__FIELDCOUNT__u32).to_le_bytes()).unwrap();for n in [std::mem::size_of::<accepted::GpuPlan>(),std::mem::size_of::<candidate::GpuPlan>()]{f.write_all(&(n as u64).to_le_bytes()).unwrap();}assert_eq!(std::mem::size_of::<accepted::GpuPlan>(),std::mem::size_of::<candidate::GpuPlan>());
let mut count=0u64;
__FIELDS__
let kinds:Vec<u8>=spot.tree.nodes.iter().map(|n|n.kind).collect();dump(&mut f,&words(&kinds));dump(&mut f,&words(&spot.tree.children));f.flush().unwrap();f.get_ref().sync_all().unwrap();
let v=serde_json::json!({"id":id,"fixture_index":id/4,"board":spot.config.board,"iso_requested":iso,"iso_active":a.iso_active,"full_arenas":full,"first":if id%2==1{"candidate"}else{"baseline"},"baseline_plan_ms":ams,"candidate_plan_ms":bms,"fields":__FIELDCOUNT__,"baseline_words":count,"nodes":spot.tree.nodes.len(),"action_nodes":a.action_nodes.len(),"all_nonpermuted_fields_bitwise_equal":true,"all_vec_capacities_equal":true,"struct_size_equal":true,"gpu_executions":0,"full_cycle_performance_measured":false});println!("D092 {v}");}
'''
probe = probe.replace('__FIELDCOUNT__',str(len(fields))).replace('__FIELDS__','\n'.join(f'count+=field(&mut f,{i},"{f["name"]}",&a.{f["name"]},&b.{f["name"]},{str(f["name"]=="action_nodes").lower()});' for i,f in enumerate(fields)))
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
print(json.dumps({'id':'D092-action-arity-order','path':str(H),'fields':len(fields),'candidate_sha256':old.sha(H/'candidate-plan.rs'),'native_executions':0,'production_source_activated':False}),flush=True)
