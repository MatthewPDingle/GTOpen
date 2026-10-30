import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as now
ar=now.ar;now.custody();assert not (ROOT/'gpu-run.lock').exists()
Q=ROOT/'comparisons/E051-qualification-r2';q=now.read(Q/'report.json');C=ROOT/'comparisons/E051-remaining-native-r3';c=now.read(C/'cumulative.json');h=now.read(C/'holdout.json')
assert q['status']=='accepted_source_integrated' and c['status']=='pass_fresh_original_cumulative' and h['strict_guard_failed'] is False
now.save(ROOT/'runs/E051-remaining-build-r3/terminal.json',{'at':now.now(),'session':76172,'returncode':0,'all_compilers_terminal':True,'native_executions':0,'complete_sha256':now.sha(ROOT/'runs/E051-remaining-build-r3/complete.json')})
now.save(ROOT/'runs/E051-remaining-native-execution-r3/terminal.json',{'at':now.now(),'session':14569,'returncode':0,'all_children_terminal':True,'complete_sha256':now.sha(ROOT/'runs/E051-remaining-native-execution-r3/complete.json')})
names=['E051-remaining-build-plan','E051-remaining-build-plan-r2','E051-remaining-build-plan-r3','E051-remaining-build','E051-remaining-build-r2','E051-remaining-build-r3','E051-remaining-native-plan','E051-remaining-native-plan-r2','E051-remaining-native-plan-r3','E051-remaining-native-execution','E051-remaining-native-execution-r3','E051-main-integration','E051-main-integration-r2','accepted-E051']
directories=[ROOT/'runs'/n for n in names]+[ROOT/'comparisons'/n for n in ['E051-remaining-native','E051-remaining-native-r3','E051-remaining-root-check','E051-qualification','E051-qualification-r2']]
published={}
def put(src,key):
 dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
 if dst.exists():assert dst.read_bytes()==data,key
 else:dst.write_bytes(data)
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=30) as response:assert response.read()==data,key
 published[key]=now.sha(src)
for directory in directories:
 if not directory.exists():continue
 for src in directory.rglob('*'):
  if src.is_file() and '__pycache__' not in src.parts:put(src,directory.name+'/'+src.relative_to(directory).as_posix())
for src in (ROOT/'runs').glob('E051-*.py'):put(src,'E051-final-scripts/'+src.name)
now.save(Q/'publication.json',{'at':now.now(),'http_byte_verified_files':len(published),'artifact_sha256':published,'source_integrated':True,'live_deployed':False})
links=[{'label':label,'url':'evidence/'+key} for label,key in [('E051 accepted qualification and tested scope','E051-qualification-r2/report.json'),('E051 fresh original cumulative comparison','E051-remaining-native-r3/cumulative.json'),('E051 six actual owned-capacity cases','E051-remaining-native-r3/capacity.json'),('E051 full-range turn holdout, all raw-state comparisons','E051-remaining-native-r3/holdout.json'),('E051 remaining root replay,153checks','E051-remaining-root-check/report.json'),('E051 exact source integration','E051-main-integration-r2/report.json'),('E051 updated accepted-source epoch','accepted-E051/baseline.json')]]
def merge(existing,extra):
 urls={x['url'] for x in existing};return existing+[x for x in extra if x['url'] not in urls]
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 now.custody();st=now.read(ar.STATUS);assert st['accepted_complete_run']['candidate_id']=='E020';stamp=now.now()
 record={'status':'validated','scope':'complete_run','candidate_id':'E051','baseline_ms':c['baseline_full_cycle_ms'],'best_ms':c['candidate_full_cycle_ms'],'observed_gain_pct':c['observed_gain_pct'],'correctness':'pass','measured_at':stamp,'method':q['scope']}
 st['accepted_complete_run']=record;st['accepted_history'].append(record|{'at':stamp})
 st['validation']={'status':'pass','candidate_id':'E051','summary':'All registered E051 exactness/performance/resource/capacity/holdout gates passed.84ordinary unit tests; full96result/736checkpoint fresh confirmation;160state/menu/resume snapshots each; F32/paging/stored checks exact. Root replay is not external independent review. Last isolated server validation remains E020.'}
 st['deployment'].update(candidate_id='E051',commit=q['heads']['main'],summary='E051 exact tested source integrated in main and research. Live executable replacement/restart remains blocked by automatic approval review: blocked by policy. Live executable remains the original version; the retained prepared server binary and last isolated server validation are E020.')
 st['deployment']['last_prepared_binary_candidate']='E020'
 st.update(updated_at=stamp,state='running',stage='E051 accepted; next GPU hypothesis',activity='Accepted2.175173%fresh16increment; fresh-original cumulative12.437227%. All registered gates passed; source integrated. Continue from new accepted E051 custody epoch. Live deployment remains blocked.',active_experiment=None)
 e=next(x for x in st['experiments'] if x['id']=='E051');e.update(status='accepted',stage='Qualified and source integrated',reason='Fresh16pairs:2.175173%gain,16/16improving; strict fixture guards pass. Exact raw/state/F32/continuation/capacity checks and fixed holdout pass. Fresh original cumulative12.437227%; no percentages added. Live executable unchanged.',accepted=True,correctness='pass',evidence=merge(e.get('evidence',[]),links),accepted_at=stamp)
 st['evidence']=merge(st.get('evidence',[]),links)
 for fixture,row,guard in zip(st['fixtures'],c['fixtures'],c['strict_fixture_guards']):
  fixture['baseline'].update(full_cycle_ms=row['baseline']['full_cycle_ms']['median_ms'],solve_ms=row['baseline']['solve_ms']['median_ms'],fingerprint=row['exact_screen']['fingerprint'],repetitions=3,provisional=False)
  fixture['best']={'status':'accepted','candidate_id':'E051','full_cycle_ms':row['candidate']['full_cycle_ms']['median_ms'],'solve_ms':row['candidate']['solve_ms']['median_ms'],'fingerprint':row['exact_screen']['fingerprint'],'median_regression_pct':guard['median_slowdown_pct'],'guard_passed':not guard['failed']}
  fixture['correctness']={'status':'pass','details':'Full non-timing states/settings/stops/checkpoints exact. Current strict guard rejects any positive median slowdown with >=2/3slower pairs. Separate fresh16confirmation, F32/saves/continuation/capacity and full-range turn holdout pass.'};fixture['evidence']=merge(fixture.get('evidence',[]),links)
 ar.atomic_json(ar.STATUS,st)
ledger=ar.REPO/'research/postflop-gpu-20261016/experiments.md';data=ledger.read_bytes();assert b'### E051 accepted after complete qualification' not in data
text=f'''\n### E051 accepted after complete qualification\n\nThe user's1%no-tradeoff policy accepts the exact tested strategy-store scheduling source. Fresh16confirmation remains2.1751731507%incremental,16/16positivepairs. Actual retained owned metadata/canonical state/workspace/public host sizes are exact across6existing construction cases. Device-wide observations are retained but never treated as solver-only allocations; no forced-spill or driver/temporary-peak proof is claimed. Compiled up_action registers66to62,local64/shared0 unchanged; no new host/graph/ABI/storage structure.\n\nFixed full169wide-turn holdout: six complete non-timing results/36checkpoints/all six full raw q/scale files exact to historical acceptedE020. Baseline median452.6791ms,candidate450.6156ms,0.4558416768%observed gain. The first candidate pair was7.090227%slower and is preserved; remaining2pairs improved, strict median/majority non-regression guard passed. No samples added or historical timings pooled.\n\nFresh original comparison B168/E051O1,E051O2/B169,B170/E051O3 gives{c['baseline_full_cycle_ms']:.10f}to{c['candidate_full_cycle_ms']:.10f}ms,**{c['observed_gain_pct']:.10f}%cumulative gain**. All18full payloads/138checkpoints exact; all current strict fixture guards pass. Prior10.3798%and incremental2.1752%are not added. Root raw/byte/arithmetic replay passes153checks ({now.sha(ROOT/'comparisons/E051-remaining-root-check/report.json')}); this is root review, not external independent review.\n\nAll failed build/artifact/path/historical-assessor/CRLF-whitespace preparations are preserved. Repairs changed wrappers only before dependent measured outcomes; capacity measurements were replayed without rerun, and no holdout/cumulative samples were excluded/repeated. Git whitespace handling recognizes exact testedCRLFbytes; no source normalization or global Git setting changed.\n\nQualification {now.sha(Q/'report.json')} precedes exact tested-source integration: research{q['heads']['research']},main{q['heads']['main']}. New acceptedE051 custody/helper/protection epoch is separate; all historical helpers and pins remain immutable. Registered suite scope includes construction/init/NVRTC/JIT/solve/checks/readback,warmdrivercache; excludes compilation/fingerprinting/destruction/API/browser/saving. No universal/cold-start/other-device/F32-speed claim. Live replacement/restart remains blocked by automatic review as blocked by policy; live bytes unchanged. All evidence files HTTPbyteverified. Goal remains active; next hypothesis starts fromE051.\n'''
nl=b'\r\n' if b'\r\n' in data else b'\n';ledger.write_bytes(data+text.encode('utf-8').replace(b'\n',nl))
now.custody()
with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/status.json',timeout=20) as response:live=json.load(response)
assert live['accepted_complete_run']['candidate_id']=='E051' and live['accepted_complete_run']['observed_gain_pct']==c['observed_gain_pct']
print(json.dumps({'status':'accepted_and_http_verified','published_files':len(published),'incremental_gain_pct':q['fresh16_gain_pct'],'cumulative_gain_pct':c['observed_gain_pct'],'publication_sha256':now.sha(Q/'publication.json')}),flush=True)
