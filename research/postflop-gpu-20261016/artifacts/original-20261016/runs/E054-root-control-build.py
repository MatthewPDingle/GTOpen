"""Close exact raw-control receipt and freeze fresh E054 integrated builds."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
K=ROOT/'runs/E054-kernel-control';R=ROOT/'comparisons/E054-kernel-control-root-check/report.json';q=old.read(R)
assert q['status']=='pass_scoped_up_action_raw_equivalence' and q['cases']==819 and q['kernel_launches']==1638 and q['checks']==63899 and q['all_parent_child_cfv_rows_disjoint']
assert q['output_words_both_arms']==12375858 and q['immutable_words_both_arms']==5199114 and q['guard_words_both_arms']==10240828
for p,h in q['raw_file_sha256'].items():old.pin(p,h)
for label in ['rustc','probe']:
 e=old.read(K/'execution'/(label+'.exit.json'));assert e['returncode']==0 and e['error'] is e['cleanup'] is None
old.save(K/'execution/terminal.json',{'at':old.now(),'exec_chunk_id':'39f249','returncode':0,'all_children_terminal':True,'complete_sha256':old.sha(K/'execution/complete.json'),'root_report_sha256':old.sha(R),'no_native_rerun':True})
H=ROOT/'runs/E054-build-plan';H.mkdir();prior=ROOT/'runs/E053-build-plan';D=ROOT/'runs/E054-source'
(H/'build.py').write_text((prior/'build.py').read_text(encoding='utf-8').replace('E053','E054'),encoding='utf-8',newline='\n')
p=old.read(prior/'build-protocol.json');p.update(id='E054-final-build',at=old.now(),accepted_source_sha256=old.BASE,protected_main=str(ROOT/'runs/accepted-E051/protected-main.json'),owned={'crates/solver/src/gpu/kernels.cu':{'base':str(D/'baseline.cu'),'base_sha256':old.sha(D/'baseline.cu'),'candidate':str(D/'candidate.cu'),'candidate_sha256':old.sha(D/'candidate.cu')}})
p['phases']=[{**x,'target':x['target'].replace('e053','e054'),'outputs':{k:v.replace('E053','E054') for k,v in x['outputs'].items()}} for x in p['phases']]
paths=[H/'build.py',D/'manifest.json',D/'source-review.json',D/'baseline.cu',D/'candidate.cu',R,K/'protocol.json',K/'execution/complete.json',K/'execution/terminal.json',ROOT/'runs/E054-resource/report.json',ROOT/'comparisons/E054-resource-root-check/report.json',Path(p['protected_main']),ROOT/'runs/accepted-E051/common_e051.py',old.REPO/'tools/postflop_autoresearch.py']
p['input_sha256']={str(x):old.sha(x) for x in paths};old.save(H/'build-protocol.json',p)
published={}
for directory,prefix in [(H,H.name),(R.parent,R.parent.name),(K,'E054-kernel-control-native')]:
 for src in directory.rglob('*'):
  if not src.is_file() or src.suffix in ['.exe','.pdb'] or '__pycache__' in src.parts:continue
  key=prefix+'/'+src.relative_to(directory).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data,key
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as r:assert r.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-build-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E054');e.update(stage='819raw cases exact; fresh integrated builds',reason='1638launches;12,375,858output words,5,199,114actual immutable words and10,240,828guards exact. All parent/child rows disjoint. Speed remains unmeasured.');e['evidence'] +=[{'label':'E054 complete raw root replay','url':'evidence/E054-kernel-control-root-check/report.json'},{'label':'E054 fresh build protocol','url':'evidence/E054-build-plan/build-protocol.json'}];st.update(state='running',stage='E054 fresh integrated builds',activity='Compile fresh primary/feature binaries from exact one-store scheduling transform; restore acceptedE051 after every phase.',updated_at=old.now());old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'raw_checks':q['checks'],'published':len(published),'build_protocol_sha256':old.sha(H/'build-protocol.json'),'phases':[x['id'] for x in p['phases']]}),flush=True)
