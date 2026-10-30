"""D111: source dependency audit and immutable showdown order census."""
import array,json,struct,sys,subprocess,shutil
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();assert shutil.disk_usage(ROOT).free>66*1024**3
H=ROOT/'runs/D111-showdown-order-audit';H.mkdir();A=ROOT/'runs/D092-action-arity-order';AR=old.read(A/'report.json');S=old.read(A/'field-schema.json');want={'show_nodes','show_spans','node_river_slot','cfv_slot','cfv_blocks','num_slots','num_nodes'}
inputs=[Path(__file__),A/'report.json',A/'field-schema.json',old.REPO/'crates/solver/src/gpu/plan.rs',old.REPO/'crates/solver/src/gpu/mod.rs',old.REPO/'crates/solver/src/gpu/kernels.cu']+[A/'execution'/f'case-{i:02d}.bin' for i in range(12)]
old.save(H/'protocol.json',{'id':'D111','at':old.now(),'scope':'Source dependency/ownership audit and already-saved E051 baseline CPU plan data only. No new native process or timing.','input_sha256':{str(p):old.sha(p) for p in inputs},'order':'Stable deterministic tuple (river_slot,node_id) within each unchanged level span only.','checks':'Exact unique node multisets, same span counts, valid slots, disjoint persistent CFV rows, transition census.','selection':'Only if at least one registered level has fewer adjacent board-slot transitions; this is a structural prerequisite, not predicted GPU caching/time or performance admission.','source_unchanged':True,'no_D110_timing_inference':True})
checks=0
def ck(v,label):
 global checks
 assert v,label;checks+=1

def vector(f,read=False):
 n=struct.unpack('<Q',f.read(8))[0];ck(n<100000000,'bounded words')
 if not read:f.seek(n*8,1);return None
 v=array.array('Q');v.fromfile(f,n);ck(len(v)==n,'complete vector');return v
cases=[]
for identity,anchor in enumerate(AR['cases']):
 path=A/'execution'/f'case-{identity:02d}.bin';old.pin(path,anchor['raw_sha256']);fields={}
 with path.open('rb') as f:
  ck(f.read(16)==b'D092-PLAN-RAW1\0\0','framing');ck(struct.unpack('<II',f.read(8))==(identity,53),'case/schema');f.read(16)
  for index,desc in enumerate(S['fields']):
   ck(struct.unpack('<I',f.read(4))[0]==index,'field id');vector(f);vector(f);v=vector(f,desc['name'] in want);vector(f)
   if v is not None:fields[desc['name']]=v
  vector(f);vector(f);ck(f.read(1)==b'','full endpoint')
 n=fields['num_nodes'][0];ns=fields['num_slots'][0];cfvb=fields['cfv_blocks'][0]
 shown=fields['show_nodes'];sp=fields['show_spans'];slots=fields['node_river_slot'];cfv=fields['cfv_slot'];ck(shown[0]==len(shown)-1,'show framing');ck(sp[0]*2+1==len(sp),'span framing');ck(slots[0]==cfv[0]==n,'node geometry')
 shown=list(shown[1:]);slots=slots[1:];cfv=cfv[1:];proposed=[];levels=[];end=0;writes=set()
 for level in range(sp[0]):
  start,count=sp[1+2*level:3+2*level];ck(start==end and start+count<=len(shown),'span partition');end=start+count;original=shown[start:end]
  ck(len(set(original))==count and all(x<n and slots[x]<ns and cfv[x]<cfvb for x in original),'all nodes slots valid')
  ck(all(cfv[x] not in writes for x in original) and len({cfv[x] for x in original})==len(original),'disjoint persistent CFV rows');writes.update(cfv[x] for x in original)
  new=sorted(original,key=lambda x:(slots[x],x));ck(set(new)==set(original),'exact same level multiset');ck(all((slots[x],x)<(slots[y],y) for x,y in zip(new,new[1:])),'strict deterministic tuple order')
  before=sum(slots[x]!=slots[y] for x,y in zip(original,original[1:]));after=sum(slots[x]!=slots[y] for x,y in zip(new,new[1:]));unique=len({slots[x] for x in original})
  ck(after==max(0,unique-1) and after<=before,'exact minimal adjacency transitions')
  levels.append({'level':level,'count':count,'distinct_slots':unique,'before_slot_transitions':before,'after_slot_transitions':after,'changed_positions':sum(x!=y for x,y in zip(original,new))});proposed.extend(new)
 ck(end==len(shown)==len(proposed)==len(writes),'all spans/full disjoint output coverage')
 out=H/f'case-{identity:02d}-proposed.bin'
 with out.open('xb') as f:
  f.write(b'D111-SHOW-ORDER1');f.write(struct.pack('<IQ',identity,len(proposed)));array.array('I',proposed).tofile(f)
 cases.append({'id':identity,'board':anchor['board'],'iso_requested':anchor['iso_requested'],'full_arenas':anchor['full_arenas'],'show_nodes':len(shown),'unique_output_rows':len(writes),'before_slot_transitions':sum(x['before_slot_transitions'] for x in levels),'after_slot_transitions':sum(x['after_slot_transitions'] for x in levels),'changed_positions':sum(x['changed_positions'] for x in levels),'levels':levels,'raw_baseline_sha256':old.sha(path),'raw_proposed_sha256':old.sha(out),'raw_proposed_bytes':out.stat().st_size})
 print(json.dumps({'case':identity,'show_nodes':len(shown),'transitions':[cases[-1]['before_slot_transitions'],cases[-1]['after_slot_transitions']],'changed_positions':cases[-1]['changed_positions']}),flush=True)
report={'id':'D111','at':old.now(),'status':'structural_ordering_hypothesis_supported' if any(c['before_slot_transitions']>c['after_slot_transitions'] for c in cases) else 'no_reordering_opportunity','checks':checks,'cases':cases,'source_findings':['GpuPlan CFV/worklist/river arrays and node-scalar/dense-owner arrays have independent post-DFS immutable inputs but would require concurrency/peak/lifetime qualification. No parallel candidate created or gain inferred.','Show worklists currently append node IDs in ascending order within levels, before river slots are assigned. Both training and evaluation launch up_show using these fixed per-level spans.','up_show reads reach and immutable metadata, and each terminal writes its own persistent CFV row. It does not read the CFV buffer. Reordering distinct show nodes within the same stream launch preserves per-node arithmetic and inter-kernel dependency order.','No applicable show-by-river ordering candidate found in bounded current ledger, preserved Rust source or local all-ref plan history searches; not exhaustive remote history.','Different GPU block scheduling, reach/output locality and added CPU sort cost could erase any immutable-table locality advantage; no hardware cache counter or predicted speedup.'],'new_native_processes':0,'gpu_executions':0,'new_timing_samples':0,'uses_D110_timing_for_selection':False,'optimization_accepted':False,'accepted_source_unchanged':True,'next':'If structural prerequisite passes, freeze one plan-only tuple-sort candidate; exact full fields/capacities/permutation/disjoint outputs and CPU sort overhead precede fixed complete-solve screen. No CUDA/math/launch-count/resource/quality changes or variants.','limits':'Historical baseline CPU plan metadata and static source only. Slot-transition counts are not GPU scheduler order, cache misses, bandwidth, latency or speed evidence; exact CPU metadata does not prove runtime numerical/whole-state equivalence.'}
old.save(H/'report.json',report);old.custody();print(json.dumps({'status':report['status'],'checks':checks,'report_sha256':old.sha(H/'report.json')}),flush=True)