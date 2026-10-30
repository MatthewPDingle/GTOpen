from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E085-kernel-control';O=R/'runs/E085-direct-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'execute.py'),'8d71f0d216c0b08e0a83dbe858de036ff6862ec97eb0f7a1c87fbf7584091b37'],O,'direct',old.env(),1000)
old.child([sys.executable,'-B',str(H/'audit.py')],O,'audit',old.env(),300)
old.custody()
print('819 raw action pairs and separate reader passed',flush=True)
