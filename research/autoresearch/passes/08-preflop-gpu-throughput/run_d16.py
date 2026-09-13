"""Guard the learning-only support bound; no GPU workload or state mutation."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
if __name__=='__main__':
    names=['d15-zero-bound.json','d15-verified.json','d11-work-census.json',
           'd10-small-v1.json','d10-large-v1.json']
    run07.run('d16-learning-bound-v1',[sys.executable,HERE/'d16_learning_bound.py'],180,
        [HERE/'D16_PROTOCOL.md',HERE/'d16_learning_bound.py',Path(__file__),*[HERE/'raw'/n for n in names]])
