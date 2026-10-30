"""Full independent integer decoder of all primitive device images and graph edges."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D286-fork-join-primitive';P=h.read(H/'binding-protocol-r2.json');C=h.read(H/'execution-r2/native-complete.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
h.pin(H/'execution-r2/raw-results.jsonl',C['raw_sha256']);h.pin(H/'execution-r2/graph-dags.json',C['DAG_sha256'])
special=[0,0x80000000,1,0x80000001,0x007fffff,0x00800000,0x3f800000,0xbf800000,0x7f7fffff,0xff7fffff,0x7f800000,0xff800000,0x7fc12345,0xffc54321,0x7f812345,0xff854321]
def pattern(n,tag):
 out=[];shift=tag%31+1
 for i in range(n):
  if i<16:v=special[i]^(0x80000000 if tag&1 else 0)
  else:
   z=(i*0x9e3779b9+tag*0x85ebca6b)&0xffffffff;v=((z<<shift)|(z>>(32-shift)))&0xffffffff
  out.append(v)
 return out
checks=words=0;records=[]
def verify(r):
 global checks,words
 n=r['n'];total=2*n+37;epoch=r['epoch'];assert r['total']==total
 for name,length,tag in [('source_a_words',n+6,1),('source_b_words',n+10,2),('initial_words',total,3)]:assert r[name]==pattern(length,epoch*10+tag);checks+=length
 exp=r['initial_words'].copy();exp[7:7+n]=r['source_a_words'][3:3+n];exp[n+19:2*n+19]=r['source_b_words'][5:5+n]
 state=r['expected_state'];assert state in ['outputs','producer_only','poisoned']
 assert r['cfv_words']==(exp if state!='poisoned'else[0x4b123456]*total);assert r['consumer_words']==(exp if state=='outputs'else[0x4b654321]*total);checks+=2*total
 regions=r['regions'];assert regions['producer_a_offset_words']==7 and regions['producer_b_offset_words']==n+19 and regions['producer_words']==n
 extents=[]
 for name,expected_words in [('a',n+6),('b',n+10),('init',total),('cfv',total),('out',total)]:
  base,size=regions[name];assert isinstance(base,int)and base>0 and base%4==0 and size==4*expected_words;extents.append((base,base+size))
 for i,(a,b)in enumerate(extents):
  for c,d in extents[i+1:]:assert b<=c or d<=a
 assert 7+n<=n+19 and 2*n+19<=total;words+=8*n+127;checks+=26
def dagcheck(d):
 deps=d['dependencies'];want={'prefix','a','b'}if d['abort']else{'prefix','a','b','consumer'};assert set(deps)==want and d['kernel_nodes']==len(want)
 for k,v in deps.items():assert len(v)==len(set(v))and all(x in want and x!=k for x in v)
 def ancestors(target):
  todo=list(deps[target]);seen=set()
  while todo:
   x=todo.pop();assert x!=target
   if x not in seen:seen.add(x);todo.extend(deps[x])
  return seen
 assert 'prefix'in ancestors('a')and'prefix'in ancestors('b')
 if d['fork']:assert'a'not in ancestors('b')and'b'not in ancestors('a')
 else:assert'a'in ancestors('b')
 if not d['abort']:assert {'a','b'}<=ancestors('consumer')
 matches=[r for r in records if r['n']==d['n']and r['regions']['cfv'][0]==next(p['dst']for p in d['parameters']if p['label']=='prefix')];assert matches
 r=matches[0];g=r['regions'];n=r['n'];expected={'prefix':(g['init'][0],g['cfv'][0],2*n+37),'a':(g['a'][0]+12,g['cfv'][0]+28,n),'b':(g['b'][0]+20,g['cfv'][0]+4*(n+19),n),'consumer':(g['cfv'][0],g['out'][0],2*n+37)}
 assert {p['label']for p in d['parameters']}==want
 for p in d['parameters']:assert (p['src'],p['dst'],p['words'])==expected[p['label']]
order=[(n,arm,epoch,'eager'if epoch==0 else'graph_replay','outputs')for n in P['sizes']for arm in ['serial','fork']for epoch in range(5)]+[(257,'fork',10,'host_abort_eager','producer_only'),(257,'fork',11,'recovery_eager','outputs'),(257,'fork',12,'host_abort_capture','poisoned'),(257,'fork',13,'recovery_capture','outputs')]
with (H/'execution-r2/raw-results.jsonl').open(encoding='utf-8')as f:
 for expected in order:
  line=f.readline();assert line;r=json.loads(line);assert tuple(r[k]for k in ['n','arm','epoch','stage','expected_state'])==expected;verify(r);records.append(r)
 assert f.read()==''
dags=h.read(H/'execution-r2/graph-dags.json');assert len(dags)==15
for i,d in enumerate(dags):
 assert d['abort']==(i==14)and d['n']==(P['sizes'][i//2]if i<14 else 257)and d['fork']==(i%2==1 or i==14);dagcheck(d)
negative=[]
bad=copy.deepcopy(records[0]);bad['cfv_words'][0]^=1
try:verify(bad)
except AssertionError:negative.append('changed_output_word')
else:raise AssertionError('changed output accepted')
bad=copy.deepcopy(records[0]);bad['regions']['b'][0]=bad['regions']['a'][0]
try:verify(bad)
except AssertionError:negative.append('overlapping_device_allocations')
else:raise AssertionError('overlap accepted')
bad=copy.deepcopy(dags[1]);bad['dependencies']['b'].append('a')
try:dagcheck(bad)
except AssertionError:negative.append('serialized_fork_graph')
else:raise AssertionError('serialized fork accepted')
assert len(records)==74 and sum(d['kernel_nodes']for d in dags)==59 and C['summary']['actual_application_kernel_executions']==291
h.custody();h.save(H/'report.json',{'id':'D286','at':h.now(),'status':'pass_scoped_disjoint_buffer_fork_join_eager_capture_replay_primitive','protocol_sha256':h.sha(H/'binding-protocol-r2.json'),'raw_sha256':C['raw_sha256'],'raw_bytes':C['raw_bytes'],'DAG_sha256':C['DAG_sha256'],'all74_full_device_records_independent_integer_oracle_exact':True,'all_device_words_decoded':words,'checks':checks,'all15actual_graph_DAGs_and_parameters_checked':True,'captured_kernel_nodes':59,'actual_application_kernel_executions':291,'negative_reader_fixtures':negative,'all_owned_streams_graphs_events_allocations_released':True,'limits':'Unchanged accepted copy_span transport only; same physical destination allocation has disjoint producer ranges and joined dependent consumer. Eventtracking explicitlydisabled asproduction. Two deliberate host aborts verify normal eager/capture cleanup/recovery, not arbitraryCUDAfailure safety. No poker arithmetic/actualterminalkernel overlap/solver/optimizer/capacity/material/performance/adoption evidence. Device concurrency capability or independent graph branches do not prove simultaneous execution or speed.','CFR_solver_NVRTC_speed_samples':0,'candidate_accepted':False});print(json.dumps({'status':'pass_scoped_primitive','records':len(records),'words':words,'graphs':len(dags),'negative_fixtures':negative}),flush=True)
