"""Root full raw decoder for the fixed E048 mask/card chance comparison."""
import json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
P=old.read(HERE/'protocol.json');C=old.read(HERE/'execution/complete.json');corpus=old.read(HERE/'corpus.json');cases=corpus['cases'];checks=0
def req(v,m):
 global checks
 assert v,m;checks+=1
for p,h in P['input_sha256'].items():old.pin(p,h)
for p,h in C['raw_file_sha256'].items():old.pin(p,h)
req(sys.byteorder=='little','native word decoding')
class Reader:
 def __init__(self,p,magic):self.data=Path(p).read_bytes();req(self.data.startswith(magic),'raw magic');self.at=len(magic)
 def u32(self):v,=struct.unpack_from('<I',self.data,self.at);self.at+=4;return v
 def vec(self):
  n,=struct.unpack_from('<Q',self.data,self.at);self.at+=8;req(n<=corpus['max_case_array_words'] and self.at+4*n<=len(self.data),'full array bounds');v=memoryview(self.data)[self.at:self.at+4*n].cast('I');self.at+=4*n;return v
 def vecs(self):
  n=self.u32();req(n<=20,'vector-list bounds');return [self.vec() for _ in range(n)]
 def eof(self):req(self.at==len(self.data),'full raw endpoint')
rawdir=Path(P['raw_output']);inp=Reader(rawdir/'inputs.bin',b'E048_IN1');base=Reader(rawdir/'baseline.bin',b'E048_OUT1');cand=Reader(rawdir/'candidate.bin',b'E048_OUT1')
req(base.data==cand.data,'entire GPU output and immutable-image files equal')
output_words=0;immutable_words=0;guard_words=0;cpu_down_relations=0;full_up_cards=set();families={0:0,1:0}
def card_value(j,pattern,salt):return j%52 if pattern==0 else [0,25,51][j%3] if pattern==1 else (j*17+13)%52 if pattern==2 else (j+salt)%52
def masks(mask,a,b,n):
 req(len(a)==len(b)==max(n,1)+3 and len(mask)==2*len(a),'complete card/mask arrays')
 for i in range(len(a)):
  req(0<=a[i]<b[i]<52,'canonical card IDs');req(mask[2*i]|(mask[2*i+1]<<32)==(1<<a[i])|(1<<b[i]),'exact canonical mask relation')
 if n==1326:req(len(set(zip(a[:n],b[:n])))==1326,'full canonical hand coverage')
def unowned(v,seed,ranges):
 global guard_words
 cursor=0
 for lo,hi in sorted(ranges):
  req(cursor<=lo<=hi<=len(v),'disjoint bounded owned intervals');req(v[cursor:lo]==seed[cursor:lo],'complete unowned gap unchanged');guard_words+=lo-cursor;cursor=hi
 req(v[cursor:]==seed[cursor:],'complete unowned suffix unchanged');guard_words+=len(v)-cursor
for case in cases:
 req(inp.u32()==case['id'],'input case order');d=list(inp.vec());req(d==case['descriptor'],'descriptor exact');im=inp.vecs();seeds=inp.vecs()
 f,n0,n1,threads,active,mode,perm,width,pattern,salt=d;families[f]+=1
 req(f in [0,1] and threads in [1,32,64,128,256] and active in [0,1] and mode in [0,1,2],'declared scalar domain')
 if f==0:
  req(len(im)==11 and len(seeds)==2,'down complete input inventory')
  pa,ch,ca,r0,r1,m0,m1,a0,b0,a1,b1=im
  req([len(pa),len(ch),len(ca)]==[width+4]*3 and len(r0)==len(r1)==width+10,'down metadata geometry')
  req(r0[2]==2 and r1[2]==3,'down parent rows');masks(m0,a0,b0,n0);masks(m1,a1,b1,n1)
  for j in range(width):req(pa[j+1]==2 and ch[j+1]==j+4 and ca[j+1]==card_value(j,pattern,salt) and r0[j+4]==j+4 and r1[j+4]==6+width-1-j,'all down edges/slots')
  req([len(x) for x in seeds]==[(width+12)*n0+17,(width+12)*n1+17],'complete down output seed geometry')
 else:
  req(len(im)==12 and len(seeds)==1,'up complete input inventory')
  nodes,cs,cc,card,child,cp,inv,mask,a,b,hp,slot=im
  req(list(nodes)==[0xdeadbeef,2,0xdeadbeef] and cs[2]==3 and cc[2]==width and slot[2]==2,'up actual root/span')
  req(len(cs)==len(cc)==len(inv)==len(slot)==width+10 and len(card)==len(child)==len(cp)==width+6,'up metadata geometry');masks(mask,a,b,n0)
  req(len(hp)==4*n0+7,'all permutation words present')
  if n0:req(all(hp[k*n0+i]==(i+k*17)%n0 for k in range(4) for i in range(n0)),'all identity/nonidentity mappings')
  for j in range(width):req(card[j+3]==card_value(j,pattern,salt) and child[j+3]==4+j and cp[j+3]==(0 if perm==0 else j%4) and slot[4+j]==4+width-1-j,'all up cards/children/permutations/slots')
  req(len(seeds[0])==(width+12)*(n0+5)+17,'complete up output seed geometry')
  if case['group']=='up_each_card_canonical':req(width==1 and n0==1326 and mode==0 and perm==0 and active==1,'isolated canonical card matrix');full_up_cards.add(card[3])
 for arm in [base,cand]:
  req(arm.u32()==case['id'],'actual GPU image case order');post=arm.vecs();out=arm.vecs()
  req(len(post)==len(im) and all(a==b for a,b in zip(post,im)),'every actual device immutable word preserved')
  req([len(x) for x in out]==[len(x) for x in seeds],'full output geometry')
  if f==0:
   for p,nh in [(0,n0),(1,n1)]:
    rs=im[3+p];ranges=[(rs[im[1][j+1]]*nh,rs[im[1][j+1]]*nh+nh) for j in range(width)] if active and nh else [];unowned(out[p],seeds[p],ranges)
    if mode==0 and active:
     mask=im[5+p];parent=rs[2]*nh
     for j in range(width):
      card=im[2][j+1];start=rs[im[1][j+1]]*nh
      for i in range(nh):
       blocked=(mask[2*i]|(mask[2*i+1]<<32))&(1<<card);expected=0 if blocked else seeds[p][parent+i]
       req(out[p][start+i]==expected,'independent positive-finite down zero/copy relation');cpu_down_relations+=1
  else:
   lo=2*(n0+5);unowned(out[0],seeds[0],[(lo,lo+n0)] if active and n0 else [])
  output_words+=sum(len(x) for x in out);immutable_words+=sum(len(x) for x in post)
for reader in [inp,base,cand]:reader.eof()
end=C['raw_marker_summary'];req(end['cases']==len(cases) and end['kernel_launches']==2*len(cases),'actual dynamic case/launch counts')
req(families=={int(k):v for k,v in corpus['family_case_counts'].items()},'family inventory')
req(full_up_cards==set(range(52)),'every individual dealt card/all1326 hands covered on GPU')
req(output_words==end['output_words_both_arms'] and immutable_words==end['immutable_words_both_arms'] and guard_words==end['guard_words_both_arms'],'full word inventories recomputed')
old.custody();OUT=old.ROOT/'comparisons/E048-kernel-control';OUT.mkdir()
report={'id':'E048-kernel-control','at':old.now(),'status':'pass_scoped_chance_raw_equivalence','root_cross_check_only':True,'checks':checks,'cases':len(cases),'kernel_launches':2*len(cases),'family_cases':families,'output_words_both_arms':output_words,'actual_immutable_words_both_arms':immutable_words,'guard_words_both_arms':guard_words,'independent_cpu_down_relations_both_arms':cpu_down_relations,'individual_up_dealt_cards_full_canonical_hands':52,'full_raw_files_equal':True,'actual_immutable_images_preserved':True,'raw_file_sha256':C['raw_file_sha256'],'protocol_sha256':old.sha(HERE/'protocol.json'),'corpus_sha256':old.sha(HERE/'corpus.json'),'complete_sha256':old.sha(HERE/'execution/complete.json'),'audit_script_sha256':old.sha(HERE/'audit.py'),'accepted162_main_live_ptx_unchanged':True,'performance_measured':False,'candidate_accepted':False,'limits':'Finite canonical card/float corpus and small physical offsets; not malformed custom HandInfo or >2^32 span equivalence. Root decoder is not external independent review. No full solver or speed claim.'}
old.save(OUT/'report.json',report);print(json.dumps({k:report[k] for k in ['status','checks','cases','kernel_launches','output_words_both_arms','actual_immutable_words_both_arms','guard_words_both_arms','independent_cpu_down_relations_both_arms']}));print(old.sha(OUT/'report.json'),flush=True)
