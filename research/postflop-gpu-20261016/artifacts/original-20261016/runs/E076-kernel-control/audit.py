"""Decode every physical image, guard and logical output for disjoint/in-place rows."""
from pathlib import Path
import json,struct,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
P=old.read(H/'protocol.json');C=old.read(H/'execution/complete.json');cases=old.read(H/'corpus.json')['cases'];checks=0
for p,h in P['input_sha256'].items():old.pin(p,h)
for p,h in C['raw_file_sha256'].items():old.pin(p,h)
def req(v,label):
 global checks
 assert v,label;checks+=1
class Reader:
 def __init__(self,p,magic):self.data=Path(p).read_bytes();req(self.data.startswith(magic),'framing');self.at=len(magic)
 def id(self):n,=struct.unpack_from('<I',self.data,self.at);self.at+=4;return n
 def vec(self):
  n,=struct.unpack_from('<Q',self.data,self.at);self.at+=8;req(n<=1000000 and self.at+4*n<=len(self.data),'bounded complete array');v=memoryview(self.data)[self.at:self.at+4*n].cast('I');self.at+=4*n;return v
 def eof(self):req(self.at==len(self.data),'full endpoint')
raw=Path(P['raw_output']);readers=[Reader(raw/n,m)for n,m in [('inputs.bin',b'E076_IN1'),('baseline.bin',b'E076_OUT1'),('candidate.bin',b'E076_OUT1'),('baseline-inputs.bin',b'E076_IM1'),('candidate-inputs.bin',b'E076_IM1')]]
inp,base,cand,bi,ci=readers;output_words=immutable_words=guards=aliases=0
for case in cases:
 for r in readers:req(r.id()==case['id'],'fixed case order')
 req(list(inp.vec())==case['descriptor'],'exact case descriptor')
 nh,na,p,role,count=[case[k]for k in ['hands','actions','p','role','count']];nn=na+8;stride=nh+5
 images=[];seeds=[]
 for arm in range(2):images.append([inp.vec()for _ in range(12)]);seeds.append([inp.vec()for _ in range(3)])
 for arm,br,ir in [(0,base,bi),(1,cand,ci)]:
  imm=images[arm];seed=seeds[arm]
  req([len(x)for x in imm]==[3,nn,nn,2*nn,nn,na+4,nn,6*max(nh,1)+7,2*nn,5+na*nh+17,nn,3],'immutable geometry')
  req(list(imm[11])==case['discount_bits'],'production discount bits')
  req(imm[0][1]==2 and imm[1][2]==(1-p if role==2 else p)and imm[2][2]==na,'node/actor/arity')
  req(imm[3][4]==13 and imm[3][5]==0 and imm[4][2]==2 and imm[6][2]==3,'node offsets/reach')
  req(list(imm[8][4:6])==([5,0]if role==1 else[0xffffffff,0xffffffff]),'lock path')
  req(list(imm[5][2:2+na])==list(range(4,4+na)),'child indices')
  expected_slots=list(range(nn));expected_slots[4:4+na]=list(reversed(range(4,4+na)))
  if arm==1 and na==1:expected_slots[4]=2
  req(list(imm[10])==expected_slots,'only sole child may alias parent row')
  req([len(x)for x in seed]==[13+na*nh+17,13+na*nh+17,(nn+3)*stride+17],'seed geometry')
  result=[br.vec()for _ in range(3)];post=[ir.vec()for _ in range(12)]
  req(all(x==y for x,y in zip(imm,post)),'every actual immutable device word')
  req([len(x)for x in result]==[len(x)for x in seed],'full output lengths')
  for kind,(v,s)in enumerate(zip(result,seed)):
   lo=2*stride if kind==2 else 13;size=(nh if kind==2 else na*nh)if count and(kind==2 or role==0)else 0
   req(v[:lo]==s[:lo]and v[lo+size:]==s[lo+size:],'all nonowned and guard words unchanged')
   output_words+=len(v);guards+=len(v)-size
  immutable_words+=sum(len(x)for x in post)
  if arm==0:before=result
  else:
   req(all(x==y for x,y in zip(before[:2],result[:2])),'whole regret/strategy arrays bitwise exact')
   if count:req(before[2][2*stride:2*stride+nh]==result[2][2*stride:2*stride+nh],'whole logical parent CFV output bitwise exact')
   expected=list(seed[2])
   if count:expected[2*stride:2*stride+nh]=before[2][2*stride:2*stride+nh]
   req(list(result[2])==expected,'complete expected physical candidate CFV image')
 req(all(images[0][i]==images[1][i]for i in range(12)if i!=10),'all other arm metadata equal')
 req(seeds[0][0]==seeds[1][0]and seeds[0][1]==seeds[1][1],'identical mutable arena seeds')
 expected=list(seeds[0][2])
 if na==1:
  expected[2*stride:3*stride]=seeds[0][2][4*stride:5*stride];aliases+=1
 req(list(seeds[1][2])==expected,'candidate seed changes only by own child-row copy')
for reader in readers:reader.eof()
summary=C['raw_marker_summary'];req(summary['cases']==len(cases)==819 and summary['kernel_launches']==1638,'exact application launch inventory')
req((output_words,immutable_words,guards)==(summary['output_words_both_arms'],summary['immutable_words_both_arms'],summary['guard_words_both_arms']),'every raw word counted')
markers=[json.loads(x.split('E076_UNIT ',1)[1])for x in (H/'execution/probe.stdout.log').read_text(encoding='utf-8').splitlines()if 'E076_UNIT 'in x];req(len(markers)==820,'marker inventory')
for case,marker in zip(cases,markers[:-1]):
 req(marker['id']==case['id']and marker['baseline_parent_child_rows_disjoint']and marker['candidate_parent_child_alias']==(case['actions']==1),'per-case row contract')
 witnesses=marker['disjoint_device_ranges'];req([x['arm']for x in witnesses]==['baseline','candidate'],'both actual device witnesses')
 nh=case['hands'];na=case['actions'];stride=nh+5;nn=na+8
 lengths=[(13+na*nh+17)*4]*2+[((nn+3)*stride+17)*4]
 for witness in witnesses:
  regions=witness['regions'];req(len(regions)==3 and[x[1]for x in regions]==lengths,'physical mutable extents')
  req(all(isinstance(p,int)and p>0 and p+n<2**64 for p,n in regions),'valid owned pointers')
  req(all(regions[i][0]+regions[i][1]<=regions[j][0]or regions[j][0]+regions[j][1]<=regions[i][0]for i in range(3)for j in range(i+1,3)),'regret/strategy/CFV allocations disjoint')
old.custody();OUT=R/'comparisons/E076-kernel-control-root-check';assert not OUT.exists();OUT.mkdir()
report={'id':'E076-kernel-control','at':old.now(),'status':'pass_scoped_in_place_CFV_raw_equivalence','root_cross_check_only':True,'checks':checks,'cases':819,'alias_cases':aliases,'kernel_launches':1638,'output_words_both_arms':output_words,'immutable_words_both_arms':immutable_words,'guard_words_both_arms':guards,'logical_parent_and_full_regret_strategy_outputs_exact':True,'full_physical_images_and_actual_inputs_match_own_expected':True,'raw_file_sha256':C['raw_file_sha256'],'protocol_sha256':old.sha(H/'protocol.json'),'source_main_live_PTX_custody_pass':True,'performance_measured':False,'candidate_accepted':False,'limits':'Fixed corpus and root decoder only. Physical layouts intentionally differ; complete expected per-arm buffers are validated. Not universal NaN/alias proof or external independent audit. Integrated whole solver/state/graph/material and all performance gates remain.'};old.save(OUT/'report.json',report);print(json.dumps({k:report[k]for k in ['status','checks','cases','alias_cases','output_words_both_arms','immutable_words_both_arms','guard_words_both_arms']}),flush=True)
