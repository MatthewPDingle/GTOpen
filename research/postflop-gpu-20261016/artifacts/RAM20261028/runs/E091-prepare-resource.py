import sys,json,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status());H=ROOT/'runs/E091-resource';H.mkdir(exist_ok=False)
reference=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs\E089-resource');shutil.copyfile(reference/'probe.rs',H/'reference-parent.rs');old=(H/'reference-parent.rs').read_text(encoding='utf-8')
code=old.replace('E089_RESOURCE','E091_RESOURCE').replace('["up_show"]','["down_action"]').replace('let dynamic=4*1326u32+16*1081u32;','let dynamic=0u32;').replace('same128threads_max1326hands','same128threads_no_dynamic_shared')
assert 'up_show'not in code and'4*1326'not in code;(H/'probe.rs').write_text(code,encoding='utf-8',newline='\n')
S=ROOT/'runs/E091-source';m=h.read(S/'manifest.json');n='crates/solver/src/gpu/kernels.cu';h.pin(m['owned'][n]['base'],h.custody()[n]);h.pin(m['owned'][n]['candidate'],m['candidate_owned_sha256'][n])
for v in['baseline','candidate']:shutil.copyfile(S/(v+'.cu'),H/(v+'.cu'))
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,stem in[('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',name+'='+str(deps/stem)]
cmd+=['-o',str(H/'probe.exe')]
files=[Path(__file__),ROOT/'runs/E091-resource-execute.py',H/'probe.rs',H/'reference-parent.rs',H/'baseline.cu',H/'candidate.cu',S/'manifest.json',S/'source-review.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json']+[p for p in deps.iterdir()if p.is_file()]
P={'id':'E091-resource','at':h.now(),'status':'FROZEN_PRE_COMPILER','measurement_epoch':'RAM20261028','GPU_uuid':'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee','rustc_command':cmd,'required_free_bytes':66*1024**3,'expected_entries':h.read(reference/'protocol.json')['expected_entries'],'input_sha256':{str(p):h.sha(p)for p in files},'scope':'Exactly one compiler and one no-launch resource process. Four NVRTC compilations, unchanged production flags, physical X output. Require unchanged other8 normalized entries/18parameterABI/barriers, no local/shared/occupancy/stack/max-thread/default-limit regression. Register values reported; alone no fail if all stated gates pass. No larger-code penalty or smaller-body requirement presumed. Any failed prerequisite closes the source form with no source/gate/sample rescue.'}
compile((ROOT/'runs/E091-resource-execute.py').read_text(encoding='utf-8'),'E091-resource-execute.py','exec');h.save(H/'protocol.json',P)
pub=[]
for p in H.iterdir():
 key=H.name+'/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
h.save(H/'publication.json',{'at':h.now(),'HTTP_verified_artifacts':pub,'protocol_sha256':h.sha(H/'protocol.json'),'native_or_compiler_children_started':0})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E091');x.update(stage='Compiled resource prerequisites',reason='Inspect compiled ABI, other entries and actual driver resource limits before launching application kernels. No correctness or speed result yet.');x.setdefault('evidence',[]).append({'label':'Frozen compiler prerequisite','url':'evidence/E091-resource/protocol.json'});s.update(updated_at=h.now(),stage='E091 compiler prerequisite',activity='Check the staged zero-reach action shortcut for compiled resource regressions before device numerical controls. E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(h.sha(H/'protocol.json'),flush=True)
