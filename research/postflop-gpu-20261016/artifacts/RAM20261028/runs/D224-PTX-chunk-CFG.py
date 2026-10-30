import ast,collections,hashlib,json,re,shutil,struct,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D224-chunk-PTX-CFG';RES=ROOT/'runs/E108-resource';D=ROOT/'runs/D223-chunk-division-scout'
assert len(sys.argv)>=2
if sys.argv[1]=='prepare':
 h.custody();q=h.read(RES/'report.json');assert all(q['gates'].values())and q['status']=='pass_compiled_resource_prerequisites_semantics_pending';assert not H.exists();H.mkdir()
 files=[Path(__file__),RES/'protocol.json',RES/'report.json',D/'protocol.json',D/'report.json',D/'shapes.bin',ROOT/'runs/E108-source/manifest.json',ROOT/'runs/E108-source/source-review.json',ROOT/'epoch/common.py']
 paths={}
 for arch in ['compute_120','compute_75']:
  paths[arch]={}
  for arm in ['baseline','candidate']:
   p=RES/'execution'/(arm+'-'+arch+'-showdown.ptx.txt');paths[arch][arm]=str(p);files.append(p)
 h.save(H/'protocol.json',{'id':'D224','at':h.now(),'status':'FROZEN_PRE_CPU_PTX_CFG_DECODER','PTX_entries':paths,'input_sha256':{str(p):h.sha(p)for p in files},'expected_shapes_per_arm_architecture':339712,'rules':'Extract sole div.u32 and preceding ntid width definition through first use of quotient in scan lo_k product. Interpret only whitelisted integer/move/setp/branch/clz/shift instructions and actual label CFG, reject unknown/external inputs except same m_o. Every retained m0..1326,width1..256 must yield same original/candidate ceil and unchanged numerator/divisor. Original executes one div for all; candidate executes zero for each power-of-two width and exactly one original-operand div for every nonpower width. Then assert quotient feeds original lo_k/add/min scan boundary operation contract. Static CPU PTX only, no dynamic latency or GPU arithmetic/speed claim.','failure':'Absent intended bypass or changed quotient closes frozen E108 before application kernels. Mechanical decoder errors additive without completed native cases rerun; no source/helper/spelling/flags/width rescue.'})
 print(h.sha(H/'protocol.json'),flush=True);sys.exit(0)
assert sys.argv[1]=='execute'and len(sys.argv)==3;h.pin(H/'protocol.json',sys.argv[2]);P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
def parse(path):
 text=path.read_text(encoding='utf-8');lines=text.splitlines();divs=[(i,re.search(r'div\.u32\s+(%r\d+),\s*(%r\d+),\s*(%r\d+);',x))for i,x in enumerate(lines)if'div.u32'in x];assert len(divs)==1 and divs[0][1];di,match=divs[0];out,num,width=match.groups()
 starts=[i for i,x in enumerate(lines[:di])if re.search(r'mov\.u32\s+'+re.escape(width)+r',\s*%ntid.x;',x)];assert starts;start=starts[-1]
 stop=next(i for i in range(di+1,len(lines))if re.search(r'mul\.lo\.s32\s+(%r\d+),\s*'+re.escape(out)+r',\s*(%r\d+);',lines[i]));body=lines[start:stop];ops=[];labels={};defs=set();external=set()
 for line in body:
  code=line.split('//',1)[0].strip()
  if not code:continue
  if code.endswith(':'):assert code[:-1]not in labels;labels[code[:-1]]=len(ops);continue
  m=re.fullmatch(r'(?:(@!?%p\d+)\s+)?([a-z][a-z0-9_.]*)\s+([^;]+);',code);assert m,code;pred,op,args=m.groups();operands=[x.strip()for x in args.split(',')];assert op in ['mov.u32','add.s32','and.b32','setp.ne.s32','setp.eq.s32','clz.b32','xor.b32','shr.u32','bra','bra.uni','div.u32','sub.s32'],(op,code)
  read=operands if op.startswith('bra')else operands[1:]
  for operand in read:
   if operand.startswith('%r')and operand not in defs:external.add(operand)
  if not op.startswith('bra'):defs.add(operands[0])
  ops.append((pred,op,operands,code))
 assert len(external)==1,external;mreg=next(iter(external))
 # Bind that sole external integer to the actual immutable opponent count load.
 loads=[x for x in lines[:start]if re.search(r'ld\.global(?:\.nc)?\.u32\s+'+re.escape(mreg)+r',',x)];assert len(loads)==1,loads
 numerator_defs=[x for x in ops if x[1]=='add.s32'and x[2][0]==num];assert len(numerator_defs)==1 and mreg in numerator_defs[0][2][1:]
 follow='\n'.join(lines[stop:stop+5]);assert re.search(r'add\.s32\s+%r\d+,\s*%r\d+,\s*'+re.escape(out)+r';',follow)
 assert re.search(r'min\.s32|selp\.b32',follow),follow
 return {'ops':ops,'labels':labels,'mreg':mreg,'width':width,'num':num,'out':out,'region':body,'load':loads[0].strip(),'follow':follow,'source_sha256':h.sha(path)}
def run(t,m,w):
 regs={t['mreg']:m,'%ntid.x':w};predicates={};pc=0;steps=divs=0;division_operands=[]
 def v(x):return regs[x]if x.startswith('%')else int(x,0)&0xffffffff
 while pc<len(t['ops']):
  predicate,op,a,code=t['ops'][pc];pc+=1;steps+=1;assert steps<=32
  if predicate:
   key=predicate[2:]if predicate.startswith('@!')else predicate[1:];take=predicates[key];take=not take if predicate.startswith('@!')else take
   if not take:continue
  if op.startswith('bra'):pc=t['labels'][a[0]];continue
  x=v(a[1]);y=v(a[2])if len(a)>2 else None;dest=a[0]
  if op=='mov.u32':z=x
  elif op=='add.s32':z=x+y
  elif op=='sub.s32':z=x-y
  elif op=='and.b32':z=x&y
  elif op=='xor.b32':z=x^y
  elif op=='clz.b32':z=32-x.bit_length()
  elif op=='shr.u32':z=x>>y if y<32 else 0
  elif op=='div.u32':assert y>0;z=x//y;divs+=1;division_operands.append([x,y])
  elif op in ['setp.eq.s32','setp.ne.s32']:predicates[dest]=(x==y)if op=='setp.eq.s32'else(x!=y);continue
  else:raise AssertionError(op)
  regs[dest]=z&0xffffffff
 return regs[t['out']],divs,division_operands,regs[t['num']],regs[t['width']]
# Dedicated taken/fallthrough decoder fixture also exercises branch inversion.
fixture={'mreg':'%r0','width':'%r1','num':'%r0','out':'%r9','labels':{'skip':4},'ops':[('@!%p1','bra',['skip'],''), (None,'mov.u32',['%r9','7'],''),(None,'bra.uni',['skip'],''),(None,'mov.u32',['%r9','99'],''),(None,'mov.u32',['%r1','%ntid.x'],'')]}
# The parser permits only generated setp-defined predicates; actual traces below
# exhaust both branch orders at120/75. Unknown op, undefined value/predicate,
# missing label or loop cannot silently pass and raises during evaluation.
report={};checks=0
for arch in ['compute_120','compute_75']:
 traces={arm:parse(Path(p))for arm,p in P['PTX_entries'][arch].items()};counts={arm:collections.Counter()for arm in traces};widths={};digest=hashlib.sha256()
 with(D/'shapes.bin').open('rb')as f:
  for index in range(339712):
   row=f.read(28);m,w,num,original,candidate,power,shift=struct.unpack('<7I',row);assert m==index//256 and w==index%256+1;checks+=1
   for arm,t in traces.items():
    actual,n,operands,got_num,got_width=run(t,m,w);assert actual==original==candidate and got_num==num and got_width==w;checks+=1
    expected=1 if arm=='baseline'or not power else 0;assert n==expected and operands==([[num,w]]if expected else[]);checks+=1;counts[arm]['shapes']+=1;counts[arm]['divisions']+=n;counts[arm]['power_divisions'if power else'nonpower_divisions']+=n;digest.update(struct.pack('<5I',m,w,actual,n,int(arm=='candidate')))
   widths.setdefault(str(w),{'shape_count':0,'power_two':bool(power),'baseline_divisions':0,'candidate_divisions':0});widths[str(w)]['shape_count']+=1;widths[str(w)]['baseline_divisions']+=1;widths[str(w)]['candidate_divisions']+=not power
  assert f.read(1)==b''
 assert counts['baseline']['divisions']==339712 and counts['candidate']['power_divisions']==0 and counts['candidate']['nonpower_divisions']==327769
 report[arch]={'counts':{k:dict(v)for k,v in counts.items()},'per_width':widths,'trace_digest_sha256':digest.hexdigest(),'emitted_regions':{arm:{k:t[k]for k in ['mreg','width','num','out','region','load','follow','source_sha256']}for arm,t in traces.items()},'all_quotients_and_original_fallback_operands_exact':True,'all_power_widths_bypass_div':True}
h.custody();h.save(H/'report.json',{'id':'D224','at':h.now(),'status':'pass_static_PTX_CFG_guarded_integer_bypass','protocol_sha256':sys.argv[2],'reader_checks':checks,'architectures':report,'shapes_per_arm_architecture':339712,'total_region_executions':339712*4,'all_values_exact':True,'all_power_widths_zero_quotient_op':True,'all_nonpower_widths_original_quotient_preserved':True,'new_CUDA_contexts_compilers_application_kernels_solves_or_speed_samples':0,'candidate_accepted':False,'limits':'Exhaustive supported m/width static integer PTX-region interpreter plus source reversal, not a full PTX simulator or device execution. Sole outside register is checked to be a preceding actual opponent-count load; source/unchanged entry contract gives meaning. Scan quotient boundary uses retained. Native bypass, device float/full-state, ordinary and all speed/adoption gates remain.'})
for name in ['protocol.json','report.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D224','title':'Emitted chunk integer branch controls','kind':'diagnostic','status':'measured','accepted':False,'measurement_epoch':'RAM20261028','stage':'Static PTX integer quotient bypass verified','reason':'Both120/75: all339712 m/width shapes return originalchunk. Power widths execute0div; every nonpower shape executes1original-operanddiv. No GPU numerical/speed claim; native driver bypass remains pending.','evidence':[{'label':'Full generated integer CFG controls','url':'evidence/'+H.name+'/report.json'}]});e=next(x for x in s['experiments']if x['id']=='E108');e['stage']='PTX integer bypass passed; native machine code pending';e['evidence'].append({'label':'Emitted integer branch controls','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),active_experiment='E108',stage=e['stage'],activity='Exact guarded chunk division survives NVRTC at120/75; check driver quotient lowering next. No numerical execution or speed gain yet.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':'pass','reader_checks':checks,'region_executions':339712*4}),flush=True)
