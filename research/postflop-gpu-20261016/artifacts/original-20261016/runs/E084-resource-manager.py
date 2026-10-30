from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E084-resource'
O=R/'runs/E084-resource-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'execute.py'),'9faa124a6a6183c0b1f211c4aaddd256a6dc97cdbfd7632a643d818f4b36bc97'],O,'resource',old.env(),1000)
old.custody()
print(old.read(H/'report.json')['status'],flush=True)
