from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E086-kernel-control';O=R/'runs/E086-direct-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'execute.py'),'7c23e9e875ee128ae08614dceb3968d3549a63bf255f080803081f69cd98cb96'],O,'direct',old.env(),1000)
old.child([sys.executable,'-B',str(H/'audit.py')],O,'audit',old.env(),300)
old.custody();print('425 chance pairs and raw reader passed',flush=True)
