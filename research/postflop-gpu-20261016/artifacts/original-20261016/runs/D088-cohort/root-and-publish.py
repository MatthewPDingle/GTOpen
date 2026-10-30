"""Raw constructor marker and four-clock observer replay by the root agent."""
import datetime,json,math,statistics,sys,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
P=old.read(H/'protocol.json');q=old.read(H/'report.json');E=H/'execution';done=old.read(E/'complete.json');assert done['all_children_terminal'] and done['report_sha256']==old.sha(H/'report.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
checks=[]
def ck(label,v):checks.append({'label':label,'passed':bool(v)});assert v,label
def near(a,b):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8)
reference=old.historical.exact_raw('E020C1');anchor=reference[0][0];trajectory=[r for r in reference[1] if r['fixture_id']=='rainbow'];reports={};last=None;rawpins={};profiles={}
for identity in P['order']:
 d=ROOT/'runs'/identity;r=old.read(d/'report.json');stdout=d/'stdout.log';stderr=d/'stderr.log';old.pin(stdout,r['stdout_sha256']);raw=stdout.read_text()
 values=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_RESULT ' in x];ck(identity+' all non-timing state',values==r['results'] and len(values)==1 and {k:v for k,v in values[0].items() if k not in old.historical.EXCLUDED}==anchor)
 stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_STAGE ' in x];cs=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check'];ck(identity+' all ten checkpoints',cs==trajectory and len(cs)==10)
 receipt=old.read(E/(identity+'.exit.json'));a=datetime.datetime.fromisoformat(receipt['started_at']);b=datetime.datetime.fromisoformat(receipt['finished_at']);ck(identity+' serial terminal0',receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None and a<=b and (last is None or last<=a));last=b
 ck(identity+' accepted sources restored',r['provenance']['source_sha256']==old.BASE);reports[identity]=r
 events=[]
 for line in stderr.read_text().splitlines():
  if line.startswith('D088_INIT '):events.append(('init',json.loads(line[10:])))
  elif line.startswith('D088_ZERO '):events.append(('zero',json.loads(line[10:])))
 if identity.startswith('D088B'):ck(identity+' no diagnostic markers',not events)
 else:
  expected=[]
  for label in P['outer_stages']:
   if label.endswith('_upload'):expected.append(('zero',0 if label.startswith('regret') else 1))
   expected.append(('init',label))
  ck(identity+' exact actual marker order',[(kind,x['stage'] if kind=='init' else x['which']) for kind,x in events]==expected)
  ck(identity+' finite positive timings',all(math.isfinite(x['elapsed_ms']) and x['elapsed_ms']>=0 for _,x in events))
  times={x['stage']:x['elapsed_ms'] for kind,x in events if kind=='init'};zero=[x for kind,x in events if kind=='zero'];ck(identity+' exactly12outer4scans',len(times)==12 and len(zero)==4 and all(x['positive_zero'] is True for x in zero))
  ck(identity+' nested scans contained',all(x['elapsed_ms']<=times[label]+1e-6 for x,label in zip(zero,['regret0_upload','regret1_upload','strategy0_upload','strategy1_upload'])))
  total=sum(times.values());declared=q['profiles'][identity];ck(identity+' enclosing init/accounting',total<=r['results'][0]['init_ms'] and declared['outer_stages_ms']==times and declared['nested_zero_scans']==zero and near(total,declared['accounted_outer_ms']) and near(r['results'][0]['init_ms']-total,declared['unattributed_init_ms']))
  ck(identity+' event images match retained profile',json.loads(json.dumps(events))==declared['full_event_order'] and old.sha(stderr)==declared['stderr_sha256'])
  profiles[identity]={'outer_stages_ms':times,'nested_zero_scans_ms':[x['elapsed_ms'] for x in zero],'zero_scan_sum_ms':sum(x['elapsed_ms'] for x in zero),'outer_sum_ms':total,'unattributed_init_ms':r['results'][0]['init_ms']-total,'enclosing_gpu_init_ms':r['results'][0]['init_ms']}
 for p in [d/'report.json',stdout,stderr,E/(identity+'.exit.json'),E/(identity+'.outer-wall.json')]:rawpins[str(p)]=old.sha(p)
observers=[]
for pair,declared in zip(P['pairs'],q['pairs']):
 b,t=reports[pair['baseline']],reports[pair['diagnostic']];changes={'cycle_change_pct':100*(t['results'][0]['full_cycle_ms']/b['results'][0]['full_cycle_ms']-1),'init_change_pct':100*(t['results'][0]['init_ms']/b['results'][0]['init_ms']-1),'native_change_pct':100*(t['process_wall_ms']/b['process_wall_ms']-1),'runner_change_pct':100*(old.read(E/(pair['diagnostic']+'.outer-wall.json'))['elapsed_ms']/old.read(E/(pair['baseline']+'.outer-wall.json'))['elapsed_ms']-1)}
 ck(pair['diagnostic']+' four raw observer clocks',all(near(v,declared[k]) for k,v in changes.items()));passed=all(abs(v)<=10 for v in changes.values());ck(pair['diagnostic']+' preset observer decision',passed==declared['usefulness_pass']);observers.append(passed)
passed=all(observers);ck('complete observer rule',passed==q['observer_usefulness_pass'] and q['status']==('pass_scoped_constructor_diagnostic' if passed else 'observer_gate_failed'))
ck('no exclusions or extensions or pooling',q['excluded_samples']==[] and q['extension_runs']==0 and q['historical_timing_samples_used']==0)
median_stages=[{'stage':label,'median_ms':statistics.median(v['outer_stages_ms'][label] for v in profiles.values()),'raw_ms':[v['outer_stages_ms'][label] for v in profiles.values()]} for label in P['outer_stages']];median_stages.sort(key=lambda x:x['median_ms'],reverse=True)
R=ROOT/'comparisons/D088-constructor-root-check';R.mkdir();report={'at':old.now(),'status':'pass_scoped_constructor_diagnostic' if passed else 'observer_gate_failed_diagnostic_only','checks':checks,'checks_passed':len(checks),'native_results_exact':6,'convergence_checkpoints_exact':60,'observer_usefulness_pass':passed,'observer_changes':q['pairs'],'median_stages':median_stages,'median_nested_zero_scan_sum_ms':statistics.median(v['zero_scan_sum_ms'] for v in profiles.values()),'median_outer_sum_ms':statistics.median(v['outer_sum_ms'] for v in profiles.values()),'median_unattributed_init_ms':statistics.median(v['unattributed_init_ms'] for v in profiles.values()),'profiles':profiles,'preserved_raw_sha256':rawpins,'cohort_report_sha256':old.sha(H/'report.json'),'accepted_source':'E051','accepted_cumulative_gain_unchanged':12.4372274192464,'optimization_accepted':False,'root_external_independent_review':False,'limits':P['limits']+' Individual medians do not sum to a median complete cycle. No optimizer admitted by this diagnostic alone.'};old.save(R/'report.json',report);old.custody()
published={}
directories=[(H,H.name),(R,R.name),(ROOT/'runs/D088-source','D088-source'),(ROOT/'runs/D088-build-plan','D088-build-plan'),(ROOT/'runs/D088-final-build','D088-final-build')]+[(ROOT/'runs'/i,i) for i in P['order']]
for directory,prefix in directories:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.dll','.pdb','.obj','.lib','.exp'] or '__pycache__' in src.parts:continue
  key=prefix+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data,key
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(R/'publication.json',{'at':old.now(),'http_byte_verified_files':len(published),'artifact_sha256':published,'accepted_source_unchanged':True})
links=[{'label':'D088 constructor markers and four observer clocks','url':'evidence/'+R.name+'/report.json'},{'label':'D088 complete fixed matched results','url':'evidence/'+H.name+'/report.json'}]
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='D088');e.update(status='measured' if passed else 'rejected',stage='Constructor diagnostic validated' if passed else 'Observer gate failed',correctness='pass',accepted=False,reason='All6states/60checks exact;12outer and4nested zero scan markers replay. '+('All complete/init/native/runner clock changes pass10%in everypair.' if passed else 'Diagnostic observer gate failed; no native stage cost inference.'));e['evidence'] +=links;st['evidence'] +=links;st.update(state='running',updated_at=old.now(),stage='D088 measured; review dominant constructor stages',activity='AcceptedE051 remains12.437227%cumulative; constructor observations guide source investigation without adopting a performance change.',active_experiment=None);old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'status':report['status'],'checks':len(checks),'median_stages':median_stages,'median_nested_zero_scan_sum_ms':report['median_nested_zero_scan_sum_ms'],'median_unattributed_init_ms':report['median_unattributed_init_ms'],'published':len(published),'report_sha256':old.sha(R/'report.json')}),flush=True)
