"""Publish complete E045 primary evidence; acceptance remains conditional."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
HERE=ROOT/'runs/E045-primary-plan';P=old.read(HERE/'protocol.json');Q=old.read(ROOT/'comparisons/E045-three-pair-comparison/report.json');R=old.read(ROOT/'comparisons/E045-root-crosscheck-r2/report.json');v=Q['performance'];passed=v['primary_timing_pass']
assert Q['decision']==('advance_to_separately_frozen_confirmation' if passed else 'rejected')
assert R['status']==('pass_initial_timing_only' if passed else 'pass_rejected')
directories=[HERE,ROOT/'runs/E045-native-execution',ROOT/'comparisons/E045-three-pair-comparison',ROOT/'comparisons/E045-root-crosscheck',ROOT/'comparisons/E045-root-crosscheck-r2',ROOT/'comparisons/E045-integer-control-root']+[ROOT/'runs'/n for n in P['measurement_order']]
published={}
for directory in directories:
 for source in directory.rglob('*'):
  if not source.is_file() or '__pycache__' in source.parts:continue
  key=directory.name+'/'+source.relative_to(directory).as_posix();target=ar.DASHBOARD/'evidence'/key;target.parent.mkdir(parents=True,exist_ok=True);raw=source.read_bytes()
  if target.exists():assert target.read_bytes()==raw
  else:target.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(source)
old.save(HERE/'primary-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'decision':Q['decision'],'candidate_accepted':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 status=old.read(ar.STATUS);e=next(x for x in status['experiments'] if x['id']=='E045')
 e.update(status='preparing' if passed else 'rejected',correctness='pass',stage='Initial screen passed; fresh16-pair confirmation required' if passed else 'Closed after fixed primary screen',baseline_full_cycle_ms=v['baseline_full_cycle_ms'],full_cycle_ms=v['candidate_full_cycle_ms'],observed_gain_pct=v['observed_gain_pct'])
 if passed:e['reason']=f"Initial gain{v['observed_gain_pct']:.4f}% passes1%/fixture gates; not accepted. Exact18 results/138 checkpoints and86 ordinary tests passed. Fresh16-pair confirmation, broader/holdout/cumulative and CPU/resource/responsiveness checks remain required."
 else:e['reason']=f"Aggregate gain{v['observed_gain_pct']:.4f}% clears1%, but river median5.7183% slower with2/3 slower pairs fails the strict fixture guard. Exact18 results/138 checkpoints,86 ordinary tests and4092 integer/predicate comparisons passed. No extra samples, chunk/threshold sweep, confirmation or adoption. E020 retained."
 e['evidence'].extend([{'label':'E045 primary assessment','url':'evidence/E045-three-pair-comparison/report.json'},{'label':'E045 root raw arithmetic cross-check','url':'evidence/E045-root-crosscheck-r2/report.json'},{'label':'Preserved root accumulation-order assertion','url':'evidence/E045-root-crosscheck/failure.json'}])
 status.update(state='running',stage='Preparing E045 fixed confirmation' if passed else 'Next source investigation',activity='E045 initial timing passed; fresh confirmation and no-tradeoff qualification pending.' if passed else 'E045 rejected; accepted E020 retained. Further source investigation remains active.',updated_at=ar.now());ar.atomic_json(ar.STATUS,status)
D=ROOT/'runs/E045-design-r2';B=ROOT/'runs/E045-final-build-r2';C=ROOT/'runs/E045-control-execution/complete.json'
fixtures='; '.join(f"{f['fixture_id']} gain{f['observed_gain_pct']:.10f}%" for f in Q['fixtures'])
guards='; '.join(f"{g['fixture_id']} median slowdown{g['median_slowdown_pct']:.10f}%,{g['slower_pairs']}/3 slower,failed={g['failed']}" for g in v['fixture_regression_guard'])
outcome='This initial screen advances only to a separately frozen fresh16-pair confirmation. No candidate adoption or new cumulative gain is established.' if passed else 'E045 is rejected. No extra samples, chunk/threshold sweep, fresh confirmation, broader/holdout/cumulative/resource qualification or adoption follows.'
text=f'''

## D075 history correction and E045 parallel zero-proof screen

The source-history check found E043 exactly repeated earlier rejected D049: both candidate CUDA files hash aa7c5d83b610b94ca3b722312cfe977d235c2f286333453bbbe5b68c1a7762fb. The new D075 correction preserves both original records and labels E043 a repeat, not a new hypothesis. No further duplicate execution occurred. D075 separately revisited the unimplemented D041 parallel integer-OR suggestion. Historical D042 summed fixture-median host envelopes are270.8338ms for the complete predicates,18.8896ms for allocation/submission and56.6650ms for existing waits. They are instrumented historical spans, not current removable work, a projected saving or disjoint causal effects.

E045 changes only arena.rs: both complete signed/unsigned q scans retain exact u16 OR, with fixed1Miword chunks for inputs at least2Miwords, using the existing Rayon pool. Small scans remain serial. Scale-first bit checks, signed casts, snapshot/inactive/F32 guards, source arrays, CUDA, all upload/readback arithmetic, buffers and graph/launch shape stay unchanged. Added CPU concurrency is a potential resource cost: before any adoption, separately frozen matched whole-process CPU-time/peak-memory and responsiveness qualification is required, including rejection for positive median CPU-time increase with a strict majority paired increases. Wall time alone never proves no tradeoffs.

The first feature build failed on two test Store constructors expecting u64 rather than usize. Session42814's failed source/diagnostics/restoration remain preserved; primary and native tests never started. R2 changes only those bounded test length casts, with production bytes identical. Source manifest {old.sha(D/'manifest.json')} binds candidate {old.sha(D/'candidate-arena.rs')}. Fresh feature and GPU-primary R2 builds completed in session11351; terminal {old.sha(B/'terminal.json')} binds all compiler completion and accepted162 restoration. V045-unit ran once after that barrier:86passed/4ignored. Native tests compared3516 complete raw integer OR results at1/2/16 workers across chunk/threshold boundaries, single bits, signed representations and dense inputs, plus576 full accepted-original predicate cases covering scales, nonfinite/signedzero bits and both snapshot guards. Inputs remained unchanged. Root check {old.sha(ROOT/'comparisons/E045-integer-control-root/report.json')} verified source scope, exact copied reference, raw markers, corpus arithmetic and compiled provenance in16 checks; it is not an external independent audit.

Protocol {old.sha(HERE/'protocol.json')} froze exactly B137/E045R1,E045R2/B138,B139/E045R3 after controls.42 artifacts were served and HTTP byte-verified before timing. Native session50061 completed all six processes once. All18 complete non-timing payloads and138 convergence checkpoints match E020C1. Aggregate medians {v['baseline_full_cycle_ms']:.10f} to {v['candidate_full_cycle_ms']:.10f}ms give {v['observed_gain_pct']:.10f}% observed gain. Descriptive fixtures: {fixtures}. Strict guards: {guards}. {outcome}

The first root arithmetic observer used sequential bs+=median instead of Python3.12 sum's compensated aggregation. The same three medians differed by about1.8e-12ms, causing its exact-equality assertion to fail. Its script/failure are preserved. An assessment-only R2 independently uses math.fsum over the same retained medians and passes49 checks; no native sample, decision, threshold, rounded source value or exclusion changed. Primary assessment {old.sha(ROOT/'comparisons/E045-three-pair-comparison/report.json')} and root recomputation {old.sha(ROOT/'comparisons/E045-root-crosscheck-r2/report.json')} preserve the rejection, with no historical timing pooling or extension. Root cross-checks do not establish statistical confidence or universal equivalence. The complete evidence is published and HTTP verified. Accepted E020 remains at its previously qualified10.3798454492% cumulative gain; last actual primary baseline isB139. Main/HEAD/live, accepted162 and both protected PTX files remain exact. The research goal remains active.
'''
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';previous=ledger.read_bytes();assert b'## D075 history correction and E045 parallel zero-proof screen' not in previous
newline=b'\r\n' if b'\r\n' in previous else b'\n';ledger.write_bytes(previous+text.encode('utf-8').replace(b'\n',newline))
print(json.dumps({'decision':Q['decision'],'gain_pct':v['observed_gain_pct'],'publication_sha256':old.sha(HERE/'primary-publication.json'),'published_files':len(published)}),flush=True)
