"""Frozen compiler/module-load prerequisite. No application kernels execute."""
import sys,json,re,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E091-resource';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.custody();h.pin(H/'protocol.json',sys.argv[1])
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
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
 t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',t);t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t);return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
 gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid']in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernel_launches':0})
 h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
 h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('E091_RESOURCE ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E091_RESOURCE 'in x];assert len(markers)==4 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete'
rows={x['variant']:x for x in markers[1:-1]};assert set(rows)=={'baseline','candidate'}
tables={(v,a):entries(O/f'{v}-{a}.ptx')for v in['baseline','candidate']for a in['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries'])for t in tables.values());gates={};other={}
for arch in['compute_120','compute_75']:
 b,c=tables['baseline',arch],tables['candidate',arch]
 other[arch]={n:{'normalized_exact':normalize(b[n])==normalize(c[n]),'baseline_sha256':hashlib.sha256(b[n].encode()).hexdigest(),'candidate_sha256':hashlib.sha256(c[n].encode()).hexdigest()}for n in b if n!='down_action'}
 gates[arch+':other8entries_exact']=all(x['normalized_exact']for x in other[arch].values())
 bh,ch=b['down_action'].split('{',1)[0],c['down_action'].split('{',1)[0]
 gates[arch+':global18parameter_ABI_exact']=bh==ch and bh.count('.param ')==18
 gates[arch+':target_entry_changed']=normalize(b['down_action'])!=normalize(c['down_action'])
 gates[arch+':CTA_barrier_sites_exact']=b['down_action'].count('bar.sync')==c['down_action'].count('bar.sync')
b,c=rows['baseline'],rows['candidate'];bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads'])
gates.update(local_not_increased=c['local_bytes_per_thread']<=b['local_bytes_per_thread'],static_shared_exact=c['static_shared_bytes']==b['static_shared_bytes'],dynamic_shared_zero=b['dynamic_shared_bytes']==c['dynamic_shared_bytes']==0,max_threads_not_reduced=c['max_threads']>=b['max_threads'],all_fixed_thread_controls_legal=min(b['max_threads'],c['max_threads'])>=256,all_three_occupancies_not_reduced=all(co[t]>=bo[t]>0 for t in[64,128,256]),both_fit_default_limits=b['fits_default_limits']and c['fits_default_limits'],no_stack_limit_increase=c['context_stack_limit_after_load']<=b['context_stack_limit_after_load'])
passed=all(gates.values());report={'id':'E091-resource','at':h.now(),'status':'pass_compiled_prerequisites'if passed else'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'baseline':b,'candidate':c,'other8entries':other,'raw_markers':markers,'ptx_sha256':{v+'-'+a:h.sha(O/f'{v}-{a}.ptx')for v in['baseline','candidate']for a in['compute_120','compute_75']},'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'source_main_live_PTX_custody_pass':True,'scope':'Four NVRTC compilations, actual compute120 module loads, driver register/local/shared/stack/default-limit queries and theoretical occupancy at64/128/256 threads. Register increases alone are recorded, with no local/shared/occupancy regression permitted. No universal resource, correctness, dynamic occupancy, actual whole CPU/memory/capacity or speed claim. No extension or source/resource-gate variant after a real failure.'}
h.save(H/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0});verify()
print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'registers':[b['registers'],c['registers']],'local':[b['local_bytes_per_thread'],c['local_bytes_per_thread']],'occupancy128':[bo[128],co[128]]}),flush=True)
