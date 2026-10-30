import json, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
here=Path(__file__).resolve().parent
prepared='cac3399c20ce42c85fd0f2074f41cbb93d790ebe345673808857f46892f43340'
assert ar.sha256(here/'prepared-manifest.json')==prepared
pins={
 'comparisons/E020-independent-review/manifest.json':'764ddfd51fc33450f1d179a7933b5380397bd6faa1a6baafe007891d446bb5cc',
 'comparisons/E020-independent-review/summary.md':'174e9859c23f4b7d6a869810593cb75a19bce876e9d4bb5d93208fad09178a66',
 'comparisons/E020-holdout-source-review/review.md':'bb4476bd1c33a81b6591ebd784134ff1623a6cfee194ea37a09aa8f14cf0e507',
 'comparisons/E020-holdout-source-review/manifest.json':'6a0b54474f31239146e9ff266869573e99266a7616089cf4f05314c03301a2cd',
}
for path,h in pins.items():assert ar.sha256(ar.RESEARCH/path)==h,path
assert not (ar.RESEARCH/'gpu-run.lock').exists()
assert json.loads((ar.RESEARCH/'runs/E020-qualification-build/complete.json').read_text(encoding='utf-8'))['status']=='pass'
record={'at':ar.now(),'candidate':'E020','phase':'build','prepared_manifest_sha256':prepared,
 'primary_audit_pass':True,'holdout_source_review_pass':True,
 'required_evidence':[{'path':str(ar.RESEARCH/path),'sha256':h} for path,h in pins.items()],
 'scope':'Build-only authorization; all-builds-ready does not yet exist. No native GPU testing, acceptance or deployment.'}
with (here/'build-authorization.json').open('x',encoding='utf-8',newline='\n') as f:
    json.dump(record,f,indent=2);f.write('\n')
print(ar.sha256(here/'build-authorization.json'))
