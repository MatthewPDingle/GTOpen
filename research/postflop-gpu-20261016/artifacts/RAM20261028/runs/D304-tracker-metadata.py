"""Recover display-only dates/scores from the tracker's published evidence."""
import copy, datetime, json, math, re, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D304-tracker-display-metadata'

def timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        result = datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None or result > datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5):
            return None
        return result
    except ValueError:
        return None

def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0

def candidates(row):
    result = []
    for link in row.get('evidence', []):
        url = link.get('url', '')
        if not isinstance(url, str) or not url.startswith('evidence/') or not url.endswith('.json'):
            continue
        path = (h.ar.DASHBOARD / url).resolve()
        if not path.is_relative_to((h.ar.DASHBOARD / 'evidence').resolve()) or not path.is_file():
            continue
        # Only evidence identifying this same row, rather than a later child
        # experiment that happens to be linked as its successor.
        if not re.search(r'(?<![A-Za-z0-9])' + re.escape(row['id']) + r'(?=[/_.-]|$)', url):
            continue
        if path.stat().st_size > 2 * 1024**2:
            continue
        try:
            record = h.read(path)
        except (ValueError, UnicodeError):
            continue
        if isinstance(record, dict):
            result.append((path, url, record))
    return result

if len(sys.argv) == 1:
    h.custody()
    h.ar.refuse_active(h.ar.live_status())
    assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
    H.mkdir(exist_ok=False)
    before = h.ar.STATUS.read_bytes()
    (H / 'before-status.json').write_bytes(before)
    status = json.loads(before)
    patches, unresolved, sources = [], [], {}
    for index, row in enumerate(status['experiments']):
        missing_date = not row.get('at')
        perf = row.get('performance')
        needs_score = not number(row.get('full_cycle_ms')) and isinstance(perf, dict) and number(perf.get('baseline_full_cycle_ms')) and number(perf.get('candidate_full_cycle_ms'))
        if not missing_date and not needs_score:
            continue
        records = candidates(row)
        patch, provenance = {}, {}
        if missing_date:
            dates = [(timestamp(record.get('at')), path, url, record.get('at')) for path, url, record in records if timestamp(record.get('at'))]
            if dates:
                _, path, url, value = max(dates, key=lambda item: item[0])
                patch['at'] = value
                provenance['at'] = {'url': url, 'field': 'at', 'sha256': h.sha(path)}
                sources[str(path)] = h.sha(path)
            else:
                unresolved.append({'row_index': index, 'id': row['id'], 'field': 'at', 'reason': 'No same-ID published JSON with a valid explicit timezone timestamp. Left unrecorded; no filesystem date inferred.'})
        if needs_score:
            matches = [(path, url, record) for path, url, record in records if record.get('performance') == perf and re.search(r'sum.*median', str(perf.get('aggregation', '')), re.I)]
            if matches:
                path, url, record = matches[0]
                patch['full_cycle_ms'] = perf['candidate_full_cycle_ms']
                patch['baseline_full_cycle_ms'] = perf['baseline_full_cycle_ms']
                patch['score_aggregation'] = perf['aggregation']
                if not row.get('fixture'):
                    patch['fixture'] = 'Three-fixture benchmark score · sum of medians'
                provenance['score'] = {'url': url, 'field': 'performance', 'sha256': h.sha(path)}
                sources[str(path)] = h.sha(path)
            else:
                unresolved.append({'row_index': index, 'id': row['id'], 'field': 'score', 'reason': 'No identical same-ID published performance object with explicit sum-of-medians aggregation; no timing inferred.'})
        if patch:
            patch['display_metadata_evidence'] = provenance
            patches.append({'row_index': index, 'id': row['id'], 'set': patch})
    h.save(H / 'plan.json', {'id': 'D304', 'at': h.now(), 'status': 'FROZEN_PRE_DISPLAY_ONLY_STATUS_UPDATE',
        'script_sha256': h.sha(__file__), 'status_before_sha256': h.sha(H / 'before-status.json'),
        'source_evidence_sha256': sources, 'patches': patches, 'unresolved': unresolved,
        'allowed_row_keys': ['at', 'full_cycle_ms', 'baseline_full_cycle_ms', 'fixture', 'score_aggregation', 'display_metadata_evidence'],
        'invariants': 'Preserve all original rows/order/IDs/status/accepted/quality/reasons/evidence/raw/scientific/performance/fixtures/acceptedhistory/currentRAMbaseline/configuration; fill missing display fields only, using same-ID immutable published evidence. Date=latest explicit evidence at, not experiment start or mtime. Scores=existing exact performance object only; no new/pooled/recomputed measurements, significance, promotion or gain adoption. Unknown dates/scores remain unknown.',
        'new_native_compiler_GPU_solver_or_speed_samples': 0})
    print(json.dumps({'plan_sha256': h.sha(H / 'plan.json'), 'patched_rows': len(patches),
        'dates_recovered': sum('at' in item['set'] for item in patches), 'scores_recovered': sum('full_cycle_ms' in item['set'] for item in patches),
        'unresolved': unresolved}), flush=True)
    sys.exit(0)

assert len(sys.argv) == 2
h.pin(H / 'plan.json', sys.argv[1])
plan = h.read(H / 'plan.json')
h.pin(__file__, plan['script_sha256'])
for path, digest in plan['source_evidence_sha256'].items():
    h.pin(path, digest)
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    h.pin(h.ar.STATUS, plan['status_before_sha256'])
    old = h.read(H / 'before-status.json')
    status = copy.deepcopy(old)
    for item in plan['patches']:
        row = status['experiments'][item['row_index']]
        assert row['id'] == item['id'] and set(item['set']) <= set(plan['allowed_row_keys'])
        for key, value in item['set'].items():
            if key in ['at', 'fixture']:
                assert not row.get(key)
            if key in ['full_cycle_ms', 'baseline_full_cycle_ms']:
                assert not number(row.get(key))
            row[key] = value
    # Verify reversing only declared additions recovers every original field.
    replay = copy.deepcopy(status)
    for item in plan['patches']:
        row, previous = replay['experiments'][item['row_index']], old['experiments'][item['row_index']]
        for key in item['set']:
            if key in previous:
                row[key] = previous[key]
            else:
                del row[key]
    assert replay == old
    h.save(H / 'report.json', {'id': 'D304', 'at': h.now(), 'status': 'pass_evidence_bound_display_metadata_reconciliation',
        'plan_sha256': sys.argv[1], 'original_rows_retained': len(old['experiments']),
        'patched_rows': len(plan['patches']), 'dates_recovered': sum('at' in item['set'] for item in plan['patches']),
        'aggregate_scores_recovered': sum('full_cycle_ms' in item['set'] for item in plan['patches']),
        'unresolved': plan['unresolved'], 'all_original_row_content_and_top_level_fields_recovered_by_reversal': True,
        'no_status_accepted_measurement_baseline_quality_or_raw_artifact_changes': True,
        'new_native_GPU_solver_or_speed_samples': 0,
        'limits': 'Display metadata only. Each date identifies a published evidence timestamp, not necessarily run start. Composite score explicitly labeled sum of fixture medians; no new speed or optimizer gain. Original data preserved in before-status.json.'})
    assert not any(row['id'] == 'D304' for row in status['experiments'])
    status['experiments'].append({'id': 'D304', 'at': h.now(), 'title': 'Recover tracker dates and benchmark scores from evidence',
        'kind': 'diagnostic', 'status': 'measured', 'accepted': False, 'stage': 'Display metadata repaired',
        'reason': f"Recovered {sum('at' in item['set'] for item in plan['patches'])} evidence timestamps and {sum('full_cycle_ms' in item['set'] for item in plan['patches'])} aggregate benchmark scores; original decisions, measurements and baseline unchanged. Unknown fields stay unknown.",
        'evidence': [{'label': 'Evidence-bound display update', 'url': 'evidence/D304-tracker-display-metadata/report.json'},
                     {'label': 'All preserved fields and source references', 'url': 'evidence/D304-tracker-display-metadata/plan.json'}]})
    status.update(updated_at=h.now(), stage='Tracker display metadata repaired; performance search continues', activity=status['experiments'][-1]['reason'] + ' E123 remains closed; E080 remains qualified/live.', active_experiment='D304')
    h.ar.atomic_json(h.ar.STATUS, status)
    shutil.copyfile(h.ar.STATUS, H / 'after-status.json')
for path in [H / 'plan.json', H / 'report.json']:
    destination = h.ar.DASHBOARD / 'evidence' / H.name / path.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists()
    shutil.copyfile(path, destination)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + H.name + '/' + path.name, timeout=20) as response:
        assert response.read() == path.read_bytes()
h.save(H / 'publication.json', {'at': h.now(), 'status_before_sha256': plan['status_before_sha256'], 'status_after_sha256': h.sha(H / 'after-status.json'),
    'report_sha256': h.sha(H / 'report.json'), 'all_original_data_reversal_exact': True, 'HTTP_report_plan_exact': True, 'candidate_adopted': False})
h.custody()
print(json.dumps(h.read(H / 'report.json')), flush=True)
