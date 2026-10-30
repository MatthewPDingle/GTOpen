from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E086-resource';O=R/'runs/E086-resource-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'execute.py'),'64679c945e3ee0715b4d586a62595be50929ea56e71db0a52faea58baff0c51b'],O,'resource',old.env(),1000)
old.custody();print(old.read(H/'report.json')['status'],flush=True)
