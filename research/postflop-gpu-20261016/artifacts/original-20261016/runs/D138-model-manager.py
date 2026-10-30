from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/D138-transfer-model';O=R/'runs/D138-model-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'execute.py'),'5626486cd9ef666f689042f267faefe171e0871d973cf3e55df0abca208509cf'],O,'model',old.env(),1800)
old.child([sys.executable,'-B',str(H/'audit.py')],O,'audit',old.env(),1000)
old.custody();print('D138 CPU model and full raw reader passed',flush=True)
