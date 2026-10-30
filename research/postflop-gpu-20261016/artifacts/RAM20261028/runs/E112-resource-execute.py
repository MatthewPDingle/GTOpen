import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E112-resource';P=h.read(H/'protocol.json');O=H/'execution';assert len(sys.argv)==2
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
def entries(path):
 t=path.read_text(encoding='utf-8');out={};i=0
 while True:
  i=t.find('.visible .entry ',i)
  if i<0:break
  a=t.index('(',i);name=t[i+len('.visible .entry '):a].strip();a=t.index('{',a);j=a+1;depth=1
  while depth:depth+=(t[j]=='{')-(t[j]=='}');j+=1
  assert name not in out;out[name]=t[i:j];i=j
 return out
def norm(t):
 t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',t);t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t);return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
def params(t):
 out=[]
 for l in t.split('{',1)[0].splitlines():
  if l.strip().startswith('.param '):
   m=re.fullmatch(r'\s*\.param\s+(.+?)\s+\w+_param_(\d+),?\s*',l);assert m,l;attrs=re.sub(r'\s+',' ',m[1]);assert int(m[2])==len(out);out.append(attrs)
 return out
verify();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
rows=[json.loads(x.split('E112_RESOURCE ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E112_RESOURCE 'in x];assert len(rows)==20 and rows[-1]['stage']=='complete';resources={(x['variant'],x['kernel']):x for x in rows if x['stage']=='resource'};symbol=[x for x in rows if x['stage']=='symbol'];assert len(resources)==18 and len(symbol)==1
gates={'symbol:actual12zero_initialized_bytes':symbol[0]['bytes']==12 and symbol[0]['actual_initial_bytes']==[0]*12};tables={}
for arch in ['compute_120','compute_75']:
 b=entries(H/('baseline-'+arch+'.ptx'));c=entries(O/('candidate-'+arch+'.ptx'));gates[arch+':entryset']=set(b)==set(c)==set(P['original_entries']);tables[arch]={}
 for name in P['original_entries']:
  old,new=params(b[name]),params(c[name]);tables[arch][name]={'old_parameter_attributes':old,'new_parameter_attributes':new,'entire_entry_alpha_exact':norm(b[name])==norm(c[name])}
  if name!='up_action':gates[arch+':'+name+':entire_entry_ABI_exact']=tables[arch][name]['entire_entry_alpha_exact']
  else:
   gates[arch+':up_action:declared_ABI_20_to_19']=len(old)==20 and len(new)==19 and old[17]=='.u64 .ptr .align 1'and old[:17]+old[18:]==new
   gates[arch+':up_action:constant_access_present']='ld.const.'in c[name]and'gto_postflop_discounts'in c[name]
   for arm,t in [('baseline',b[name]),('candidate',c[name])]: (O/(arm+'-'+arch+'-up_action.ptx.txt')).write_bytes(t.encode())
warnings=[]
for name in P['original_entries']:
 b,c=resources['baseline',name],resources['candidate',name];keys=['registers','local_bytes_per_thread','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','context_stack_after']
 if name!='up_action':gates[name+':original_resources_exact']=all(b[k]==c[k]for k in keys)
 else:
  bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads']);gates.update({name+':no_new_local':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],name+':no_dynamic_growth':c['dynamic_shared_bytes']==b['dynamic_shared_bytes'],name+':no_maxthread_loss':c['max_threads']>=b['max_threads'],name+':positive_fixed_occupancies':all(bo[t]>0 and co[t]>0 for t in[64,128,256]),name+':default_limits_fit':c['static_shared_bytes']+c['dynamic_shared_bytes']<=c['device_shared_limit']and c['max_threads']>=256 and c['device_thread_limit']>=256,name+':no_stack_growth':c['context_stack_after']<=b['context_stack_after']})
  if c['registers']>b['registers']or c['static_shared_bytes']>b['static_shared_bytes']or any(co[t]<bo[t]for t in bo):warnings.append({'entry':name,'baseline':b,'candidate':c})
passed=all(gates.values());h.save(H/'report.json',{'id':'E112-resource','at':h.now(),'status':'pass_scoped_constant_resources_ABI_operand_review_pending'if passed else'rejected_closed_fixed_constant_resources_or_ABI','protocol_sha256':sys.argv[1],'gates':gates,'entry_tables':tables,'resource_rows':list(resources.values()),'actual_constant_symbol':symbol[0],'resource_warnings':warnings,'constant_attribute_deltas':{n:resources['candidate',n]['constant_bytes']-resources['baseline',n]['constant_bytes']for n in P['original_entries']},'PTX_sha256':{arm+'-'+arch:h.sha((H if arm=='baseline'else O)/(arm+'-'+arch+'.ptx'))for arm in['baseline','candidate']for arch in['compute_120','compute_75']},'all_owned_children_terminal':True,'application_kernel_launches_solver_or_speed_samples':0,'candidate_accepted':False,'source_activated':False,'limits':P['scope']});h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernels':0});verify()
p=H/'report.json';dst=h.ar.DASHBOARD/'evidence'/H.name/p.name;shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E112');e.update(status='running'if passed else'rejected',stage='Constant resource/ABI gate passed; operand/host controls pending'if passed else'Closed at fixed constant resource/ABI gate',reason='Module-only pass='+str(passed)+'; failed gates='+str([k for k,v in gates.items()if not v])+'. All constant attribute and resource changes retained; no poker kernel or speed samples.');e['evidence'].append({'label':'Actual compiled resources and ABI','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),active_experiment='E112',stage=e['stage'],activity=e['reason']+' E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'pass':passed,'failed':[k for k,v in gates.items()if not v],'action_resources':[x for x in resources.values()if x['kernel']=='up_action']}),flush=True)
