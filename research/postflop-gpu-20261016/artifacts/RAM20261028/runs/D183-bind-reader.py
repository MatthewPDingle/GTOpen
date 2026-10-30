import ast,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();H=ROOT/'runs/D183-plan-phase-diagnostic/visibility-adapter';old=h.read(H/'protocol.json');assert not(H/'execution').exists() and not(H/'probe.exe').exists()
new_files=[]
for kind in ['execute','audit']:
 parent=ROOT/'runs'/('D183-'+kind+'-visibility-adapter.py');code=parent.read_text();assert "H/'protocol.json'" in code;code=code.replace("H/'protocol.json'","H/'protocol-r2.json'")
 if kind=='execute':
  needle="str(ROOT/'runs/D183-audit.py')";assert code.count(needle)==1;code=code.replace(needle,"str(ROOT/'runs/D183-audit-visibility-adapter-r2.py')",1)
 script=ROOT/'runs'/('D183-'+kind+'-visibility-adapter-r2.py');assert not script.exists();script.write_text(code,encoding='utf-8',newline='\n');ast.parse(code);new_files.extend([parent,script])
P={**old,'at':h.now(),'pre_native_reader_route_correction':'Copied controller still named original pre-adapter reader. Source review caught this before either adapter compiler or any native output. Bind the already fixed visibility-aware reader; preserve old protocol/scripts. All plan/probe/source/order/fixtures/marks/fields/raw/flags/clock/math/gates remain literal unchanged. No observation repeated.','previous_pre_native_protocol_sha256':h.sha(H/'protocol.json'),'input_sha256':old['input_sha256']|{str(p):h.sha(p) for p in new_files+[Path(__file__),H/'protocol.json']}}
h.save(H/'protocol-r2.json',P);dst=h.ar.DASHBOARD/'evidence/D183-visibility-adapter/protocol-r2.json';assert not dst.exists();shutil.copyfile(H/'protocol-r2.json',dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/D183-visibility-adapter/protocol-r2.json',timeout=20) as response:assert response.read()==(H/'protocol-r2.json').read_bytes()
print(h.sha(H/'protocol-r2.json'),flush=True)
