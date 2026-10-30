import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D225-chunk-native-bypass';assert len(sys.argv)>=2
if sys.argv[1]=='prepare':
 files=[Path(__file__),H/'protocol.json',H/'capture-report.json',ROOT/'runs/E108-resource/report.json',ROOT/'runs/D224-chunk-PTX-CFG-r3/report.json']+[p for arm in ['baseline','candidate']for p in (H/'execution'/arm).iterdir()if p.is_file()and p.suffix in ['.json','.txt','.log','.cubin']]
 h.save(H/'reader-plan.json',{'id':'D225-native-review','at':h.now(),'status':'FROZEN_PRE_STATIC_NATIVE_READER','input_sha256':{str(p):h.sha(p)for p in files},'rules':'Exact current-driver width-load/width-minus-one/AND-LUT/nonzero-predicate branch, FLO/shift, jump-over-only-reciprocal region and quotient scan join. Enumerate positive widths1..256 and all fastpath m0..1326, same5barriers and terminal capture/disassembly receipts. Nonpower numerical lowering remains for real direct controls; do not pretend static SASS is a full device simulator or dynamic performance observation.','semantics':'LOP3 LUT0xc0 is bitwiseAandB for conventional A/B/C truth index4A+2B+C; predicate result is interpreted as nonzero, matched to retained PTX setp.ne on same width AND. Constant0x360 is mapped to ntid.x from the matching sole integer-divider region. FLO.U32 is interpreted as most-significant-set index; subsequent31-minus/xor31 yields log2 for nonzero power widths. These native instruction/source mappings are static inferences cross-checked against exhaustively decoded PTX; device float/exactness tests remain mandatory.','failure':'Absent expected native bypass closes frozen E108, no source/helper/spelling/width/flags rescue.'})
 print(h.sha(H/'reader-plan.json'),flush=True);sys.exit(0)
assert sys.argv[1]=='execute'and len(sys.argv)==3;h.pin(H/'reader-plan.json',sys.argv[2]);P=h.read(H/'reader-plan.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
C=h.read(H/'capture-report.json');gates={};witness={};parsed={}
for arm in ['baseline','candidate']:
 O=H/'execution'/arm;h.pin(O/'up_show.sass.txt',C['captures'][arm]['up_show_sha256']);text=(O/'up_show.sass.txt').read_text(encoding='utf-8');rows={};labels={};pending=[]
 for line in text.splitlines():
  lm=re.fullmatch(r'\s*(\.L_x_\d+):\s*',line)
  if lm:pending.append(lm[1]);continue
  m=re.match(r'^\s*/\*([0-9a-f]{4})\*/\s*(.*?)\s*;',line)
  if m:
   addr=int(m[1],16);assert addr not in rows;rows[addr]=m[2]
   for label in pending:assert label not in labels;labels[label]=addr
   pending=[]
 barriers=[a for a,op in rows.items()if op.startswith('BAR.SYNC')];rcp=[a for a,op in rows.items()if op.startswith('MUFU.RCP')];gates[arm+':five_barriers']=len(barriers)==5;gates[arm+':one_integer_quotient_reciprocal_site']=len(rcp)==1
 for name in ['capture','disassemble']:
  v=h.read(O/(name+'.exit.json'));gates[arm+':'+name+':terminal_zero']=v['returncode']==0 and v['error']is v['cleanup']is None
 parsed[arm]=(rows,labels);witness[arm]={'barriers_hex':[hex(x)for x in barriers],'reciprocal_hex':[hex(x)for x in rcp]}
b,_=parsed['baseline'];c,labels=parsed['candidate']
expected={0x800:'LDCU UR7, c[0x0][0x360]',0x830:'UIADD3 UR4, UPT, UPT, UR7, -0x1, URZ',0x840:'ULOP3.LUT UP0, URZ, UR7, UR4, URZ, 0xc0, !UPT',0x850:'IADD R13, R4, UR4',0x860:'BRA.U UP0, `(.L_x_208)',0x870:'FLO.U32 R18, UR7',0x880:'IADD R18, -R18, 0x1f',0x890:'LOP3.LUT R18, R18, 0x1f, RZ, 0x3c, !PT',0x8a0:'SHF.R.U32.HI R18, RZ, R18, R13',0x8b0:'BRA `(.L_x_209)',0x8c0:'UI2F.U32.RP UR4, UR7',0x8e0:'MUFU.RCP R18, UR4',0x9e0:'IMAD R13, R14, R18.reuse, RZ',0xa00:'IADD R19, R13, R18',0xa10:'VIMNMX.S32 R18, R4, R19, PT'}
for addr,op in expected.items():gates['candidate:witness:'+hex(addr)]=c.get(addr)==op
gates['candidate:nonpower_label_enters_reciprocal_region']=labels.get('.L_x_208')==0x8c0
gates['candidate:fast_jump_bypasses_reciprocal_to_scan_join']=labels.get('.L_x_209')==0x9e0 and 0x8c0<0x8e0<0x9e0
gates['baseline:width_from_same_builtin']=b.get(0x810)=='LDCU UR17, c[0x0][0x360]'
gates['baseline:unconditional_reciprocal_in_chunk_region']=b.get(0x890)=='MUFU.RCP R9, UR4'and not any('BRA'in op for a,op in b.items()if 0x810<=a<0x890)
def lut(a,b,c,table):
 z=0
 for bit in range(32):
  index=4*((a>>bit)&1)+2*((b>>bit)&1)+((c>>bit)&1);z|=((table>>index)&1)<<bit
 return z
truth_checks=0
for a in [0,1]:
 for bbit in [0,1]:
  for cbit in [0,1]:assert (lut(a,bbit,cbit,0xc0)&1)==(a&bbit);truth_checks+=1
widths=[];shapechecks=0
for width in range(1,257):
 and_value=lut(width,width-1,0,0xc0);assert and_value==(width&(width-1));branch_nonpower=and_value!=0;power=not branch_nonpower
 if power:
  flo=width.bit_length()-1;leading=31-flo;shift=lut(leading,31,0,0x3c);assert shift==flo
  for m in range(1327):assert (m+width-1)>>shift==(m//width+int(m%width!=0));shapechecks+=1
 widths.append({'width':width,'nonpower_branch_predicate':branch_nonpower,'modeled_reachable_reciprocal':branch_nonpower,'fastpath_shift':width.bit_length()-1 if power else None})
gates['all_widths:static_bypass_truth_table']=sum(not x['modeled_reachable_reciprocal']for x in widths)==9 and shapechecks==11943
passed=all(gates.values());h.custody();h.save(H/'report.json',{'id':'D225','at':h.now(),'status':'pass_static_native_chunk_bypass'if passed else'failed_static_native_mechanism_or_reader_witness','reader_plan_sha256':sys.argv[2],'gates':gates,'witnesses':witness,'exact_candidate_instructions':{hex(k):{'expected':v,'actual':c.get(k)}for k,v in expected.items()},'width_path_models':widths,'fastpath_chunk_checks':shapechecks,'LUT_truth_checks':truth_checks,'native_semantic_inferences':P['semantics'],'all_owned_capture_and_disassembly_children_terminal':True,'new_application_kernels_solves_or_speed_samples':0,'candidate_accepted':False,'limits':'Static driverJIT control-flow/operand witnesses and PTX-linked integer model; no general SASS simulator, device-floating equivalence, measured latency, universal compiler guarantee or speed claim. Real original/candidate whole-output/input controls including nonpower widths required before full solver and complete-cycle timing.'})
for name in ['protocol.json','capture-report.json','reader-plan.json','report.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
print(json.dumps({'status':'pass'if passed else'failed','failed_gates':[k for k,v in gates.items()if not v]}),flush=True);assert passed
