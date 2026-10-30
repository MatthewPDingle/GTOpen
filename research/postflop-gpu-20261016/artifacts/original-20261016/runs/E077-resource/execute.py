"""One exact-source compiler/resource process; no application kernels or source activation."""
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
 t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',t)
 t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t)
 return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
assert normalize('$L__BB7_2: __local_depot7[64]')==normalize('$L__BB8_2: __local_depot8[64]')
assert normalize('add.u32 %r1, %r2, 4;')!=normalize('add.u32 %r1, %r2, 8;')
def child(command,label,timeout):
 proc=None;error=None;cleanup=None;start=old.now()
 try:
  with (O/(label+'.stdout.log')).open('xb')as out,(O/(label+'.stderr.log')).open('xb')as err:
   old.save(O/(label+'.invocation.json'),{'at':start,'command':command,'cwd':str(O)});proc=subprocess.Popen(command,cwd=O,env=old.env(),stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW);proc.wait(timeout=timeout)
  assert proc.returncode==0,(label,(O/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
 except BaseException as exc:error=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
 finally:old.save(O/(label+'.exit.json'),{'started_at':start,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
verify()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3;assert not O.exists()and not (H/'probe.exe').exists();O.mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid']in gpu['stdout'];old.save(O/'before.json',{'at':old.now(),'GPU':gpu,'application_kernel_launches':0})
 child(P['rustc_command'],'rustc',180);verify();old.save(O/'build-complete.json',{'at':old.now(),'compiler_terminal':True,'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
 child([str(H/'probe.exe')],'probe',180);verify()
 markers=[json.loads(x.split('E077_RESOURCE ',1)[1])for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if 'E077_RESOURCE 'in x];assert len(markers)==22 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['shape']):x for x in markers[1:-1]};assert len(rows)==20
 tables={(v,a):entries(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries'])for t in tables.values())
 gates={};abi={};mechanism={}
 for arch in ['compute_120','compute_75']:
  b,c=tables['baseline',arch],tables['candidate',arch]
  comparisons={n:{'raw_exact':b[n]==c[n],'normalized_only_local_function_ordinals_exact':normalize(b[n])==normalize(c[n])}for n in b if n!='up_show'}
  gates[arch+':other8entries_exact_modulo_only_local_function_ordinals']=all(x['normalized_only_local_function_ordinals_exact']for x in comparisons.values())
  be,ce=b['up_show'],c['up_show'];bs=be.split('{',1)[0];cs=ce.split('{',1)[0];gates[arch+':ABI27_exact']=bs==cs and bs.count('.param ')==27
  masks=lambda t:re.findall(r'\band\.b32\s+[^;\n]*,\s*(?:2147483647|0x7[fF]{7})\s*;',t)
  bm,cm=masks(be),masks(ce);gates[arch+':low31bit_decode_masks_emitted']=len(cm)>=2 and len(cm)>len(bm);gates[arch+':show_entry_changed']=normalize(be)!=normalize(ce)
  abi[arch]={'parameters':bs.count('.param '),'baseline_header_sha256':hashlib.sha256(bs.encode()).hexdigest(),'candidate_header_sha256':hashlib.sha256(cs.encode()).hexdigest()}
  fp=lambda t:dict(collections.Counter(re.findall(r'\b(?:add|sub|mul|fma|div|rcp|sqrt|abs|max|min|setp)(?:\.[A-Za-z0-9_]+)*\.f(?:32|64)\b',t)))
  mechanism[arch]={'other_entries':comparisons,'baseline_low31_mask_sites':bm,'candidate_low31_mask_sites':cm,'FP_opcode_counts_diagnostic_only':{'baseline':fp(be),'candidate':fp(ce)},'limits':'Static masks and changed entry prove new index decode was compiled. This is not full dataflow, dynamic dead-store, SASS/traffic, numeric or speed proof. Source demand/control proof and direct raw cases remain mandatory.'}
 sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
 feasibility={};warnings=[]
 for shape in P['shapes']:
  b,c=rows['baseline',shape],rows['candidate',shape];a=evaluate_feasibility(b,c,old.read(P['allocation_proof']['path']));feasibility[shape]=a
  gates.update({shape+':'+k:v for k,v in a['gates'].items()});gates[shape+':local_bytes_exact']=b['local_bytes_per_thread']==c['local_bytes_per_thread'];gates[shape+':static_shared_bytes_exact']=b['static_shared_bytes']==c['static_shared_bytes'];gates[shape+':dynamic_shared_bytes_exact']=b['dynamic_shared_bytes']==c['dynamic_shared_bytes'];warnings.extend(a['resource_warnings'])
 report={'id':'E077-resource','at':old.now(),'status':'pass_compiled_selective_prefix_prerequisites'if all(gates.values())else'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'rows':markers[1:-1],'feasibility':feasibility,'resource_warnings':warnings,'abi':abi,'emitted_mechanism':mechanism,'raw_markers':markers,'ptx_sha256':{v+'-'+a:old.sha(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']},'binary_sha256':old.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'accepted_main_live_PTX_unchanged':True,'limits':'Source-matched PTX decode masks/ABI/other8 entries and queried resources only. No SASS/dynamic memory, GPU numerical/state, compiled host tagging, actual material/CPU cost, integrated solver or speed proof.'};old.save(H/'report.json',report)
 old.save(O/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0})
 print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'registers':[rows['baseline',P['shapes'][0]]['registers'],rows['candidate',P['shapes'][0]]['registers']],'resource_warnings':warnings,'report_sha256':old.sha(H/'report.json')}),flush=True)
