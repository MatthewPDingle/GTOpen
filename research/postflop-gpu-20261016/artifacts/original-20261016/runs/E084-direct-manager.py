from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E084-kernel-control'
O=R/'runs/E084-direct-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'execute.py'),'6ce4ceb303fe137c41a35a065dc4d9ac5d0d9962005fb0165b72bc0d42769f36'],O,'direct',old.env(),1200)
old.child([sys.executable,'-B',str(H/'audit.py')],O,'audit',old.env(),300)
old.custody()
print('Full raw GPU and reader controls passed',flush=True)
