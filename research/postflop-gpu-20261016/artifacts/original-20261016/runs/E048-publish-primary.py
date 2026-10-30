"""Publish the complete fixed E048 cohort and decision, without adopting a preliminary pass."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
HERE=ROOT/'runs/E048-primary-plan';P=old.read(HERE/'protocol.json');Q=old.read(ROOT/'comparisons/E048-three-pair-comparison/report.json');R=old.read(ROOT/'comparisons/E048-root-crosscheck/report.json');v=Q['performance'];passed=v['primary_timing_pass'];gain=v['observed_gain_pct']
assert Q['decision']==('advance_to_separately_frozen_confirmation' if passed else 'rejected') and R['status']==('pass_initial_timing_only' if passed else 'pass_rejected')
T=old.read(ROOT/'runs/E048-native-execution/terminal.json');assert T['returncode']==0 and T['complete_sha256']==old.sha(ROOT/'runs/E048-native-execution/complete.json')
directories=[HERE,ROOT/'runs/E048-native-execution',ROOT/'comparisons/E048-three-pair-comparison',ROOT/'comparisons/E048-root-crosscheck']+[ROOT/'runs'/n for n in P['control_ids']+P['measurement_order']]
published={}
for directory in directories:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(HERE/'primary-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'decision':Q['decision'],'candidate_accepted':False})
failed_guards=[g['fixture_id'] for g in v['fixture_regression_guard'] if g['failed']]
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);e=next(x for x in s['experiments'] if x['id']=='E048');e.update(status='preparing' if passed else 'rejected',correctness='pass',stage='Initial timing passed; fresh16pair confirmation required' if passed else 'Closed after fixed primary screen',baseline_full_cycle_ms=v['baseline_full_cycle_ms'],full_cycle_ms=v['candidate_full_cycle_ms'],observed_gain_pct=gain)
 reason=(f'Initial{gain:.4f}% gain passes1%/fixture gates; fresh16pair/broader/holdout/cumulative/actual-capacity-resource qualification required before adoption.' if passed else f'Aggregate gain{gain:.4f}%'+(' below1%.' if gain<1 else ' clears1%.')+(' Strict fixture guards failed: '+', '.join(failed_guards)+'.' if failed_guards else ' No strict fixture guard failed.')+' No extra samples, partial-kernel/packing/factor rescue, confirmation or adoption.')
 e['reason']=reason+' Exact18 full results/138 checkpoints,84 ordinary tests and425 directGPU cases passed. E020 retained.'
 e['evidence'].extend([{'label':'E048 complete primary assessment','url':'evidence/E048-three-pair-comparison/report.json'},{'label':'E048 root raw arithmetic check','url':'evidence/E048-root-crosscheck/report.json'}]);s.update(state='running',stage='Preparing E048 fixed confirmation' if passed else 'Next source investigation',activity='E048 initial screen passes; no new accepted gain yet.' if passed else 'E048 closed; accepted E020 retained. Research continues.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
guard_text='; '.join(f"{g['fixture_id']} median slowdown{g['median_slowdown_pct']:.10f}%,{g['slower_pairs']}/3 slower,failed={g['failed']}" for g in v['fixture_regression_guard'])
outcome='The initial screen advances only to a separately frozen fresh16-pair confirmation; broader/F32/continuation/capacity/holdout/fresh-original cumulative and material-cost gates remain. E048 is not adopted.' if passed else 'E048 is rejected. No extra sample, partial-kernel/packing/factor rescue, confirmation, broader/holdout/cumulative work or adoption follows.'
text=f'''

## E048 canonical chance card comparisons - fixed primary outcome

D078 caller review decoded the entire140608-record CPU algebra file and verified the canonical hand factory and supported saved-session reconstruction. E048 changes down_chance/up_chance membership tests to compare against existing u32 card IDs; masks remain public CPU-plan fields. Manually inconsistent custom Rust HandInfo values are outside the supported canonical-input claim. The frozen no-launch resource protocolce727172eb9bb1f0ebb4df756a72c976bb35629d98560eec176fda1a5d417cc7 passed: down registers30 to28, up30unchanged, local/static/dynamic sharedzero, maxthreads1024 and theoretical64/128/256 occupancy24/12/6 unchanged. Changed ABI types/indices/qualifiers and other7 PTX entries are exact. Resource report11d2a50b1f77834360ccea390764c9911cc56e917dbf9023c95804d726419197 and root checkeb1dcffd68b7d864847f0f78b0ec3efc56e476fb48608a0278cddc7e8cc43fa1 qualify only that prerequisite.

Control protocolc5dfcb338ad3f3de5e78c1f1a04c12e1c241e8e4d334073c709b236d7b96352e froze425 cases/850 launches across both kernels, with157 down/268up cases. Every canonical1326-hand/dealt-card relation is checked individually, with both-player asymmetry, zero counts/empty lists, tails, permutations, signedzero/subnormal/quietNaN/infinity and finite-overflow stress. Source inputs, full outputs and actual immutable-device images are retained in3 raw files. Native comparison passed once with dynamic loop-derived summary counts. Root decoder18e7b82e00e855d345d733f47695e5f918588f6d03bbf4196da8f636d5268dd7 passed2508695 checks, comparing18950844 full output words,3951272 actual immutable words and13112256 guard/unowned words across both arms, plus1840420 independent finite down zero/copy relations. These finite small-offset canonical controls are not universal floating/malformed-input proof, and root review is not external independent review.

Final source manifestcb0345a95ef6420b55eaf483eba9782afdf54db32509062fc9c87295179b58a2 freezes3 files: kernels.cu changes both predicates/interfaces, mod.rs updates all4production callers plus1full-down unit reference and removes2private device mask buffers/uploads, continuation_capacity.rs removes the matching expected/observed GPU payload. No public plan fields, capacity-vector indices, floating/reduction order, discounts/accuracy/cadence/readback, launch shape or additional allocation changes. Declared device payload falls8*(nh0+nh1)bytes; actual constructor/module/capacity/lifetime costs still require qualification before adoption. Build protocol98c714d9a32d4440ac206c955014124888695328a9b02e25d76dd3d6df336c63 completed fresh feature/primary artifacts, terminal session50152, restoring accepted162 after each phase.

Primary protocol {old.sha(HERE/'protocol.json')} froze protocol-owned V048-unit and exactly B143/E048R1,E048R2/B144,B145/E048R3. Native session35746 completed once.84 ordinary tests passed/4ignored; all18 complete non-timing payloads and138 convergence checkpoints match E020C1. Sum of per-fixture medians {v['baseline_full_cycle_ms']:.10f} to {v['candidate_full_cycle_ms']:.10f}ms gives {gain:.10f}% observed gain. Strict guards: {guard_text}. {outcome}

Primary assessment {old.sha(ROOT/'comparisons/E048-three-pair-comparison/report.json')} and root raw arithmetic replay {old.sha(ROOT/'comparisons/E048-root-crosscheck/report.json')} preserve the decision. All observations remain included, without historical timing pooling, exclusions, extensions or statistical-confidence claims. Controls, source/build/prospective timing evidence and final reports are served and HTTP byte-verified. Accepted E020 remains at its previously qualified10.3798454492% cumulative suite gain; last actual primary baselineB145. Accepted162/main/HEAD/live/protected PTX remain exact. The research goal remains active.
'''
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'## E048 canonical chance card comparisons - fixed primary outcome' not in raw;nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+text.encode('utf-8').replace(b'\n',nl))
print(json.dumps({'decision':Q['decision'],'gain_pct':gain,'publication_sha256':old.sha(HERE/'primary-publication.json'),'published_files':len(published)}),flush=True)
