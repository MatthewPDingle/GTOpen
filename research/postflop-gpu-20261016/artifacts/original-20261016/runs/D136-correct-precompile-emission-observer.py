"""Allow compiler loop unrolling in an emission observer before compilation."""
import ast
from pathlib import Path
import shutil
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
old.custody()
A=R/'runs/E085-resource';H=R/'runs/E085-resource-r2'
assert not(A/'execution').exists()and not(A/'probe.exe').exists()and not H.exists()
H.mkdir()
for n in ['baseline.cu','candidate.cu','probe.rs']:shutil.copyfile(A/n,H/n)
t=(A/'execute.py').read_text()
before="gates[arch+':streaming_stores_emitted_all4paths']=bt.count('st.global.cs.f32')==0 and ct.count('st.global.cs.f32')==4"
after="gates[arch+':streaming_store_emitted']=bt.count('st.global.cs.f32')==0 and ct.count('st.global.cs.f32')>=1"
assert t.count(before)==1
t=t.replace(before,after,1);ast.parse(t)
(H/'execute.py').write_text(t,encoding='utf-8',newline='\n')
old.save(H/'precompile-observer-correction.json',{'at':old.now(),
    'original_protocol_sha256':old.sha(A/'protocol.json'),
    'reason':'Static4store count assumed one store per template. Compiler unrolling may legally emit multiple stores per template. This is not a semantic/resource requirement. Source shows the same replacement in the shared helper for all four dispatch forms; direct corpus must cover all four. Emission observer requires actual streaming instruction presence and none in baseline.',
    'before':before,'after':after,'compiler_executions':0,'native_executions':0,
    'candidate_and_original_Rust_compiler_probe_bytes_unchanged':True,
    'resource_math_performance_gates_unchanged':True})
P=old.read(A/'protocol.json')
P.update(id='E085-resource-r2',at=old.now(),
    rustc_command=[x.replace(str(A),str(H))for x in P['rustc_command']],
    resource_gates=P['resource_gates'].replace('all4strategy streaming stores emitted','streaming strategy store emission present (static counts may vary with unrolling); shared helper source and direct controls cover all4dispatch forms'))
for p in [str(x)for x in A.iterdir()if x.is_file()]:P['input_sha256'].pop(p,None)
P['input_sha256'].update({str(p):old.sha(p)for p in [Path(__file__),A/'protocol.json',*[x for x in H.iterdir()if x.is_file()]]})
old.save(H/'protocol.json',P)
for p in H.iterdir():
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
    assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS)
    e=next(x for x in s['experiments']if x['id']=='E085')
    e['evidence'].extend([{'label':'Precompiler emission observer correction','url':'evidence/E085-resource-r2/precompile-observer-correction.json'},{'label':'Frozen resource protocol','url':'evidence/E085-resource-r2/protocol.json'}])
    s['updated_at']=old.now();old.ar.atomic_json(old.ar.STATUS,s)
print(old.sha(H/'protocol.json'),flush=True)
