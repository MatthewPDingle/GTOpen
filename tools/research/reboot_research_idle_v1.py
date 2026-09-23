"""Fail-closed activity probe, including a verified empty post-reboot session."""
import json
import urllib.request
import urllib.error


def idle():
    for route in ('preflop/status', 'status', 'reports/status'):
        with urllib.request.urlopen('http://127.0.0.1:56708/api/'+route, timeout=5) as response:
            data = json.load(response)
        if route == 'reports/status':
            if data.get('running') is not False:
                return False
        elif route == 'preflop/status' and data.get('state') == '':
            if data.get('iteration') != 0 or data.get('published_iteration') != 0:
                return False
            try:
                with urllib.request.urlopen('http://127.0.0.1:56708/api/preflop/session', timeout=5):
                    return False
            except urllib.error.HTTPError as error:
                if error.code != 400 or error.read().decode() != 'no preflop game built yet':
                    return False
        elif data.get('state') not in ('idle', 'done', 'stopped', 'ready', 'empty', 'error'):
            return False
    return True
