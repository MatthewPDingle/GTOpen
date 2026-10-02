"""Publish candidate-specific retention evidence and read-only output review."""
import hashlib
import importlib.util
import json
from pathlib import Path
import time

STAGE=Path(__file__).resolve().parent
ROOT=Path(r'T:\Dev\GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
DEST=OUT/'ntfs-retention-evidence-20261002'
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda:stream.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def write(path,raw):
    assert path.resolve().is_relative_to(ROOT.resolve()) and not path.exists()
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(raw)
def main():
    assert not DEST.exists()
    auditpath=STAGE/'ntfs-expected-retention-independent-readback-v1/result.json'
    assert sha(auditpath)=='a42ced01a4c0d5119e87ce8eb7486f55624f1f86a8fa658b9e43194fceb88326'
    audit=read(auditpath);control=read(STAGE/'preflop-expected-ntfs-retention-control-v2-result.json')
    assert audit['passed'] and control['passed'] and not audit['scientific_accuracy_qualified']
    pins=read(STAGE/'native-export-bounds-review-v1/source-pins.json')
    for p,h in audit['input_pins'].items():assert sha(p)==h,p
    for p,h in pins['source_identities'].items():assert sha(p)==h,p
    for item in pins['native_binaries'].values():assert sha(item['path'])==item['sha256']
    manifest=read(STAGE/'native-export-bounds-review-v1/artifact-manifest.json')
    for name,h in manifest['artifact_sha256'].items():
        p=STAGE/'native-export-bounds-review-v1'/name
        assert p.resolve().is_relative_to((STAGE/'native-export-bounds-review-v1').resolve())
        assert sha(p)==h,name
    outputs=[];inputs={}
    def copy(p,target):
        inputs[str(p)]=sha(p);write(target,p.read_bytes())
        assert sha(target)==inputs[str(p)]
        outputs.append(dict(path=str(target),sha256=sha(target)))
    library=ROOT/'tools/research/ntfs_expected_retention_v2.py'
    copy(STAGE/'ntfs_expected_retention_v2.py',library)
    for name in ('ntfs_expected_retention_v1.py','ntfs_expected_retention_v2.py',
                 'preflop_expected_ntfs_retention_check_v1.py','preflop_expected_ntfs_retention_check_v2.py'):
        copy(STAGE/name,DEST/'sources'/name)
    for folder in ('ntfs-expected-retention-independent-readback-v1','native-export-bounds-review-v1'):
        for p in sorted((STAGE/folder).iterdir()):
            if p.is_file():copy(p,DEST/folder/p.name)
    for version in (1,2):
        store=Path(r'S:\GTOpen-research')/f'ntfs-expected-profile-control-v{version}'
        names=['attempt.json','fixture/nested/python-writer-receipt.json']
        names+=['failure.json'] if version==1 else ['copied-manifest.json','result.json']
        for name in names:copy(store/name,DEST/f'control-v{version}'/name)
    copy(STAGE/'STACK-CONTEXT-LOSSLESS-RETENTION-20261002.md',OUT/'STACK-CONTEXT-LOSSLESS-RETENTION-20261002.md')
    # Read-only published-path qualification; no second control or copy run.
    spec=importlib.util.spec_from_file_location('published_ntfs',library)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    began=time.monotonic();measured=module.measure_tree(Path(control['store'])/'profile-copy',lambda:None)
    assert measured==control['copied_storage']
    assert module.file_identity(Path(control['store'])/'fixture/nested/hardlink.bin')['links']==2
    published=dict(passed=True,scope='Read-only published-library measurement of already qualified copy',
                   module=str(library),source_sha256=sha(library),measurement=measured,seconds=time.monotonic()-began)
    target=DEST/'published-readback.json';write(target,(json.dumps(published,sort_keys=True,indent=2)+'\n').encode())
    outputs.append(dict(path=str(target),sha256=sha(target)))
    journal=OUT/'RIVER-CONTINUATION-RUNNING.md';before=sha(journal)
    block='''

## 2026-10-02 Adelaide - complete lossless retention qualification and six-child output review

Previous goal turn produced the genuine audited native pipeline profile; this continuation finished published-path qualification and local commit91ac598c, then completed a new-directory lossless retention control. Two809-file copies preserve all1,278,992,546logical bytes while each occupies311,489,940named allocated bytes (24.3543%,75.6457% saving). V2 control6.750s and independent retained readback8.578s passed; these are software/storage controls, not poker accuracy or a training speed benchmark. Eight CPU copy workers were used; no GPU fit or scientific/native poker run occurred.

The original v1 control failed at its final hardlink-accounting test and is preserved. Actual WindowsPython3.12 DirEntry.stat(follow_symlinks=False).st_nlink returned0 for the two-link fixture; Path.stat and Win32 returned2. A separate v2 uses actual GetFileInformationByHandle file identity/link count and refuses shared-file accounting. Its inaccurate 'can report1' comment is explicitly qualified by the independent audit, without altering attempted sources. Both809-file sets, original hashes/attributes, nested inheritance, both Python invocation receipts, seek/append/rename and actual hardlink refusal were reconstructed read-only. Reparse rejection was mocked, not an actual junction fixture.

A read-only source-pinned export review found direct queries.json,updates.json and action-trace.json escape current stdout/stderr limits. The main coordinator overlaps all five workers, producing up to six native children. Proposed64MB aggregate transport/two2GB board envelopes plus three river stdout copies give4.448GB nominal; conservative unqualified stderr copying can reach5.408GB. Polling alone does not prove transient overshoot. No bound/helper/Rust/native executable or original scientific gate was changed by that review.

Saved STACK-CONTEXT-LOSSLESS-RETENTION-20261002.md, exact working NTFS helper, both attempts/failure/control sources, independent audit and output review locally. Published helper readback measures the existing qualified copy; it launches no second retention attempt. All original source and scientific result pins remain preserved. Historical files were not compressed, linked, overwritten or removed; production56708unchanged, no GitHub push/deployment.

Next: qualify complete direct-output receipts and prospective export-only pre-write limits with identical serialized bytes, reserve six-child/transient and metadata space, refresh the global800GB inventory, and measure a genuine full-five-depth cycle before registering sufficiently sampled stability/fresh-payoff comparisons. Stack-specific openings, five-bets, additional positions, multiway/Wizard accuracy and production readiness remain outstanding. Broad goal remains active.
'''
    assert 'complete lossless retention qualification and six-child output review' not in journal.read_text(encoding='utf-8')
    assert sha(journal)==before
    with journal.open('ab') as stream:stream.write(block.encode())
    outputs.append(dict(path=str(journal),sha256=sha(journal)))
    copy(Path(__file__).resolve(),DEST/'publication-source.py')
    receipt=dict(passed=True,scope='Candidate-specific storage qualification and exact local publication; no poker accuracy claim',
                 inputs=inputs,outputs=outputs,audit_sha256=sha(auditpath),journal_before_sha256=before,
                 scientific_accuracy_qualified=False,production_modified=False,github_pushed=False)
    path=DEST/'publication.json';write(path,(json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode())
    paths=[str(Path(row['path']).relative_to(ROOT)).replace('\\','/') for row in outputs]
    paths+=[str(path.relative_to(ROOT)).replace('\\','/'),str((DEST/'git-paths.json').relative_to(ROOT)).replace('\\','/')]
    assert len(paths)==len(set(paths))
    write(DEST/'git-paths.json',(json.dumps(paths,indent=2)+'\n').encode())
    print(json.dumps(dict(passed=True,files=len(paths),publication_sha256=sha(path),published_readback_seconds=published['seconds'])))
if __name__=='__main__':main()
