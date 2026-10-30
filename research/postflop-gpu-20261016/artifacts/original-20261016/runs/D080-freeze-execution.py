"""Seal buffered evidence IO and serialized standalone diagnostic execution."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D080-river-slot-headroom';R=H/'r2';R.mkdir()
s=(H/'probe.rs').read_text(encoding='utf-8')
assert s.count('let mut f=fs::File::create(path).unwrap();')==2
s=s.replace('let mut f=fs::File::create(path).unwrap();','let mut f=std::io::BufWriter::new(fs::File::create(path).unwrap());')
(R/'probe.rs').write_text(s,encoding='utf-8')
p=old.read(H/'protocol.json');p.update(id='D080-R2',at=old.now(),amendment='Before any compiler/native execution, buffer raw evidence writes to avoid millions of tiny file syscalls. Original source/protocol preserved. Numeric expressions, cases, timing/warmup/order and payload bytes unchanged; no outcome was seen.')
p['command']=[x.replace(str(H/'probe.rs'),str(R/'probe.rs')).replace(str(H/'probe.exe'),str(R/'probe.exe')) for x in p['command']]
p['cpu_input_sha256'][str(R/'probe.rs')]=old.sha(R/'probe.rs')
old.save(R/'protocol.json',p)
script=r'''import json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent.parent.parent/'small-gain-confirmation-plan'));import common as old
assert len(sys.argv)==2;old.pin(HERE/'execution-seal.json',sys.argv[1]);S=old.read(HERE/'execution-seal.json')
for p,h in S['input_sha256'].items():old.pin(p,h)
P=old.read(HERE/'protocol.json')
for k in ['cpu_input_sha256','dependency_artifact_sha256']:
 for p,h in P[k].items():old.pin(p,h)
old.custody();old.ar.refuse_active(old.ar.live_status())
OUT=HERE/'execution';assert not OUT.exists();assert not (HERE/'probe.exe').exists()
with old.ar.exclusive_lock(old.ROOT/'gpu-run.lock'):
 assert shutil.disk_usage(old.ROOT).free>=54*1024**3
 OUT.mkdir();old.child(P['command'],OUT,'rustc',old.env(),600)
 old.custody();old.ar.refuse_active(old.ar.live_status())
 old.save(OUT/'compiled.json',{'at':old.now(),'binary_sha256':old.sha(HERE/'probe.exe'),'protocol_sha256':old.sha(HERE/'protocol.json'),'all_compilers_terminal':True,'solver_executions':0,'production_source_unchanged':True})
 old.child([str(HERE/'probe.exe'),str(HERE.parent/'fixtures.json'),str(OUT/'raw')],OUT,'native',old.env(),240)
 old.custody()
 old.save(OUT/'complete.json',{'at':old.now(),'execution_seal_sha256':sys.argv[1],'binary_sha256':old.sha(HERE/'probe.exe'),'compiler_and_native_returncode':0,'accepted162_main_live_ptx_unchanged':True,'artifact_sha256':{str(x):old.sha(x) for x in OUT.rglob('*') if x.is_file()},'candidate_accepted':False})
print(json.dumps({'status':'D080_terminal_pending_assessment','complete_sha256':old.sha(OUT/'complete.json')}),flush=True)
'''
# HERE is runs/D080.../r2, so helper lives at HERE.parent.parent/small-gain...
script=script.replace("HERE.parent.parent.parent/'small-gain-confirmation-plan'","HERE.parent.parent/'small-gain-confirmation-plan'")
(R/'native.py').write_text(script,encoding='utf-8')
old.save(R/'execution-seal.json',{'id':'D080-R2-execution','at':old.now(),'input_sha256':{str(x):old.sha(x) for x in [R/'native.py',R/'protocol.json',R/'probe.rs',H/'fixtures.json',H/'protocol.json',H/'probe.rs']},'no_prior_compiler_native_execution':True,'no_production_activation':True})
published={}
for name in ['probe.rs','protocol.json','native.py','execution-seal.json']:
 src=R/name;key=H.name+'/r2/'+name;dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
 published[key]=old.sha(src)
old.save(R/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published})
print(json.dumps({'seal_sha256':old.sha(R/'execution-seal.json'),'protocol_sha256':old.sha(R/'protocol.json'),'published':len(published)}),flush=True)
