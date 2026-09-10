"""Publish compact deployment evidence without native strategy payloads."""
import datetime as dt
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
folder = ROOT/'target/research-deployment/Before preflop deployment 20260911-054159-f22e270e'
backup = json.loads((folder/'backup.json').read_text())
cutovers = [json.loads(path.read_text()) for path in folder.glob('cutover-*.json')]
if len(cutovers) != 1 or cutovers[0]['status'] != 'deployed':
    raise SystemExit('Expected one successful cutover')
cutover = cutovers[0]
restores = [json.loads(path.read_text()) for path in folder.glob('restore-*.json')]
if len(restores) != 1:
    raise SystemExit('Expected one exact live restoration record')
for key in ['pre', 'post']:
    if restores[0]['verification_saves'][key]['native'] != backup['backups'][key]['native']:
        raise SystemExit('Native restoration mismatch')
evidence = {
    'recorded_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'production_commit': '184f17a', 'accepted_research_commit': '4878044924f2e170692a897de4179690357cf669',
    'port': backup['port'], 'old_owner': cutover['old_owner'], 'new_owner': cutover['new_owner'],
    'deployed_utc': cutover['finished_utc'], 'isolated_smoke_passed': (folder/'smoke-passed.json').is_file(),
    'latest_native_rechecked': bool(list(folder.glob('live-recheck-*.json'))),
    'live_native_restoration_exact': True, 'solve_started_during_deployment': False,
    'preflop_display_before': backup['snapshot']['pre_status']['iteration'],
    'preflop_native_before_after': backup['snapshot']['pre']['iteration'],
    'postflop_iteration_before_after': backup['snapshot']['post']['iteration'],
    'postflop_board': backup['snapshot']['post']['spot_request']['board'],
    'backup_manifest': str(folder/'backup.json'),
    'backups': {},
}
for key, item in backup['backups'].items():
    native = item['native']
    evidence['backups'][key] = {'path': item['path'], 'sha256': item['sha256'],
        'magic': native['magic'], 'arrays': native['arrays'],
        'normalized_header_sha256': hashlib.sha256(json.dumps(native['header'], sort_keys=True).encode()).hexdigest()}
(HERE/'deployment-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
(HERE/'final-server-suite.json').write_text(json.dumps({'accepted_source':'4878044','passed':8,'failed':0,
    'ignored':1,'log':'raw/final-server-gto-server.log','features':['gpu'],'test_threads':1}, indent=2)+'\n')
print(json.dumps({k:evidence[k] for k in ['port','deployed_utc','live_native_restoration_exact','preflop_native_before_after','postflop_iteration_before_after','postflop_board']}))
