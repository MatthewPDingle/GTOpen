import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D236-stride-eval';assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O=H/'execution';assert not O.exists()and not(H/'output').exists()and not(H/'probe.exe').exists();assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());O.mkdir();h.child(P['rustc_command'],O,'rustc',600);verify();data=(H/'probe.exe').read_bytes();assert all((H/(a+'.ptx')).read_bytes()in data for a in ['baseline','candidate']);h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe'),'both_sealed_PTX_embedded':True})
 h.child([str(H/'probe.exe'),str(H/'output')],O,'probe',1200);verify();rows=[json.loads(l.split('D236_UNIT ',1)[1])for l in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'D236_UNIT 'in l];assert len(rows)==1639 and rows[-1]['stage']=='complete'and rows[-1]['cases']==1638 and rows[-1]['kernel_launches']==3276
 files=[p for p in(H/'output').iterdir()if p.is_file()];assert len(files)==5 and sum(p.stat().st_size for p in files)<=P['raw_reservation_bytes'];h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'raw_marker_summary':rows[-1],'raw_file_sha256':{str(p):h.sha(p)for p in files},'all_owned_native_children_terminal':True,'performance_measured':False})
 h.child([sys.executable,str(H/'audit.py')],O,'audit',1200);verify();R=ROOT/'comparisons/D236-stride-eval-root-check/report.json';r=h.read(R);assert r['cases']==1638 and r['kernel_launches']==3276;h.save(O/'reader-complete.json',{'at':h.now(),'report_sha256':h.sha(R),'all_owned_children_terminal':True})
dest=h.ar.DASHBOARD/'evidence'/R.parent.name/R.name;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(R,dest)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+R.parent.name+'/'+R.name,timeout=20)as z:assert z.read()==R.read_bytes()
print(json.dumps({k:r[k]for k in ['status','cases','kernel_launches','checks','output_words_both_arms','immutable_words_both_arms','guard_words_both_arms']}),flush=True)
