import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D230-native-stride';R=ROOT/'runs/E109-resource';assert len(sys.argv)>=2
if sys.argv[1]=='prepare':
 c=h.read(H/'capture-report.json');paths=[Path(__file__),H/'protocol.json',H/'capture-report.json',H/'execution/complete.json',H/'execution/candidate/capture.exit.json',H/'execution/candidate/disassemble.exit.json',R/'report.json',ROOT/'runs/D229-stride-PTX-r2/report.json',ROOT/'runs/E109-source/manifest.json',ROOT/'runs/E109-source/source-review.json']+[Path(v['path'])for arm in c['entry_sections'].values()for v in arm.values()]+[p for p in(R/'execution').glob('baseline-compute_120-*.ptx.txt')]
 h.save(H/'reader-plan.json',{'id':'D230-native-stride-reader','at':h.now(),'status':'FROZEN_PRE_NATIVE_OPERAND_READER','input_sha256':{str(p):h.sha(p)for p in paths},'rules':'For each affectedentry infer last32parameter constoffset from exact original PTX ABI natural8/4packing plusknown kernelargbase0x380; compare matched scalar load/copy definitions with overwrite-sensitive32/64/128wordregister model. Require baseline stride signbitshift+highpartialIMAD, candidate no stride signbitshift/highpartialIMAD, original/candidate unsigned32x32->64strideproducts present. All five mustpass,no source/helper/count/entrysubset/flags rescue. Actualinput/output rawtests stillmandatory.','limits':'Static local integer-register dataflow with source/PTX-linked constantlayout,not a fullSASSCFG/value/FPsimulator. Conditionalcopies and crossbranch registerlifetimes require scopedwitness review; tagged instructionchain outputretained. No dynamicdevicecycle/speed/accuracy/no-tradeoff/adoptionclaim.'})
 print(h.sha(H/'reader-plan.json'),flush=True);sys.exit(0)
assert sys.argv[1]=='execute'and len(sys.argv)==3;h.pin(H/'reader-plan.json',sys.argv[2]);P=h.read(H/'reader-plan.json');h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
def reg(operand):
 operand=operand.strip().replace('.reuse','')
 return operand if re.fullmatch(r'U?R\d+',operand)else None
def words(register,count):
 m=re.fullmatch(r'(U?R)(\d+)',register);return[m[1]+str(int(m[2])+i)for i in range(count)]
def trace(text,offset):
 pure={};high={};loads=[];signs=[];high_products=[];wide=[];instructions=0
 for line in text.splitlines():
  m=re.match(r'^\s*/\*([0-9a-f]{4,})\*/\s*(.*?)\s*;',line)
  if not m:continue
  pc=int(m[1],16);code=m[2];clean=re.sub(r'^@\S+\s+','',code);parts=clean.split(None,1);op=parts[0];a=[x.strip()for x in parts[1].split(',')]if len(parts)>1 else[];instructions+=1
  def item(extra=None):return {'address_hex':hex(pc),'instruction':code,**(extra or{})}
  # Constant vector loads can place the scalar in any contained32bitword.
  cm=re.fullmatch(r'(LDCU|LDC)(?:\.(64|128))?',op)
  if cm and len(a)==2 and reg(a[0]):
   n=int(cm[2]or '32')//32;dest=reg(a[0]);out=words(dest,n)
   for r in out:pure.pop(r,None);high.pop(r,None)
   lm=re.fullmatch(r'c\[0x0\]\[0x([0-9a-f]+)\]',a[1])
   if lm:
    start=int(lm[1],16)
    if start<=offset<start+4*n:
     r=out[(offset-start)//4];proof=item({'scalar_register':r,'constant_byte_offset':offset,'vector_load_words':n});pure[r]=proof;loads.append(proof)
   continue
  dest=reg(a[0])if a else None
  # Optional predicate+register LOP3 output: the secondoperand is the worddest.
  if not dest and len(a)>1 and re.fullmatch(r'U?P\d+',a[0])and op in ['LOP3.LUT','ULOP3.LUT']:dest=reg(a[1])
  references=[reg(x)for x in a[1:]]
  if op in ['SHF.R.S32.HI','USHF.R.S32.HI']and len(a)==4 and a[2]=='0x1f'and reg(a[3])in pure and a[1]in ['RZ','URZ']:
   source=pure[reg(a[3])];proof=item({'stride_value_definition':source});signs.append(proof);new_high=proof
  else:new_high=None
  if op.startswith(('IMAD','UIMAD'))and '.MOV.'not in op and len(a)>=4:
   multiplicands=[reg(a[1]),reg(a[2])];tagged=[x for x in multiplicands if x in high]
   if tagged and a[1]not in ['RZ','URZ','0x0']and a[2]not in ['RZ','URZ','0x0']:high_products.append(item({'signed_stride_high_definition':high[tagged[0]]}))
   stride_inputs=[x for x in multiplicands if x in pure]
   if '.WIDE.U32'in op and stride_inputs and dest:wide.append(item({'stride_value_definition':pure[stride_inputs[0]],'destination_word_pair':words(dest,2)}))
  copy_source=None
  if op in ['MOV','UMOV','R2UR']and len(a)==2:copy_source=reg(a[1])
  elif op=='IMAD.MOV.U32'and len(a)==4 and a[1]in ['RZ','URZ']and a[2]in ['RZ','URZ']:copy_source=reg(a[3])
  new_pure=pure.get(copy_source);copy_high=high.get(copy_source)
  if dest:
   count=4 if '.128'in op else(2 if '.64'in op or'.WIDE'in op else 1)
   for r in words(dest,count):pure.pop(r,None);high.pop(r,None)
   if new_pure:pure[dest]=item({'copied_stride_value_definition':new_pure})
   if new_high:high[dest]=new_high
   elif copy_high:high[dest]=item({'copied_stride_high_definition':copy_high})
 return {'constant_offset_hex':hex(offset),'stride_constant_loads':loads,'stride_signbit_extractions':signs,'signed_stride_high_partial_products':high_products,'stride_unsigned_wide_products':wide,'instruction_count_diagnostic_only':instructions}
fixture='''/*0000*/ LDCU UR4, c[0x0][0x440];
/*0010*/ USHF.R.S32.HI UR5, URZ, 0x1f, UR4;
/*0020*/ IMAD R1, R2, UR5, R3;
/*0030*/ IMAD.WIDE.U32 R6, R2, UR4, RZ;
/*0040*/ UMOV UR4, URZ;
/*0050*/ USHF.R.S32.HI UR9, URZ, 0x1f, UR4;
/*0060*/ LDCU.64 UR10, c[0x0][0x438];
/*0070*/ LDCU.128 UR12, c[0x0][0x438];
/*0080*/ USHF.R.S32.HI UR15, URZ, 0x1f, UR14;
/*0090*/ UIMAD UR16, UR2, UR15, UR3;
/*00a0*/ UIMAD.WIDE.U32 UR20, UR2, UR14, URZ;
'''
f=trace(fixture,0x440);assert[len(f[k])for k in ['stride_constant_loads','stride_signbit_extractions','signed_stride_high_partial_products','stride_unsigned_wide_products']]==[2,2,2,2];assert [x['address_hex']for x in f['stride_signbit_extractions']]==['0x10','0x80']
C=h.read(H/'capture-report.json');resource=h.read(R/'report.json');results={};gates={};offsets={}
for name,arms in {n:{a:v[n]for a,v in C['entry_sections'].items()}for n in C['entry_sections']['baseline']}.items():
 ptx=(R/'execution'/('baseline-compute_120-'+name+'.ptx.txt')).read_text(encoding='utf-8').split('{',1)[0];widths=[int(x)for x in re.findall(r'\.param\s+\.u(32|64)\s+',ptx)];assert len(widths)==resource['entry_tables']['compute_120'][name]['parameter_count']and widths[-1]==32;offset=0
 for i,bits in enumerate(widths):align=bits//8;offset=(offset+align-1)//align*align;last=offset;offset+=align
 constoff=0x380+last;offsets[name]=constoff;results[name]={}
 for arm,info in arms.items():
  h.pin(info['path'],info['sha256']);results[name][arm]=trace(Path(info['path']).read_text(encoding='utf-8'),constoff)
 b,c=results[name]['baseline'],results[name]['candidate'];gates[name+':both_scalar_const_words_found']=bool(b['stride_constant_loads'])and bool(c['stride_constant_loads']);gates[name+':baseline_stride_signcorrection_present']=bool(b['stride_signbit_extractions'])and bool(b['signed_stride_high_partial_products']);gates[name+':candidate_stride_signcorrection_absent']=not c['stride_signbit_extractions']and not c['signed_stride_high_partial_products'];gates[name+':unsigned_wide_products_preserved']=bool(b['stride_unsigned_wide_products'])and bool(c['stride_unsigned_wide_products'])
assert offsets=={'up_fold':0x410,'up_show':0x440,'up_chance':0x3e4,'up_action':0x40c,'up_action_eval':0x3ec},offsets
passed=all(gates.values());h.custody();h.save(H/'report.json',{'id':'D230','at':h.now(),'status':'pass_static_native_stride_signcorrection_removal'if passed else'failed_native_stride_mechanism_or_reader','reader_plan_sha256':sys.argv[2],'gates':gates,'native_entry_dataflow':results,'parameter_constant_offsets':{k:hex(v)for k,v in offsets.items()},'overwrite_and_vector_constant_word_fixture_passed':True,'all_owned_native_disassembler_children_terminal':True,'new_applicationkernels_solves_or_speed_samples':0,'candidate_accepted':False,'limits':P['limits'],'next':'Freezeall5affectedkerneldirectphysical/exceptional/guardand actualengine controls withoriginal source/addressvalues and unchanged27/21/15/20/17argument bitABIs,then fullcanonical/ordinary/fullcycle1%strictfixture/fresh16/broad/material/holdout/cumulative/application beforeadoption. No gain fromstaticcode/resource indicators.'})
for name in ['protocol.json','capture-report.json','reader-plan.json','report.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
print(json.dumps({'status':'pass'if passed else'failed','failed_gates':[k for k,v in gates.items()if not v],'counts':{n:{a:{k:len(d[k])for k in ['stride_constant_loads','stride_signbit_extractions','signed_stride_high_partial_products','stride_unsigned_wide_products']}for a,d in arms.items()}for n,arms in results.items()}}),flush=True);assert passed
