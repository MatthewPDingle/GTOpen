"""Complete unexecuted resource protocol after a missing legacy template field."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E051-source';H=ROOT/'runs/E051-resource';draft=H/'draft-r1';draft.mkdir()
assert not (H/'protocol.json').exists() and not (H/'execution').exists() and not (H/'probe.exe').exists()
src=ROOT/'runs/E051-prepare-resource.py';(draft/'prepare.py').write_bytes(src.read_bytes())
old.save(draft/'failure.json',{'at':old.now(),'exec_chunk_id':'cb3acc','returncode':1,'error':'KeyError expected_abi in legacy E047 protocol template','preparation_script_sha256':old.sha(src),'compiler_native_executions':0,'source_scope':'Candidate source/review and resource source/script written, no protocol sealed, publication, activation or outcome.','repair':'Derive expected ABI from current accepted C signature. Candidate/source-review/probe/runner bytes unchanged.'})
p1=old.read(ROOT/'runs/E048-resource/protocol.json')
base=(D/'baseline.cu').read_text(encoding='utf-8');start=base.index('extern "C" __global__ void up_action(');header=base[start:base.index('{',start)]
parameters=header.split('(',1)[1].rsplit(')',1)[0].split(',');abi=['u64' if '*' in x else 'u32' for x in parameters];assert len(abi)==20
p={'id':'E051-resource','at':old.now(),'status':'FROZEN_PRE_EXECUTION_NO_LAUNCH','preparation_revision':'R2 protocol field repair before any compiler/native outcome','source_manifest_sha256':old.sha(D/'manifest.json'),'changed_entries':['up_action'],'gpu_uuid':p1['gpu_uuid'],'expected_entries':p1['expected_entries'],'expected_abi':{'up_action':{'baseline':abi,'candidate':abi}},'rustc_command':[x.replace('E048-resource','E051-resource') for x in p1['rustc_command']],'input_sha256':{k:v for k,v in p1['input_sha256'].items() if Path(k).suffix in ['.rlib','.lib'] or Path(k).name in ['common.py','postflop_autoresearch.py','protected-main.json']},'fixed_gates':'Changed entry, exact originalABI/other8entries, no register/local/shared increase, no maxthreads/64/128/256occupancy decrease, fits limits. No numerical or speed work after any failure.'}
p['input_sha256'].update({str(x):old.sha(x) for x in [H/'execute.py',H/'probe.rs',H/'baseline.cu',H/'candidate.cu',D/'manifest.json',D/'source-review.json',draft/'failure.json',draft/'prepare.py',ROOT/'runs/D038-next-hypothesis-source/README.md',ROOT/'runs/E003.patch']})
old.save(H/'protocol.json',p)
published={}
for directory in [D,H]:
 for f in directory.rglob('*'):
  if not f.is_file():continue
  key=directory.name+'/'+f.relative_to(directory).as_posix();out=ar.DASHBOARD/'evidence'/key;out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_bytes(f.read_bytes())
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==f.read_bytes()
  published[key]=old.sha(f)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);assert not any(x['id']=='E051' for x in st['experiments']);st['experiments'].append({'id':'E051','title':'Independent strategy-store scheduling','kind':'candidate','status':'running','stage':'Frozen no-launch compiler/resource gate','reason':'One store-scheduling transform; same arithmetic/order, no new array/cache/qualifier/launch. Protocol preparation field error preserved; source unchanged and no native outcome.','evidence':[{'label':'D082/E051 source review','url':'evidence/E051-source/source-review.json'},{'label':'E051 resource protocol','url':'evidence/E051-resource/protocol.json'}]});st.update(state='running',stage='E051 compiler/resource prerequisite',activity='Test actual compiled scheduling/resource effect before raw numerical or timing work.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
old.custody();print(json.dumps({'candidate_sha256':old.sha(D/'candidate.cu'),'resource_protocol_sha256':old.sha(H/'protocol.json'),'published':len(published)}),flush=True)
