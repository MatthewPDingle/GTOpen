"""One fixed full raw down_action comparison; no speed score."""
import json,re,shutil,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(HERE/'execution-plan.json',sys.argv[1]);P=old.read(HERE/'execution-plan.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
OUT=HERE/'execution'
def child(cmd,label,env,timeout):
 proc=None;fault=None;cleanup=None;started=old.now();clock=time.monotonic()
 old.save(OUT/(label+'.invocation.json'),{'at':started,'command':cmd,'cwd':str(OUT)})
 try:
  with (OUT/(label+'.stdout.log')).open('xb') as stdout,(OUT/(label+'.stderr.log')).open('xb') as stderr:
   proc=subprocess.Popen(cmd,cwd=OUT,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
   while True:
    try:proc.wait(timeout=10);break
    except subprocess.TimeoutExpired:
     elapsed=time.monotonic()-clock
     if elapsed>=timeout:raise TimeoutError(label)
     print(label,'running',int(elapsed),'seconds; child',proc.pid,flush=True)
 except BaseException as exc:
  fault=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(OUT/(label+'.exit.json'),{'at':old.now(),'started_at':started,'command':cmd,'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
 assert proc.returncode==0,(label,(OUT/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
with old.ar.exclusive_lock(old.ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(old.ROOT).free>=54*1024**3
 assert not OUT.exists() and not (HERE/'evidence').exists() and not (HERE/'probe.exe').exists();OUT.mkdir()
 old.save(OUT/'before.json',{'at':old.now(),'execution_plan_sha256':sys.argv[1],'application_kernel_launches_before':0,'input_sha256':P['input_sha256']})
 env=old.env();assert not {k:v for k,v in env.items() if k in {'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER'} or k.startswith('CARGO_PROFILE_RELEASE_')}
 child(P['rustc_command'],'rustc',env,180);old.custody()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(HERE/'probe.exe'),'native_numerical_executions':0})
 env['E067_DOWN_RAW_DIR']=str(HERE/'evidence');child([str(HERE/'probe.exe')],'probe',env,600);old.custody()
 markers=[json.loads(x.split('E067_DOWN_RAW ',1)[1]) for x in (OUT/'probe.stdout.log').read_text().splitlines() if x.startswith('E067_DOWN_RAW ')]
 assert len(markers)==1197 and markers[-1]['stage']=='complete';records=markers[:-1];done=markers[-1]
 assert done['cases']==1196 and done['kernel_launches']==2392 and done['all_raw_exact'] and done['all_inputs_and_guards_exact'] and [x['id'] for x in records]==list(range(1196))
 files={str(p):{'sha256':old.sha(p),'bytes':p.stat().st_size} for p in (HERE/'evidence').iterdir()};assert len(files)==5
 report={'id':'E067-kernel-control','at':old.now(),'status':'pass_scoped_down_action_full_raw_equivalence','execution_plan_sha256':sys.argv[1],'cases':1196,'kernel_launches':2392,'output_words_both_arms':done['output_words_both_arms'],'actual_immutable_words_both_arms':done['immutable_words_both_arms'],'guard_words_both_arms':done['guard_words_both_arms'],'all_full_outputs_inputs_guards_exact':True,'raw_files':files,'corpus_sha256':old.sha(HERE/'corpus.json'),'binary_sha256':old.sha(HERE/'probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'source_activated':False,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'limits':'Native full raw twooutput/twelveactualimmutablebuffers and unownedranges compared; finite declared cases, no complete solver/graph/material/speed/otherGPU proof. Root independent replay still required.'}
 old.save(HERE/'report.json',report);old.save(OUT/'complete.json',{'at':old.now(),'report_sha256':old.sha(HERE/'report.json'),'all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True})
 print(json.dumps(report),flush=True)