import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import common as h
if __name__=='__main__':
 h.custody()
 try:result=h.ar.main()
 finally:h.custody()
 raise SystemExit(result)
