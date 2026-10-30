import collections,hashlib,json,re,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D296-hand-word-PTX';R=ROOT/'runs/E121-resource'
def math_signature(t):
 floats={};preds={};out=[]
 def sub(m):
  d=floats if m[0].startswith('%f')else preds
  if m[0]not in d:d[m[0]]=len(d)
  return('F'if d is floats else'P')+str(d[m[0]])
 for line in t.splitlines():
  if re.match(r'^\s*(?:add|sub|mul|fma|div|mov|selp)[\w.]*\.f32\s',line):out.append(re.sub(r'%[fp]\d+',sub,' '.join(line.split())))
 return out
def definitions(t):
 out=collections.defaultdict(list)
 for line in t.splitlines():
  m=re.match(r'^\s*(?:@!?%p\d+\s+)?([a-z][\w.]*)\s+([^;]+);\s*$',line)
  if m:
   op=m[1];args=[x.strip()for x in m[2].split(',')]
   if not op.startswith(('st.','bar.','bra'))and re.fullmatch(r'%[rf]\w*\d+',args[0]):out[args[0]].append((op,args[1:]))
 return out
def ancestry(reg,defs,seen=None):
 seen=set()if seen is None else seen
 if reg in seen:return set()
 seen.add(reg);out=set()
 for op,args in defs.get(reg,[]):
  if op.startswith('ld.param.'):
   for a in args:
    m=re.search(r'param_(\d+)',a)
    if m:out.add(int(m[1]))
  else:
   for a in args:
    for p in re.findall(r'%[rf]\w*\d+',a):out|=ancestry(p,defs,seen)
 return out
def inspect(name,t,b):
 body=t.split('{',1)[1];old=b.split('{',1)[1];legacy=[11,12]if name=='up_fold'else[20,21];same_param=15 if name=='up_fold'else 19
 for param in legacy:assert name+'_param_'+str(param)+']'in old and name+'_param_'+str(param)+']'not in body
 assert math_signature(t)==math_signature(b)and '.ftz'not in t
 assert re.findall(r'\bbar\.(?:sync|red)(?:\.[\w]+)*[^;]*;',t)==re.findall(r'\bbar\.(?:sync|red)(?:\.[\w]+)*[^;]*;',b)
 shifts=re.findall(r'shr\.u32\s+(%r\d+),\s*(%r\d+),\s*12;',body);assert len(shifts)==1;sc,word=shifts[0]
 loads=re.findall(r'ld\.global\.nc\.u32\s+'+re.escape(word)+r',\s*\[(%rd\d+)\];',body);assert len(loads)==1;assert same_param in ancestry(loads[0],definitions(body))
 sentinel=re.search(r'setp\.eq\.s32\s+(%p\d+),\s*'+re.escape(sc)+r',\s*2047;\s*mov\.f32\s+(%f\d+),\s*0f00000000;\s*@\1 bra\s+(\$L__BB\d+_\d+);',body);assert sentinel;join=body.index(sentinel[3]+':',sentinel.end());load_region=body[sentinel.end():join];assert re.search(r'mul\.wide\.u32\s+(%rd\d+),\s*'+re.escape(sc)+r',\s*4;',load_region);assert re.search(r'ld\.shared\.f32\s+'+re.escape(sentinel[2])+r',\s*\[%rd\d+\];',load_region)
 first=re.search(r'shl\.b32\s+(%r\d+),\s*'+re.escape(word)+r',\s*(\d+);\s*cvt\.u64\.u32\s+(%rd\d+),\s*\1;\s*and\.b64\s+(%rd\d+),\s*\3,\s*(\d+);',body);assert first and(first[2],first[5])==('2','252')
 second=re.search(r'shr\.u32\s+(%r\d+),\s*'+re.escape(word)+r',\s*(\d+);\s*cvt\.u64\.u32\s+(%rd\d+),\s*\1;\s*and\.b64\s+(%rd\d+),\s*\3,\s*(\d+);',body);assert second and(second[2],second[5])==('4','252')
 return {'packed_word_register':word,'packed_global_load_address':loads[0],'same_param_index':same_param,'legacy_card_param_indices_unused':legacy,'same_decode_shift':12,'absent_sentinel':2047,'same_shared_load_branch':sentinel[0]+load_region,'card1_byte_expression':{'left_shift':int(first[2]),'mask':int(first[5]),'PTX':first[0]},'card2_byte_expression':{'right_shift':int(second[2]),'mask':int(second[5]),'PTX':second[0]},'ordered_FP_math_select_register_topology_exact':True,'FP_math_select_instructions':len(math_signature(t)),'FP_math_select_signature_sha256':hashlib.sha256('\n'.join(math_signature(t)).encode()).hexdigest(),'static_barrier_inventory_exact':True,'limits':'Canonicalmath/select-registertopology omits memoryaddresses and integerpredicateprovenance; individualhandwordload/decode/sentinelbinds themonlypartially. Not afullPTXinterpreter/universalFPproof. Source/callers/privateencoding/rawGPU/fullengine/canonical/broadgates remain required.'}
if len(sys.argv)==1:
 h.custody();H.mkdir(exist_ok=False);assert all(h.read(R/'report.json')['gates'].values());files=[Path(__file__),ROOT/'epoch/common.py',R/'protocol.json',R/'report.json',R/'host-encode-report.json',R/'execution/host-hand-words.bin',ROOT/'runs/E121-source/manifest.json',ROOT/'runs/D295-hand-word-scout/encoding-contract.json']+[R/'execution'/(a+'-'+arch+'-'+name+'.ptx.txt')for a in ['baseline','candidate']for arch in ['compute_120','compute_75']for name in ['up_fold','up_show']]
 h.save(H/'protocol.json',{'id':'D296','at':h.now(),'status':'FROZEN_PRE_EMITTED_PTX_AND_HOST_RAW_ADDRESS_READER','input_sha256':{str(p):h.sha(p)for p in files},'requirements':'All4targetentry/arch actualpackedload/sameparamancestor,legacycardparam dependenciesabsent,12shift/2047sentinel skips originalroread;actualbyteoffsetdecode(left2&252,right4&252), originalorderedFPmath/select-registercanonicaltopology andbarriers exact. Check actualcompiledbyteexpressions onall1763580retainedhostwordrecords. Wrongsentinel/cardmask/cardshift/FPoperation/legacyload negativefixtures. No compiler/module/applicationkernel/solver/speed.'});print(h.sha(H/'protocol.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json');h.custody()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status())
 for p,d in P['input_sha256'].items():h.pin(p,d)
 witnesses={};negatives=[]
 for arch in ['compute_120','compute_75']:
  for name in ['up_fold','up_show']:
   t=(R/'execution'/('candidate-'+arch+'-'+name+'.ptx.txt')).read_text();b=(R/'execution'/('baseline-'+arch+'-'+name+'.ptx.txt')).read_text();w=inspect(name,t,b);witnesses[arch+':'+name]=w
   mutations=[('sentinel',t.replace('2047;','2046;',1)),('card_mask',t.replace(w['card1_byte_expression']['PTX'],w['card1_byte_expression']['PTX'].replace('252;','248;'),1)),('card_shift',t.replace(w['card2_byte_expression']['PTX'],re.sub(r',\s*4;',', 5;',w['card2_byte_expression']['PTX'],count=1),1)),('FP_operation',t.replace('sub.f32','add.f32',1)),('legacy_load',t.replace('{','{\n ld.param.u64 %rd999999, ['+name+'_param_'+str(w['legacy_card_param_indices_unused'][0])+'];',1))]
   for label,bad in mutations:
    assert bad!=t
    try:inspect(name,bad,b)
    except AssertionError:negatives.append(arch+':'+name+':'+label)
    else:raise AssertionError('negativefixtureaccepted '+label)
 raw=(R/'execution/host-hand-words.bin').read_bytes();magic=b'E121_HAND_WORDS_V1\n';assert raw.startswith(magic);count,=struct.unpack_from('<Q',raw,len(magic));start=len(magic)+8;assert count==1763580 and len(raw)==start+count*16;checks=0
 for a,b,s,word in struct.iter_unpack('<IIII',raw[start:]):
  for w in witnesses.values():
   assert((word<<w['card1_byte_expression']['left_shift'])&0xffffffff)&w['card1_byte_expression']['mask']==a*4
   assert(word>>w['card2_byte_expression']['right_shift'])&w['card2_byte_expression']['mask']==b*4
   sc=word>>w['same_decode_shift'];assert(0xffffffff if sc==w['absent_sentinel']else sc)==s;checks+=3
 h.save(H/'report.json',{'id':'D296','at':h.now(),'status':'pass_scoped_terminal_hand_word_PTX_load_decode_FP_topology_and_host_address_domain','protocol_sha256':sys.argv[1],'entry_witnesses':witnesses,'negative_reader_fixtures':negatives,'compiled_host_records_address_replayed':count,'compiled_expression_checks':checks,'new_compiler_GPU_applicationkernels_solver_or_speed_samples':0,'candidate_adopted':False});h.custody()
print('D296 packedword/load/decode/FPtopology andwholehostaddressdomain pass.',flush=True)
