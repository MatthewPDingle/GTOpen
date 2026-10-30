import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists();h.ar.refuse_active(h.ar.live_status())
B=h.read(ROOT/'comparisons/RAM20261028-baseline/report.json');assert B['status']=='pass_current_hardware_baseline'and B['aggregate_ms']==10456.4109
E=h.read(ROOT/'runs/E090-initial-decision/decision.json');assert E['decision']=='rejected'and E['performance']['observed_gain_pct']==0.7765774427945334
D=h.read(ROOT/'comparisons/D142-profile/report.json');assert D['status']=='pass_finite_diagnostic'and D['full_results_exact']==3
S=ROOT/'runs/E091-source';m=h.read(S/'manifest.json');r=h.read(S/'source-review.json');assert r['GPU_or_compiler_children']==0 and not r['production_source_activated']and not r['numerical_equivalence_established']
for n,digest in m['candidate_owned_sha256'].items():h.pin(m['owned'][n]['candidate'],digest)
hist=h.read(ROOT/'runs/D143-zero-reach-source/history.json');assert hist['files_checked']==400 and hist['down_action_bodies_extracted']==399 and hist['files_without_down_action']==1 and not hist['matching_bodies']
O=ROOT/'runs/RAM20261028-research-checkpoint';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);changed=[]
 for x in s['current_hardware_baseline']['fixtures']:
  before=x['description'];x['description']=before.replace('\u00c2\u00b7','\u00b7')
  if before!=x['description']:changed.append({'field':x['id']+'.description','before':before,'after':x['description']})
 before=s['measurement_epoch']['label'];s['measurement_epoch']['label']=before.replace('\u00c2\u00b7','\u00b7')
 if before!=s['measurement_epoch']['label']:changed.append({'field':'measurement_epoch.label','before':before,'after':s['measurement_epoch']['label']})
 s['updated_at']=h.now();h.ar.atomic_json(h.ar.STATUS,s)
h.save(O/'presentation-correction.json',{'at':h.now(),'cosmetic_changes':changed,'scientific_values_or_gates_changed':False,'native_children_started':0})
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D142 and D143 current-RAM follow-up'not in raw
entry=f"""

### D142 and D143 current-RAM follow-up

E090 remains rejected without source or sample rescue. D142 frozen diagnostic protocol {h.sha(ROOT/'runs/D142-profile-plan/protocol-r2.json')} ran one accepted E080 process with the three unchanged full solves, then one extra synchronized training iteration per fixture. All3 scientific results/full arena fingerprints and23 checkpoints match E020C1. No source change, hardware counters or speed gain claim. The first protocol and executor had a Python parser typo (else201); the original and pre-native syntax repair remain retained and bound to the revised protocol. No native/compiler/sample had started before that repair.

Per-family wall times include synchronization overhead, omit normal captured-graph scheduling and do not measure device-only latency or evaluation-family cost. On rainbow/two-tone the up-action family measured8.7764/6.4606ms, down-action5.7047/3.0098ms and showdown7.5946/4.4014ms in one instrumented iteration. These finite observations guide review only, with no production time-share/headroom/statistical claim.

D143 checksum-checked400 cataloged retained CUDA files:399 down-action bodies extracted,1 explicitly absent. No matching per-hand zero-reach normalization shortcut found in that bounded text/all-local-ref/current-ledger review; no exhaustive semantic/remote novelty claim. Initial extractor assumed every up-show catalog entry contained down-action and failed before candidate staging. Original extractor and error/reader repair retained; no GPU/compiler was involved.

E091 staged source SHA {m['candidate_owned_sha256']['crates/solver/src/gpu/kernels.cu']}, exact reversal proven. It adds one unlocked per-hand signed-zero-own-reach shortcut after the unchanged ordered positive-regret sum. Finite sums permit signed-zero output in unchanged action/address order; nonfinite sums and all locked inputs keep the original path. No E035/E036 terminal CTA shortcut or E090 scratch hunk is composed. This source case analysis has not established CUDA equivalence, incidence, compiled resources, material costs or complete-solve speed. The implementation is staged outside the repository; accepted source/main/live/protected PTX remain unchanged. Next: finite raw CUDA controls including signed zeros, nonfinite/overflow sums, action counts/orientations/locks/tails/full guards, then production incidence and resource prerequisites. No native E091 work yet.

The live tracker retains current E080 baseline10.4564109s and separates the historical14.7414% prior-RAM gain. Cosmetic current fixture/epoch middle-dot encoding was corrected after measurements; no scientific value/input/gate changed. All new artifacts/builds/raw observations physically on X; archive read-only. All owned native/compiler/profile children terminal0; locks absent; source/main/live/PTX custody passed. No adoption, push or server replacement. Goal active, E091 pending.
"""
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','-c','gc.auto=0','commit','--only','-m','research: profile new RAM epoch and stage zero-reach review','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
h.custody()
report={'id':'RAM20261028-research-checkpoint','at':h.now(),'current_E080_baseline_ms':B['aggregate_ms'],'baseline_scored_processes':5,'baseline_scientific_results_exact':15,'baseline_checkpoints_exact':115,'E090_decision':'rejected','E090_gain_pct':E['performance']['observed_gain_pct'],'E090_fixture_guard_failure':'river','E090_full_results_exact':18,'E090_checkpoints_exact':138,'D142_status':D['status'],'E091_status':'staged_not_activated_no_GPU_controls_or_speed_result','E091_source_sha256':m['candidate_owned_sha256'],'research_git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=h.REPO,text=True).strip(),'source_main_live_PTX_custody_pass':True,'all_owned_native_and_compiler_children_terminal':True,'GPU_and_sequence_locks_absent':True,'all_new_artifacts_physical_X':True,'research_free_bytes':shutil.disk_usage(ROOT).free,'goal_status':'active','candidate_adopted':False,'pushed':False,'evidence_sha256':{str(p):h.sha(p)for p in[ROOT/'comparisons/RAM20261028-baseline/report.json',ROOT/'runs/E090-initial-decision/decision.json',ROOT/'comparisons/D142-profile/report.json',ROOT/'runs/D143-zero-reach-source/history.json',S/'source-review.json',S/'manifest.json']}}
h.save(O/'report.json',report)
key=O.name+'/report.json';dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(O/'report.json',dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==(O/'report.json').read_bytes()
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as z:served=json.load(z)
assert served['active_experiment']=='E091'and served['current_hardware_baseline']['aggregate_ms']==10456.4109 and served['measurement_epoch']['id']=='RAM20261028'
h.save(O/'publication.json',{'at':h.now(),'report_HTTP_bytes_exact':True,'served_epoch_baseline_and_next_candidate_verified':True,'no_extra_native_samples':True})
print(json.dumps({k:report[k]for k in['current_E080_baseline_ms','E090_decision','E090_gain_pct','E091_status','research_git_head','source_main_live_PTX_custody_pass']}),flush=True)
