"""Guard the immutable host-only pipeline resource and traffic screen."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
if __name__=='__main__':
    names=['d13-ranks-manifest.json','d13-fixed-ranks-v1.json.gz','d11-work-census.json']
    for f in ['small','large']:
        names.extend([f'c14-{f}-layout-v1.json',f'd10-{f}-v1.json',f'd10-{f}-v1-witness-manifest.json',f'd10-{f}-v1-witness.bin.gz'])
    run07.run('d18-pipeline-v1',[sys.executable,HERE/'d18_pipeline.py'],180,
        [HERE/'D18_PROTOCOL.md',HERE/'d18_pipeline.py',Path(__file__),*[HERE/'raw'/n for n in names]])
