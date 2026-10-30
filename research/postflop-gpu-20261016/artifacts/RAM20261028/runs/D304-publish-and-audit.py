"""Preserve browser proof, the HTML-only fix, and final custody checks."""
import copy, json, shutil, subprocess, sys, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D304-tracker-display-metadata'
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
plan, before, after = [h.read(H / name) for name in ['plan.json', 'before-status.json', 'after-status.json']]
assert h.sha(H / 'before-status.json') == plan['status_before_sha256']
for item in plan['patches']:
    row = after['experiments'][item['row_index']]
    assert row['id'] == item['id']
    for key, value in item['set'].items():
        assert row[key] == value
    provenance = item['set']['display_metadata_evidence']
    for kind, source in provenance.items():
        path = h.ar.DASHBOARD / source['url']
        h.pin(path, source['sha256'])
        record = h.read(path)
        if kind == 'at':
            assert row['at'] == record['at']
        else:
            assert row['performance'] == record['performance']
            assert row['full_cycle_ms'] == record['performance']['candidate_full_cycle_ms']
            assert row['baseline_full_cycle_ms'] == record['performance']['baseline_full_cycle_ms']
    old = before['experiments'][item['row_index']]
    restored = copy.deepcopy(row)
    for key in item['set']:
        if key in old:
            restored[key] = old[key]
        else:
            del restored[key]
    assert restored == old
for key in ['accepted_complete_run', 'accepted_history', 'fixtures', 'hardware_epoch', 'current_ram_baseline']:
    if key in before:
        assert before[key] == after[key]
fix = h.read(H / 'layout-fix.json')
h.pin(h.ar.DASHBOARD / 'index.html', fix['after_sha256'])
old_html = (H / 'index-before.html').read_bytes()
new_html = (H / 'index-after.html').read_bytes()
rule = b'    #experiments td:last-child .badge{display:inline-block;max-width:100%;white-space:normal;overflow-wrap:anywhere}\n'
assert new_html.replace(rule, b'', 1) == old_html
snapshot = Path(r'X:\Dev\GTOpen\.playwright-cli\page-2026-10-29T20-12-41-640Z.yml')
text = snapshot.read_text(encoding='utf-8')
assert 'E122 \u00b7 Oct 30, 06:18:06 AM' in text and '9.20 s' in text
assert 'E123 \u00b7 Oct 30, 06:34:31 AM' in text
raw = H / 'browser-evidence'
raw.mkdir(exist_ok=False)
browser_files = [snapshot, ROOT / 'output/playwright/D304-e122-row.png', ROOT / 'output/playwright/D304-e122-row-wrapped.png', ROOT / 'output/playwright/E123-tracker-closed.png']
for source in browser_files:
    shutil.copyfile(source, raw / source.name)
    assert source.read_bytes() == (raw / source.name).read_bytes()
h.save(H / 'browser-check.json', {'at': h.now(), 'status': 'pass_scoped_rendered_tracker_display',
    'actual_rendered': 'E122 datedOct30 06:18:06, rejected,9.20s/threefixture sumofmedians; E123 datedOct30 06:34:31,rejected,no invented timing. D304dated/metadatacount displayed. CLIconsole0errors0warnings. Before/after scoped row screenshots inspected; long validation labels now wrap inside table.',
    'HTML_before_sha256': fix['before_sha256'], 'HTML_after_sha256': fix['after_sha256'],
    'browser_evidence_sha256': {str(path): h.sha(path) for path in raw.iterdir()},
    'all_owned_browsers_explicitly_closed': True, 'native_GPU_solver_or_speed_samples': 0,
    'original_status_rows_order_decisions_measurements_and_evidence_preserved': True})
paths = [H / name for name in ['report.json', 'plan.json', 'layout-fix.json', 'layout-preparation-v1.json', 'browser-check.json', 'index-before.html', 'index-after.html']]
paths += list(raw.iterdir())
for path in paths:
    relative = Path(H.name) / path.relative_to(H)
    destination = h.ar.DASHBOARD / 'evidence' / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == path.read_bytes()
    else:
        shutil.copyfile(path, destination)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + relative.as_posix(), timeout=20) as response:
        assert response.read() == path.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'), timeout=3):
    status = h.read(h.ar.STATUS)
    e = next(row for row in status['experiments'] if row['id'] == 'D304')
    e.update(correctness='pass', stage='Browser display and original-data checks passed')
    e['evidence'] += [{'label': 'Rendered result and CSS scope', 'url': 'evidence/D304-tracker-display-metadata/browser-check.json'},
                      {'label': 'Readable experiment row', 'url': 'evidence/D304-tracker-display-metadata/browser-evidence/D304-e122-row-wrapped.png'}]
    status.update(updated_at=h.now(), stage='Tracker verified; distinct performance lead search continues',
                  activity='Recovered160dates/20aggregate scores from immutable evidence and wrapped long labels. Browser checks pass; original data/decisions/baseline unchanged. E123closed at compiler gates; E080 remains qualified/live.')
    h.ar.atomic_json(h.ar.STATUS, status)
ledger = h.REPO / 'research/postflop-gpu-20261016/experiments.md'
prefix = ledger.read_bytes()
assert b'\n## D304 evidence-bound tracker display repair' not in prefix
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).strip()
entry = f'''

## D304 evidence-bound tracker display repair - browser verified

ActualD302/E123browsercheck foundmanualcandidate rows missingtimestamps/renderedscorecolumns despiteimmutablepublishedreports. D304frozeplan{h.sha(H/'plan.json')}andfullbeforestatus5.35MB beforemutation. Inspectedonlysame-IDcontainedpublishedJSONlinks withvalidtimezoneat,2MiBcap,nofilesystemdateinference. Fillmissing dates fromlatestexplicitown-evidencetimestamp(whichisnotnecessarilyrunstart); fillaggregatecolumns onlywhenrow's existingperformanceobject literallyequals publishedown-IDreport andexplicitaggregationis sumofmedians.160dates/20scores recovered in161originalrows;all1486originalrows/order/IDs/status/accepted/reasons/quality/evidence/scientific/performance/acceptedhistory/fixtures/currentRAMbaseline fields preserved. Reversingdeclaredadditionsrecoversoriginalrows andpre-activitytopdataexactly. E097/D214/D255date andE112scoreleftunknown ratherthaninferred;all4reasonsrecorded. No new/pooled/recomputedmeasurements/optimizerpromotion/gain.

LivebrowserafterpatchshowsE122Oct30 06:18:06 rejected9.20s/three-fixture sumofmedians,E123Oct30 06:34:31 rejected/noinventedtime, D304counts;console0errors0warnings. Before-row screenshotrevealednowrapvalidationbadge stretchedtable; one scoped CSS rule makesonlyresearch-tablelast-columnbadgesinline-block/max100%/normalwrap/anywhere. EntirepreexistingHTMLrecoveredbyremovingoneASCIICSSline. OriginalpreparerassumedCRLF; safeassertionstoppedbeforebackup/mutation(actual189LF/0CRLF),originalscript/errorretained; additivev2preservesLF. Source/data/solveruntouchedbyrepair;notanoptimizerrescue. HTMLmainindexwasalreadymodifiedbeforethisCSS; fullpriorbytesbackup{H/'index-before.html'},afterSHA{fix['after_sha256']}; no originaleditsreset. Actualscopedrowbefore/afterPNGinspected,afterfitsreadably;ownsnapshot/PNGarchivedX,allownedbrowsersclosed.

Rootindependentreplaychecksall160timestamps/20scoresagainstimmutablepublishedfields/hashes andeverymodifiedoriginalrowfullreversal. No scientific/raw/source/CUDA/quality changes,allnewbulkX/Sreadonly/noT. {len(paths)}HTML/report/plan/browserartifactsHTTPbyteverified. E123fixedform remainsclosed,2ownedcompiler/modulechildren terminal0/noapplicationkernelorspeedtrial; liveE080/GPU/compressed/16/defaultaffinity andRAMreference10456.4109ms unchanged,newadoptedgain0,lastprimaryB377/nextB378. Priorledgerprefixbyteexact/localledgeronlycommit/nopush;goalactive.
'''
ledger.write_bytes(prefix + entry.encode())
assert ledger.read_bytes()[:len(prefix)] == prefix
h.custody()
subprocess.run(['git', 'add', '--', 'research/postflop-gpu-20261016/experiments.md'], cwd=h.REPO, check=True)
assert subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=h.REPO, text=True).splitlines() == ['research/postflop-gpu-20261016/experiments.md']
subprocess.run(['git', '-c', 'gc.auto=0', 'commit', '-m', 'research: restore evidence dates and scores in live tracker'], cwd=h.REPO, check=True)
h.custody()
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=h.REPO, text=True).strip()
assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=h.REPO, text=True).strip()
process = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command', "Get-CimInstance Win32_Process -Filter 'ProcessId = 26528 OR ProcessId = 36796 OR ProcessId = 30784 OR ProcessId = 37556 OR ProcessId = 55680' | Select-Object ProcessId,ExecutablePath | ConvertTo-Json -Compress"], text=True))
assert process['ProcessId'] == 26528 and process['ExecutablePath'].lower() == r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'.lower()
for path, url in [(h.ar.STATUS, 'status.json'), (h.ar.DASHBOARD / 'index.html', 'index.html'), (H / 'browser-check.json', 'evidence/D304-tracker-display-metadata/browser-check.json')]:
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/' + url, timeout=20) as response:
        assert response.read() == path.read_bytes()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
h.save(H / 'terminal-audit.json', {'at': h.now(), 'status': 'E123_CLOSED_D304_DISPLAY_VERIFIED_ALL_OWNED_WORK_TERMINAL',
    'local_ledger_commit': head, 'research_tracked_diff_clean': True, 'accepted_main_live_protected_PTX_exact': True,
    'HTML_only_scoped_rule_preserves_preexisting_main_changes': True, 'all_browsers_closed_compiler_module_children_terminal': True,
    'locks_absent': True, 'live_pid': 26528, 'server_idle': True, 'HTTP_status_index_report_exact': True,
    'last_primary_baseline': 'B377', 'next_unused_primary_baseline': 'B378', 'new_adopted_gain': False,
    'X_free_bytes': shutil.disk_usage(ROOT).free, 'all_new_bulk_X_S_readonly_no_T': True, 'goal_active': True})
print(json.dumps(h.read(H / 'terminal-audit.json')), flush=True)
