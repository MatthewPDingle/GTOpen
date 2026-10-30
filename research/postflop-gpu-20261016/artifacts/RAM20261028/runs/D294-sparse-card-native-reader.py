import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D294-sparse-card-native'
def parse(t):
 rows={};labels={};pending=[]
 for line in t.splitlines():
  m=re.match(r'\s*(\.L_x_\d+):',line)
  if m:pending.append(m[1])
  m=re.match(r'\s*/\*([0-9a-f]+)\*/\s*(.*?)\s*;\s*/\*',line)
  if m:
   pc=int(m[1],16);rows[pc]=m[2]
   for label in pending:labels[label]=pc
   pending=[]
 return rows,labels
def inspect(t):
 r,l=parse(t);assert r[0xe0]=='LDCU UR7, c[0x0][0x43c]'and r[0x160]=='UISETP.GT.U32.AND UP0, UPT, UR7, 0x52e, UPT'
 assert r[0x370]=='LDG.E.CONSTANT R12, desc[UR10][R12.64]'and r[0x3b0]=='STS [R15], R12'and r[0x3c0]=='ISETP.GT.U32.AND P0, PT, R12, 0x67800000, PT'and r[0x3e0]=='LOP3.LUT R10, R10, R17, RZ, 0xfc, !PT'
 assert r[0x580]=='ISETP.NE.U32.AND P0, PT, R10, RZ, PT'and r[0x590]=='BAR.RED.OR.DEFER_BLOCKING 0x0, P0'and r[0x5a0]=='B2R.RESULT RZ, P0'
 assert not any(re.match(r'\S+ P0,',op)for pc,op in r.items()if 0x5a0<pc<0x990)
 bars=[(pc,op)for pc,op in r.items()if op.startswith('BAR.')];assert [pc for pc,op in bars]==[0x590,0x8a0,0x1430,0x1da0,0x20b0]
 assert r[0x980]=='MOV R15, R14'and r[0x990]=='@P0 BRA `(.L_x_211)'and l['.L_x_211']==0xec0 and r[0xf00]=='STS [R14], R15'
 pack={pc:op for pc,op in r.items()if 0x940<=pc<=0xf20};assert not any(re.search(r'\b(?:FADD|FMUL|FFMA|HFMA)',op)for op in pack.values())
 for pc,op in [(0xb30,'ISETP.NE.AND P1, PT, R18, RZ, PT'),(0xb60,'@P1 STS [R19], R24'),(0xbe0,'ISETP.NE.AND P1, PT, R18, RZ, PT'),(0xc10,'@P1 STS [R25], R16'),(0xcd0,'ISETP.NE.AND P1, PT, R18, RZ, PT'),(0xd00,'@P1 STS [R23], R20'),(0xd50,'ISETP.NE.AND P2, PT, R19, RZ, PT'),(0xd80,'@P2 STS [R24], R21'),(0xdd0,'ISETP.NE.AND P1, PT, R18, RZ, PT'),(0xe00,'@P1 STS [R23], R22'),(0xe60,'ISETP.NE.AND P2, PT, R19, RZ, PT'),(0xe90,'@P2 STS [R21], R20')]:assert r[pc]==op
 assert r[0x22e0]=='S2R R18, SR_CgaCtaId'and r[0x22f0]=='MOV R19, 0x400'and r[0x2330]=='LEA R22, R18, R19, 0x18'and r[0x2360]=='IMAD R25, R23, 0x4, R22'and r[0x2370]=='LDS R31, [R25]'and r[0x2420]=='IADD R28, R0, R31'
 return {'barriers':[{'PC':hex(pc),'op':op}for pc,op in bars],'source_reach_guard':'param25constant0x43c ->unsignednh_o>1326;originalR12global/sharedword ->uint>0x67800000 ->ORR10 ->BAR.RED.OR/B2R P0.','unsafe_original_endpoint':'R15=originalend R14 at0x980;@P0 at0x990 ->0xec0reconverge ->same0xf00endstore. P0notrewritten insideguardtoskipdomain.','six_conditional_shared_position_stores_and_nonzero_bit_predicates':True,'compaction_native_instructions':[{'PC':hex(pc),'op':op}for pc,op in pack.items()],'first_card_endpoint_consumer':'Afterlastbarrier: CGAsharedbase0x400,cardidxR23*4 ->LDSR31 ->originalcard_baseR0+endpoint at0x2420. Both card consumer paths are separately bound in D293PTX.','limits':'Bounded fixed-driver nativeguard/OR/compactionstore/fallback/firstendpoint/barrier witness. Does not fully symbolically interpret every pointer, every integer loop or secondnativeconsumer. Fullsource/D293PTX/directraw/engine/canonical/broadqualification remain mandatory, no universalIEEE orspeedclaim.'}
if len(sys.argv)==1:
 h.custody();C=h.read(H/'capture-report.json');files=[Path(__file__),H/'protocol.json',H/'capture-report.json',ROOT/'runs/D293-sparse-card-PTX/report.json']+[Path(v['path'])for v in C['entry_sections'].values()]
 h.save(H/'reader-protocol.json',{'at':h.now(),'status':'FROZEN_PRE_NATIVE_INSTRUCTION_READER','input_sha256':{str(p):h.sha(p)for p in files},'scope':'Native ORguard/sameoriginalphysicalreachbits/default5barriers/conditionalintegerpositionstores/originalendfallback/postjoinendpoint witness; D293PTX and rawGPUfullcorpus remain required. Wrongthreshold/predicatedstore/fallback/barrier negativefixtures.'});print(h.sha(H/'reader-protocol.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;h.pin(H/'reader-protocol.json',sys.argv[1]);P=h.read(H/'reader-protocol.json');h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
C=h.read(H/'capture-report.json');t=Path(C['entry_sections']['candidate']['path']).read_text();w=inspect(t);fixtures=[]
for name,old,new in [('wrong_threshold','R12, 0x67800000, PT','R12, 0x67800001, PT'),('wrong_position','@P1 STS [R19], R24','@P1 STS [R19], R16'),('wrong_fallback','@P0 BRA `(.L_x_211)','@P0 BRA `(.L_x_215)'),('missing_reduction','BAR.RED.OR.DEFER_BLOCKING 0x0, P0','BAR.SYNC.DEFER_BLOCKING 0x0')]:
 assert old in t;bad=t.replace(old,new,1)
 try:inspect(bad)
 except AssertionError:fixtures.append(name)
 else:raise AssertionError('negativefixtureaccepted '+name)
h.save(H/'report.json',{'id':'D294','at':h.now(),'status':'pass_scoped_sparse_card_native_guard_compaction_fallback_and_join_witness','protocol_sha256':sys.argv[1],'witness':w,'negative_reader_fixtures':fixtures,'all_owned_capture_disassembly_children_terminal':True,'new_application_kernel_solver_or_speed_samples':0,'candidate_adopted':False});h.custody();print('D294native scoped mechanism witness passed.',flush=True)
