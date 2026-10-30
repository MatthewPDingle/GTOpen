import sys,json
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
F=R/'runs/E087-transfer-preparation-failure';F.mkdir(exist_ok=False)
p=R/'runs/E087-prepare-transfer-control.py';raw=p.read_bytes()
(F/'original-preparer.py').write_bytes(raw)
assert not list((R/'runs/E087-transfer-control').iterdir())
old.save(F/'report.json',{'at':old.now(),'stage':'source preparation before compiler/native','error':'Windows default cp1252 rejected UTF8 copied source','H_empty_verified':True,'compiler_invocations':0,'native_invocations':0,'candidate_source_unchanged':True})
t=raw.decode().replace('H.mkdir(exist_ok=False)','assert H.is_dir() and not list(H.iterdir())')
t=t.replace('.read_text()',".read_text(encoding='utf-8')")
t=t.replace("shim=oldmod[oldmod.index('pub mod plan {'):oldmod.index('\\n',oldmod.index('pub mod plan {'))]","shim=oldmod[oldmod.index('pub mod plan {'):oldmod.index('\\nmod arena;')]")
t=t.replace(" assert (d/'arena.rs').read_text(encoding='utf-8').split('\\npub(super) fn e087_manual(')[0]==arena.rstrip('\\n')+'\\n' if False else True"," assert (d/'arena.rs').read_text(encoding='utf-8').startswith(arena+'\\n')")
(R/'runs/E087-prepare-transfer-control-r2.py').write_bytes(t.encode())
