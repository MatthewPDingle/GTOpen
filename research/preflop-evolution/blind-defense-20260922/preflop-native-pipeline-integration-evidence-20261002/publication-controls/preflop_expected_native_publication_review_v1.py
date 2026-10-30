"""Review exact publication and small published-path controls; append owned journal."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

STAGE=Path(__file__).resolve().parent
ROOT=Path(r'T:\Dev\GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
DEST=OUT/'preflop-native-pipeline-integration-evidence-20261002'
PROFILE=Path(r'S:\GTOpen-research\preflop-expected-native-cycle-profile-v1')
EXPECTED_PUBLICATION='b9f05878a3ffb61422642b10b3d4dbea573c941f72c75f242767eacc91f3c370'
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def write(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(raw)
def main():
    assert sha(DEST/'publication.json')==EXPECTED_PUBLICATION
    publication=read(DEST/'publication.json'); registration=read(PROFILE/'registration.json')
    inputs={str(DEST/'publication.json'):EXPECTED_PUBLICATION}
    for entry in publication['outputs']:
        assert sha(entry['path'])==entry['sha256'],entry['path']
        inputs[entry['path']]=entry['sha256']
    for p,h in publication['inputs'].items(): assert sha(p)==h,p
    for p,h in registration['config']['source_identities'].items():
        assert sha(p)==h,p
        inputs[p]=h
    control=read(STAGE/'preflop-expected-published-controls-v1/result.json')
    assert control['passed'] and len(control['checks'])==5
    for row in control['checks']:
        assert row['exit_code']==0 and row['payload']['passed']
        assert Path(row['argv'][2]).parent==ROOT/'tools/research'
        assert sha(row['argv'][2])==row['source_sha256']
    copies=[]
    for p in sorted((STAGE/'preflop-expected-published-controls-v1').rglob('*')):
        if p.is_file():
            target=DEST/'publication-controls'/p.relative_to(STAGE/'preflop-expected-published-controls-v1')
            write(target,p.read_bytes()); assert sha(target)==sha(p)
            inputs[str(p)]=sha(p);copies.append(dict(path=str(target),sha256=sha(target)))
    for name in ('preflop_expected_published_controls_v1.py',Path(__file__).name):
        p=STAGE/name;target=DEST/'publication-controls'/name
        write(target,p.read_bytes());copies.append(dict(path=str(target),sha256=sha(target)))
    journal=OUT/'RIVER-CONTINUATION-RUNNING.md'; old=journal.read_bytes();before=sha(journal)
    block='''

## 2026-10-02 Adelaide - genuine native pipeline cycle and independent retained audit pass

The previous study turn produced authoritative progress: a registered one-shot 20bb native collection, both actual CUDA fits, complete checkpoint restoration and independent retained-artifact readback. The intervening user question explained how equilibrium accuracy is established; it did not authorize any change to scientific gates. This continuation verified exact publication and qualified all five small published-import-path fixtures in parallel (12.764 seconds). Original science, sources, budgets, models, failed improvement finding and failed software/readback evidence remain preserved.

The genuine profile passed in 91.531 seconds with two full-board exports, all 1081 legal private holdings per actor, 169 physical deals in thirteen ordered batches, posterior64, three river/two board workers and two four-step CUDA fits. It used only the initial uniform played model and restored all cumulative targets, reservoirs, sampler/action/retention RNGs and network state. Independent v2 readback passed in 27.968 seconds, checking 127 pins, two board replays, thirteen physical batches, 117 native receipts and the 809-file manifest. The v1 exact-hash failure from one-thread rather than four-thread BLAS is retained with diagnosis; v2 pinned the original runtime and kept exact gates. No native/scientific attempt was retried.

Published STACK-CONTEXT-NATIVE-PIPELINE-20261002.md and exact new research sources/evidence are reviewed locally. The cycle is software/resource qualification only: K2/F4 and a single 20bb context do not prove poker accuracy, convergence, improved ranges or deployment readiness. Native execution uses owned process handles; shared cancellation stops pending and active nested worker tasks at cooperative boundaries. Published cancellation and resource controls pass.

The profile retained 1,278,992,546 logical bytes. Hash-verified duplicate river exports account for 588,895,857 bytes (46%); no historical files were linked, compressed or deleted. Read-only zlib samples show potential savings, without filesystem admission credit. The last global named-allocation snapshot was 778,101,470,861 bytes before the profile, against 800GB. Current output limits omit separate bridge/query/trace output paths and remain polled rather than hard quotas; larger admission needs complete direct-output accounting and explicit overshoot reserves.

Next: qualify transparent lossless retention only in new directories, cover all direct native outputs, measure one complete cycle across all five fitting depths, then prospectively register independent stability and fresh payoff comparisons with adequate boards. Stack-appropriate openings, five-bets, additional positions, multiway accuracy and matched GTO Wizard validation remain outstanding. No production56708 modification, GitHub push or deployment; broad goal active.
'''
    assert 'genuine native pipeline cycle and independent retained audit pass' not in old.decode('utf-8')
    assert sha(journal)==before
    with journal.open('ab') as stream:stream.write(block.encode('utf-8'))
    copies.append(dict(path=str(journal),sha256=sha(journal)))
    report=dict(passed=True,scope='Exact publication and published-path software controls; native profile is resource qualification only',
                inputs=inputs,outputs=copies,publication_sha256=EXPECTED_PUBLICATION,
                original_profile_registration_sha256=sha(PROFILE/'registration.json'),
                journal_before_sha256=before,journal_after_sha256=sha(journal),
                scientific_accuracy_qualified=False,production_modified=False,github_pushed=False)
    target=DEST/'review.json';write(target,(json.dumps(report,sort_keys=True,indent=2)+'\n').encode())
    paths=read(DEST/'git-paths.json')+[str(Path(row['path']).relative_to(ROOT)).replace('\\','/') for row in copies]
    paths += [str(target.relative_to(ROOT)).replace('\\','/'),str((DEST/'final-git-paths.json').relative_to(ROOT)).replace('\\','/')]
    assert len(set(paths))==len(paths)
    write(DEST/'final-git-paths.json',(json.dumps(paths,indent=2)+'\n').encode())
    for row in copies:assert sha(row['path'])==row['sha256']
    print(json.dumps(dict(passed=True,outputs=len(copies),git_paths=len(paths),review_sha256=sha(target))))
if __name__=='__main__':main()
