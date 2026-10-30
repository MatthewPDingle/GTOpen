"""One compile/resource process, no application kernel or current-source activation."""
from pathlib import Path
import collections,hashlib,json,re,shutil,subprocess,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');O=H/'execution'
def verify():
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
def normalize(t):
 t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',t);t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t)
 return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
def abi(t):return re.findall(r'\.param\s+\.(\w+)\s+(\w+)',t.split('{',1)[0])
assert normalize('$L__BB7_2: __local_depot7[64]')==normalize('$L__BB8_2: __local_depot8[64]')
assert normalize('add.u32 %r1, %r2, 4;')!=normalize('add.u32 %r1, %r2, 8;')
assert abi('.visible .entry x(.param .u64 x_param_0, .param .u32 x_param_1){')==[('u64','x_param_0'),('u32','x_param_1')]
def child(command,label,timeout):
 proc=None;error=None;cleanup=None;start=old.now()
 try:
  with(O/(label+'.stdout.log')).open('xb')as out,(O/(label+'.stderr.log')).open('xb')as err:
   old.save(O/(label+'.invocation.json'),{'at':start,'command':command,'cwd':str(O)});proc=subprocess.Popen(command,cwd=O,env=old.env(),stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW);proc.wait(timeout=timeout)
  assert proc.returncode==0,(label,(O/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
 except BaseException as exc:error=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(O/(label+'.exit.json'),{'started_at':start,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;assert not O.exists()and not(H/'probe.exe').exists();O.mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid']in gpu['stdout'];old.save(O/'before.json',{'at':old.now(),'GPU':gpu,'application_kernel_launches':0})
 child(P['rustc_command'],'rustc',180);verify();old.save(O/'build-complete.json',{'at':old.now(),'compiler_terminal':True,'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
 child([str(H/'probe.exe')],'probe',180);verify();markers=[json.loads(x.split('E078_RESOURCE ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if x.startswith('E078_RESOURCE ')];assert len(markers)==4 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete'
 rows={x['variant']:x for x in markers[1:-1]};assert set(rows)=={'baseline','candidate'}
 tables={(v,a):entries(O/f'{v}-{a}.ptx')for v in['baseline','candidate']for a in['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries'])for t in tables.values());gates={};mechanism={}
 for arch in['compute_120','compute_75']:
  b,c=tables['baseline',arch],tables['candidate',arch];other={n:{'raw_exact':b[n]==c[n],'normalized_only_local_function_ordinals_exact':normalize(b[n])==normalize(c[n])}for n in b if n!='up_action'};gates[arch+':other8entries_exact_modulo_only_local_function_ordinals']=all(x['normalized_only_local_function_ordinals_exact']for x in other.values())
  ba,ca=abi(b['up_action']),abi(c['up_action']);gates[arch+':original20ABI_parameters_exact']=len(ba)==20 and ca[:20]==ba;gates[arch+':candidate30ABI_parameters']=len(ca)==30 and [t for t,_ in ca[20:]]==['u64']*9+['u32']
  shared=re.findall(r'\.shared\s+\.align\s+(\d+)\s+\.b8\s+(\S+)\[(\d+)\];',c['up_action']);sizes=sorted(int(x[2])for x in shared);gates[arch+':three_original_fold_shared_arrays']=sizes==[208,1024,5304]
  marker_tests=re.findall(r'\bsetp\.(?:eq|ne)\.(?:s32|u32|b32)\s+[^;\n]*,\s*(?:-1|4294967295|0x[fF]{8})\s*;',c['up_action']);gates[arch+':private_fold_marker_compare_emitted']=bool(marker_tests)
  barriers=len(re.findall(r'\bbar\.sync\s+0\s*;',c['up_action']));gates[arch+':fold_collectives_emitted']=barriers>=4;gates[arch+':action_entry_changed']=normalize(b['up_action'])!=normalize(c['up_action'])
  fp=lambda t:dict(collections.Counter(re.findall(r'\b(?:add|sub|mul|fma|div|rcp|sqrt|abs|max|min|setp)(?:\.[A-Za-z0-9_]+)*\.f(?:32|64)\b',t)))
  mechanism[arch]={'other_entries':other,'baseline_ABI':ba,'candidate_ABI':ca,'candidate_shared_declarations':shared,'candidate_fold_marker_compares':marker_tests,'candidate_barrier_instruction_sites':barriers,'FP_opcode_counts_diagnostic_only':{'baseline':fp(b['up_action']),'candidate':fp(c['up_action'])},'limits':'Source-matched ABI/shared/marker/barrier emission only; not complete FPdataflow, raw numerical equivalence, SASS/dynamic traffic or speed. Exact folded/arithmetic/hand/CFV raw controls remain.'}
 sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
 feasibility=evaluate_feasibility(rows['baseline'],rows['candidate'],old.read(P['allocation_proof']['path']));gates.update(feasibility['gates']);gates['dynamic_shared_exact']=rows['baseline']['dynamic_shared_bytes']==rows['candidate']['dynamic_shared_bytes']==0
 report={'id':'E078-resource','at':old.now(),'status':'pass_compiled_fold_parent_prerequisites'if all(gates.values())else'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'rows':markers[1:-1],'feasibility':feasibility,'resource_warnings':feasibility['resource_warnings'],'emitted_mechanism':mechanism,'ptx_sha256':{v+'-'+a:old.sha(O/f'{v}-{a}.ptx')for v in['baseline','candidate']for a in['compute_120','compute_75']},'binary_sha256':old.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'accepted_main_live_PTX_unchanged':True,'limits':'Resource queries/compiler-only. Staticshared/register/occupancy differences disclosed, not actual process/GPU peaks or no-tradeoff proof. Default dynamic0 for every hand shape and conservative1326staticbound, actual64/128/256driveroccupancies. No native numerical/application kernel/solver/speed test yet. All exact/broad/state/material/1%/strictfixture/fresh16/holdout/cumulative gates remain.'};old.save(H/'report.json',report);old.save(O/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0})
 print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'rows':report['rows'],'resource_warnings':report['resource_warnings'],'report_sha256':old.sha(H/'report.json')}),flush=True)
