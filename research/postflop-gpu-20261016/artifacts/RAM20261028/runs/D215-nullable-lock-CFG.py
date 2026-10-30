"""Conservative static lock-pointer reachability only; never CUDA execution."""
import collections,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D215-nullable-lock-CFG';RESOURCE=ROOT/'runs/E106-resource-host'

def parse(text):
 body=text[text.index('{')+1:text.rindex('}')];instructions=[];labels={}
 for raw in body.splitlines():
  s=raw.split('//',1)[0].strip()
  if not s or s[0] in '.{}':continue
  if s.endswith(':'):assert s[:-1] not in labels;labels[s[:-1]]=len(instructions);continue
  assert s.endswith(';'),s
  pred=None;m=re.match(r'@(!)?(%p\d+)\s+(.*)',s)
  if m:pred=(m[2],bool(m[1]));s=m[3]
  parts=re.split(r'\s+',s[:-1],maxsplit=1);op=parts[0];args=parts[1].strip() if len(parts)>1 else '';instructions.append({'op':op,'args':args,'pred':pred,'raw':raw.strip()})
 assert instructions and any(x['op']=='ret' for x in instructions)
 for x in instructions:
  assert not x['op'].startswith(('brx','call','jmp')),x['raw']
  if x['op'].startswith('bra'):assert x['args'] in labels,x['raw']
 return instructions,labels

def analyze(text,name,param,absent):
 ins,labels=parse(text);base=set();alias=set();loads=[];nh=set()
 for x in ins:
  m=re.fullmatch(r'(%\w+),\s*\['+re.escape(name)+r'_param_(\d+)\]',x['args'])
  if x['op'].startswith('ld.param.') and m:
   if int(m[2])==param:base.add(m[1]);alias.add(m[1])
   if int(m[2])==15:nh.add(m[1])
 assert base,'target pointer parameter loaded'
 # Monotone conservative pointer-origin closure. Memory values are not pointers.
 # Local pointer spills, calls and indirect control transfer are unsupported.
 taint=set(base);arithmetic=('mov.','cvt.','cvta.','add.','sub.','mul.','mad.','shl.','shr.','selp.','and.','or.','xor.')
 for _ in range(len(ins)+1):
  old=(set(taint),set(alias))
  for x in ins:
   regs=re.findall(r'%\w+',x['args']);op=x['op']
   if not regs:continue
   if op.startswith(arithmetic) and any(r in taint for r in regs[1:]):taint.add(regs[0])
   if op.startswith(('mov.','cvta.')) and len(regs)==2 and regs[1] in alias:alias.add(regs[0])
  if old==(taint,alias):break
 else:raise AssertionError('origin closure convergence')
 for pc,x in enumerate(ins):
  regs=re.findall(r'%\w+',x['args']);op=x['op']
  if op.startswith('st.local'):assert not any(r in taint for r in regs[1:]),'unsupported pointer spill'
  if op.startswith('ld.global'):
   m=re.search(r'\[(%\w+)(?:[+-]\d+)?\]',x['args']);assert m,x['raw']
   if m[1] in taint:loads.append(pc)
  # Any unknown instruction consuming the pointer prevents a positive proof.
  if op.startswith(('ld.','st.','setp.','bra','ret')) or op.startswith(arithmetic):continue
  if any(r in taint for r in regs[1:]):raise AssertionError(('unsupported pointer operation',x['raw']))
 assert loads,'actual lock-offset load sites found'
 known={};witness=[]
 for pc,x in enumerate(ins):
  m=re.fullmatch(r'(%p\d+),\s*(%\w+),\s*0',x['args'])
  relation=re.fullmatch(r'setp\.(eq|ne)\.[sbu]64',x['op'])
  if m and relation and m[2] in alias:
   assert m[1] not in known;known[m[1]]=absent if relation[1]=='eq' else not absent;witness.append({'pc':pc,'instruction':x['raw'],'pointer_parameter':param,'known_predicate':known[m[1]]})
 if not absent:assert known or loads
 reached=set();executed=set();edges=[];todo=[0]
 while todo:
  pc=todo.pop()
  if pc in reached or pc==len(ins):continue
  assert 0<=pc<len(ins);reached.add(pc);x=ins[pc];condition=None
  if x['pred']:
   p,neg=x['pred'];condition=known.get(p)
   if condition is not None and neg:condition=not condition
  if x['pred'] is None or condition is not False:executed.add(pc)
  if x['op']=='ret':nexts=[] if x['pred'] is None or condition is True else [pc+1]
  elif x['op'].startswith('bra'):
   target=labels[x['args']]
   nexts=[target] if x['pred'] is None or condition is True else [pc+1] if condition is False else [target,pc+1]
  else:nexts=[pc+1]
  edges.extend((pc,n) for n in nexts);todo.extend(nexts)
 return {'parameter':param,'base_parameter_registers':sorted(base),'pointer_alias_registers':sorted(alias),'all_static_lock_load_sites':[{'pc':pc,'instruction':ins[pc]['raw']} for pc in loads],'reachable_lock_load_sites':[{'pc':pc,'instruction':ins[pc]['raw']} for pc in loads if pc in executed],'known_pointer_guards':witness,'reachable_instruction_count':len(reached),'conservative_unknown_branches_take_both_successors':True,'total_instructions':len(ins),'direct_CFG_edges':len(edges),'null_argument':absent}

def calibrate():
 sample='''.visible .entry test(.param .u64 test_param_12){
 ld.param.u64 %rd1, [test_param_12];
 mov.u64 %rd2, %rd1;
 setp.eq.s64 %p1, %rd2, 0;
 @%p1 bra DONE;
 cvta.to.global.u64 %rd3, %rd1;
 add.u64 %rd4, %rd3, %rd99;
 ld.global.u64 %rd5, [%rd4];
 DONE:
 ret;
 }'''
 assert not analyze(sample,'test',12,True)['reachable_lock_load_sites'];assert len(analyze(sample,'test',12,False)['reachable_lock_load_sites'])==1
 bad1=sample.replace('@%p1 bra DONE;','@!%p1 bra DONE;');assert analyze(bad1,'test',12,True)['reachable_lock_load_sites']
 bad2=sample.replace('@%p1 bra DONE;','@%p99 bra DONE;');assert analyze(bad2,'test',12,True)['reachable_lock_load_sites']
 bad3=sample.replace('setp.eq.s64 %p1, %rd2, 0;','setp.eq.s64 %p1, %rd77, 0;');assert analyze(bad3,'test',12,True)['reachable_lock_load_sites']
 bad4=sample.replace('DONE:\n ret;','DONE:\n ld.global.u64 %rd7, [%rd1];\n ret;');assert analyze(bad4,'test',12,True)['reachable_lock_load_sites']
 bad5=sample.replace('ret;','call.uni f;\n ret;')
 try:analyze(bad5,'test',12,True)
 except AssertionError:pass
 else:raise AssertionError('unsupported call calibration')
 return {'static_cases':7,'positive_null_and_present':True,'inverted_guard_unknown_guard_wrong_pointer_and_unguarded_alias_load_detected':True,'opaque_call_rejected':True,'scope':'Conservative pointer alias closure and direct CFG/null-predicate model only. Numeric memory values/FP predicates/general pointer bounds are not simulated.'}

h.custody();assert not(ROOT/'gpu-run.lock').exists();r=h.read(RESOURCE/'report.json');assert r['status']=='pass_host_layout_and_compiled_resources_mechanism_pending';assert h.read(RESOURCE/'execution/complete.json')['all_owned_children_terminal']
if sys.argv[1:]==['--freeze']:
 H.mkdir(exist_ok=False);h.save(H/'calibration.json',calibrate());paths=[Path(__file__),H/'calibration.json',RESOURCE/'protocol.json',RESOURCE/'report.json',RESOURCE/'execution/complete.json',ROOT/'runs/E106-source-r2/source-review.json',ROOT/'runs/E106-source-r2/manifest.json',ROOT/'epoch/common.py']+[p for p in (RESOURCE/'execution').glob('*-*.ptx.txt')]
 h.save(H/'protocol.json',{'id':'D215','at':h.now(),'status':'FROZEN_BEFORE_FIRST_WHOLE_PTX_CFG_READER','targets':h.read(RESOURCE/'protocol.json')['targets'],'input_sha256':{str(p):h.sha(p) for p in paths},'required_result':'For both120/75 and all3targets, original null argument retains reachable lock-offset reads (positive control), candidate null has none and at least one recognized guard, candidate present keeps reachable original reads. Unknown other branches take both successors. No numeric/FP equivalence or native liveness claim.','source_and_shader_fixed_before_compiler':True,'GPU_kernel_or_speed_runs':0});print(h.sha(H/'protocol.json'),flush=True);sys.exit(0)
assert len(sys.argv)==3 and sys.argv[1]=='--run';P=h.read(H/'protocol.json');h.pin(H/'protocol.json',sys.argv[2])
for p,d in P['input_sha256'].items():h.pin(p,d)
assert calibrate()==h.read(H/'calibration.json');cases=[]
for arch in ['compute_120','compute_75']:
 for name,contract in P['targets'].items():
  analyses={}
  for arm,absent,key in [('baseline',True,'original_zero_argument_positive_control'),('candidate',True,'candidate_null'),('candidate',False,'candidate_present')]:
   p=RESOURCE/'execution'/(arm+'-'+arch+'-'+name+'.ptx.txt');analyses[key]=analyze(p.read_text(encoding='utf-8'),name,contract['lock_pointer_parameter'],absent)
  gates={'baseline_lock_reads_detected':bool(analyses['original_zero_argument_positive_control']['reachable_lock_load_sites']),'candidate_zero_lock_reads':not analyses['candidate_null']['reachable_lock_load_sites'],'candidate_null_guard_detected':bool(analyses['candidate_null']['known_pointer_guards']),'candidate_present_lock_reads_detected':bool(analyses['candidate_present']['reachable_lock_load_sites'])};cases.append({'architecture':arch,'kernel':name,'gates':gates,'analyses':analyses})
passed=all(all(x['gates'].values()) for x in cases);h.save(H/'report.json',{'id':'D215','at':h.now(),'status':'pass_scoped_nullable_lock_load_bypass' if passed else 'rejected_closed_nullable_lock_mechanism_absent','protocol_sha256':sys.argv[2],'cases':cases,'calibrations':h.read(H/'calibration.json'),'application_kernels':0,'native_or_compiler_repeats':0,'performance_samples':0,'candidate_accepted':False,'limits':'Static direct PTX CFG with conservative alias origins and known null/nonzero pointer predicates. Unknown other branches take both successors. No numerical memory or floating-point dataflow equivalence, SASS/full device liveness, locks/graph/lifecycle/capacity/material/complete speed or universal pointer-safety proof. Direct/engine/full raw states still required.'});h.custody()
for name in ['protocol.json','calibration.json','report.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D215','title':'Nullable lock-offset generated-code reachability','kind':'diagnostic','status':'measured' if passed else 'rejected','accepted':False,'measurement_epoch':'RAM20261028','stage':'Null argument skips all target lock-offset loads' if passed else 'Closed: intended nullable load bypass absent','reason':'Six target/architecture CFG checks plus original/present controls and parser calibrations. No application kernels, numeric states or speed measured.','evidence':[{'label':'Static CFG result','url':'evidence/'+H.name+'/report.json'},{'label':'Frozen reader protocol','url':'evidence/'+H.name+'/protocol.json'}]});item=next(x for x in s['experiments'] if x['id']=='E106');item.update(status='staged' if passed else 'rejected',stage='Host/resources/nullable load bypass passed; numeric controls pending' if passed else 'Closed at emitted mechanism gate',correctness='pending_direct_and_full_state_numerics');s.update(updated_at=h.now(),active_experiment='E106',stage=item['stage'],activity='The compiler bypasses lock-offset loads for null arguments in all three kernels on both targets. Numerical, lock/graph lifecycle and complete-cycle qualification remain.' if passed else 'Nullable lock mechanism failed; exact form closed. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':passed,'cases':len(cases),'gates':[{k:x[k] for k in ['architecture','kernel','gates']} for x in cases]}),flush=True)
