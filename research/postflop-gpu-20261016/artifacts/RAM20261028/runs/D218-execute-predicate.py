import collections,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D218-lock-map-boundaries';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();assert not(ROOT/'gpu-run.lock').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',1200);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe')});h.ar.refuse_active(h.ar.live_status());h.child([str(H/'probe.exe'),str(H/'metadata.json')],O,'probe',1200);verify()
M=h.read(H/'metadata.json');assert M['cases']==20 and M['constructor_pairs']==20 and M['update_pairs']==60 and len(M['records'])==80 and M['application_kernel_launches']==M['solver_iterations']==0
checks=0;flags=collections.Counter()
def req(v,label):
 global checks
 assert v,label;checks+=1
for i,r in enumerate(M['records']):
 req(r['case']==i//4 and r['stage']==('constructor' if i%4==0 else 'update'),'all original fixed states');locks=r['CPU_locks'];req(len(locks)<=1,'single-map extent');off=[-1]*r['node_count'];sigma=[]
 for entry in locks:off[entry['node']]=len(sigma);sigma.extend(entry['bits'])
 if not sigma:sigma=[0]
 expected=len(locks)==0;req(r['expected_absent']==expected,'CPU map presence independent of sigma length')
 for arm in ['baseline','candidate']:
  state=r[arm];req(state['offsets']==off and state['sigma_bits']==sigma,'every actual offset and sigma bit matches CPU map');req(state['wrapper_bytes']==4448 and not state['training_graphs_present'] and state['eval_graphs_present']==[False,False],'original layout/no graphs');req(state['absent']==(expected if arm=='candidate' else None),'actual candidate predicate')
 flags[expected]+=1
req(flags=={True:24,False:56},'both predicate branches and all empty-vector boundaries');logs=(O/'probe.stdout.log').read_text(encoding='utf-8');req(logs.count('D218_PTX baseline')==logs.count('D218_PTX candidate')==20,'all40 original sealed module bindings');req('D218_COMPLETE 20 cases 80 states no kernels' in logs,'native terminal marker')
report={'id':'D218','at':h.now(),'status':'pass_scoped_actual_lock_map_and_dummy_buffer_boundaries','protocol_sha256':sys.argv[1],'cases':20,'constructor_pairs':20,'update_pairs':60,'actual_state_pairs':80,'actual_absent_states':flags[True],'actual_nonempty_map_states':flags[False],'reader_checks':checks,'metadata_sha256':h.sha(H/'metadata.json'),'all_actual_offset_and_sigma_bits_match_CPU':True,'malformed_vectors_never_consumed_by_kernels':True,'application_kernel_launches':0,'solver_iterations':0,'source_activated':False,'performance_samples':0,'candidate_accepted':False,'limits':'Constructor and table-update boundary evidence only. Malformed lock vector lengths remain outside normal solver/API kernel inputs. Original partial upload error propagation is source-reviewed, not injected. No fullcanonical/paging/material/capacity/complete speed/adoption claim.'};h.save(H/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'all_owned_compiler_native_children_terminal':True,'report_sha256':h.sha(H/'report.json'),'source_main_live_protected_PTX_unchanged':True,'application_kernel_launches':0});verify()
for name in ['report.json','execution/complete.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D218');item.update(status='measured',stage='All80 actual predicate/table states passed',correctness='actual_map_dummy_buffer_boundaries_pass',reason='20constructor pairs/60updates,24absent and56nonempty-map states. All actual table words and flags match CPU maps. No solver kernels or speed score.');item.setdefault('evidence',[]).append({'label':'Actual boundary result','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),active_experiment='E106',stage='Direct kernels and host boundaries passed',activity='E106 passes8397direct pairs and80actual map/table states. Next original full canonical CPU/all66device state and lifecycle before complete-cycle speed. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({k:report[k] for k in ['status','cases','actual_state_pairs','reader_checks']}),flush=True)
