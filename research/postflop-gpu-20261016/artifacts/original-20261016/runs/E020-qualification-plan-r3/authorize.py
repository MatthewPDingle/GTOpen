import json, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
here=Path(__file__).resolve().parent
old=ar.RESEARCH/'runs/E020-qualification-plan/authorization.json'
assert ar.sha256(old)=='364775cadca51f63136784e92ca013792d1ab23dc521be47ba8b9a93ecb54a4f'
prepared='e2e1e7a896f70eb54107bf4d83c6d9334953bbcbfcc20d7ad5db94850121110d'
assert ar.sha256(here/'prepared-manifest.json')==prepared
record=json.loads(old.read_text(encoding='utf-8'))
pins={
 'comparisons/E020-qualification-r3-source-review/review.md':'d08656373e2d3fd2878008c8a81f8876897fe41d273c526d1ce1abd900402475',
 'comparisons/E020-qualification-r3-source-review/manifest.json':'58ec697416ddfb698f82fefb8dc6359ac1542b1b70a3b11eb21552f3c6df3dfd',
 'comparisons/E020-build-readiness-review/primary-and-broader-embedded-cuda.json':'f6945e25ca7176b7634a8120ad2dd8dc5952961f95de62c4b1ba31fd8384ed6b',
}
for path,h in pins.items():
    assert ar.sha256(ar.RESEARCH/path)==h,path
    record['evidence_sha256'][str(ar.RESEARCH/path)]=h
for path,h in record['evidence_sha256'].items():assert ar.sha256(Path(path))==h,path
for path,h in json.loads((here/'prepared-manifest.json').read_text(encoding='utf-8'))['artifact_sha256'].items():
    assert ar.sha256(here/path)==h,path
record.update(at=ar.now(),prepared_manifest_sha256=prepared,
 scope='R3 canonical holdout path binding only. Reuse seven valid broader builds; do not rerun build.py. New verified all-builds-ready is mandatory before native controls, then independent broader/holdout audits before cumulative. No acceptance or deployment.',
 supersedes_execution_authorization=str(old),invalid_prior_readiness_preserved=True)
with (here/'authorization.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(record,f,indent=2);f.write('\n')
print(ar.sha256(here/'authorization.json'))
