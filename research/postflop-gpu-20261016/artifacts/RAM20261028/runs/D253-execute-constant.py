import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D253-constant-controls';assert len(sys.argv)==2;P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(H/'output')],O,'probe',600);verify()
 rows=[json.loads(x.split('D253_CONTROL ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'D253_CONTROL 'in x];assert len(rows)==25 and rows[-1]['stage']=='complete'and rows[-1]['kernel_executions']==240;assert sum(p.stat().st_size for p in(H/'output').iterdir())<=P['raw_reservation_bytes'];h.save(O/'complete-native.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'summary':rows[-1],'raw_sha256':{str(p):h.sha(p)for p in(H/'output').iterdir()if p.is_file()},'all_owned_native_children_terminal':True})
 h.child([sys.executable,str(H/'audit.py')],O,'audit',600);verify();report=ROOT/'comparisons/D253-constant-controls/report.json';h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(report),'all_owned_children_terminal':True,'solver_or_speed_samples':0})
p=report;dst=h.ar.DASHBOARD/'evidence'/report.parent.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+report.parent.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='D253');e.update(status='measured',stage='All24constant symbol/graph shapes passed',reason='240 float-bit transport kernels,48captured graphs; actual distinct live modules/symbol regions,updated values,wholeoutputs/guards andfreshthirdmodulezeros exact. No floating-CFR/solver/speed proof.');e['evidence'].append({'label':'Whole symbol/graph/raw result','url':'evidence/'+report.parent.name+'/'+p.name});s.update(updated_at=h.now(),active_experiment='D253',stage='Constant primitive passed; solver integration pending',activity=e['reason']+' E080 stays live.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.read(report)['status'],flush=True)
