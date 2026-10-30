"""Publish the sealed CPU comparison before executing its one fixed campaign."""
from pathlib import Path
import shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as c
c.custody();assert not(R/'gpu-run.lock').exists();H=R/'runs/D115-parallel-plan-control';P=c.read(H/'protocol.json')
for p,h in P['input_sha256'].items():c.pin(p,h)
def publish(src,key):
 dst=c.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes()
 else:shutil.copyfile(src,dst)
 with urllib.request.urlopen(c.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
 return {'url':'evidence/'+key,'sha256':c.sha(src)}
pub=[]
for folder in [H,R/'runs/E071-source']:
 for p in folder.iterdir():
  if p.is_file():pub.append(publish(p,folder.name+'/'+p.name))
for name in ['D115-prepare.py','D115-execute.py','D115-root-check.py',Path(__file__).name]:pub.append(publish(R/'runs'/name,'D115-runners/'+name))
c.save(H/'pre-native-publication.json',{'at':c.now(),'protocol_sha256':c.sha(H/'protocol.json'),'files_http_byte_verified':pub,'compiler_and_native_executions':0})
with c.ar.exclusive_lock(c.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=c.read(c.ar.STATUS);assert not any(x['id']=='E071'for x in s['experiments'])
 s['experiments'].append({'id':'E071','at':c.now(),'updated_at':c.now(),'title':'Parallel preparation of independent GPU-plan arrays','kind':'candidate','status':'running','scope':'complete_run','stage':'D115 CPU field and capacity controls','correctness':'pending','accepted':False,'reason':'One fixed two-branch Rayon join for flop/turn CPU GPU-plan preparation; river remains sequential. Every original statement stays within its original ordered branch. No new explicit array allocation, CUDA, arithmetic, launch or quality change. CPU raw-field/capacity checks and actual material costs remain unproven. No speed result yet.','evidence':[{'label':'Frozen source and dependency review','url':'evidence/E071-source/source-review.json'},{'label':'Fixed CPU plan controls','url':'evidence/'+H.name+'/protocol.json'}]})
 s.update(updated_at=c.now(),state='running',goal_status='active',active_experiment='E071',stage='Checking E071 CPU preparation equivalence',activity='E051 remains deployed. E071 checks whether two independent CPU-plan groups can share the existing Rayon pool for flop/turn preparation. River remains sequential. One compiler and exactly 12 CPU cases compare all 53 fields and capacities before any solver activation or GPU speed screen.');c.ar.atomic_json(c.ar.STATUS,s)
O=R/'runs/D115-manager';assert not O.exists();O.mkdir()
try:
 c.child([sys.executable,'-B',str(R/'runs/D115-execute.py'),c.sha(H/'protocol.json')],O,'native',c.env(),3000)
 c.child([sys.executable,'-B',str(R/'runs/D115-root-check.py')],O,'root-replay',c.env(),300)
except BaseException as e:
 c.save(O/'failure.json',{'at':c.now(),'error':repr(e),'all_evidence_preserved':True,'candidate_accepted':False});raise
q=c.read(H/'report.json');assert q['status']=='pass_all53_CPU_fields_and_capacities'and q['all53_fields_exact']and q['all_capacities_exact']
for folder in [H,O]:
 for p in folder.iterdir():
  if p.is_file()and p.suffix in ['.json','.py','.rs','.log']:pub.append(publish(p,folder.name+'/'+p.name))
c.save(O/'complete.json',{'at':c.now(),'status':'CPU_controls_passed_no_solver_activation','report_sha256':c.sha(H/'report.json'),'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'files_http_byte_verified':pub,'GPU_or_complete_solve_performance_samples':0})
with c.ar.exclusive_lock(c.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=c.read(c.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E071');e.update(stage='CPU exactness passed; isolated solver builds next',correctness='CPU plan fields/capacities exact; integrated solver untested',reason='All 53 fields, every vector capacity, struct size and actual tree bytes match in 12 CPU cases and the retained accepted baseline. Fixed warmed CPU component results are descriptive only. No GPU or complete-solve performance claim; actual CPU/host peak/resource and full solver qualification remain required.',updated_at=c.now());e['evidence'].append({'label':'Complete CPU raw-record replay','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=c.now(),stage='E071 isolated solver build preparation',activity='E071 passed all 53 CPU plan fields and capacities in 12 cases. Prepare fixed integrated builds and exactly three alternating complete-solve pairs against accepted E051. The unrounded 1% cutoff and strict fixture guard stay unchanged. No CPU component result is a complete-solve speedup.');c.ar.atomic_json(c.ar.STATUS,s)
c.custody();print({'CPU_controls':'pass','checks':q['checks'],'raw_bytes':q['raw_bytes'],'canonical_component_added_ms':q['canonical_added_component_ms'],'next':'isolated builds and fixed primary3pairs','candidate_accepted':False},flush=True)
