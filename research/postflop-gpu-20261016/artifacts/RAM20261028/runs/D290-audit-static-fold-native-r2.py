import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D290-static-fold-native'
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
 r,l=parse(t);assert r[0x11f0]=='LDCU UR8, c[0x0][0x360]'and r[0x1210]=='UISETP.NE.AND UP0, UPT, UR8, 0x80, UPT'and r[0x1230]=='BRA.U !UP0, `(.L_x_267)'and l['.L_x_267']==0x1330
 fast={pc:op for pc,op in r.items()if 0x1330<=pc<=0x15c0};assert sum('BAR.SYNC'in op for op in fast.values())==7 and sum('FADD'in op for op in fast.values())==7 and sum('STS'in op for op in fast.values())==7
 assert not any(any(x in op for x in ['SHF.','BRA','LDG','STG','SHFL'])for op in fast.values())
 for pc,offset in[(0x1350,'0x100'),(0x13b0,'0x80'),(0x1410,'0x40'),(0x1470,'0x20'),(0x14d0,'0x10'),(0x1530,'0x8')]:assert re.fullmatch(r'@!P[01] LDS R\d+, \[R2\+'+offset+r'\]',r[pc])
 assert r[0x1590]=='@!P1 LDS.64 R8, [R6+0xd0]'and r[0x15a0]=='@!P1 FADD R3, R9, R8'and r[0x15b0]=='@!P1 STS [R6+0xd0], R3'
 assert r[0x1270]=='SHF.R.U32.HI R9, RZ, 0x1, R3'and r[0x12e0].startswith('BAR.SYNC')and r[0x1310]=='@P0 BRA `(.L_x_269)'and l['.L_x_269']==0x1270 and l['.L_x_268']==0x15d0
 assert r[0x90]=='S2R R0, SR_TID.X';assert r[0x1060]=='S2R R11, SR_CgaCtaId'and r[0x1080]=='MOV R9, 0x400'and r[0x10a0]=='IADD R2, R9, 0xd0'and r[0x10c0]=='LEA R3, R11, R2, 0x18'and r[0x10d0]=='IMAD R2, R0, 0x4, R3';assert r[0x1560]=='@!P1 LEA R6, R11, R9, 0x18'
 return{'uniform_width_guard_and_fast_PC':'0x11f0LDCU/0x1210NE128/0x1230uniform!NEbranch ->0x1330','fast_native_instructions':[{'pc':hex(pc),'op':op}for pc,op in fast.items()],'fast_CTA_barriers':7,'fast_FP_adds':7,'fast_shared_stores':7,'dynamic_shift_or_branch_in_fast_ladder':False,'six_fixed_relative_offsets':[256,128,64,32,16,8],'final_phase':'PredicatedLDS.64 paired2words/FADD/STSatshared0xd0; D289PTXbinds originalstep1operands. ThisboundedreaderdoesnotfullysymbolicallyproveR6addressancestry. FulloriginalrawGPUcorpusmustresolveactualbits/guards.','generic_native_shift_barrier_backedge_retained':True,'limits':'Fixed-driver localinstruction/control witness plusD289PTX; not universalSASSinterpreter,completeFP/addressproof,dynamiccounter,latency orspeed proof.'}
if len(sys.argv)==1:
 h.custody();H0=h.read(H/'capture-report.json');files=[Path(__file__),H/'protocol.json',H/'capture-report.json',ROOT/'runs/D289-static-fold-PTX/report.json']+[Path(v['path'])for v in H0['entry_sections'].values()];h.save(H/'reader-protocol-r2.json',{'at':h.now(),'status':'FROZEN_PRE_STATIC_NATIVE_READER','input_sha256':{str(p):h.sha(p)for p in files},'requirements':'Actualdefault128uniformbranch to7shared-add/store/CTAbarrierstaticphases; noshift/backedge/shuffle/globalmemoryonthatroute; originalgenericloop retained. Negativefixtures. D289PTXidentity andrawGPUfullcorpusremainmandatory.'});print(h.sha(H/'reader-protocol-r2.json'));sys.exit(0)
assert len(sys.argv)==2;h.pin(H/'reader-protocol-r2.json',sys.argv[1]);P=h.read(H/'reader-protocol-r2.json');h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
c=h.read(H/'capture-report.json');t=Path(c['entry_sections']['candidate']['path']).read_text(encoding='utf-8');w=inspect(t);negative=[]
for name,old,new in [('wrong_width','UR8, 0x80, UPT','UR8, 0x40, UPT'),('wrong_offset','[R2+0x100]','[R2+0xfc]'),('removed_barrier','/*1390*/                   BAR.SYNC.DEFER_BLOCKING 0x0','/*1390*/                   NOP'),('wrong_fallback_backedge','@P0 BRA `(.L_x_269)','@P0 BRA `(.L_x_268)')]:
 assert old in t;bad=t.replace(old,new,1)
 try:inspect(bad)
 except AssertionError:negative.append(name)
 else:raise AssertionError('negativefixtureaccepted '+name)
h.save(H/'report.json',{'id':'D290','at':h.now(),'status':'pass_scoped_native_default128_static_fold_ladder','protocol_sha256':sys.argv[1],'witness':w,'negative_reader_fixtures':negative,'all_owned_capture_disassembly_children_terminal':True,'new_application_kernel_solver_or_speed_samples':0,'candidate_accepted':False});h.custody();print('D290native128static7phase route/genericloop witness pass.',flush=True)
