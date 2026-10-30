import sys,json,re,hashlib,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D170-offset-width';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.custody();h.pin(H/'protocol.json',sys.argv[1])
 for path,digest in P['input_sha256'].items():h.pin(path,digest)
def entries(path):
 text=path.read_text(encoding='utf-8');out={};i=0
 while True:
  i=text.find('.visible .entry ',i)
  if i<0:break
  n=text.index('(',i);name=text[i+len('.visible .entry '):n].strip();a=text.index('{',n);j=a+1;depth=1
  while depth:
   if text[j]=='{':depth+=1
   elif text[j]=='}':depth-=1
   j+=1
  assert name not in out;out[name]=text[i:j];i=j
 return out
def normalize(t):
 t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',t);t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t);return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
def pointer_loads(entry,name,param):
 origins={};loads=[]
 for raw in entry.splitlines():
  t=raw.strip().split('//',1)[0].strip();m=re.fullmatch(r'ld\.param\.u64\s+(%\w+),\s*\['+name+r'_param_('+str(param)+r')\];',t)
  if m:origins[m[1]]={int(m[2])};continue
  m=re.search(r'\bld\.global(?:\.[A-Za-z0-9_]+)*\.(u|b)(16|32|64)\s+(%\w+),\s*\[(%\w+)(?:\+\d+)?\];',t)
  if m:
   if origins.get(m[4]):loads.append({'parameters':sorted(origins[m[4]]),'bits':int(m[2]),'line':t})
   origins.pop(m[3],None);continue
  m=re.match(r'(?:@!?%\w+\s+)?(?:add|sub|mul|mad|shl|shr|mov|cvt|cvta)(?:\.[A-Za-z0-9_]+)*\s+(%\w+),\s*(.*);$',t)
  if m:origins[m[1]]=set().union(*(origins.get(reg,set()) for reg in re.findall(r'%\w+',m[2])))
 return loads
parser_fixtures=[]
for name,param in [('down_action',5),('up_action',6),('up_action_eval',7)]:
 for bits in [32,64]:
  sample=f'ld.param.u64 %rd1, [{name}_param_{param}];\ncvta.to.global.u64 %rd2, %rd1;\nmad.wide.u32 %rd3, %r8, 4, %rd2;\nld.global.nc.u{bits} %r1, [%rd3];\ncvt.u64.u32 %rd4, %r1;\nld.global.nc.u32 %r2, [%rd4];'
  result=pointer_loads(sample,name,param);assert len(result)==1 and result[0]['bits']==bits
  assert pointer_loads(sample,name,param+1)==[];parser_fixtures.append({'kernel':name,'bits':bits,'positive_and_wrong_param_and_loaded_value_checks':True})
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
 gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid'] in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernel_launches':0})
 h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
 h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(line.split('D170_RESOURCE ',1)[1]) for line in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'D170_RESOURCE ' in line]
assert len(markers)==8 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==6
tables={(v,a):entries(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries']) for t in tables.values());gates={};proof={};other={};warnings=[]
for arch in ['compute_120','compute_75']:
 b,c=tables['baseline',arch],tables['candidate',arch];other[arch]={n:normalize(b[n])==normalize(c[n]) for n in b if n not in P['targets']};gates[arch+':other6entries_exact']=len(other[arch])==6 and all(other[arch].values());proof[arch]={}
 for n,contract in P['targets'].items():
  bh,ch=b[n].split('{',1)[0],c[n].split('{',1)[0];gates[arch+':'+n+':ABI_exact']=bh==ch and bh.count('.param ')==contract['parameters'];gates[arch+':'+n+':CTA_barriers_exact']=b[n].count('bar.sync')==c[n].count('bar.sync')
  bl=pointer_loads(b[n],n,contract['param']);cl=pointer_loads(c[n],n,contract['param']);proof[arch][n]={'baseline':bl,'candidate':cl}
  gates[arch+':'+n+':intended_u64_to_u32_loads']=bool(bl) and bool(cl) and all(x['bits']==64 for x in bl) and all(x['bits']==32 for x in cl)
for n in P['targets']:
 b,c=rows['baseline',n],rows['candidate',n];bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads'])
 checks={'no_new_local_or_spill':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'no_dynamic_shared_increase':c['dynamic_shared_bytes']<=b['dynamic_shared_bytes'],'max_threads_not_lowered':c['max_threads']>=b['max_threads'],'positive_fixed_occupancies':all(bo[t]>0 and co[t]>0 for t in [64,128,256]),'both_fit_default_limits':b['fits_default_limits'] and c['fits_default_limits'],'no_stack_growth':c['context_stack_limit_after_load']<=b['context_stack_limit_after_load']}
 gates.update({n+':'+k:v for k,v in checks.items()})
 if c['registers']>b['registers'] or c['static_shared_bytes']>b['static_shared_bytes'] or any(co[t]<bo[t] for t in bo):warnings.append({'kernel':n,'baseline':b,'candidate':c})
passed=all(gates.values());report={'id':'D170','at':h.now(),'status':'pass_compiled_prerequisites' if passed else 'rejected_closed_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'pointer_load_proof':proof,'other6entries':other,'resource_rows':list(rows.values()),'resource_warnings':warnings,'parser_fixtures':parser_fixtures,'ptx_sha256':{v+'-'+a:h.sha(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']},'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'scope':'Compile/module/load/ABI/intended offset-load width/resource feasibility only. Actual resource differences disclosed under D108. No scientific equivalence, actual capacity/speed or main integration claim. Future admitted work requires separately frozen full numerical and wide-fallback/host ownership proof, complete speed and all adoption gates. No real failure rescue.'}
h.save(H/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0});verify()
p=H/'report.json';dest=h.ar.DASHBOARD/'evidence'/H.name/p.name;assert not dest.exists();shutil.copyfile(p,dest)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/report.json',timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D170');item.update(status='measured' if passed else 'rejected',stage='Compile prerequisite passed; numerical controls next' if passed else 'Compiled prerequisite failed; form closed',reason='Actual pointer-load width/ABI/unaffected entry/resource checks completed; no application kernels or speed samples. Failed gates: '+str([k for k,v in gates.items() if not v]));item['evidence'].append({'label':'Compiled mechanism and resources','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),stage=item['stage'],activity='E080/16 unchanged. D170 compile-only result published; no new gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items() if not v],'resources':[{'variant':r['variant'],'kernel':r['kernel'],'registers':r['registers'],'local':r['local_bytes_per_thread'],'occupancy':r['occupancy_by_threads']} for r in rows.values()]}),flush=True)
