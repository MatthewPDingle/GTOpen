"""Execute one prospectively frozen capacity/holdout/cumulative package. No adoption."""
import importlib.util,json,os,re,shutil,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
H=ROOT/'runs/E051-remaining-native-plan-r2';E=ROOT/'runs/E051-remaining-native-execution-r2';O=ROOT/'comparisons/E051-remaining-native-r2'
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
spec=importlib.util.spec_from_file_location('holdout_codec',P['codec']);codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
def stage(label):
 with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
  st=old.read(old.ar.STATUS);st.update(updated_at=old.now(),stage='E051 remaining qualification',activity=label)
  e=next(x for x in st['experiments'] if x['id']=='E051');e.update(stage=label,status='preparing',accepted=False)
  old.ar.atomic_json(old.ar.STATUS,st)
def native(label,binary,args,environment,timeout):
 verify();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=52*1024**3
 out=E/label;out.mkdir();stage(label)
 with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  old.child([binary]+args,out,'native',environment,timeout)
 verify();return out
def markers(path,tag):return codec.markers(path,tag)
def holdout(out,raw):
 log=out/('native.stdout.log' if (out/'native.stdout.log').exists() else 'stdout.log');codec.native_pass(log,'postflop_wide_turn_holdout')
 results=markers(log,'AUTORESEARCH_RESULT');assert len(results)==1;r=results[0]
 assert r['fixture_id']=='wide-turn-full169' and r['iteration']==120 and r['target_met'] is True
 assert r['target_pct']==0.3 and r['check_every']==20 and r['max_iterations']==400
 assert r['config']==old.read(P['holdout_fixture']) and r['algorithm']=='Dcfr' and r['storage']=='compressed' and r['use_isomorphism'] is True
 assert r['nodes']==9387 and all(r[k]>0 for k in ['build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms'])
 assert r['full_cycle_ms']>=sum(r[k] for k in ['build_ms','init_ms','solve_ms','readback_ms'])
 stages=markers(log,'AUTORESEARCH_STAGE');checks=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check']
 assert [x['iteration'] for x in checks]==list(range(20,121,20))
 layout=codec.raw_layout(raw,r)
 return {'non_timing':{k:v for k,v in r.items() if k not in codec.TIMINGS},'checks':checks,'full_cycle_ms':r['full_cycle_ms'],'raw':layout,'stdout_sha256':old.sha(log)}
verify();assert not E.exists() and not O.exists() and not (ROOT/'gpu-run.lock').exists();E.mkdir();O.mkdir()
for p in P['cumulative_order']:assert not (ROOT/'runs'/p).exists()
try:
 capacity=old.read(ROOT/'comparisons/E051-remaining-native/capacity.json')
 assert capacity['status']=='pass_exact_actual_owned_accounting'
 old.save(O/'capacity.json',capacity)
 historical=Path(P['historical_holdout']);anchor=holdout(historical,Path(P['historical_raw']))
 rows={};first=None
 for identity in P['holdout_order']:
  arm=P['holdout_arms'][identity];binary=P['binaries']['holdout-'+arm];raw=E/(identity+'.raw');assert not raw.exists()
  env=old.env()
  for key in ['POSTFLOP_AUTORESEARCH_FIXTURE','POSTFLOP_AUTORESEARCH_STORAGE','POSTFLOP_AUTORESEARCH_PROFILE']:env.pop(key,None)
  env['POSTFLOP_HOLDOUT_STATE']=str(raw)
  out=native(identity,binary['path'],['postflop_wide_turn_holdout','--ignored','--nocapture','--test-threads=1'],env,600)
  row=holdout(out,raw);assert row['non_timing']==anchor['non_timing'] and row['checks']==anchor['checks']
  # Hash plus full streaming comparison, all q/scales and framing included.
  assert codec.binary_equal(raw,Path(P['historical_raw']))
  if first is None:first=raw
  assert codec.binary_equal(raw,first);rows[identity]=row
  old.save(out/'parsed.json',row);print('Holdout completed',identity,flush=True)
 b=[rows[x['baseline']]['full_cycle_ms'] for x in P['holdout_pairs']];c=[rows[x['candidate']]['full_cycle_ms'] for x in P['holdout_pairs']]
 bm,cm=statistics.median(b),statistics.median(c);slow=(cm/bm-1)*100;paired=[(y/x-1)*100 for x,y in zip(b,c)];guard=slow>0 and sum(x>0 for x in paired)>=2
 old.save(O/'holdout.json',{'at':old.now(),'status':'rejected_repeatable_holdout_slowdown' if guard else 'pass_fixed_holdout_nonregression','baseline_ms':b,'candidate_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'observed_gain_pct':(1-cm/bm)*100,'median_slowdown_pct':slow,'paired_slowdown_pct':paired,'strict_guard_failed':guard,'results_exact':6,'checkpoints_exact':36,'full_raw_files_exact':6,'historical_timing_pooled':False,'rows':rows,'candidate_accepted':False})
 if guard:
  old.save(E/'complete.json',{'at':old.now(),'status':'rejected_holdout','cumulative_not_executed':True,'all_children_terminal':True,'candidate_accepted':False});stage('Rejected: repeatable wide-turn holdout slowdown');sys.exit(0)
 # Fresh original-to-candidate complete-cycle cohort, fixed before any outcome.
 reports={};anchor_primary=old.exact_raw('E020C1');environment=None;gpu=None
 for identity in P['cumulative_order']:
  verify();stage('Fresh original comparison '+identity);arm=P['cumulative_arms'][identity];binary=P['binaries']['original' if arm=='baseline' else 'primary-candidate']
  command=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','E051 fresh original '+identity,'--kind',arm,'--binary',binary['path'],'--build-manifest',binary['manifest'],'--test','postflop_complete_cycle']
  old.child(command,E,identity,old.env(),1200);verify();r=old.read(ROOT/'runs'/identity/'report.json');old.compare.validate_run(r,{})
  assert r['binary_sha256']==binary['sha256'] and r['binary_build_manifest']['sha256']==binary['manifest_sha256'] and old.exact_raw(identity)==anchor_primary
  if environment is None:environment=r['environment'];gpu=old.compare.gpu_identity(r)
  assert r['environment']==environment and old.compare.gpu_identity(r)==gpu;reports[identity]=r
 pairs=P['cumulative_pairs'];summary=old.compare.summarize([reports[x['baseline']] for x in pairs],[reports[x['candidate']] for x in pairs],old.BASE)
 bs=sum(f['baseline']['full_cycle_ms']['median_ms'] for f in summary['fixtures']);cs=sum(f['candidate']['full_cycle_ms']['median_ms'] for f in summary['fixtures']);gain=old.compare.gain(bs,cs);guards=[]
 for f in summary['fixtures']:
  slow=[-p['fixture_gain_pct'][f['fixture_id']] for p in summary['pairs']];median_slow=-f['observed_gain_pct'];guards.append({'fixture_id':f['fixture_id'],'median_slowdown_pct':median_slow,'paired_slowdown_pct':slow,'slower_pairs':sum(x>0 for x in slow),'failed':median_slow>0 and sum(x>0 for x in slow)>=2})
 passed=gain>=1 and not any(x['failed'] for x in guards)
 summary['performance']={'aggregation':'Unrounded sum of fixed three per-fixture medians; fresh original comparison','baseline_full_cycle_ms':bs,'candidate_full_cycle_ms':cs,'observed_gain_pct':gain,'required_gain_pct':1.0,'aggregate_gate_met':gain>=1.0,'fixture_regression_guard':guards,'passed':passed,'statistical_significance_established':False}
 summary.update(at=old.now(),status='pass_fresh_original_cumulative' if passed else 'rejected_cumulative',baseline_full_cycle_ms=bs,candidate_full_cycle_ms=cs,observed_gain_pct=gain,required_gain_pct=1.0,strict_fixture_guards=guards,full_non_timing_results_exact=18,checkpoints_exact=138,historical_timing_samples_used=0,candidate_accepted=False,statistical_significance_established=False)
 old.save(O/'cumulative.json',summary)
 verify();old.save(E/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'status':'pass_remaining_pending_root_replay' if passed else 'rejected_cumulative','capacity_cases_each':6,'holdout_order':P['holdout_order'],'cumulative_order':P['cumulative_order'],'all_children_terminal':True,'candidate_accepted':False,'reports_sha256':{str(p):old.sha(p) for p in O.glob('*.json')}})
 stage('Remaining gates terminal; root replay pending');print('E051 remaining gates terminal; no source adoption.',flush=True)
except BaseException as exc:
 if isinstance(exc,SystemExit):raise
 old.save(E/'failure.json',{'at':old.now(),'error':repr(exc),'candidate_accepted':False});raise
