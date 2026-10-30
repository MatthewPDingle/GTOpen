"""Scope diagnostic hook generation to the one constructor; preserve failure."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/D088-source';H=ROOT/'runs/D088-build-plan';assert not list(D.iterdir()) and not list(H.iterdir())
draft=D/'draft-r1';draft.mkdir();original=ROOT/'runs/D088-prepare.py';(draft/'prepare.py').write_bytes(original.read_bytes())
old.save(draft/'failure.json',{'at':old.now(),'outer_exec_chunk_id':'295c30','returncode':1,'failure':'Guard rejected whole-file build_lock_table occurrence count2: one constructor plus one lock-update method. No source files generated or activated, no compiler/native work.','repair':'Restrict every mod.rs instrumentation anchor to the new_with_budget constructor segment. Other methods remain byte-exact.','performance_or_solver_behavior_changed':False})
s=original.read_text(encoding='utf-8')
s=s.replace("D=ROOT/'runs/D088-source';D.mkdir();H=ROOT/'runs/D088-build-plan';H.mkdir()","D=ROOT/'runs/D088-source';H=ROOT/'runs/D088-build-plan';assert {p.name for p in D.iterdir()}=={'draft-r1'} and not list(H.iterdir())")
needle=" if name=='mod.rs':\n";assert s.count(needle)==1
s=s.replace(needle,needle+"  ctor_start=original.index('    pub fn new_with_budget(');ctor_end=original.index('    fn cfg(',ctor_start);s=original[ctor_start:ctor_end]\n",1)
needle=" (D/('baseline-'+name)).write_bytes"
assert s.count(needle)==1;s=s.replace(needle," if name=='mod.rs':s=original[:ctor_start]+s+original[ctor_end:]\n"+needle,1)
s=s.replace("old.REPO/'tools/postflop_autoresearch.py']","old.REPO/'tools/postflop_autoresearch.py',D/'draft-r1/prepare.py',D/'draft-r1/failure.json',ROOT/'runs/D088-prepare-r2.py']")
s=s.replace(' for src in directory.iterdir():\n  key=directory.name+\'/\'+src.name;',' for src in directory.rglob(\'*\'):\n  if not src.is_file():continue\n  key=directory.name+\'/\'+src.relative_to(directory).as_posix();')
(ROOT/'runs/D088-prepare-r2.py').write_text(s,encoding='utf-8',newline='\n')
print('Preparation guard failure preserved; constructor-scoped R2 ready.',flush=True)
