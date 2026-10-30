"""Retain narrow independent prose resolution and record fresh preflight."""
import hashlib,json,time
from pathlib import Path
STAGE=Path(__file__).resolve().parent
ROOT=Path(r'T:\Dev\GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
DEST=OUT/'native-bounds-evidence-20261003'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return dict(path=str(Path(p).resolve()),sha256=sha(p),bytes=Path(p).stat().st_size)
def main():
    folder=STAGE/'native-bounds-publication-independent-review-v2'
    p=folder/'resolution.json'
    if sha(p)!='21d289b79b25e87a610782180a97017496872fe1f59e1a4f7400ca01cdbe3553':raise ValueError('Resolution changed')
    result=json.loads(p.read_bytes())
    if result['passed'] is not True or result['native_runs'] or result['control_reruns']:
        raise ValueError('Unexpected resolution scope')
    pairs=[]
    for source in (p,folder/'resolve_errata.py',Path(__file__)):
        target=DEST/'followup'/'native-bounds-publication-independent-review-v2'/source.name
        with target.open('xb') as f:f.write(source.read_bytes())
        if sha(target)!=sha(source):raise ValueError('Copy changed')
        pairs.append(dict(original=info(source),copy=info(target)))
    journal=OUT/'RIVER-CONTINUATION-RUNNING.md';before=info(journal)
    text="""

Independent publication review completed 7,993 retained technical checks and
hashed 1,604 distinct files; all 775 copies, 15 retained exclusions and exact
runtime/Rust sources passed. The original review intentionally remains false
for one prose issue. Additive ERRATA.md and independent resolution.json clarify
that two successful bridge/trace Python children received OS command-line checks,
two transport children did not, and execution-v2 has a separate such control.
The resolution passed without rerunning the full audit or controls. The earlier
audit-script argument collision and original report remain preserved.

Fresh three-root Win32 named-allocation inventory observed780,207,000,146 bytes,
leaving19,792,999,854 under the800GB cap. At that observation:89.2GB RAM available,
20,193MiB GPU free, production available, no matching live research worker;
S:282.98GB free versus T:10.76GB. This is preflight evidence, not a registered
profile or launch admission. Separate five-depth planning identifies ALL Python
derived/NPZ/checkpoint/receipt writers and requires unthrottled per-write checks
or atomic reservations in spawned workers. Preparation of that resource-only
layer and a separate launcher is ongoing; no profile/scientific attempt started.
"""
    with journal.open('a',encoding='utf-8',newline='\n') as f:f.write(text)
    receipt=dict(passed=True,created_unix=time.time(),copies=pairs,journal_before=before,journal_after=info(journal),
        scope='Independent prose resolution and truthful preflight journal checkpoint',scientific_runs=0,
        native_runs=0,control_reruns=0,production_changed=False,profile_started=False)
    target=DEST/'resolution-publication.json'
    with target.open('x',encoding='utf-8',newline='\n') as f:json.dump(receipt,f,indent=2,sort_keys=True);f.write('\n')
    manifest=STAGE/'native-bounds-publication-v1-git-paths.txt';old=manifest.read_text().splitlines()
    added=[str(Path(x['copy']['path']).relative_to(ROOT)).replace('\\','/') for x in pairs]
    added.append(str(target.relative_to(ROOT)).replace('\\','/'))
    manifest.write_text('\n'.join(dict.fromkeys(old+added))+'\n')
    print(json.dumps(dict(passed=True,receipt=info(target),journal=info(journal))))
if __name__=='__main__':main()
