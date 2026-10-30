from pathlib import Path
import ast
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
t=(R/'runs/E085-checkpoint.py').read_text().replace('E085','E086').replace('E086-resource-r2','E086-resource').replace('B283','B286')
t=t.replace('progress:closedD134/E083andE084withactualcomponent/fullsolveevidence','progress:closedE085withfixedcomplete-solveevidence')
ast.parse(t)
target=R/'runs/E086-checkpoint.py';assert not target.exists()
target.write_text(t,encoding='utf-8',newline='\n')
print(target,flush=True)
