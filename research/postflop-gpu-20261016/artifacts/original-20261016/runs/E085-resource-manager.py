from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E085-resource-r2';O=R/'runs/E085-resource-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'execute.py'),'bd5fe745a3dc7cfb77596b16819f4c0f62631cce5cd299186c662f3e6a894ea0'],O,'resource',old.env(),1000)
old.custody()
print(old.read(H/'report.json')['status'],flush=True)
