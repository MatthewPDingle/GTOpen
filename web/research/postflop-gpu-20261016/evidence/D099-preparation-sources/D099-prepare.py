"""Freeze exact CPU GpuPlan scratch-reuse controls and fixed component screening."""
import ast,difflib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
H=ROOT/'runs/D099-plan-posting-scratch';assert not H.exists();H.mkdir();prior=ROOT/'runs/D092-action-arity-order'
base=(old.REPO/'crates/solver/src/gpu/plan.rs').read_bytes();old.pin(old.REPO/'crates/solver/src/gpu/plan.rs',old.BASE['crates/solver/src/gpu/plan.rs'])
text=base.decode().replace('\r\n','\n');a=text.index('        for p in 0..2 {',text.index('let mut riv_max_cnt'));b=text.index('        // --- Per-node scalar arrays',a);body=text[a:b]
oldline='                let mut by_card: Vec<Vec<u32>> = vec![Vec::new(); 52];\n';assert body.count(oldline)==1
body=body.replace(oldline,'')
needle='        for p in 0..2 {\n            for &key in &slots {\n';assert body.count(needle)==1
body=body.replace(needle,'        for p in 0..2 {\n            let mut by_card: Vec<Vec<u32>> = vec![Vec::new(); 52];\n            for &key in &slots {\n                for positions in &mut by_card {\n                    positions.clear();\n                }\n')
candidate=(text[:a]+body+text[b:]).replace('\n','\r\n' if b'\r\n' in base else '\n').encode()
(H/'accepted-plan.rs').write_bytes(base);(H/'candidate-plan.rs').write_bytes(candidate)
(H/'candidate.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='accepted-E051/plan.rs',tofile='D099-prototype/plan.rs')),encoding='utf-8',newline='')
for n in ['game.rs','field-schema.json','fixture-0.json','fixture-1.json','fixture-2.json']:(H/n).write_bytes((prior/n).read_bytes())
assert (H/'game.rs').read_bytes()==(old.REPO/'crates/solver/src/game.rs').read_bytes()
source=(prior/'probe.rs').read_text(encoding='utf-8').replace('D092','D099')
source=source.replace('&b.action_nodes,true','&b.action_nodes,false')
needle='for candidate_first in [id%2==1,id%2!=1]';start=source.index(needle);end=source.index('let a=a.unwrap();let b=b.unwrap();',start)
assert start<end
benchmark=r'''let mut baseline_samples=Vec::new();let mut candidate_samples=Vec::new();
let orders=[false,true,false,true,false,true,false,true,false];
// Two complete warmup pairs, not scored. No hidden full-solve warm start.
for candidate_first in [false,true]{for arm in [candidate_first,!candidate_first]{if arm{let mut p=candidate::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}std::hint::black_box(&p);drop(p);}else{let mut p=accepted::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}std::hint::black_box(&p);drop(p);}}}
for (pair,&candidate_first) in orders.iter().enumerate(){
 for arm in [candidate_first,!candidate_first]{
  let t=Instant::now();
  if arm{let mut p=candidate::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}let ms=t.elapsed().as_secs_f64()*1000.0;std::hint::black_box(&p);candidate_samples.push(ms);if pair==8{b=Some(p);}else{drop(p);}}
  else{let mut p=accepted::GpuPlan::build(&spot,iso);if full{p.use_full_action_arenas(&spot);}let ms=t.elapsed().as_secs_f64()*1000.0;std::hint::black_box(&p);baseline_samples.push(ms);if pair==8{a=Some(p);}else{drop(p);}}
 }
}
fn median(x:&[f64])->f64{let mut v=x.to_vec();v.sort_by(f64::total_cmp);v[v.len()/2]}
ams=median(&baseline_samples);bms=median(&candidate_samples);
'''
source=source[:start]+benchmark+source[end:]
needle='let v=serde_json::json!('
audit=r'''// Separate untimed allocator-mechanism audit on the actual returned tables.
let mut mechanism=Vec::new();
for p in 0..2{
 let mut retained:Vec<Vec<u32>>=vec![Vec::new();52];let mut old_allocations=0usize;let mut reused_allocations=1usize;let mut old_peak=0usize;let mut reused_peak=0usize;let mut old_final_capacity=0usize;let mut visits=0usize;
 for slot in 0..a.num_slots{
  let mut original:Vec<Vec<u32>>=vec![Vec::new();52];old_allocations+=1;
  for v in &mut retained{v.clear();}
  let lo=a.riv_off[p][slot] as usize;let hi=lo+a.riv_cnt[p][slot] as usize;
  for (position,&hand) in a.riv_sorted_idx[p][lo..hi].iter().enumerate(){let h=&spot.hands[p][hand as usize];for card in [h.c1 as usize,h.c2 as usize]{if original[card].len()==original[card].capacity(){old_allocations+=1;}if retained[card].len()==retained[card].capacity(){reused_allocations+=1;}original[card].push(position as u32);retained[card].push(position as u32);visits+=1;}}
  for card in 0..52{let lo=a.riv_card_off[p][53*slot+card]as usize;let hi=a.riv_card_off[p][53*slot+card+1]as usize;assert_eq!(&original[card],&retained[card]);assert_eq!(&original[card][..],&a.riv_card_pos[p][lo..hi]);}
  let oc=original.capacity()*std::mem::size_of::<Vec<u32>>()+original.iter().map(|v|4*v.capacity()).sum::<usize>();let rc=retained.capacity()*std::mem::size_of::<Vec<u32>>()+retained.iter().map(|v|4*v.capacity()).sum::<usize>();old_peak=old_peak.max(oc);reused_peak=reused_peak.max(rc);old_final_capacity=oc;
 }
 mechanism.push(serde_json::json!({"player":p,"slots":a.num_slots,"membership_words":visits,"baseline_allocation_growth_events":old_allocations,"reused_allocation_growth_events":reused_allocations,"baseline_peak_temporary_requested_capacity_bytes":old_peak,"reused_peak_temporary_requested_capacity_bytes":reused_peak,"baseline_last_slot_temporary_requested_capacity_bytes":old_final_capacity,"all_card_posting_values_and_order_exact":true}));
}
'''
assert source.count(needle)==1;source=source.replace(needle,audit+needle)
needle='"baseline_plan_ms":ams,"candidate_plan_ms":bms,';assert source.count(needle)==1
source=source.replace(needle,needle+'"baseline_samples_ms":baseline_samples,"candidate_samples_ms":candidate_samples,"pair_orders":orders.iter().map(|&x|if x{"CB"}else{"BC"}).collect::<Vec<_>>(),"warmup_pairs":2,"measured_pairs":9,"posting_mechanism":mechanism,')
source=source.replace('"all_nonpermuted_fields_bitwise_equal":true','"all53fields_bitwise_equal":true')
assert 'action_nodes,false' in source and 'action_nodes,true' not in source
(H/'probe.rs').write_text(source,encoding='utf-8',newline='\n')
executor='''"""One compile and12CPU-only fresh processes, retain every fixed observation."""
import json,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify();B=H/'build';E=H/'execution';assert not B.exists() and not E.exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=82*1024**3;B.mkdir();E.mkdir()
 old.child(P['command'],B,'rustc',old.env(),600);verify();binary=old.sha(B/'probe.exe')
 old.save(B/'complete.json',{'at':old.now(),'binary_sha256':binary,'compiler_terminal':True,'native_executions':0,'production_source_activated':False})
 results=[]
 for case in P['cases']:
  verify();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=66*1024**3
  label=f'case-{case:02d}';old.pin(B/'probe.exe',binary)
  old.child([str(B/'probe.exe'),str(case),str(E/(label+'.bin'))],E,label,old.env(),180)
  verify();rows=[json.loads(x.split('D099 ',1)[1]) for x in (E/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines() if x.startswith('D099 ')];assert len(rows)==1;v=rows[0]
  assert v['id']==case and v['fields']==53 and v['all53fields_bitwise_equal'] and v['all_vec_capacities_equal'] and v['struct_size_equal']
  assert v['measured_pairs']==9 and v['warmup_pairs']==2 and len(v['baseline_samples_ms'])==len(v['candidate_samples_ms'])==9
  assert v['gpu_executions']==0 and v['full_cycle_performance_measured'] is False
  results.append(v);old.save(E/(label+'.result.json'),v)
  print(json.dumps({'case':case,'baseline_plan_ms':v['baseline_plan_ms'],'candidate_plan_ms':v['candidate_plan_ms'],'all53fields_exact':True}),flush=True)
 old.save(H/'native-report.json',{'at':old.now(),'id':P['id'],'status':'native_complete_pending_raw_root_replay','protocol_sha256':sys.argv[1],'binary_sha256':binary,'cases':results,'raw_sha256':{p.name:old.sha(p) for p in E.glob('*.bin')},'all_owned_children_terminal':True,'source_activated':False,'gpu_executions':0,'full_cycle_performance_measured':False,'optimization_accepted':False})
 verify();print('D099all12native cases terminal; raw root replay and fixed proxy gate pending.',flush=True)
'''
ast.parse(executor);(H/'execute.py').write_text(executor,encoding='utf-8',newline='\n')
P=old.read(prior/'protocol.json');cmd=[x.replace(str(prior),str(H)).replace('d092_probe','d099_probe') for x in P['command']]
deps={p:h for p,h in P['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']}
inputs=[*H.iterdir(),Path(__file__),old.REPO/'crates/solver/src/gpu/plan.rs',old.REPO/'crates/solver/src/game.rs',ROOT/'runs/E060-closure/next-source-scout.json',ROOT/'comparisons/E060-root-crosscheck/report.json',ROOT/'runs/accepted-E051/common_e051.py']
pinmap={str(p):old.sha(p) for p in inputs if p.is_file()}|deps
reference=old.read(ROOT/'comparisons/E060-root-crosscheck/report.json');reference_ms=sum(f['baseline_median_ms'] for f in reference['fixtures']);assert reference_ms==9802.7425
old.save(H/'protocol.json',{'id':H.name,'at':old.now(),'status':'FROZEN_PRE_COMPILE_AND_NATIVE','command':cmd,'cases':list(range(12)),'input_sha256':pinmap,'same_accepted_solver_rlib_and_mimalloc':True,'same53field_schema':True,'candidate_owned_off_tree_source_sha256':old.sha(H/'candidate-plan.rs'),'change':'Move by_card52temporary vectors from inside river-slot loop to per-player scope, clear each before next slot. Identical membership append and flatten order; all returned fields and capacities must be bitwise equal. No CUDA/host-launch/quality/cache/precision/order change.','fixed_sampling':'12fixed canonical3fixture x isooff/on x compact/full processes. Each2unscored warmup pairs plus9alternating BC/CB measured pairs. All retained. Timing is CPU-plan component only, not whole solve; no confidence or cold application inference. No extension, exclusions, variants or primary timing pooling.','screen_reference_ms':reference_ms,'screen_minimum_savings_ms':reference_ms*0.01,'screen_rule':'After complete raw53field/capacity equality, sum baseline-minus-prototype medians in canonical iso-on compact cases2/6/10. Advance only if savings >=1%of the frozen prior accepted full-cycle reference and none of these3component cases has a positive median slowdown with>=5/9slower pairs. This is a prospective research-admission proxy, not a complete-cycle speed measurement or mathematical bound. If it fails, close allocation-reuse hypothesis without integration or variants. If it passes, actual whole-cycle1%/fixture/fresh16/broad/material/holdout/cumulative gates still mandatory.','temporary_memory_rule':'Untimed replay counts actual Vec growth events/capacities with both source algorithms and requires exact card/position order vs actual plan tables. Returned persistent capacities exact. Temporary retained capacity is reported separately; no GPU capacity claim from CPU metadata.','no_source_activation':True,'gpu_executions':0,'full_cycle_performance_measured':False,'root_review_only':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(e['id']=='D099' for e in s['experiments'])
 s['experiments'].append({'id':'D099','at':old.now(),'kind':'diagnostic','title':'Measure stable river-posting scratch reuse','status':'running','correctness':'pending','stage':'Frozen12case CPU plan/source/allocator control','reason':'One off-tree temporary Vec reuse form; compare all53plan fields/capacities, fixed9pair component medians and actual posting allocation counts. No solve speed claim.','evidence':[]})
 s.update(updated_at=old.now(),state='running',active_experiment='D099',stage='D099 CPU plan allocation screen',activity='Previous turn made progress: D098captured driver code and E060rejected on measured river tradeoff. D099now tests a distinct exact metadata-preparation mechanism.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'off_tree_prototype_sha256':old.sha(H/'candidate-plan.rs'),'component_admission_reference_ms':reference_ms,'component_minimum_savings_ms':reference_ms*.01,'native_runs':0}),flush=True)
