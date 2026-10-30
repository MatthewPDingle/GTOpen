import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D256-constant-action';assert len(sys.argv)==2;P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(H/'output')],O,'probe',1200);verify();files=list((H/'output').iterdir());assert len(files)==6 and all(p.is_file()for p in files)and sum(p.stat().st_size for p in files)<=P['raw_reservation_bytes'];rows=[json.loads(x.split('D256_UNIT ',1)[1])for x in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'D256_UNIT 'in x];assert len(rows)==820 and rows[-1]['cases']==819 and rows[-1]['kernel_launches']==1638
 h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'raw_marker_summary':rows[-1],'raw_file_sha256':{str(p):h.sha(p)for p in files},'all_owned_native_children_terminal':True,'solver_or_speed_samples':0});h.child([sys.executable,str(H/'audit.py')],O,'audit',600);verify();report=ROOT/'comparisons/D256-stride-up-action-root-check/report.json';h.save(O/'reader-complete.json',{'at':h.now(),'report_sha256':h.sha(report),'all_owned_children_terminal':True,'solver_or_speed_samples':0})
p=report;dst=h.ar.DASHBOARD/'evidence'/report.parent.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+report.parent.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='D256');e.update(status='measured',stage='All819constant action cases passed',reason='All1638kernels exact: wholemutable/immutable/guards plus actualbefore/upload/postmoduleconstant andoriginalglobalimages. Same originalcompleteedgecorpus,20to19binding/actualdisjointregions. No solver/speed proof.');e['evidence'].append({'label':'Complete direct numerical raw result','url':'evidence/'+report.parent.name+'/'+p.name});s.update(updated_at=h.now(),active_experiment='E112',stage='Constant action direct controls passed; full solver controls next',activity=e['reason']+' E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.read(report)['status'],flush=True)
