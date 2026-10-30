from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
assert len(sys.argv)==2
H=R/'runs/E084-primary-plan-r2'
old.pin(H/'protocol.json',sys.argv[1])
O=R/'runs/E084-primary-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'run.py'),sys.argv[1]],O,'primary',old.env(),2200)
old.custody()
print(old.read(R/'comparisons/E084-three-pair-comparison/report.json')['decision'],flush=True)
