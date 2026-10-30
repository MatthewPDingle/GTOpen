import json, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
assert len(sys.argv)==3
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    s.update(updated_at=ar.now(),stage=sys.argv[1],activity=sys.argv[2])
    ar.atomic_json(ar.STATUS,s)
print(sys.argv[1])
