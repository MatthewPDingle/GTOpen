import json,sys,statistics
from pathlib import Path
sys.path.insert(0,'tools');import postflop_autoresearch as ar
out=ar.RESEARCH/'comparisons/D013-isolated-summary';assert not out.exists();out.mkdir()
exactkeys=['config','algorithm','storage','iteration','max_iterations','check_every','target_pct','target_met','exploit_bits','fingerprint','state_fingerprint','nodes','cpu_arena_bytes','use_isomorphism']
fields=['build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms'];fixtures=[];inputs=[]
for tag,name in [('T','two-tone'),('R','river')]:
 groups={}
 for kind in ['B','C']:
  groups[kind]=[]
  for n in range(1,4):
   rid=f'D013-{tag}{kind}{n}';p=ar.RESEARCH/'runs'/rid/'report.json';report=json.loads(p.read_text(encoding='utf-8-sig'))
   assert report['status']=='measured' and len(report['results'])==1
   r=report['results'][0];assert r['fixture_id']==name;groups[kind].append(r)
   inputs.append({'id':rid,'report_sha256':ar.sha256(p),'log_sha256':ar.sha256(p.with_name('stdout.log'))})
 baseline=groups['B'][0]
 for r in groups['B']+groups['C']:
  for k in exactkeys: assert r[k]==baseline[k], (name,k)
 metrics={}
 for field in fields:
  b=[r[field] for r in groups['B']];c=[r[field] for r in groups['C']];bm=statistics.median(b);cm=statistics.median(c)
  metrics[field]={'baseline_values':b,'candidate_values':c,'baseline_median':bm,'candidate_median':cm,'median_regression_pct':100*(cm/bm-1),'paired_regression_pct':[100*(y/x-1) for x,y in zip(b,c)]}
 fixtures.append({'fixture_id':name,'exact_screen':'pass','exact_fields':exactkeys,'metrics':metrics})
report={'schema_version':1,'id':out.name,'created_at':ar.now(),'kind':'diagnostic','accepted_gain':False,'baseline':'E004','candidate':'E010','fixtures':fixtures,'inputs':inputs,'interpretation':['The isolated two-tone candidate is slower overall despite lower readback time. The earlier full-suite construction advantage is absent when this fixture runs first.','The isolated river median is slower by about 7%, substantially less than the full-suite 80% regression. Three paired values vary, so this diagnostic does not establish a stable isolated river penalty.','These observations support sensitivity to execution history, without proving an allocator or CUDA cause. E010 remains rejected under the frozen full-suite evaluator.'],'limitations':['Fixture filters change first-use NVRTC/PTX costs, allocator and cache history. Do not compare absolute values with fixed-suite scores or claim a replacement qualification.','Three paired repetitions are diagnostic; no statistical significance is claimed.','The registered complete cycle excludes post-fingerprint destruction. A future object-lifetime change needs separate whole-process measurement including destruction so work moved outside the boundary is not claimed as savings.']}
ar.atomic_json(out/'report.json',report);ar.atomic_json(ar.DASHBOARD/'evidence'/out.name/'report.json',report)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=json.loads(ar.STATUS.read_text(encoding='utf-8-sig'))
 for row in s['experiments']:
  if row['id'].startswith('D013-'):
   row['correctness']='pass';row['reason']='Exact isolated fixture screen passed; diagnostic summary reports order sensitivity. E010 remains rejected.';row.setdefault('evidence',[]).append({'label':'Isolated fixture findings','url':f'evidence/{out.name}/report.json'})
 s.update(updated_at=ar.now(),state='running',stage='D013 diagnosed execution-history sensitivity; E004 restored',activity='The GPU quantization branch remains rejected. Reviewing a smaller CPU readback optimization from the accepted implementation.',active_experiment=None)
 ar.atomic_json(ar.STATUS,s)
for f in fixtures:
 print(f['fixture_id'],json.dumps(f['metrics'],indent=2))
