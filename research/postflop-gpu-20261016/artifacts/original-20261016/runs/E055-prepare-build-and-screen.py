"""Derive current-epoch integrated build and fixed initial screen helpers."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
resource=ROOT/'runs/E055-resource/report.json';old.pin(ROOT/'runs/E055-resource/conditional-proof.json',old.read(resource)['conditional_read_proof_sha256'])
source=(ROOT/'runs/E054-root-control-build.py').read_text(encoding='utf-8').replace('E054','E055').replace("'39f249'","'5ab935'")
source=source.replace("old.REPO/'tools/postflop_autoresearch.py']","old.REPO/'tools/postflop_autoresearch.py',ROOT/'runs/E055-resource/conditional-proof.json',ROOT/'runs/E055-resource/conditional_proof.py']")
(ROOT/'runs/E055-root-control-build.py').write_text(source,encoding='utf-8',newline='\n')
source=(ROOT/'runs/E054-freeze-primary.py').read_text(encoding='utf-8').replace('E054','E055').replace('B177','B180').replace('B178','B181').replace('B179','B182')
needle="paths=[baseline,binary,manifest,build,control,"
assert source.count(needle)==1
source=source.replace(needle,"p['source_scope']='One readonly load placement: read3immutable discount floats only in unlocked own-node up_action. Same values/arithmetic/reduction/store order, allother branches/ABI/host/graphs/allocations/quality. Actual PTX proves unused roles skip reads.'\n"+needle)
(ROOT/'runs/E055-freeze-primary.py').write_text(source,encoding='utf-8',newline='\n')
print('E055 build and screen helpers prepared, fixed B180..B182 unused.',flush=True)
