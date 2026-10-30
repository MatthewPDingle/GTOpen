import sys,json,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status());s=h.read(h.ar.STATUS)
assert not any(x['id']in['D142','D142R1']for x in s['experiments'])and not(ROOT/'runs/D142R1').exists()
assert h.read(ROOT/'runs/E090-initial-decision/decision.json')['decision']=='rejected'
H=ROOT/'runs/D142-profile-plan';H.mkdir(exist_ok=False);exe=ROOT/'binaries/E080-postflop_autoresearch.exe';mp=exe.with_suffix('.manifest.json');h.pin(exe,h.read(mp)['binary_sha256'])
cmd=[sys.executable,str(ROOT/'runs/D142-profile-launch.py'),'--id','D142R1','--title','D142 accepted E080 diagnostic profile with current RAM','--kind','diagnostic','--binary',str(exe),'--build-manifest',str(mp),'--test','postflop_complete_cycle']
files=[Path(__file__),ROOT/'runs/D142-profile-launch.py',ROOT/'runs/D142-execute.py',exe,mp,ROOT/'epoch/common.py',ROOT/'epoch/exact-anchor.json',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json',ROOT/'runs/E090-initial-decision/decision.json',h.REPO/'crates/solver/src/gpu/mod.rs',h.REPO/'crates/solver/tests/postflop_autoresearch.rs',h.REPO/'tools/postflop_autoresearch.py']
P={'id':'D142','at':h.now(),'status':'FROZEN_PRE_DIAGNOSTIC','measurement_epoch':'RAM20261028','command':cmd,'required_free_bytes':66*1024**3,'native_processes':1,'complete_fixtures':3,'additional_instrumented_iterations':3,'input_sha256':{str(p):h.sha(p)for p in files},'scope':'No source mutation, one full E080 suite then one extra synchronized diagnostic iteration after each fixture. Retain all observations, no repetitions/extensions/score pooling or hardware counters. E090 and prior failed mechanisms remain closed. All output on X.'}
h.save(H/'protocol.json',P);key=H.name+'/protocol.json';dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(H/'protocol.json',dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==(H/'protocol.json').read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D142','title':'Fresh E080 family profile with current RAM','kind':'diagnostic','status':'running','accepted':False,'correctness':'pending','stage':'Frozen diagnostic profile','reason':'One extra synchronized iteration after each fully checked solve. No source changes or speedup claim.','measurement_epoch':'RAM20261028','evidence':[{'label':'Frozen diagnostic plan','url':'evidence/'+key}]});s.update(updated_at=h.now(),active_experiment='D142',stage='Fresh E080 diagnostic profile',activity='E090 rejected. Profile the accepted implementation with the current RAM settings to guide a new mechanism.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
