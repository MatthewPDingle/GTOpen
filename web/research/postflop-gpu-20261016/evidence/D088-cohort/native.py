"""One frozen matched constructor-observer cohort; never an optimization gate."""
import json,math,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');E=H/'execution'
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify();assert not E.exists() and not (ROOT/'gpu-run.lock').exists();E.mkdir()
reference=old.historical.exact_raw('E020C1');anchor=(reference[0][0],[c for c in reference[1] if c['fixture_id']=='rainbow']);reports={};outer={};profiles={}
try:
 for identity in P['order']:
  verify();old.ar.refuse_active(old.ar.live_status());arm='diagnostic' if identity.startswith('D088T') else 'baseline';binary=P['binaries'][arm]
  env=old.env()
  for name in ['D085_TRACE_FILE','D085_META_FILE','D087_TRACE_FILE','D087_META_FILE']:env.pop(name,None)
  assert not env.get('CUDA_INJECTION64_PATH') and not env.get('CUDA_INJECTION32_PATH')
  command=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','D088 '+identity,'--kind','diagnostic','--binary',binary['path'],'--build-manifest',binary['manifest'],'--test','postflop_complete_cycle','--fixture','rainbow']
  started=time.monotonic();old.child(command,E,identity,env,1200);outer[identity]=(time.monotonic()-started)*1000;old.save(E/(identity+'.outer-wall.json'),{'elapsed_ms':outer[identity]});verify()
  report=old.read(ROOT/'runs'/identity/'report.json');log=ROOT/'runs'/identity/'stdout.log';old.pin(log,report['stdout_sha256']);assert report['status']=='measured' and report['returncode']==0 and report['binary_sha256']==binary['sha256'] and report['binary_build_manifest']['sha256']==binary['manifest_sha256']
  raw=log.read_text();values=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_RESULT ' in x];assert values==report['results'] and len(values)==1
  stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in raw.splitlines() if 'AUTORESEARCH_STAGE ' in x];checks=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check']
  assert ({k:v for k,v in values[0].items() if k not in old.historical.EXCLUDED},checks)==anchor;reports[identity]=report
  stderr=(ROOT/'runs'/identity/'stderr.log').read_text();events=[]
  for line in stderr.splitlines():
   if line.startswith('D088_INIT '):events.append(('init',json.loads(line[len('D088_INIT '):])))
   elif line.startswith('D088_ZERO '):events.append(('zero',json.loads(line[len('D088_ZERO '):])))
  if arm=='baseline':assert not events
  else:
   expected=[]
   for stage in P['outer_stages']:
    if stage.endswith('_upload'):expected.append(('zero',0 if stage.startswith('regret') else 1))
    expected.append(('init',stage))
   assert [(kind,row['stage'] if kind=='init' else row['which']) for kind,row in events]==expected
   assert all(math.isfinite(row['elapsed_ms']) and row['elapsed_ms']>=0 for _,row in events)
   outer_values={row['stage']:row['elapsed_ms'] for kind,row in events if kind=='init'};zero_values=[row for kind,row in events if kind=='zero'];assert len(outer_values)==12 and len(zero_values)==4 and all(row['positive_zero'] is True for row in zero_values)
   for stage,row in zip(['regret0_upload','regret1_upload','strategy0_upload','strategy1_upload'],zero_values):assert row['elapsed_ms']<=outer_values[stage]+1e-6
   total=sum(outer_values.values());assert total<=values[0]['init_ms']+1e-6
   profiles[identity]={'outer_stages_ms':outer_values,'nested_zero_scans':zero_values,'accounted_outer_ms':total,'enclosing_gpu_init_ms':values[0]['init_ms'],'unattributed_init_ms':values[0]['init_ms']-total,'full_event_order':events,'stderr_sha256':old.sha(ROOT/'runs'/identity/'stderr.log'),'limits':'Nested scan spans are part of enclosing upload stages; never add them. Unattributed time includes timer/logging boundaries, local drops and final sync outside constructor markers.'}
   old.save(E/(identity+'.profile.json'),profiles[identity])
  print('D088 completed',identity,flush=True)
 pairs=[]
 for pair in P['pairs']:
  b,t=reports[pair['baseline']],reports[pair['diagnostic']];changes={'cycle_change_pct':100*(t['results'][0]['full_cycle_ms']/b['results'][0]['full_cycle_ms']-1),'init_change_pct':100*(t['results'][0]['init_ms']/b['results'][0]['init_ms']-1),'native_change_pct':100*(t['process_wall_ms']/b['process_wall_ms']-1),'runner_change_pct':100*(outer[pair['diagnostic']]/outer[pair['baseline']]-1)}
  pairs.append(pair|changes|{'usefulness_pass':all(abs(v)<=10 for v in changes.values())})
 passed=all(p['usefulness_pass'] for p in pairs)
 old.save(H/'report.json',{'at':old.now(),'status':'pass_scoped_constructor_diagnostic' if passed else 'observer_gate_failed','protocol_sha256':sys.argv[1],'pairs':pairs,'profiles':profiles,'all6full_states_60checkpoints_exact':True,'observer_usefulness_pass':passed,'all_samples_retained':True,'historical_timing_samples_used':0,'excluded_samples':[],'extension_runs':0,'optimization_accepted':False,'accepted_source':'E051','limits':P['limits']})
 old.save(E/'complete.json',{'at':old.now(),'all_children_terminal':True,'order':P['order'],'report_sha256':old.sha(H/'report.json'),'accepted_source_restored':True});print(json.dumps({'status':'cohort_terminal','observer_pass':passed,'pairs':pairs,'report_sha256':old.sha(H/'report.json')}),flush=True)
except BaseException as exc:
 old.save(E/'failure.json',{'at':old.now(),'error':repr(exc),'completed_ids':list(reports),'optimization_accepted':False});raise
