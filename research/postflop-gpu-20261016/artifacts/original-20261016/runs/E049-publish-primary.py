"""Publish retained E049 evidence; a preliminary timing pass cannot adopt."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E049-primary-plan';P=old.read(H/'protocol.json');Q=old.read(ROOT/'comparisons/E049-three-pair-comparison/report.json');R=old.read(ROOT/'comparisons/E049-root-crosscheck/report.json')
v=Q['performance'];passed=v['primary_timing_pass'];gain=v['observed_gain_pct']
assert Q['decision']==('advance_to_separately_frozen_confirmation' if passed else 'rejected')
assert R['status']==('pass_initial_timing_only' if passed else 'pass_rejected')
T=old.read(ROOT/'runs/E049-native-execution/terminal.json');assert T['returncode']==0 and T['complete_sha256']==old.sha(ROOT/'runs/E049-native-execution/complete.json')
directories=[H,ROOT/'runs/E049-native-execution',ROOT/'comparisons/E049-three-pair-comparison',ROOT/'comparisons/E049-root-crosscheck']+[ROOT/'runs'/n for n in P['previously_terminal_control_ids']+P['measurement_order']]
published={}
for directory in directories:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'primary-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'decision':Q['decision'],'candidate_accepted':False})
fail=[x['fixture_id'] for x in v['fixture_regression_guard'] if x['failed']]
controls=old.read(P['controls_report']['path'])
ordinary=', '.join(f"{x['mode']} {x['passed']} passed/{x['ignored']} ignored" for x in controls['records'])
reason=f'Observed aggregate {gain:.6f}% '+('passes initial1% gate.' if gain>=1 else 'below1%.')+(' Strict fixture guards failed: '+', '.join(fail)+'.' if fail else ' No strict fixture guard failed.')
reason+=(' Fresh16pair confirmation and CPU/resource/whole-process/broader/holdout/cumulative gates required before adoption.' if passed else ' Rejected without extra samples, tracking/access variant rescue or confirmation.')
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E049');e.update(status='preparing' if passed else 'rejected',stage='Initial pass; fresh16 confirmation required' if passed else 'Closed after fixed primary',correctness='pass',baseline_full_cycle_ms=v['baseline_full_cycle_ms'],full_cycle_ms=v['candidate_full_cycle_ms'],observed_gain_pct=gain,reason=reason+' '+ordinary+'; 5600 original predicate comparisons and18fullresults/138checkpoints exact. E020 retained.')
 e['evidence'].extend([{'label':'E049 complete primary assessment','url':'evidence/E049-three-pair-comparison/report.json'},{'label':'E049 root raw arithmetic check','url':'evidence/E049-root-crosscheck/report.json'}]);st.update(state='running',stage='E049 confirmation preparation' if passed else 'Next source investigation',activity='E049 initial pass; no accepted gain yet.' if passed else 'E049 rejected; accepted E020 retained. Research continues.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
guards='; '.join(f"{x['fixture_id']} median slowdown {x['median_slowdown_pct']:.10f}%, {x['slower_pairs']}/3 slower, failed={x['failed']}" for x in v['fixture_regression_guard'])
text=f'''

## E049 untouched-default ownership proof - fixed primary outcome

D079 led to one frozen two-file candidate: ArenaBuf carries GPU-feature-only sticky AtomicBool metadata; every borrowed or mutable exposure invalidates before escape. By-value primitive read/length/move does not invalidate. Only concrete i16/u16 defaults establish zero. can_upload_zeros keeps original scale-bit/snapshot/inactive guards and exact q OR fallback. GPU kernels, floating arithmetic, evaluator, solve cadence, savings formats and data allocations are unchanged. Candidate source manifest {old.sha(ROOT/'runs/E049-final-source/manifest.json')} and source review {old.sha(ROOT/'runs/E049-final-source/source-review.json')} describe the invariant and potential costs. No unsafe pointer tagging or iteration-zero inference is used.

Build protocol {old.sha(ROOT/'runs/E049-build-plan/build-protocol.json')} produced fresh CPU-only, feature and primary artifacts, restoring accepted162 after each terminal phase. Control protocol {old.sha(ROOT/'runs/E049-control-plan/protocol.json')} executed full inventories and all nonignored CPU/GPU units: {ordinary}. New controls cover shared-view/rawpointer escape, mutable slice/write, by-value read, metadata, owner move, zero restoration remaining invalidated, concurrent disjoint writes, plus 5600 exact original-predicate comparisons across sizes, access histories, signedzero/nonfinite scales and both snapshot guards. Candidate executes before original scan; explicit pristine witnesses prove intended no-q-scan execution. Compiled GPU metadata sizes are32B for ArenaBuf i16/f32 and72B Store; matched baseline costs/final-artifact code/CPU performance have not been qualified. Control report {old.sha(Path(P['controls_report']['path']))} is scoped correctness, not adoption evidence.

Primary protocol {old.sha(H/'protocol.json')} froze exactly B146/E049R1,E049R2/B147,B148/E049R3. All18 complete non-timing results and138 convergence checkpoints match E020C1. Sum of per-fixture medians {v['baseline_full_cycle_ms']:.10f} to {v['candidate_full_cycle_ms']:.10f}ms yields {gain:.10f}% observed gain. Strict guards: {guards}. {reason}

Assessment {old.sha(ROOT/'comparisons/E049-three-pair-comparison/report.json')} and root raw arithmetic replay {old.sha(ROOT/'comparisons/E049-root-crosscheck/report.json')} preserve all samples without historical timing pooling, exclusions, extensions or statistical-confidence claims. Root replay is not external independent review. Complete source/build/control/fixed timing evidence is served and HTTP byte-verified. No new source adoption or speed claim: E020 remains the accepted source at previously qualified10.3798454492% cumulative suite gain. Last actual primary baseline B148. Accepted162/main/HEAD/live/protected PTX remain exact; goal active.
'''
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'## E049 untouched-default ownership proof - fixed primary outcome' not in raw;nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+text.encode('utf-8').replace(b'\n',nl))
print(json.dumps({'decision':Q['decision'],'gain_pct':gain,'published_files':len(published),'publication_sha256':old.sha(H/'primary-publication.json')}),flush=True)
