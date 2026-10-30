"""One no-launch E047 compiler/resource probe, direct Windows output handles."""
import hashlib,json,shutil,subprocess,sys,time
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

def entries(path):
 t=path.read_text(encoding='utf-8');out={};i=0
 while True:
  i=t.find('.visible .entry ',i)
  if i<0:break
  n=t.index('(',i);name=t[i+len('.visible .entry '):n].strip();a=t.index('{',n);j=a+1;depth=1
  while depth:
   if t[j]=='{':depth+=1
   elif t[j]=='}':depth-=1
   j+=1
  assert name not in out;out[name]=t[i:j];i=j
 return out

with old.ar.exclusive_lock(old.ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(old.ROOT).free>=54*1024**3
 assert not OUT.exists() and not (HERE/'probe.exe').exists();OUT.mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10)
 assert gpu['returncode']==0 and P['gpu_uuid'] in gpu['stdout']
 old.save(OUT/'before.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'input_sha256':P['input_sha256'],'gpu':gpu,'accepted162_unchanged':True,'cwd_previously_absent':True})
 env=old.env();forbidden={'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER'}
 assert not {k:v for k,v in env.items() if k in forbidden or k.startswith('CARGO_PROFILE_RELEASE_')}
 child(P['rustc_command'],'rustc',env,180)
 old.custody()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(HERE/'probe.exe'),'native_executions':0,'rustc_terminal':True,'source_unchanged':True})
 child([str(HERE/'probe.exe')],'probe',env,180)
 old.custody()
 raw=(OUT/'probe.stdout.log').read_text(encoding='utf-8')
 markers=[json.loads(x.split('E047_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E047_RESOURCE ' in x]
 assert len(markers)==4 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
 b,c=markers[1:3];assert b['variant']=='baseline' and c['variant']=='candidate'
 for row in [b,c]:assert row['kernel']=='up_action' and row['kernel_launches']==0 and row['performance_measurement'] is False
 be,ce=entries(OUT/'baseline.ptx'),entries(OUT/'candidate.ptx')
 assert set(be)==set(ce)==set(P['expected_entries'])
 unchanged=[n for n in be if be[n]==ce[n]]
 gates={'other8_entries_exact':set(unchanged)==set(be)-{'up_action'},'up_action_compiled_body_changed':be['up_action']!=ce['up_action'],
  'registers_not_increased':c['registers']<=b['registers'],'local_not_increased':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],
  'static_shared_not_increased':c['static_shared_bytes']<=b['static_shared_bytes'],'max_threads_not_reduced':c['max_threads']>=b['max_threads'],
  'fits_default_limits':b['fits_default_limits'] and c['fits_default_limits'],
  'occupancy_not_reduced':all(bt==ct and cn>=bn for (bt,bn),(ct,cn) in zip(b['occupancy_by_threads'],c['occupancy_by_threads'])) and len(c['occupancy_by_threads'])==3}
 gates['up_action_abi_exact']=be['up_action'].split('{',1)[0]==ce['up_action'].split('{',1)[0]
 report={'id':'E047-resource','at':old.now(),'status':'pass_resource_feasibility_only' if all(gates.values()) else 'rejected_resource_gate','protocol_sha256':sys.argv[1],'source_manifest_sha256':P['source_manifest_sha256'],'raw_markers':markers,'gates':gates,'ptx_sha256':{v:old.sha(OUT/(v+'.ptx')) for v in ['baseline','candidate']},'entry_body_sha256':{v:{n:hashlib.sha256(t.encode()).hexdigest() for n,t in d.items()} for v,d in [('baseline',be),('candidate',ce)]},'binary_sha256':old.sha(HERE/'probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'stderr_sha256':old.sha(OUT/'probe.stderr.log'),'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted162_unchanged':True,'main_live_ptx_unchanged':True,'limits':'Actual driver register/local/shared/default-limit queries and theoretical occupancy for this device/three block shapes only. No numerical kernel, runtime overlap, cold-start/capacity or speed evidence.'}
 old.save(HERE/'report.json',report)
 old.save(OUT/'complete.json',{'at':old.now(),'report_sha256':old.sha(HERE/'report.json'),'all_children_terminal':True,'accepted162_unchanged':True,'main_live_ptx_unchanged':True,'kernel_launches':0,'solver_executions':0})
 print(json.dumps({'status':report['status'],'gates':gates,'baseline':b,'candidate':c,'report_sha256':old.sha(HERE/'report.json')},indent=2),flush=True)
