import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
os.environ['POSTFLOP_AUTORESEARCH_PROFILE']='1';h.custody()
try:code=h.ar.main()
finally:h.custody()
raise SystemExit(code)
