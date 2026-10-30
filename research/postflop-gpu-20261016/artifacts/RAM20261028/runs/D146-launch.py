import sys, os, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
instrumented = '--instrumented' in sys.argv
if instrumented:
    sys.argv.remove('--instrumented')
os.environ['POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE'] = '1' if instrumented else '0'
print('D146_ENV ' + json.dumps({'lifecycle_enabled': instrumented, 'RAYON_NUM_THREADS': os.environ.get('RAYON_NUM_THREADS')}), flush=True)
h.custody()
try:
    result = h.ar.main()
finally:
    h.custody()
raise SystemExit(result)
