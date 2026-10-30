import sys,json,statistics,datetime,shutil,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import common as h
assert len(sys.argv)==2;h.pin(h.EPOCH/'baseline-protocol.json',sys.argv[1]);P=h.read(h.EPOCH/'baseline-protocol.json')
h.custody();O=h.ROOT/'runs/RAM20261028-execution';done=h.read(O/'complete.json')
assert done['protocol_sha256']==sys.argv[1]and done['all_owned_children_terminal']
scored=[x['id']for x in P['sequence']if x['scored']];assert len(scored)==5
reports={};previous=None;pins={}
for item in P['sequence']:
 ident=item['id'];receipt=h.read(O/(ident+'.exit.json'));assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
 start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at'])
 assert start<=end and(previous is None or previous<=start);previous=end
 r=h.read(h.ROOT/'runs'/ident/'report.json');assert r['status']=='measured'and r['returncode']==0
 for p in [O/(ident+'.exit.json'),h.ROOT/'runs'/ident/'report.json',h.ROOT/'runs'/ident/'stdout.log']:pins[str(p)]=h.sha(p)
 if not item['unit']:assert h.exact(ident)==h.read(h.EPOCH/'exact-anchor.json')
 if item['scored']:reports[ident]=r
fixtures=[]
for i,name in enumerate(['rainbow','two-tone','river']):
 values=[reports[ident]['results'][i]for ident in scored]
 row={'fixture_id':name,'raw_full_cycle_ms':[x['full_cycle_ms']for x in values],'median_full_cycle_ms':statistics.median(x['full_cycle_ms']for x in values),'min_full_cycle_ms':min(x['full_cycle_ms']for x in values),'max_full_cycle_ms':max(x['full_cycle_ms']for x in values),'median_solve_ms':statistics.median(x['solve_ms']for x in values),'fingerprint':values[0]['fingerprint'],'all_full_non_timing_states_and_stops_exact':True}
 fixtures.append(row)
aggregate=sum(x['median_full_cycle_ms']for x in fixtures)
suite_raw=[sum(x['full_cycle_ms']for x in reports[ident]['results'])for ident in scored]
D=h.ROOT/'comparisons/RAM20261028-baseline';D.mkdir(exist_ok=False)
report={'id':'RAM20261028-baseline','at':h.now(),'status':'pass_current_hardware_baseline','measurement_epoch':'RAM20261028','configuration':'Accepted E080, GPU, compressed CPU storage, Rayon16, unchanged quality/stopping/evaluator/workloads','protocol_sha256':sys.argv[1],'binary_sha256':P['baseline_binary_sha256'],'scored_runs':scored,'prespecified_warmup_runs':[x['id']for x in P['sequence']if not x['unit']and not x['scored']],'scored_run_count':5,'aggregate_ms':aggregate,'aggregation':'Unrounded sum of five-observation per-fixture complete-cycle medians','raw_serialized_suite_ms':suite_raw,'median_serialized_suite_ms':statistics.median(suite_raw),'fixtures':fixtures,'unit_passed':86,'unit_ignored':4,'scored_exact_full_results':15,'scored_exact_checkpoints':115,'all_six_processes_exact_results':18,'all_six_processes_exact_checkpoints':138,'hardware_inventory':h.read(h.EPOCH/'hardware.json'),'all_new_outputs_physically_on_X':True,'historical_timing_samples_scored':0,'excluded_scored_samples':[],'extension_runs':0,'new_optimizer_gain_claimed':False,'RAM_causal_speedup_claimed':False,'historical_14_7414pct_gain_is_prior_epoch_only':True,'evidence_sha256':pins,'limits':'A fresh baseline of the best already accepted configuration under the user changed RAM timings and current machine/storage state. Five retained observations describe timing variability; no statistical confidence or causal RAM-only attribution. Future optimization comparisons require fresh matched controls from this epoch and the unchanged 1%/fixture/fresh16/broad/material/holdout/cumulative gates. Native complete cycles include build/allocation/GPU init/JIT/quality solve/checks/full readback; Cargo, fingerprints, final destruction, saving and browser latency remain excluded.'}
h.save(D/'report.json',report)
pub=[]
for p in [D/'report.json',O/'complete.json',h.EPOCH/'hardware.json']:
 key='RAM20261028-baseline/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);current=s['current_hardware_baseline'];current.update(status='measured',measured_at=h.now(),aggregate_ms=aggregate,scored_runs=scored,repetitions=5,binary_sha256=P['baseline_binary_sha256'],correctness='pass')
 for f,row in zip(current['fixtures'],fixtures):
  assert f['id']==row['fixture_id']
  f['baseline']={'full_cycle_ms':row['median_full_cycle_ms'],'solve_ms':row['median_solve_ms'],'fingerprint':row['fingerprint'],'repetitions':5,'provisional':False}
  f['best']={'status':'accepted','candidate_id':'E080','full_cycle_ms':row['median_full_cycle_ms'],'solve_ms':row['median_solve_ms'],'fingerprint':row['fingerprint']}
  f['correctness']={'status':'pass','details':'All five fresh full results, stopping iterations and convergence checkpoints match the unchanged reference.'}
 s['measurement_epoch']['status']='baseline_complete';s['measurement_epoch']['baseline_ms']=aggregate
 s['evidence'].append({'label':'Fresh E080 baseline after RAM changes','url':'evidence/RAM20261028-baseline/report.json','detail':'Five measurements on X; earlier RAM timing cohorts are historical.'})
 for item in P['sequence']:
  x=next(x for x in s['experiments']if x['id']==item['id']);x.update(measurement_epoch_id='RAM20261028',correctness='pass',reason='86 ordinary tests passed.'if item['unit']else'Full results and all 23 checkpoints match the unchanged reference. '+('Prespecified warm-up; not scored.'if not item['scored']else'Included in the five-run baseline.'))
 s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E090',stage='New RAM baseline complete; resume performance research',activity=f'Fresh accepted E080 baseline: {aggregate:.4f} ms for the three-fixture suite, using five measurements on X. All exactness checks and 86 ordinary tests passed. Earlier gains remain historical; continue fresh matched optimization trials.')
 h.ar.atomic_json(h.ar.STATUS,s)
h.save(D/'publication.json',{'at':h.now(),'HTTP_verified_artifacts':pub,'source_main_live_PTX_custody_pass':True})
print(json.dumps({'status':report['status'],'aggregate_ms':aggregate,'fixtures':[{k:x[k]for k in ['fixture_id','median_full_cycle_ms','min_full_cycle_ms','max_full_cycle_ms']}for x in fixtures],'unit_passed':86,'scored_runs':5}),flush=True)
