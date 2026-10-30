import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=Path(__file__).resolve().parent;O=H/'execution';h.custody();P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
path=O/'host-hand-words.bin';raw=path.read_bytes();magic=b'E121_HAND_WORDS_V1\n';assert raw.startswith(magic);offset=len(magic);count,=struct.unpack_from('<Q',raw,offset);offset+=8;assert count==1763580;assert len(raw)==offset+count*16;checks=0;records=0
def row(a,b,s):
 global checks,records,offset
 aa,bb,ss,w=struct.unpack_from('<IIII',raw,offset);offset+=16;records+=1
 assert(aa,bb,ss)==(a,b,s);assert 0<=w<0x800000;assert w&63==a;assert(w>>6)&63==b;assert(0xffffffff if w>>12==2047 else w>>12)==s;checks+=5
for a in range(52):
 for b in range(a+1,52):
  for same in range(1326):row(a,b,same)
  row(a,b,0xffffffff)
cards=[(a,b)for a in range(52)for b in range(a+1,52)]
for mode in range(3):
 for i,(a,b)in enumerate(cards):row(a,b,i if mode==0 else(1325-i if mode==1 else(0xffffffff if i%7==0 else i*73%1326)))
assert records==count and offset==len(raw);h.save(H/'host-encode-report.json',{'id':'E121-host-encoding','at':h.now(),'status':'pass_entire_compiled_legal_tuple_domain_and_three_mixed_vectors','records':records,'checks':checks,'legal_tuples':1759602,'mixed_records':3978,'raw_path':str(path),'raw_bytes':len(raw),'raw_sha256':hashlib.sha256(raw).hexdigest(),'host_function_sha256':h.sha(H/'host-encode.rs'),'complete_encoding_decoded_without_ignored_words':True,'GPU_or_FP_results':0,'scope':'Actual candidate pureRusthelper compiled in resourceprobe, whole52choose2cardpairs x1326matchingindices+sentinel,3heterogeneous1326handvectors andallrawwords. Sourcecallsitearguments/lifetimes and integratedGPUencoding/numerical behavior remainunproven. No performance/materialclaim.'});h.custody();print('Host hand-word full-domain raw decode pass:',records,'records',checks,'checks',flush=True)
