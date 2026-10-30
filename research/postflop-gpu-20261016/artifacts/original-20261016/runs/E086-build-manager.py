from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E086-build-plan';O=R/'runs/E086-build-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'build.py'),'b563ba00a19f01fe439734fa3769dbe242540be3a36dc6304c1cec35965b7b5a'],O,'build',old.env(),4000)
old.custody();print('Fresh builds terminal; accepted E080 restored',flush=True)
