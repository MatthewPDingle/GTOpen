"""Freeze ordinary CPU/GPU controls before any E049 native execution."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
F=ROOT/'runs/E049-final-build';assert old.read(F/'terminal.json')['returncode']==0
assert old.read(F/'complete.json')['all_compilers_terminal']
H=ROOT/'runs/E049-control-plan';H.mkdir()
script=r'''import json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old
ar=old.ar;ROOT=old.ROOT
assert len(sys.argv)==2;old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();assert not (ROOT/'gpu-run.lock').exists()
OUT=ROOT/'runs/E049-controls-execution';OUT.mkdir()
records=[]
for mode in P['order']:
 b=P['binaries'][mode];identity=P['ids'][mode]
 old.custody();ar.refuse_active(ar.live_status())
 # A test inventory is executable code too; serialize it, then let ar own
 # the lock for actual unit tests. No ignored benchmarks are admitted here.
 with ar.exclusive_lock(ROOT/'gpu-run.lock'):
  old.child([b['path'],'--list'],OUT,mode+'-inventory',old.env(),120)
 inventory=(OUT/(mode+'-inventory.stdout.log')).read_text(encoding='utf-8')
 listed=re.findall(r'^(.+): test$',inventory,re.M)
 assert len(listed)>30 and len(set(listed))==len(listed)
 cmd=[sys.executable,'-B','tools/postflop_autoresearch.py','--id',identity,'--title','E049 '+mode+' ordinary controls','--kind','validation','--binary',b['path'],'--build-manifest',b['manifest'],'--test','*','--not-ignored']
 old.child(cmd,OUT,identity,old.env(),1200)
 r=old.read(ROOT/'runs'/identity/'report.json');raw=ROOT/'runs'/identity/'stdout.log';old.pin(raw,r['stdout_sha256'])
 text=raw.read_text(encoding='utf-8')
 summary=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)
 assert len(summary)==1
 passed,failed,ignored,measured,filtered=map(int,summary[0])
 assert failed==measured==filtered==0 and passed+ignored==len(listed)
 if mode=='gpu':
  assert (passed,ignored)==(86,4)
  assert 'E049_PREDICATE cases=5600 ' in text
  assert re.search(r'E049_METADATA arena_i16=32 arena_f32=32 store=72',text)
  assert all(name in listed for name in P['required_new_tests'])
 assert r['status']=='measured' and r['returncode']==0
 assert r['binary_sha256']==b['sha256'] and r['binary_build_manifest']['sha256']==b['manifest_sha256']
 assert r['provenance']['source_sha256']==old.BASE
 records.append({'mode':mode,'id':identity,'passed':passed,'ignored':ignored,'inventory_total':len(listed),'stdout_sha256':old.sha(raw),'report_sha256':old.sha(ROOT/'runs'/identity/'report.json')})
 old.custody()
old.save(OUT/'complete.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'records':records,'status':'pass_provenance_controls','predicate_comparisons':5600,'fast_path_witnesses_required':True,'cpu_only_ordinary_passed':True,'gpu_ordinary_passed':True,'candidate_accepted':False,'limits':'Access-history and exact original predicate controls plus ordinary tests. No GPU timing, CPU performance, final codegen, or broader adoption qualification.'})
print(json.dumps({'status':'pass_provenance_controls','records':records,'complete_sha256':old.sha(OUT/'complete.json')}),flush=True)
'''
(H/'native.py').write_text(script,encoding='utf-8')
bins={}
paths=[H/'native.py',F/'complete.json',F/'terminal.json',ROOT/'runs/E049-build-plan/build-protocol.json',ROOT/'runs/E049-final-source/manifest.json',ROOT/'runs/E049-final-source/source-review.json',ar.REPO/'tools/postflop_autoresearch.py']
for mode,stem in [('cpu','E049-cpu-solver'),('gpu','E049-solver')]:
 b=ROOT/'binaries'/(stem+'.exe');m=b.with_suffix('.manifest.json');v=old.read(m)
 old.pin(b,v['binary_sha256']);assert v['source_sha256']==old.BASE|old.read(ROOT/'runs/E049-final-source/source-review.json')['source_sha256']
 bins[mode]={'path':str(b),'sha256':old.sha(b),'manifest':str(m),'manifest_sha256':old.sha(m)};paths.extend([b,m])
p={'id':'E049-controls','at':old.now(),'order':['cpu','gpu'],'ids':{'cpu':'V049-cpu','gpu':'V049-unit'},'binaries':bins,'required_new_tests':['store::provenance_tests::untouched_default_proof_covers_all_access_paths','gpu::arena::provenance_predicate_tests::untouched_and_exposed_predicates_match_original_scan'],'input_sha256':{str(x):old.sha(x) for x in paths},'ignored_execution':False,'performance_protocol':False}
for identity in p['ids'].values():assert not (ROOT/'runs'/identity).exists()
old.save(H/'protocol.json',p)
published={}
for directory in [H,F]:
 for src in directory.rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes()
  if dst.exists():assert dst.read_bytes()==data
  else:dst.write_bytes(data)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==data
  published[key]=old.sha(src)
old.save(H/'pre-native-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E049');e.update(stage='Builds terminal; CPU and GPU controls next',reason='Fresh CPU/feature/primary artifacts built. Frozen complete inventories and all nonignored CPU/GPU units; candidate-first zero-proof witnesses required.');e['evidence'].append({'label':'E049 control protocol','url':'evidence/E049-control-plan/protocol.json'});st.update(state='running',stage='E049 ordinary and provenance controls',activity='No performance run until both ordinary suites and intended no-scan path are verified.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'published':len(published)}),flush=True)
