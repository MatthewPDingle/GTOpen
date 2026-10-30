import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/D183-plan-phase-diagnostic';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.save(O/'before.json',{'at':h.now(),'free_X_bytes':shutil.disk_usage(ROOT).free,'scope':'CPU-only source plan/Spot work; no CUDA APIs or kernels.'})
 h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe'),'compiler_terminal':True})
 for row in P['sequence']:
  verify();h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];out=H/row['id'];out.mkdir(exist_ok=False);h.child([str(H/'probe.exe'),str(out),row['order']],O,row['id'],1200);verify()
 h.child([sys.executable,str(ROOT/'runs/D183-audit.py'),sys.argv[1]],O,'audit',1200);verify()
 h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'report_sha256':h.sha(ROOT/'comparisons/D183-plan-phase-diagnostic/report.json'),'all_owned_children_terminal':True,'compiler_runs':1,'CPU_native_runs':3,'raw_reader_runs':1,'GPU_context_or_kernel_or_solver_runs':0,'candidate_accepted':False})
p=ROOT/'comparisons/D183-plan-phase-diagnostic/report.json';dst=h.ar.DASHBOARD/'evidence'/p.parent.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+p.parent.name+'/'+p.name,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D183');r=h.read(p);item.update(status='measured',stage='CPU phase and full-plan raw observation complete',correctness='all_original_plan_fields_byte_exact',reason='All18 plan pairs are byte-exact across3fixtures and iso on/off;14 phases measured. Component observations only, no complete-cycle savings or optimizer admitted.');item['evidence'].append({'label':'Every plan byte and phase measurements','url':'evidence/'+p.parent.name+'/'+p.name});s.update(updated_at=h.now(),active_experiment='D183',stage='Review dominant CPU plan phases',activity='D183 completed CPU-only observations with every plan field exact. Select a distinct source change only after reviewing measured phase costs and history. E080/16 unchanged.');h.ar.atomic_json(h.ar.STATUS,s)
r=h.read(p);print(json.dumps({'D183':r['status'],'full_plan_pairs':r['full_plan_pairs_exact'],'whole_bytes_compared':r['whole_pair_bytes_compared'],'primary_phase_totals':r['primary_iso_phase_median_sum_ms'],'source_unchanged':True}),flush=True)
