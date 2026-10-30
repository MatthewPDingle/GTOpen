import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D283-zero-tie-native'
def parse(text):
    rows={};labels={};pending=[]
    for line in text.splitlines():
        match=re.match(r'\s*(\.L_x_\d+):',line)
        if match:pending.append(match[1])
        m=re.match(r'\s*/\*([0-9a-f]+)\*/\s*(.*?)\s*;\s*/\*',line)
        if m:
            pc=int(m[1],16);assert pc not in rows;rows[pc]=m[2]
            for label in pending:labels[label]=pc
            pending=[]
    return rows,labels
def writes(op,reg):
    op=re.sub(r'^@\S+\s+','',op);parts=op.split(None,1)
    if len(parts)!=2:return False
    mnemonic,args=parts;first=args.split(',',1)[0].strip()
    if mnemonic.startswith(('ST','BRA','BAR','BSSY','BSYNC','EXIT','ISETP','UISETP','FSETP','PLOP','UPLOP')):return False
    if first==reg:return True
    m=re.fullmatch(r'(U?R)(\d+)',first)
    if m and any(x in mnemonic for x in['.64','.WIDE','.128']):return reg in[m[1]+str(int(m[2])+i)for i in range(4 if'.128'in mnemonic else 2)]
    return False
def inspect(text):
    rows,labels=parse(text);required={
      0x360:'LDG.E.CONSTANT R8, desc[UR14][R8.64]',0x3a0:'STS [R11], R8',0x3b0:'ISETP.GT.U32.AND P0, PT, R8, 0x67800000, PT',0x3c0:'SEL R17, RZ, 0x1, !P0',0x3d0:'LOP3.LUT R12, R12, R17, RZ, 0xfc, !PT',0x570:'ISETP.NE.U32.AND P0, PT, R12, RZ, PT',0x580:'BAR.RED.OR.DEFER_BLOCKING 0x0, P0',0x590:'B2R.RESULT RZ, P0',
      0x1940:'LDCU.128 UR20, c[0x0][0x390]',0x1950:'LDCU.64 UR4, c[0x0][0x3a0]',0x1970:'IADD.64 R20, R6.reuse, UR22',0x1980:'IADD.64 R18, R6.reuse, UR20',0x1990:'IADD.64 R6, R6, UR4',0x19a0:'LDG.E.CONSTANT R14, desc[UR14][R20.64]',0x19b0:'LDG.E.CONSTANT R13, desc[UR14][R18.64]',0x19c0:'LDG.E.CONSTANT R12, desc[UR14][R6.64]',
      0x3610:'FMUL R8, R14, R27',0x3620:'FFMA R17, R13, R26, R8',0x3630:'LOP3.LUT R8, R17, 0x7fffffff, RZ, 0xc0, !PT',0x3640:'IADD R8, R8, -0x1',0x3650:'ISETP.GE.U32.AND P2, PT, R8, 0x7f7fffff, PT',0x3660:'@!P2 BRA `(.L_x_248)',0x47a0:'FFMA R17, R12, R17, R9',0x4840:'STG.E desc[UR14][R8.64], R17'}
    assert all(rows.get(pc)==op for pc,op in required.items())
    barriers=[(pc,op)for pc,op in rows.items()if op.startswith('BAR.')];assert len(barriers)==5 and barriers[0][0]==0x580 and all(op.startswith('BAR.SYNC')for pc,op in barriers[1:])
    assert labels['.L_x_248']==0x47b0 and not any(writes(op,'R17')for pc,op in rows.items()if 0x47b0<=pc<0x4840)
    assert not any(op.startswith(('FADD','FMUL','FFMA','LDS','LDG'))for pc,op in rows.items()if 0x47b0<=pc<0x4840)
    assert not any(writes(op,'R13')for pc,op in rows.items()if 0x19b0<pc<0x3620);assert not any(writes(op,'R14')for pc,op in rows.items()if 0x19a0<pc<0x3610)
    for lo,hi,regs in[(0x1940,0x1970,['UR22','UR23']),(0x1940,0x1980,['UR20','UR21']),(0x1950,0x1990,['UR4','UR5']),(0x1970,0x19a0,['R20','R21']),(0x1980,0x19b0,['R18','R19']),(0x1990,0x19c0,['R6','R7'])]:
        assert not any(writes(op,reg)for pc,op in rows.items()if lo<pc<hi for reg in regs)
    replay=[{'pc':hex(pc),'instruction':op}for pc,op in rows.items()if 0x3670<=pc<=0x47a0];assert any('LDS'in row['instruction']for row in replay)and any('FADD'in row['instruction']for row in replay)
    guard=[{'pc':hex(pc),'instruction':op}for pc,op in rows.items()if 0x1aa0<=pc<=0x1b10];branch=rows[0x1b10];m=re.fullmatch(r'@P0 BRA `\((\.L_x_\d+)\)',branch);assert m and 0x4840<labels[m[1]]<0x65f0
    return{'exact_witness_instructions':[{'pc':hex(pc),'instruction':op}for pc,op in required.items()],'first_barrier_reduction_and_four_syncs':[{'pc':hex(pc),'instruction':op}for pc,op in barriers],'original_27param_payout_pointers':{'win_constant_offset':'0x390 viaUR20/21 thenR18/19,valueR13','lose_constant_offset':'0x398 viaUR22/23 thenR20/21,valueR14','tie_constant_offset':'0x3a0 viaUR4/5 thenR6/7,valueR12'},'native_prefix':'FMUL(lose,higher) ->FFMA(win,lower,product), same explicit RN instruction sequence as sealed baseline prefix; source/PTX define rounding/FTZ contract.','prefix_guard':'Masksign ->minus1 ->unsigned>=0x7f7fffff badpredicate;branchon!bad jumps0x3660to0x47b0,thenprefixR17store0x4840withnointerveningFP/load/prefixoverwrite.','skipped_replay_same_and_final_tie_region':replay,'static_uniform_guard_window':guard,'noneligible_fallback_pc':hex(labels[m[1]]),'limits':'Fixed-driver exactinstruction/overwrite/branch witness, not arbitrarySASSsimulator/dynamiccounter/latency/universalIEEEproof. D282PTXestablishes2orderedfastcorrectionadds/wordand1replayadd. No applicationkernel/solver/speed yet.'}
if len(sys.argv)==1:
    h.custody();C=h.read(H/'capture-report.json');files=[Path(__file__),ROOT/'epoch/common.py',H/'protocol.json',H/'capture-report.json',ROOT/'runs/D282-zero-tie-PTX/report.json']+[Path(x['path'])for x in C['entry_sections'].values()]
    h.save(H/'reader-protocol.json',{'at':h.now(),'status':'FROZEN_PRE_STATIC_NATIVE_READER','input_sha256':{str(p):h.sha(p)for p in files},'requirements':'Exactdriverboundedreachcompare/OR/reductionbarrier;same5barriers. 27ABIconstantpayoutptr/valuechainnooverwrite. Originalfinite-nonzeroprefixFMUL/FFMAordering, exactmask/minus1/unsignedbadpredicate,branchpastcardtotalreplay/same/valid/tied/finalFMAtooriginalprefixstorewithoutoverwritingprefix. Negativefixturesrejectwrongthreshold/prefixoperand/branch/store. No newmodule/GPU/nativework;no sourcechanges ormechanism-basedtimingclaim.'});print(h.sha(H/'reader-protocol.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;P=h.read(H/'reader-protocol.json');h.pin(H/'reader-protocol.json',sys.argv[1]);h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
C=h.read(H/'capture-report.json');text=Path(C['entry_sections']['candidate']['path']).read_text(encoding='utf-8');w=inspect(text);negative=[]
for name,old,new in[('bad_reach_bound','R8, 0x67800000, PT','R8, 0x67800001, PT'),('wrong_prefix_product','FMUL R8, R14, R27','FMUL R8, R13, R27'),('wrong_guard_polarity','@!P2 BRA `(.L_x_248)','@P2 BRA `(.L_x_248)'),('wrong_prefix_store','STG.E desc[UR14][R8.64], R17','STG.E desc[UR14][R8.64], R18')]:
    assert text.count(old)==1;wrong=text.replace(old,new,1)
    try:inspect(wrong)
    except AssertionError:negative.append({'fixture':name,'rejected':True})
    else:raise AssertionError('negative reader fixture accepted '+name)
h.save(H/'report.json',{'id':'D283','at':h.now(),'status':'pass_scoped_native_zero_tie_prefix_bypass_and_payout_chain','reader_protocol_sha256':sys.argv[1],'capture_report_sha256':h.sha(H/'capture-report.json'),'witness':w,'negative_reader_fixtures':negative,'all_owned_module_disassembly_children_terminal':True,'application_kernels_solver_or_speed_samples':0,'candidate_accepted':False,'limits':w['limits']});h.custody();print('D283nativeguard/prefix/directstorebypasswitnesses pass,noapplicationkernels.',flush=True)
