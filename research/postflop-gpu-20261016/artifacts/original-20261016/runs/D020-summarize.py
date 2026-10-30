import json,sys,statistics
sys.path.insert(0,'tools');import postflop_autoresearch as ar
ref=json.loads((ar.RESEARCH/'runs/B029/report.json').read_text(encoding='utf-8-sig'))['results'];reference={r['fixture_id']:r for r in ref}
all_profiles={name:[] for name in reference};inputs=[]
for rid in ['D020','D020R2','D020R3']:
 p=ar.RESEARCH/'runs'/rid/'report.json';d=json.loads(p.read_text(encoding='utf-8-sig'));assert d['status']=='measured' and len(d['results'])==3 and d['test_pass_count']==1
 assert d['environment']['POSTFLOP_AUTORESEARCH_PROFILE']=='1'
 for r in d['results']:
  for k in ['config','iteration','fingerprint','state_fingerprint','exploit_bits','target_met']:assert r[k]==reference[r['fixture_id']][k],(rid,k)
 stages=[]
 for line in p.with_name('stdout.log').read_text(encoding='utf-8-sig').splitlines():
  marker='AUTORESEARCH_STAGE '
  if marker in line:stages.append(json.loads(line.split(marker,1)[1]))
 assert next(s for s in stages if s['stage']=='suite_start')['profile_after_timing'] is True
 profiles=[s for s in stages if s['stage']=='diagnostic_profile'];assert len(profiles)==3
 for s in profiles:
  assert s['excluded_from_score'] and s['iteration']==reference[s['fixture_id']]['iteration']+1
  all_profiles[s['fixture_id']].append({'run':rid,**s})
 inputs.append({'id':rid,'report_sha256':ar.sha256(p),'stdout_sha256':ar.sha256(p.with_name('stdout.log')),'binary_sha256':d['binary_sha256']})
fixtures=[]
for fixture,profiles in all_profiles.items():
 names=profiles[0]['kernel_names'];counts=profiles[0]['launches'];assert all(p['kernel_names']==names and p['launches']==counts for p in profiles)
 rows=[]
 for i,name in enumerate(names):
  values=[p['profile_ms'][i] for p in profiles];median=statistics.median(values)
  rows.append({'kernel':name,'launches_per_sample':counts[i],'host_ms':values,'median_host_ms':median,'min_host_ms':min(values),'max_host_ms':max(values),'median_host_ms_per_launch':median/counts[i] if counts[i] else None})
 rows.sort(key=lambda r:r['median_host_ms'],reverse=True)
 fixtures.append({'fixture_id':fixture,'scored_iteration':reference[fixture]['iteration'],'profile_iteration':profiles[0]['iteration'],'exact_scored_state':'pass','ranked_host_spans':rows,'raw_profiles':profiles})
report={'schema_version':1,'id':'D020-profile-summary','created_at':ar.now(),'kind':'diagnostic','accepted_gain':False,'fixtures':fixtures,'inputs':inputs,'interpretation':'Both flop fixtures rank up_action, up_show, then down_action highest in repeated synchronization-instrumented host spans. These are priorities for bounded experiments, not normal CUDA-graph device-time shares.','limits':['Three late-state samples per fixture after fingerprinting; GPU state advances one extra iteration then is discarded.','Host launch setup and per-launch stream synchronization replace normal graph replay, perturbing timing; no percentage of ordinary solve time is inferred.','First copy_root also drains preceding discount upload; river/small-kernel spans are especially overhead-sensitive.','Best-response/evaluation, initialization and readback are not profiled. All complete-cycle values from these diagnostic runs remain excluded from acceptance.']}
out=ar.RESEARCH/'comparisons/D020-profile-summary';assert not out.exists();ar.atomic_json(out/'report.json',report);ar.atomic_json(ar.DASHBOARD/'evidence/D020-profile-summary/report.json',report)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=json.loads(ar.STATUS.read_text(encoding='utf-8-sig'))
 for row in s['experiments']:
  if row['id'] in ['D020','D020R2','D020R3']:
   row['correctness']='pass';row['reason']='Exact scored state matches E004. Extra profiling is diagnostic host wall time with per-launch synchronization, excluded from acceptance.';row.setdefault('evidence',[]).append({'label':'Repeated kernel profile and limits','url':'evidence/D020-profile-summary/report.json'})
 s.update(updated_at=ar.now(),stage='D020 profiles complete; selecting GPU action-kernel hypothesis',activity='Three exact diagnostic runs rank action updates and showdown highest on flops. Accepted implementation remains E004; rejected encoder variants are fully archived and reverted.',active_experiment=None);ar.atomic_json(ar.STATUS,s)
for f in fixtures:print(f['fixture_id'],[(r['kernel'],round(r['median_host_ms'],4),r['launches_per_sample']) for r in f['ranked_host_spans']])
