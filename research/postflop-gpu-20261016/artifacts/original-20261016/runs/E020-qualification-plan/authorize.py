import json, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
base=ar.RESEARCH
here=Path(__file__).resolve().parent
prepared='d47d7d34bb35c795f96fad0f55454bfed2224d3c74adb6466efa088c3c063351'
assert ar.sha256(here/'prepared-manifest.json')==prepared
pins={
 'comparisons/E020-independent-review/manifest.json':'764ddfd51fc33450f1d179a7933b5380397bd6faa1a6baafe007891d446bb5cc',
 'comparisons/E020-independent-review/summary.md':'174e9859c23f4b7d6a869810593cb75a19bce876e9d4bb5d93208fad09178a66',
 'comparisons/E020-independent-review/validation.json':'ee2992d1066faeaf782f5276f7558521990f40a5cfbeece91cade970464fd438',
 'comparisons/E020-qualification-source-review/manifest.json':'71884c878a4b9dbe21ee3660e56c806f39873740f063ac315fe1e252b378a1a0',
 'comparisons/E020-qualification-source-review/review.md':'82f903e0bc79337c1e4073d679f42797f97eddbb3aa84c15af789c37e8095b0b',
 'comparisons/E020-qualification-source-review/validation.json':'dc973ee9831bf453a3d8f958d5d769495d33b02deb5d3e1a02572b0ce47772c3',
 'comparisons/D037-candidate-source-review/review.md':'e71ba50de427ed136612e977f091cbc7e23098865ae3d5ae2acbfb8936af19dc',
 'comparisons/D037-candidate-source-review/manifest.json':'d3a2601a509e8c6a1be338ea88aec49779bdb21d275cfb85a85f9ef0782cc3d5',
}
for path,h in pins.items():assert ar.sha256(base/path)==h,path
for path,h in json.loads((here/'prepared-manifest.json').read_text(encoding='utf-8'))['artifact_sha256'].items():
    assert ar.sha256(here/path)==h,path
assert ar.source_identity()['source_sha256']==json.loads((here/'primary-source.json').read_text(encoding='utf-8'))
record={'at':ar.now(),'candidate':'E020','primary_independent_pass':True,'source_review_pass':True,
 'qualification_script_review_pass':True,'prepared_manifest_sha256':prepared,
 'evidence_sha256':{str(base/path):h for path,h in pins.items()},
 'scope':'Build and separately gated qualification only. All-builds-ready required before any native control; independent broader and holdout audits required before cumulative. No acceptance or deployment.'}
with (here/'authorization.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(record,f,indent=2);f.write('\n')
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    s.update(updated_at=ar.now(),active_experiment=None,stage='Building E020 broader controls',
      activity='Primary and qualification-script audits passed. Compiling seven control binaries; no GPU tests or timings overlap compilation. Accepted gain remains 9.62%.')
    ar.atomic_json(ar.STATUS,s)
print(ar.sha256(here/'authorization.json'))
