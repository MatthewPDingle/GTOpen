import array,hashlib,json,math,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2 and sys.byteorder=='little';G=ROOT/'runs/E099-direct-controls';P=h.read(G/'protocol.json');h.pin(G/'protocol.json',sys.argv[1]);h.custody();checks=0
for p,digest in P['input_sha256'].items():h.pin(p,digest)
def req(v,msg):
 global checks
 assert v,msg;checks+=1
class Reader:
 def __init__(self,p,magic):self.p=p;self.f=p.open('rb');self.sha=hashlib.sha256();req(self.read(len(magic))==magic,'magic')
 def read(self,n):v=self.f.read(n);req(len(v)==n,'full read');self.sha.update(v);return v
 def id(self,n):req(self.read(4)==struct.pack('<I',n),'record id')
 def words(self):
  n,=struct.unpack('<Q',self.read(8));req(n<1000000,'bounded vector');v=array.array('I');v.frombytes(self.read(n*4));return v
 def close(self):req(not self.f.read(1),'complete endpoint');self.f.close();return {'bytes':self.p.stat().st_size,'sha256':self.sha.hexdigest()}
def fl(b):return struct.unpack('<f',struct.pack('<I',b))[0]
def add(a,b):
 try:return struct.unpack('<f',struct.pack('<f',a+b))[0]
 except OverflowError:return math.inf
reports={};all_hashes={};totalout=totalimm=totalguard=totalcases=0
for name in P['native_sequence']:
 u=P['units'][name];H=Path(u['folder']);O=H/'output';corpus=h.read(H/'corpus.json');cases=corpus['cases'] if name=='up' else corpus;C=h.read(G/'execution'/(name+'-complete.json'));summary=C['last_marker'];prefix='E085' if name=='up' else 'E091';inp=Reader(O/'inputs.bin',(prefix+'_IN1').encode());b=Reader(O/'baseline.bin',(prefix+'_OUT1').encode());c=Reader(O/'candidate.bin',(prefix+'_OUT1').encode());bi=Reader(O/'baseline-inputs.bin',(prefix+'_IM1').encode());ci=Reader(O/'candidate-inputs.bin',(prefix+'_IM1').encode());readers=[inp,b,c,bi,ci];output=immutable=guard=eligible=0;zero=[0,0];nonfinite=0
 markers=[json.loads(x.split(u['marker']+' ',1)[1]) for x in (G/'execution'/(name+'-native.stdout.log')).read_text().splitlines() if u['marker']+' ' in x];req(len(markers)==len(cases)+1,'all native markers')
 for ident,case in enumerate(cases):
  for r in readers:r.id(ident)
  meta=list(inp.words());imm=[inp.words() for _ in range(12)];seeds=[inp.words() for _ in range(3 if name=='up' else 2)];br=[b.words() for _ in seeds];cr=[c.words() for _ in seeds];bp=[bi.words() for _ in range(12)];cp=[ci.words() for _ in range(12)];req(br==cr,'all output words');req(imm==bp==cp,'all actual immutable words');req(all(len(a)==len(d) for a,d in zip(br,seeds)),'output extent');immutable+=2*sum(map(len,imm));output+=2*sum(map(len,br));marker=markers[ident];req(marker['stage']=='case' and marker['id']==ident,'case marker order')
  if name=='up':
   req(meta==case['descriptor'],'frozen up descriptor');nh,na,block,p,role,algo,t,mode,count,stride,start,parent,off,loff=meta;nn=na+8;req(list(imm[11])==case['discount_bits'],'actual production discount bits');req(imm[0][1]==parent and imm[1][parent]==(1-p if role==2 else p) and imm[2][parent]==na,'actual node actor arity');req(imm[3][2*parent]==off and imm[3][2*parent+1]==0 and imm[4][parent]==2 and imm[6][parent]==3,'actual row ownership');req(list(imm[8][2*parent:2*parent+2])==([loff,0] if role==1 else [0xffffffff,0xffffffff]),'actual lock offset');req([len(v) for v in seeds]==[off+na*nh+17,off+na*nh+17,(nn+3)*stride+17],'entire mutable shapes');req([len(v) for v in imm]==[3,nn,nn,2*nn,nn,na+4,nn,6*max(nh,1)+7,2*nn,loff+na*nh+17,nn,3],'entire immutable shapes');req(imm[10][parent]==parent and all(imm[10][parent]!=imm[10][child] for child in imm[5][2:2+na]),'parent/child CFV disjoint')
   live=bool(count and nh and na==2 and (nh|stride)%2==0 and off%2==0 and(role!=1 or loff%2==0));req(live==case['paired_active_expected'] and marker['paired_active_expected']==live,'paired branch geometry');eligible+=live
   owned=[(off,na*nh) if count and role==0 else (0,0),(off,na*nh) if count and role==0 else (0,0),(parent*stride,nh) if count else(0,0)]
   expectedbytes=[len(seeds[0])*4,len(seeds[1])*4,len(seeds[2])*4,len(imm[7])*4,len(imm[9])*4];ranges=marker['disjoint_device_ranges']
  else:
   nh=case['nh'];na=case['na'];actor=case['actor'];layout=case['layout'];other=(nh+5 if nh else 5) if layout==0 else nh+5 if layout==4 else nh+6;ns=[nh,other] if actor==0 else[other,nh]
   if case['reuse_zero']:ns[1]=0
   active=ns[actor];off=13 if layout in [0,2] else 14;loff=7 if layout in [0,3] else 8;nn=na+9;rows=na+10;count=case['count'];req(meta==[ns[0],ns[1],na,case['block'],actor,case['lock_mode'],case['regret_mode'],case['reach_mode'],count,1,2,off,loff,2,rows],'frozen down descriptor');req(imm[0][1]==2 and imm[1][2]==actor and imm[2][2]==na,'down actor arity');req(imm[3][4]==off and imm[3][5]==0 and imm[4][2]==2 and imm[6][2]==2 and imm[7][2]==3,'down actual offsets');req(list(imm[10][4:6])==([loff,0] if case['lock_mode'] else [0xffffffff,0xffffffff]),'down lock path');req([len(v) for v in seeds]==[rows*max(n,1)+17 for n in ns],'whole down mutable shapes');req([len(v) for v in imm]==[3,nn,nn,2*nn,nn,na+4,nn,nn,off+na*ns[0]+17,off+na*ns[1]+17,2*nn,loff+na*nh+19],'whole down immutable shapes');live=bool(count and active and na==2 and(ns[0]|ns[1])%2==0 and off%2==0 and(not case['lock_mode'] or loff%2==0));eligible+=live;owned=[(5*active,na*active) if count and q==actor and active else(0,0) for q in range(2)];expectedbytes=[len(imm[8])*4,len(imm[9])*4,len(imm[11])*4,len(seeds[0])*4,len(seeds[1])*4];ranges=marker['device_regions']
   if count and not case['lock_mode']:
    regs=imm[8+actor];src=2 if actor==0 else 3
    for i in range(active):
     pr=seeds[actor][src*active+i]
     if pr&0x7fffffff:continue
     total=0.
     for a in range(na):r=fl(regs[off+a*active+i]);total=add(total,r if r>0 else 0.)
     if math.isfinite(total):
      for a in range(na):req(br[actor][(5+a)*active+i]==pr,'independent signed zero');zero[pr>>31]+=2
  for v,seed,(lo,size) in zip(br,seeds,owned):req(v[:lo]==seed[:lo] and v[lo+size:]==seed[lo+size:],'all nonowned/guard words');guard+=2*(len(v)-size);nonfinite+=2*sum((x&0x7f800000)==0x7f800000 for x in v[lo:lo+size])
  req([x['arm'] for x in ranges]==['baseline','candidate'],'both address witnesses')
  for row in ranges:
   regions=row['paired_float_regions'];req(len(regions)==5 and [x['bytes'] for x in regions]==expectedbytes,'all vector matrix extents');req(all(x['address']>0 and x['address']%8==0 and x['address']+x['bytes']<2**64 for x in regions),'actual natural alignment');req(all(a['address']+a['bytes']<=b['address'] or b['address']+b['bytes']<=a['address'] for i,a in enumerate(regions) for b in regions[i+1:]),'actual disjoint allocations')
 for r in readers:all_hashes[str(r.p)]=r.close()
 req(len(cases)==u['expected_cases']==summary['cases'] and summary['kernel_launches']==2*len(cases),'case/launch count');req(summary['output_words_both_arms']==output and summary['immutable_words_both_arms']==immutable and summary['guard_words_both_arms']==guard,'full physical word counts');req(eligible>0 and nonfinite>0,'vector eligible and exceptional coverage')
 for filename,identity in u['legacy_raw'].items():
  old=Path(identity['path']);h.pin(old,identity['sha256']);req(old.stat().st_size==identity['bytes'],'legacy extent')
  with old.open('rb') as before,(O/filename).open('rb') as after:
   while True:
    data=before.read(4*1024**2)
    if not data:break
    req(data==after.read(len(data)),'original legacy raw prefix retained')
 reports[name]={'cases':len(cases),'legacy_cases':u['legacy_cases'],'kernel_launches':2*len(cases),'output_words_both_arms':output,'immutable_words_both_arms':immutable,'guard_words_both_arms':guard,'eligible_nonempty_paired_cases':eligible,'nonfinite_active_words_both_arms':nonfinite,'signed_zero_witnesses_both_arms':zero,'legacy_all_input_baseline_and_immutable_prefixes_exact':True};totalout+=output;totalimm+=immutable;totalguard+=guard;totalcases+=len(cases)
h.custody();D=ROOT/'comparisons/E099-direct-controls';D.mkdir(exist_ok=False);h.save(D/'report.json',{'id':'E099-direct-controls','at':h.now(),'status':'pass_scoped_all_direct_device_words','protocol_sha256':sys.argv[1],'checks':checks,'cases':totalcases,'kernel_launches':totalcases*2,'output_words_both_arms':totalout,'immutable_words_both_arms':totalimm,'guard_words_both_arms':totalguard,'units':reports,'raw_file_sha256':all_hashes,'original_legacy_cases_unchanged':True,'all_physical_outputs_inputs_and_guards_exact':True,'solver_or_performance_runs':0,'candidate_accepted':False,'scope':'Finite declared device matrix only. Original scalar fallbacks plus prospective aligned pairgeometry, actual matrix addresses/extents, every raw word, exceptional/rounding signs and untouched areas. Original cases proven by entire legacy raw input/original output/immutable prefixes. No universal arithmetic/layout, multi-node engine/physical canonical, CPU/memory/capacity/speed/adoption proof.'});print(json.dumps({'status':'pass','checks':checks,'cases':totalcases,'units':reports}),flush=True)
