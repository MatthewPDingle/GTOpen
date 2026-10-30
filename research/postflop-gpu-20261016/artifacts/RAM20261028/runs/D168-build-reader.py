import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parent=ROOT/'runs/D166-canonical-compiler-control/audit.py';src=parent.read_text(encoding='utf-8');prefix=src[:src.index('excluded=')]
tail=(ROOT/'runs/D168-audit-tail.py').read_text(encoding='utf-8');result=prefix+tail;ast.parse(result)
out=ROOT/'runs/D168-audit.py';assert not out.exists();out.write_bytes(result.encode())
print('D168 reader uses exact retained D166 frame/byte decoders plus fixed3configuration comparisons.',flush=True)
