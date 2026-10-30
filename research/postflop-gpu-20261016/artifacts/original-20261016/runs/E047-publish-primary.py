"""Publish the entire fixed E047 screen; never adopt from this preliminary result."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
HERE=ROOT/'runs/E047-primary-plan-r2';P=old.read(HERE/'protocol.json');Q=old.read(ROOT/'comparisons/E047-three-pair-comparison/report.json');R=old.read(ROOT/'comparisons/E047-root-crosscheck/report.json');v=Q['performance'];passed=v['primary_timing_pass'];gain=v['observed_gain_pct']
assert Q['decision']==('advance_to_separately_frozen_confirmation' if passed else 'rejected') and R['status']==('pass_initial_timing_only' if passed else 'pass_rejected')
directories=[HERE,ROOT/'runs/E047-native-execution',ROOT/'runs/E047-native-execution-r2',ROOT/'comparisons/E047-three-pair-comparison',ROOT/'comparisons/E047-root-crosscheck']+[ROOT/'runs'/n for n in P['control_ids']+P['measurement_order']]
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
guard_names=[g['fixture_id'] for g in v['fixture_regression_guard'] if g['failed']]
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 status=old.read(ar.STATUS);e=next(x for x in status['experiments'] if x['id']=='E047');e.update(status='preparing' if passed else 'rejected',correctness='pass',stage='Initial timing passed; fresh16-pair confirmation required' if passed else 'Closed after fixed primary screen',baseline_full_cycle_ms=v['baseline_full_cycle_ms'],full_cycle_ms=v['candidate_full_cycle_ms'],observed_gain_pct=gain)
 if passed:reason=f'Initial{gain:.4f}% gain passes1%/fixture gates. Not accepted: fresh16pair, broader/holdout/cumulative and module/resource checks remain.'
 else:reason=f'Aggregate gain{gain:.4f}%'+(' below1%.' if gain<1 else ' clears1%.')+(' Strict fixture guards failed: '+', '.join(guard_names)+'.' if guard_names else ' No strict fixture guard failed.')+' No extra samples, arity sweep, confirmation or adoption.'
 e['reason']=reason+' Exact18 full results/138 checkpoints,84 ordinary tests and819 directGPU cases passed. E020 retained.'
 e['evidence'].extend([{'label':'E047 complete primary assessment','url':'evidence/E047-three-pair-comparison/report.json'},{'label':'E047 root arithmetic/raw check','url':'evidence/E047-root-crosscheck/report.json'}]);status.update(state='running',stage='Preparing E047 fixed confirmation' if passed else 'Next source investigation',activity='E047 initial screen passed; no new accepted gain yet.' if passed else 'E047 closed; accepted E020 retained. Further source investigation active.',updated_at=ar.now());ar.atomic_json(ar.STATUS,status)
guards='; '.join(f"{g['fixture_id']} median slowdown{g['median_slowdown_pct']:.10f}%,{g['slower_pairs']}/3 slower,failed={g['failed']}" for g in v['fixture_regression_guard'])
outcome='E047 advances only to a separately frozen fresh16-pair confirmation; broader/holdout/cumulative and resource gates remain. No adoption follows this initial screen.' if passed else 'E047 is rejected. No extra sample, arity/factor sweep, confirmation, broader/holdout/cumulative or adoption follows.'
text=f'''

## D077 one-action routing; E047 fixed primary outcome

D077 adds only na==1 routing to the byte-unchanged existing up_action_impl<1> helper inside the existing up_action entry. Current2/3/4/generic paths, all helper arithmetic, child order, ABI, host/plan/fields/stores/entries/launches/allocations stay unchanged. Unlike E005/E014, no list partition or separate specialized entry is added; unlike E042, the hand loop is not unrolled. A hash check of preserved CUDA and local all-ref history found no prior matching candidate. The old D001 census reports37926/523533 rainbow and23080/318562 two-tone action nodes with one action (about7.24%); river has none. These are historical structural counts, not latency shares or current projected savings.

CUDA candidate d9ca0a50173703d59318b40c79648bfc5a1a75bc64d79c051fe95e5ce8456f75 passed frozen no-launch resource protocol2925f5e1fa137bdf25f56b4408876276cb506f0508cbd312eaeffa638b8e5aed. Registers66/local64bytes/maxthreads896/theoretical64/128/256 residency14/7/3 stay identical; other8 PTX bodies and exact ABI are unchanged. Resource report6d5838edc17a498b23219e000e21dc31e62bcf7e33a74f57e0486e226bfe8177 and root checkdc84f120d08e21dc36aaaff24a9caf6d8387841fe3957382f432bc7a01470c06 qualify only this prerequisite, not speed or module/graph memory.

Direct control protocol6c4a8153675704a80f05e91f4221dd6a430498c1d36347f7a0e13f8ea386aa58 prospectively expanded the earlier corpus to819 cases/1638 launches, including138 changed-path cases and all original arbitrary-arity checks. Actor/lock/opponent paths, DCFR/CFR+, hand/block tails, signedzero, quiet nonfinite payloads, overflow, subnormal, countzero and permuted children are covered. Native per-case comparisons passed once, but its final marker mistakenly retained717/1434 constants, causing the wrapper assertion to fail. The original source, raw marker and failed reporting record remain preserved. Assessment-only correction derives the totals from819 actual markers, the fixed loop/source and full raw files; it reruns no native test. Root decoder0264515e2e0f511ebe3f63320f5dad098132a878d7c854ffd3103bd07ae245de passed56527 checks, comparing all12,375,858 output words,5,199,114 actual immutable-input words and10,240,828 nonowned/guard words across both arms, with all five complete raw files retained. Physical offset spans above2^32 are outside this finite corpus. Root checks are not external independent audits.

Final production source manifest92c91331b94c02cf764c58d10a6318ce01ba156afa70e0a51db4f7be8aeabd32 and build protocol548ef2a5d7acfdb7cf19aa842c984b9c15bec1600454b5ef13f900e34d364021 produced separate fresh feature and GPU-only artifacts. Both compiler phases terminated with accepted162 restored. The first primary caller retained V042-unit in two literals despite planning V047-unit. The ar evidence guard refused that existing ID before any new native test/benchmark launched. That failed invocation and original script/protocol are preserved, and original V042 report/stdout hashes remained exact. R2 reads the sole validation ID from protocol data and uses a fresh output directory, with source/binaries and still-unused six measurement IDs unchanged. Primary R2 protocol {old.sha(HERE/'protocol.json')} froze V047-unit and exactly B140/E047R1,E047R2/B141,B142/E047R3.84ordinary tests passed/4ignored. Every18 full non-timing payload and138 convergence checkpoint matches E020C1. Sum of fixture medians {v['baseline_full_cycle_ms']:.10f} to {v['candidate_full_cycle_ms']:.10f}ms gives {gain:.10f}% observed gain. Strict guards: {guards}. {outcome}

Assessment {old.sha(ROOT/'comparisons/E047-three-pair-comparison/report.json')} and root retained-record/fSum recomputation {old.sha(ROOT/'comparisons/E047-root-crosscheck/report.json')} preserve the outcome. All samples stay included with no historical timing pooling or statistical-confidence claim. Raw controls, prospective protocols/build provenance and final reports are published and HTTP byte-verified. Accepted E020 remains at its previously qualified10.3798454492% cumulative gain; last actual primary baselineB142. Accepted162/main/HEAD/live/protected PTX stay exact. The goal remains active.
'''
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'## D077 one-action routing; E047 fixed primary outcome' not in raw;nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+text.encode('utf-8').replace(b'\n',nl))
print(json.dumps({'decision':Q['decision'],'gain_pct':gain,'publication_sha256':old.sha(HERE/'primary-publication.json'),'published_files':len(published)}),flush=True)
