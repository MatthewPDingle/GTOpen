"""Root full-word decoder for current E068 up_chance raw evidence."""
import json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'accepted-E051'));import common_e051 as old
ROOT=old.ROOT;K=ROOT/'runs/E068-kernel-control';P=old.read(K/'protocol.json');C=old.read(K/'execution/complete.json');corpus=old.read(K/'corpus.json');cases=corpus['cases'];checks=0
old.custody();assert not (ROOT/'gpu-run.lock').exists()
def req(v,m):
 global checks
 assert v,m;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h)
for p,h in C['raw_file_sha256'].items():old.pin(p,h)
for label in ['rustc','probe']:
 e=old.read(K/'execution'/(label+'.exit.json'));req(e['returncode']==0 and e['error'] is e['cleanup'] is None,'terminal child')
req(sys.byteorder=='little' and len(cases)==1688,'declared complete corpus')
for v in ['baseline','candidate']:req((K/(v+'.ptx')).read_bytes()==(ROOT/'runs/E068-resource/execution'/(v+'-compute_120.ptx')).read_bytes(),'same resource/raw PTX')
class Reader:
 def __init__(self,p,magic):self.data=Path(p).read_bytes();req(self.data.startswith(magic),'raw magic');self.at=len(magic)
 def u32(self):req(self.at+4<=len(self.data),'u32 bounds');v,=struct.unpack_from('<I',self.data,self.at);self.at+=4;return v
 def vec(self):
  req(self.at+8<=len(self.data),'length bounds');n,=struct.unpack_from('<Q',self.data,self.at);self.at+=8;req(n<=corpus['max_case_array_words'] and self.at+4*n<=len(self.data),'full vector bounds');v=memoryview(self.data)[self.at:self.at+4*n].cast('I');self.at+=4*n;return v
 def vecs(self):
  n=self.u32();req(n<=20,'vector count bounds');return [self.vec() for _ in range(n)]
 def eof(self):req(self.at==len(self.data),'complete raw endpoint')
rawdir=Path(P['raw_output']);inp=Reader(rawdir/'inputs.bin',b'E068_IN1');base=Reader(rawdir/'baseline.bin',b'E068_OUT1');cand=Reader(rawdir/'candidate.bin',b'E068_OUT1');req(base.data==cand.data,'entire output and actualinput image files equal')
markers=[json.loads(x.split('E068_CONTROL ',1)[1]) for x in (K/'execution/probe.stdout.log').read_text().splitlines() if x.startswith('E068_CONTROL ')];req(len(markers)==1689,'all markers retained')
output_words=0;immutable_words=0;guard_words=0;factored_read_addresses=0;permutation_words=0;cpu_card_relations=0;cpu_zero_relations=0;cards=set();allblocked=0;allunblocked=0

def card_value(j,pattern,salt):return j%52 if pattern==0 else [0,25,51][j%3] if pattern==1 else (j*17+13)%52 if pattern==2 else 0 if pattern==4 else 51 if pattern==5 else (j+salt)%52

def unowned(v,seed,lo,hi):
 global guard_words
 req(0<=lo<=hi<=len(v),'owned range bounded');req(v[:lo]==seed[:lo] and v[hi:]==seed[hi:],'all unowned full gaps unchanged');guard_words+=len(v)-(hi-lo)

def float_from_bits(word):return struct.unpack('<f',struct.pack('<I',word))[0]
def float_bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]

for case in cases:
 id=case['id'];req(inp.u32()==id,'input order');d=list(inp.vec());req(d==case['descriptor'],'descriptor exact');im=inp.vecs();seeds=inp.vecs();req(len(im)==12 and len(seeds)==1,'complete declared inventory')
 f,n,pad,threads,active,mode,perm,width,pattern,salt=d;stride=n+pad;nodes,cs,cc,card,child,cp,inv,mask,a,b,hp,slot=im
 req(f==1 and threads in [1,32,64,128,256] and active in [0,1] and mode in [0,1,2] and n<=1326 and width<=64 and stride>=n,'scalar domain')
 req(list(nodes)==[0xdeadbeef,2,0xdeadbeef] and cs[2]==3 and cc[2]==width and slot[2]==2 and inv[2]==case['inv_bits'],'actual span/output/inverse metadata')
 req(len(cs)==len(cc)==len(inv)==len(slot)==width+10 and len(card)==len(child)==len(cp)==width+6,'metadata lengths')
 req(len(a)==len(b)==max(n,1)+3 and len(mask)==2*len(a),'complete card/mask geometry')
 for i in range(len(a)):
  req(0<=a[i]<b[i]<52,'valid two-card mask');req(mask[2*i]|(mask[2*i+1]<<32)==(1<<a[i])|(1<<b[i]),'canonical bitmask relation')
  if case['mask_style']==1:req(a[i]==0 and b[i]==1+i%51,'allblocked hand definition')
  elif case['mask_style']==2:req(a[i]==0 and b[i]==1,'allunblocked hand definition')
 if n==1326 and case['mask_style']==0:req(len(set(zip(a[:n],b[:n])))==1326,'full unique canonical hand coverage')
 req(len(hp)==4*n+7,'all permutation entries present')
 if n:
  for k in range(4):
   for i in range(n):req(hp[k*n+i]==(i+k*17)%n and hp[k*n+i]<n,'total actual permutation including blocked hands');permutation_words+=1
 req(len(seeds[0])==(width+12)*stride+17,'fully initialized CFVseed geometry')
 lo=2*stride;hi=lo+n
 for j in range(width):
  t=j+3;expected_card=card_value(j,pattern,salt);expected_child=j+4;expected_perm=0 if perm==0 else j%4
  req(card[t]==expected_card<52 and child[t]==expected_child and cp[t]==expected_perm and slot[child[t]]==4+width-1-j,'every chance/card/child/permutation/row')
  rowlo=slot[child[t]]*stride;rowhi=rowlo+n;req(rowhi<=len(seeds[0]) and (not n or rowhi<=lo or rowlo>=hi),'all child reads disjoint/bounded even when blocked')
  factored_read_addresses+=n
 record=markers[id];req(record['stage']=='case' and record['id']==id and record['descriptor']==d and record['inv_bits']==case['inv_bits'] and record['mask_style']==case['mask_style'] and record['read_addresses_prechecked']==width*n,'native actual-address precheck accounted')
 req(record['full_outputs_exact'] and record['actual_immutable_inputs_exact'] and record['guards_exact'],'native result markers')
 if case['group']=='each_card_full_canonical':req(n==1326 and width==1 and mode==0 and perm==0 and active and case['mask_style']==0,'canonical card matrix contract');cards.add(card[3])
 if case['mask_style']==1:allblocked+=1;req(pattern==4 and all((mask[2*i]|(mask[2*i+1]<<32))&1 for i in range(n)),'all hands truly blocked')
 if case['mask_style']==2:allunblocked+=1;req(pattern==5 and all(((mask[2*i]|(mask[2*i+1]<<32))&(1<<51))==0 for i in range(n)),'all hands truly unblocked')
 for arm in [base,cand]:
  req(arm.u32()==id,'actual GPU image order');post=arm.vecs();out=arm.vecs();req(len(post)==12 and all(x==y for x,y in zip(post,im)),'every actual immutable word');req(len(out)==1 and len(out[0])==len(seeds[0]),'full CFVoutput retained')
  unowned(out[0],seeds[0],lo,hi if active else lo)
  if active and (case['mask_style']==1 or width==0) and ((case['inv_bits']>>23)&255)!=255:
   expected_zero=case['inv_bits']&0x80000000
   for i in range(n):req(out[0][lo+i]==expected_zero,'independent all-skipped/empty sum signedzero relation');cpu_zero_relations+=1
  if case['group']=='each_card_full_canonical':
   for i in range(n):
    blocked=(mask[2*i]|(mask[2*i+1]<<32))&(1<<card[3]);expected=0 if blocked else float_bits(float_from_bits(seeds[0][slot[child[3]]*stride+i])*float_from_bits(inv[2]));req(out[0][lo+i]==expected,'independent onecard positive-finite IEEE product/zero relation');cpu_card_relations+=1
  output_words+=len(out[0]);immutable_words+=sum(map(len,post))
for reader in [inp,base,cand]:reader.eof()
end=C['raw_marker_summary'];req(end['cases']==1688 and end['kernel_launches']==3376,'fixed native counts');req(cards==set(range(52)) and allblocked==allunblocked==240,'all declared special families')
req(output_words==end['output_words_both_arms']==35904112 and immutable_words==end['immutable_words_both_arms']==9083648 and guard_words==end['guard_words_both_arms']==34875264,'recomputed complete word counts')
req(factored_read_addresses==end['all_ignored_and_used_read_addresses_prechecked']==10938464,'all actual used/ignored address prechecks retained')
OUT=ROOT/'comparisons/E068-kernel-control-root-check';assert not OUT.exists();OUT.mkdir()
old.save(OUT/'report.json',{'id':OUT.name,'at':old.now(),'status':'pass_scoped_up_chance_full_raw_equivalence','checks':checks,'cases':1688,'kernel_launches':3376,'full_output_words_both_arms':output_words,'full_actual_device_input_words_both_arms':immutable_words,'guard_word_checks_both_arms':guard_words,'all_full_outputs_inputs_guards_exact':True,'resource_and_raw_ptx_byte_identical':True,'native_concretely_prechecked_read_addresses':factored_read_addresses,'root_factored_read_address_coverage':factored_read_addresses,'root_actual_permutation_words':permutation_words,'independent_cpu_canonical_card_relations_both_arms':cpu_card_relations,'independent_cpu_allblocked_or_empty_signedzero_relations_both_arms':cpu_zero_relations,'all52cards_full1326hands':True,'allblocked_cases':240,'allunblocked_cases':240,'raw_file_sha256':C['raw_file_sha256'],'raw_total_bytes':sum(Path(p).stat().st_size for p in C['raw_file_sha256']),'corpus_sha256':old.sha(K/'corpus.json'),'source_activated':False,'performance_measured':False,'candidate_accepted':False,'limits':'Root fullraw parser independently checks actual metadata, total mappings, bound/disjoint child rows, every raw output/input/guard and canonical finite product/signedzero relations. Address coverage is factored by table totality/rowgeometry; native enumerated eachactual address beforelaunch. Not external independent review or fullsolver/graphs/material/holdout/speed/otherGPU proof. Syntheticduplicatehands/width>52 remain raw stress only.'})
old.save(K/'execution/terminal.json',{'at':old.now(),'native_child_receipt_sha256':old.sha(K/'execution/probe.exit.json'),'returncode':0,'all_children_terminal':True,'complete_sha256':old.sha(K/'execution/complete.json'),'root_report_sha256':old.sha(OUT/'report.json'),'no_native_reexecution':True})
old.custody();print(json.dumps({'status':'pass_full_raw_replay','checks':checks,'outputs':output_words,'inputs':immutable_words,'guards':guard_words,'address_coverage':factored_read_addresses,'cpu_card_relations':cpu_card_relations,'cpu_zero_relations':cpu_zero_relations,'report_sha256':old.sha(OUT/'report.json')}),flush=True)