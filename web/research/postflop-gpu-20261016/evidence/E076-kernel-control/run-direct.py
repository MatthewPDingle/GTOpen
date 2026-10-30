"""Own one GPU alias control and its separate complete raw replay."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
H=R/'runs/E076-kernel-control';P=old.read(H/'protocol.json');M=R/'runs/E076-direct-manager';old.custody();assert not (R/'gpu-run.lock').exists()and not M.exists();M.mkdir()
for p,h in P['input_sha256'].items():old.pin(p,h)
old.child([sys.executable,'-B',str(H/'execute.py'),old.sha(H/'protocol.json')],M,'direct',old.env(),900)
old.child([sys.executable,'-B',str(H/'audit.py')],M,'audit',old.env(),300)
qpath=R/'comparisons/E076-kernel-control-root-check/report.json';q=old.read(qpath)
assert q['status']=='pass_scoped_in_place_CFV_raw_equivalence'and q['cases']==819 and q['alias_cases']==138 and q['kernel_launches']==1638
assert(q['output_words_both_arms'],q['immutable_words_both_arms'],q['guard_words_both_arms'])==(12375858,5199114,10240828)
for label in ['direct','audit']:
 e=old.read(M/(label+'.exit.json'));assert e['returncode']==0 and e['error']is e['cleanup']is None
for p,h in q['raw_file_sha256'].items():old.pin(p,h)
old.custody();assert not (R/'gpu-run.lock').exists()
done={'id':'E076','at':old.now(),'status':'pass_scoped_full_in_place_CFV_raw_equivalence','cases':819,'alias_cases':138,'application_kernel_launches':1638,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'root_raw_report_sha256':old.sha(qpath),'raw_file_sha256':q['raw_file_sha256'],'logical_parent_and_full_regret_strategy_outputs_exact':True,'full_physical_images_and_actual_inputs_match_own_expected':True,'performance_measurements':0,'solver_executions':0,'source_activated':False,'candidate_accepted':False};old.save(H/'complete.json',done)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[];CPU=R/'runs/E076-plan-control'
for folder in [H,H/'execution',M,qpath.parent,CPU,CPU/'execution',CPU/'build']:
 for p in folder.iterdir():
  if not p.is_file()or p.suffix not in ['.json','.rs','.py','.ptx','.log']:continue
  if folder==CPU and p.name=='probe.rs':key=CPU.name+'/completed-probe.rs'
  elif folder in [H/'execution',CPU/'execution',CPU/'build']:key=folder.parent.name+'-'+folder.name+'/'+p.name
  else:key=folder.name+'/'+p.name
  pub.append(publish(p,key))
pub.append(publish(Path(__file__),H.name+'/run-direct.py'));old.save(M/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'all_owned_children_terminal':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E076');e.update(stage='Integrated solver builds next',correctness='12 full compiled layouts and819 raw GPU pairs pass',reason='All51 unchanged metadata fields/capacities/structs exact; compiled CFV maps match frozen lifetime model.819 GPU pairs include138 in-place cases. Logical outputs, full expected physical images, actual inputs and all guards pass. Full solver/state/material and performance gates remain.');e['evidence'].extend([{'label':'Compiled plan metadata result','url':'evidence/E076-plan-control/report.json'},{'label':'Complete raw in-place replay','url':'evidence/E076-kernel-control-root-check/report.json'},{'label':'Terminal direct-control receipt','url':'evidence/E076-kernel-control/complete.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E076',stage='Preparing the E076 complete-solve trial',activity='CFV row-sharing prototype passed all12 compiled metadata layouts and819 full GPU raw pairs. No CUDA source or schedule change. Fresh integrated builds and fixed complete-solve screen next; E051 accepted/live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E076 CFV lifetime-sharing controls'not in raw
entry=f'''

### E076 CFV lifetime-sharing controls

D122 admitted exactly one original-schedule Rust CFV allocator prototype. Source SHA {old.sha(R/'runs/E076-source/candidate-plan.rs')}. It shares only disjoint one-action parent/action-child pairs with child arity >=2, colors closed lifetimes in descending levels and node-id order, swaps root color to0, and assigns persistent terminal caches separately. CUDA, float operations, worklists, graph/level schedule, reach metadata, ABI, save and quality settings remain unchanged. Added temporary CPU flags/buckets/scans are not free and remain subject to full-cycle/material qualification.

The first CPU protocol {old.sha(CPU/'protocol.json')} was superseded before any compiler/native execution by {old.sha(CPU/'protocol-r2.json')}: standalone unit modules needed crate-root type/function reexports. Both original harness/protocol and explicit amendment are retained. Candidate layout/source/maps/cases/criteria did not change. One probe compiler, one unit compiler, one original/candidate invariant-test process and12 complete CPU metadata processes all exited0. Every compiled CFV map matches the separately frozen D122 model. All51 other fields, vector capacities and struct sizes are exact; each original plan matches retained accepted D092 data across all53 fields. Complete paired raw metadata retained onS. CPU report SHA {old.sha(CPU/'report.json')}. No component timings scored.

Frozen direct protocol {old.sha(H/'protocol.json')}: one Rust compiler, one819-pair/1638-launch numerical process, then one separate raw decoder. Identical accepted source/PTX in both arms; no CUDA/NVRTC/resource rerun.138 na1 cases use the candidate's sole-child/parent row alias, all other arities remain disjoint. Both players, DCFR/CFR+, own/locked/opponent paths, boundary hands/thread widths/countzero/excessgrid and finite/signedzero/subnormal/quietNaN/infinity/overflow profiles remain in the fixed corpus. Whole regret/strategy arrays and logical parent CFV outputs match. Every complete physical CFV image is compared with its own explicit expected layout; all actual immutable inputs and guards match their own seeds. Distinct physical layouts are not claimed byte-identical. All12,375,858 output words,5,199,114 actual immutable words and10,240,828 guards checked. Root decoder {q['checks']} checks; report SHA {old.sha(qpath)}. Finite declared corpus and root replay, not universal NaN/alias proof or external independent review.

All{len(pub)} published artifacts HTTP byte verified. Accepted162/main163/live/protected2PTX exact, source never activated and all owned children terminal0. No whole-solver, speed, actual host/GPU peak/capacity or adoption conclusion. Next: isolated integrated builds and original unit/fixed3-pair >=1% screen with strict fixture guard; only a pass advances to separately frozen fresh16/broad/state/F32/menu/save/resume/continuation/material/holdout/cumulative gates. No source/layout/placement variants or timing rescue after failure. E051 accepted/deployed cumulative12.4372274192% and last primary B240 unchanged; goal active.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: verify CFV row sharing against full metadata and GPU images','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps(done),flush=True)
