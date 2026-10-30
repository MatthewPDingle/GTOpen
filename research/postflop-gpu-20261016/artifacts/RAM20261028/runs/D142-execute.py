import sys,json,math,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D142-profile-plan';P=h.read(H/'protocol-r2.json')
def verify():
 h.pin(H/'protocol-r2.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();assert not(ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.ar.refuse_active(h.ar.live_status())
O=ROOT/'runs/D142-profile-execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'epoch-sequence.lock'):
 h.child(P['command'],O,'profile',1200);verify()
 r=h.read(ROOT/'runs/D142R1/report.json');assert r['status']=='measured'and r['returncode']==0 and r['environment']['POSTFLOP_AUTORESEARCH_PROFILE']=='1'
 assert h.exact('D142R1')==h.read(h.EPOCH/'exact-anchor.json')
 stages=[x['data']for x in r['stages']if x['data'].get('stage')=='diagnostic_profile'];assert[x['fixture_id']for x in stages]==['rainbow','two-tone','river']
 rows=[]
 for x in stages:
  assert x['iteration']==(61 if x['fixture_id']=='river' else 201)and x['excluded_from_score']is True
  assert x['kernel_names']==['copy_root','down_action','down_chance','up_fold','up_show','up_chance','up_action']and len(x['profile_ms'])==len(x['launches'])==7
  assert all(math.isfinite(t)and t>=0 for t in x['profile_ms'])and all(type(n)is int and n>=0 for n in x['launches'])
  total=sum(x['profile_ms']);families=[{'name':name,'wall_ms_including_sync':ms,'launches':n,'fraction_of_instrumented_wall':ms/total}for name,ms,n in zip(x['kernel_names'],x['profile_ms'],x['launches'])]
  rows.append({'fixture_id':x['fixture_id'],'instrumented_iteration':x['iteration'],'families':families,'instrumented_wall_ms':total,'total_launches':sum(x['launches'])})
 D=ROOT/'comparisons/D142-profile';D.mkdir(exist_ok=False)
 report={'id':'D142','at':h.now(),'status':'pass_finite_diagnostic','measurement_epoch':'RAM20261028','accepted_source':'E080','protocol_sha256':sys.argv[1],'native_report_sha256':h.sha(ROOT/'runs/D142R1/report.json'),'raw_log_sha256':r['stdout_sha256'],'full_results_exact':3,'convergence_checkpoints_exact':23,'fixtures':rows,'candidate_source_changed':False,'performance_gain_claimed':False,'hardware_counters_used':False,'scope':'One extra instrumented training iteration after each fully scored and fingerprinted solve. Wall times include synchronization after every family launch and omit normal captured-graph scheduling. No CUDA-event/device-only measurement, absolute speed, whole-cycle gain, evaluation-family attribution or statistical confidence claim. Family observations only guide source review; no reopening E090 or closed mechanisms.'}
 h.save(D/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'protocol_sha256':sys.argv[1],'report_sha256':h.sha(D/'report.json'),'source_main_live_PTX_custody_pass':True})
pub=[]
for folder,prefix in[(D,D.name),(O,O.name)]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key=prefix+'/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='D142');x.update(status='measured',stage='Source review guided by fresh profile',correctness='pass',reason='Fresh E080 profile completed after exact solves. One extra synchronized iteration per fixture provides family observations; instrumented times do not establish production kernel cost or speedup. E090 remains rejected.');x.setdefault('evidence',[]).append({'label':'Fresh diagnostic profile','url':'evidence/D142-profile/report.json'})
 s.update(updated_at=h.now(),stage='Reviewing a new performance mechanism',active_experiment='D142',activity='The new RAM baseline is complete. E090 was exact but rejected for a 0.777% gain and a river slowdown. Fresh E080 profiling now guides the next independent source review.');h.ar.atomic_json(h.ar.STATUS,s)
h.save(O/'publication.json',{'at':h.now(),'HTTP_verified_artifacts':pub,'all_owned_children_terminal':True})
h.custody();print(json.dumps({'status':report['status'],'fixtures':rows}),flush=True)
