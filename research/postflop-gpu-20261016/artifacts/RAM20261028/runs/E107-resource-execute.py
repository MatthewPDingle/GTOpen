import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E107-resource';P=h.read(H/'protocol.json');O=H/'execution'
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
def payout_loads(t):
 # Static conservative provenance, not a dynamic scheduling or SASS proof.
 origins={};loads=[];barriers=0
 for line_no,line in enumerate(t.splitlines(),1):
  code=line.split('//',1)[0].strip()
  if 'bar.sync' in code:barriers+=1
  m=re.match(r'(?:@!?%p\d+\s+)?([a-z][a-z0-9_.]*)\s+([^;]+);$',code)
  if not m:continue
  op=m[1];operands=[x.strip()for x in m[2].split(',')];dest=operands[0];refs=set()
  for operand in operands[1:]:
   for register in re.findall(r'%rd\d+',operand):refs|=origins.get(register,set())
  if op.startswith('ld.global.'):
   for param in sorted(refs):loads.append({'parameter':param,'line':line_no,'preceding_barriers':barriers,'opcode':op,'code':code})
  if dest.startswith('%rd'):
   if op=='ld.param.u64':
    p=re.fullmatch(r'\[up_show_param_(\d+)\]',operands[1]);origins[dest]={int(p[1])}if p and int(p[1])in [3,4,5]else set()
   elif op in ['cvta.to.global.u64','mov.u64','add.s64','add.u64']:origins[dest]=refs
   else:origins[dest]=set()
 return {'barriers':barriers,'loads':loads,'limits':'Conservative static alias/placement witness only. Driver scheduling and all numerical/complete-cycle qualification remain unproved.'}
fixture='''ld.param.u64 %rd1, [up_show_param_3];
cvta.to.global.u64 %rd2, %rd1;
add.s64 %rd3, %rd2, %rd99;
ld.global.nc.f32 %f1, [%rd3];
bar.sync 0;
ld.param.u64 %rd4, [up_show_param_4];
mov.u64 %rd5, %rd4;
ld.global.f32 %f2, [%rd5];
ld.param.u64 %rd6, [up_show_param_5];
mov.u64 %rd6, 0;
ld.global.f32 %f3, [%rd6];'''
f=payout_loads(fixture);assert[(x['parameter'],x['preceding_barriers'])for x in f['loads']]==[(3,0),(4,1)]and f['barriers']==1
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid']in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernels':0})
 h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('E107_RESOURCE ',1)[1])for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if 'E107_RESOURCE 'in x];assert len(markers)==19 and markers[-1]['stage']=='complete';rows={(x['variant'],x['kernel']):x for x in markers[:-1]};assert len(rows)==18
gates={};tables={};mechanism={};warnings=[]
for arch in ['compute_120','compute_75']:
 b=entries(H/('baseline-'+arch+'.ptx'));c=entries(O/('candidate-'+arch+'.ptx'));assert set(b)==set(c)==set(P['original_entries']);t=P['target_entry'];tables[arch]={'unchanged_entries':{n:normalize(b[n])==normalize(c[n])for n in b if n!=t},'target_alpha_exact':normalize(b[t])==normalize(c[t])}
 gates[arch+':original8entries_exact']=all(tables[arch]['unchanged_entries'].values());gates[arch+':target_ABI_exact']=b[t].split('{',1)[0]==c[t].split('{',1)[0] and c[t].split('{',1)[0].count('.param ')==P['parameter_count']
 mechanism[arch]={}
 for arm,entry in [('baseline',b[t]),('candidate',c[t])]:
  (O/(arm+'-'+arch+'-showdown.ptx.txt')).write_bytes(entry.encode('utf-8'));m=payout_loads(entry);mechanism[arch][arm]=m
  gates[arch+':'+arm+':five_barriers']=m['barriers']==5
  gates[arch+':'+arm+':all_payout_loads_identified_once']=len(m['loads'])==3 and sorted(x['parameter']for x in m['loads'])==[3,4,5]and all(x['opcode']in ['ld.global.f32','ld.global.nc.f32']for x in m['loads'])
  gates[arch+':'+arm+':intended_payout_placement']=all(x['preceding_barriers']==(5 if arm=='baseline'else 0)for x in m['loads'])and len(m['loads'])==3
for name in P['original_entries']:
 b,c=rows['baseline',name],rows['candidate',name];keys=['registers','local_bytes_per_thread','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','context_stack_after']
 if name!=P['target_entry']:gates[name+':actual_original_resources_exact']=all(b[k]==c[k]for k in keys)
 else:
  bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads']);gates.update({'target:no_new_local_spill':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'target:no_dynamic_shared_growth':c['dynamic_shared_bytes']==b['dynamic_shared_bytes'],'target:no_maxthread_loss':c['max_threads']>=b['max_threads'],'target:positive_fixed_occupancies':all(bo[t]>0 and co[t]>0 for t in [64,128,256]),'target:default_limits_fit':c['static_shared_bytes']+c['dynamic_shared_bytes']<=c['device_shared_limit']and c['max_threads']>=256 and c['device_thread_limit']>=256,'target:no_stack_growth':c['context_stack_after']<=b['context_stack_after']})
  if c['registers']>b['registers']or c['static_shared_bytes']>b['static_shared_bytes']or any(co[t]<bo[t]for t in bo):warnings.append({'entry':name,'baseline':b,'candidate':c})
passed=all(gates.values());report={'id':'E107-resource','at':h.now(),'status':'pass_compiled_prerequisites_numerical_pending'if passed else'rejected_closed_compiled_mechanism_or_resource_gate','protocol_sha256':sys.argv[1],'gates':gates,'entry_tables':tables,'payout_load_mechanism':mechanism,'parser_fixture':f,'resource_rows':list(rows.values()),'resource_warnings':warnings,'PTX_sha256':{v+'-'+a:h.sha((H if v=='baseline'else O)/(v+'-'+a+'.ptx'))for v in ['baseline','candidate']for a in ['compute_120','compute_75']},'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_samples':0,'source_activated':False,'candidate_accepted':False,'failure_policy':'A genuine failure closes frozen declaration relocation. No placement, volatile, asm, helper, flags, cache hint, entry subset or sample rescue.','limits':'Static placement and driver resource gate only; not device instruction scheduling, numerical equivalence or speed. All downstream exactness, complete-cycle, broad, material, holdout, cumulative and app qualification remain if passed.'};h.save(H/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernels':0});verify()
p=H/'report.json';dst=h.ar.DASHBOARD/'evidence'/H.name/p.name;assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20)as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments']if x['id']=='E107');item.update(status='running'if passed else'rejected',stage='Compiled prerequisite passed; driver semantics and numerical controls pending'if passed else'Closed at emitted scheduling/resource gate',correctness='no_candidate_numerical_tests_yet',reason='Compiled prerequisite pass: '+str(passed)+'. Failed gates: '+str([k for k,v in gates.items()if not v])+'. No application kernel or solve ran.');item.setdefault('evidence',[]).append({'label':'Emitted scheduling and actual driver resources','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),active_experiment='E107',stage=item['stage'],activity='E107 compiled result retained. E080 source and live server remain unchanged. No new gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'entry_tables':tables,'mechanism':mechanism,'target_resources':[rows[v,P['target_entry']]for v in ['baseline','candidate']]}),flush=True)
