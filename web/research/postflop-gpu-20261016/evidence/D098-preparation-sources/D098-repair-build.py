"""Preserve the pre-native SDK-header failure and repair only the capture harness."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();A=ROOT/'runs/D098-driver-machine-code';H=ROOT/'runs/D098-driver-machine-code-r2';assert not H.exists();H.mkdir()
P=old.read(A/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
assert old.read(A/'build/cl.exit.json')['returncode']==2
assert 'crt/host_defines.h' in (A/'build/cl.stdout.log').read_text()
assert not list((A/'execution').glob('capture.*')) and not list((A/'build').glob('*.exe'))
src=(A/'probe.cpp').read_text(encoding='utf-8');assert src.count('"down_eval"')==1
src=src.replace('"down_eval"','"copy_span"')
(H/'probe.cpp').write_text(src,encoding='utf-8',newline='\n')
nv=ROOT/'runs/D085-cupti-activity/vendor/cuda_nvcc_headers/cuda_nvcc-windows-x86_64-12.9.86-archive/include'
assert (nv/'crt/host_defines.h').exists()
P['command']=P['command'].replace(str(A/'probe.cpp'),str(H/'probe.cpp')).replace(str(A/'build'),str(H/'build'))
assert P['command'].count('cl /nologo')==1
P['command']=P['command'].replace('cl /nologo','cl /I'+str(nv)+' /nologo')
P.update(id=H.name,at=old.now(),preparation_revision='r2: add already-retained required NVCC header include, correct one function query from nonexistent down_eval to actual copy_span before any native execution. Original compile failure/bytes retained; no source/solver/PTX/arithmetic changes.')
P['input_sha256'].pop(str(A/'probe.cpp'));P['input_sha256'][str(H/'probe.cpp')]=old.sha(H/'probe.cpp')
for p in [A/'protocol.json',A/'probe.cpp',A/'execute.py',A/'build/cl.exit.json',A/'build/cl.stdout.log',A/'build/cl.stderr.log',Path(__file__)]+list(nv.rglob('*.h')):P['input_sha256'][str(p)]=old.sha(p)
(H/'execute.py').write_bytes((A/'execute.py').read_bytes());P['input_sha256'][str(H/'execute.py')]=old.sha(H/'execute.py')
old.save(H/'repair.json',{'at':old.now(),'failed_compile_terminal':True,'failed_compile_exit':2,'native_runs_before_repair':0,'preserved_artifact_sha256':{str(p):old.sha(p) for p in list((A/'build').glob('*'))+list((A/'execution').glob('*')) if p.is_file()},'actual_entry_names_verified_from_accepted_ptx_and_source':P['expected_entries'],'production_source_changed':False})
P['input_sha256'][str(H/'repair.json')]=old.sha(H/'repair.json');old.save(H/'protocol.json',P)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'revision':str(H),'native_runs_before_repair':0}),flush=True)
