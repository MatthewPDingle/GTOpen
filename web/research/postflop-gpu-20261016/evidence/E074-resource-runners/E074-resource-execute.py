"""One sealed generic-fallback codegen/resource probe; no application kernels."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parent.parent;H=R/'runs/E074-resource';sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
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
 def child(command,label,timeout):
  proc=None;error=None;cleanup=None;started=old.now()
  try:
   with(O/(label+'.stdout.log')).open('xb')as stdout,(O/(label+'.stderr.log')).open('xb')as stderr:
    old.save(O/(label+'.invocation.json'),{'at':started,'command':command,'cwd':str(O)});proc=subprocess.Popen(command,cwd=O,env=old.env(),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW);proc.wait(timeout=timeout)
   assert proc.returncode==0,(label,(O/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
  except BaseException as exc:error=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
  finally:old.save(O/(label+'.exit.json'),{'started_at':started,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
 child(P['rustc_command'],'rustc',180);verify();old.save(O/'build-complete.json',{'at':old.now(),'compiler_terminal':True,'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
 child([str(H/'probe.exe')],'probe',180);verify()
 markers=[json.loads(x.split('E074_RESOURCE ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E074_RESOURCE 'in x];assert len(markers)==4 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==2
 tables={(v,a):entries(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries'])for t in tables.values())
 gates={};mechanism={};unchanged={}
 for arch in ['compute_120','compute_75']:
  b,c=tables['baseline',arch],tables['candidate',arch];comparison={n:{'raw_exact':b[n]==c[n],'local_function_names_normalized_exact':normalize(b[n])==normalize(c[n]),'baseline_sha256':hashlib.sha256(b[n].encode()).hexdigest(),'candidate_sha256':hashlib.sha256(c[n].encode()).hexdigest()}for n in b if n!='up_action'};unchanged[arch]=comparison
  gates[arch+':other8entries_exact_modulo_only_local_function_ordinals']=all(x['local_function_names_normalized_exact']for x in comparison.values())
  bs=b['up_action'].split('{',1)[0];cs=c['up_action'].split('{',1)[0];gates[arch+':global_ABI20_exact']=bs==cs and bs.count('.param ')==20
  text=(O/('candidate-'+arch+'.ptx')).read_text(encoding='utf-8');matches=list(re.finditer(r'\.func\s+([^\s(]*up_action_generic[^\s(]*)\s*\(',text));gates[arch+':one_private_helper_emitted']=len(matches)==1
  details={'private_functions':len(matches),'up_action_entry_lines':[len(b['up_action'].splitlines()),len(c['up_action'].splitlines())],'driver_SASS_inspected':False}
  if len(matches)==1:
   m=matches[0];name=m[1];body_left=text.index('{',m.end());end=body_left+1;depth=1
   while depth:
    if text[end]=='{':depth+=1
    elif text[end]=='}':depth-=1
    end+=1
   header=text[m.start():body_left];body=text[body_left:end];calls=re.findall(r'\bcall(?:\.[A-Za-z0-9_]+)*\s+\n?\s*'+re.escape(name)+r'\b',c['up_action'])
   gates[arch+':one_entry_call_to_same_helper']=len(calls)==1;gates[arch+':callee20parameters']=header.count('.param ')==20;gates[arch+':no_recursive_helper_call']=not re.search(r'\bcall(?:\.[A-Za-z0-9_]+)*\s+\n?\s*'+re.escape(name)+r'\b',body)
   details.update(helper_name=name,helper_parameters=header.count('.param '),entry_calls=len(calls),callee_local_declared_bytes=[int(x)for x in re.findall(r'\.local\s+\.align\s+\d+\s+\.b8\s+\w+\[(\d+)\]',body)],entry_local_declared_bytes=[int(x)for x in re.findall(r'\.local\s+\.align\s+\d+\s+\.b8\s+\w+\[(\d+)\]',c['up_action'])],callee_PTX_bytes=len((header+body).encode()),callee_body_sha256=hashlib.sha256(body.encode()).hexdigest(),entry_call_parameter_declarations=re.findall(r'\.param\s+\.b(?:32|64)\s+param\d+;',c['up_action']))
  else:
   for name in ['one_entry_call_to_same_helper','callee20parameters','no_recursive_helper_call']:gates[arch+':'+name]=False
  mechanism[arch]=details
 sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
 b,c=rows['baseline','up_action'],rows['candidate','up_action'];admission=evaluate_feasibility(b,c,old.read(P['allocation_proof']['path']));gates|={'up_action:'+k:v for k,v in admission['gates'].items()};gates['static_shared_bytes_exact']=b['static_shared_bytes']==c['static_shared_bytes'];gates['dynamic_shared_bytes_exact']=b['dynamic_shared_bytes']==c['dynamic_shared_bytes'];gates['target_actual_register_count_reduced']=c['registers']<b['registers'];gates['target_128thread_driver_occupancy_improved']=dict(c['occupancy_by_threads'])[128]>dict(b['occupancy_by_threads'])[128];gates['driver_context_stack_limit_not_increased']=c['context_stack_limit_after_load']<=b['context_stack_limit_after_load']
 report={'id':'E074-resource','at':old.now(),'status':'pass_compiled_call_boundary_prerequisites'if all(gates.values())else'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'baseline':b,'candidate':c,'feasibility':admission,'mechanism':mechanism,'other8entries':unchanged,'raw_markers':markers,'ptx_sha256':{v+'-'+a:old.sha(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']},'binary_sha256':old.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'accepted_main_live_PTX_unchanged':True,'limits':'PTX call emission and queried driver resources only. Local function ordinal normalization changes no instructions/registers/constants/parameters/offsets. Driver context stack limit/local_size do not establish actual dynamic call-frame bytes, runtime memory/capacity, accuracy, CPU costs or speed; full raw numerical and complete qualification remain mandatory.'};old.save(H/'report.json',report);old.save(O/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0})
 print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'registers':[b['registers'],c['registers']],'local':[b['local_bytes_per_thread'],c['local_bytes_per_thread']],'occupancy128':[dict(b['occupancy_by_threads'])[128],dict(c['occupancy_by_threads'])[128]],'context_stack_limits':[b['context_stack_limit_after_load'],c['context_stack_limit_after_load']],'report_sha256':old.sha(H/'report.json')}),flush=True)
