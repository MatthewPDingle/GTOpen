"""Root raw-array decoder for the fixed E047 direct GPU comparison."""
import json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
assert sys.byteorder=='little'
P=old.read(HERE/'protocol.json');C=old.read(HERE/'execution/complete-r2.json');cases=old.read(HERE/'corpus.json')['cases']
for p,h in P['input_sha256'].items():old.pin(p,h)
for p,h in C['raw_file_sha256'].items():old.pin(p,h)
OUT=old.ROOT/'comparisons/E047-kernel-control-r2';assert not OUT.exists();OUT.mkdir();checks=0
def req(v,m):
 global checks
 assert v,m;checks+=1
class Reader:
 def __init__(self,p,magic):
  self.data=Path(p).read_bytes();req(self.data.startswith(magic),'raw magic');self.at=len(magic)
 def id(self):
  n,=struct.unpack_from('<I',self.data,self.at);self.at+=4;return n
 def vec(self):
  n,=struct.unpack_from('<Q',self.data,self.at);self.at+=8
  req(n<=1000000 and self.at+4*n<=len(self.data),'raw array bounds')
  result=memoryview(self.data)[self.at:self.at+4*n].cast('I');self.at+=4*n;return result
 def eof(self):req(self.at==len(self.data),'complete raw endpoint')
R=Path(P['raw_output']);inp=Reader(R/'inputs.bin',b'E047_IN1');base=Reader(R/'baseline.bin',b'E047_OUT1');cand=Reader(R/'candidate.bin',b'E047_OUT1');bi=Reader(R/'baseline-inputs.bin',b'E047_IM1');ci=Reader(R/'candidate-inputs.bin',b'E047_IM1')
req(base.data==cand.data,'full original/candidate files byte-identical');req(bi.data==ci.data,'actual device immutable-input images byte-identical')
output_words=0;immutable_words=0;guards=0
for c in cases:
 for reader in [inp,base,cand,bi,ci]:req(reader.id()==c['id'],'case order')
 req(list(inp.vec())==c['descriptor'],'declared descriptor')
 nh,na,p,role,count=c['hands'],c['actions'],c['p'],c['role'],c['count'];nn=na+8;stride=nh+5
 imm=[inp.vec() for _ in range(12)];seeds=[inp.vec() for _ in range(3)]
 lengths=[3,nn,nn,2*nn,nn,na+4,nn,6*max(nh,1)+7,2*nn,5+na*nh+17,nn,3]
 req([len(v) for v in imm]==lengths,'complete immutable geometry')
 req(list(imm[11])==c['discount_bits'],'production discount bits')
 req(imm[0][1]==2 and imm[1][2]==(1-p if role==2 else p) and imm[2][2]==na,'actual node/actor/arity')
 req(imm[3][4]==13 and imm[3][5]==0 and imm[4][2]==2 and imm[6][2]==3,'actual offsets')
 req(list(imm[5][2:2+na])==list(range(4,4+na)) and list(imm[10][4:4+na])==list(reversed(range(4,4+na))),'actual child/permuted slot coverage')
 req(list(imm[8][4:6])==([5,0] if role==1 else [0xffffffff,0xffffffff]),'actual lock path')
 req([len(v) for v in seeds]==[13+na*nh+17,13+na*nh+17,(nn+3)*stride+17],'mutable seed geometry')
 for br,ir in [(base,bi),(cand,ci)]:
  result=[br.vec() for _ in range(3)];post=[ir.vec() for _ in range(12)]
  req(all(a==b for a,b in zip(post,imm)),'full actual device inputs unchanged')
  req([len(v) for v in result]==[len(v) for v in seeds],'full output geometry')
  for kind,(v,seed) in enumerate(zip(result,seeds)):
   if count and (kind==2 or role==0):
    lo=2*stride if kind==2 else 13;size=nh if kind==2 else na*nh
   else:lo=0;size=0
   req(v[:lo]==seed[:lo] and v[lo+size:]==seed[lo+size:],'all nonowned/guard/child words unchanged')
   guards+=len(v)-size;output_words+=len(v)
  immutable_words+=sum(len(v) for v in post)
for r in [inp,base,cand,bi,ci]:r.eof()
summary=C['validated_summary'];req(summary['cases']==len(cases)==819 and summary['kernel_launches']==1638,'launch/case inventory')
req(output_words==summary['output_words_both_arms'],'full output word inventory');req(immutable_words==summary['immutable_words_both_arms'],'full actual immutable word inventory');req(guards==summary['guard_words_both_arms'],'all guard word inventory')
old.custody()
report={'id':'E047-kernel-control-r2','at':old.now(),'status':'pass_scoped_up_action_raw_equivalence','root_cross_check_only':True,'reporting_failure_sha256':old.sha(HERE/'execution/wrapper-failure.json'),'new_native_runs':0,'checks':checks,'cases':819,'kernel_launches':1638,'output_words_both_arms':output_words,'immutable_words_both_arms':immutable_words,'guard_words_both_arms':guards,'full_raw_files_equal':True,'actual_device_inputs_retained_both_arms':True,'raw_file_sha256':C['raw_file_sha256'],'protocol_sha256':old.sha(HERE/'protocol.json'),'corpus_sha256':old.sha(HERE/'corpus.json'),'complete_sha256':old.sha(HERE/'execution/complete-r2.json'),'audit_script_sha256':old.sha(HERE/'audit-r2.py'),'accepted162_main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False,'limits':'Finite declared corpus only, no universal NaN/layout or wide-address guarantee. Root decoder is not an external independent audit. Full solver accuracy and speed gates remain pending.'}
old.save(OUT/'report.json',report);print(json.dumps({k:report[k] for k in ['status','checks','cases','output_words_both_arms','immutable_words_both_arms','guard_words_both_arms']}));print(old.sha(OUT/'report.json'))
