import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E106-resource-host';P=h.read(H/'protocol.json');O=H/'execution'
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
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid'] in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernels':0})
 h.child(P['rustc_command'],O,'rustc',1200);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('E106_RESOURCE ',1)[1]) for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'E106_RESOURCE ' in x];assert len(markers)==20 and markers[0]['stage']=='host_layout' and markers[-1]['stage']=='complete';layout=markers[0];rows={(x['variant'],x['kernel']):x for x in markers if x['stage']=='resource'};assert len(rows)==18
gates={'actual_wrapper_within_prospective8byte_bound':0<=layout['wrapper_delta_bytes']<=8,'exact_baseline_wrapper':layout['baseline_wrapper_bytes']==4448,'helper16_and_static8bytes':layout['candidate']['argument_helper_bytes']==16 and layout['candidate']['static_zero_word_bytes']==8};tables={};warnings=[]
for arch in ['compute_120','compute_75']:
 b=entries(H/('baseline-'+arch+'.ptx'));c=entries(O/('candidate-'+arch+'.ptx'));assert set(b)==set(c)==set(P['original_entries']);tables[arch]={'unchanged_entries':{name:normalize(b[name])==normalize(c[name]) for name in b if name not in P['targets']}}
 gates[arch+':original6entries_exact']=all(tables[arch]['unchanged_entries'].values())
 for name,contract in P['targets'].items():
  gates[arch+':'+name+':ABI_exact']=b[name].split('{',1)[0]==c[name].split('{',1)[0] and c[name].split('{',1)[0].count('.param ')==contract['parameter_count'];gates[arch+':'+name+':no_new_barriers']=b[name].count('bar.sync')==c[name].count('bar.sync')==0
  for arm,entry in [('baseline',b[name]),('candidate',c[name])]:
   (O/(arm+'-'+arch+'-'+name+'.ptx.txt')).write_text(entry,encoding='utf-8',newline='\n')
for name in P['original_entries']:
 b,c=rows['baseline',name],rows['candidate',name];keys=['registers','local_bytes_per_thread','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','context_stack_after']
 if name not in P['targets']:gates[name+':original_resources_exact']=all(b[k]==c[k] for k in keys)
 else:
  bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads']);checks={'no_new_local_spill':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'no_dynamic_shared_growth':c['dynamic_shared_bytes']==b['dynamic_shared_bytes'],'no_maxthread_loss':c['max_threads']>=b['max_threads'],'positive_fixed_occupancies':all(bo[t]>0 and co[t]>0 for t in [64,128,256]),'default_limits_fit':c['static_shared_bytes']+c['dynamic_shared_bytes']<=c['device_shared_limit'] and c['max_threads']>=256 and c['device_thread_limit']>=256,'no_stack_growth':c['context_stack_after']<=b['context_stack_after']};gates.update({name+':'+k:v for k,v in checks.items()})
  if c['registers']>b['registers'] or c['static_shared_bytes']>b['static_shared_bytes'] or any(co[t]<bo[t] for t in bo):warnings.append({'entry':name,'baseline':b,'candidate':c})
passed=all(gates.values());report={'id':'D214-E106','at':h.now(),'status':'pass_host_layout_and_compiled_resources_mechanism_pending' if passed else 'rejected_closed_host_layout_or_compiled_resource','protocol_sha256':sys.argv[1],'gates':gates,'actual_host_layout':layout,'entry_tables':tables,'resource_rows':list(rows.values()),'resource_warnings':warnings,'PTX_sha256':{v+'-'+a:h.sha((H if v=='baseline' else O)/(v+'-'+a+'.ptx')) for v in ['baseline','candidate'] for a in ['compute_120','compute_75']},'all_owned_children_terminal':True,'GPU_solver_constructor_calls':0,'application_kernel_launches':0,'solver_executions':0,'performance_samples':0,'source_activated':False,'candidate_accepted':False,'scope':'Full host typechecking/codegen/layout and CUDA resource/unchanged6entry/modifiedABI prerequisite only. Nullable-lock semantic CFG proof required before any application kernel. All raw/numeric/material/complete1%/strictfixture/fresh16/broad/holdout/cumulative/application requirements remain; no rescue after genuine failure.'};h.save(H/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernels':0});verify()
p=H/'report.json';dst=h.ar.DASHBOARD/'evidence'/H.name/p.name;assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS)
 for ident in ['D214','E106']:
  item=next(x for x in s['experiments'] if x['id']==ident);item.update(status='measured' if passed else 'rejected',stage='Host layout and resources passed; pointer semantics pending' if passed else 'Closed at host/resource gate',correctness='no_numerical_tests_yet',reason='Compiled gate: '+str(passed)+'. Failed: '+str([k for k,v in gates.items() if not v])+'. Actual wrapper delta '+str(layout['wrapper_delta_bytes'])+' bytes. No GPU solver constructor or application kernel.');item.setdefault('evidence',[]).append({'label':'Actual host layout and compiler resources','url':'evidence/'+H.name+'/report.json'})
 s.update(updated_at=h.now(),active_experiment='E106',stage='No-lock pointer semantics prerequisite' if passed else 'No-lock compiler gate closed',activity='Host/resource result published. Accepted E080 sources and live server remain unchanged; no gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items() if not v],'host_layout':layout,'modified_resources':[rows[v,n] for n in P['targets'] for v in ['baseline','candidate']]}),flush=True)
