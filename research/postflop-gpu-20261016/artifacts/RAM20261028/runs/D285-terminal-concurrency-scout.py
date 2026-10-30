"""Frozen retained-plan proof for independent fold/show work; no native work."""
import array,json,re,shutil,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D285-terminal-concurrency-scout';parent=ROOT/'runs/D262-chance-ownership/protocol.json'
SELECT=['num_levels','num_nodes','nh','nh_max','cfv_blocks','cfv_slot','fold_nodes','fold_spans','show_nodes','show_spans','action_nodes','chance_nodes']
if len(sys.argv)==1:
 h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();H.mkdir(exist_ok=False)
 pp=h.read(parent);ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
 revisions=subprocess.check_output(['git','log','--all','--format=%H','--','crates/solver/src/gpu/mod.rs'],cwd=h.REPO,text=True).splitlines();blobs={};matches=[]
 pattern=re.compile(r'(?:fold|show|terminal)[^\n]{0,90}(?:stream|event)|(?:stream|event)[^\n]{0,90}(?:fold|show|terminal)',re.I)
 for rev in revisions:
  data=subprocess.check_output(['git','show',rev+':crates/solver/src/gpu/mod.rs'],cwd=h.REPO);digest=__import__('hashlib').sha256(data).hexdigest()
  blobs.setdefault(digest,[]).append(rev)
  for i,line in enumerate(data.decode('utf-8').splitlines(),1):
   if pattern.search(line):matches.append({'revision':rev,'line':i,'text':line})
 h.save(H/'history.json',{'at':h.now(),'path':'crates/solver/src/gpu/mod.rs','local_all_ref_revisions':revisions,'unique_blob_revisions':blobs,'literal_same_line_terminal_stream_matches':matches,'semantic_classification':'Bounded local solver-host history only. E104 changes launch phases into cooperative grid, E111 shares metadata within clusters, E078 fuses fold into parents; this concept preserves original kernels and independent terminal grids, forks only fold/show of one level, rejoins before all dependent work. E040 readback pipeline and E079 CPU/context overlap are different boundaries. No multi-iteration batching or missed per-iteration stop/lock checks. Negative literal search is not exhaustive semantic/remote novelty proof.'})
 files=[Path(__file__),parent,Path(pp['schema_path']),H/'history.json',ROOT/'epoch/common.py',ROOT/'runs/D212-current-RAM-activity/report.json',ROOT/'comparisons/E118-three-pair-comparison/report.json',ledger,h.REPO/'crates/solver/src/gpu/mod.rs',h.REPO/'crates/solver/src/gpu/plan.rs',h.REPO/'crates/solver/src/gpu/kernels.cu']
 h.save(H/'protocol.json',{'id':'D285','at':h.now(),'status':'FROZEN_PRE_RETAINED_PLAN_DECODER','raw_inputs':pp['raw_inputs'],'schema_path':pp['schema_path'],'selected_fields':SELECT,'input_sha256':{str(p):h.sha(p)for p in files},'concept':'Original fold/show grids of same up-sweep level can use separate nonblocking streams after a common readiness event, then join main stream before chance/action/nextlevel/return. No CUDA math/source/launch shape/arrays/ordering within kernels changes. Timing opportunity is conditional; no concurrency/speed guarantee. No production source/candidate yet.','requirements':'Every original terminal output row globally unique and bounded, disjoint from all action/chance scratch. Samelevel fold/show node sets unique/disjoint and span partition complete. Both read immutable reach/metadata, neither reads CFV. Original13? No hardcoded family counts; exact functions inspected. Later raw-pointer disjoint ownership, explicit disabled-event-tracking stream lifetime/error joins, actual graph dependencies/capture/primitive and component budget required before optimizer.','doc_links':['https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-programming-guide/index.html#cross-stream-dependencies-and-events','https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-programming-guide/index.html#concurrent-kernel-execution'],'docs_contract':'Cross-stream captured events must belong to same capture graph; side stream must rejoin origin before EndCapture. Different-stream execution may overlap, but is not guaranteed. Never rely on concurrent progress for correctness.','new_GPU_compiler_solver_performance_samples':0});print(h.sha(H/'protocol.json'),flush=True);sys.exit(0)
assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json');h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
fields=[v[0]for v in h.read(P['schema_path'])['fields']]
def vec(raw,code):
 n,=struct.unpack_from('<Q',raw);v=array.array(code);v.frombytes(raw[8:]);assert len(v)==n
 if sys.byteorder!='little':v.byteswap()
 return v
def plan(path):
 out={}
 with path.open('rb')as f:
  assert f.read(17)==b'D183_PLAN_RAW1\0\0\0'
  for name in fields:
   n,=struct.unpack('<I',f.read(4));assert f.read(n).decode()==name;size,=struct.unpack('<Q',f.read(8))
   if name in SELECT:out[name]=f.read(size);assert len(out[name])==size
   else:f.seek(size,1)
  assert not f.read(1)
 return out
rows=[];checks=0
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status())
 for item in P['raw_inputs']:
  path=Path(item['path']);h.pin(path,item['sha256']);assert path.stat().st_size==item['bytes'];raw=plan(path);n,=struct.unpack('<Q',raw['num_nodes']);levels,=struct.unpack('<Q',raw['num_levels']);blocks,=struct.unpack('<Q',raw['cfv_blocks']);stride,=struct.unpack('<Q',raw['nh_max']);nh=list(vec(raw['nh'],'Q'));assert max(nh)==stride and stride<=1326
  d={k:vec(raw[k],'I')for k in ['cfv_slot','fold_nodes','show_nodes','action_nodes','chance_nodes']};assert len(d['cfv_slot'])==n
  terminal_nodes=list(d['fold_nodes'])+list(d['show_nodes']);assert len(terminal_nodes)==len(set(terminal_nodes));slots=[d['cfv_slot'][node]for node in terminal_nodes];assert len(slots)==len(set(slots))and all(s<blocks for s in slots)
  scratch={d['cfv_slot'][node]for node in list(d['action_nodes'])+list(d['chance_nodes'])};assert set(slots).isdisjoint(scratch);checks+=len(terminal_nodes)*3+len(scratch)+4
  spans={}
  for kind in ['fold','show']:
   sr=raw[kind+'_spans'];num,=struct.unpack_from('<Q',sr);assert num==levels and len(sr)==8+8*num;spans[kind]=list(struct.Struct('<II').iter_unpack(sr[8:]));cursor=0
   for start,count in spans[kind]:assert start==cursor;cursor+=count
   assert cursor==len(d[kind+'_nodes'])
  lr=[]
  for level in range(levels):
   fn=[d['fold_nodes'][i]for i in range(sum(spans['fold'][level][:1]),sum(spans['fold'][level]))];sn=[d['show_nodes'][i]for i in range(sum(spans['show'][level][:1]),sum(spans['show'][level]))]
   fs={d['cfv_slot'][node]for node in fn};ss={d['cfv_slot'][node]for node in sn};assert fs.isdisjoint(ss)and len(fs)==len(fn)and len(ss)==len(sn);checks+=len(fs)+len(ss)+3
   lr.append({'level':level,'fold_CTAs':len(fn),'show_CTAs':len(sn),'both_nonempty':bool(fn and sn),'CFV_rows_globally_disjoint':True,'both_players_output_extent_words':[stride*blocks for _ in nh],'per_row_owned_words':nh})
  rows.append({'id':item['fixture']['id'],'nodes':n,'CFV_rows':blocks,'CFV_stride':stride,'terminal_rows':len(slots),'scratch_rows':len(scratch),'overlap_levels':sum(x['both_nonempty']for x in lr),'levels':lr,'raw_sha256':item['sha256']})
 h.custody()
assert len(rows)==6
source=(h.REPO/'crates/solver/src/gpu/kernels.cu').read_bytes().decode('utf-8');a=source.index('extern "C" __global__ void up_fold(');b=source.index('extern "C" __global__ void up_show(');c=source.index('extern "C" __global__ void up_chance(');fold=source[a:b];show=source[b:c]
# CFV has only one write in each original kernel; no previous-CFV read or atomic.
for body in [fold,show]:assert body.count('cfv[')==1 and re.search(r'cfv\[[^;]+\]\s*=\s*',body)and 'atomic'not in re.sub(r'//[^\n]*','',body)
ref=h.read(ROOT/'comparisons/E118-three-pair-comparison/report.json')['performance']['baseline_full_cycle_ms'];activity=h.read(ROOT/'runs/D212-current-RAM-activity/report.json');h.save(H/'report.json',{'id':'D285','at':h.now(),'status':'pass_scoped_terminal_output_independence_next_graph_primitive','protocol_sha256':sys.argv[1],'checks':checks,'cases':rows,'kernel_CFV_store_only_source_checked':True,'all_original6_fullplan_hashes_verified':True,'original_phase_timings_not_used':True,'component_effort_reference_ms':ref,'minimum_component_effort_saving_ms':ref*.01,'current_activity_fold_sum_median_ms':sum(activity['median_activity_ms_by_family']['up_fold'].values())if'median_activity_ms_by_family'in activity else None,'limits':'Structural proof and prospective fork/join concept, not actual graph/ownership/capture failure cleanup/overlap/numerical/material/headroom/performance/adoption evidence. No new compiler/CUDA context/kernel/solve/source candidate. Component effort constant is a screening proxy, not a proven removable bound or fullcycle gain. Same CUDA functions must be retained; exact overlap primitive then full-size actual terminal component before considering production optimizer.','new_compiler_CUDA_context_kernel_solver_or_performance_samples':0,'optimizer_created_or_accepted':False});print(json.dumps({'checks':checks,'overlap_levels':[x['overlap_levels']for x in rows],'minimum_effort_saving_ms':ref*.01}),flush=True)
