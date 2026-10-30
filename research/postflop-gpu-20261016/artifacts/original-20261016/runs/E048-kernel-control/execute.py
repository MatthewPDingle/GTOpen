"""E048 one-shot direct up_action comparison, serialized and immutable."""
import json,shutil,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2
old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
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
 finally:
  old.save(OUT/(label+'.exit.json'),{'at':old.now(),'started_at':started,'command':cmd,'returncode':proc.returncode if proc else None,'error':fault,'cleanup':cleanup})
 assert proc.returncode==0,(label,(OUT/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])


with old.ar.exclusive_lock(old.ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(old.ROOT).free>=54*1024**3
 assert not OUT.exists() and not (HERE/'probe.exe').exists() and not Path(P['raw_output']).exists();OUT.mkdir()
 assert old.read(P['resource_report'])['status']=='pass_resource_feasibility_only'
 old.save(OUT/'before.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'all_inputs_verified':True,'accepted162_unchanged':True})
 env=old.env();child(P['rustc_command'],'rustc',env,180);old.custody()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 binary=HERE/'probe.exe';data=binary.read_bytes();assert all((HERE/(v+'.ptx')).read_bytes() in data for v in ['baseline','candidate'])
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(binary),'exact_ptx_embedded':True,'rustc_terminal':True,'native_executions':0})
 env['E048_CONTROL_DIR']=P['raw_output'];child([str(binary)],'probe',env,300);old.custody()
 raw=(OUT/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E048_CONTROL ',1)[1]) for x in raw.splitlines() if 'E048_CONTROL ' in x]
 corpus=old.read(HERE/'corpus.json');cases=corpus['cases'];assert len(markers)==len(cases)+1
 for c,m in zip(cases,markers[:-1]):assert m['stage']=='case' and m['id']==c['id'] and m['descriptor']==c['descriptor'] and m['full_outputs_exact'] and m['actual_immutable_inputs_exact'] and m['guards_exact']
 end=markers[-1];assert end['stage']=='complete' and end['cases']==len(cases) and end['kernel_launches']==2*len(cases) and end['full_outputs_exact'] and end['actual_immutable_inputs_exact']
 assert (OUT/'probe.stderr.log').read_bytes()==b''
 rawdir=Path(P['raw_output']);files={str(p):old.sha(p) for p in rawdir.iterdir()};assert len(files)==3 and sum(p.stat().st_size for p in rawdir.iterdir())<=corpus['max_raw_bytes']
 old.save(OUT/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'source_review_sha256':old.sha(HERE/'source-review.json'),'binary_sha256':old.sha(binary),'raw_marker_summary':end,'raw_file_sha256':files,'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'all_children_terminal':True,'accepted162_main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False})
 print(json.dumps({'summary':end,'complete_sha256':old.sha(OUT/'complete.json')},indent=2),flush=True)
