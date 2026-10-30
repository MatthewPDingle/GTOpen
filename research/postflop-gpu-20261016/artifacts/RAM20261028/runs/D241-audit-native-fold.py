import collections,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D241-native-fold-copy'
def parse(text):
 out=[]
 for line in text.splitlines():
  m=re.match(r'^\s*/\*([0-9a-f]+)\*/\s*(.*?)\s*;',line)
  if m:out.append((int(m[1],16),m[2]))
 return out
def writes(op):
 op=re.sub(r'^@!?[UP]\d+\s+','',op);code=op.split()[0]
 if code.startswith(('ST','ISETP','UISETP','FSETP','DSETP','USETP','BRA','BSSY','BSYNC','BAR','EXIT','NOP','RET')):return set()
 m=re.search(r'\bR(\d+)\b',op)
 if not m:return set()
 n=int(m[1]);size=4 if '.128'in code else 2 if '.64'in code or code.startswith('IMAD.WIDE')else 1
 return {'R'+str(i)for i in range(n,n+size)}
def inspect(ops,candidate):
 barriers=[pc for pc,op in ops if op.startswith('BAR.SYNC')];assert len(barriers)==3;first,second=barriers[:2];pre=[(pc,op)for pc,op in ops if pc<first];mid=[(pc,op)for pc,op in ops if first<pc<second];stores=[(pc,op)for pc,op in mid if op.startswith('STS ')];assert len(stores)==2
 totalpc,total=stores[-1];partial=re.fullmatch(r'STS \[R\d+\], (R\d+)',total)[1]
 fadds=[]
 for pc,op in pre if candidate else mid:
  m=re.fullmatch(r'FADD (R\d+), (R\d+)(?:\.reuse)?, (R\d+)(?:\.reuse)?',op)
  if m and m[1]==partial and partial in m.groups()[1:]:fadds.append((pc,m))
 assert len(fadds)==1;addpc,add=fadds[0];rhs=next(x for x in add.groups()[1:]if x!=partial)
 if candidate:
  assert len([op for pc,op in pre if op.startswith('FADD ')])==1
  loads=[(pc,op)for pc,op in pre if re.match(r'LDG\.[\w.]+ '+rhs+r', ',op)];assert len(loads)==1;loadpc,load=loads[0]
  sts=[(pc,op)for pc,op in pre if re.fullmatch(r'STS \[R\d+\], '+rhs,op)];assert len(sts)==1 and loadpc<sts[0][0]<addpc<first
  assert not[(pc,op)for pc,op in pre if loadpc<pc<addpc and rhs in writes(op)]
  assert any(re.fullmatch(r'MOV '+partial+r', RZ',op)for pc,op in pre if pc<loadpc)
  clobbers=[(pc,op)for pc,op in ops if first<pc<totalpc and partial in writes(op)];assert not clobbers,clobbers
 else:
  assert not[op for pc,op in pre if op.startswith('FADD ')]
  loads=[(pc,op)for pc,op in mid if re.fullmatch(r'LDS '+rhs+r', \[R\d+\]',op)and pc<addpc];assert loads
  loadpc,load=loads[-1];assert not[(pc,op)for pc,op in mid if loadpc<pc<addpc and rhs in writes(op)]
  assert any(pc>addpc and pc<totalpc and'BRA 'in op for pc,op in mid)
 return {'first_barrier_pc':hex(first),'second_barrier_pc':hex(second),'partial_register':partial,'input_register':rhs,'producer_pc':hex(loadpc),'producer':load,'ordered_add_pc':hex(addpc),'ordered_add':add[0],'total_parts_store_pc':hex(totalpc),'total_parts_store':total,'candidate_keeps_partial_unmodified_across_card_stage':candidate,'native_barrier_sites':3}
if len(sys.argv)==1:
 h.custody();cap=h.read(H/'capture-report.json');files=[Path(__file__),H/'protocol.json',H/'capture-report.json',ROOT/'runs/D240-fold-copy-PTX/report.json',ROOT/'runs/E110-source/source-review.json',ROOT/'epoch/common.py']+[Path(cap['entry_sections'][a]['up_fold']['path'])for a in ['baseline','candidate']]
 h.save(H/'reader-plan.json',{'at':h.now(),'status':'FROZEN_PRE_STATIC_NATIVE_READER','input_sha256':{str(p):h.sha(p)for p in files},'gate':'Candidate beforefirstbarrier actualglobalLDG scalar isalsoSTSsource andselfFADDoperand; zero-seededpartial hasno scalar/vector writer throughcardstage tooriginaltotalpartsstore. Baseline totalpartsstore feedsfromlaterLDS/selfFADDloop, no prefirstbarrierFADD. All3barriers same. Scalar/vector overwrite negativefixture andactualwrongoperand fixture required. PTXparam19induction andsource-reversal separately frozen.','limits':'Source/PTX-linked local native operand/schedule witness, not fullSASS CFG/FP execution, latency/bottleneck or speed proof. Native FADD operandordering maycommute; rawGPU NaN/Inf/subnormal/zero exactness still mandatory. No newcapture/nativeappkernels orcounters.'});print(h.sha(H/'reader-plan.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;P=h.read(H/'reader-plan.json');h.pin(H/'reader-plan.json',sys.argv[1]);h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
cap=h.read(H/'capture-report.json');ops={a:parse(Path(cap['entry_sections'][a]['up_fold']['path']).read_text())for a in ['baseline','candidate']};rows={a:inspect(ops[a],a=='candidate')for a in ops};cr=rows['candidate'];first=int(cr['first_barrier_pc'],16);total=int(cr['total_parts_store_pc'],16);original=ops['candidate'];mutant=list(original);at=next(i for i,(pc,op)in enumerate(mutant)if first<pc<total);mutant.insert(at,(first+1,'LDC.128 '+cr['partial_register']+', c[0x0][0x500]'))
try:inspect(mutant,True)
except AssertionError:clobber=True
else:raise AssertionError('vector overwrite not caught')
mutant=[(pc,op.replace(cr['ordered_add'],'FADD '+cr['partial_register']+', RZ, '+cr['partial_register']))for pc,op in original]
try:inspect(mutant,True)
except (AssertionError,StopIteration):wrong=True
else:raise AssertionError('wrong producer not caught')
h.save(H/'report.json',{'id':'D241','at':h.now(),'status':'pass_static_native_global_copy_partial_fusion','reader_plan_sha256':sys.argv[1],'witnesses':rows,'negative_fixtures':{'scalar_vector_writer_clobber_detected':clobber,'wrong_producer_operand_detected':wrong},'all_owned_capture_disassembly_children_terminal':True,'new_appkernel_or_counter_or_speed_runs':0,'candidate_accepted':False,'limits':P['limits']})
for name in ['protocol.json','capture-report.json','reader-plan.json','report.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
print(json.dumps(rows),flush=True)
