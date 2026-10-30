"""One sealed generic-fallback codegen/resource probe; no application kernels."""
from pathlib import Path
import collections,hashlib,json,os,re,shutil,subprocess,sys
R=Path(__file__).resolve().parent.parent;H=R/'runs/E075-resource';sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');O=H/'execution'
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.pin(P['allocation_proof']['path'],P['allocation_proof']['sha256']);old.custody()
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
def normalize(text):
 # Only compiler-local function ordinal names may change with one new .func.
 t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',text)
 t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t)
 t=re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
 return t
assert normalize('$L__BB7_2: __local_depot7[64]')==normalize('$L__BB8_2: __local_depot8[64]')
assert normalize('add.u32 %r1, %r2, 4;')!=normalize('add.u32 %r1, %r2, 8;')
assert normalize('add.u32 %r1, %r2, 4;')!=normalize('add.u32 %r2, %r2, 4;')
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;assert not O.exists()and not(H/'probe.exe').exists();O.mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid']in gpu['stdout'];old.save(O/'before.json',{'at':old.now(),'GPU':gpu,'application_kernel_launches':0})
 def child(command,label,timeout,override_env=None):
  proc=None;error=None;cleanup=None;started=old.now()
  try:
   with(O/(label+'.stdout.log')).open('xb')as stdout,(O/(label+'.stderr.log')).open('xb')as stderr:
    old.save(O/(label+'.invocation.json'),{'at':started,'command':command,'cwd':str(O)});proc=subprocess.Popen(command,cwd=O,env=old.env()if override_env is None else override_env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW);proc.wait(timeout=timeout)
   assert proc.returncode==0,(label,(O/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
  except BaseException as exc:error=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
  finally:old.save(O/(label+'.exit.json'),{'started_at':started,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
 child(P['rustc_command'],'rustc',180);verify();old.save(O/'build-complete.json',{'at':old.now(),'compiler_terminal':True,'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
 child([str(H/'probe.exe')],'probe',180);verify()
 markers=[json.loads(x.split('E075_RESOURCE ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E075_RESOURCE 'in x];assert len(markers)==4 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==2
 tables={(v,a):entries(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries'])for t in tables.values())

 gates={};mechanism={};unchanged={}
 for arch in ['compute_120','compute_75']:
  b,c=tables['baseline',arch],tables['candidate',arch]
  comparison={n:{'raw_exact':b[n]==c[n],'local_function_names_normalized_exact':normalize(b[n])==normalize(c[n]),'baseline_sha256':hashlib.sha256(b[n].encode()).hexdigest(),'candidate_sha256':hashlib.sha256(c[n].encode()).hexdigest()}for n in b if n!='up_action'};unchanged[arch]=comparison
  gates[arch+':other8entries_exact_modulo_only_local_function_ordinals']=all(x['local_function_names_normalized_exact']for x in comparison.values())
  bs=b['up_action'].split('{',1)[0];cs=c['up_action'].split('{',1)[0];gates[arch+':global_ABI20_exact']=bs==cs and bs.count('.param ')==20
  sites=lambda t:re.findall(r'ldu[.]global[.](?:u32|s32|u64|s64)',t)
  bl,cl=sites(b['up_action']),sites(c['up_action']);gates[arch+':explicit_uniform_node_loads_emitted']=not bl and bool(cl)
  mechanism[arch]={'baseline_LDU_sites':collections.Counter(bl),'candidate_LDU_sites':collections.Counter(cl),'entry_lines':[len(b['up_action'].splitlines()),len(c['up_action'].splitlines())],'floating_source_body_unchanged':True,'native_benefit_not_inferred':True}
 sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
 b,c=rows['baseline','up_action'],rows['candidate','up_action'];admission=evaluate_feasibility(b,c,old.read(P['allocation_proof']['path']));gates|={'up_action:'+k:v for k,v in admission['gates'].items()};gates['static_shared_bytes_exact']=b['static_shared_bytes']==c['static_shared_bytes'];gates['dynamic_shared_bytes_exact']=b['dynamic_shared_bytes']==c['dynamic_shared_bytes'];gates['no_new_context_stack_limit']=c['context_stack_limit_after_load']<=b['context_stack_limit_after_load']
 # A resource failure closes before capture; passing resources permit only the
 # predeclared two owned module captures, never a kernel, counter or live attach.
 captures={};sass=None
 if all(gates.values()):
  env=old.env();env['PATH']=P['driver_capture']['private_dll_dir']+os.pathsep+env['PATH'];assert not any(k in env for k in ['CUDA_INJECTION64_PATH','CUDA_INJECTION32_PATH','CUPTI_INJECTION64_PATH','NVBIT_TOOL'])
  for arm in ['baseline','candidate']:
   stage=O/(arm+'-driver');stage.mkdir();ptx=O/(arm+'-compute_120.ptx')
   child([P['driver_capture']['binary'],str(ptx),str(stage)],arm+'-capture',120,env);verify()
   raw=(O/(arm+'-capture.stdout.log')).read_text(encoding='utf-8');marks={}
   for line in raw.splitlines():
    prefix,payload=line.split(' ',1);assert prefix in ['D098_DEVICE','D098_KERNEL','D098_MODULE','D098_COMPLETE'];marks.setdefault(prefix,[]).append(json.loads(payload))
   assert len(marks['D098_DEVICE'])==len(marks['D098_COMPLETE'])==1
   assert len(marks['D098_KERNEL'])==9 and {x['name']for x in marks['D098_KERNEL']}==set(P['expected_entries'])
   end=marks['D098_COMPLETE'][0];assert end=={'callback_errors':0,'modules':1,'kernel_launches':0,'solver_executions':0,'performance_measured':False}
   modules=list(stage.glob('*.cubin'));assert len(modules)==len(marks['D098_MODULE'])==1;module=modules[0];data=module.read_bytes();assert data[:6]==bytes([127,69,76,70,2,1]);assert marks['D098_MODULE'][0]['same_owned_context']and marks['D098_MODULE'][0]['bytes']==len(data)
   child([P['driver_capture']['nvdisasm'],'--emit-json',str(module)],arm+'-sass-json',60,env);verify()
   head,functions=old.read(O/(arm+'-sass-json.stdout.log'));assert head['SM']['version']=={'major':12,'minor':0};byname={f['function-name']:f for f in functions};assert len(byname)==len(functions)and set(P['expected_entries']).issubset(byname)
   attrs=next(x for x in marks['D098_KERNEL']if x['name']=='up_action');ref=b if arm=='baseline'else c;assert(attrs['registers'],attrs['local'],attrs['shared'],attrs['maxthreads'],attrs['occupancy64_128_256'])==(ref['registers'],ref['local_bytes_per_thread'],ref['static_shared_bytes'],ref['max_threads'],[v for t,v in ref['occupancy_by_threads']])
   captures[arm]={'markers':marks,'ptx_sha256':old.sha(ptx),'cubin_sha256':old.sha(module),'cubin_bytes':len(data),'JSON_sha256':old.sha(O/(arm+'-sass-json.stdout.log')),'producer':head['Producer'],'entry':byname['up_action']}
  counts=lambda f:dict(collections.Counter(x['opcode']for x in f['sass-instructions']if x.get('opcode','').startswith(('LDG','LDU'))))
  bc,cc=counts(captures['baseline']['entry']),counts(captures['candidate']['entry'])
  same=captures['baseline']['entry']['sass-instructions']==captures['candidate']['entry']['sass-instructions'];gates['actual_up_action_native_instruction_stream_changed']=not same;gates['actual_global_load_opcode_counts_changed']=bc!=cc
  sass={'status':'changed_native_load_encoding'if not same and bc!=cc else'compiled_native_load_mechanism_absent','instruction_stream_exact':same,'global_load_opcode_counts':{'baseline':bc,'candidate':cc},'instruction_counts':{arm:len(v['entry']['sass-instructions'])for arm,v in captures.items()},'limits':'Static opcode counts/native differences are not dynamic instructions/cache traffic/removable headroom or speed. Each CUBIN is the actual driver-loaded module from its sealed source-matched PTX, not extracted from the accepted benchmark executable.'}
 report={'id':'E075-resource','at':old.now(),'status':'pass_compiled_uniform_load_prerequisites'if all(gates.values())else'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'baseline':b,'candidate':c,'feasibility':admission,'mechanism':mechanism,'other8entries':unchanged,'raw_markers':markers,'driver_capture':{arm:{k:v for k,v in row.items()if k!='entry'}for arm,row in captures.items()},'native_code_assessment':sass,'ptx_sha256':{v+'-'+a:old.sha(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']},'binary_sha256':old.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'accepted_main_live_PTX_unchanged':True,'limits':'Source-uniform metadata and PTX/driver resource/native encoding proof only. No new app kernel, numerical result, real cache traffic, actual integrated CPU/memory/capacity or speed proof. Full raw controls and all complete-solve/broad/material qualification remain mandatory.'};old.save(H/'report.json',report);old.save(O/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0})
 print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'registers':[b['registers'],c['registers']],'local':[b['local_bytes_per_thread'],c['local_bytes_per_thread']],'driver_captures':len(captures),'native_code':sass,'report_sha256':old.sha(H/'report.json')}),flush=True)
