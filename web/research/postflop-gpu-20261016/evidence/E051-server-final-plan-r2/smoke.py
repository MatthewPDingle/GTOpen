"""Root-only isolated E051 API smoke; live process/executable explicitly excluded."""
import server_common as c
import json,math,socket,subprocess,sys,time,traceback,urllib.request
OUT=c.ROOT/'runs/E051-server-final-smoke'
PORT=43736
BASE='http://127.0.0.1:43736'
LIVE='http://127.0.0.1:43735'
OWNED=None
BINARY=None

def owned_listener():
    assert OWNED is not None and OWNED.poll() is None and OWNED.pid!=c.LIVE['pid']
    code=f"$ls=@(Get-NetTCPConnection -LocalPort 43736 -State Listen -ErrorAction Stop); $p=Get-CimInstance Win32_Process -Filter 'ProcessId={int(OWNED.pid)}'; @{{listeners=@($ls|Select-Object -ExpandProperty OwningProcess -Unique);pid=$p.ProcessId;path=$p.ExecutablePath}} | ConvertTo-Json -Compress"
    value=c.powershell(code)
    assert value['listeners']==[OWNED.pid] and value['pid']==OWNED.pid
    assert c.Path(value['path']).resolve()==BINARY.resolve()!=c.Path(c.LIVE['executable']).resolve()
    assert c.sha(value['path'])==c.sha(BINARY)!=c.LIVE['sha256'];return value

def request(path,body=None,base=BASE,timeout=10):
    assert base in (BASE,LIVE)
    if body is not None:
        assert base==BASE,'POST is restricted to the owned isolated43736 server'
        owned_listener()
    data=None if body is None else json.dumps(body).encode('utf-8')
    req=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=timeout) as response:return json.load(response)

def live_state():
    c.live_identity()
    return {path:request(path,base=LIVE) for path in ['/api/status','/api/preflop/status','/api/reports/status']}

def port_free():
    with socket.socket() as probe:
        probe.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1);probe.bind(('127.0.0.1',PORT))

def unit_gate():
    report=c.pin(c.AUTH['server_unit_report']);assert report==c.ROOT/'runs/V051-server-unit/report.json'
    j=c.read(report);unit,manifest=c.binary('E051-server-tests')
    assert j['status']=='measured' and j['returncode']==0 and j['test_pass_count']==20 and j['binary_sha256']==c.sha(unit)
    assert j['command']==[str(unit),'--nocapture','--test-threads=1']
    raw=report.parent/'stdout.log';assert c.sha(raw)==j['stdout_sha256']
    text=raw.read_text(encoding='utf-8');import re
    assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)==[('20','0','1','0','0')]
    expected=c.read(c.HERE/'unit-inventory.json')
    assert sorted(re.findall(r'^test ([\w:]+) \.\.\.',text,re.M))==expected['expected_test_names']
    assert 'test report_tests::report_adaptation_benchmark ... ignored' in text
    assert 'FAILED' not in text
    return {'report_sha256':c.sha(report),'stdout_sha256':c.sha(raw),'binary_sha256':c.sha(unit),'manifest_sha256':c.sha(manifest)}

def finite_tree(value):
    if isinstance(value, float):
        assert math.isfinite(value), value
    elif isinstance(value, dict):
        for child in value.values():
            finite_tree(child)
    elif isinstance(value, list):
        for child in value:
            finite_tree(child)


def check_node(node):
    finite_tree(node)
    assert node["node_type"] == "action", node["node_type"]
    assert len(node["board"]) == 5
    assert node["actions"] and len(node["players"]) == 2
    actor = node["player"]
    checked = 0
    max_sum_error = 0.0
    for player in node["players"]:
        assert player["hands"]
        for hand in player["hands"]:
            if hand["reach"] > 0 and hand["valid"] > 0:
                assert isinstance(hand["ev"], (int, float)) and math.isfinite(hand["ev"])
                assert isinstance(hand["eq"], (int, float)) and math.isfinite(hand["eq"])
    for hand in node["players"][actor]["hands"]:
        strategy = hand["strategy"]
        assert len(strategy) == len(node["actions"])
        assert all(-1e-7 <= x <= 1.0000001 for x in strategy)
        delta = abs(sum(strategy) - 1)
        assert delta < 1e-5, delta
        max_sum_error = max(max_sum_error, delta)
        checked += 1
    return {"acting_hands_checked": checked, "max_strategy_sum_error": max_sum_error,
            "actions": [a["label"] for a in node["actions"]], "player": actor}


def main():
    global OWNED,BINARY
    assert len(sys.argv)==2,'smoke authorization SHA required';c.initialize('smoke',sys.argv[1])
    with c.ar.exclusive_lock(c.ROOT/'gpu-run.lock'):
        c.verify();units=unit_gate();assert not OUT.exists();port_free();OUT.mkdir()
        BINARY,manifest=c.binary('E051-gto-server')
        assert c.sha(manifest)==c.AUTH['server_manifest_sha256'] and c.sha(BINARY)==c.AUTH['server_binary_sha256']
        result={'started_at':c.now(),'passed':False,'binary':str(BINARY),'binary_sha256':c.sha(BINARY),'manifest_sha256':c.sha(manifest),'authorization_sha256':sys.argv[1],'acceptance':c.AUTH['acceptance'],'port':PORT,'working_directory':str(c.REPO),'unit_gate':units,'scope':'Isolated API correctness smoke only; no performance/deployment claim'}
        before=None
        try:
            before=live_state();c.ar.refuse_active(before);c.save(OUT/'live-before.json',before)
            e=c.env();e.update(PORT=str(PORT),SOLVER_GPU='1',SOLVER_COMPRESS='1')
            with (OUT/'stdout.log').open('xb') as out,(OUT/'stderr.log').open('xb') as err:
                OWNED=subprocess.Popen([str(BINARY)],cwd=c.REPO,env=e,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
            assert OWNED.pid!=c.LIVE['pid'];result['owned_pid']=OWNED.pid
            c.save(OUT/'launch.json',dict(result,live_exclusion=c.LIVE,environment={'PORT':str(PORT),'SOLVER_GPU':'1','SOLVER_COMPRESS':'1','RAYON_NUM_THREADS':'16','NVRTC':str(c.NVRTC)}))
            (OUT/'server.pid').write_text(str(OWNED.pid),encoding='ascii')
            deadline=time.monotonic()+60
            while True:
                assert OWNED.poll() is None,'Owned test server exited before readiness'
                try:initial=request('/api/status',timeout=2);break
                except (OSError,TimeoutError):
                    if time.monotonic()>deadline:raise TimeoutError('Readiness60s')
                    time.sleep(.1)
            result['listener_identity']=owned_listener()
            assert initial['state']=='idle' and initial['tree'] is None;c.save(OUT/'initial-status.json',initial)
            spot=c.read(c.HERE/'spot-request.json');solve=c.read(c.HERE/'solve-request.json')
            c.save(OUT/'spot-request.json',spot);c.save(OUT/'tree.json',request('/api/spot',spot,timeout=30))
            c.save(OUT/'solve-request.json',solve);c.save(OUT/'solve-response.json',request('/api/solve',solve))
            deadline=time.monotonic()+120;polls=[]
            while True:
                assert OWNED.poll() is None
                status=request('/api/status');polls.append({'at':c.now(),'status':status})
                if status['state']!='running':break
                if time.monotonic()>deadline:raise TimeoutError('Isolated solve120s')
                time.sleep(.1)
            c.save(OUT/'status-polls.json',polls);c.save(OUT/'final-status.json',status);finite_tree(status)
            assert status['state']=='done' and status['iteration']==100 and status['gpu'] is True
            assert not status['error'] and not status['gpu_note']
            for key in ['exploit_chips','exploit_pct','elapsed_secs']:assert isinstance(status[key],(int,float)) and math.isfinite(status[key])
            node=request('/api/node',{'path':[]},timeout=30);c.save(OUT/'root-node.json',node);result['root_checks']=check_node(node)
            child=request('/api/node',{'path':[{'type':'action','index':0}]},timeout=30);c.save(OUT/'check-child-node.json',child);result['child_checks']=check_node(child)
            c.verify();assert c.sha(BINARY)==result['binary_sha256'] and c.sha(manifest)==result['manifest_sha256']
            result['final_status']=status;result['passed']=True
        except BaseException as exc:
            result['passed']=False;result['error']=repr(exc);result['traceback']=traceback.format_exc()
        finally:
            # Only the Popen handle created above may be terminated/killed. No taskkill,
            # port-occupant kill, live restart, alternate launcher or equivalent retry.
            try:
                if OWNED is not None:
                    assert OWNED.pid!=c.LIVE['pid']
                    if OWNED.poll() is None:OWNED.terminate()
                    try:OWNED.wait(timeout=10)
                    except subprocess.TimeoutExpired:OWNED.kill();OWNED.wait(timeout=10)
                    result['owned_process_exit_code']=OWNED.returncode;result['owned_process_stopped']=OWNED.poll() is not None
                port_free();result['test_port_released']=True
            except BaseException as exc:result['passed']=False;result['cleanup_error']=repr(exc)
            try:
                after=live_state();c.save(OUT/'live-after.json',after);result['live_api_unchanged']=before==after
                assert before==after,'Live API changed during isolated smoke'
                assert c.sha(BINARY)==result['binary_sha256'] and c.sha(manifest)==result['manifest_sha256']
                c.verify()
            except BaseException as exc:result['passed']=False;result['final_verification_error']=repr(exc)
            result['finished_at']=c.now();c.save(OUT/'result.json',result)
    print(json.dumps({k:result.get(k) for k in ['passed','owned_pid','binary_sha256','error','owned_process_stopped','test_port_released','live_api_unchanged']}),flush=True)
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
