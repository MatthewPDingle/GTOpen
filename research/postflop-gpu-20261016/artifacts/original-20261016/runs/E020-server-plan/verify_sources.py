"""Read-only source/hash preflight; no build, native process, network or GPU call."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
pins=json.loads((HERE/'source-pins.json').read_text(encoding='utf-8'))
for name,want in pins.items():
    assert hashlib.sha256((REPO/name).read_bytes()).hexdigest()==want,name
print(f'All {len(pins)} E020 solver/server source pins match.')
