from pathlib import Path
import sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
H=R/'runs/E085-build-plan';O=R/'runs/E085-build-manager'
O.mkdir(exist_ok=False)
old.child([sys.executable,'-B',str(H/'build.py'),'2a2b42f0b9ec85acadeed2215fead2388b40164aae14fe3c1ece5c433a5ab3f3'],O,'build',old.env(),4000)
old.custody()
print('Both full builds terminal; accepted E080 restored',flush=True)
