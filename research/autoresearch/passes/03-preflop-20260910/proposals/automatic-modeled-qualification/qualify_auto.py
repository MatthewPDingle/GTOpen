"""Explicit later-only modeled automatic-budget API qualification. No live mutations."""
import argparse
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'final-api-qualification'))
import qualify_api as reviewed
from qualify_api import HERE, ROOT, LAB, DEADLINE, ORIGINAL, CANDIDATE, HASHES
from qualify_api import get, live_idle, free_port, zero_hash, native, sha, write_new, require, owner
FIXED_ENV = {'SOLVER_THREADS':'16', 'RAYON_NUM_THREADS':'16', 'SOLVER_GPU':'1',
             'PREFLOP_EQ_SAMPLES':'1024', 'PREFLOP_GPU_LAYOUT_STATS':'1'}
SOLVE = {'iterations':2, 'check_every':2, 'target_gap':0.005}


def case_environment(inherited, budget, port, private):
    env=dict(inherited)
    for key in list(env):
        if key.startswith(('PREFLOP_MW_','PREFLOP_GPU_','PREFLOP_PHASE_')):
            env.pop(key)
    env.pop('SOLVER_GPU_MEM_MB',None)
    env.update(FIXED_ENV)
    if budget is not None:
        require(isinstance(budget,int) and budget>0,'invalid observed budget')
        env['SOLVER_GPU_MEM_MB']=str(budget)
    env.update(PORT=str(port),REALIZATION_FIT=str(private/'cache/realization_fit.json'))
    return env


def checkpoint(status):
    return (status.get('iteration') == 2 and status.get('phase') != 'measuring'
            and len(status.get('gaps',[])) == 6 and len(status.get('evs',[])) == 6)


def parse_layout(text, side):
    if side == 'candidate':
        rows = [json.loads(l.split(': ',1)[1]) for l in text.splitlines() if l.startswith('preflop gpu layout: ')]
        require(len(rows) <= 1, 'multiple candidate layouts')
        return rows[0] if rows else None
    batches = re.findall(r'preflop gpu: coupled multiway, 1024 particles, [0-9]+ reach CDFs, ([0-9]+)-particle batches', text)
    require(len(batches) <= 1, 'multiple original layouts')
    return {'multiway_batch':int(batches[0]), 'hu_cache_observation':'not emitted; inferred from same-budget literal reference'} if batches else None


def comparable(candidate, original):
    c,o=candidate.get('layout'),original.get('layout')
    return bool(c and o and c.get('batch_policy') == 'deployed_prepass'
        and c.get('multiway_batch') == c.get('literal_reference_multiway_batch') == o.get('multiway_batch')
        and isinstance(c.get('literal_reference_hu_cache_enabled'),bool)
        and c.get('hu_equity_cache_enabled') == c.get('literal_reference_hu_cache_enabled')
        and original['case']['budget_mb'] == c.get('budget_mb'))


def strict_comparator(d):
    require(d['iteration']==2 and d['payoff_model']=='coupled_deck_v1','wrong comparison state')
    require(d['headers_identical_after_point_lock_order_canonicalization'] and d['all_compared_values_finite'], 'metadata/nonfinite mismatch')
    require(d['invalid_effective_entries']==d['invalid_reach_classes']==0,'invalid policies/reaches')
    for row in [*d['raw_arenas'].values(),d['effective_average_strategy'],d['raw_arena_normalized_strategy']]:
        require(row['entries']==row['bit_equal']==row['finite_pairs'] and row['max_abs']==row['max_ulp']==0,'native exactness failure')


def run_case(case, input_native, folder, caches, pair_end):
    private = folder / case['side']
    (private / 'saves/preflop').mkdir(parents=True)
    (private / 'cache').mkdir()
    shutil.copy2(case['exe'], private / 'gto-server.exe')
    require(sha(private / 'gto-server.exe') == case['sha256'], 'copied executable changed')
    shutil.copy2(case['input'], private / 'saves/preflop/input.gtop')
    require(sha(private / 'saves/preflop/input.gtop') == case['input_sha256'], 'input copy changed')
    for name, item in caches.items():
        shutil.copy2(item['path'], private / 'cache' / name)
        require(sha(private / 'cache' / name) == item['sha256'], 'cache copy changed')
    env = case_environment(os.environ, case['budget_mb'], case['port'], private)
    env['PATH'] = str(ROOT / '.cuda-nvrtc/nvidia/cuda_nvrtc/bin') + os.pathsep + env['PATH']
    live_idle()
    require(time.monotonic() < pair_end, 'pair600second deadline before launch')
    require(dt.datetime.now(dt.timezone.utc) < DEADLINE, 'deadline before server launch')
    started = time.monotonic()
    result = {'case': case, 'statuses': [], 'completed': False, 'error': None}
    stop = threading.Event()
    failure = []
    with (private / 'server.log').open('x', encoding='utf-8') as log:
        process = subprocess.Popen([str(private / 'gto-server.exe')], cwd=private, env=env,
                                   stdout=log, stderr=subprocess.STDOUT, creationflags=subprocess.CREATE_NO_WINDOW)
        (HERE/'active.json').write_text(json.dumps({'running': True, 'event': 'api_qualification',
            'id': folder.name+'-'+case['side'], 'pid': process.pid, 'port': case['port'],
            'exe': str(private/'gto-server.exe'), 'log': str(private/'server.log')}), encoding='utf-8')
        def monitor():
            while not stop.wait(0.5):
                try:
                    live_idle()
                    require(dt.datetime.now(dt.timezone.utc) < DEADLINE, 'global deadline')
                    require(time.monotonic() < pair_end, 'pair600second deadline')
                    require(time.monotonic() - started < 240, 'case240second deadline')
                except Exception as error:
                    failure.append(str(error))
                    if process.poll() is None:
                        process.kill()  # Only this retained child handle, never the live app.
                    return
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        expected = None
        def own():
            require(not failure and process.poll() is None, 'owned server stopped: ' + '; '.join(failure))
            actual = owner(case['port'])
            require(actual['pid'] == process.pid and actual['sha256'] == case['sha256'], 'wrong isolated listener')
            if expected is not None:
                require(actual['created'] == expected['created'] and Path(actual['exe']).samefile(expected['exe']), 'listener identity changed')
            return actual
        def post(route, body):
            require(case['port'] != 56708 and route in ['/api/preflop/load', '/api/preflop/solve', '/api/preflop/node', '/api/preflop/save'], 'POST forbidden')
            own()
            request = urllib.request.Request(f'http://127.0.0.1:{case["port"]}{route}',
                json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
            before = time.monotonic()
            with urllib.request.urlopen(request, timeout=240) as response:
                value = json.load(response)
            return value, before, time.monotonic()
        try:
            while True:
                require(not failure and process.poll() is None, 'startup failed: ' + '; '.join(failure))
                try:
                    expected = own()
                    if get(case['port'], '/api/status')['state'] == 'idle':
                        break
                except (OSError, ValueError):
                    pass
                require(time.monotonic() - started < 60, 'startup timeout')
                time.sleep(0.2)
            result['owner'] = expected
            loaded, _, _ = post('/api/preflop/load', {'name': 'input'})
            require(loaded['iteration'] == 0 and loaded['config'] == input_native['header']['config'], 'load changed starting state')
            require(loaded['multiway_equity_model'] == 'coupled_deck_v1' and [s['profile'] for s in loaded['seats']] == input_native['header']['seat_profiles'] and [s['frozen'] for s in loaded['seats']] == input_native['header']['seat_frozen'], 'wrong models/seats')
            require(loaded.get('hero') == input_native['header']['hero'], 'hero changed on load')
            response, t0, ack = post('/api/preflop/solve', SOLVE)
            result.update(solve_response=response, post_ack_seconds=ack-t0)
            last_poll = t0
            while True:
                require(not failure and process.poll() is None, 'solve interrupted: ' + '; '.join(failure))
                poll_started = time.monotonic()
                status = get(case['port'], '/api/preflop/status')
                now = time.monotonic()
                result['statuses'].append({'seconds': now-t0, 'status': status})
                require(not status.get('error') and not status.get('gpu_note'), 'solver error/fallback: ' + str(status))
                if checkpoint(status):
                    result.update(first_published_checkpoint_seconds=now-t0,
                                  publication_interval_lower_seconds=last_poll-t0,
                                  publication_interval_upper_seconds=now-t0,
                                  final_status=status)
                    break
                require(status['state'] == 'running', 'solver ended before qualifying checkpoint')
                last_poll = poll_started
                time.sleep(0.2)
            require(status['gpu'] is True, 'GPU qualification fell back to CPU')
            require(all(math.isfinite(x) for x in status['gaps'] + status['evs']), 'nonfinite checkpoint')
            root, _, served = post('/api/preflop/node', {'path': []})
            result.update(first_strategy_response_seconds=served-t0, root_strategy=root)
            session = get(case['port'], '/api/preflop/session')
            require(session['iteration'] == 2 and session['state'] == 'done', 'final native state not2/done')
            saved, _, _ = post('/api/preflop/save', {'name': 'result'})
            require(saved.get('ok') is True and saved['iteration'] == 2, 'result save failed')
            output = private / 'saves/preflop/result.gtop'
            result_native = native(output)
            expected_header = dict(input_native['header'], iteration=2)
            require(result_native['header'] == expected_header, 'native metadata changed beyond iteration')
            result.update(completed=True, output=str(output), output_sha256=sha(output), native=result_native,
                          case_seconds=time.monotonic()-started)
        except Exception as error:
            result['error'] = str(error)
        finally:
            stop.set()
            thread.join(timeout=10)
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=30)
            result['guard_failures'] = failure
            write_new(private / 'result.json', result)
            (HERE/'active.json').write_text(json.dumps({'running': False,
                'last': folder.name+'-'+case['side']}), encoding='utf-8')
    if failure:
        result['completed'] = False
    result['layout'] = parse_layout((private/'server.log').read_text(errors='replace'), case['side'])
    result['timed_out'] = 'case240second deadline' in failure and not any(x != 'case240second deadline' for x in failure)
    write_new(private/'qualification.json', result)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--id',required=True)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    require(args.execute and os.name=='nt','explicit later --execute on Windows required')
    require(re.fullmatch('[A-Za-z0-9_-]+',args.id),'unsafe ID')
    require(json.loads((HERE/'active.json').read_text()).get('running') is False,'research queue active')
    require((DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()>=660,'need660seconds before deadline')
    live_idle()
    source_protocol=HERE/'extended-convergence-protocol.json'
    source_record=json.loads(source_protocol.read_text())['runs']['extended-convergence-modeled-original-a']
    source=Path(source_record['input'])
    require(sha(source)==source_record['input_sha256'],'frozen source changed')
    initial=native(source);h=initial['header']
    require(h['iteration']==0 and len(h['config']['positions'])==6 and h['multiway_equity_model']=='coupled_deck_v1','wrong modeled input')
    require(any(p is not None for p in h['seat_profiles']) and h['seat_profiles'][h['config']['positions'].index('BTN')] is None,'modeled opponents / BTN solver required')
    require(all(a['sha256']==zero_hash(a['elements']) for a in initial['arrays']),'input not zero initialized')
    folder=LAB/'target/research-api-qualification'/args.id
    folder.parent.mkdir(parents=True,exist_ok=True)
    require(shutil.disk_usage(folder.parent).free > source.stat().st_size*5+1024**3,'insufficient private disk')
    folder.mkdir(exist_ok=False)
    caches={name:{'path':str(LAB/'cache'/name),'sha256':sha(LAB/'cache'/name)} for name in ['preflop_eq169.bin','realization_fit.json']}
    deps={Path(x['path']).name:x['sha256'] for x in json.loads(source_protocol.read_text())['frozen_dependencies']}
    require(all(x['sha256']==deps[n] for n,x in caches.items()),'frozen cache changed')
    cases=[]
    for side,exe in [('candidate',CANDIDATE),('original',ORIGINAL)]:
        require(sha(exe)==HASHES[side],'runtime changed')
        cases.append({'side':side,'exe':str(exe),'sha256':HASHES[side],'port':free_port(),
            'input':str(source),'input_sha256':source_record['input_sha256'],'budget_mb':None})
    require(cases[0]['port']!=cases[1]['port'],'duplicate private ports; use new ID')
    comp=LAB/'target/release/examples/preflop_compare_saved.exe'
    comp_hash='155e8f1ee3661d29ab3e8e3e4ee9b33e02b7583e3c28cb5625b7b09702398e89'
    require(sha(comp)==comp_hash,'comparator changed')
    run_id=args.id+'-native-exact'
    require(not (HERE/'raw'/(run_id+'.log')).exists(),'comparator ID exists')
    protocol={'frozen_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'deadline_utc':DEADLINE.isoformat(),
        'case_timeout_seconds':240,'pair_timeout_seconds':600,'minimum_start_remaining_seconds':660,
        'cases':cases,'order':['candidate','original'],'fixed_environment':FIXED_ENV,'solve_body':SOLVE,
        'budget_rule':'Candidate environment removes SOLVER_GPU_MEM_MB; original pins exact candidate layout budget. No re-evaluation, no retries.',
        'cache_comparability':'Original does not log HU mode. Require candidate deployed_prepass actual batch/cache identical to its literal reference; original batch and exact budget corroborate that same source planner.',
        'source_protocol_sha256':sha(source_protocol),'caches':caches,'comparator':str(comp),'comparator_sha256':comp_hash,
        'runner_sha256':sha(__file__),'helper_sha256':{str(p):sha(p) for p in [Path(reviewed.__file__),Path(reviewed.__file__).parents[1]/'final-deployment/session_guard.py',HERE/'run_guarded.py',HERE/'assert_saved_exact.py']},
        'timeout_outcome':'candidate_completed_original_timeout is not parity/performance success',
        'comparison_gate':'Only both completed and same literal grouping/cache; otherwise explicit noncomparability. Full native + root semantic exactness, no tolerances.'}
    write_new(folder/'protocol.json',protocol)
    require((DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()>=660,'late after preflight')
    pair_end=time.monotonic()+600
    summary={'full_native_exact':False,'fixed_pair_only':True,'candidate_automatic_budget':True,'outcome':'incomplete'}
    try:
        candidate=run_case(cases[0],initial,folder,caches,pair_end)
        if not candidate['completed']:
            summary['outcome']='candidate_failed';return
        layout=candidate['layout']
        require(layout and isinstance(layout.get('budget_mb'),int) and layout['budget_mb']>0,'missing actual automatic budget')
        summary['candidate_layout']=layout
        cases[1]['budget_mb']=layout['budget_mb']
        write_new(folder/'original-resolved-budget.json',cases[1])
        original=run_case(cases[1],initial,folder,caches,pair_end)
        if not original['completed']:
            summary['outcome']='candidate_completed_original_timeout' if original['timed_out'] else 'candidate_completed_original_failed';return
        if not comparable(candidate,original):
            summary['outcome']='both_completed_noncomparable_layout';return
        require(candidate['native']==original['native'],'full native header/arena mismatch')
        require(candidate['root_strategy']==original['root_strategy'],'root semantic mismatch')
        remaining=min(pair_end-time.monotonic(),(DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds())
        require(remaining>15,'insufficient guarded comparator reserve')
        env=os.environ.copy();env['PREFLOP_VALIDATION_TIMEOUT']=str(int(remaining)-10)
        subprocess.run([sys.executable,str(HERE/'run_guarded.py'),run_id,str(comp),original['output'],candidate['output'],caches['preflop_eq169.bin']['path']],env=env,check=True,timeout=remaining,creationflags=subprocess.CREATE_NO_WINDOW)
        strict_comparator(json.loads((HERE/'raw'/(run_id+'.log')).read_text()))
        remaining=min(pair_end-time.monotonic(),(DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds())
        require(remaining>1,'deadline before assertion')
        subprocess.run([sys.executable,str(HERE/'assert_saved_exact.py'),run_id],check=True,timeout=remaining,creationflags=subprocess.CREATE_NO_WINDOW)
        summary.update(outcome='both_completed_full_native_exact',full_native_exact=True,comparator_run=run_id,
            first_checkpoint_seconds={'candidate':candidate['first_published_checkpoint_seconds'],'original':original['first_published_checkpoint_seconds']})
    except Exception as error:
        summary.update(outcome='qualification_failed',error=str(error));raise
    finally:
        summary['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
        write_new(folder/'summary.json',summary)
        print(str(folder/'summary.json'))


if __name__=='__main__':
    main()
