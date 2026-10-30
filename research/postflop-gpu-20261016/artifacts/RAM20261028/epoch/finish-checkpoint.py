import sys,json,shutil,subprocess,urllib.request,statistics
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import common as h
h.custody();assert not(h.ROOT/'gpu-run.lock').exists()and not(h.ROOT/'epoch-sequence.lock').exists()
P=h.read(h.EPOCH/'baseline-protocol.json');O=h.ROOT/'runs/RAM20261028-execution';D=h.ROOT/'comparisons/RAM20261028-baseline'
q=h.read(D/'report.json');assert q['status']=='pass_current_hardware_baseline'
transition=h.read(h.EPOCH/'post-measurement-ui-transition.json')
for p,digest in P['input_sha256'].items():
 if p==transition['original_UI_path']:h.pin(transition['preserved_exact_measurement_UI'],digest)
 else:h.pin(p,digest)
receipts={}
for item in P['sequence']:
 ident=item['id'];path=O/(ident+'.exit.json');x=h.read(path)
 assert x['returncode']==0 and x['error']is x['cleanup']is None
 receipts[ident]={'sha256':h.sha(path),'returncode':0}
 if not item['unit']:assert h.exact(ident)==h.read(h.EPOCH/'exact-anchor.json')
assert h.read(O/'assessment.exit.json')['returncode']==1
assert h.read(D/'publication-repair.json')['new_native_processes']==0
assert q['aggregate_ms']==sum(f['median_full_cycle_ms']for f in q['fixtures'])==10456.4109
for f in q['fixtures']:assert statistics.median(f['raw_full_cycle_ms'])==f['median_full_cycle_ms']
local=h.read(h.ROOT/'reference/localization.json')
for f in local['copies']:h.pin(f['local'],f['sha256'])
snap=h.ar.live_status();h.ar.refuse_active(snap)
state=h.read(h.ar.STATUS);assert state['current_hardware_baseline']['aggregate_ms']==q['aggregate_ms']
assert state['measurement_epoch']['id']=='RAM20261028'and state['research_storage']['physical_drive']=='X:'
assert state['deployment']['candidate_id']=='E080'
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as z:assert z.read()==h.ar.STATUS.read_bytes()
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/',timeout=20)as z:assert z.read()==(h.ar.DASHBOARD/'index.html').read_bytes()
proof=h.ROOT/'output/playwright/ram-baseline-desktop.png';assert proof.is_file()
H=h.ROOT/'runs/RAM20261028-checkpoint';H.mkdir(exist_ok=False)
h.save(H/'report.json',{'at':h.now(),'status':'pass_checkpoint','goal_status':'active','previous_goal_turn':'progress: E089 compiled/raw/full-solve trial completed and rejected below 1%','this_turn':'progress: restored verified server after reboot; completed D141 integer model and prepared E090; followed new user RAM/storage instruction with a separate fresh E080 baseline on X and verified the updated tracker','measurement_epoch':'RAM20261028','best_accepted_configuration':'E080, GPU, compressed, Rayon16','fresh_baseline_ms':q['aggregate_ms'],'native_unit_tests_passed':86,'native_unit_tests_ignored':4,'scored_processes':5,'prespecified_warmup_processes':1,'scored_exact_full_results':15,'scored_exact_checkpoints':115,'all_six_complete_processes_exact_results':18,'all_six_complete_processes_exact_checkpoints':138,'all_seven_native_children_terminal':True,'native_receipts':receipts,'original_assessment_publication_failure_preserved':True,'reader_only_repair_did_not_rerun_measurements':True,'measurement_UI_preserved_at_original_hash':transition['preserved_exact_measurement_UI'],'tracker_current_HTTP_bytes_exact':True,'tracker_browser_check':'Fresh baseline and per-fixture values rendered correctly; earlier14.74% gain and graph explicitly labeled previous RAM. Console0errors0warnings; owned browser closed.','tracker_screenshot':str(proof),'tracker_screenshot_sha256':h.sha(proof),'source_main_live_PTX_custody_pass':True,'new_output_root':str(h.ROOT),'output_root_free_bytes':shutil.disk_usage(h.ROOT).free,'historical_archive_preserved_read_only':str(Path(r'S:\GTOpen-research\postflop-gpu-20261016')),'next_trial':'E090, exact two host stride statements, checksum-verified references and dependencies on X','next_trial_GPU_validation_run':False,'new_optimizer_gain_claimed':False,'RAM_causal_speedup_claimed':False,'live_server_intended_to_remain_running':state['deployment']['live_pid'],'live_status':snap})
pub=[]
for p in [H/'report.json',D/'publication-repair.json',h.EPOCH/'post-measurement-ui-transition.json',h.EPOCH/'chart-completeness-transition.json',h.EPOCH/'finish-baseline-publication.py',h.EPOCH/'update-dashboard.py',h.EPOCH/'localize-next-trial.py']:
 key='RAM20261028-baseline/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes()
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### RAM20261028 fresh baseline on X'not in raw
entry=f"""

### D141 CFV row-width model and E090 source preparation

Previous turn completed E089 and rejected 0.4581100427% complete-cycle gain below the current 1% gate. New scoped history rejected chance child-to-slot translation as overlapping E018/E039. D141 found no per-traverser unpadded CFV stride in 223 retained GpuSolver sources or local all-ref history. This differs from E025 row padding/allocation and E076 lifetime coloring/slot sharing: all CFV row IDs and allocation formulas remain unchanged.

Frozen D141 CPU/source/integer analysis decoded 12 accepted D092 layouts. All 124239154 producer/dependency/permutation/row-interval checks passed. Full up passes write every row without depending on incoming CFV bytes; BR/average retained terminals keep the same producer identities. Two traverser widths preserve injective row/hand addressing within the original larger allocation and root slot zero. Full writer maps were retained. This is finite integer/source evidence, not real GPU accuracy, bandwidth, footprint or speed. The narrower address envelope does not save allocated bytes.

E090 is exactly two existing local assignments in paired_sweep and eval_up: pass nh_p as the CFV row stride. Source SHA 92893002e72295c10ac8a899199a8046620daca37017aa4a75a80e988dd9339a. Kernel bytes, floating expressions/order, counts, slots, schedule, allocations/admission, root staging and save paths remain. No source activation, GPU controller or performance trial ran. After the user's new storage instruction, 90 source/proof/dependency artifacts totaling111234371bytes were copied and checksum verified on X with explicit original-to-local bindings; originals remain preserved.

### RAM20261028 fresh baseline on X

User reports T drive trouble, projects now on X, and changed RAM timings; requests a fresh best-configuration baseline and continued optimization. Current repos are physical X, older scientific archive physical S. All new outputs now use X:\\Dev\\GTOpen-research\\postflop-gpu-20261028. Frozen archive remains read-only; no new T dependency. Current source and deployed E080 binary match accepted hashes. The October28 Windows reboot had stopped the app; exact E080 was restarted hidden on43735,PID26528, with unchanged2214saved-file inventory and exact served root/preflopJS. Earlier October19 recovery and its pre-start Get-FileHash/.NET reader repair remain retained.

New hardware inventory: Ryzen5950X,128GiB, fourDIMMs reporting2933configured speed, sameRTX5090UUID and610.88driver. Exact active latency timings are not exposed by standard Windows inventory, so no inference from the DIMM part number. New RAM epoch does not pool earlier timing samples or attribute differences solely to RAM.

Frozen new baseline protocol {h.sha(h.EPOCH/'baseline-protocol.json')}: exact accepted E080 binaries copied and checksum verified on X;86ordinary units pass,4ignored. One prespecified unscored complete warm-up then exactly five scored fresh processes RAM20261028-B01..B05, GPU/compressed/Rayon16, unchanged evaluator/quality/stops. All15scored full non-timing records and115checkpoints match unchanged E020C1. Including warm-up,18records/138checkpoints exact. No scored exclusions, extension or native rerun. Aggregate is sum of five-observation fixture medians: rainbow6126.5299ms,two-tone4209.3584ms,river120.5226ms,total10456.4109ms. Raw suite sums {json.dumps(q['raw_serialized_suite_ms'])}. Native serial suite median and aggregate statistic remain separate.

All seven native processes returned0. The first assessment wrote the correct immutable report then stopped on an already-published hardware evidence filename. Original exit1/trace retained. Reader/publication-only repair verified identical bytes and reused the existing artifact; no sample or score changed. Baseline report SHA {h.sha(D/'report.json')}. The pre-measurement dashboard bytes were preserved at the protocol hash before presentation changes. Browser verification shows fresh10.46sbaseline, current per-fixture values, and prior14.74%/progress clearly labeled earlier RAM. Latest E080 historical graph point is now shown. Console0errors/warnings; owned browser closed. Screenshot {proof}.

Source/main/live/protected PTX custody passes. Existing E080 remains accepted/live; no optimizer was adopted, no new optimizer or causal RAM gain claimed, no push or source activation. All new artifacts and future trial references are on X. E090 GPU controls, original complete-cycle1%/strictfixture/fresh16/broad/material/capacity/holdout/new-epoch cumulative qualification remain. Goal active.
"""
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: rebaseline accepted GPU solver after RAM change on X','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
h.custody();h.save(H/'publication.json',{'at':h.now(),'HTTP_verified_artifacts':pub,'goal_active':True,'all_research_native_processes_terminal':True,'intended_app_server_remains_live':True})
print(json.dumps({'status':'pass_checkpoint','baseline_ms':q['aggregate_ms'],'scored_runs':5,'tests_passed':86,'output_root':str(h.ROOT),'goal':'active'}),flush=True)
