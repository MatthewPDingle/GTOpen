import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
try:
    result = h.ar.main()
finally:
    h.custody()
raise SystemExit(result)
