"""Append only the ignored timing harness; freeze the numerical implementation."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
f=ROOT/'crates/solver/src/preflop/gpu/static_cdf/ordinary/tests.rs'
old=f.read_bytes();assert old==(P/'c24_ordinary_tests.rs.txt').read_bytes()
f.write_bytes(old+(P/'c24_benchmark.rs.txt').read_bytes())
folder=P/'artifacts/c24-benchmark-v1';folder.mkdir(exist_ok=False)
mapping={}
for file,entry in json.loads((P/'artifacts/c24-integration-source-map.json').read_text()).items():
    target=ROOT/file;raw=target.read_bytes()
    if target!=f:assert hashlib.sha256(raw).hexdigest()==entry['sha256']
    out=folder/file;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
    mapping[file]={'sha256':hashlib.sha256(raw).hexdigest(),'archive':str(out.relative_to(P))}
(P/'artifacts/c24-benchmark-source-map.json').write_text(json.dumps(mapping,indent=2)+'\n')
