import collections,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D229-stride-PTX';R=ROOT/'runs/E109-resource';assert len(sys.argv)>=2
if sys.argv[1]=='prepare':
 q=h.read(R/'report.json');assert q['status']=='pass_compiled_resources_mechanism_pending'and all(q['gates'].values());H.mkdir(exist_ok=False)
 files=[Path(__file__),R/'protocol.json',R/'report.json',ROOT/'runs/E109-source/manifest.json',ROOT/'runs/E109-source/source-review.json',ROOT/'runs/E109-source/baseline.cu',ROOT/'runs/E109-source/candidate.cu',ROOT/'runs/D228-CFV-stride-scout/report.json',ROOT/'epoch/common.py']+[p for p in(R/'execution').glob('*.ptx.txt')]
 h.save(H/'protocol.json',{'id':'D229','at':h.now(),'status':'FROZEN_PRE_CPU_COMPILED_TYPE_DATAFLOW_READER','input_sha256':{str(p):h.sha(p)for p in files},'targets':h.read(R/'protocol.json')['target_entries'],'rules':'Bind each target last32bitparam to nh_max using exact9ABIheaders and unchangedhostarg/source contract. Forboth120/75 trace identitycopies/conversions from thatparam, require baseline signed64extension(s),candidate zero such strideextensions and preserved64bit stride-derived multiplyresults. Source reverses exactly aftersix types, so everyfloating expression/condition/loop/address expression token unchanged. Inventory emittedfloatarithmetic/compare ops in full; counts/scheduling/unrolling differences diagnostic, never proof/waiver of numerical equivalence. Actualcurrent-driver native signtermremoval/wideproduct witnesses required next; no applicationkernels until both gates.','failure':'Absent intended signextension/wideaddress mechanism closes exactsix-declaration form, noothercount/entrysubset/width/helper/flagsrescue. Mechanicalreadererrors additive withoutcompletedGPUcasesrerun.'})
 print(h.sha(H/'protocol.json'),flush=True);sys.exit(0)
assert sys.argv[1]=='execute'and len(sys.argv)==3;h.pin(H/'protocol.json',sys.argv[2]);P=h.read(H/'protocol.json');h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
base=(ROOT/'runs/E109-source/baseline.cu').read_bytes();candidate=(ROOT/'runs/E109-source/candidate.cu').read_bytes();assert base.count(b'int nh_max)')==candidate.count(b'u32 nh_max)')==6 and candidate.replace(b'u32 nh_max)',b'int nh_max)')==base
resources=h.read(R/'report.json');tables={};gates={}
def trace(path,name,nparam):
 text=path.read_text(encoding='utf-8');pure=set();derived=set();signed=[];wide=[];other_mult=[];fops=collections.Counter();root=[]
 for number,line in enumerate(text.splitlines(),1):
  code=line.split('//',1)[0].strip();m=re.fullmatch(r'(?:@!?%p\d+\s+)?([a-z][a-z0-9_.]*)\s+([^;]+);',code)
  if not m:continue
  op=m[1];a=[x.strip()for x in m[2].split(',')];dest=a[0];refs=[r for x in a[1:]for r in re.findall(r'%r(?:d)?\d+',x)];ispure=any(r in pure for r in refs);isderived=any(r in derived for r in refs)
  if re.search(r'\.(?:f32|f64)(?:\.|$)',op)and not op.startswith(('ld.','st.','mov.','cvt.')):fops[op]+=1
  if op=='ld.param.u32'and a[1]=='['+name+'_param_'+str(nparam-1)+']':
   root.append({'register':dest,'line':number,'code':code});pure.add(dest);derived.add(dest);continue
  if op=='cvt.s64.s32'and ispure:signed.append({'line':number,'code':code})
  if op.startswith(('mul.','mad.'))and isderived:
   item={'line':number,'code':code}
   if dest.startswith('%rd')and ('.s64'in op or'.u64'in op or'.wide.'in op):wide.append(item)
   else:other_mult.append(item)
  if re.fullmatch(r'%r(?:d)?\d+',dest):
   identity=op in ['mov.u32','mov.b32','mov.u64','mov.b64','cvt.u64.u32','cvt.s64.s32','cvt.u32.u64','cvt.u32.s64']and ispure
   if identity:pure.add(dest)
   else:pure.discard(dest)
   if isderived and not op.startswith('ld.'):derived.add(dest)
   else:derived.discard(dest)
 return {'PTX_sha256':h.sha(path),'stride_parameter_ordinal':nparam-1,'stride_parameter_bindings':root,'stride_signed64_extensions':signed,'stride_derived_wide_multiplies':wide,'other_stride_derived_multiplications':other_mult,'float_arithmetic_compare_opcode_inventory':dict(fops),'static_only':True}
for arch in ['compute_120','compute_75']:
 tables[arch]={}
 for name in P['targets']:
  count=resources['entry_tables'][arch][name]['parameter_count'];arms={arm:trace(R/'execution'/(arm+'-'+arch+'-'+name+'.ptx.txt'),name,count)for arm in ['baseline','candidate']};b,c=arms['baseline'],arms['candidate'];gates[arch+':'+name+':one_original_scalar32_parameter_binding']=len(b['stride_parameter_bindings'])==len(c['stride_parameter_bindings'])==1;gates[arch+':'+name+':baseline_stride_signextension_present']=len(b['stride_signed64_extensions'])>0;gates[arch+':'+name+':candidate_stride_signextension_removed']=len(c['stride_signed64_extensions'])==0;gates[arch+':'+name+':wide_address_product_preserved']=len(b['stride_derived_wide_multiplies'])>0 and len(c['stride_derived_wide_multiplies'])>0
  arms['float_opcode_inventory_equal']=b['float_arithmetic_compare_opcode_inventory']==c['float_arithmetic_compare_opcode_inventory'];tables[arch][name]=arms
passed=all(gates.values());h.custody();h.save(H/'report.json',{'id':'D229','at':h.now(),'status':'pass_param_qualified_stride_signextension_removal'if passed else'failed_compiled_stride_mechanism_or_reader','protocol_sha256':sys.argv[2],'gates':gates,'entry_dataflow':tables,'floating_source_dependencies_byte_exact':True,'ABI_all9_headers_exact':True,'all_CFVarithmetic_source_still_u64':True,'new_CUDA_contexts_compilers_applicationkernels_solves_or_speed_samples':0,'candidate_accepted':False,'limits':'Conservative static scalar identity/derived-register trace,not fullPTX/FP-DAG/controlflow simulator. Same original sourcefloatdependency statements and exacttype reversal; emittedarithmetic inventories retained including anyloopunrolling differences. No devicefloat/numerical equivalence, dynamiclatency,completecycle oradoption claim. Native signterm/wideproduct review then all raw/engine/fullcanonical/ordinary/speed/adoption gates remain.'})
for name in ['protocol.json','report.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
print(json.dumps({'status':'pass'if passed else'failed','failed_gates':[k for k,v in gates.items()if not v],'float_inventory_equal':{a:{n:d['float_opcode_inventory_equal']for n,d in values.items()}for a,values in tables.items()}}),flush=True);assert passed
