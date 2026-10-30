import json,os,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
B=ROOT/'runs/E109-direct-batch';assert len(sys.argv)==2;h.pin(B/'protocol.json',sys.argv[1]);P=h.read(B/'protocol.json')
def verify():
 h.pin(B/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
 for x in P['stages']:
  H=Path(x['folder']);h.pin(H/'protocol.json',x['protocol_sha256']);q=h.read(H/'protocol.json')
  for p,d in q['input_sha256'].items():h.pin(p,d)
verify();reports=[]
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 for x in P['stages']:
  H=Path(x['folder']);q=h.read(H/'protocol.json');O=H/'execution';raw=Path(q['raw_output']);
  if q['family']=='fold':q.update(marker='D235_FOLD_UNIT ',native_environment={'D235_FOLD_KERNEL_CONTROL_DIR':str(raw)})
  if q['family']=='chance':q['report']=str(ROOT/'comparisons/D234-kernel-control/report.json')
  assert not O.exists()and not raw.exists()and not(H/'probe.exe').exists();assert shutil.disk_usage(ROOT).free>=q['required_free_bytes'];h.ar.refuse_active(h.ar.live_status());verify();O.mkdir()
  h.child(q['rustc_command'],O,'rustc',600);verify();data=(H/'probe.exe').read_bytes();assert all((H/(a+'.ptx')).read_bytes()in data for a in ['baseline','candidate']);h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe'),'both_sealed_PTX_embedded':True})
  previous={k:os.environ.get(k)for k in q['native_environment']};os.environ.update(q['native_environment'])
  try:h.child([str(H/'probe.exe'),str(raw)],O,'probe',1200)
  finally:
   for k,v in previous.items():
    if v is None:os.environ.pop(k,None)
    else:os.environ[k]=v
  verify()
  if q['family']=='fold':
   assert not(H/'probe.stdout.log').exists();shutil.copyfile(O/'probe.stdout.log',H/'probe.stdout.log');h.pin(H/'probe.stdout.log',h.sha(O/'probe.stdout.log'))
  text=(O/'probe.stdout.log').read_text(encoding='utf-8');rows=[json.loads(l.split(q['marker'],1)[1])for l in text.splitlines()if q['marker']in l];assert len(rows)==q['cases']+1 and rows[-1]['stage']=='complete';last=rows[-1];assert last['cases']==q['cases']and last['kernel_launches']==q['kernel_launches'];files=[p for p in raw.iterdir()if p.is_file()];assert len(files)==q['raw_file_count']and sum(p.stat().st_size for p in files)<=q['raw_reservation_bytes'];rawpins={str(p):h.sha(p)for p in files};h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':x['protocol_sha256'],'raw_marker_summary':last,'raw_file_sha256':rawpins,'all_owned_native_children_terminal':True,'performance_measured':False,'candidate_accepted':False})
  report=Path(q['report'])
  if q['family']=='fold':report.parent.mkdir(exist_ok=False)
  h.child(q['audit_command'],O,'audit',1200);verify();r=h.read(report);assert r['cases']==q['cases']and r['kernel_launches']==q['kernel_launches'];h.save(O/'reader-complete.json',{'at':h.now(),'report_sha256':h.sha(report),'all_owned_children_terminal':True});reports.append({'id':x['id'],'report':str(report),'sha256':h.sha(report),'cases':q['cases'],'launches':q['kernel_launches']})
  dest=h.ar.DASHBOARD/'evidence'/report.parent.name/report.name;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(report,dest)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+report.parent.name+'/'+report.name,timeout=20)as z:assert z.read()==report.read_bytes()
  print(x['id'],'raw controls passed',flush=True)
assert sum(x['cases']for x in reports)==P['expected_cases']and sum(x['launches']for x in reports)==P['expected_kernel_launches'];h.custody();h.save(B/'report.json',{'id':'E109-direct-batch','at':h.now(),'status':'pass_scoped_original_uptraining_chance_fold_raw_controls','protocol_sha256':sys.argv[1],'category_reports':reports,'cases':1604,'kernel_launches':3208,'all_owned_compilers_native_readers_terminal':True,'source_main_live_protected_PTX_unchanged':True,'new_NVRTC_or_performance_samples':0,'candidate_accepted':False,'limits':'Finite originalcorpuses,allactualimmutablebuffers/fulloutputs/guards andoriginalrawreaders. DoesnotcompleteBR/avgdirect/fullcanonical/ordinary/fullcycle/material/adoption qualification.'});print('All3direct groups passed; no speedgain/adoption.',flush=True)
