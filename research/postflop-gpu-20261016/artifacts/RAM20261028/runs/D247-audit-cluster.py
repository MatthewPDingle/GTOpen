import json,struct,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
P=h.read(H/'protocol.json');C=h.read(H/'execution/complete-native.json');cases=h.read(H/'corpus.json');checks=0
def req(v,label):
 global checks
 assert v,label;checks+=1
for p,d in P['input_sha256'].items():h.pin(p,d)
for p,d in C['raw_sha256'].items():h.pin(p,d)
data=(H/'output/raw.bin').read_bytes();magic=b'D247-CLUSTER-RAW1\0';req(data.startswith(magic),'rawmagic');at=len(magic)
def integer():
 global at
 req(at+4<=len(data),'wordbounds');v,=struct.unpack_from('<I',data,at);at+=4;return v
def vector():
 global at
 req(at+8<=len(data),'lengthbounds');n,=struct.unpack_from('<Q',data,at);at+=8;req(n<=1000000 and at+4*n<=len(data),'vectorbounds');v=list(struct.unpack_from('<'+'I'*n,data,at));at+=4*n;return v
req(integer()==len(cases)==132,'wholecasecount');meta=h.read(H/'output/metadata.json');req(meta['case_count']==132 and meta['kernel_launches']==660 and meta['capture_kernel_nodes']==132,'metadatawholecounts');req(len(meta['cases'])==132,'allmetadata')
MASK=2**32-1;B=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x7f800000,0xff800000,0x7fc01234,0xffc01234,0x7f801234,0xff801234,0x7f7fffff,0xffffffff];words=changed=guards=actual_input_words=actual_output_words=0
for c,m in zip(cases,meta['cases']):
 id,threads,clusters,n=c['id'],c['threads'],c['clusters'],c['words_per_block'];blocks=2*clusters;length=36+blocks*n
 req([integer()for _ in range(5)]==[id,threads,clusters,n,length],'wholeactualdescriptor');src=vector();req(len(src)==length,'sourceextent');expected=[(0xa5123456+id*131+i*17)&MASK for i in range(length)]
 for b in range(blocks):
  for i in range(n):expected[17+b*n+i]=((i*0x85ebca6b)&MASK)^((id*0xc2b2ae35)&MASK)^(((b+1)*0x9e3779b9)&MASK)if i%3==0 else B[(i+id+b)%16]
 req(src==expected,'fullsourcegeneration');words+=length
 req(m['id']==id and m['descriptor']==c and m['eager_launches']==1 and m['graph_replays']==4 and m['whole_outputs_inputs_guards_exact'],'allcasemetadata');g=m['graph'];req(g=={'kernel_nodes':1,'grid':[blocks,1,1],'block':[threads,1,1],'dynamic_shared_per_block':max(1,n)*4,'captured_function_required_cluster_dimensions':[2,1,1]},'actualsinglekernelgraph/staticclusterdimensions/shape')
 ranges=m['actual_device_regions'];req(len(ranges)==2 and all(isinstance(p,int)and p>0 and size==length*4 and p+size<2**64 for p,size in ranges),'realdeviceextents');(a,asz),(b,bsz)=ranges;req(a+asz<=b or b+bsz<=a,'actualsourceoutputallocationsdisjoint')
 for phase in range(5):
  req(integer()==phase,'all5executionframes');seed,out,post=vector(),vector(),vector();req(len(seed)==len(out)==len(post)==length,'wholephysicalframes');poison=[0xcd000000^((id*257)&MASK)^((phase*0x9e37)&MASK)^((i*13)&MASK)for i in range(length)];req(seed==poison,'actualprelaunchpoison');req(post==src,'wholeimmutableactualdeviceinput');req(out[:17]==seed[:17]and out[17+blocks*n:]==seed[17+blocks*n:],'allunownedguards')
  for block in range(blocks):req(out[17+block*n:17+(block+1)*n]==src[17+(block^1)*n:17+((block^1)+1)*n],'completepeerremoteimage')
  this=sum(x!=y for x,y in zip(out,seed));req(n==0 or this>0,'nonvacuousreplaywrites');changed+=this;words+=3*length;guards+=36;actual_input_words+=length;actual_output_words+=2*length
req(at==len(data),'rawendpoint');req(words==meta['represented_raw_words']and changed==meta['nonvacuous_output_changes'],'native/readerwordandchangecounts');rows=[json.loads(l.split('D247_CONTROL ',1)[1])for l in(H/'execution/probe.stdout.log').read_text().splitlines()if'D247_CONTROL 'in l];req(len(rows)==133 and rows[-1]['cases']==132 and rows[-1]['kernel_launches']==660,'allterminalmarkers')
for c,row in zip(cases,rows[:-1]):req(all(row[k]==c[k]for k in ['id','threads','clusters','words_per_block'])and row['exact']and row['eager']==1 and row['graph_replays']==4,'eachactualcasemarker')
h.custody();O=ROOT/'comparisons/D247-cluster-controls';O.mkdir(exist_ok=False);h.save(O/'report.json',{'id':'D247','at':h.now(),'status':'pass_scoped_cluster_peer_transport_lifetime_and_graph_raw_controls','cases':132,'kernel_launches':660,'graph_capture_kernel_nodes':132,'represented_raw_words':words,'actual_immutable_input_words':actual_input_words,'actual_output_prepost_words':actual_output_words,'unowned_guard_words':guards,'nonvacuous_changed_output_words':changed,'reader_checks':checks,'raw_sha256':C['raw_sha256'],'protocol_sha256':h.sha(H/'protocol.json'),'reader_sha256':h.sha(__file__),'candidate_accepted':False,'solver_or_speed_samples':0,'limits':'Finiteintegerbittransport/graphprimitive only. Actualtwo-blockclusterfunctionattrs,wholeinputs/peeroutputs/guards andnonvacuous4replays,bothpublication/lifetimebarriers structurallybound. No floatingCFR/scan/largegame/resourcepeak/latency/performance/solverprototype oradoptionproof.'});print(json.dumps({'status':'pass','cases':132,'kernel_launches':660,'raw_words':words,'reader_checks':checks}),flush=True)
