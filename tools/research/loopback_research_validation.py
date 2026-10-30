"""Same bounded research guard with direct IPv4 loopback status probes.

On this host localhost's failed IPv6 connection attempt adds about two
seconds per request. All three safety checks and fail-closed behavior stay
unchanged. The outer overnight registration freezes this wrapper and the
base guard. This does not change any server binding or system networking.
"""
import json
from types import SimpleNamespace
import urllib.request
import paged_continuation_validation as base


def idle():
    for route in ['preflop/status', 'status', 'reports/status']:
        with urllib.request.urlopen('http://127.0.0.1:56708/api/'+route, timeout=5) as response:
            data = json.load(response)
        if route == 'reports/status':
            if data.get('running') is not False:
                return False
        elif data.get('state') not in ['idle', 'done', 'stopped', 'ready', 'empty', 'error']:
            return False
    return True


if __name__ == '__main__':
    base.guard = SimpleNamespace(idle=idle)
    base.run()
