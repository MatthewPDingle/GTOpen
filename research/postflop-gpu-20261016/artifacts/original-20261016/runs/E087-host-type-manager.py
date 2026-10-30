from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E087-host-type-check';O=R/'runs/E087-host-type-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'execute.py'),'fc5c2a830d44768331a71b5f6a7835f3501d794ca64fcafbd7b5e9028e8611b2'],O,'host',old.env(),1200)
old.custody();print('E087 exact arena source type/CPU checks complete',flush=True)
