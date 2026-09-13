"""One guarded, immutable D14 census."""
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'07-large-refinement-20260912'))
import run07
run07.RAW=HERE/'raw'
if __name__=='__main__':
    inputs=[HERE/'D14_PROTOCOL.md',HERE/'d14_warp_census.py',Path(__file__),
            *[HERE/'raw'/s for s in ('d13-fixed-ranks-v1.json.gz','d13-ranks-manifest.json',
                                     'd13-verified.json','d11-work-census.json')]]
    run07.run('d14-warp-inventory-v1',[sys.executable,HERE/'d14_warp_census.py'],180,inputs)
