import collections,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D293-sparse-card-PTX';R=ROOT/'runs/E120-resource'
def fp_inventory(t):return dict(collections.Counter(re.findall(r'^\s*((?:add|sub|mul|fma|div|mov|setp|abs|selp)[\w.]*\.f32)\s',t,re.M)))
def inspect(t,b):
 barriers=list(re.finditer(r'\bbar\.(?:sync|red)(?:\.[\w]+)*[^;]*;',t));assert len(barriers)==5 and barriers[0][0].startswith('bar.red.or.pred')and all(x[0].startswith('bar.sync')for x in barriers[1:])
 assert '.ftz'not in t and fp_inventory(t)==fp_inventory(b)
 assert '.shared .align 4 .b8 _ZZ7up_showE13kept_card_end[208];'in t
 pre=t[:barriers[0].start()];assert re.search(r'ld\.param\.u32\s+%r140,\s*\[up_show_param_25\];',pre)
 assert re.search(r'setp\.gt\.u32\s+%p2,\s*%r140,\s*1326;\s*selp\.u32\s+%r290,\s*1,\s*0,\s*%p2;',pre)
 assert re.search(r'ld\.global\.nc\.f32\s+%f92,\s*\[%rd70\];',pre)
 assert re.search(r'st\.shared\.f32\s+\[%rd73\],\s*%f92;\s*mov\.b32\s+%r147,\s*%f92;\s*setp\.gt\.u32\s+%p4,\s*%r147,\s*1736441856;\s*selp\.u32\s+%r148,\s*1,\s*0,\s*%p4;\s*or\.b32\s+%r290,\s*%r290,\s*%r148;',pre)
 assert re.search(r'setp\.ne\.u32\s+%p1,\s*%r290,\s*0;\s*bar\.red\.or\.pred\s+%p2,\s*0,\s*%p1;\s*selp\.u32\s+%r17,\s*1,\s*0,\s*%p2;',t)
 pack=t[t.index('$L__BB4_15:'):t.index('$L__BB4_36:')];assert barriers[1].end()<t.index('$L__BB4_15:')<t.index('$L__BB4_36:')<barriers[2].start()
 assert re.search(r'ld\.global\.nc\.u32\s+%r26,\s*\[%rd98\];\s*sub\.s32\s+%r27,\s*%r26,\s*%r4;\s*ld\.global\.nc\.u32\s+%r28,\s*\[%rd98\+4\];\s*sub\.s32\s+%r29,\s*%r28,\s*%r4;\s*mov\.u32\s+%r302,\s*%r29;\s*@%p13 bra\s+\$L__BB4_35;',pack)
 assert re.search(r'setp\.ne\.s32\s+%p13,\s*%r17,\s*0;',pack)
 assert not re.search(r'\b(?:add|sub|mul|fma|div)\.[\w.]*f32\b',pack)
 for r in range(159,168):
  if r==160:continue
  assert re.search(r'ld\.shared\.u32\s+%r'+str(r)+r',\s*\[%rd\d+\];\s*setp\.(?:eq|ne)\.s32\s+%p\d+,\s*%r'+str(r)+r',\s*0;',pack)
 stores=[('%rd105','%r33'),('%rd109','%r37'),('%rd114','%r46'),('%rd118','%r49'),('%rd122','%r52'),('%rd126','%r55')]
 for addr,pos in stores:assert re.search(r'st\.shared\.u32\s+\['+addr+r'\],\s*'+pos+r';',pack)
 assert re.search(r'add\.s32\s+%r297,\s*%r297,\s*4;\s*setp\.ne\.s32\s+%p26,\s*%r297,\s*%r29;\s*@%p26 bra\s+\$L__BB4_26;',pack)
 assert re.search(r'add\.s64\s+%rd129,\s*%rd128,\s*%rd127;\s*st\.shared\.u32\s+\[%rd129\],\s*%r302;',pack)
 consumers=t[barriers[4].end():];assert consumers.count('_ZZ7up_showE13kept_card_end')==2
 for base,addr,end,out in [('%rd177','%rd178','%r100','%r101'),('%rd241','%rd242','%r115','%r116')]:
  assert re.search(r'mov\.u64\s+'+base+r',\s*_ZZ7up_showE13kept_card_end;\s*add\.s64\s+'+addr+r',\s*'+base+r',\s*%rd\d+;\s*ld\.shared\.u32\s+'+end+r',\s*\['+addr+r'\];\s*add\.s32\s+'+out+r',\s*'+end+r',\s*%r4;',consumers)
 return {'five_barriers':[m[0]for m in barriers],'bounded_reach_bits':hex(0x67800000),'nh_o_limit':1326,'unsafe_fallback':'Anybad r17!=0 ->BB35 withr302 originalrelativeend r29; endpointstores thencommonprefix/consumer.','compaction_region':pack,'six_nontrivial_index_store_sites':stores,'first_peeled_element':'Originalbeginpos remains in-place; bit!=0incrementswrite exactlyone, no redundant selfstore.','all7peeled_unrolled_reach_zero_tests':True,'all_endpoint_consumers_after_original_fifth_barrier':True,'floating_opcode_inventory_unchanged':fp_inventory(t),'limits':'Bounded fixedPTX instruction/CFG witness and sourcecontract, not a generalPTX interpreter/fulladdress-or-floatingprovenanceproof. Actualnative/dataflow and rawGPU/wholeengine/canonical/broad gates remain. FPcounts alone do not prove equivalence.'}
if len(sys.argv)==1:
 h.custody();H.mkdir(exist_ok=False);assert all(h.read(R/'report.json')['gates'].values());files=[Path(__file__),ROOT/'epoch/common.py',R/'protocol.json',R/'report.json',ROOT/'runs/E120-source/manifest.json',ROOT/'runs/D292-sparse-card-scout/dependency-and-FP-contract.json']+[R/'execution'/(a+'-compute_120-up_show.ptx.txt')for a in ['baseline','candidate']]
 h.save(H/'protocol.json',{'id':'D293','at':h.now(),'status':'FROZEN_PRE_EMITTED_PTX_READER','input_sha256':{str(p):h.sha(p)for p in files},'requirements':'ActualORreachguard/fullnh_o<=1326 +2^80uintbound, samefivebarriers with compaction between2/3, originalend fallback,7actualzero-bitpeel/unrollsites/stableoriginalpositionstores/endpoints,2endpointconsumers after5. OriginalFPinventory, noFTZ. Wrongthreshold/zerotest/fallback/store/barrier negativefixtures. No GPU/compiler/solver/performance.'});print(h.sha(H/'protocol.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json');h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
t=(R/'execution/candidate-compute_120-up_show.ptx.txt').read_text();b=(R/'execution/baseline-compute_120-up_show.ptx.txt').read_text();w=inspect(t,b);fixtures=[]
mutations=[('threshold','1736441856;','1736441857;'),('zero_predicate','%p22, %r164, 0;','%p22, %r164, 1;'),('fallback','@%p13 bra \t$L__BB4_35;','@%p13 bra \t$L__BB4_36;'),('wrong_position','[%rd105], %r33;','[%rd105], %r37;'),('missing_barrier','bar.sync \t0;','nop;')]
for name,old,new in mutations:
 assert old in t;bad=t.replace(old,new,1)
 try:inspect(bad,b)
 except AssertionError:fixtures.append(name)
 else:raise AssertionError('negative fixtureaccepted '+name)
h.save(H/'report.json',{'id':'D293','at':h.now(),'status':'pass_scoped_sparse_card_PTX_guard_compaction_endpoint_and_barrier_witness','protocol_sha256':sys.argv[1],'witness':w,'negative_reader_fixtures':fixtures,'new_GPU_kernel_solver_compiler_or_speed_samples':0,'candidate_adopted':False});h.custody();print('D293 scoped PTX mechanism pass; full raw controls still mandatory.',flush=True)
