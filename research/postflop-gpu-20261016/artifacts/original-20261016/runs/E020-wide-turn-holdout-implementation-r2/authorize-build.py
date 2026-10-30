import json, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
here=Path(__file__).resolve().parent
old=ar.RESEARCH/'runs/E020-wide-turn-holdout-implementation/build-authorization.json'
assert ar.sha256(old)=='8bdd6c6306f63e53b87bda7eca2bb7f8aa690e09e21657f08b3747165366d5ef'
prepared='3e55bec74defdbc3a5e87d299c08722bccfbfc9d388c2908f8e7f5273cafac91'
assert ar.sha256(here/'prepared-manifest.json')==prepared
record=json.loads(old.read_text(encoding='utf-8'))
pins={
 'comparisons/E020-holdout-r2-source-review/review.md':'0032fd514c2cf0ab139013feb743c61343b1e5fcdb6cf9c5e763019a708548e0',
 'comparisons/E020-holdout-r2-source-review/manifest.json':'3eb7f3ba4b082551d739f4bc40c2babd9219a63e05f70d84cc1fef9e3f10334e',
 'comparisons/E020-build-readiness-review/readiness-r1-invalid.json':'77de1620eeea94bb4221661bdec677c5c7d1bce798bbe52aa314315c4cd79369',
}
for path,h in pins.items():
    assert ar.sha256(ar.RESEARCH/path)==h,path
    record['required_evidence'].append({'path':str(ar.RESEARCH/path),'sha256':h})
for item in record['required_evidence']:assert ar.sha256(Path(item['path']))==item['sha256']
assert not (ar.RESEARCH/'gpu-run.lock').exists()
record.update(at=ar.now(),prepared_manifest_sha256=prepared,
 scope='R2 build-only correction: separate initially absent arm target directories and embedded-source guards. R1 remains invalid and preserved. No numerical protocol changes or native test authorization; new qualification R3 readiness required.')
with (here/'build-authorization.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(record,f,indent=2);f.write('\n')
print(ar.sha256(here/'build-authorization.json'))
