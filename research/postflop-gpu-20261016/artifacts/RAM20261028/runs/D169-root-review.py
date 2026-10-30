import json,re,statistics,sys,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();H=ROOT/'runs/D169-worker-comparison';P=h.read(H/'protocol.json')
assert h.sha(H/'protocol.json')=='81f0d073dc40f3928fa0e81216d28d6151ef010a28fa4624e7cfdf46206ff761'
for path,digest in P['input_sha256'].items():h.pin(path,digest)
anchor=h.read(ROOT/'epoch/exact-anchor.json');records={};checks=0;logpins={}
excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms'}
for row in P['sequence']:
 d=ROOT/'runs'/row['id'];r=h.read(d/'report.json');receipt=h.read(d/'exit.json');inv=h.read(d/'invocation.json')
 h.pin(d/'stdout.log',r['stdout_sha256']);raw=(d/'stdout.log').read_text(encoding='utf-8')
 assert receipt['returncode']==r['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
 assert inv['RAYON_NUM_THREADS']==str(row['workers']) and inv['kind']==row['kind'] and inv['block']==row.get('block')
 assert inv['binary_sha256']==h.sha(inv['command'][0]) and r['protocol_sha256']==h.sha(H/'protocol.json')
 t=receipt['terminal_process_times'];assert t==r['terminal_process_times']
 assert t['lifetime_ms']==(t['exit_FILETIME']-t['creation_FILETIME'])/10000
 assert t['CPU_ms']==(t['kernel_100ns']+t['user_100ns'])/10000
 assert t['lifetime_ms']<=receipt['parent_wall_ms']<t['lifetime_ms']+2000
 if row['kind']=='unit':assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('86','0','4','0','0')]
 else:
  results=[json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]) for line in raw.splitlines() if 'AUTORESEARCH_RESULT ' in line]
  stages=[json.loads(line.split('AUTORESEARCH_STAGE ',1)[1]) for line in raw.splitlines() if 'AUTORESEARCH_STAGE ' in line]
  quality=[{k:s[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for s in stages if s.get('stage')=='convergence_check']
  assert [[{k:v for k,v in x.items() if k not in excluded} for x in results],quality]==anchor and results==r['results']
  assert [json.loads(line.split('D169_POOL ',1)[1]) for line in raw.splitlines() if line.startswith('D169_POOL ')]==[{'requested':row['workers'],'actual':row['workers'],'after_entire_suite_and_destructors':True}]
  assert raw.index('D169_POOL ')>raw.rindex('AUTORESEARCH_RESULT ') and 'test result: ok. 1 passed; 0 failed; 0 ignored;' in raw
  assert len(quality)==23 and all(x['runtime_nvrtc_jit_included'] for x in results)
  if row['kind']=='scored':records[row['block'],row['workers']]=(results,t)
 checks+=10
 for name in ['stdout.log','report.json','exit.json','invocation.json']:logpins[str(d/name)]=h.sha(d/name)
R=h.read(ROOT/'comparisons/D169-worker-comparison/report.json');out={}
for w in [8,32]:
 bsum=csum=0.;failed=[];guards=[]
 for f in ['rainbow','two-tone','river']:
  b=[next(x['full_cycle_ms'] for x in records[k,16][0] if x['fixture_id']==f) for k in [1,2,3]]
  c=[next(x['full_cycle_ms'] for x in records[k,w][0] if x['fixture_id']==f) for k in [1,2,3]]
  bm=sorted(b)[1];cm=sorted(c)[1];bsum+=bm;csum+=cm;slower=sum(y>x for x,y in zip(b,c));guard=cm>bm and slower>=2
  original=next(x for x in R['configuration_outcomes'][str(w)]['fixtures'] if x['fixture_id']==f)
  assert original['reference_ms']==b and original['candidate_ms']==c and original['guard_failed']==guard
  guards.append({'fixture':f,'median_slowdown_pct':100*(cm/bm-1),'slower_pairs':slower,'failed':guard});checks+=3
 gain=100*(bsum-csum)/bsum
 if gain<1:failed.append('aggregate_ge1pct')
 if any(x['failed'] for x in guards):failed.append('strict_fixture_clear')
 costs={}
 for metric in ['CPU_ms','lifetime_ms']:
  b=[records[k,16][1][metric] for k in [1,2,3]];c=[records[k,w][1][metric] for k in [1,2,3]]
  delta=100*(sorted(c)[1]/sorted(b)[1]-1);costs[metric]=delta
  assert R['configuration_outcomes'][str(w)]['whole_process_costs'][metric]['median_regression_pct']==delta
  if delta>1:failed.append(metric+'_median_regression_le1pct')
  checks+=2
 o=R['configuration_outcomes'][str(w)];assert o['observed_gain_pct']==gain and o['reference_sum_fixture_medians_ms']==bsum and o['candidate_sum_fixture_medians_ms']==csum
 assert o['failed_gates']==failed and o['decision']=='rejected_closed'
 out[str(w)]={'reference_ms':bsum,'candidate_ms':csum,'gain_pct':gain,'guards':guards,'process_median_change_pct':costs,'failed_gates':failed};checks+=4
assert R['advancing_worker_counts']==[] and len(records)==9
D168=ROOT/'comparisons/D168-worker-raw-control/report.json';q=h.read(D168)
assert q['status']=='pass_actual_worker_counts_and_full_canonical_raw_state' and q['actual_workers']=={'reference16':16,'workers8':8,'workers32':32}
for path,identity in q['whole_compared_file_sha256'].items():assert Path(path).stat().st_size==identity['bytes'];checks+=1
assert len(q['whole_compared_file_sha256'])==99 and q['raw_output_bytes']==163825995585
for parent in [ROOT/'runs/D168-worker-raw-control/execution',H/'execution']:
 for p in parent.glob('*.exit.json'):
  e=h.read(p);assert e['returncode']==0 and e['error'] is e['cleanup'] is None;checks+=1
 assert h.read(parent/'complete.json')['all_owned_children_terminal']
h.custody();D=ROOT/'comparisons/D169-root-review';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'at':h.now(),'status':'independent_log_pool_science_process_math_and_decision_replay_pass','checks':checks,'outcomes':out,'D168_retained_extents_verified':99,'D168_full_reader_report_sha256':h.sha(D168),'D168_full_raw_comparison_not_repeated':True,'D169_report_sha256':h.sha(ROOT/'comparisons/D169-worker-comparison/report.json'),'retained_log_receipt_sha256':logpins,'no_native_or_extra_timing_runs':True,'best_qualified_workers':16,'new_gain_accepted':False,'RAM20261028_original_baseline_ms':10456.4109,'matched_harness_absolute_control_not_pooled_with_original_baseline':True})
def publish(folder,names):
 for name in names:
  p=folder/name;dest=h.ar.DASHBOARD/'evidence'/folder.name/name;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert dest.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dest)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D169')
 item.update(status='rejected',stage='8/32 worker options closed; 16 remains qualified',correctness='pass_27_scored_full_records_207_checks_86_units_each',reason='8 workers +0.1019819169%, river slower 2/3; 32 workers +0.1742801228%, river slower 3/3 and CPU +23.0907457323%. Both below 1% and fail strict river guard; no extensions or variants. Independent replay passed; no gain adopted.')
 item.setdefault('evidence',[]).append({'label':'Independent full-log and decision replay','url':'evidence/D169-root-review/report.json'})
 s.update(updated_at=h.now(),stage='Worker configuration screen closed',activity='Keep accepted E080 with 16 workers. Eight and 32 workers rejected; fixed cohort retained and independently checked. Current RAM baseline remains 10.4564109 s across three fixture medians. Distinct GPU source scouting continues.')
 h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':'pass','checks':checks,'outcomes':out,'retained_extents':99}),flush=True)
