"""Resume unchanged registered collection with progress-only lock tolerance."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import json
from pathlib import Path
import time
import traceback
from board_river_deal_coverage_common_v1 import *
from board_prefix_publication_v1 import atomic_json
from board_river_deal_coverage_archive_v1 import read_archive
from research_progress_replace_v1 import progress_json
import board_river_deal_coverage_collect_v2 as collector


def status(value):
    result=progress_json(OUT/(PREFIX+'-status.json'),value)
    if not result['published']:
        print(json.dumps(dict(progress_update_deferred=True,**result)),flush=True)


def main():
    control_path=OUT/(PREFIX+'-resume-control-v1.json');control=read(control_path)
    assert control['passed'];verify(control['inputs'])
    assert not LOCK.exists() and not OTHER.exists() and not collector.RESULT.exists()
    registration=read(collector.REG);verify(registration['inputs']);selected=read(collector.SELECTION)
    paths=[Path(__file__),ROOT/'tools/research/research_progress_replace_v1.py',control_path,
        ROOT/'tools/research/board_river_deal_coverage_collect_v2.py',collector.REG,collector.SELECTION]
    hashes={str(p):sha(p) for p in paths};reg=OUT/(PREFIX+'-resume-registration-v1.json')
    assert not reg.exists();checked=[];expected={c['case_id']:c for c in selected['cases']}
    for mp in sorted((STORE/'cases').glob('*.manifest.json')):
        manifest=read(mp);ap=STORE/'cases'/manifest['archive'];raw=read_archive(ap,manifest)
        record=json.loads(raw['record.json']);case=record['case'];assert case==expected[case['case_id']]
        assert record['registration_sha256']==sha(collector.REG)
        import hashlib
        assert record['policies_sha256']==hashlib.sha256(raw['policies.npz']).hexdigest()
        assert record['export_sha256']==hashlib.sha256(raw['export.json']).hexdigest()
        checked.append(dict(case_id=case['case_id'],archive_sha256=sha(ap),manifest_sha256=sha(mp)))
    assert len({row['case_id'] for row in checked})==len(checked)
    verify(hashes)
    atomic_json(reg,dict(inputs=hashes,verified_completed_cases=checked,completed_cases=len(checked),
        change='Only collector status() uses bounded-retry best-effort replacement. All scientific and durable writers unchanged.',
        original_collection_registration_sha256=sha(collector.REG),created_unix=time.time(),production_modified=False))
    collector.status=status
    print(json.dumps(dict(resuming_verified_cases=len(checked),total_cases=selected['selected_cases'])),flush=True)
    try:
        collector.main('study',True)
        verify(hashes)
        atomic_json(OUT/(PREFIX+'-resume-result-v1.json'),dict(passed=True,complete=True,
            registration_sha256=sha(reg),collection_sha256=sha(collector.RESULT),production_modified=False))
    except Exception as error:
        atomic_json(OUT/(PREFIX+'-resume-failure-v1.json'),dict(error=repr(error),traceback=traceback.format_exc()));raise


if __name__=='__main__':main()
