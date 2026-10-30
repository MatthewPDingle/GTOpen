"""Publish E051's frozen initial decision without preliminary adoption."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E051-primary-plan';P=old.read(H/'protocol.json');Q=old.read(ROOT/'comparisons/E051-three-pair-comparison/report.json');R=old.read(ROOT/'comparisons/E051-root-crosscheck/report.json');v=Q['performance'];gain=v['observed_gain_pct'];passed=v['primary_timing_pass']
assert Q['decision']==('advance_to_separately_frozen_confirmation' if passed else 'rejected')
assert R['status']==('pass_initial_timing_only' if passed else 'pass_rejected')
EX=ROOT/'runs/E051-native-execution';T=old.read(EX/'terminal.json');assert T['returncode']==0 and T['complete_sha256']==old.sha(EX/'complete.json')
published={}
for directory in [H,EX,ROOT/'comparisons/E051-three-pair-comparison',RPATH:=ROOT/'comparisons/E051-root-crosscheck']+[ROOT/'runs'/n for n in P['control_ids']+P['measurement_order']]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'primary-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'decision':Q['decision'],'candidate_accepted':False})
fail=[x['fixture_id'] for x in v['fixture_regression_guard'] if x['failed']]
reason=f'Observed aggregate {gain:.6f}% '+('passes initial1% gate.' if gain>=1 else 'below1%.')+(' Strict fixture guards failed: '+', '.join(fail)+'.' if fail else ' No strict fixture guard failed.')
reason+=(' Separately frozen fresh16pairs and broader/F32/continuation/holdout/fresh-original cumulative/resource gates required before adoption.' if passed else ' Rejected without extra samples, scheduling/cache/qualifier/factor rescue or confirmation.')
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E051');e.update(status='preparing' if passed else 'rejected',stage='Initial pass; fresh16confirmation required' if passed else 'Closed after fixed primary',correctness='pass',baseline_full_cycle_ms=v['baseline_full_cycle_ms'],full_cycle_ms=v['candidate_full_cycle_ms'],observed_gain_pct=gain,reason=reason+' 84ordinary tests,819direct cases and18fullresults/138checkpoints exact. E020 retained.');e['evidence'].extend([{'label':'E051 full initial assessment','url':'evidence/E051-three-pair-comparison/report.json'},{'label':'E051 root raw arithmetic replay','url':'evidence/E051-root-crosscheck/report.json'}]);st.update(state='running',stage='E051 fixed confirmation preparation' if passed else 'Next GPU hotspot investigation',activity='E051 initial pass; no new accepted gain.' if passed else 'E051 rejected; E020 retained. Research continues.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
guards='; '.join(f"{x['fixture_id']} median slowdown{x['median_slowdown_pct']:.10f}%,{x['slower_pairs']}/3 slower,failed={x['failed']}" for x in v['fixture_regression_guard'])
text=f'''

## D082 / E051 independent strategy-store scheduling - fixed primary outcome

E051 moves unlocked own-node strategy FMA/store into its existing ascending expectation loop, with hand reach read immediately before it. The final ordered loop updates regrets after the complete node value is known. Source candidate {old.sha(ROOT/'runs/E051-source/candidate.cu')} changes only this helper scheduling: no new array/cache/alias qualifier/arity factor/dispatch, host path, floating expression or out-reduction order. Existing locked/opponent branches and allother source entries stay exact. D038 already showed common2/3/4paths sharing sigma registers, so no duplicated-common-division removal was claimed. The invariant relies on supported disjoint learning/CFV owners. E003 qualifiers and rejected E024/E047 mechanisms are not composed.

Two pre-native preparation failures are retained: R1 referenced a missing legacy expected_abi field; R2 counted commas inside a source comment. R3 derives the20parameter ABI after stripping comments, with candidate/probe/runner bytes unchanged and no outcome seen. Resource protocol {old.sha(ROOT/'runs/E051-resource/protocol.json')} completed one no-launch probe: registers66to62, local64/shared0unchanged, maxthreads896to1024, theoretical64/128/256occupancy14/7/3to16/8/4. ABI and other8current-architecture entries are byte-exact. Root replay {old.sha(ROOT/'comparisons/E051-resource-root-check/report.json')} confirms only resource feasibility.

Raw control protocol {old.sha(ROOT/'runs/E051-kernel-control/protocol.json')} passed819cases/1638launches across3roles,bothactors/algorithms,arities1-17,hands0-1326,alternateblocks,signedzero/subnormal/quietNaN/infinity/finiteoverflow/count0.264cases execute the changed nonempty unlocked path. Native summary counts derive from actual vector length; no copied E047 stale summary recurred. All12375858output,5199114actual immutable and10240828guard/unowned words compare exactly. Actual mutable device extents are captured and checked disjoint for botharms/everycase. Five full raw files remain retained. Source owner review covers ordinary/continuation/paging allocation and positional swaps. Root raw decoder {old.sha(ROOT/'comparisons/E051-kernel-control/report.json')} passed63080checks; it is not external independent review or universal malformed-input proof.

Build protocol {old.sha(ROOT/'runs/E051-build-plan/build-protocol.json')} produced fresh feature/primary artifacts and restored accepted162 aftereachterminalphase. Primary protocol {old.sha(H/'protocol.json')} froze V051-unit and exactly B149/E051R1,E051R2/B150,B151/E051R3.84ordinary tests passed/4ignored. All18complete non-timing results/138convergence checkpoints match E020C1. Sum of fixture medians {v['baseline_full_cycle_ms']:.10f} to {v['candidate_full_cycle_ms']:.10f}ms gives {gain:.10f}% observed gain. Strict guards: {guards}. {reason}

Assessment {old.sha(ROOT/'comparisons/E051-three-pair-comparison/report.json')} and root raw arithmetic replay {old.sha(RPATH/'report.json')} preserve all observations without historical timing pooling/exclusions/extensions or statistical-confidence claims. Prospective and final artifacts are served/HTTP byte-verified. No preliminary source adoption occurs; E020 stays accepted at previously qualified10.3798454492% cumulative suite gain. Last actual primary baseline B151; accepted162/main/HEAD/live/protected PTX remain exact. Goal active.
'''
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'## D082 / E051 independent strategy-store scheduling' not in raw;nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+text.encode('utf-8').replace(b'\n',nl))
print(json.dumps({'decision':Q['decision'],'gain_pct':gain,'published':len(published),'publication_sha256':old.sha(H/'primary-publication.json')}),flush=True)
