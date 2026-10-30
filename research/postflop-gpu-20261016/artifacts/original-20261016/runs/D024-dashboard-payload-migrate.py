import copy,json,sys,hashlib
sys.path.insert(0,'tools');import postflop_autoresearch as ar
out=ar.RESEARCH/'runs/D024-dashboard-payload';out.mkdir(exist_ok=False)
input_files=[ar.RESEARCH/f'runs/{identity}/{name}' for identity in ['B032','B033','B034','E014','E014R2','E014R3'] for name in ['report.json','stdout.log']]
hashes={str(p):ar.sha256(p) for p in input_files}
for identity in ['B032','E014']:
 r=json.loads((ar.RESEARCH/f'runs/{identity}/report.json').read_text());original=copy.deepcopy(r)
 compact=ar.compact_dashboard_results(r['results']);assert r==original
 assert ar.compact_dashboard_results(compact)==compact
 for old,new in zip(r['results'],compact):assert new=={k:v for k,v in old.items() if k not in {'config','state_fingerprint'}}
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 raw=ar.STATUS.read_bytes();(out/'status-before.json').write_bytes(raw);before=json.loads(raw);after=copy.deepcopy(before)
 count=0
 for row in after['experiments']:
  if isinstance(row.get('results'),list):count+=len(row['results']);row['results']=ar.compact_dashboard_results(row['results'])
 # This reconstruction verifies every non-result field, row order and scalar
 # result field remains exactly equal; only two named nested fields disappear.
 restored=copy.deepcopy(after)
 for old,new in zip(before['experiments'],restored['experiments']):
  if isinstance(old.get('results'),list):new['results']=old['results']
 assert restored==before
 ar.atomic_json(ar.STATUS,after);(out/'status-after.json').write_bytes(ar.STATUS.read_bytes())
 assert len(after['experiments'])==len(before['experiments'])
 assert after['accepted_complete_run']==before['accepted_complete_run']
 assert after['deployment']==before['deployment']
 assert all(ar.sha256(p)==hashes[str(p)] for p in input_files)
report={'id':'D024','at':ar.now(),'kind':'tooling_only','performance_claim':False,'before_bytes':len(raw),'after_bytes':ar.STATUS.stat().st_size,'rows_preserved':len(after['experiments']),'result_entries_compacted':count,'removed_keys_only':['config','state_fingerprint'],'other_fields_and_order_exact':True,'input_reports_and_logs_unchanged':hashes,'pure_function_nonmutation':True,'idempotent':True,'runner_sha256':ar.sha256(ar.REPO/'tools/postflop_autoresearch.py'),'cohort_boundary':'Applied between completed E014 cohort and any E015 measurement. Full raw evidence and frozen evaluator unchanged.'}
ar.atomic_json(out/'report.json',report);print(json.dumps({k:report[k] for k in ['before_bytes','after_bytes','rows_preserved','result_entries_compacted','runner_sha256']}))
