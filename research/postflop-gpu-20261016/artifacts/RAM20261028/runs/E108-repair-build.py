import ast,copy,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
old=ROOT/'runs/E108-build-plan';failed=ROOT/'runs/E108-final-build';P=h.read(old/'protocol.json');assert failed.is_dir()and not list(failed.iterdir())
assert [Path(x['target']).name for x in P['phases']]==['build-e107-final-feature','build-e107-final-primary']
h.save(failed/'preflight-failure.json',{'at':h.now(),'controller_returncode':1,'failed_script_sha256':h.sha(ROOT/'runs/E108-build.py'),'frozen_protocol_sha256':h.sha(old/'protocol.json'),'failure':'Inherited lowercase e107 build target paths referred to preserved prior candidate folders. Existing-target guard refused before source activation, Cargo compiler or native execution.','source_activations_compilers_or_native_runs':0,'accepted_source_main_live_protected_PTX_unchanged':True})
H=ROOT/'runs/E108-build-plan-r2';H.mkdir(exist_ok=False);script=ROOT/'runs/E108-build-r2.py';assert not script.exists();code=(ROOT/'runs/E108-build.py').read_text(encoding='utf-8').replace("H=ROOT/'runs/E108-build-plan'","H=ROOT/'runs/E108-build-plan-r2'").replace("OUT=ROOT/'runs/E108-final-build'","OUT=ROOT/'runs/E108-final-build-r2'")
needle="    for phase in P['phases']:\n        assert not Path(phase['target']).exists()";assert code.count(needle)==1;code=code.replace(needle,"    for phase in P['phases']:\n        assert Path(phase['target'])==ROOT/('build-e108-final-'+phase['id'])\n        assert not Path(phase['target']).exists()",1);ast.parse(code);script.write_bytes(code.encode('utf-8'))
Q=copy.deepcopy(P)
for phase in Q['phases']:
 phase['target']=str(ROOT/('build-e108-final-'+phase['id']));assert not Path(phase['target']).exists()
assert not(ROOT/'runs/E108-final-build-r2').exists()
Q['input_sha256']={k:v for k,v in Q['input_sha256'].items()if k!=str(ROOT/'runs/E108-build.py')}
for p in [Path(__file__),script,ROOT/'runs/E108-build.py',old/'protocol.json',failed/'preflight-failure.json']:Q['input_sha256'][str(p)]=h.sha(p)
Q.update(at=h.now(),preparation_revision='r2: fresh e108 target folders and own empty output/plan paths; exact source, compiler features/options/dependencies and output binary names unchanged. Original frozen protocol/script/preflight failure retained. No compiler/native/source activation before repair.')
h.save(H/'protocol.json',Q)
primary=ROOT/'runs/E108-prepare-primary.py';text=primary.read_text(encoding='utf-8');text=text.replace('E108-build-plan/protocol.json','E108-build-plan-r2/protocol.json').replace('E108-final-build','E108-final-build-r2').replace("ROOT/'runs/E108-build.py'","ROOT/'runs/E108-build-r2.py'");ast.parse(text);primary.write_bytes(text.encode('utf-8'))
pub=ROOT/'runs/E108-publish-primary.py';text=pub.read_text(encoding='utf-8').replace("'E108-final-build'","'E108-final-build-r2'").replace('E108-build-plan/protocol.json','E108-build-plan-r2/protocol.json').replace('E108-final-build/complete.json','E108-final-build-r2/complete.json')
text=text.replace("'canonical_scope':", "'preserved_build_preflight_failure':{'path':str(ROOT/'runs/E108-final-build/preflight-failure.json'),'sha256':h.sha(ROOT/'runs/E108-final-build/preflight-failure.json'),'compilers_or_native_runs_before_repair':0},'canonical_scope':")
text=text.replace("P,Q,A,H/'report.json']", "ROOT/'runs/E108-final-build/preflight-failure.json',ROOT/'runs/E108-build-plan/protocol.json',P,Q,A,H/'report.json']")
text=text.replace('Twofreshordinary feature/primary builds use actualruntimeNVRTC/JIT', 'Build target existing-folder guard refused inheritede107paths beforeanycompiler/sourceactivation/native; exactsource/options retained with fresh e108folders in additiveR2,originalplan/script/failurerecord kept. Twofreshordinary feature/primary builds use actualruntimeNVRTC/JIT');ast.parse(text);pub.write_bytes(text.encode('utf-8'))
p=H/'protocol.json';dst=h.ar.DASHBOARD/'evidence'/H.name/p.name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
print(h.sha(H/'protocol.json'),flush=True)
