import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E114-resource';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
def entries(path):
 text=path.read_text(encoding='utf-8');out={};i=0
 while True:
  i=text.find('.visible .entry ',i)
  if i<0:break
  a=text.index('(',i);name=text[i+len('.visible .entry '):a].strip();a=text.index('{',a);j=a+1;depth=1
  while depth:
   if text[j]=='{':depth+=1
   elif text[j]=='}':depth-=1
   j+=1
  assert name not in out;out[name]=text[i:j];i=j
 return out
def normalize(t):
 t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',t);t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t);return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid']in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernels':0})
 h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('E114_RESOURCE ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E114_RESOURCE 'in x];assert len(markers)==19 and markers[-1]['stage']=='complete';rows={(x['variant'],x['kernel']):x for x in markers[:-1]};assert len(rows)==18
gates={};tables={};warnings=[]
for arch in ['compute_120','compute_75']:
 b=entries(H/('baseline-'+arch+'.ptx'));c=entries(O/('candidate-'+arch+'.ptx'));assert set(b)==set(c)==set(P['original_entries']);tables[arch]={}
 for name in P['original_entries']:
  tables[arch][name]={'parameter_count':b[name].split('{',1)[0].count('.param '),'header_ABI_exact':b[name].split('{',1)[0]==c[name].split('{',1)[0],'body_alpha_exact':normalize(b[name])==normalize(c[name])}
  gates[arch+':'+name+':header_ABI_exact']=tables[arch][name]['header_ABI_exact']
  if name not in P['target_entries']:gates[arch+':'+name+':untargeted_body_exact']=tables[arch][name]['body_alpha_exact']
  else:
   gates[arch+':'+name+':barriers_exact']=b[name].count('bar.sync')==c[name].count('bar.sync')
   for arm,text in [('baseline',b[name]),('candidate',c[name])]: (O/(arm+'-'+arch+'-'+name+'.ptx.txt')).write_bytes(text.encode('utf-8'))
for name in P['original_entries']:
 b,c=rows['baseline',name],rows['candidate',name];keys=['registers','constant_bytes','local_bytes_per_thread','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','context_stack_after']
 if name not in P['target_entries']:gates[name+':actual_resources_exact']=all(b[k]==c[k]for k in keys)
 else:
  bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads']);gates.update({name+':no_new_local':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],name+':no_constant_growth':c['constant_bytes']<=b['constant_bytes'],name+':no_dynamic_growth':c['dynamic_shared_bytes']==b['dynamic_shared_bytes'],name+':no_maxthread_loss':c['max_threads']>=b['max_threads'],name+':fixed_occupancies_positive':all(bo[t]>0 and co[t]>0 for t in[64,128,256]),name+':default_limits_fit':c['static_shared_bytes']+c['dynamic_shared_bytes']<=c['device_shared_limit']and c['max_threads']>=256 and c['device_thread_limit']>=256,name+':no_stack_growth':c['context_stack_after']<=b['context_stack_after']})
  if c['registers']>b['registers']or c['static_shared_bytes']>b['static_shared_bytes']or any(co[t]<bo[t]for t in bo):warnings.append({'entry':name,'baseline':b,'candidate':c})
for arch in ['compute_120','compute_75']:
 gates[arch+':paired_chance_emitted_change']=not tables[arch]['up_chance']['body_alpha_exact']
passed=all(gates.values());h.save(H/'report.json',{'id':'E114-resource','at':h.now(),'status':'pass_compiled_resources_mechanism_pending'if passed else'rejected_closed_resource_or_ABI_gate','protocol_sha256':sys.argv[1],'gates':gates,'entry_tables':tables,'resource_rows':list(rows.values()),'resource_warnings':warnings,'PTX_sha256':{arm+'-'+arch:h.sha((H if arm=='baseline'else O)/(arm+'-'+arch+'.ptx'))for arm in ['baseline','candidate']for arch in ['compute_120','compute_75']},'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_samples':0,'source_activated':False,'candidate_accepted':False,'limits':'ABI/resource/all9 unchanged ABI and resource gate only; Two ordered chance accumulators; emitted shared immutable metadata/two recurrence and caller/extent reviews remain before numerical controls. No speed/no-cost/accuracy/adoption proof. Failure closes exactform without othercount/width/helper/flags/source/sample rescue.'});h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernels':0});verify()
p=H/'report.json';dst=h.ar.DASHBOARD/'evidence'/H.name/p.name;assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E114');e.update(status='running'if passed else'rejected',stage='Resources/ABI passed; paired chance operand mechanism pending'if passed else'Closed at compiled resource/ABI gate',correctness='no_candidate_device_numerical_trials',reason='Compiled resource pass='+str(passed)+'. Failedgates='+str([k for k,v in gates.items()if not v])+'. All risks retained; no applicationkernel or speedrun.');e['evidence'].append({'label':'All9ABIs/resources and changed fold entry','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),active_experiment='E114',stage=e['stage'],activity=e['reason']+' Live E080 unchanged, no new gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':'pass'if passed else'failed','failed_gates':[k for k,v in gates.items()if not v],'changed_entries':{a:[n for n,t in table.items()if not t['body_alpha_exact']]for a,table in tables.items()},'resource_warning_entries':[x['entry']for x in warnings]}),flush=True)
