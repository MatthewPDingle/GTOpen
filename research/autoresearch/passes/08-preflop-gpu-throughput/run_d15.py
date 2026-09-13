"""Guard the immutable host-only sparse scan bound."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
if __name__=='__main__':
    names=['d10-verified.json','d11-work-census.json']
    for f in ['small','large']:
        names.extend([f'd10-{f}-v1-witness.bin.gz',f'd10-{f}-v1-witness-manifest.json',f'd10-{f}-v1.json',f'c14-{f}-layout-v1.json'])
    run07.run('d15-zero-bound-v1',[sys.executable,HERE/'d15_zero_bound.py'],180,
        [HERE/'D15_PROTOCOL.md',HERE/'d15_zero_bound.py',Path(__file__),*[HERE/'raw'/n for n in names]])
