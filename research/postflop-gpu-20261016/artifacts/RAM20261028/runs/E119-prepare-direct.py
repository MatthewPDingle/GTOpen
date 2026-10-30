import ast, json, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D291-static-fold-control';H.mkdir(exist_ok=False)
parent=ROOT/'runs/D243-fold-copy-direct';P=h.read(parent/'protocol.json')
assert h.read(ROOT/'runs/D290-static-fold-native/report.json')['status']=='pass_scoped_native_default128_static_fold_ladder'
assert h.read(ROOT/'runs/D289-static-fold-PTX/report.json')['status']=='pass_scoped_default128_static7phase_PTX_ladder'
for name in ['audit.py','corpus.json']:shutil.copyfile(parent/name,H/name)
code=(parent/'probe.rs').read_bytes().replace(b'D243',b'D291');(H/'probe.rs').write_bytes(code)
shutil.copyfile(ROOT/'runs/D207-resident-resource/baseline-compute_120.ptx',H/'baseline.ptx')
shutil.copyfile(ROOT/'runs/E119-resource/execution/candidate-compute_120.ptx',H/'candidate.ptx')
executor=ROOT/'runs/D291-execute-static-fold.py';code=(ROOT/'runs/D243-execute-fold-copy.py').read_text(encoding='utf-8').replace('D243-fold-copy-direct','D291-static-fold-control').replace('D243','D291');ast.parse(code);executor.write_bytes(code.encode())
def sub(v):
 if isinstance(v,str):return v.replace('D243-fold-copy-direct','D291-static-fold-control').replace('D243','D291')
 if isinstance(v,list):return [sub(x)for x in v]
 if isinstance(v,dict):return {sub(k):sub(x)for k,x in v.items()}
 return v
P=sub(P);P['at']=h.now();P['id']='D291';P['status']='FROZEN_PRE_COMPILER_ENTIRE_ORIGINAL360CASE_DIRECT_CORPUS'
files=[Path(__file__),executor,parent/'protocol.json',parent/'probe.rs',parent/'audit.py',parent/'corpus.json',ROOT/'runs/E119-source/manifest.json',ROOT/'runs/E119-resource/report.json',ROOT/'runs/D289-static-fold-PTX/report.json',ROOT/'runs/D290-static-fold-native/report.json',ROOT/'epoch/common.py']+list(H.iterdir())
P['input_sha256']={str(p):h.sha(p)for p in files}
P['input_sha256'].update({p:d for p,d in h.read(parent/'protocol.json')['input_sha256'].items()if '\\reference\\accepted-e080-deps\\'in p})
P['failure']='Any genuine output/input/guard/numerical failure closes E119, no source/shape/width/architecture/helper/flags/quality/sample rescue. Mechanical reader repair preserves completed native cases. Full original corpus. Preliminary speed screen follows direct checks and ordinary tests; full raw lifecycle and broad qualification still required before adoption.'
assert h.sha(H/'corpus.json')==h.sha(parent/'corpus.json')
h.save(H/'protocol.json',P);h.custody();print(h.sha(H/'protocol.json'),flush=True)
