import ast,collections,json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D240-fold-copy-PTX';R=ROOT/'runs/E110-resource';S=ROOT/'runs/E110-source'
def inspect(text,candidate):
 pre,after=text.split('bar.sync',1);middle=after.split('bar.sync',1)[0]
 loads=re.findall(r'ld\.global\.nc\.f32\s+(%f\d+),\s*\[(%rd\d+)\];',pre);assert len(loads)==1
 value,address=loads[0];assert re.search(r'st\.shared\.f32\s+\[%rd\d+\],\s*'+re.escape(value)+r';',pre)
 stores=re.findall(r'st\.shared\.f32\s+\[%rd\d+\],\s*(%f\d+);',middle);assert len(stores)==2;partial=stores[-1]
 where=pre if candidate else middle;rhs=value if candidate else None
 adds=re.findall(r'add\.f32\s+'+re.escape(partial)+r',\s*'+re.escape(partial)+r',\s*(%f\d+);',where);assert len(adds)==1
 if candidate:assert adds[0]==value and not re.search(r'\b(?:add|mov|ld\.[\w.]+)\.f32\s+'+re.escape(partial)+r'[,\s]',middle)
 else:
  assert not re.search(r'add\.f32',pre);rhs=adds[0];assert re.search(r'ld\.shared\.f32\s+'+re.escape(rhs)+r',\s*\[%rd\d+\];',middle)
 assert re.search(r'mov\.f32\s+'+re.escape(partial)+r',\s*0f00000000;',where)
 # Identify actual induction loop containing the recurrence/load, not only counts.
 mark=where.rindex('add.f32',0,where.index('add.f32',where.find(partial+', '+partial)) + 1) if False else None
 actual=next(m for m in re.finditer(r'add\.f32\s+'+re.escape(partial)+r',\s*'+re.escape(partial)+r',\s*'+re.escape(adds[0])+r';',where))
 label=list(re.finditer(r'(\$L__BB\d+_\d+):',where[:actual.start()]))[-1][1];end=where.find('\n$L__BB',actual.end());loop=where[where.rfind(label+':',0,actual.start()):end if end>=0 else None]
 branch=re.search(r'@(%p\d+)\s+bra\s+'+re.escape(label)+r';',loop);assert branch
 pred=branch[1];cmp=re.search(r'setp\.lt\.s32\s+'+re.escape(pred)+r',\s*(%r\d+),\s*(%r\d+);',loop);assert cmp
 j,nh=cmp[1],cmp[2];inc=re.search(r'add\.s32\s+'+re.escape(j)+r',\s*'+re.escape(j)+r',\s*(%r\d+);',loop);assert inc;width=inc[1]
 assert re.search(r'ld\.param\.u32\s+'+re.escape(nh)+r',\s*\[up_fold_param_19\];',text)
 assert re.search(r'mov\.u32\s+'+re.escape(width)+r',\s*%ntid\.x;',where)
 init=re.search(r'mov\.u32\s+'+re.escape(j)+r',\s*(%r\d+);',where[:where.rfind(label+':',0,actual.start())]);assert init;tid=init[1]
 assert re.search(r'mov\.u32\s+'+re.escape(tid)+r',\s*%tid\.x;',text)
 assert re.search(r'(?:cvt\.s64\.s32|mul\.wide\.s32)\s+%rd\d+,\s*'+re.escape(j)+r'(?:;|,\s*4;)',loop)
 return {'global_fill_value':value,'global_fill_address':address,'partial_value':partial,'partial_rhs':adds[0],'partial_producer':'global fill'if candidate else'later shared reread','loop_label':label,'induction_register':j,'bound_parameter':19,'width_register':width,'TID_register':tid,'recurrence_loop':loop,'same_global_value_stored_to_shared':True,'zero_seed_and_thread_j_stride_bound_verified':True,'partial_store_after_card_loop':True,'barrier_sites':text.count('bar.sync'),'float_arithmetic_inventory':dict(collections.Counter(re.findall(r'^\s*((?:add|sub|mul|div|fma|mad|max|min|sqrt|rcp)(?:\.[\w]+)*\.f(?:32|64))\s',text,re.M)))}
if len(sys.argv)==1:
 h.custody();H.mkdir(exist_ok=False);assert all(h.read(R/'report.json')['gates'].values());files=[Path(__file__),R/'protocol.json',R/'report.json',S/'manifest.json',S/'source-review.json',ROOT/'runs/D239-fold-copy-sum-scout/source-review.json',ROOT/'epoch/common.py']+[R/'execution'/(arm+'-'+arch+'-up_fold.ptx.txt')for arm in ['baseline','candidate']for arch in ['compute_120','compute_75']]
 h.save(H/'protocol.json',{'id':'D240','at':h.now(),'status':'FROZEN_PRE_CPU_STATIC_READER','input_sha256':{str(p):h.sha(p)for p in files},'gate':'Both120/75 actual globalf32fill load also sharedstored; candidate exactsame register feeds zero-seeded selfaddition loop withTID init,+blockDim andnh_o param19bound beforefirstbarrier. Original recurrence consumes later sharedload withsameinduction andstored totalparts aftercardloop. Candidate retains computedpartial unchanged acrosscardloop tothatstore. AllFP arithmeticopcode counts andbarrier sites identical. Source-byte reversal establishes unchanged card/reduction/math/address instructions, further numerical/native gates mandatory.','limits':'Operand/induction/source structural witness, not fullPTX CFG/FP simulator/universal IEEEpayload/nativebehavior/timing proof. Positive/wrongoperand negative fixtures required; no appkernels.'});print(h.sha(H/'protocol.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;P=h.read(H/'protocol.json');h.pin(H/'protocol.json',sys.argv[1]);h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
rows={};fixtures=[]
for arch in ['compute_120','compute_75']:
 b=(R/'execution'/('baseline-'+arch+'-up_fold.ptx.txt')).read_text();c=(R/'execution'/('candidate-'+arch+'-up_fold.ptx.txt')).read_text();br=inspect(b,False);cr=inspect(c,True);assert br['barrier_sites']==cr['barrier_sites']==3 and br['float_arithmetic_inventory']==cr['float_arithmetic_inventory'];rows[arch]={'baseline':br,'candidate':cr}
 wrong=c.replace('add.f32\t'+cr['partial_value'], 'add.f32\t'+cr['partial_value']) # Mutation uses actual whitespace-independent match below.
 pat=r'(add\.f32\s+'+re.escape(cr['partial_value'])+r',\s*'+re.escape(cr['partial_value'])+r',\s*)'+re.escape(cr['global_fill_value'])+r';';wrong,n=re.subn(pat,lambda m:m[1]+'%f999999;',c);assert n==1
 try:inspect(wrong,True)
 except AssertionError:fixtures.append({'arch':arch,'wrong_global_operand_detected':True})
 else:raise AssertionError('wrong operand not detected')
h.save(H/'report.json',{'id':'D240','at':h.now(),'status':'pass_source_and_param_bound_fused_partial_PTX','protocol_sha256':sys.argv[1],'architecture_witnesses':rows,'negative_fixtures':fixtures,'all_owned_children_terminal':True,'application_kernels_or_speed_samples':0,'candidate_accepted':False,'limits':P['limits']})
for name in ['protocol.json','report.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
print('Both PTX producer/partial/induction/static FP gates passed.',flush=True)
