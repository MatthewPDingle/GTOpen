import json,sys,struct,hashlib,itertools
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
M=h.read(H/'output/metadata.json');checks=words=guards=0
def req(v,label):
 global checks
 assert v,label;checks+=1
def oracle(state,scratch,n,phases,mode):
 a=state.copy();b=scratch.copy();ix=(np.arange(n,dtype=np.int64)+128)%n if n else np.array([],dtype=np.int64)
 for phase in range(phases):
  values=a[17+ix]
  b[17:17+n]=values if mode==0 else values^np.uint32((0x9e3779b9+phase)&0xffffffff)
  a[17:17+n]=b[17:17+n]
 return a,b
raw=H/'output/raw.bin';expected=[]
for blocks in [1,2,170,2040]:
 for length_index,n in enumerate([0,1,127,128,129,513,1326,blocks*128+1]):
  for phases,mode in itertools.product([0,1,2,17],[0,1]):expected.append((blocks,length_index,n,phases,mode))
req(len(expected)==len(M['cases'])==M['case_count']==256,'whole matrix')
with raw.open('rb') as f:
 req(f.read(16)==b'D205-GRID-RAW1\0\0','raw magic');req(struct.unpack('<I',f.read(4))[0]==256,'casecount')
 for ident,dims in enumerate(expected):
  desc=struct.unpack('<7I',f.read(28));blocks,length_index,n,phases,mode=dims;count=n+36
  req(desc==(ident,blocks,length_index,n,phases,mode,count),'original ordered descriptor')
  arrays=[np.fromfile(f,dtype='<u4',count=count) for _ in range(8)];req(all(len(x)==count for x in arrays),'full vectors')
  a,b=arrays[:2];want=oracle(a,b,n,phases,mode);want2=oracle(*want,n,phases,mode)
  for actual,w in zip(arrays[2:],list(want)+list(want)+list(want2)):
   req(np.array_equal(actual,w),'entire phase output plus guard');words+=len(actual)
  for index,actual in enumerate(arrays[2:]):
   before=arrays[index%2];req(np.array_equal(actual[:17],before[:17]) and np.array_equal(actual[17+n:],before[17+n:]),'all prefix/tail guards');guards+=36
  row=M['cases'][ident];req((row['id'],row['blocks'],row['length_index'],row['active_words'],row['phases'],row['mode'],row['physical_words_each'])==(ident,*dims,count),'native metadata dimensions')
  for name in ['eager_addresses','graph_addresses']:
   a0,b0,extent=row[name]['state'],row[name]['scratch'],row[name]['each_bytes'];req(extent==count*4 and (a0+extent<=b0 or b0+extent<=a0) and row[name]['disjoint'],'actual physical allocations disjoint')
  req(row['graph']['kernel_nodes']==row['graph']['cooperative_kernel_attribute']==1 and row['graph']['node_types'].count(0)==1,'actual single cooperative graph kernel')
  req(row['completed_eager_launches']==1 and row['completed_graph_replays']==2 and row['all_full_vectors_and_guards_exact'],'all native case stages')
 req(f.read(1)==b'','whole EOF')
req(M['kernel_launches']==768 and M['capture_kernel_nodes']==256 and M['resident_blocks_per_SM']==12 and M['SM_count']==170 and M['max_cooperative_grid_blocks']==2040,'full native launch/resources inventory')
req(words+sum(2*(x[2]+36) for x in expected)==M['represented_u32_words'],'whole native word inventory')
h.custody();D=ROOT/'comparisons/D205-cooperative-grid-controls';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D205','at':h.now(),'status':'pass_scoped_cooperative_grid_visibility_and_graph_raw_controls','protocol_sha256':h.sha(H/'protocol.json'),'cases':256,'completed_kernel_launches':768,'captured_cooperative_graphs':256,'actual_state_and_scratch_words_compared':words,'guard_words_compared':guards,'reader_checks':checks,'raw_sha256':h.sha(raw),'raw_bytes':raw.stat().st_size,'native_metadata_sha256':h.sha(H/'output/metadata.json'),'all_full_outputs_and_guards_exact':True,'actual_allocations_disjoint':True,'all_actual_graph_kernel_cooperative_attributes_verified':True,'compiler_or_solver_or_speed_samples':0,'candidate_accepted':False,'scope':'Finitecopy/xorcrossblock recurrence underofficialgridbarriers,empty/tail/whole/fullresidentgrids,zero/1/2/17phases,eager andtwo graphreplays. Allrawwords/guards andactualgraphcooperative attribute exact. Integer/rawfloatbittransport only,no floatingarithmetic/CFR/wholetraversal/barrier-schedule/errorpath/otherGPU/universal liveness/performance/resource ormemory-tradeoff proof. Doesnotadmitoptimizerorclaimspeedup.'})
print(json.dumps({'status':'pass_scoped_grid_raw','cases':256,'kernel_launches':768,'words':words,'guards':guards,'checks':checks}),flush=True)
