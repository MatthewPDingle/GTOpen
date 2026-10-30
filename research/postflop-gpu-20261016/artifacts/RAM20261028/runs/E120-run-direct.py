import sys,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;H=ROOT/'runs/E120-kernel-control';h.pin(H/'protocol.json',sys.argv[1]);O=ROOT/'runs/E120-direct-audit';O.mkdir(exist_ok=False)
h.child([sys.executable,str(H/'execute.py'),sys.argv[1]],O,'capture',1200);h.custody()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());h.child([sys.executable,str(H/'audit.py')],O,'reader',1200);h.custody()
Q=ROOT/'comparisons/E120-kernel-control-root-check/report.json';q=h.read(Q);assert q['inventory']['comparison_pairs']==13180 and q['kernel_launches']==26360
dst=h.ar.DASHBOARD/'evidence'/Q.parent.name/Q.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(Q,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+Q.parent.name+'/'+Q.name,timeout=20)as z:assert z.read()==Q.read_bytes()
h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'protocol_sha256':sys.argv[1],'report_sha256':h.sha(Q),'new_speed_samples':0,'candidate_adopted':False});h.custody();print(q['status'],q['inventory'],flush=True)
