"""Single no-application-kernel compile/resource probe for E072 fold staging."""
from pathlib import Path
import collections,hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'runs/E072-resource';sys.path.insert(0,str(ROOT/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');OUT=H/'execution'
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
verify()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=66*1024**3;assert not OUT.exists()and not(H/'probe.exe').exists();OUT.mkdir()
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid']in gpu['stdout'];old.save(OUT/'before.json',{'at':old.now(),'GPU':gpu,'application_kernel_launches':0})
 # The probe writes its PTX to cwd; keep every output physically in this S folder.
 def child(command,label,timeout):
  proc=None;error=None;cleanup=None;started=old.now()
  try:
   with(OUT/(label+'.stdout.log')).open('xb')as stdout,(OUT/(label+'.stderr.log')).open('xb')as stderr:
    old.save(OUT/(label+'.invocation.json'),{'at':started,'command':command,'cwd':str(OUT)});proc=subprocess.Popen(command,cwd=OUT,env=old.env(),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW);proc.wait(timeout=timeout)
   assert proc.returncode==0,(label,(OUT/(label+'.stderr.log')).read_text(encoding='utf-8',errors='replace')[-3000:])
  except BaseException as exc:error=repr(exc);cleanup=old.ar.cleanup_child(proc);raise
  finally:old.save(OUT/(label+'.exit.json'),{'started_at':started,'finished_at':old.now(),'returncode':proc.returncode if proc else None,'error':error,'cleanup':cleanup})
 child(P['rustc_command'],'rustc',180);verify();old.save(OUT/'build-complete.json',{'at':old.now(),'compiler_terminal':True,'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
 child([str(H/'probe.exe')],'probe',180);verify()
 markers=[json.loads(x.split('E072_RESOURCE ',1)[1])for x in(OUT/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E072_RESOURCE 'in x];assert len(markers)==4 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==2
 tables={(v,a):entries(OUT/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries'])for t in tables.values())
 gates={};mechanism={};abi={}
 for arch in ['compute_120','compute_75']:
  b,c=tables['baseline',arch],tables['candidate',arch];gates[arch+':unchanged8entries_exact']=all(b[n]==c[n]for n in b if n!='up_fold');gates[arch+':only_fold_entry_changed']={n for n in b if b[n]!=c[n]}=={'up_fold'}
  be,ce=b['up_fold'],c['up_fold'];bs=be.split('{',1)[0];cs=ce.split('{',1)[0];gates[arch+':ABI_exact']=bs==cs;abi[arch]={'baseline_header_sha256':hashlib.sha256(bs.encode()).hexdigest(),'candidate_header_sha256':hashlib.sha256(cs.encode()).hexdigest()}
  fp=lambda text:collections.Counter(re.findall(r'\b(?:add|sub|mul|fma|div|rcp|sqrt|abs|max|min|setp)(?:\.[A-Za-z0-9_]+)*\.f(?:32|64)\b',text))
  gates[arch+':FP_opcode_counts_exact']=fp(be)==fp(ce)
  loads=len(re.findall(r'\bld\.shared\.(?:u32|b32)\b',ce));stores=len(re.findall(r'\bst\.shared\.(?:u32|b32)\b',ce));bars=lambda text:len(re.findall(r'\bbar\.sync\b',text));gates[arch+':integer_shared_staging_emitted']=loads>0 and stores>0;gates[arch+':additional_barrier_emitted']=bars(ce)>=bars(be)+1
  mechanism[arch]={'integer_shared_load_sites':loads,'integer_shared_store_sites':stores,'barrier_sites':[bars(be),bars(ce)],'FP_opcodes':dict(fp(ce)),'driver_SASS_inspected':False}
 sys.path.insert(0,str(old.REPO/'tools'));from postflop_resource_feasibility import evaluate_feasibility
 b,c=rows['baseline','up_fold'],rows['candidate','up_fold'];admission=evaluate_feasibility(b,c,old.read(P['allocation_proof']['path']));gates|={'up_fold:'+k:v for k,v in admission['gates'].items()};gates['static_shared_bytes_exact']=b['static_shared_bytes']==c['static_shared_bytes'];gates['dynamic_shared_bytes_exact']=b['dynamic_shared_bytes']==c['dynamic_shared_bytes']
 report={'id':'E072-resource','at':old.now(),'status':'pass_compiled_resource_and_integer_staging_prerequisites'if all(gates.values())else'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'baseline':b,'candidate':c,'feasibility':admission,'abi':abi,'emitted_mechanism':mechanism,'raw_markers':markers,'ptx_sha256':{v+'-'+a:old.sha(OUT/f'{v}-{a}.ptx')for v in ['baseline','candidate']for a in ['compute_120','compute_75']},'binary_sha256':old.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'accepted_main_live_PTX_unchanged':True,'limits':'PTX/driver resources and integer shared-staging sites only; no SASS traffic, GPU float equality, actual integrated CPU/memory/capacity or speed proof. All direct and full-solver qualification gates remain required.'};old.save(H/'report.json',report)
 old.save(OUT/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0})
 print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'registers':[b['registers'],c['registers']],'local':[b['local_bytes_per_thread'],c['local_bytes_per_thread']],'static_shared':[b['static_shared_bytes'],c['static_shared_bytes']],'report_sha256':old.sha(H/'report.json')}),flush=True)
