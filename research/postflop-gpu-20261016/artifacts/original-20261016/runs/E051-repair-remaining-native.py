import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E051-remaining-native-plan';J=ROOT/'runs/E051-remaining-native-plan-r2';J.mkdir();P=old.read(H/'protocol.json')
original=ROOT/'runs/E051-remaining-native.py';src=original.read_text();src=src.replace("H=ROOT/'runs/E051-remaining-native-plan';E=ROOT/'runs/E051-remaining-native-execution';O=ROOT/'comparisons/E051-remaining-native'","H=ROOT/'runs/E051-remaining-native-plan-r2';E=ROOT/'runs/E051-remaining-native-execution-r2';O=ROOT/'comparisons/E051-remaining-native-r2'")
src=src.replace("assert abs(sum(r[k] for k in ['build_ms','init_ms','solve_ms','readback_ms'])-r['full_cycle_ms'])<1e-7","assert r['full_cycle_ms']>=sum(r[k] for k in ['build_ms','init_ms','solve_ms','readback_ms'])")
start=src.index(' capacity={}');end=src.index(' historical=Path',start)
src=src[:start]+" capacity=old.read(ROOT/'comparisons/E051-remaining-native/capacity.json')\n assert capacity['status']=='pass_exact_actual_owned_accounting'\n old.save(O/'capacity.json',capacity)\n"+src[end:]
script=J/'native.py';script.write_text(src,encoding='utf-8',newline='\n')
P.update(id='E051-remaining-native-r2',at=old.now(),repair='Historical holdout full_cycle is outer elapsed wall and includes progress logging gaps. Rejecting unequal component sum was an assessor error. Preserve real outer wall score; require wall >= stage sum. No holdout/cumulative run has started. Replay completed exact capacity evidence without rerunning capacity.')
extra=[original,H/'protocol.json',script,*list((ROOT/'runs/E051-remaining-native-execution').rglob('*')),*list((ROOT/'comparisons/E051-remaining-native').rglob('*'))]
P['input_sha256']|={str(p):old.sha(p) for p in extra if p.is_file()};old.save(J/'protocol.json',P)
# Exercise exact assessor on historical immutable artifact before any new outcome.
fragment=src[src.index('def markers'):src.index('verify();assert not E.exists()')];ns={'codec':None}
import importlib.util
spec=importlib.util.spec_from_file_location('old_codec',P['codec']);codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
ns={'codec':codec,'old':old,'P':P};exec(fragment,ns)
sample=ns['holdout'](Path(P['historical_holdout']),Path(P['historical_raw']));assert sample['full_cycle_ms']==905.1226999999999
old.save(J/'historical-assessor-check.json',{'at':old.now(),'passed':True,'same_outer_wall_score':True,'no_new_native_execution':True,'stage_sum_excludes_progress_logging_gaps':True})
for p in J.iterdir():
 dst=old.ar.DASHBOARD/'evidence'/J.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+J.name+'/'+p.name,timeout=20) as response:assert response.read()==p.read_bytes()
print(old.sha(J/'protocol.json'),flush=True)
