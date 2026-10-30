"""E047 one-shot direct up_action comparison, serialized and immutable."""
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
 env=old.env();child(P['rustc_command'],'rustc',env,180)
 old.custody()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 binary=HERE/'probe.exe';data=binary.read_bytes()
 assert (HERE/'baseline.ptx').read_bytes() in data and (HERE/'candidate.ptx').read_bytes() in data
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(binary),'native_executions':0,'exact_ptx_embedded':True,'rustc_terminal':True})
 env['E047_KERNEL_CONTROL_DIR']=P['raw_output'];child([str(binary)],'probe',env,180)
 old.custody()
 raw=(OUT/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E047_UNIT ',1)[1]) for x in raw.splitlines() if 'E047_UNIT ' in x]
 corpus=old.read(HERE/'corpus.json')['cases'];assert len(markers)==820
 for c,m in zip(corpus,markers[:-1]):
  assert m['stage']=='case' and all(m[k]==c[k] for k in ['id','hands','actions','threads','p','role','algorithm','iteration','value_mode','count','discount_bits'])
  assert m['all_raw_exact'] and m['guards_exact']
 end=markers[-1];assert end['stage']=='complete' and end['cases']==819 and end['kernel_launches']==1638 and end['all_raw_exact'] and end['all_inputs_and_guards_exact'] and end['raw_device_inputs_retained_both_arms']
 assert (OUT/'probe.stderr.log').read_bytes()==b''
 rawdir=Path(P['raw_output']);files={str(p):old.sha(p) for p in rawdir.iterdir()};assert len(files)==5
 assert sum(p.stat().st_size for p in rawdir.iterdir())<2*1024**3
 old.save(OUT/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'source_review_sha256':old.sha(HERE/'source-review.json'),'binary_sha256':old.sha(binary),'raw_marker_summary':end,'raw_file_sha256':files,'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'all_children_terminal':True,'accepted162_unchanged':True,'main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False})
 print(json.dumps({'summary':end,'complete_sha256':old.sha(OUT/'complete.json')},indent=2),flush=True)
