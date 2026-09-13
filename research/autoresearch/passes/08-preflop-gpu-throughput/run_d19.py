"""One guarded immutable static-layout census."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
if __name__=='__main__':
    names=['d13-ranks-manifest.json','d13-fixed-ranks-v1.json.gz','c14-small-layout-v1.json','c14-large-layout-v1.json']
    run07.run('d19-static-cdf-v1',[sys.executable,HERE/'d19_static_cdf.py'],180,[HERE/'D19_PROTOCOL.md',HERE/'d19_static_cdf.py',Path(__file__),*[HERE/'raw'/n for n in names]])
