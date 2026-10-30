import sys,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==3;F=ROOT/'runs/D298-hand-word-fold';G=ROOT/'runs/E121-show-control';h.pin(F/'protocol.json',sys.argv[1]);h.pin(G/'protocol.json',sys.argv[2]);h.custody();O=ROOT/'runs/E121-direct-execution';O.mkdir(exist_ok=False)
h.child([sys.executable,str(ROOT/'runs/D298-execute-hand-word-fold.py'),sys.argv[1]],O,'fold',1200);h.custody()
h.child([sys.executable,str(G/'execute.py'),sys.argv[2]],O,'show',1200);h.custody()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());h.child([sys.executable,str(G/'audit.py')],O,'show-reader',1200);h.custody()
q=ROOT/'comparisons/E121-kernel-control-root-check/report.json';r=h.read(q);assert r['status']=='pass_scoped_encoded_hand_word_full_raw_equivalence'
dst=h.ar.DASHBOARD/'evidence'/q.parent.name/q.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(q,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+q.parent.name+'/'+q.name,timeout=20)as z:assert z.read()==q.read_bytes()
h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'fold_protocol_sha256':sys.argv[1],'show_protocol_sha256':sys.argv[2],'fold_report_sha256':h.sha(ROOT/'comparisons/D298-hand-word-fold/report.json'),'show_report_sha256':h.sha(q),'application_results_not_timing_samples':True,'candidate_adopted':False});h.custody();print('Both full direct terminal matrices passed.',flush=True)
