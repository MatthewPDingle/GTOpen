"""Read-only final source/runtime check. Never changes or stops a live session."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import psutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE / 'proposals/final-deployment'))
from session_guard import api, owner, queues_clear, require, write_new


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Output already exists')
    queues_clear()
    accepted = json.loads((HERE / 'proposals/final-integration-audit/accepted-source-manifest.json').read_text())
    checked = []
    for row in accepted['files']:
        data = subprocess.check_output(['git', 'show', 'HEAD:' + row['path']], cwd=ROOT)
        working = (ROOT / row['path']).read_bytes().replace(b'\r\n', b'\n')
        digest = hashlib.sha256(data).hexdigest()
        require(digest == row['sha256_git_bytes'] and working == data, 'Accepted source changed: ' + row['path'])
        checked.append({'path': row['path'], 'sha256': digest, 'accepted_and_working_exact': True})
    deployment = json.loads((HERE / 'deployment-evidence.json').read_text())
    current_owner = owner(56708)
    for field in ('pid', 'created', 'exe', 'cwd', 'sha256'):
        require(current_owner[field] == deployment['new_owner'][field], 'Live runtime identity changed: ' + field)
    servers = []
    for process in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if (process.info['name'] or '').lower() == 'gto-server.exe':
                servers.append(process.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    require({p['pid'] for p in servers} == {current_owner['pid']}, 'Unexpected extra GTO server remains')
    pre = api(56708, '/api/preflop/status')
    session = api(56708, '/api/preflop/session')
    post = api(56708, '/api/status')
    reports = api(56708, '/api/reports/status')
    report = {
        'checked_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'read_only': True, 'sources': checked, 'runtime_owner': current_owner,
        'only_one_gto_server': True,
        'preflop': {key: pre.get(key) for key in ('state', 'iteration', 'gpu', 'error', 'multiway_equity_model')},
        'preflop_session_iteration': session['iteration'],
        'postflop': {key: post.get(key) for key in ('state', 'iteration', 'error')},
        'postflop_board': post.get('spot_request', {}).get('board'),
        'reports_running': reports.get('running'),
        'interpretation': 'Current read-only snapshot. User activity may advance sessions after deployment; no live action was issued.'
    }
    write_new(args.output, report)
    print(json.dumps({key: report[key] for key in ('checked_utc', 'only_one_gto_server', 'preflop', 'preflop_session_iteration', 'postflop', 'postflop_board', 'reports_running')}, indent=2))


if __name__ == '__main__':
    main()
