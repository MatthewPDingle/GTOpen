import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists()and not(ROOT/'epoch-sequence.lock').exists()
H=ROOT/'runs/E090-primary-plan';P=h.read(H/'protocol.json');qp=ROOT/'comparisons/E090-three-pair-comparison/report.json';rp=ROOT/'comparisons/E090-root-crosscheck/report.json';q=h.read(qp);r=h.read(rp);perf=q['performance'];passed=perf['primary_timing_pass']
assert r['aggregate_gain_pct']==perf['observed_gain_pct']and r['status']==('pass_initial_timing_only'if passed else'pass_rejected')
assert h.read(ROOT/'runs/E090-primary-execution/complete.json')['all_owned_children_terminal']
for p,digest in P['input_sha256'].items():h.pin(p,digest)
O=ROOT/'runs/E090-initial-decision';O.mkdir(exist_ok=False)
reason=f"The fixed complete-solve screen with the current RAM settings measured {perf['observed_gain_pct']:.6f}% aggregate improvement. All 18 scientific results, 138 convergence checkpoints, 86 ordinary units and the raw engine controls (32 cases, 288 snapshots) passed. "
if passed:reason+='The initial speed gate passed; separate confirmation with 16 fresh pairs, broader correctness and resource checks, holdout and cumulative qualification remain. Not adopted.'
else:
 failures=[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']];why=[]
 if perf['observed_gain_pct']<1:why.append('below the unrounded1% cutoff')
 if failures:why.append('repeatable slowdown: '+', '.join(failures))
 reason+='Rejected: '+'; '.join(why)+'. The exact per-player scratch-stride form is closed; no width/alignment/fixture/source variant or extra-sample rescue.'
h.save(O/'decision.json',{'id':'E090','at':h.now(),'measurement_epoch':'RAM20261028','decision':q['decision'],'performance':perf,'all18_scientific_records_and138_checkpoints_exact':True,'ordinary_units_passed':86,'ordinary_units_ignored':4,'raw_GPU_control_cases':32,'raw_GPU_snapshot_pairs':288,'assessment_sha256':h.sha(qp),'root_replay_sha256':h.sha(rp),'primary_raw_arena_bytes_independently_compared':False,'primary_whole_arena_fingerprints_exact':True,'source_adopted':False,'live_source':'E080','historical_or_RAM_baseline_samples_scored':0,'excluded_samples':[],'extension_runs':0,'reason':reason})
pub=[]
for folder,prefix in[(H,H.name),(ROOT/'runs/E090-primary-execution','E090-primary-execution'),(qp.parent,qp.parent.name),(rp.parent,rp.parent.name),(O,O.name)]:
 for p in folder.rglob('*'):
  if not p.is_file()or p.suffix not in['.json','.py','.rs','.log']:continue
  key=prefix+'/'+p.relative_to(folder).as_posix();dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E090');x.update(status='measured'if passed else'rejected',accepted=False,correctness='pass_scoped',measurement_epoch='RAM20261028',stage='Initial pass; separate confirmation pending'if passed else'Closed: speed gate failed',reason=reason,baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],full_cycle_ms=perf['candidate_full_cycle_ms'],observed_gain_pct=perf['observed_gain_pct'],updated_at=h.now())
 x.setdefault('evidence',[]).extend([{'label':'Current RAM speed comparison','url':'evidence/E090-three-pair-comparison/report.json'},{'label':'Independent complete-log replay','url':'evidence/E090-root-crosscheck/report.json'},{'label':'Initial decision','url':'evidence/E090-initial-decision/decision.json'}])
 s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E090'if passed else None,stage='Prepare E090 separate confirmation'if passed else'Investigating the next independent performance mechanism',activity=reason+' The accepted E080 baseline with the current RAM settings remains 10.4564 s. The earlier 14.74% cumulative gain belongs to the previous RAM settings.');h.ar.atomic_json(h.ar.STATUS,s)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20)as z:served=json.load(z)
assert served['current_hardware_baseline']['aggregate_ms']==10456.4109 and served['measurement_epoch']['id']=='RAM20261028'
h.save(O/'publication.json',{'at':h.now(),'HTTP_verified_artifacts':pub,'served_epoch_baseline_verified':True,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'all_new_bulk_physical_X_only':True,'candidate_adopted':False})
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E090 current-RAM per-player CFV stride'not in raw
entry=f"""

### E090 current-RAM per-player CFV stride

Current hardware epoch RAM20261028 follows the user's RAM/storage changes. New outputs, builds and complete raw observations reside on X. Archived inputs were copied/hash-bound without modifying their source. Prior RAM timings, including the fresh five-run E080 epoch baseline, are not pooled into this candidate comparison.

The exact staged E090 source (mod.rs SHA 92893002e72295c10ac8a899199a8046620daca37017aa4a75a80e988dd9339a) changes only two CFV stride values in paired_sweep/eval_up from max hand count to current traverser hand count. Arithmetic, kernels, precision, row IDs, ordering, graph schedule, allocations, budget/root extraction, learning/reach and persistence remain unchanged. No allocation or VRAM saving claim. D141's retained finite row-writer/address proof preceded real GPU controls.

Frozen engine protocol {h.sha(ROOT/'runs/E090-engine-control/protocol.json')}: one compiler, one GPU process and independent retained-raw reader all terminal0. 32 fixed cases cover both storage formats/algorithms, both asymmetric range orders, symmetry off/on and cold versus CPU-warm/raked starts (rake tied to warm flag, not an independent cross). All288 GPU snapshot pairs,32 full66-buffer constructor pairs,128 exploitability comparisons,320 standard iterations and128 extra isolated-player sweeps pass. Reader610370 checks cover187104160 represented words,23978400 logical CFV words and55904 physical guards. Full physical CFV layouts are retained and logically mapped, not claimed byte-identical. Query, locks/graph recapture, full CPU state, save/load/resume files match. Finite controls only; no universal address proof or physical peak claim.

Two fresh feature/primary Cargo builds on X finished successfully, restoring accepted E080 after each. Primary protocol {h.sha(H/'protocol.json')} froze V090-unit (86 passed,4 ignored) followed by B293/E090R1,E090R2/B294,B295/E090R3. All18 non-timing result records/full arena fingerprints and138 checkpoints match original E020C1; primary raw arena bytes were not independently compared. Complete cycles include tree/CPUallocation,all GPUinit/NVRTC/JIT,samequality solve/checks/fullreadback; compilation/fingerprints excluded. No extra/excluded/historical/epoch-baseline samples. Sum fixture medians {perf['baseline_full_cycle_ms']} to {perf['candidate_full_cycle_ms']}ms; unrounded gain {perf['observed_gain_pct']}%. Strict fixture guards {json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}.

{reason}

Independent full-log replay passed{r['checks']} checks; assessment SHA {h.sha(qp)}. {len(pub)} small evidence artifacts HTTP byte-verified. All owned children terminal; locks absent; accepted/main/live/protected PTX custody passed. No adoption, live replacement or push. Current E080 RAM baseline10.4564109s remains distinct from prior-epoch14.7414188354% cumulative gain. Last primaryB295; goal active.
"""
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','-c','gc.auto=0','commit','--only','-m','research: measure per-player CFV stride on new RAM epoch','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True)
h.custody();print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'fixture_guards':perf['fixture_regression_guard'],'HTTP_artifacts':len(pub)}),flush=True)
