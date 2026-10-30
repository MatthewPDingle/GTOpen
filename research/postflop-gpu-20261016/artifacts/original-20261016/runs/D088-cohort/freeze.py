"""Freeze exactly three baseline/diagnostic rainbow pairs after compiler exit."""
import json,sys,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
done=old.read(ROOT/'runs/D088-final-build/complete.json');assert done['all_compilers_terminal'] and done['native_executions']==0
for p,h in done['evidence_sha256'].items():old.pin(p,h)
binaries={}
for arm,stem in [('baseline','E051-postflop_autoresearch'),('diagnostic','D088-postflop_autoresearch')]:
 path=ROOT/'binaries'/(stem+'.exe');manifest=path.with_suffix('.manifest.json');m=old.read(manifest);old.pin(path,m['binary_sha256']);expected=old.BASE if arm=='baseline' else old.BASE|old.read(ROOT/'runs/D088-source/manifest.json')['candidate_owned_sha256'];assert m['source_sha256']==expected
 binaries[arm]={'path':str(path),'sha256':old.sha(path),'manifest':str(manifest),'manifest_sha256':old.sha(manifest)}
ids=['D088B1','D088T1','D088T2','D088B2','D088B3','D088T3'];assert all(not (ROOT/'runs'/i).exists() for i in ids)
paths=[H/'native.py',Path(__file__),ROOT/'runs/D088-final-build/complete.json',ROOT/'runs/D088-build-plan/build-protocol.json',ROOT/'runs/D088-source/manifest.json',ROOT/'runs/D088-source/source-review.json',ROOT/'comparisons/D087-driver-phase-root-check/report.json',ROOT/'runs/accepted-E051/common_e051.py']+[Path(v[k]) for v in binaries.values() for k in ['path','manifest']]
P={'id':'D088-constructor-cohort','at':old.now(),'status':'FROZEN_PRE_NATIVE','order':ids,'pairs':[{'baseline':'D088B1','diagnostic':'D088T1'},{'baseline':'D088B2','diagnostic':'D088T2'},{'baseline':'D088B3','diagnostic':'D088T3'}],'binaries':binaries,'fixture':'rainbow','storage':'compressed','profile_after_timing':'0','outer_stages':['plan_budget','context_stream','nvrtc_module','pinned_staging','arena_layouts','regret0_upload','regret1_upload','strategy0_upload','strategy1_upload','lock_table','fold_table','metadata_upload_and_object'],'quality_gate':'Exact accepted6full states/60checkpoints;12ordered outer markers and4nested positive-zero scans perdiagnostic. Nested spans<=matching upload; outer sum<=enclosing GPU-init clock. Source/ABI/allocations/quality unchanged except CPU timing logs.','observer_gate':'Absolute complete/native/whole-runner wall changes<=10%in every fixedpair. All observations retained; no extensions/exclusions/historical timing pooling.','limits':'Only fresh compressed rainbow and fixed measured process lifecycle. Observer gate is not universal/per-stage-bias proof. CPU markers perturb codegen/scheduling and log outside their own spans. No optimizer accepted; nested times are not additive to enclosing spans.','input_sha256':{str(p):old.sha(p) for p in paths},'accepted_source':'E051','optimization_accepted':False}
P['observer_gate']='Absolute complete-cycle, enclosingGPU-init, native-process and whole-runner wall changes<=10%in every fixedpair. No exclusions, extensions or historical timing pooling.'
P['additional_init_gate_provenance']='Prospectively added before any native observation: D012 found code-layout-associated constructor stalls. The target stage must itself remain representative, beyond the three coarse clocks in the initial diagnostic source review.'
old.save(H/'protocol.json',P)
for src in H.iterdir():
 if not src.is_file():continue
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15).read()==src.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='D088');e.update(stage='Build complete; fixed matched constructor observations',reason='AcceptedE051 restored. Six fixed rainbow processes compare stage observer against immutable accepted binary; exact state/checkpoints and all three clocks required.');e['evidence'].append({'label':'D088 frozen matched cohort','url':'evidence/D088-cohort/protocol.json'});st.update(updated_at=old.now(),stage='D088 matched constructor profiling',activity='Exactly3ordinary/diagnostic pairs with12outer stages and4nested zero-state scans; no optimization acceptance.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json')}),flush=True)
