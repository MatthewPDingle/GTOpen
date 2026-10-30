"""One no-launch E070 compiler/resource probe, direct Windows output handles."""
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
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(old.ROOT).free>=66*1024**3
 assert not OUT.exists() and not (HERE/'probe.exe').exists();OUT.mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid'] in gpu['stdout']
 old.save(OUT/'before.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'gpu':gpu,'application_kernel_launches':0})
 env=old.env();assert not {k:v for k,v in env.items() if k in {'RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','RUSTC','RUSTC_WRAPPER','RUSTC_WORKSPACE_WRAPPER'} or k.startswith('CARGO_PROFILE_RELEASE_')}
 child(P['rustc_command'],'rustc',env,180)
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.save(OUT/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(HERE/'probe.exe'),'rustc_terminal':True,'native_executions':0})
 child([str(HERE/'probe.exe')],'probe',env,180);old.custody()
 raw=(OUT/'probe.stdout.log').read_text(encoding='utf-8');markers=[json.loads(x.split('E070_RESOURCE ',1)[1]) for x in raw.splitlines() if 'E070_RESOURCE ' in x];assert len(markers)==10 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==8
 tables={(v,a):entries(OUT/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']}
 assert all(set(t)==set(P['expected_entries']) for t in tables.values());changed=set(P['changed_entries']);gates={};details={};abi={};mechanism={}
 for arch in ['compute_120','compute_75']:
  be,ce=tables['baseline',arch],tables['candidate',arch]
  gates[arch+':other5_entries_exact']=all(be[n]==ce[n] for n in be if n not in changed)
  gates[arch+':exact4_changed_entries']={n for n in be if be[n]!=ce[n]}==changed
  for name in P['changed_entries']:
   def sig(t):return re.findall(r'\.param\s+\.(u[0-9]+)((?:\s+\.ptr\s+\.align\s+[0-9]+)?)\s+'+re.escape(name)+r'_param_([0-9]+)',t.split('{',1)[0])
   bs,cs=sig(be[name]),sig(ce[name]);meta=P['parameter_schema'][name];assert [int(x[2]) for x in bs]==list(range(len(bs))) and [int(x[2]) for x in cs]==list(range(len(cs)))
   expected=[x for x,p in zip(bs,meta['baseline']) if p['name']!='node_na'];same=len(bs)==len(meta['baseline']) and len(cs)==len(meta['candidate'])==len(expected) and [(x[0],x[1]) for x in cs]==[(x[0],x[1]) for x in expected]
   gates[arch+':'+name+':ABI_transform']=same;abi[arch+':'+name]={'baseline':bs,'candidate':cs,'source_parameter_schema':meta}
   narrow=len(re.findall(r'\bld\.global(?:\.[a-z0-9]+)*\.(?:u8|u16)\b',ce[name]));gates[arch+':'+name+':narrow_metadata_load_emitted']=narrow>0;mechanism[arch+':'+name]={'candidate_PT X_narrow_global_load_sites'.replace('PT X','PTX'):narrow,'driver_SASS_inspected':False}
 sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
 proof=old.read(P['allocation_proof']['path'])
 for name in P['changed_entries']:
  b,c=rows['baseline',name],rows['candidate',name];admission=evaluate_feasibility(b,c,proof);kg=admission['gates']|{'same_dynamic_bytes':b['dynamic_shared_bytes']==c['dynamic_shared_bytes']};details[name]={'baseline':b,'candidate':c,'feasibility':admission};gates.update({name+':'+k:v for k,v in kg.items()})
 report={'id':'E070-resource','at':old.now(),'status':'pass_resource_and_encoding_prerequisites' if all(gates.values()) else 'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'details':details,'abi':abi,'emitted_mechanism':mechanism,'raw_markers':markers,'ptx_sha256':{v+'-'+a:old.sha(OUT/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']},'entry_body_sha256':{v+'-'+a:{n:hashlib.sha256(t.encode()).hexdigest() for n,t in table.items()} for(v,a),table in tables.items()},'binary_sha256':old.sha(HERE/'probe.exe'),'stdout_sha256':old.sha(OUT/'probe.stdout.log'),'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'host_integration_implemented':False,'accepted_main_live_ptx_unchanged':True,'limits':'Compiler PTX narrow loads and driver attributes/occupancy only. No driver SASS, GPU floating-result equivalence, actual integrated allocation/graph/CPU/peak/capacity or speed qualification. No source activation.'}
 old.save(HERE/'report.json',report);old.save(OUT/'complete.json',{'at':old.now(),'report_sha256':old.sha(HERE/'report.json'),'all_children_terminal':True,'application_kernel_launches':0})
 print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items() if not v],'resources':{n:{'registers':[details[n][v]['registers'] for v in ['baseline','candidate']],'local':[details[n][v]['local_bytes_per_thread'] for v in ['baseline','candidate']],'max_threads':[details[n][v]['max_threads'] for v in ['baseline','candidate']]} for n in details},'report_sha256':old.sha(HERE/'report.json')}),flush=True)
