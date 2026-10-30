import sys,json,re,hashlib,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E096-resource';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
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
def cfv_loads(entry,name,param):
 origins={};loads=[]
 for raw in entry.splitlines():
  t=raw.strip().split('//',1)[0].strip();m=re.fullmatch(r'ld\.param\.u64\s+(%\w+),\s*\['+name+r'_param_('+str(param)+r')\];',t)
  if m:origins[m[1]]={int(m[2])};continue
  m=re.search(r'\b(ld\.global(?:\.[A-Za-z0-9_]+)*)\.(f|u|b)(32|64)\s+(%\w+),\s*\[(%\w+)(?:\+\d+)?\];',t)
  if m:
   if origins.get(m[5]):loads.append({'parameters':sorted(origins[m[5]]),'bits':int(m[3]),'type':m[2],'opcode':m[1]+'.'+m[2]+m[3],'line':t})
   origins.pop(m[4],None);continue
  m=re.match(r'(?:@!?%\w+\s+)?(?:add|sub|mul|mad|shl|shr|mov|cvt|cvta)(?:\.[A-Za-z0-9_]+)*\s+(%\w+),\s*(.*);$',t)
  if m:origins[m[1]]=set().union(*(origins.get(reg,set()) for reg in re.findall(r'%\w+',m[2])))
 return loads
fixtures=[]
for name,param in [('up_chance',12),('up_action',16),('up_action_eval',14)]:
 for cache in ['', '.cg']:
  sample=f'ld.param.u64 %rd1, [{name}_param_{param}];\ncvta.to.global.u64 %rd2, %rd1;\nmad.wide.u32 %rd3, %r8, 4, %rd2;\nld.global{cache}.f32 %f1, [%rd3];\nmov.b32 %r4, %f1;\ncvt.u64.u32 %rd5, %r4;\nld.global.f32 %f2, [%rd5];\nst.global.f32 [%rd3], %f2;'
  result=cfv_loads(sample,name,param);assert len(result)==1 and result[0]['opcode']=='ld.global'+cache+'.f32' and result[0]['bits']==32;assert cfv_loads(sample,name,param+1)==[];fixtures.append({'entry':name,'cache':cache,'positive_cvta_mad_and_negative_wrongparam_loadedvalue_store_checks':True})
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid'] in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernel_launches':0})
 h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(s.split('E096_RESOURCE ',1)[1]) for s in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'E096_RESOURCE ' in s];assert len(markers)==8 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete';rows={(r['variant'],r['kernel']):r for r in markers[1:-1]};assert len(rows)==6
tables={(v,a):entries(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries']) for t in tables.values());gates={};other={};proof={};warnings=[]
for arch in ['compute_120','compute_75']:
 b,c=tables['baseline',arch],tables['candidate',arch];other[arch]={n:normalize(b[n])==normalize(c[n]) for n in b if n not in P['targets']};gates[arch+':other6entries_exact']=len(other[arch])==6 and all(other[arch].values());proof[arch]={}
 for name,contract in P['targets'].items():
  bh,ch=b[name].split('{',1)[0],c[name].split('{',1)[0];gates[arch+':'+name+':ABI_exact']=bh==ch and bh.count('.param ')==contract['parameters'];gates[arch+':'+name+':barriers_exact']=b[name].count('bar.sync')==c[name].count('bar.sync');bl=cfv_loads(b[name],name,contract['cfv_param']);cl=cfv_loads(c[name],name,contract['cfv_param']);proof[arch][name]={'baseline':bl,'candidate':cl};gates[arch+':'+name+':intended_CFV_cg32_loads']=bool(bl) and bool(cl) and all(x['bits']==32 for x in bl+cl) and any('.cg.' not in x['opcode'] for x in bl) and all('.cg.' in x['opcode'] for x in cl)
for name in P['targets']:
 b,c=rows['baseline',name],rows['candidate',name];bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads']);checks={'no_new_local_spill':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'no_dynamic_shared_increase':c['dynamic_shared_bytes']<=b['dynamic_shared_bytes'],'max_threads_not_lowered':c['max_threads']>=b['max_threads'],'positive_fixed_occupancies':all(bo[t]>0 and co[t]>0 for t in [64,128,256]),'both_fit_default_limits':b['fits_default_limits'] and c['fits_default_limits'],'no_stack_growth':c['context_stack_limit_after_load']<=b['context_stack_limit_after_load']};gates.update({name+':'+k:v for k,v in checks.items()})
 if c['registers']>b['registers'] or c['static_shared_bytes']>b['static_shared_bytes'] or any(co[t]<bo[t] for t in bo):warnings.append({'entry':name,'baseline':b,'candidate':c})
passed=all(gates.values());report={'id':'E096-resource','at':h.now(),'status':'pass_compiled_prerequisites' if passed else 'rejected_closed_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'CFV_pointer_load_proof':proof,'other6entry_bodies':other,'resource_rows':list(rows.values()),'resource_warnings':warnings,'parser_fixtures':fixtures,'ptx_sha256':{v+'-'+a:h.sha(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']},'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'scope':'Coherent cache load source compiled mechanism/ABI/otherentries/device feasibility only, no numerical or speed claim. All resource differences disclosed underD108. Any genuine failure closes exacthintform withoutcacheop/entrysubset/flags/source rescue. Passing requires fullrawphysics/samequalityspeed/adoption before gain.'};h.save(H/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0});verify()
dest=h.ar.DASHBOARD/'evidence'/H.name/'report.json';assert not dest.exists();shutil.copyfile(H/'report.json',dest)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/report.json',timeout=20) as response:assert response.read()==(H/'report.json').read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='E096');item.update(status='running' if passed else 'rejected',stage='Compiled mechanism/resources passed; full raw controls next' if passed else 'Compiled prerequisite failed; form closed',reason='IntendedCFV.cg32/ABI/unaffected6entries/resource gates: '+str(passed)+'. No applicationkernels/accuracy/speed measured. Failedgates: '+str([k for k,v in gates.items() if not v]));item['evidence'].append({'label':'Compiled CFV loads and actual resources','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),stage=item['stage'],activity='E080/16 unchanged, no newgainadopted. E096 compileonly result published.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items() if not v],'load_counts':{a:{n:{v:len(x) for v,x in row.items()} for n,row in p.items()} for a,p in proof.items()},'resources':[{'entry':r['kernel'],'variant':r['variant'],'regs':r['registers'],'local':r['local_bytes_per_thread'],'occupancy':r['occupancy_by_threads']} for r in rows.values()]}),flush=True)
