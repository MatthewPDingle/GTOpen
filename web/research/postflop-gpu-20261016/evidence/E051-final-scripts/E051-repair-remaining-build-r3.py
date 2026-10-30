import sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E051-remaining-build-plan-r2';J=ROOT/'runs/E051-remaining-build-plan-r3';J.mkdir()
failure=ROOT/'runs/E051-remaining-build-r2/terminal.json';old.save(failure,{'at':old.now(),'returncode':1,'failure':'rustc could not resolve transitive dependencies: baseline solver Cargo-reported lib is in release root, so dependency path must use serde_json sibling deps directory. No native outcomes.','native_executions':0})
P=old.read(H/'protocol.json');P.update(id='E051-remaining-build-r3',at=old.now(),repair='Pin unchanged compiled artifacts; -L dependency uses correct serde_json deps directory for both arms.')
P['input_sha256']|={str(p):old.sha(p) for p in [H/'protocol.json',H/'build.py',failure,*list((ROOT/'runs/E051-remaining-build-r2').rglob('*'))] if p.is_file()}
src=(H/'build.py').read_text().replace("OUT=ROOT/'runs/E051-remaining-build-r2'","OUT=ROOT/'runs/E051-remaining-build-r3'").replace("Path(binding['solver']).parent","Path(binding['serde_json']).parent")
(J/'build.py').write_text(src,encoding='utf-8',newline='\n');P['input_sha256'][str(J/'build.py')]=old.sha(J/'build.py');old.save(J/'protocol.json',P)
for p in J.iterdir():
 dst=old.ar.DASHBOARD/'evidence'/J.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+J.name+'/'+p.name,timeout=20) as response:assert response.read()==p.read_bytes()
print(old.sha(J/'protocol.json'),flush=True)
