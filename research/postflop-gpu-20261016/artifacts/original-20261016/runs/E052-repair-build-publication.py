import sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();H=ROOT/'runs/E052-build-plan';P=old.read(H/'build-protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.save(H/'publication-failure.json',{'at':old.now(),'reason':'Raw native assessment and root replay directories shared a basename. Immutable public report collision detected before overwrite; no build/native solve started.','existing_root_public_report_preserved':True,'repair':'Distinct native and root publication prefixes; all existing evidence stays unchanged.'})
directories=[(H,H.name),(ROOT/'comparisons/E052-kernel-control','E052-kernel-control-root-check'),(ROOT/'runs/E052-kernel-control','E052-kernel-control-native'),(ROOT/'runs/E052-resource','E052-resource'),(ROOT/'comparisons/E052-resource-root-check','E052-resource-root-check')];published={}
for directory,prefix in directories:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.pdb'] or '__pycache__' in src.parts:continue
  key=prefix+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data,key
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-build-publication-r2.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'no_native_or_build_rerun':True,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E052');e.update(stage='Raw controls passed; fresh integrated builds',reason='328cases/656launches exact;1519952output words/2762740actual immutable words/1164920guards checked. Resource gate passed. Complete solve performance unmeasured.');e['evidence'] +=[{'label':'E052 root full-raw replay','url':'evidence/E052-kernel-control-root-check/report.json'},{'label':'E052 native complete raw assessment','url':'evidence/E052-kernel-control-native/report.json'},{'label':'E052 fixed build protocol','url':'evidence/E052-build-plan/build-protocol.json'}];st.update(updated_at=old.now(),stage='E052 fresh integrated builds',activity='Build fresh feature and GPU-only binaries. Restore acceptedE051 after each phase.');old.ar.atomic_json(old.ar.STATUS,st)
print(old.sha(H/'build-protocol.json'),flush=True)
