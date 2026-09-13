"""Guard the two-method host occupancy census after exact witness extraction."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
if __name__=='__main__':
    names=['d13-ranks-manifest.json','d13-fixed-ranks-v1.json.gz','d16-learning-bound.json']
    for fixture in ['small','large']:
        names.extend(f'd17-{fixture}-v1'+suffix for suffix in ['-manifest.json','-support.bin.gz','.json','-exit.json'])
        names.append(f'd10-{fixture}-v1.json')
    run07.run('d17-occupancy-v1',[sys.executable,HERE/'d17_occupancy.py'],180,
        [HERE/'D17_PROTOCOL.md',HERE/'d17_occupancy.py',Path(__file__),*[HERE/'raw'/n for n in names]])
