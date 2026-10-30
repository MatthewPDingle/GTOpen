import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D247-cluster-controls';assert len(sys.argv)==2;P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();assert not O.exists()and not(H/'output').exists()and not(H/'probe.exe').exists();O.mkdir()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();assert(H/'primitive.ptx').read_bytes()in(H/'probe.exe').read_bytes();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe'),'exact_sealed_PTX_embedded':True})
 h.child([str(H/'probe.exe'),str(H/'output')],O,'probe',600);verify();rows=[json.loads(l.split('D247_CONTROL ',1)[1])for l in(O/'probe.stdout.log').read_text().splitlines()if'D247_CONTROL 'in l];assert len(rows)==133 and rows[-1]['stage']=='complete'and rows[-1]['cases']==132 and rows[-1]['kernel_launches']==660;files=list((H/'output').iterdir());assert len(files)==2 and all(p.is_file()for p in files)and sum(p.stat().st_size for p in files)<=P['raw_reservation_bytes'];h.save(O/'complete-native.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'native_marker_summary':rows[-1],'raw_sha256':{str(p):h.sha(p)for p in files},'all_owned_native_children_terminal':True,'solver_or_speed_samples':0})
 h.child([sys.executable,str(H/'audit.py')],O,'audit',600);verify();R=ROOT/'comparisons/D247-cluster-controls/report.json';h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(R),'all_owned_children_terminal':True,'no_solver_or_speed_sample':True})
dst=h.ar.DASHBOARD/'evidence'/R.parent.name/R.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(R,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+R.parent.name+'/'+R.name,timeout=20)as z:assert z.read()==R.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='D247');e.update(status='measured',stage='Original132raw/graphcases passed',reason='660actualclusterkernel executions,132singlekernelgraphs and4nonvacuousreplayspercase;wholepeeroutputs/actualimmutableinputs/allguards exact. Primitiveintegertransport only; nofloatingCFR/scan/speedclaim.');e['evidence'].append({'label':'Complete peer/lifetime/graph raw result','url':'evidence/'+R.parent.name+'/'+R.name});s.update(updated_at=h.now(),active_experiment='D247',stage='Cluster primitive passed; poker source feasibility pending',activity=e['reason']+' E080remainslive,nooptimizeradmitted.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.read(R)['status'],flush=True)
