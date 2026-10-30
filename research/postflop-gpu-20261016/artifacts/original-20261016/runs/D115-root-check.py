"""Replay all53raw fields/capacities against both arms and retained accepted anchor."""
import array,datetime,json,math,statistics,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'runs/accepted-E051-live-20261018'));import common_e051_live as old
old.custody();assert not(ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D115-parallel-plan-control';E=H/'execution';P=old.read(H/'protocol.json');N=old.read(H/'native-report.json');A=ROOT/'runs/D092-action-arity-order';AR=old.read(A/'report.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
assert N['protocol_sha256']==old.sha(H/'protocol.json')and N['all_owned_children_terminal']and len(N['cases'])==12
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
 label=f'case-{identity:02d}';receipt=old.read(E/(label+'.exit.json'));ck(receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None,'terminal native')
 start=datetime.datetime.fromisoformat(receipt['started_at']);end=datetime.datetime.fromisoformat(receipt['finished_at']);ck(start<=end and(previous is None or previous<=start),'serial fresh-process order');previous=end
 path=E/(label+'.bin');old.pin(path,N['raw_sha256'][path.name]);old.pin(A/'execution'/(label+'.bin'),AR['cases'][identity]['raw_sha256'])
 native=[json.loads(x.split('D115 ',1)[1])for x in(E/(label+'.stdout.log')).read_text(encoding='utf-8').splitlines()if x.startswith('D115 ')];ck(native==[observed],'native report agreement')
 words=0
 with path.open('rb')as f,(A/'execution'/(label+'.bin')).open('rb')as g:
  ck(f.read(16)==b'D115-PLAN-RAW1\0\0'and g.read(16)==b'D092-PLAN-RAW1\0\0','raw magic')
  ck(struct.unpack('<II',f.read(8))==struct.unpack('<II',g.read(8))==(identity,53),'case/schema')
  sa,sb=struct.unpack('<QQ',f.read(16));ga,gb=struct.unpack('<QQ',g.read(16));ck(sa==sb==ga==gb and sa>0,'struct size')
  for field in range(53):
   ck(struct.unpack('<I',f.read(4))[0]==struct.unpack('<I',g.read(4))[0]==field,'field IDs')
   ca,cb,wa,wb=[vector(f)for _ in range(4)];oc=vector(g);vector(g,True);ow=vector(g);vector(g,True)
   ck(ca==cb==oc,'all capacities exact');ck(wa==ow,'baseline equals accepted anchor');ck(wa==wb,'all53fields exact');words+=len(wa)
  for _ in range(2):ck(vector(f)==vector(g),'tree kinds/children exact')
  ck(f.read(1)==g.read(1)==b'','complete raw endpoints')
 ck(words==observed['baseline_words'],'word inventory');total+=words;raw_bytes+=path.stat().st_size
 b,c=observed['baseline_samples_ms'],observed['candidate_samples_ms'];ck(len(b)==len(c)==9 and observed['pair_orders']==P['pair_order'],'fixed9pairs/order');ck(all(math.isfinite(v)and v>=0 for v in b+c),'finite timings')
 bm,cm=statistics.median(b),statistics.median(c);ck(bm==observed['baseline_plan_ms']and cm==observed['candidate_plan_ms'],'median replay')
 results.append({'case':identity,'baseline_median_plan_ms':bm,'candidate_median_plan_ms':cm,'added_plan_ms':cm-bm,'slower_pairs':sum(y>x for x,y in zip(b,c)),'raw_sha256':old.sha(path),'all53fields_and_capacities_exact':True,'struct_and_tree_exact':True})
old.custody();report={'id':'D115','at':old.now(),'status':'pass_all53_CPU_fields_and_capacities','checks':checks,'protocol_sha256':old.sha(H/'protocol.json'),'native_report_sha256':old.sha(H/'native-report.json'),'cases':results,'all53_fields_exact':True,'all_capacities_exact':True,'all_encoded_baseline_words_compared':total,'raw_bytes':raw_bytes,'canonical_cases':[2,6,10],'canonical_added_component_ms':sum(results[i]['added_plan_ms']for i in[2,6,10]),'source_activated':False,'gpu_executions':0,'full_cycle_performance_measured':False,'optimization_accepted':False,'limits':'CPU component/raw metadata evidence only. All fixed complete-solve1%,fixture,fresh16,broad,actual material CPU/peak/responsiveness/capacity,holdout,cumulative gates remain required. Root replay is not an external independent audit.'}
old.save(H/'report.json',report);print(json.dumps({'status':report['status'],'checks':checks,'words':total,'canonical_added_plan_ms':report['canonical_added_component_ms'],'report_sha256':old.sha(H/'report.json')}),flush=True)
