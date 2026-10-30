import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/E051-remaining-build-plan';J=ROOT/'runs/E051-remaining-build-plan-r2';J.mkdir()
failure=ROOT/'runs/E051-remaining-build/terminal.json'
old.save(failure,{'at':old.now(),'returncode':1,'session':77035,'failure':'Artifact selector expected hashed libsolver-*.rlib; Cargo reports release/libsolver.rlib for --lib build. Cargo itself terminal0. No rustc probes/native executions started.','preserved_original_plan':True,'native_executions':0})
P=old.read(H/'protocol.json');Q=dict(P);Q.update(id='E051-remaining-build-r2',at=old.now(),repair='Accept Cargo-reported un-hashed libsolver.rlib. Reuse terminal0 freshly built/pinned baseline library; no native outcome exists.')
stage=ROOT/'runs/E051-remaining-build/baseline-feature-library';records=[json.loads(x) for x in (stage/'cargo.stdout.log').read_text().splitlines()];artifacts=[x for x in records if x.get('reason')=='compiler-artifact'];deps={f:old.sha(f) for x in artifacts for f in x.get('filenames',[]) if Path(f).is_file() and Path(f).suffix in ['.rlib','.rmeta','.lib','.dll']}
assert any(x.get('reason')=='build-finished' and x.get('success') for x in records)
solver=[x for x in artifacts if x['target']['name']=='solver'];assert len(solver)==1 and solver[0]['fresh'] is False and solver[0]['features']==['gpu','preflop-research']
assert old.read(stage/'cargo.exit.json')['returncode']==0
Q['input_sha256']=P['input_sha256']|deps|{str(p):old.sha(p) for p in [H/'protocol.json',H/'build.py',failure,*stage.glob('*')] if p.is_file()}
text=(H/'build.py').read_text();text=text.replace("OUT=ROOT/'runs/E051-remaining-build'","OUT=ROOT/'runs/E051-remaining-build-r2'")
text=text.replace("Path(p).name.startswith('lib'+name+'-')","(Path(p).name.startswith('lib'+name+'-') or Path(p).name=='lib'+name+'.rlib')")
text=text.replace(";assert not Path(P['baseline_feature_target']).exists()",'')
start=text.index(" stage=OUT/'baseline-feature-library'");end=text.index(" records=[json.loads",start)
text=text[:start]+" stage=ROOT/'runs/E051-remaining-build/baseline-feature-library'\n verify()\n"+text[end:]
# Keep original stage immutable; the r2 complete receipt goes in its new output.
text=text.replace("old.save(stage/'complete.json'","old.save(OUT/'baseline-feature-library-complete.json'")
(J/'build.py').write_text(text,encoding='utf-8',newline='\n');Q['input_sha256'][str(J/'build.py')]=old.sha(J/'build.py');old.save(J/'protocol.json',Q)
published={}
for p in J.iterdir():
 dst=old.ar.DASHBOARD/'evidence'/J.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+J.name+'/'+p.name,timeout=20) as response:assert response.read()==p.read_bytes()
 published[p.name]=old.sha(p)
old.save(J/'pre-compile-publication.json',{'at':old.now(),'artifact_sha256':published,'native_executions':0})
print(old.sha(J/'protocol.json'),flush=True)
