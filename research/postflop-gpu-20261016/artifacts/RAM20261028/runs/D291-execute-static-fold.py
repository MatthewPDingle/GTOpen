import json,os,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D291-static-fold-control';assert len(sys.argv)==2;P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();assert not O.exists()and not(H/'probe.exe').exists();assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());O.mkdir();h.child(P['rustc_command'],O,'rustc',600);verify();data=(H/'probe.exe').read_bytes();assert all((H/(a+'.ptx')).read_bytes()in data for a in ['baseline','candidate']);h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe'),'both_sealed_PTX_embedded':True})
 previous={k:os.environ.get(k)for k in P['native_environment']};os.environ.update(P['native_environment'])
 try:h.child([str(H/'probe.exe')],O,'probe',1200)
 finally:
  for k,v in previous.items():
   if v is None:os.environ.pop(k,None)
   else:os.environ[k]=v
 verify();rows=[json.loads(l.split(P['marker'],1)[1])for l in(O/'probe.stdout.log').read_text().splitlines()if P['marker']in l];assert len(rows)==361 and rows[-1]['stage']=='complete'and rows[-1]['cases']==360 and rows[-1]['kernel_launches']==720;files=list(Path(P['raw_output']).iterdir());assert len(files)==5 and all(p.is_file()for p in files)and sum(p.stat().st_size for p in files)<=P['raw_reservation_bytes'];h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'raw_marker_summary':rows[-1],'raw_file_sha256':{str(p):h.sha(p)for p in files},'all_owned_native_children_terminal':True,'performance_measured':False});report=Path(P['report']);report.parent.mkdir(exist_ok=False);h.child(P['audit_command'],O,'audit',1200);verify();r=h.read(report);assert r['cases']==360 and r['kernel_launches']==720;h.save(O/'reader-complete.json',{'at':h.now(),'report_sha256':h.sha(report),'all_owned_children_terminal':True})
dst=h.ar.DASHBOARD/'evidence'/report.parent.name/report.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(report,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+report.parent.name+'/'+report.name,timeout=20)as z:assert z.read()==report.read_bytes()
print(json.dumps({k:r[k]for k in ['status','cases','kernel_launches','checks','output_words_both_arms','immutable_words_both_arms','guard_words_both_arms']}),flush=True)
