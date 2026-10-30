import ast,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D237-stride-canonical';parent=ROOT/'runs/D178-canonical-cache-control';S=ROOT/'runs/E109-source';R=ROOT/'runs/E109-resource';direct=ROOT/'comparisons/D236-stride-eval-root-check/report.json';review=h.read(H/'source-review.json');assert not(H/'protocol.json').exists()and not(H/'execution').exists()
original=ROOT/'runs/D237-prepare-canonical.py';source=original.read_bytes().decode('utf-8');tail=source[source.index('deps='):]
assert tail.count('D232-stride-showdown-audit/audit.exit.json')==1;tail=tail.replace('D232-stride-showdown-audit/audit.exit.json','D232-stride-showdown-audit/reader.exit.json',1)
tail=tail.replace('paths=[Path(__file__),','paths=[Path(__file__),original,',1)
old='assert not dst.exists();shutil.copyfile(p,dst)';assert tail.count(old)==1
tail=tail.replace(old,"\n  if dst.exists():assert dst.read_bytes()==p.read_bytes()\n  else:shutil.copyfile(p,dst)",1)
h.save(H/'preparation-error.json',{'at':h.now(),'original_preparer_sha256':h.sha(original),'phase':'Before protocol freeze or any compiler/native execution','error':'Pinned D232 reader exit receipt was mistakenly named audit.exit.json; actual terminal receipt is reader.exit.json. Reuse already-published identical direct report.','retained_prepared_file_sha256':{str(p):h.sha(p)for p in H.rglob('*')if p.is_file()},'source_PTX_harness_quality_cases_limits_unchanged':True,'completed_native_cases_repeated':0})
ast.parse(tail);exec(compile(tail,str(original)+'-metadata-tail','exec'),globals())
