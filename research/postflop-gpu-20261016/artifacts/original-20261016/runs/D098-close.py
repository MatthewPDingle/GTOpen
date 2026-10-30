"""Replay captured static code, preserve pre-native harness failure, publish diagnostic."""
import collections,json,re,struct,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
A=ROOT/'runs/D098-driver-machine-code';H=ROOT/'runs/D098-driver-machine-code-r2';E=H/'execution'
P=old.read(H/'protocol.json');q=old.read(H/'capture-report.json');checks=0
def check(v):
 global checks
 assert v;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h);checks+=1
check(q['protocol_sha256']==old.sha(H/'protocol.json'))
for label in ['cl']:
 check(old.read(H/'build'/(label+'.exit.json'))['returncode']==0)
for label in ['capture','nvdisasm-version','module-0-sass','module-0-json']:
 check(old.read(E/(label+'.exit.json'))['returncode']==0)
check(old.read(A/'build/cl.exit.json')['returncode']==2)
check(not list((A/'execution').glob('capture.*')))
check(old.read(H/'repair.json')['native_runs_before_repair']==0)
check(old.read(E/'complete.json')['all_owned_children_terminal'])
check(set(q['module_sha256'])=={'module-0.cubin'})
cubin=E/'module-0.cubin';old.pin(cubin,q['module_sha256'][cubin.name]);data=cubin.read_bytes()
check(data[:6]==b'\x7fELF\x02\x01');check(struct.unpack_from('<H',data,18)[0]==190)
head,functions=old.read(E/'module-0-json.stdout.log')
check(head['SM']['version']=={'major':12,'minor':0})
check('12.9.88' in head['Producer'])
check(head['.note.nv.tkinfo']['tki_toolName']=='ptxas')
byname={f['function-name']:f for f in functions};check(len(byname)==len(functions))
check(set(P['expected_entries']).issubset(byname))
check(len(set(byname)-set(P['expected_entries']))==5)
attrs={r['name']:r for r in q['markers']['D098_KERNEL']};check(set(attrs)==set(P['expected_entries']))
for name,row in attrs.items():
 check(row['binary_version']==row['ptx_version']==120)
 check(byname[name]['length']>0)
for r in q['markers']['D098_MODULE']:check(r['same_owned_context'] and r['elf_magic'] and r['bytes']==len(data))
end=q['markers']['D098_COMPLETE'][0];check(end=={'callback_errors':0,'modules':1,'kernel_launches':0,'solver_executions':0,'performance_measured':False})
counts={name:dict(collections.Counter(i.get('opcode','') for i in f['sass-instructions'])) for name,f in byname.items()}
s=byname['up_action']['sass-instructions'];rcp=[i for i,x in enumerate(s) if x.get('opcode')=='MUFU.RCP'];check(len(rcp)==17)
groups=[rcp[:2],rcp[-7:-4],rcp[-4:]];check([len(g) for g in groups]==[2,3,4])
proof=[]
for g in groups:
 denominator=[s[i]['operands'].split(',')[1].removesuffix('.reuse') for i in g]
 check(denominator==['R35']*len(g))
 writes=[]
 for i in range(g[0]+1,g[-1]):
  ins=s[i];op=ins.get('opcode','');first=ins.get('operands','').split(',')[0].removesuffix('.reuse')
  if first=='R35' and op not in ['BRA','CALL.REL.NOINC','STG.E']:writes.append(i)
 check(writes==[])
 proof.append({'reciprocal_indices':g,'denominator_register':'R35','lexical_explicit_writes_between':writes,'instructions':[{'index':i,'instruction':s[i]} for i in g],'scope':'Repeated same physical denominator register with no intervening explicit destination writes in these code windows. Does not prove all control-flow/slowpath call state or exact reusable arithmetic.'})
check(attrs['up_chance']['registers']==30 and attrs['up_chance']['local']==0)
check(attrs['up_action']['registers']==62 and attrs['up_action']['local']==64 and attrs['up_action']['occupancy64_128_256']==[16,8,4])
report={'id':'D098','at':old.now(),'status':'pass_static_source_matched_driver_diagnostic','checks_passed':checks,'capture_report_sha256':old.sha(H/'capture-report.json'),'protocol_sha256':old.sha(H/'protocol.json'),'input_ptx_sha256':q['input_ptx_sha256'],'cubin_sha256':old.sha(cubin),'cubin_bytes':len(data),'disassembler':head['Producer'],'driver_jit_tool_metadata':head['.note.nv.tkinfo'],'all9entry_symbols_and5internal_helpers':True,'entry_attributes':attrs,'instruction_counts':counts,'up_action_same_denominator_groups':proof,'conclusion':'Actual source-matched up_action SASS repeats reciprocal and refinement work for the same denominator in common2/3/4 paths. It does not already share every reciprocal. This supports examining a separately frozen reuse candidate, with guarded unchanged native-division fallback; no numerical equivalence or speed/admission result follows.','original_compile_failure_preserved':True,'native_capture_executions':1,'all_owned_children_terminal':True,'source_activated':False,'kernel_launches':0,'solver_executions':0,'performance_measured':False,'candidate_accepted':False,'accepted_source':'E051','accepted_cumulative_gain_pct':12.4372274192464,'limits':P['scope']}
R=ROOT/'comparisons/D098-static-root-check';R.mkdir();old.save(R/'report.json',report)
checkpoint={'at':old.now(),'goal_active':True,'accepted_source':'E051','last_primary_baseline':'B185','all_owned_children_terminal':True,'source_main_live_ptx_unchanged':True,'next':'Investigate one independent up_action common-arity shared reciprocal-refinement candidate. Preserve IEEE/native fallback for all values outside conservative positive-normal guard; retain exact FMA expression/order from observed driver fast division; require GPU raw division/kernel bit checks, all resource allocation constraints, unchanged initial/fresh16/broader/material/holdout/cumulative gates. Never treat direct multiplication by rounded reciprocal as exact. No historical candidate variants reopened.'}
old.save(H/'checkpoint.json',checkpoint)
published=[]
def put(p,prefix):
 key='evidence/'+prefix+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():check(dst.read_bytes()==p.read_bytes())
 else:dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=15) as response:check(response.read()==p.read_bytes())
 published.append({'path':str(p),'url':key,'sha256':old.sha(p)})
for p in [A/'protocol.json',A/'bootstrap.json',A/'probe.cpp',A/'execute.py']:put(p,A.name)
for p in (A/'build').iterdir():
 if p.is_file() and p.suffix in ['.json','.log']:put(p,'D098-original-build-failure')
for p in [H/'protocol.json',H/'repair.json',H/'probe.cpp',H/'execute.py',H/'capture-report.json',H/'checkpoint.json']:put(p,H.name)
for p in list((H/'build').iterdir())+list(E.iterdir()):
 if p.is_file() and p.suffix in ['.json','.log','.cubin']:put(p,'D098-'+p.parent.name+'-r2')
for p in [Path(__file__),ROOT/'runs/D098-prepare.py',ROOT/'runs/D098-repair-build.py']:put(p,'D098-preparation-sources')
put(R/'report.json',R.name)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='D098')
 e.update(status='passed',correctness='passed',notes='One owned source-matched CUBIN captured,9entries/5internal helpers disassembled, zero kernel launches. Common action paths repeat denominator reciprocal work. Original pre-native build/header failure retained and fixed. No speed or numerical-equivalence claim.',updated_at=old.now())
 e['evidence'].extend([{'label':'Static code/root replay','url':'evidence/'+R.name+'/report.json'},{'label':'Driver capture and exact inputs','url':'evidence/'+H.name+'/capture-report.json'},{'label':'Preserved build repair','url':'evidence/'+H.name+'/repair.json'},{'label':'Next-step checkpoint','url':'evidence/'+H.name+'/checkpoint.json'}])
 st.update(updated_at=old.now(),state='running',active_experiment=None,stage='Preparing exact reciprocal-reuse candidate',activity='D098 source-matched driver code shows repeated reciprocal refinement. No source change or new speed gain adopted; E051 cumulative12.437227% unchanged.')
 old.ar.atomic_json(old.ar.STATUS,st)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D098 source-matched driver' not in raw
note=f'''

### D098 source-matched driver CUBIN and reciprocal audit

Captured one owned off-tree module from the exact retained E051-source compute_120 PTX using cuModuleLoadData with default options, matching the cudarc loader API. Official CUPTI12.9.79 RESOURCE_MODULE_LOADED callback copies module bytes during callback lifetime; no CUDA calls in callback. No injection, live attachment, counters, elevation, kernel launches or solves. Private nvdisasm12.9.88 package comes from the pinned NVIDIA12.9.1 manifest/archive SHA955ba1f52f7115031f10408ce3cec4c745df41dba8fdf6024c3983d899e9fbbc. Driver-generated module metadata reports ptxas13.3.80/sm_120a; this is driver JIT metadata, not an installed toolchain update.

Original C++ build exited2 before any native capture because required crt/host_defines.h was not on the include path. Preserve source/protocol/logs/receipt; revision2 adds the already-retained NVCC headers and corrects a nonexistent down_eval function query to actual copy_span before native execution. Revision2 protocol95385401b37f48b17a1efdd25cba0bd5263fe31381f9b9d85d2cfbc7e6ff87c2; compiler, single capture, version, text and JSON disassembly all terminal0. No completed native capture repeated.

One195,184byte ELF contains all9entries and5internal division helpers. Up_action reports62registers/64local bytes and16/8/4active blocks at64/128/256threads; chance30registers/0local. Static up_action has17MUFU.RCP,16FCHK,17CALL sites. Common2/3/4 windows repeat2/3/4reciprocals of R35 with no explicit intervening writes to that denominator; observed division fast sequences use reciprocal refinement plus numerator-specific FMAs. Counts are static, not dynamic frequency or speed. Calls/exceptional inputs require separate exact treatment; a rounded reciprocal multiplication is not equivalent to division. Root{report['checks_passed']}checks SHA{old.sha(R/'report.json')}. Source/PTX-matched capture is not extraction from the frozen timed executable, and root replay is not independent external review.

Next consider one guarded shared-refinement candidate with native division fallback, GPU raw exactness and fixed allocation/resource gates before unchanged full1%/fixture/fresh16/broad/material/holdout/cumulative qualification. No optimization, precision or new performance claim from this diagnostic. All{len(published)}artifacts HTTP-byte verified. Accepted162/main157/live/protectedPTX unchanged, acceptedE051 cumulative12.4372274192%, lastprimaryB185. Goal active.
'''
newline=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+note.encode('utf-8').replace(b'\n',newline))
old.save(H/'publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'no_optimization_accepted':True});old.custody()
print(json.dumps({'status':report['status'],'checks':report['checks_passed'],'module_bytes':len(data),'repeated_same_denominator_groups':[len(g) for g in groups],'public_artifacts':len(published),'new_speed_gain':False}),flush=True)
