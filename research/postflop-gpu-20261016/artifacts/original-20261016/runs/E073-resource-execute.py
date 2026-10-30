"""One frozen compile/resource probe for private u16 river boundaries."""
from pathlib import Path
import collections,hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parent.parent;H=R/'runs/E073-resource';sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
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
def boundary_loads(entry):
 # Track pointer-address arithmetic only, never the loaded boundary's value.
 origins={};loads=[]
 for raw in entry.splitlines():
  t=raw.strip().split('//',1)[0].strip()
  m=re.fullmatch(r'ld\.param\.u64\s+(%\w+),\s*\[up_show_param_(12|13)\];',t)
  if m:origins[m[1]]={int(m[2])};continue
  m=re.search(r'\bld\.global(?:\.[A-Za-z0-9_]+)*\.(u|b)(16|32|64)\s+(%\w+),\s*\[(%\w+)(?:\+\d+)?\];',t)
  if m:
   if origins.get(m[4]):loads.append({'parameters':sorted(origins[m[4]]),'bits':int(m[2]),'line':t})
   origins.pop(m[3],None);continue
  m=re.match(r'(?:@!?%\w+\s+)?(?:add|sub|mul|mad|shl|shr|mov|cvt)(?:\.[A-Za-z0-9_]+)*\s+(%\w+),\s*(.*);$',t)
  if m:
   source=set().union(*(origins.get(reg,set())for reg in re.findall(r'%\w+',m[2])));origins[m[1]]=source
 return loads
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
 markers=[json.loads(x.split('E073_RESOURCE ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E073_RESOURCE 'in x];assert len(markers)==22 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['shape']):x for x in markers[1:-1]};assert len(rows)==20
 tables={(v,a):entries(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries'])for t in tables.values())
 gates={};mechanism={};abi={}
 for arch in ['compute_120','compute_75']:
  b,c=tables['baseline',arch],tables['candidate',arch];gates[arch+':unchanged8entries_exact']=all(b[n]==c[n]for n in b if n!='up_show');gates[arch+':only_show_entry_changed']={n for n in b if b[n]!=c[n]}=={'up_show'}
  be,ce=b['up_show'],c['up_show'];bs=be.split('{',1)[0];cs=ce.split('{',1)[0];gates[arch+':ABI_exact']=bs==cs and bs.count('.param ')==27;abi[arch]={'baseline_header_sha256':hashlib.sha256(bs.encode()).hexdigest(),'candidate_header_sha256':hashlib.sha256(cs.encode()).hexdigest(),'parameters':bs.count('.param ')}
  bl,cl=boundary_loads(be),boundary_loads(ce)
  gates[arch+':baseline_two_boundary_parameters_loaded32']=bool(bl)and{p for row in bl for p in row['parameters']}=={12,13}and all(row['bits']==32 for row in bl)
  gates[arch+':candidate_two_boundary_parameters_loaded16']=bool(cl)and{p for row in cl for p in row['parameters']}=={12,13}and all(row['bits']==16 for row in cl)
  fp=lambda text:collections.Counter(re.findall(r'\b(?:add|sub|mul|fma|div|rcp|sqrt|abs|max|min|setp)(?:\.[A-Za-z0-9_]+)*\.f(?:32|64)\b',text))
  mechanism[arch]={'baseline_boundary_loads':bl,'candidate_boundary_loads':cl,'FP_opcode_counts_diagnostic_only':{'baseline':dict(fp(be)),'candidate':dict(fp(ce))},'driver_SASS_inspected':False}
 sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
 feasibility={};warnings=[]
 for shape in P['shapes']:
  b,c=rows['baseline',shape],rows['candidate',shape];a=evaluate_feasibility(b,c,old.read(P['allocation_proof']['path']));feasibility[shape]=a
  gates|={shape+':'+k:v for k,v in a['gates'].items()};gates[shape+':local_bytes_exact']=b['local_bytes_per_thread']==c['local_bytes_per_thread'];gates[shape+':static_shared_bytes_exact']=b['static_shared_bytes']==c['static_shared_bytes'];gates[shape+':dynamic_shared_bytes_exact']=b['dynamic_shared_bytes']==c['dynamic_shared_bytes'];warnings.extend(a['resource_warnings'])
 report={'id':'E073-resource','at':old.now(),'status':'pass_compiled_resource_and_narrow_load_prerequisites'if all(gates.values())else'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'rows':markers[1:-1],'feasibility':feasibility,'resource_warnings':warnings,'abi':abi,'emitted_mechanism':mechanism,'raw_markers':markers,'ptx_sha256':{v+'-'+a:old.sha(O/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']},'binary_sha256':old.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'accepted_main_live_PTX_unchanged':True,'limits':'Emitted PTX narrow pointer loads and queried driver resources only; no SASS/cache traffic, GPU output equivalence, actual integrated CPU/host/memory/capacity or speed proof. Source floating recurrences are unchanged, but full raw numerical controls and all complete-solve qualification remain mandatory.'};old.save(H/'report.json',report)
 old.save(O/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0})
 print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'registers':[rows['baseline',P['shapes'][0]]['registers'],rows['candidate',P['shapes'][0]]['registers']],'resource_warnings':warnings,'report_sha256':old.sha(H/'report.json')}),flush=True)
