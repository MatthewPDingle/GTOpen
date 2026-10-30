"""Preserve publication review and add an explicit prose correction; no reruns."""
import hashlib,json,os
from pathlib import Path
import time

STAGE=Path(__file__).resolve().parent
OUT=Path(r'T:\Dev\GTOpen\research\preflop-evolution\blind-defense-20260922')
DEST=OUT/'native-bounds-evidence-20261003'
ERRATA="""# Publication wording correction

Read this together with STACK-CONTEXT-COMPLETE-NATIVE-BOUNDS-20261003.md.
The original findings and publication receipt are preserved byte for byte.

The findings' phrase "four small Python wiring controls separately checked OS
command lines" is too broad. In the successful river-control suite, the two
bridge/trace children received independent OS command-line checks. The two
history/selected transport children checked argument/payload bindings without
independent OS command-line checks. The execution-v2 suite has one separate
OS-attestation control. Do not extend those checks to all 39 native receipts:
their observed_argv field records the owned Popen argument vector.

The independent publication review passed all technical byte/source/wiring
checks but intentionally saved overall passed=false for this prose issue.
This additive correction resolves the wording without rewriting that report or
rerunning any control. Its earlier audit-script helper argument-name failure is
also retained; it was not an implementation failure or a scientific attempt.
"""

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):return dict(path=str(Path(p).resolve()),sha256=sha(p),bytes=Path(p).stat().st_size)
def write(p,v):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    publication=DEST/'publication.json'
    if sha(publication)!='eadcf1572e967f8be6a2b323830b431d06df7f77d00e04675df7de5bfc416ec0':raise ValueError('Publication changed')
    review=STAGE/'native-bounds-publication-independent-review-v2/result.json'
    if sha(review)!='2823b37693f8ee87fb67453e6caf2046328350d7486e294808d272d76a549120':raise ValueError('Review changed')
    r=json.loads(review.read_bytes())
    if r['failures'] or not r['exact_copy_and_source_review_passed'] or not r['runtime_wiring_review_passed']:
        raise ValueError('Technical publication review incomplete')
    if len(r['prose_issues'])!=1:raise ValueError('Unexpected prose issues')
    folders=['native-bounds-publication-independent-review-v1','native-bounds-publication-independent-review-v2',
             'preflop-five-depth-resource-preflight-v1','preflop-expected-full-native-cycle-prospective-plan-v1']
    copied=[]
    for name in folders:
        target=DEST/'followup'/name
        if target.exists():raise FileExistsError(target)
        target.mkdir(parents=True)
        for p in sorted((STAGE/name).rglob('*')):
            if not p.is_file():continue
            if p.stat().st_size>1_000_000:raise ValueError('Unexpected followup payload')
            d=target/p.relative_to(STAGE/name);d.parent.mkdir(parents=True,exist_ok=True)
            original=info(p)
            with d.open('xb') as f:f.write(p.read_bytes())
            copied.append(dict(original=original,copy=info(d)))
            if sha(d)!=original['sha256']:raise ValueError('Copy changed')
    with (DEST/'ERRATA.md').open('x',encoding='utf-8',newline='\n') as f:f.write(ERRATA)
    for p in (Path(__file__),STAGE/'preflop_five_depth_resource_preflight_v1.py'):
        d=DEST/'followup'/p.name
        with d.open('xb') as f:f.write(p.read_bytes())
        copied.append(dict(original=info(p),copy=info(d)))
    receipt=dict(passed=True,created_unix=time.time(),original_publication=info(publication),
        independent_review=info(review),copies=copied,errata=info(DEST/'ERRATA.md'),
        scope='Exact followup preservation and explicit prose correction; fresh preflight is not admission',
        native_runs=0,control_reruns=0,scientific_runs=0,profile_registered=False,profile_started=False)
    write(DEST/'followup-publication.json',receipt)
    paths=STAGE/'native-bounds-publication-v1-git-paths.txt'
    previous=paths.read_text().splitlines()
    additions=[str(p.relative_to(OUT.parents[2])).replace('\\','/') for p in
        [DEST/'ERRATA.md',DEST/'followup-publication.json',*[Path(x['copy']['path']) for x in copied]]]
    paths.write_text('\n'.join(dict.fromkeys(previous+additions))+'\n')
    print(json.dumps(dict(passed=True,errata=info(DEST/'ERRATA.md'),receipt=info(DEST/'followup-publication.json'),files=len(copied))))
if __name__=='__main__':main()
