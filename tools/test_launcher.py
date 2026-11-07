"""Windows integration checks using an isolated copied server and unused ports."""
import http.server
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import threading
import unittest
import urllib.request

import psutil

ROOT = Path(__file__).resolve().parent.parent


def free_port(host='127.0.0.1'):
    family = socket.AF_INET6 if ':' in host else socket.AF_INET
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()[1]


@unittest.skipUnless(os.name == 'nt', 'Windows launcher')
class LauncherTests(unittest.TestCase):
    def test_hidden_scenario_recovery_preserves_original_and_newer_saves(self):
        with tempfile.TemporaryDirectory(prefix='GTOpen scenario ') as tmp:
            directory = Path(tmp)
            base = directory/'8-max $2-2'
            stream = Path(str(base)+': limps.json')
            scenario = {'name':'8-max $2/2: limps', 'players':8, 'stack':150}
            stream.write_text(json.dumps(scenario))
            command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                       str(ROOT/'tools/recover-scenarios.ps1'), '-Directory', str(directory)]
            subprocess.run(command, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            recovered = directory/'8-max $2-2- limps.json'
            self.assertEqual(json.loads(recovered.read_text()), scenario)
            self.assertEqual(json.loads(stream.read_text()), scenario)
            scenario['stack'] = 200
            recovered.write_text(json.dumps(scenario))
            subprocess.run(command, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(json.loads(recovered.read_text())['stack'], 200)

    def test_cold_double_launch_reuses_one_server_and_handles_spaces(self):
        self.check_cold_double_launch(None)

    def test_ipv6_double_launch_reuses_one_server(self):
        self.check_cold_double_launch('::1')

    def check_cold_double_launch(self, bind_host):
        connect_host = bind_host or '127.0.0.1'
        url_host = f'[{connect_host}]' if ':' in connect_host else connect_host
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with tempfile.TemporaryDirectory(prefix='GTOpen launcher ') as tmp:
            repo = Path(tmp)
            (repo/'tools').mkdir()
            (repo/'target/desktop-runtime/release').mkdir(parents=True)
            (repo/'bin').mkdir()
            for name in ['launch.ps1', 'server-status.ps1', 'recover-scenarios.ps1']:
                shutil.copy2(ROOT/'tools'/name, repo/'tools'/name)
            executable = Path(os.environ.get('GTOPEN_TEST_SERVER', ROOT/'target/desktop-runtime/release/gto-server.exe'))
            if not executable.exists(): executable = ROOT/'target/release/gto-server.exe'
            shutil.copy2(executable, repo/'target/desktop-runtime/release/gto-server.exe')
            (repo/'bin/cargo.cmd').write_text('@echo off\necho built>>"%~dp0builds.txt"\nexit /b 0\n')
            env = os.environ.copy()
            env.update(USERPROFILE=str(repo), PATH=str(repo/'bin')+os.pathsep+env['PATH'],
                       SOLVER_GPU='0', SOLVER_THREADS='2')
            env.pop('GTOPEN_HOST', None)
            if bind_host is not None: env['GTOPEN_HOST'] = bind_host
            port = free_port(connect_host)
            url = f'http://{url_host}:{port}'
            command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                       str(repo/'tools/launch.ps1'), '-NoBrowser', '-Port', str(port)]
            children = []
            try:
                for i in range(2):
                    with (repo/f"launch-{i}.log").open("w") as output_file:
                        children.append(subprocess.Popen(command, env=env, stdout=output_file,
                            stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW))
                for child in children: child.wait(timeout=60)
                output = [(repo/f"launch-{i}.log").read_text() for i in range(2)]
                for p, text in zip(children, output): self.assertEqual(p.returncode, 0, text)
                self.assertEqual((repo/'bin/builds.txt').read_text().splitlines(), ['built'])
                self.assertEqual(sum('Reusing the running app' in text for text in output), 1)
                self.assertTrue(all(url in text for text in output), output)
                status = json.load(opener.open(url+'/api/status'))
                self.assertEqual(status['state'], 'idle')
                # Exercise save/list/delete over HTTP, including the colon that
                # previously hid scenario data in an NTFS alternate stream.
                name = '8-max $2/2: test scenario'
                def request(path, body):
                    req = urllib.request.Request(url+path,
                        data=json.dumps(body).encode(), headers={'Content-Type':'application/json'})
                    return json.load(opener.open(req))
                request('/api/preflop/scenarios/save', {'name':name, 'scenario':{'players':8, 'stack':150}})
                saved = json.load(opener.open(url+'/api/preflop/scenarios'))
                self.assertEqual(saved, [{'name':name, 'players':8, 'stack':150}])
                ordinary = list((repo/'saves/scenarios').glob('*.json'))
                self.assertEqual(len(ordinary), 1)
                self.assertGreater(ordinary[0].stat().st_size, 0)
                request('/api/preflop/scenarios/delete', {'name':name})
                self.assertFalse(ordinary[0].exists())
            finally:
                for child in children:
                    if child.poll() is None: child.kill(); child.wait()
                for proc in psutil.process_iter(['exe']):
                    if proc.info['exe'] and Path(proc.info['exe']).resolve() == (repo/'target/desktop-runtime/release/gto-server.exe').resolve():
                        proc.kill(); proc.wait(10)

    def test_other_http_service_is_not_opened_or_replaced(self):
        self.check_other_http_service('127.0.0.1')

    def test_other_ipv6_http_service_is_not_opened_or_replaced(self):
        self.check_other_http_service('::1')

    def check_other_http_service(self, bind_host):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.end_headers(); self.wfile.write(b'{"state":"idle"}')
            def log_message(self, *args): pass
        class Server(http.server.ThreadingHTTPServer):
            address_family = socket.AF_INET6 if ':' in bind_host else socket.AF_INET
        server = Server((bind_host, 0), Handler)
        env = os.environ.copy()
        env['GTOPEN_HOST'] = bind_host
        url_host = f'[{bind_host}]' if ':' in bind_host else bind_host
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                '-File', str(ROOT/'tools/launch.ps1'), '-NoBrowser', '-Port', str(server.server_port)],
                capture_output=True, text=True, timeout=30, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(result.returncode, 1, result.stdout+result.stderr)
            self.assertIn('occupied', result.stdout.lower())
            self.assertNotIn('Building release', result.stdout)
            self.assertEqual(opener.open(f'http://{url_host}:{server.server_port}/').status, 200)
        finally:
            server.shutdown(); server.server_close(); thread.join()


    def test_endpoint_urls_keep_family_and_literal_validation(self):
        helper = str(ROOT/'tools/server-status.ps1').replace("'", "''")
        script = f". '{helper}'; " + r"""
$cases = @(
    @('', 'http://127.0.0.1:4242'),
    @('   ', 'http://127.0.0.1:4242'),
    @(' 127.0.0.1 ', 'http://127.0.0.1:4242'),
    @('0.0.0.0', 'http://127.0.0.1:4242'),
    @('::', 'http://[::1]:4242'),
    @(' ::1 ', 'http://[::1]:4242'),
    @('192.0.2.1', 'http://192.0.2.1:4242'),
    @('2001:db8::1', 'http://[2001:db8::1]:4242')
)
foreach ($case in $cases) {
    $actual = (Get-GTOpenEndpoint 4242 -BindHost $case[0]).Url
    if ($actual -ne $case[1]) { throw "Expected $($case[1]), got $actual" }
}
foreach ($bad in @('localhost', '[::1]', '1.2.3.4:5', '127.1',
    '2130706433', '0x7f000001', '127.00.0.1', '256.1.1.1', 'fe80::1%1')) {
    try {
        Get-GTOpenEndpoint 4242 -BindHost $bad
        throw "Unexpectedly accepted $bad"
    } catch {
        if ($_.Exception.Message -notmatch 'is not an IP address') { throw }
    }
}
# Expected, caught rejections can leave PowerShell's success flag false.
exit 0
"""
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
            capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)

    def test_invalid_host_fails_before_building_or_starting(self):
        env = os.environ.copy()
        env['GTOPEN_HOST'] = 'localhost'
        result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', str(ROOT/'tools/launch.ps1'), '-NoBrowser', '-Port', str(free_port())],
            env=env, capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('is not an IP address', result.stdout+result.stderr)
        self.assertNotIn('Checking for GTOpen', result.stdout)
        self.assertNotIn('Building release', result.stdout)

    def test_wildcard_readiness_uses_matching_loopback_without_proxy(self):
        # Only the stub's loopback socket is exposed, never a wildcard app API.
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps(dict(state='idle', iteration=0, history=[],
                    tree=None, spot_request=None)).encode())
            def log_message(self, *args): pass
        for bind_host, connect_host in [('0.0.0.0', '127.0.0.1'), ('::', '::1')]:
            with self.subTest(bind_host=bind_host):
                class Server(http.server.ThreadingHTTPServer):
                    address_family = socket.AF_INET6 if ':' in connect_host else socket.AF_INET
                server = Server((connect_host, 0), Handler)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                try:
                    env = os.environ.copy()
                    env.update(GTOPEN_HOST=bind_host, HTTP_PROXY='http://127.0.0.1:1',
                               HTTPS_PROXY='http://127.0.0.1:1', ALL_PROXY='http://127.0.0.1:1')
                    helper = str(ROOT/'tools/server-status.ps1').replace("'", "''")
                    script = f". '{helper}'; Get-GTOpenServerState {server.server_port}"
                    result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                        env=env, capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
                    self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
                    self.assertEqual(result.stdout.strip(), 'Ready', result.stdout+result.stderr)
                finally:
                    server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__': unittest.main()
