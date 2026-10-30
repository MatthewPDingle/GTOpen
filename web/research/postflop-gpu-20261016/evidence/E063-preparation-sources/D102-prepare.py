"""Freeze one distinct per-card boundary-precomputation form before execution."""
import ast,difflib,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();old.ar.refuse_active(old.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
assert shutil.disk_usage(ROOT).free>=82*1024**3
assert old.read(ROOT/'runs/E062-closure/decision.json')['D101_fixed_docket_exhausted']
H=ROOT/'runs/D102-card-cutoffs';S=ROOT/'runs/E063-source';assert not H.exists() and not S.exists();H.mkdir();S.mkdir()
helper=r'''// E063: CPU-only upload representation; public GpuPlan tables retain their meaning.
fn pack_show_bounds(plan: &GpuPlan) -> ([Vec<u32>; 2], [Vec<u32>; 2]) {
    let mut lower = plan.riv_lower.clone();
    let mut upper = plan.riv_upper.clone();
    for p in 0..2 {
        let o = 1 - p;
        for slot in 0..plan.num_slots {
            let begin = plan.riv_off[p][slot] as usize;
            let end = begin + plan.riv_cnt[p][slot] as usize;
            for j in begin..end {
                let i = plan.riv_sorted_idx[p][j] as usize;
                let lb = plan.riv_lower[p][j];
                let ub = plan.riv_upper[p][j];
                debug_assert!(lb <= ub && ub <= 1326);
                for (x, card) in [plan.hand_c1[p][i], plan.hand_c2[p][i]].into_iter().enumerate() {
                    let c = slot * 53 + card as usize;
                    let a = plan.riv_card_off[o][c] as usize;
                    let b = plan.riv_card_off[o][c + 1] as usize;
                    let positions = &plan.riv_card_pos[o][a..b];
                    debug_assert!(positions.len() <= 51);
                    let lo = positions.partition_point(|&pos| pos < lb) as u32;
                    let hi = positions.partition_point(|&pos| pos < ub) as u32;
                    if x == 0 { lower[p][j] |= (lo << 11) | (hi << 17); }
                    else { upper[p][j] |= (lo << 11) | (hi << 17); }
                }
            }
        }
    }
    (lower, upper)
}
'''
(H/'helper.rs').write_text(helper,encoding='utf-8',newline='\n')
base=(old.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes();text=base.decode('utf-8');nl='\r\n' if '\r\n' in text else '\n';text=text.replace('\r\n','\n')
a='        u32 lb = p_lower[pb + k], ub = p_upper[pb + k];'
b='''        u32 bounds1 = p_lower[pb + k], bounds2 = p_upper[pb + k];
        u32 lb = bounds1 & 2047u, ub = bounds2 & 2047u;'''
assert text.count(a)==1;text=text.replace(a,b)
a='''            for (u32 t = c0; t < c1; t++) {
                u32 pos = card_pos_sh[t - card_base];
                float r = reach_sh[pos];
                tot_c += r;
                if (pos < lb) lower_c += r;
                else if (pos >= ub) higher_c += r;
            }'''
b='''            u32 packed = x == 0 ? bounds1 : bounds2;
            u32 lower_end = c0 + ((packed >> 11) & 63u);
            u32 upper_end = c0 + ((packed >> 17) & 63u);
            for (u32 t = c0; t < lower_end; t++) {
                float r = reach_sh[card_pos_sh[t - card_base]];
                tot_c += r;
                lower_c += r;
            }
            for (u32 t = lower_end; t < upper_end; t++) {
                float r = reach_sh[card_pos_sh[t - card_base]];
                tot_c += r;
            }
            for (u32 t = upper_end; t < c1; t++) {
                float r = reach_sh[card_pos_sh[t - card_base]];
                tot_c += r;
                higher_c += r;
            }'''
assert text.count(a)==1;text=text.replace(a,b)
(S/'baseline.cu').write_bytes(base);(S/'candidate.cu').write_bytes(text.replace('\n',nl).encode())
mod=(old.REPO/'crates/solver/src/gpu/mod.rs').read_bytes();m=mod.decode().replace('\r\n','\n')
a='        Ok(GpuSolver {';assert m.count(a)==1
m=m.replace(a,'        let (packed_lower, packed_upper) = pack_show_bounds(&plan);\n\n'+a)
for name in ['lower','upper']:
 a=f'd_riv_{name}: [up32(&plan.riv_{name}[0])?, up32(&plan.riv_{name}[1])?],';b=f'd_riv_{name}: [up32(&packed_{name}[0])?, up32(&packed_{name}[1])?],';assert m.count(a)==1;m=m.replace(a,b)
m+='\n'+helper
(S/'baseline-mod.rs').write_bytes(mod);(S/'candidate-mod.rs').write_bytes(m.replace('\n','\r\n' if b'\r\n' in mod else '\n').encode())
patch=''.join(difflib.unified_diff(base.decode().splitlines(keepends=True),(S/'candidate.cu').read_text().splitlines(keepends=True),fromfile='a/crates/solver/src/gpu/kernels.cu',tofile='b/crates/solver/src/gpu/kernels.cu'))
patch+=''.join(difflib.unified_diff(mod.decode().splitlines(keepends=True),(S/'candidate-mod.rs').read_text().splitlines(keepends=True),fromfile='a/crates/solver/src/gpu/mod.rs',tofile='b/crates/solver/src/gpu/mod.rs'))
(S/'candidate.patch').write_text(patch,encoding='utf-8',newline='\n')
history_paths=[old.REPO/'research/postflop-gpu-20261016/experiments.md']+sorted((ROOT/'runs').glob('E0[0-6][0-9]-source/source-review.json'))
terms=['pack_show_bounds','per-card cutoff','packed boundary','packed lower','precomputed card bound','three ordered segments']
hits=[]
for path in history_paths:
 for n,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
  if any(t in line.lower() for t in terms):hits.append({'path':str(path),'line':n,'text':line})
old.save(H/'history-audit.json',{'at':old.now(),'scope_sha256':{str(p):old.sha(p) for p in history_paths},'terms':terms,'hits':hits,'finding':'Bounded indexed-source/ledger search found no prior executed exact mechanism. E062closure mentions next idea only. Distinct from E031shared offset caching,E05216bit shared positions,E057prefix swizzle and all timed failures. Not an exhaustive semantic novelty proof.','source_not_activated':True})
old.save(S/'source-review.json',{'id':'E063','at':old.now(),'mechanism':'Once per constructor, compute two card-local lower/upper split counts for each own sorted hand. Pack first-card6+6bits above the existing11bit global lower, and second-card6+6bits above global upper. GPU uses three contiguous ordered loops, removing per-position strength comparisons. No source variants permitted.','source_scope':['crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/kernels.cu'],'layout':'Same two u32 GPU words per own sorted row, same lengths/ABI/launch/shared storage. Public CPU GpuPlan fields remain unmodified; constructor owns four temporary clone vectors.','range_proof':'Legal Spot::new enumerates unique NUM_COMBOS=1326 unordered two-card combos. Each card appears in at most51. Sorted opponent bounds<=1326 fit11bits; local counts<=51 fit6bits. Bits0..10,11..16,17..22 are disjoint. Board-valid river lists are subsets.','float_dependency_proof':'Card positions are appended in ascending sorted position. Three segments partition the same list. tot_c visits every reach in identical first-card then second-card order; lower_c visits exactly the original pos<lb subsequence; higher_c visits exactly the original pos>=ub subsequence. No extra floating add/sub, reassociation, prefix scan, final formula, barrier or quality change. Compiled raw GPU exactness still mandatory.','temporary_host_cost':'Clone payload exactly8*(sum_p riv_lower[p].len()) bytes; Vec capacity measured. Valid flop max1176 river slots with at most1081 sorted hands/player gives20340096bytes (<20MiB), freed on constructor return, no GPU persistent/capacity increase. CPU preparation/copies are inside complete-cycle timing; material/peak/lifetime checks required before adoption. Same pageable Vec upload lifetime as existing plan vectors; no added stream synchronization.','history_audit_sha256':old.sha(H/'history-audit.json'),'candidate_accepted':False,'limits':'Root source proof only; no GPU numerical/resource/performance result or universal speed/no-tradeoff claim.'})
owned={'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu'),'crates/solver/src/gpu/mod.rs':old.sha(S/'candidate-mod.rs')}
old.save(S/'manifest.json',{'id':'E063','at':old.now(),'candidate_owned_sha256':owned,'source_sha256':old.BASE|owned,'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir() if p.is_file()},'source_activated':False,'one_fixed_form':True})
probe=r'''use std::{collections::{BTreeMap,HashSet},fs,io::Write};
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
'''
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
execute=r'''import json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
OUT=HERE/'execution'
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=82*1024**3;assert not OUT.exists();OUT.mkdir()
 old.child(P['rustc_command'],OUT,'rustc',old.env(),180)
 rows=[]
 for case in P['cases']:
  old.child([str(HERE/'probe.exe'),str(case['id']),case['path']],OUT,'case-'+str(case['id']).zfill(2),old.env(),120)
  lines=(OUT/('case-'+str(case['id']).zfill(2)+'.stdout.log')).read_text(encoding='utf-8').splitlines();markers=[json.loads(x.split('D102_RESULT ',1)[1]) for x in lines if x.startswith('D102_RESULT ')];assert len(markers)==1;row=markers[0];assert row['case_id']==case['id'] and row['status']=='pass_exact_integer_selectors';rows.append(row)
 old.custody();report={'id':'D102-card-cutoffs','at':old.now(),'status':'pass_cpu_integer_selector_proof_only','protocol_sha256':sys.argv[1],'binary_sha256':old.sha(HERE/'probe.exe'),'cases':rows,'checks':sum(r['checks'] for r in rows),'rows':sum(r['rows'] for r in rows),'selected_card_positions':sum(r['selected_card_positions'] for r in rows),'exhaustive_field_values':sum(r['exhaustive_disjoint_field_values'] for r in rows),'maximum_extra_host_capacity_bytes':max(r['extra_host_capacity_bytes'] for r in rows),'extra_gpu_bytes':0,'source_activated':False,'gpu_executions':0,'performance_measured':False,'candidate_accepted':False,'all_children_terminal':True,'limits':'CPU logical selected-index order only; no float GPU/compiler/resource or speed qualification. Mirror struct contains the exact required field types, not a full GpuPlan. Candidate helper bytes exactly match the function staged in candidate-mod.rs; integrated compile/tests still mandatory. Retained D092only baseline words used; old action-order candidate not used.'};old.save(HERE/'report.json',report);print(json.dumps({k:v for k,v in report.items() if k!='cases'}),flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
prior=old.read(ROOT/'runs/D092-action-arity-order/report.json');cases=[{'id':c['id'],'path':c['raw_file'],'sha256':c['raw_sha256']} for c in prior['cases']];assert [c['id'] for c in cases]==list(range(12))
deps=ROOT/'build-e051-final-primary/release/deps';sj=next(deps.glob('libserde_json-*.rlib'))
command=['rustc','--edition=2021',str(H/'probe.rs'),'--crate-name','d102_probe','-C','opt-level=3','--extern','serde_json='+str(sj),'-L','dependency='+str(deps),'-o',str(H/'probe.exe')]
paths=[*H.iterdir(),*S.iterdir(),Path(__file__),ROOT/'runs/D092-action-arity-order/report.json',ROOT/'runs/D092-action-arity-order/field-schema.json',ROOT/'runs/D092-action-arity-order/accepted-plan.rs',ROOT/'runs/E062-closure/decision.json',old.REPO/'crates/solver/src/game.rs',old.REPO/'crates/solver/src/range.rs',old.REPO/'crates/solver/src/gpu/plan.rs',ROOT/'runs/accepted-E051/common_e051.py',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']+list(deps.glob('*.rlib'))
P={'id':'D102-card-cutoffs','at':old.now(),'status':'FROZEN_PRE_CPU_NATIVE','cases':cases,'rustc_command':command,'input_sha256':{str(p):old.sha(p) for p in paths if p.is_file()}|{c['path']:c['sha256'] for c in cases},'source_manifest_sha256':old.sha(S/'manifest.json'),'required_remaining_reserve_bytes':50*1024**3,'maximum_additional_disk_reservation_bytes':2*1024**3,'disk_free_bytes':shutil.disk_usage(ROOT).free,'admission_rule':'All12canonical isooff/on compact/full baseline metadata and independent rank/card-list/ordered selector checks exact; exhaustive field and endpoint controls pass; no GPU payload length increase, maximum temporary host clone capacity<=20MiB on these cases. Then current D094allocated-resource/ABI/other8entry and compiled-mechanism gate before raw GPU numerical tests. No source variants or retries of semantic failures. Current whole-cycle1%/fixture/fresh16/broad/material/holdout/cumulative requirements remain; CPU proof is no speed/acceptance claim.','source_not_activated':True,'gpu_executions':0,'performance_measured':False}
old.save(H/'protocol.json',P)
published={}
for folder in [H,S]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key='evidence/'+folder.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id']=='D102' for e in st['experiments']);st['experiments'].append({'id':'D102','at':old.now(),'kind':'diagnostic','title':'Per-card cutoff integer and packing proof','status':'running','correctness':'pending','stage':'Untimed CPU selector proof','reason':'Distinct one-time preprocessing mechanism for showdown correction comparisons. Exact original public plan meanings, selected reach order and GPU payload lengths required. No speed claim.','evidence':[{'label':'Frozen CPU proof protocol','url':'evidence/D102-card-cutoffs/protocol.json'},{'label':'Fixed proposed source','url':'evidence/E063-source/source-review.json'}]});st.update(updated_at=old.now(),state='running',active_experiment='D102',stage='CPU boundary-precomputation proof',activity='Verify all12baseline metadata cases, disjoint bit fields and each accumulator selected-index order before compiling any candidate GPU kernel.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'status':'frozen','protocol_sha256':old.sha(H/'protocol.json'),'candidate_cuda_sha256':old.sha(S/'candidate.cu'),'candidate_mod_sha256':old.sha(S/'candidate-mod.rs'),'native_executions':0}),flush=True)
