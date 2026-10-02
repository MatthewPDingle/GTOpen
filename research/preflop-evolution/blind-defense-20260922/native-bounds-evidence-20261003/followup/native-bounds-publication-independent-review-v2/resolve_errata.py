"""Narrow, read-only prose-issue resolution; no research/control imports."""
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent
OUT = Path(r'T:\Dev\GTOpen\research\preflop-evolution\blind-defense-20260922\native-bounds-evidence-20261003')


def identity(path):
    path = Path(path)
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def pinned(path, expected):
    actual = identity(path)
    assert actual['sha256'] == expected, str(path)
    return actual


review_id = pinned(HERE/'result.json', '2823b37693f8ee87fb67453e6caf2046328350d7486e294808d272d76a549120')
review = json.loads((HERE/'result.json').read_bytes())
assert review['passed'] is False and review['prose_review_passed'] is False
assert review['exact_copy_and_source_review_passed'] and review['runtime_wiring_review_passed']
assert review['failures'] == [] and len(review['prose_issues']) == 1
assert review['prose_issues'][0]['original_claim'] == 'four small Python wiring controls separately checked OS command lines'
errata_id = pinned(OUT/'ERRATA.md', 'e5bd152162860c5c3ea9dc60906d58d73461ac20c19555b1c3f10e3ae7772060')
errata_text = (OUT/'ERRATA.md').read_text()
text = ' '.join(errata_text.split())
for phrase in (
    'the two bridge/trace children received independent OS command-line checks',
    'The two history/selected transport children checked argument/payload bindings without independent OS command-line checks',
    'The execution-v2 suite has one separate OS-attestation control',
    'Do not extend those checks to all 39 native receipts: their observed_argv field records the owned Popen argument vector',
    'without rewriting that report or rerunning any control',
    'it was not an implementation failure or a scientific attempt',
):
    assert phrase in text, phrase
followup_id = pinned(OUT/'followup-publication.json', 'c6ec2c30d107582141a2619462114e72bc47475d83d270acceb30c8188c4b77e')
followup = json.loads((OUT/'followup-publication.json').read_bytes())
assert followup['passed'] and followup['errata'] == errata_id
assert followup['independent_review'] == review_id
assert followup['native_runs'] == followup['scientific_runs'] == followup['control_reruns'] == 0
assert followup['profile_registered'] is False and followup['profile_started'] is False
publication_id = pinned(OUT/'publication.json', review['publication_receipt']['sha256'])
assert publication_id == followup['original_publication']
findings_id = pinned(review['findings_identity']['path'], review['findings_identity']['sha256'])
assert findings_id == review['findings_identity']
source_identities = []
for expected in review['runtime_sources'] + review['rust_sources']:
    observed = pinned(expected['path'], expected['sha256'])
    assert observed == expected
    source_identities.append(observed)
preserved_reviews = []
for pair in followup['copies']:
    if Path(pair['original']['path']).parent.name not in {
        'native-bounds-publication-independent-review-v1',
        'native-bounds-publication-independent-review-v2',
    }:
        continue
    for item in (pair['original'], pair['copy']):
        assert pinned(item['path'], item['sha256']) == item
    assert pair['original']['sha256'] == pair['copy']['sha256']
    preserved_reviews.append(pair)
assert len(preserved_reviews) == 4
assert identity(HERE/'result.json') == review_id
assert identity(OUT/'publication.json') == publication_id
assert identity(OUT/'ERRATA.md') == errata_id
resolution = dict(
    format=1,
    passed=True,
    scope='Narrow additive prose-issue resolution based on retained technical publication review; no full audit replay',
    prior_review=review_id,
    retained_review_overall_passed=False,
    retained_review_prose_review_passed=False,
    retained_review_technical_checks_passed=True,
    inherited_technical_checks=review['checks'],
    inherited_technical_checks_rerun=False,
    resolved_issue=review['prose_issues'][0],
    errata=errata_id,
    errata_text=errata_text,
    independent_prose_assessment='The additive wording exactly resolves the single retained review prose failure: two successful bridge/trace children, two history/selected children without independent OS cmdline, and one separate execution-v2 OS-attestation control. The original report intentionally remains passed=false.',
    publication_receipt_unchanged=publication_id,
    findings_unchanged=findings_id,
    followup_receipt=followup_id,
    preserved_audit_attempt_files=preserved_reviews,
    runtime_and_rust_bytes_unchanged=source_identities,
    byte_gate_changes=False,
    scientific_changes=False,
    resource_profile_admitted=False,
    poker_accuracy_established=False,
    native_runs=0,
    control_reruns=0,
    full_audit_reruns=0,
    scientific_runs=0,
    imports_reexecuted=False,
    repo_writes=False,
    correction_written_by_this_reviewer=False,
    resolution_source=identity(__file__),
    terminal_unix=time.time(),
)
target = HERE/'resolution.json'
with target.open('x', encoding='utf-8', newline='\n') as stream:
    json.dump(resolution, stream, sort_keys=True, indent=2)
    stream.write('\n')
print(json.dumps(dict(passed=True, resolution=identity(target), source=identity(__file__))))
