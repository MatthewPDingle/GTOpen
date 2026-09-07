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


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
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
        with tempfile.TemporaryDirectory(prefix='GTOpen launcher ') as tmp:
            repo = Path(tmp)
            (repo/'tools').mkdir()
            (repo/'target/release').mkdir(parents=True)
            (repo/'bin').mkdir()
            for name in ['launch.ps1', 'server-status.ps1', 'recover-scenarios.ps1']:
                shutil.copy2(ROOT/'tools'/name, repo/'tools'/name)
            executable = ROOT/'target/updated-server/release/gto-server.exe'
            if not executable.exists(): executable = ROOT/'target/release/gto-server.exe'
            shutil.copy2(executable, repo/'target/release/gto-server.exe')
            (repo/'bin/cargo.cmd').write_text('@echo off\necho built>>"%~dp0builds.txt"\nexit /b 0\n')
            env = os.environ.copy()
            env.update(USERPROFILE=str(repo), PATH=str(repo/'bin')+os.pathsep+env['PATH'], SOLVER_GPU='0')
            port = free_port()
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
                status = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/api/status'))
                self.assertEqual(status['state'], 'idle')
                # Exercise save/list/delete over HTTP, including the colon that
                # previously hid scenario data in an NTFS alternate stream.
                name = '8-max $2/2: test scenario'
                def request(path, body):
                    req = urllib.request.Request(f'http://127.0.0.1:{port}'+path,
                        data=json.dumps(body).encode(), headers={'Content-Type':'application/json'})
                    return json.load(urllib.request.urlopen(req))
                request('/api/preflop/scenarios/save', {'name':name, 'scenario':{'players':8, 'stack':150}})
                saved = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/api/preflop/scenarios'))
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
                    if proc.info['exe'] and Path(proc.info['exe']).resolve() == (repo/'target/release/gto-server.exe').resolve():
                        proc.kill(); proc.wait(10)

    def test_other_http_service_is_not_opened_or_replaced(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.end_headers(); self.wfile.write(b'{"state":"idle"}')
            def log_message(self, *args): pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                '-File', str(ROOT/'tools/launch.ps1'), '-NoBrowser', '-Port', str(server.server_port)],
                capture_output=True, text=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(result.returncode, 1, result.stdout+result.stderr)
            self.assertIn('occupied', result.stdout.lower())
            self.assertNotIn('Building release', result.stdout)
            self.assertEqual(urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/').status, 200)
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__': unittest.main()
