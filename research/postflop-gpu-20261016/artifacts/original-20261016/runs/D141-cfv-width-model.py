import sys,array,struct,collections,shutil,json
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
H=R/'runs/D141-cfv-width';A=R/'runs/D092-action-arity-order'
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
old.custody();assert not(R/'gpu-run.lock').exists()and sys.byteorder=='little'
for p,h in P['input_sha256'].items():old.pin(p,h)
assert shutil.disk_usage(R).free>=68*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
O=H/'output';O.mkdir(exist_ok=False);AR=old.read(A/'report.json');schema=old.read(A/'field-schema.json')['fields']
checks=0
def ck(v,label):
 global checks
 assert v,label;checks+=1
def vector(f,read=False):
 raw=f.read(8);ck(len(raw)==8,'vector header');n=struct.unpack('<Q',raw)[0];ck(n<100000000,'vector bound')
 if not read:f.seek(n*8,1);return None
 a=array.array('Q');a.fromfile(f,n);ck(len(a)==n,'complete vector');return a
def payload(a):ck(a[0]+1==len(a),'payload frame');return a[1:]
def spans(a,nl):ck(a[0]==nl and len(a)==1+2*nl,'span frame');return[(int(a[1+2*i]),int(a[2+2*i]))for i in range(nl)]
def pair(a):
 ck(a[0]==2,'pair frame');n=a[1];m=a[2+n];x=a[2:2+n];y=a[3+n:];ck(len(y)==m,'pair endpoint');return[x,y]
def geometry(rows,oldwidth,newwidth,allocation,root=0):
 return rows>0 and 0<newwidth<=oldwidth and rows*oldwidth<=allocation and root==0
controls=[(3,7,3,21,0,True),(3,7,0,21,0,False),(3,7,8,21,0,False),(3,7,3,20,0,False),(3,7,3,21,1,False)]
for rows,w,s,alloc,root,want in controls:ck(geometry(rows,w,s,alloc,root)==want,'geometry positive/negative control')
selected=[0,1,2,3,5,6,11,12,13,14,15,16,17,18,20,22,24,27,36,37]
names=['num_levels','nh','nh_max','num_nodes','action_nodes','action_spans','chance_nodes','chance_node_spans','fold_nodes','fold_spans','show_nodes','show_spans','cc_start','cc_count','cc_child','hand_perm_flat','node_na','node_children_start','cfv_slot','cfv_blocks']
ck([schema[i]['name']for i in selected]==names,'exact selected schema')
cases=[]
for case in range(12):
 path=A/'execution'/f'case-{case:02d}.bin';old.pin(path,AR['cases'][case]['raw_sha256']);F={};first=checks
 with path.open('rb')as f:
  ck(f.read(16)==b'D092-PLAN-RAW1\0\0','raw magic');ck(struct.unpack('<II',f.read(8))==(case,53),'raw case/schema');ck(len(f.read(16))==16,'struct sizes')
  for i in range(53):
   ck(struct.unpack('<I',f.read(4))[0]==i,'field order');vector(f);vector(f);a=vector(f,i in selected);vector(f)
   if a is not None:F[i]=a
  kinds=payload(vector(f,True));children=payload(vector(f,True));ck(f.read(1)==b'','full endpoint')
 nl=int(F[0][0]);nh=list(F[1][1:]);w=int(F[2][0]);n=int(F[3][0]);B=int(F[37][0])
 ck(len(nh)==2 and 0<min(nh)<=w==max(nh)<=1326,'hand counts');ck(len(kinds)==n,'node count')
 families=[(payload(F[ni]),spans(F[si],nl))for ni,si in [(5,6),(11,12),(13,14),(15,16)]]
 action,chance,fold,show=[x[0]for x in families];slots=payload(F[36]);arity=payload(F[24]);cs=payload(F[27]);ccs=payload(F[17]);ccc=payload(F[18]);cc=payload(F[20]);perms=pair(F[22])
 ck(all(len(x)==n for x in [slots,arity,cs,ccs,ccc]),'node arrays');level=array.array('i',[-1])*n
 allrows=set();terminalrows=set();nonterminalrows=set()
 for kind,(nodes,ss)in enumerate(families):
  at=0
  for lev,(start,count)in enumerate(ss):
   ck(start==at and start+count<=len(nodes),'work span');at+=count
   rows=set()
   for node in nodes[start:start+count]:
    ck(node<n and level[node]==-1 and kinds[node]==kind and slots[node]<B,'reached kind/slot')
    level[node]=lev;ck(slots[node]not in rows,'same family/level write disjoint');rows.add(slots[node]);allrows.add(slots[node])
    (nonterminalrows if kind<2 else terminalrows).add(slots[node])
  ck(at==len(nodes),'complete worklist')
 ck(allrows==set(range(B))and slots[0]==0,'every allocated row used and root zero')
 ck(not terminalrows.intersection(nonterminalrows)and len(terminalrows)==len(fold)+len(show),'persistent terminal rows disjoint')
 reads=0
 def sweep(writer,terminals):
  global reads
  writes=0
  for lev in reversed(range(nl)):
   outlevel=set();inlevel=set()
   for kind in [2,3,1,0]:
    if kind>=2 and not terminals:continue
    nodes,ss=families[kind];start,count=ss[lev]
    for node in nodes[start:start+count]:
     row=int(slots[node]);ck(row not in outlevel,'all same-level outputs disjoint');outlevel.add(row)
     if kind==0:
      ck(0<arity[node]<=255 and cs[node]+arity[node]<=len(children),'action span')
      inputs=children[cs[node]:cs[node]+arity[node]]
     elif kind==1:
      ck(ccs[node]+ccc[node]<=len(cc),'chance span');inputs=cc[ccs[node]:ccs[node]+ccc[node]]
     else:inputs=[]
     for child in inputs:
      ck(child<n and level[child]==lev+1 and slots[child]<B,'actual child level and slot')
      crow=int(slots[child]);ck(writer[crow]==child,'read sees exact current child producer');inlevel.add(crow);reads+=1
     writer[row]=node;writes+=1
   ck(not outlevel.intersection(inlevel),'all same-level input/output intervals disjoint')
  ck(all(x!=0xffffffff for x in writer),'full rows initialized before completion')
  return writes
 writers=array.array('I',[0xffffffff])*B;fullwrites=sweep(writers,True);before=writers.tobytes();avgwrites=sweep(writers,False)
 ck(writers.tobytes()==before,'same final row writer IDs after retained-terminal mode')
 out=O/f'case-{case:02d}-last-writers.bin'
 with out.open('xb')as f:f.write(b'D141-WRITER-v1\0\0');f.write(struct.pack('<IIQ',case,1,B));writers.tofile(f)
 ck(out.stat().st_size==32+4*B,'writer frame')
 players=[]
 for p,s in enumerate(nh):
  ck(geometry(B,w,s,B*w,int(slots[0])),'allocation and root geometry')
  ck(len(perms[p])%s==0,'permutation geometry')
  for i in perms[p]:ck(i<s,'every actual hand permutation index bounded')
  # Exhaust every actual row interval. Equal row IDs retain exactly the same
  # hand aliases; different row IDs map to nonoverlapping equal-width intervals.
  for row in range(B):
   oldlo=row*w;newlo=row*s;oldhi=oldlo+s;newhi=newlo+s
   ck(0<=oldlo<=oldhi<=B*w and 0<=newlo<=newhi<=B*w,'every full row interval in allocation')
   ck(newhi==(row+1)*s and (row==0 or newlo==(row-1)*s+s),'adjacent rows nonoverlapping')
   ck(newlo//s==row and (newhi-1)//s==row and oldlo//w==row and (oldhi-1)//w==row,'first/last hand row identity')
  players.append({'p':p,'logical_hands':s,'old_stride_words':w,'proposed_stride_words':s,'allocation_words_unchanged':B*w,'old_address_envelope_words':(B-1)*w+s,'proposed_address_envelope_words':B*s,'row_intervals_checked':B,'actual_hand_permutations_checked':len(perms[p])})
 row={'case':case,'board':AR['cases'][case]['board'],'iso_requested':AR['cases'][case]['iso_requested'],'full_arenas':AR['cases'][case]['full_arenas'],'nodes':n,'CFV_rows':B,'full_producer_writes':fullwrites,'retained_terminal_mode_writes':avgwrites,'actual_child_dependency_reads_checked':reads,'all_producer_dependencies_exact':True,'all_rows_independent_of_incoming_CFV_bytes':True,'players':players,'row_writer_file':str(out),'row_writer_sha256':old.sha(out),'accepted_raw_sha256':AR['cases'][case]['raw_sha256'],'checks':checks-first,'GPU_executions':0,'performance_measurement':False}
 old.save(O/f'case-{case:02d}.json',row);cases.append(row);print(json.dumps({k:row[k]for k in ['case','board','CFV_rows','actual_child_dependency_reads_checked','checks']}),flush=True)
old.custody();report={'id':'D141','at':old.now(),'status':'pass_retained_CFV_width_model_admit_one_host_prototype','protocol_sha256':sys.argv[1],'cases':cases,'checks':checks,'geometry_control_cases':len(controls),'compiler_invocations':0,'CUDA_contexts':0,'GPU_kernels':0,'solve_executions':0,'performance_measurement':False,'candidate_accepted':False,'source_activated':False,'limits':'Finite retained source/integer producer/address model. Interval endpoints and injective affine mapping prove the complete modeled row domains without enumerating every float address; no GPU numerical, generated-code, timing, physical memory footprint, actual capacity or universal behavior claim. Allocations remain fixed; a narrower address envelope is not memory saved. Real GPU full raw logical/physical guards, eager/captured evaluation/learning/continuation/state/save and complete performance/material gates remain.'}
old.save(H/'report.json',report);print(json.dumps({'status':report['status'],'cases':len(cases),'checks':checks,'GPU_executions':0}),flush=True)
