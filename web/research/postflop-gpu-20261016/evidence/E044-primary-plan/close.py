"""Publish E044 rejection without modifying accepted implementation or old evidence."""
import json,sys,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
ROOT=old.ROOT;ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
P=old.read(HERE/'protocol.json');Q=old.read(ROOT/'comparisons/E044-three-pair-comparison/report.json');R=old.read(ROOT/'comparisons/E044-root-crosscheck/report.json')
assert Q['decision']=='rejected' and R['status']=='pass_rejected'
assert Q['exactness']['all_exact'] and Q['exactness']['fixture_results']==18
paths=[HERE,ROOT/'runs/E044-native-execution',ROOT/'comparisons/E044-three-pair-comparison',ROOT/'comparisons/E044-root-crosscheck']+[ROOT/'runs'/n for n in P['measurement_order']]
published={}
for directory in paths:
 for source in directory.rglob('*'):
  if not source.is_file() or '__pycache__' in source.parts:continue
  key=directory.name+'/'+source.relative_to(directory).as_posix();raw=source.read_bytes();target=ar.DASHBOARD/'evidence'/key;target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():assert target.read_bytes()==raw
  else:target.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(source)
old.save(HERE/'closure-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'decision':'rejected','candidate_accepted':False})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);row=next(e for e in s['experiments'] if e['id']=='E044');v=Q['performance']
 row.update(status='rejected',correctness='pass',stage='Closed after fixed primary screen',reason='Aggregate1.6823% slower; rainbow/two-tone/river fixture slowdown guards all failed. Exact18 results/138 checkpoints;84 ordinary tests and14 GPU lifecycle cases/308 raw pairs passed. No extra samples, slot-count sweep, confirmation or adoption. Accepted E020 retained.',baseline_full_cycle_ms=v['baseline_full_cycle_ms'],full_cycle_ms=v['candidate_full_cycle_ms'],observed_gain_pct=v['observed_gain_pct'])
 row['evidence'] += [{'label':'E044 primary rejection','url':'evidence/E044-three-pair-comparison/report.json'},{'label':'E044 raw arithmetic cross-check','url':'evidence/E044-root-crosscheck/report.json'}]
 s.update(state='running',stage='Next source investigation',activity='E044 rejected; accepted E020 retained. Investigating a distinct source of overhead.',updated_at=ar.now())
 ar.atomic_json(ar.STATUS,s)
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md'
text=ledger.read_text(encoding='utf-8');assert '## D074 pinned discount upload; E044 rejected' not in text
text+='''

## D074 pinned discount upload; E044 rejected

D074 reviewed ordinary three-float CPU discount uploads as a possible source of pageable staging synchronization. Driver documentation permits such synchronization; this was a hypothesis, not measured idle-time headroom. E044 used two disjoint three-float windows of the existing pinned staging allocation, reserving ownership before submission and draining before reuse. A first-declared-field guard drained pending sources before other fields released. Tiny staging retained the original upload; both readback methods reset ownership after their existing initial drain. Original CPU discount arithmetic, CUDA, plan, storage, graph shape and continuation discount path stayed unchanged. No new pinned/device/event/stream/graph allocation was added; measured solver object size rose4448 to4464bytes.

Source manifest6e99a2a1c82fc935b6a578ccb9ec5762160ad89b7fd0b91af3a340f5e56ccadb binds the off-tree candidate39e56fce7214cd6ee033ddc497757c8b86d23c7efd73640c9e286e07f51414bc. Fresh feature and primary builds passed under protocol4226ac9a7a4185958e5844b563ee30780d2a44f143dbdceec4704825db241232, terminal session9712; accepted162 restored. Native control protocolabe498b0e3e80d1618b3c581af21e319ee41d16f5d890c3495473a63f039e321 ran once:84 ordinary tests passed/5ignored;14 original-versus-candidate lifecycle cases covered DCFR/CFR+, compressed/F32, full/compact/iso and four tiny fallbacks. Ten cases used the pinned path. Each retained45 files/22 raw pairs, totaling630files/308pairs; unsynchronized batch lengths1/2/3/5/8, profiled iterate, exploitability, full/strategy readback, symmetry materialization, lock replacement, save/query and continued iterations matched exactly. Normal, injected-post-copy-error and unwind drop controls each drained once with stream readiness observed before field release. These finite controls do not establish speed or responsiveness.

The first root decoder incorrectly compared strategy-only CPU regrets with a snapshot preceding ensure_symmetric. Its failure and original script are preserved. Assessment-only revision compares the retained preceding materialized snapshot; no source, binary or native run changed. Root report5d4e0656e0f7ce870cf7ce63e38e611841d71287862fa35cc28e78a5f2a65011 passed7834 checks and directly decoded all retained raw states. This is a root cross-check, not an external independent audit.686 evidence files including the full raw corpus, corrected observer, failed assertion and frozen primary were served and HTTP verified before timing.

Primary protocolaf13e9d14a0b72628c655dba751b2c77bd82e3aa9bac6968bb6147afb3c8d040 froze exactly B134/E044R1, E044R2/B135, B136/E044R3. Native session84930 completed once. All18 full non-timing results and138 checkpoints match E020C1. Complete-cycle aggregate10341.6549 to10515.6351ms is1.6823245572% slower, so E044 is rejected. Median slowdowns are1.5270231875% rainbow with2/3 slower pairs,1.1417558101% two-tone with2/3, and31.0347319302% river with3/3. All three strict fixture guards fail. Comparisonb6981d1b1c34649e58c07a755c50ad4a8f772c4e7f95f26a6daa7dc7acd78265 and root arithmetic recomputationf85d80345a30067777cd69564ecc12157ac8905330ff5613e038e6d68cf2cdeb preserve the decision. Component changes do not attribute a unique cause. No extra samples, slot-count sweep, confirmation, broader/stop/process-wall qualification or adoption followed.

Rejection evidence is published and HTTP verified. E020 remains accepted at its previously qualified10.3798454492% cumulative gain; last actual primary baseline isB136. Main/HEAD/live, accepted162 and both protected PTX files remain exact. The goal remains active for a distinct source investigation.
'''
ledger.write_text(text,encoding='utf-8')
print(json.dumps({'published_files':len(published),'closure_sha256':old.sha(HERE/'closure-publication.json'),'accepted':'E020','last_baseline':'B136'}),flush=True)
