"""One no-launch E060 compiler/resource probe, direct Windows output handles."""
import hashlib,json,re,shutil,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'accepted-E051'));import common_e051 as old
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
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid'] in gpu['stdout']
 old.save(OUT/'before.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'input_sha256':P['input_sha256'],'gpu':gpu,'accepted162_unchanged':True})
 env=old.env();assert not {k:v for k,v in env.items() if k in {'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER'} or k.startswith('CARGO_PROFILE_RELEASE_')}
 child(P['rustc_command'],'rustc',env,180);old.custody()
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(HERE/'probe.exe'),'native_executions':0,'rustc_terminal':True})
 child([str(HERE/'probe.exe')],'probe',env,180);old.custody()
 raw=(OUT/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E060_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E060_RESOURCE ' in x]
 assert len(markers)==4 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert set(rows)=={(v,k) for v in ['baseline','candidate'] for k in P['changed_entries']}
 be,ce=entries(OUT/'baseline.ptx'),entries(OUT/'candidate.ptx');assert set(be)==set(ce)==set(P['expected_entries'])
 unchanged=[k for k in be if be[k]==ce[k]];gates={'other8_entries_exact':set(unchanged)==set(be)-set(P['changed_entries'])};details={};abi={}
 for k in P['changed_entries']:
  b,c=rows['baseline',k],rows['candidate',k]
  assert all(r['kernel_launches']==0 and r['performance_measurement'] is False for r in [b,c])
  sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_admission import evaluate_pair
  admission=evaluate_pair(b,c,old.read(P['allocation_proof']['path']))
  kg={'changed_body':be[k]!=ce[k],**admission['gates']}

  abi[k]={}
  for variant,table in [('baseline',be),('candidate',ce)]:
   header=table[k].split('{',1)[0]
   params=re.findall(r'\.param\s+\.(u[0-9]+)((?:\s+\.ptr\s+\.align\s+[0-9]+)?)\s+'+k+r'_param_([0-9]+)',header)
   observed=[{'type':t,'pointer':bool(ptr),'index':int(idx)} for t,ptr,idx in params];abi[k][variant]=observed
   expected=P['expected_abi'][k][variant]
   kg[variant+'_abi_exact']=[x['type'] for x in observed]==expected and [x['index'] for x in observed]==list(range(len(expected))) and all(x['pointer']==(x['type']=='u64') for x in observed)
  details[k]={'baseline':b,'candidate':c,'gates':kg,'allocation_admission':admission};gates.update({k+':'+name:value for name,value in kg.items()})

 report={'id':'E060-resource','at':old.now(),'status':'pass_resource_prerequisite' if all(gates.values()) else 'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'source_manifest_sha256':P['source_manifest_sha256'],'raw_markers':markers,'details':details,'abi':abi,'gates':gates,'ptx_sha256':{v:old.sha(OUT/(v+'.ptx')) for v in ['baseline','candidate']},'entry_body_sha256':{v:{n:hashlib.sha256(t.encode()).hexdigest() for n,t in table.items()} for v,table in [('baseline',be),('candidate',ce)]},'binary_sha256':old.sha(HERE/'probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'stderr_sha256':old.sha(OUT/'probe.stderr.log'),'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True,'limits':'Actual compiled attributes and theoretical occupancy only. No numerical, runtime utilization, capacity or speed qualification.'}
old.save(HERE/'report.json',report);old.save(OUT/'complete.json',{'at':old.now(),'report_sha256':old.sha(HERE/'report.json'),'all_children_terminal':True,'kernel_launches':0,'solver_executions':0,'accepted162_main_live_ptx_unchanged':True})
 print(json.dumps({'status':report['status'],'registers':[rows['baseline','up_action']['registers'],rows['candidate','up_action']['registers']],'local_bytes':[rows['baseline','up_action']['local_bytes_per_thread'],rows['candidate','up_action']['local_bytes_per_thread']],'failed_gates':[k for k,v in gates.items() if not v],'report_sha256':old.sha(HERE/'report.json')}),flush=True)
