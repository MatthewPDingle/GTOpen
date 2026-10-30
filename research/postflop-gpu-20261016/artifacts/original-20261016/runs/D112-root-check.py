"""D112 root replay: every full field, capacities, and the independently frozen order."""
import array,datetime,json,math,statistics,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D112-showdown-order-control';E=H/'execution';P=old.read(H/'protocol.json');N=old.read(H/'native-report.json');A=ROOT/'runs/D092-action-arity-order';AR=old.read(A/'report.json');D=ROOT/'runs/D111-showdown-order-audit';DR=old.read(D/'report.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
seal=old.read(H/'execution-seal.json');old.pin(H/'execute.py',seal['script_sha256']);assert seal['protocol_sha256']==old.sha(H/'protocol.json')
assert N['protocol_sha256']==old.sha(H/'protocol.json') and N['all_owned_children_terminal'] and len(N['cases'])==12
assert old.read(H/'build/rustc.exit.json')['returncode']==0
checks=0;total=0;raw_bytes=0;results=[];previous=None

def ck(v,label):
 global checks
 assert v,label;checks+=1

def vector(f,skip=False):
 n=struct.unpack('<Q',f.read(8))[0];ck(n<=100000000,'bounded words')
 if skip:f.seek(n*8,1);return None
 a=array.array('Q');a.fromfile(f,n);ck(len(a)==n,'whole vector');return a
for identity,observed in enumerate(N['cases']):
 label=f'case-{identity:02d}';receipt=old.read(E/(label+'.exit.json'));ck(receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None,'terminal native')
 start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);ck(start<=end and (previous is None or previous<=start),'serial order');previous=end
 path=E/(label+'.bin');old.pin(path,N['raw_sha256'][path.name]);old.pin(A/'execution'/(label+'.bin'),AR['cases'][identity]['raw_sha256'])
 native=[json.loads(x.split('D112 ',1)[1]) for x in (E/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines() if x.startswith('D112 ')];ck(native==[observed],'native report agreement')
 words=0;fields={}
 with path.open('rb') as f,(A/'execution'/(label+'.bin')).open('rb') as g:
  ck(f.read(16)==b'D112-PLAN-RAW1\0\0' and g.read(16)==b'D092-PLAN-RAW1\0\0','raw magic')
  ck(struct.unpack('<II',f.read(8))==struct.unpack('<II',g.read(8))==(identity,53),'case/schema')
  sa,sb=struct.unpack('<QQ',f.read(16));ga,gb=struct.unpack('<QQ',g.read(16));ck(sa==sb==ga==gb and sa>0,'struct size')
  for field in range(53):
   ck(struct.unpack('<I',f.read(4))[0]==struct.unpack('<I',g.read(4))[0]==field,'field ids')
   ca,cb,wa,wb=[vector(f) for _ in range(4)];oc=vector(g);vector(g,True);ow=vector(g);vector(g,True)
   ck(ca==cb==oc,'all capacities exact');ck(wa==ow,'baseline exact accepted anchor')
   if field!=15:ck(wa==wb,'all52nonorder fields exact')
   if field in [3,15,16,32,36,37,43]:fields[field]=(wa,wb)
   words+=len(wa)
  for _ in range(2):ck(vector(f)==vector(g),'actual tree source exact')
  ck(f.read(1)==g.read(1)==b'','complete raw endpoints')
 ck(words==observed['baseline_words'],'word inventory');total+=words;raw_bytes+=path.stat().st_size
 shown=list(fields[15][0][1:]);candidate=list(fields[15][1][1:]);sp=fields[16][0];slots=fields[32][0][1:];cfv=fields[36][0][1:];n=fields[3][0][0];ns=fields[43][0][0];cfvb=fields[37][0][0]
 ck(fields[15][0][0]==fields[15][1][0]==len(shown)==len(candidate),'show vector framing');ck(len(sp)==1+2*sp[0],'span framing')
 writes=set();end=0
 for level in range(sp[0]):
  start,count=sp[1+2*level:3+2*level];ck(start==end and start+count<=len(shown),'same full span partition');end=start+count
  a=shown[start:end];b=candidate[start:end];ck(len(set(a))==count and set(a)==set(b),'same level unique nodes')
  ck(all(x<n and slots[x]<ns and cfv[x]<cfvb for x in a),'valid row slots');ck(len({cfv[x] for x in a})==count and not writes.intersection(cfv[x] for x in a),'globally disjoint outputs');writes.update(cfv[x] for x in a)
  ck(b==sorted(a,key=lambda x:(slots[x],x)),'exact prospective tuple order')
 ck(end==len(shown)==len(writes),'full coverage')
 proposed=D/f'case-{identity:02d}-proposed.bin';old.pin(proposed,DR['cases'][identity]['raw_proposed_sha256'])
 with proposed.open('rb') as f:
  ck(f.read(16)==b'D111-SHOW-ORDER1','independent order framing');ck(struct.unpack('<IQ',f.read(12))==(identity,len(candidate)),'independent order geometry');aa=array.array('I');aa.fromfile(f,len(candidate));ck(list(aa)==candidate and f.read(1)==b'','exact independent D111 order')
 b,c=observed['baseline_samples_ms'],observed['candidate_samples_ms'];ck(len(b)==len(c)==9 and observed['pair_orders']==P['pair_order'],'fixed9pairs/order');ck(all(math.isfinite(v) and v>=0 for v in b+c),'finite timings')
 bm,cm=statistics.median(b),statistics.median(c);ck(bm==observed['baseline_plan_ms'] and cm==observed['candidate_plan_ms'],'median replay')
 results.append({'case':identity,'baseline_median_plan_ms':bm,'candidate_median_plan_ms':cm,'added_plan_ms':cm-bm,'slower_pairs':sum(y>x for x,y in zip(b,c)),'raw_sha256':old.sha(path),'all52_nonorder_fields_exact':True,'all_capacities_and_struct_size_exact':True,'show_order_equals_D111':True,'same_level_disjoint_output_rows':True})
old.custody()
report={'id':'D112','at':old.now(),'status':'pass_cpu_metadata_and_concrete_ownership','checks':checks,'protocol_sha256':old.sha(H/'protocol.json'),'native_report_sha256':old.sha(H/'native-report.json'),'cases':results,'concrete_same_level_ownership_pass':True,'nonorder_fields_exact':True,'all_encoded_baseline_words_compared':total,'raw_bytes':raw_bytes,'canonical_cases':[2,6,10],'canonical_added_component_ms':sum(results[i]['added_plan_ms'] for i in [2,6,10]),'source_activated':False,'gpu_executions':0,'full_cycle_performance_measured':False,'optimization_accepted':False,'limits':'CPU metadata/control replay only; component sort costs are not complete-solve loss or predicted GPU gain. All frozen full-cycle, fixture, fresh16 and material tradeoff gates remain required. Root replay is not external independent review.'}
old.save(H/'report.json',report);print(json.dumps({'status':report['status'],'checks':checks,'words':total,'canonical_added_plan_ms':report['canonical_added_component_ms'],'report_sha256':old.sha(H/'report.json')}),flush=True)
