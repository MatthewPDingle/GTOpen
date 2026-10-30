import sys,json,struct,array,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D163-down-action';P=h.read(H/'protocol.json');C=h.read(H/'execution/native-complete.json');O=H/'output';cases=h.read(H/'corpus.json');checks=0;guards=0;outwords=0;immwords=0;zerowitnesses=[0,0];nonfinite=0
def req(v,label):
 global checks
 assert v,label;checks+=1
for p,digest in P['input_sha256'].items():h.pin(p,digest)
for p,digest in C['raw_sha256'].items():h.pin(p,digest)
class Reader:
 def __init__(self,path,magic):self.f=path.open('rb');req(self.f.read(len(magic))==magic,'magic')
 def id(self,n):req(self.f.read(4)==struct.pack('<I',n),'record id')
 def words(self):
  b=self.f.read(8);req(len(b)==8,'length');n=struct.unpack('<Q',b)[0];req(n<1000000,'bounded vector');v=array.array('I');v.frombytes(self.f.read(n*4));req(len(v)==n,'whole vector');return v
 def close(self):req(self.f.read(1)==b'','complete endpoint');self.f.close()
inp=Reader(O/'inputs.bin',b'E091_IN1');base=Reader(O/'baseline.bin',b'E091_OUT1');cand=Reader(O/'candidate.bin',b'E091_OUT1');bi=Reader(O/'baseline-inputs.bin',b'E091_IM1');ci=Reader(O/'candidate-inputs.bin',b'E091_IM1')
def value(bits):return struct.unpack('<f',struct.pack('<I',bits))[0]
def add(a,b):
 try:return struct.unpack('<f',struct.pack('<f',a+b))[0]
 except OverflowError:return math.inf
for ident,c in enumerate(cases):
 for r in[inp,base,cand,bi,ci]:r.id(ident)
 meta=inp.words();actor=c['actor'];nh=c['nh'];other=nh+5 if nh else 5;ns=[nh,other]if actor==0 else [other,nh]
 req(list(meta)==[ns[0],ns[1],c['na'],c['block'],actor,c['lock_mode'],c['regret_mode'],c['reach_mode'],c['count'],1,2,13,7,2,c['na']+10],'frozen dimensions')
 immutable=[inp.words()for _ in range(12)];seed=[inp.words(),inp.words()];b=[base.words(),base.words()];d=[cand.words(),cand.words()];postb=[bi.words()for _ in range(12)];postc=[ci.words()for _ in range(12)]
 req(immutable==postb==postc,'every actual immutable word both arms');req(b==d,'all physical output words');immwords+=2*sum(map(len,immutable));outwords+=2*sum(map(len,b))
 for p in range(2):
  req(len(b[p])==len(seed[p])==(c['na']+10)*max(ns[p],1)+17,'whole output geometry')
  for i,v in enumerate(b[p]):
   live=c['count']!=0 and p==actor and nh>0 and 5<=i//nh<5+c['na']
   if not live:req(v==seed[p][i],'every guard word');guards+=2
   elif v&0x7f800000==0x7f800000:nonfinite+=2
 if c['count']and not c['lock_mode']:
  regs=immutable[8+actor];src=2 if actor==0 else 3
  for i in range(nh):
   pr=seed[actor][src*nh+i]
   if pr&0x7fffffff:continue
   total=0.
   for a in range(c['na']):
    r=value(regs[13+a*nh+i]);total=add(total,r if r>0 else 0.)
   if math.isfinite(total):
    for a in range(c['na']):req(b[actor][(5+a)*nh+i]==pr,'independent signed-zero witness');zerowitnesses[pr>>31]+=2
for r in[inp,base,cand,bi,ci]:r.close()
last=C['last_marker'];req(last['cases']==len(cases)and last['kernel_launches']==2*len(cases),'case/launch inventory');req(last['output_words_both_arms']==outwords and last['immutable_words_both_arms']==immwords and last['guard_words_both_arms']==guards,'full word inventory');req(all(n>0 for n in zerowitnesses),'both zero signs witnessed');req(nonfinite>0,'nonfinite outputs covered')
h.custody();D=ROOT/'comparisons/D163-down-action';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D163-down-action','at':h.now(),'status':'pass_scoped_down_action_raw_equivalence','protocol_sha256':h.sha(H/'protocol.json'),'checks':checks,'cases':len(cases),'kernel_launches':2*len(cases),'output_words_both_arms':outwords,'immutable_words_both_arms':immwords,'guard_words_both_arms':guards,'positive_negative_zero_witness_words':zerowitnesses,'nonfinite_output_words_both_arms':nonfinite,'all_full_actual_inputs_and_outputs_exact':True,'raw_sha256':C['raw_sha256'],'performance_measurement':False,'candidate_accepted':False,'source_main_live_PTX_custody_pass':True,'scope':'Finite declared matrix only. All physical outputs and twelve actual immutable input vectors compared in full, with whole guards. Independent CPU ordered-f32 classification verifies both signed-zero output invariants for finite sums. No universal NaN/layout, trained-game, production incidence, cost/capacity or speed claim.'})
print(json.dumps({'status':'pass','cases':len(cases),'checks':checks,'zero_witnesses':zerowitnesses,'nonfinite_outputs':nonfinite}),flush=True)
