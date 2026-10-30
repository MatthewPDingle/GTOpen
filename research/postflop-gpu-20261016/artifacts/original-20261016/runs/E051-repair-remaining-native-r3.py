import sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E051-remaining-native-plan-r2';J=ROOT/'runs/E051-remaining-native-plan-r3';J.mkdir()
old.save(H/'launch-failure.json',{'at':old.now(),'returncode':1,'failure':'Moving native.py into a nested plan directory broke its relative ROOT calculation; import failed before any native launch.','native_executions':0})
P=old.read(H/'protocol.json');script=J/'native.py';src=(H/'native.py').read_text().replace('ROOT=Path(__file__).resolve().parent.parent',"ROOT=Path(r'S:\\GTOpen-research\\postflop-gpu-20261016')").replace("H=ROOT/'runs/E051-remaining-native-plan-r2';E=ROOT/'runs/E051-remaining-native-execution-r2';O=ROOT/'comparisons/E051-remaining-native-r2'","H=ROOT/'runs/E051-remaining-native-plan-r3';E=ROOT/'runs/E051-remaining-native-execution-r3';O=ROOT/'comparisons/E051-remaining-native-r3'")
script.write_text(src,encoding='utf-8',newline='\n');P.update(id='E051-remaining-native-r3',at=old.now(),repair='Explicit absolute artifact root; previous nested-path import failed before launch. Preserve all fixed samples/rules and completed capacity evidence.')
P['input_sha256']|={str(p):old.sha(p) for p in [script,H/'native.py',H/'protocol.json',H/'launch-failure.json']};old.save(J/'protocol.json',P)
for p in J.iterdir():
 dst=old.ar.DASHBOARD/'evidence'/J.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+J.name+'/'+p.name,timeout=20) as response:assert response.read()==p.read_bytes()
print(old.sha(J/'protocol.json'),flush=True)
