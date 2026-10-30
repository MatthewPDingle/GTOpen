from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E084-build-plan'
O=R/'runs/E084-build-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'build.py'),'8e2dfe76728dcc8b8e9f155e11c57c4b96d47b1b6317733de2c6f8c213a6f84d'],O,'build',old.env(),4000)
old.custody()
print('Both compilers terminal; accepted E080 restored',flush=True)
