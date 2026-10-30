"""One no-launch E052 compiler/resource probe, direct Windows output handles."""
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
 raw=(OUT/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E052_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E052_RESOURCE ' in x]
 assert len(markers)==22 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['shape']):x for x in markers[1:-1]};assert len(rows)==20
 actual='compute_120'
 be,ce=entries(OUT/f'baseline-{actual}.ptx'),entries(OUT/f'candidate-{actual}.ptx')
 bf,cf=entries(OUT/'baseline-compute_75.ptx'),entries(OUT/'candidate-compute_75.ptx')
 assert set(be)==set(ce)==set(bf)==set(cf)==set(P['expected_entries'])
 unchanged=[k for k in be if be[k]==ce[k]]
 gates={'other8_entries_exact':set(unchanged)==set(be)-{'up_show'},'other8_sm75_entries_exact':all(bf[k]==cf[k] for k in bf if k!='up_show'),'sm75_show_changed':bf['up_show']!=cf['up_show'],'shared16load_emitted':bool(re.search(r'ld\.shared(?:\.[a-z]+)*\.u16',ce['up_show'])),'shared16store_emitted':bool(re.search(r'st\.shared(?:\.[a-z]+)*\.(?:u16|b16)',ce['up_show']))}

 details={};abi={}
 for shape in P['shapes']:
  b,c=rows['baseline',shape],rows['candidate',shape]
  kg={'registers_not_increased':c['registers']<=b['registers'],'local_not_increased':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'static_shared_not_increased':c['static_shared_bytes']<=b['static_shared_bytes'],'dynamic_shared_reduced_as_prescribed':c['dynamic_shared_bytes']==b['dynamic_shared_bytes']-4*P['shape_dimensions'][shape][1],'max_threads_not_reduced':c['max_threads']>=b['max_threads'],'fits_default_limits':b['fits_default_limits'] and c['fits_default_limits'],'occupancy_not_reduced':all(bt==ct and cn>=bn for (bt,bn),(ct,cn) in zip(b['occupancy_by_threads'],c['occupancy_by_threads'])) and len(c['occupancy_by_threads'])==3}
  details[shape]={'baseline':b,'candidate':c,'gates':kg};gates.update({shape+':'+k:v for k,v in kg.items()})
 def signature(text):
  return re.findall(r'\.param\s+\.(u[0-9]+)((?:\s+\.ptr\s+\.align\s+[0-9]+)?)\s+up_show_param_([0-9]+)',text.split('{',1)[0])
 abi={'baseline':signature(be['up_show']),'candidate':signature(ce['up_show'])}
 gates['abi_exact']=abi['baseline']==abi['candidate'] and len(abi['baseline'])==P['up_show_parameter_count']
 report={'id':'E052-resource','at':old.now(),'status':'pass_resource_feasibility_only' if all(gates.values()) else 'rejected_resource_gate','protocol_sha256':sys.argv[1],'source_manifest_sha256':P['source_manifest_sha256'],'raw_markers':markers,'details':details,'abi':abi,'gates':gates,'ptx_sha256':{v:old.sha(OUT/(v+'-compute_120.ptx')) for v in ['baseline','candidate']},'entry_body_sha256':{v:{n:hashlib.sha256(t.encode()).hexdigest() for n,t in table.items()} for v,table in [('baseline',be),('candidate',ce)]},'binary_sha256':old.sha(HERE/'probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'stderr_sha256':old.sha(OUT/'probe.stderr.log'),'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted162_main_live_ptx_unchanged':True,'limits':'Actual compiled attributes and theoretical occupancy only. No numerical, runtime utilization, capacity or speed qualification.'}
 old.save(HERE/'report.json',report);old.save(OUT/'complete.json',{'at':old.now(),'report_sha256':old.sha(HERE/'report.json'),'all_children_terminal':True,'kernel_launches':0,'solver_executions':0,'accepted162_main_live_ptx_unchanged':True})
 print(json.dumps({'status':report['status'],'details':details,'gates':gates,'report_sha256':old.sha(HERE/'report.json')},indent=2),flush=True)
