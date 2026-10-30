import hashlib,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E099-resource';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
def entries(path):
 text=path.read_text();out={};i=0
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
def memory_ops(entry,name):
 origins={};out=[]
 for raw in entry.splitlines():
  t=raw.strip().split('//',1)[0].strip();m=re.fullmatch(r'ld\.param\.u64\s+(%\w+),\s*\['+name+r'_param_(\d+)\];',t)
  if m:origins[m[1]]={int(m[2])};continue
  m=re.search(r'\b(ld|st)\.global((?:\.[A-Za-z0-9_]+)*)\s+(.*);$',t)
  if m:
   rest=m[3];addr=re.search(r'\[(%\w+)(?:\+\d+)?\]',rest);params=origins.get(addr[1],set()) if addr else set();op=m[1]+'.global'+m[2];bits=64 if '.v2.' in op and re.search(r'\.(?:f32|b32|u32|s32)$',op) else 64 if re.search(r'\.(?:b64|u64|s64)$',op) else 32 if re.search(r'\.(?:f32|b32|u32|s32)$',op) else None
   if params:out.append({'kind':m[1],'opcode':op,'bits':bits,'parameters':sorted(params),'line':t})
   if m[1]=='ld':
    before=rest.split('[',1)[0]
    for reg in re.findall(r'%\w+',before):origins.pop(reg,None)
   continue
  m=re.match(r'(?:@!?%\w+\s+)?(?:add|sub|mul|mad|shl|shr|mov|cvt|cvta|selp|and|or|xor)(?:\.[A-Za-z0-9_]+)*\s+(%\w+),\s*(.*);$',t)
  if m:origins[m[1]]=set().union(*(origins.get(reg,set()) for reg in re.findall(r'%\w+',m[2])))
 return out
# Positive pointer selection/addressing and negative loaded-value/store/width controls.
sample='ld.param.u64 %rd1, [test_param_9];\nld.param.u64 %rd2, [test_param_10];\nselp.b64 %rd3, %rd1, %rd2, %p1;\nmad.wide.u32 %rd4, %r1, 4, %rd3;\nld.global.v2.f32 {%f1,%f2}, [%rd4];\nst.global.v2.f32 [%rd4], {%f1,%f2};\nld.global.u64 %rd5, [%rd4];\nld.global.u64 %rd6, [%rd5];'
fixtures=memory_ops(sample,'test');assert len(fixtures)==3 and all(x['parameters']==[9,10] for x in fixtures) and [x['kind'] for x in fixtures]==['ld','st','ld'] and all(x['bits']==64 for x in fixtures)
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid'] in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernel_launches':0})
 h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('E099_RESOURCE ',1)[1]) for x in (O/'probe.stdout.log').read_text().splitlines() if 'E099_RESOURCE ' in x];assert len(markers)==8 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete';rows={(r['variant'],r['kernel']):r for r in markers[1:-1]};assert len(rows)==6
tables={(v,a):entries(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']};gates={};unchanged={};proof={};warnings=[]
for arch in ['compute_120','compute_75']:
 b,c=tables['baseline',arch],tables['candidate',arch];assert set(b)==set(P['original_entries']) and set(c)==set(P['original_entries'])|set(P['new_entries']);unchanged[arch]={n:normalize(b[n])==normalize(c[n]) for n in b};gates[arch+':original9entries_alpha_exact']=all(unchanged[arch].values());proof[arch]={}
 for name,contract in P['new_entries'].items():
  old=contract['original'];bh=b[old].split('{',1)[0];ch=c[name].split('{',1)[0].replace(name,old);gates[arch+':'+name+':ABI_exact']=bh==ch and bh.count('.param ')==contract['parameter_count'];gates[arch+':'+name+':no_barriers']=c[name].count('bar.sync')==b[old].count('bar.sync')==0
  ops=memory_ops(c[name],name);vector=[x for x in ops if x['bits']==64];proof[arch][name]={'pointer_origin_64bit_operations':vector,'all_data_operations':ops};gates[arch+':'+name+':typed_v2_emitted']=any('.v2.' in x['opcode'] for x in vector)
  for kind,key in [('ld','paired_load_parameters'),('st','paired_store_parameters')]:
   present=set().union(*(set(x['parameters']) for x in vector if x['kind']==kind));gates[arch+':'+name+':'+key]=set(contract[key])<=present
for name,contract in P['new_entries'].items():
 b,c=rows['baseline',contract['original']],rows['candidate',name];same=rows['candidate',contract['original']];keys=['registers','local_bytes_per_thread','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads'];gates[name+':original_driver_resources_exact']=all(b[k]==same[k] for k in keys);bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads']);checks={'no_new_local_spill':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'no_dynamic_shared_growth':c['dynamic_shared_bytes']==b['dynamic_shared_bytes'],'no_maxthread_loss':c['max_threads']>=b['max_threads'],'positive_fixed_occupancies':all(bo[t]>0 and co[t]>0 for t in [64,128,256]),'default_limits_fit':b['fits_default_limits'] and c['fits_default_limits'],'no_stack_growth':c['context_stack_limit_after_load']<=b['context_stack_limit_after_load']};gates.update({name+':'+k:v for k,v in checks.items()})
 if c['registers']>b['registers'] or c['static_shared_bytes']>b['static_shared_bytes'] or any(co[t]<bo[t] for t in bo):warnings.append({'entry':name,'baseline':b,'candidate':c})
passed=all(gates.values());report={'id':'E099-resource','at':h.now(),'status':'pass_compiled_prerequisites' if passed else 'rejected_closed_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'original9entry_bodies':unchanged,'paired_memory_operations':proof,'resource_rows':list(rows.values()),'resource_warnings':warnings,'pointer_parser_positive_negative_fixture':fixtures,'PTX_sha256':{v+'-'+a:h.sha(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']},'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'source_activated':False,'candidate_accepted':False,'scope':'Compiled paired-memory instruction/ABI/original-entry and default resource feasibility only. No runtime numerical/launch/CPU/memory/capacity/speed/no-tradeoff claim. Any genuine mechanism/ABI/resource failure closes this exact form without width/arity/guard/entry/helper/flags/registercap/launchbound/source/sample rescue.'};h.save(H/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0});verify()
p=H/'report.json';dst=h.ar.DASHBOARD/'evidence'/H.name/p.name;assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='E099');item.update(status='running' if passed else 'rejected',stage='Compiler gate passed; raw numerical controls pending' if passed else 'Closed at compiled-resource/mechanism gate',correctness='not_numerically_tested',reason='Compiled gates passed: '+str(passed)+'. Failed: '+str([k for k,v in gates.items() if not v])+'. No application kernel or solve ran.');item['evidence'].append({'label':'Actual paired instructions and resource gates','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),active_experiment='E099',stage=item['stage'],activity='E099 compiler-only result published. Original E080 sources/server remain unchanged; no gain accepted.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items() if not v],'resources':[{'kernel':r['kernel'],'variant':r['variant'],'regs':r['registers'],'local':r['local_bytes_per_thread'],'max_threads':r['max_threads'],'occupancy':r['occupancy_by_threads']} for r in rows.values()]}),flush=True)
