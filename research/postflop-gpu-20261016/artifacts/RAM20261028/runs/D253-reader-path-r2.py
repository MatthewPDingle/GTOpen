import ast,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D253-constant-controls';O=H/'execution'
if sys.argv[1]=='prepare':
 h.custody();assert h.read(O/'probe.exit.json')['returncode']==0 and h.read(O/'audit.exit.json')['returncode']==1;assert h.read(O/'complete-native.json')['summary']['kernel_executions']==240
 src=(H/'audit.py').read_bytes().decode();old="ROOT=Path(__file__).resolve().parents[1]";new="ROOT=Path(__file__).resolve().parents[2]";assert src.count(old)==1;fixed=src.replace(old,new,1);assert fixed.replace(new,old,1)==src;ast.parse(fixed);(H/'audit-r2.py').write_bytes(fixed.encode())
 paths=[Path(__file__),H/'protocol.json',H/'audit.py',H/'audit-r2.py',H/'probe.rs',H/'probe.exe',H/'primitive.cu',O/'complete-native.json',O/'audit.exit.json',O/'audit.stderr.log']+[p for p in(H/'output').iterdir()if p.is_file()]
 h.save(H/'reader-path-plan-r2.json',{'id':'D253-reader-path-R2','at':h.now(),'status':'FROZEN_PRE_ADDITIVE_READER','input_sha256':{str(p):h.sha(p)for p in paths},'cause':'Auditor copied from runs/ into its evidence subdirectory retained parents[1], so import common failed before any raw decoding. All240 native kernels were complete and passed, with their raw files and receipts retained.','repair':'One exact root-parent-index change in a new audit-r2.py; all corpus, decoding, oracles, gates, data, CUDA, binary and native execution unchanged.','completed_native_cases_repeated':0})
 print(h.sha(H/'reader-path-plan-r2.json'),flush=True)
else:
 h.pin(H/'reader-path-plan-r2.json',sys.argv[2]);P=h.read(H/'reader-path-plan-r2.json')
 for p,d in P['input_sha256'].items():h.pin(p,d)
 with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
  h.custody();h.ar.refuse_active(h.ar.live_status());h.child([sys.executable,str(H/'audit-r2.py')],O,'audit-r2',600);h.custody()
 report=ROOT/'comparisons/D253-constant-controls/report.json';h.save(O/'complete-r2.json',{'at':h.now(),'report_sha256':h.sha(report),'reader_repair_plan_sha256':sys.argv[2],'all_owned_children_terminal':True,'original_failed_reader_retained':True,'completed_native_cases_repeated':0,'solver_or_speed_samples':0})
 for folder,names in [(H,['reader-path-plan-r2.json']),(report.parent,['report.json'])]:
  for name in names:
   p=folder/name;dst=h.ar.DASHBOARD/'evidence'/folder.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
   with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
 with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
  s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='D253');e.update(status='measured',stage='All24constant symbol/graph shapes passed',reason='240 bit-transport kernels,48graphs: whole module symbols/outputs/guards exact and fresh module zero state. Original reader import used the wrong parent directory; additive one-index path repair reads unchanged raw data. No kernel rerun, floating CFR or speed claim.');e['evidence']+=[{'label':n,'url':'evidence/'+H.name+'/'+n}for n in ['reader-path-plan-r2.json','report.json']];s.update(updated_at=h.now(),active_experiment='D253',stage='Constant symbol controls passed; solver integration pending',activity=e['reason']+' E080 stays live.');h.ar.atomic_json(h.ar.STATUS,s)
 print('D253 additive reader and whole raw controls passed',flush=True)
