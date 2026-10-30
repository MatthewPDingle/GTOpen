import json, shutil, sys
from pathlib import Path
sys.path.insert(0,r'X:\Dev\GTOpen-gpu-research-20261016\tools')
import postflop_autoresearch as ar
folder=ar.RESEARCH/'comparisons/E020-build-readiness-review'
pins={'readiness-r1-invalid.json':'77de1620eeea94bb4221661bdec677c5c7d1bce798bbe52aa314315c4cd79369',
 'readiness-r1-invalid.md':'54832648cf5035f59691f588edb053d463e6bd9f88c4e27ddfed34d23277700f'}
for name,h in pins.items():
    assert ar.sha256(folder/name)==h
    target=ar.DASHBOARD/'evidence/E020-build-readiness-review'/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert ar.sha256(target)==h
    else:shutil.copyfile(folder/name,target)
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    s=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    row=next(r for r in s['experiments'] if r['id']=='E020')
    row.update(updated_at=ar.now(),stage='Holdout build identity failed; isolated-build correction in review',
      details='Primary result remains provisional. R1 holdout compilation reused the E015 executable for both arms; direct embedded-CUDA inspection confirms the wrong candidate artifact. No holdout resource query or solve ran. Failed source review/build/readiness evidence is preserved. R2 uses fresh per-arm target directories plus embedded-source checks. Existing seven broader control binaries remain valid.')
    url='evidence/E020-build-readiness-review/readiness-r1-invalid.md'
    if not any(e['url']==url for e in row['evidence']):row['evidence'].append({'label':'Holdout build failure audit (no native runs)', 'url':url})
    s.update(updated_at=ar.now(),stage='Reviewing isolated holdout build correction',
      activity='Wrong-arm Cargo artifact reuse was caught before execution. Reviewing separate per-arm build directories and linked-source checks; no change to the frozen workload, accuracy or performance gates. Accepted gain remains 9.62%.')
    ar.atomic_json(ar.STATUS,s)
print('Published failed build-provenance evidence; no performance result changed.')
