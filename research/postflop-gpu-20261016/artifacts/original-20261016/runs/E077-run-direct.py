"""Own one full raw selective-prefix numerical matrix and its independent replay."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
H=R/'runs/E077-kernel-control';M=R/'runs/E077-direct-manager';P=old.read(H/'protocol.json');old.custody();assert not(R/'gpu-run.lock').exists()and not M.exists();M.mkdir()
for p,h in P['input_sha256'].items():old.pin(p,h)
old.child([sys.executable,'-B',str(H/'execute.py'),old.sha(H/'protocol.json')],M,'direct',old.env(),1200)
old.child([sys.executable,'-B',str(H/'audit.py')],M,'audit',old.env(),300)
qpath=R/'comparisons/E077-kernel-control-root-check/report.json';q=old.read(qpath);assert q['status']=='pass_scoped_full_selective_prefix_raw_equivalence'and q['kernel_launches']==3640 and q['inventory']['comparison_pairs']==1820
assert q['inventory']['full_output_words_both_arms']==8436520 and q['inventory']['device_input_word_checks']==15329720 and q['inventory']['output_guard_word_checks']==6464120
for label in ['direct','audit']:
 e=old.read(M/(label+'.exit.json'));assert e['returncode']==0 and e['error']is e['cleanup']is None
old.custody();assert not(R/'gpu-run.lock').exists()
done={'id':'E077','at':old.now(),'status':'pass_scoped_full_selective_prefix_raw_equivalence','cases':1820,'application_kernel_launches':3640,'tested_block_widths':P['widths'],'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'root_raw_report_sha256':old.sha(qpath),'raw_sha256':q['raw_sha256'],'raw_bytes':q['raw_bytes'],'whole_physical_outputs_bitwise_equal':True,'all_actual_inputs_match_own_encoded_expected':True,'performance_measurements':0,'solver_executions':0,'source_activated':False,'candidate_accepted':False};old.save(H/'complete.json',done)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[];CPU=R/'runs/E077-plan-control'
for folder in [H,H/'execution',M,qpath.parent,CPU,CPU/'execution',CPU/'build',R/'runs/E077-host-manager',R/'runs/E077-host-manager-r2']:
 for p in folder.iterdir():
  if not p.is_file()or p.suffix not in ['.json','.rs','.py','.ptx','.log']:continue
  if folder in[H/'execution',CPU/'execution',CPU/'build']:key=folder.parent.name+'-'+folder.name+'/'+p.name
  else:key=folder.name+'/'+p.name
  pub.append(publish(p,key))
pub.append(publish(Path(__file__),H.name+'/run-direct.py'));old.save(M/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'all_owned_children_terminal':True})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E077');e.update(stage='Integrated solver builds next',correctness='12 full host maps and1820 full raw GPU pairs pass',reason='Compiled tags match frozen D124, all52 other fields/capacities/structs exact,3 plan tests pass.1820 pairs/3640 launches across1/32/64/128/256 threads: full CFV outputs, all actual input images and guards exact. No full-solver/material/performance result yet.');e['evidence'].extend([{'label':'Compiled full host-tag maps','url':'evidence/E077-plan-control/report.json'},{'label':'Complete raw GPU replay','url':'evidence/E077-kernel-control-root-check/report.json'},{'label':'Terminal raw control receipt','url':'evidence/E077-kernel-control/complete.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E077',stage='Preparing E077 integrated solver builds',activity='Selective prefix materialization passed12 exact compiled tag maps and1820 full raw GPU pairs across5 widths. Whole outputs and expected input/guard images match. No new speed gain accepted; E051 live gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E077 compiled host tags and full GPU raw controls'not in raw
entry=f'''

### E077 compiled host tags and full GPU raw controls

Prior goal turn completed D124 retained prefix-demand/index-tag model, E077 sole CUDA resource run and D125 read-only byte-offset semantic repair. Same frozen3-file source: CUDA5c815c688d3565a7f8405738273f2f4ba3d3625df8c47b5a52e9e9788223f03d, plan c941683287f3683be1d713ad4c1a954d47801439f9a2b51fa56de88d38c4e165, mod2753a4aa658022d879b5882312a0e2a89e4edb94ecaee603d185debee4686e12. No flag/mask/source/width/kernel changes after resource compilation. Shared/local/dynamic and actual occupancy unchanged, registers38to39 within same allocation quantum; no speed/material conclusion from that.

Host protocol {old.sha(CPU/'protocol.json')}: one probe compiler, one unit compiler, three tests and native case00 completed0. Python array(Q).extend(array(I)) failed in expected-map decoding before candidate raw data inspection. Original reader/error/protocol/receipts retained. R2 {old.sha(CPU/'protocol-r2.json')} changes only integer-container iteration, replays original case00 bytes and runs exactly pending01..11. No rebuild/test/case00 native repeat or sample extension. All12 actual compiled tag arrays match frozen D124 maps; every52 other field/value/capacity/struct equals accepted data and public build remains exact before tagging. Three native tests cover original plan invariants, exact required tags/hand IDs and idempotence. CPU report SHA {old.sha(CPU/'report.json')}; all complete raw metadata retained onS.

GPU protocol {old.sha(H/'protocol.json')} frozen before first numerical launch: same364 geometry/profile/count descriptors times fixed widths1/32/64/128/256 =1820 pairs/3640 launches. One compiler, one native process and one separate complete raw decoder, same resource PTX, zero NVRTC/resource reruns. Candidate p_idx/o_idx highbit flags computed from both-sided actual strength-boundary demand and total; low31 original physical IDs retained. Other19 actual input buffers identical. All8,436,520 complete physical CFV output words and15,329,720 actual immutable input words checked,6,464,120 guards exact. Original128-thread sparse rounding witness retained twice; extra widths compare their own original arithmetic order. Includes actual accepted7card rank validation, full/partial/empty/tails/countzero/excessgrid, finite/signedzero/subnormal/quietNaN/infinity/overflow profiles. Full raw JSONL {q['raw_bytes']} bytes, SHA {q['raw_sha256']}, retained physically onS. Root {q['checks']} checks, report SHA {old.sha(qpath)}. Finite corpus/root replay, not universal NaN/illegal-address proof or external independence.

All{len(pub)} code/protocol/report/log evidence files HTTP byte verified. All owned children terminal0 for successful controls, original host reader-error parent preserved separately; no production source activation, full solver or speed samples. Accepted162/main163/live/protected2PTX exact. Next fresh isolated feature/primary builds and original ordinary units/fixed3pair1% strict-fixture screen; only a pass advances fresh16/broad/F32/state/menu/save/resume/continuation/actual CPU/host+GPU peak/capacity/responsiveness/holdout/fresh-original cumulative gates. No source/helper/flag/map/mask/width/placement/sample rescue after an actual failure. E051 accepted/deployed12.4372274192%,last primary B243 unchanged; goal active.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: verify selective prefix tags and full GPU outputs','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps(done),flush=True)
