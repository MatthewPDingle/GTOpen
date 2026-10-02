"""Preserve the actual passed pre-publication source/evidence, before hardening."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
sources={};results={}
for name in ('preflop-expected-training-checkpoint-control-v1-result.json','preflop-expected-training-cuda-control-v1-result.json'):
    path=root/name;value=json.loads(path.read_bytes());assert value['passed'] and not value['scientific_attempt']
    results[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    for name,h in value['inputs'].items():
        p=Path(name);assert hashlib.sha256(p.read_bytes()).hexdigest()==h,(name,h)
        if p.parent==root:
            destination=root/(p.stem+'-initial-staging.py');raw=p.read_bytes()
            if destination.exists():assert destination.read_bytes()==raw
            else:
                with destination.open('xb') as out:out.write(raw)
            sources[str(p)]=dict(snapshot=str(destination),sha256=h)
with (root/'preflop-expected-training-initial-preservation-v1.json').open('x',encoding='utf-8') as out:
    json.dump(dict(results=results,sources=sources,scope='Passed synthetic initial controls; no science'),out,indent=2)
print(json.dumps(dict(results=results,preserved_sources=len(sources))))
