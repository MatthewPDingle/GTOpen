import sys,json,shutil,importlib.util,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for path,digest in P['input_sha256'].items():h.pin(path,digest)
def publish(folder,names):
 for name in names:
  p=folder/name;dest=h.ar.DASHBOARD/'evidence'/folder.name/name;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert dest.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dest)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
verify();O=H/'execution';O.mkdir(exist_ok=False);spec=importlib.util.spec_from_file_location('bounded',H/'bounded_child.py');bounded=importlib.util.module_from_spec(spec);spec.loader.exec_module(bounded)
initial=bounded.memory();assert initial['available_physical']>=P['limits']['available_RAM_before_bytes'] and shutil.disk_usage(ROOT).free>=P['limits']['required_free_bytes'];h.save(O/'admission.json',{'at':h.now(),'actual_global_memory':initial,'X_free_bytes':shutil.disk_usage(ROOT).free,'no_native_children_yet':True})
publish(H,['protocol.json','source-review.json','audit.py'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);assert not any(x['id']=='D171' for x in s['experiments']);s['experiments'].append({'id':'D171','title':'Full canonical offset-width accuracy controls','kind':'diagnostic','status':'running','accepted':False,'correctness':'pending','measurement_epoch':'RAM20261028','stage':'Two sealed source probes, full CPU/device/lifecycle comparison','reason':'Original ranges/quality/stopping. Compare65 physicalarrays/fullCFV exactly; retain and losslessly decode32-bit offset payload against original64. No speed score.','evidence':[{'label':name,'url':'evidence/'+H.name+'/'+name} for name in ['protocol.json','source-review.json']]});s.update(updated_at=h.now(),active_experiment='D171',stage='Offset metadata full raw accuracy controls',activity='E094 staged off-tree; source/GPU/host boundary tests and every canonical state/lifecycle field before ordinary speed builds. E080/16 unchanged.');h.ar.atomic_json(h.ar.STATUS,s)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status())
 for arm in P['sequence']:
  h.child(P['rustc_commands'][arm],O,'rustc-'+arm,1200);verify();assert(H/(arm+'.ptx')).read_bytes() in(H/(arm+'.exe')).read_bytes();h.save(O/(arm+'.binary.json'),{'sha256':h.sha(H/(arm+'.exe')),'sealed_PTX_embedded':True})
 h.child([str(H/'candidate.exe'),'offset_','--nocapture','--test-threads=1'],O,'offset-boundaries',600);verify();raw=(O/'offset-boundaries.stdout.log').read_text(encoding='utf-8');assert 'test result: ok. 2 passed; 0 failed;' in raw
 for arm in P['sequence']:
  verify();h.ar.refuse_active(h.ar.live_status());output=H/(arm+'-output');output.mkdir(exist_ok=False);bounded.run([str(H/(arm+'.exe')),'--exact','postflop_complete_cycle','--ignored','--nocapture','--test-threads=1'],O,arm,h,P['limits'],H,output);verify()
 h.save(O/'native-complete.json',{'at':h.now(),'all_owned_children_terminal':True,'native_offset_boundary_tests':2,'full_canonical_arm_processes':2})
 h.child([sys.executable,str(H/'audit.py')],O,'audit',1800);verify();D=ROOT/'comparisons/D171-offset-raw-control';r=h.read(D/'report.json');h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(D/'report.json'),'performance_samples':0,'new_gain_accepted':False})
publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D171');item.update(status='measured',correctness='pass_full_canonical_state_and_private_format',stage='Original full state/locks/save/resume exact',reason='All6fullrecords/46checks,12wholeCPU/GPUframes,6queries/3saves/9futureEVpairs exact, actual lossless offset payload retained. Ordinary full-build/full-clock speed and broad resource qualification next.');item['evidence'].append({'label':'Full retained state result','url':'evidence/'+D.name+'/report.json'});s.update(updated_at=h.now(),stage='Offset metadata full state controls passed',activity='No speed gain accepted. E080/16 live. E094 must include real compile/JIT/packing/synchronization and pass ordinary complete-solve performance and later qualification.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({k:r[k] for k in ['status','full_records_exact','checkpoints_exact','reader_checks','exact_decoded_offset_values']}),flush=True)
