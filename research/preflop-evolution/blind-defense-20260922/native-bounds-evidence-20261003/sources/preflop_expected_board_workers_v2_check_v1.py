"""File-only prospective wrapper controls; no native process or poker calculation.

The provider/values and native process receipt are deliberately synthetic. Only
run_native is replaced: the actual native_execution_v2 verifier reads and checks
these new ordinary files. Fabricated child identity is not owned-process evidence.
The control checks exact wrapper argv/bounds/provenance and refusal timing.
"""
import copy
import json
import os
from pathlib import Path
import time
import traceback
import types
from unittest.mock import patch

import psutil
import preflop_expected_board_workers_v2 as worker
import preflop_expected_native_execution_v2 as native
from preflop_expected_board_workers_check_v1 import SyntheticProvider

STAGE = Path(__file__).resolve().parent
REVIEW = STAGE/'preflop-expected-board-worker-v2-integration-review-v1'
ROOT = REVIEW/'software-control-v1'
SOURCE_PINS = {str(Path(p).resolve()):worker.sha(p) for p in (
    worker.__file__, native.__file__, STAGE/'preflop_expected_board_workers_v1.py',
    STAGE/'preflop_expected_board_workers_check_v1.py', __file__)}

def save(path, document):
    with Path(path).open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(document,indent=2,allow_nan=False)+'\n')

class FileOnlyNative:
    def __init__(self, mutate=None):
        self.mutate = mutate or (lambda result:None)
        self.calls, self.checks = [], []

    def run_native(self, executable, arguments, *, folder, label, expected_identities,
                   guard, timeout, max_output_bytes, direct_outputs):
        guard()
        assert direct_outputs == (), 'Board must declare no direct outputs'
        assert arguments == [str(worker._STATE['context_path']),str(folder/'request.json'),
            '--output-byte-limit='+str(worker._STATE['runtime_limits']['max_output_bytes'])]
        self.calls.append(dict(arguments=arguments,timeout=timeout,
            max_output_bytes=max_output_bytes,direct_outputs=list(direct_outputs)))
        request = json.loads(Path(arguments[1]).read_bytes())
        stdout,stderr,rp = [folder/(label+suffix) for suffix in
            ('-stdout.bin','-stderr.bin','-receipt.json')]
        with stdout.open('xb') as stream:
            stream.write(json.dumps(dict(synthetic=True,board=request['board'])).encode())
        with stderr.open('xb') as stream: stream.write(b'')
        start = time.time()
        argv = [str(executable),*arguments]
        receipt = dict(format=2,method=native.METHOD,outcome='success',
            executable=str(executable),argv=argv,expected_identities=dict(expected_identities),
            caller=dict(pid=worker._STATE['pid'],creation_time=worker._STATE['creation_time']),
            # Deliberately fabricated software fixture, never a launched process.
            process=dict(pid=os.getpid()+1,parent_pid=os.getpid(),creation_time=start,observed_argv=argv),
            folder=str(folder),label=label,direct_outputs=[],direct_output_artifacts=[],
            started_unix=start,terminal_unix=time.time(),returncode=0,
            timeout_seconds=timeout,max_output_bytes=max_output_bytes,stdin=None,
            stdout=dict(path=str(stdout),exists=True,bytes=stdout.stat().st_size,sha256=worker.sha(stdout)),
            stderr=dict(path=str(stderr),exists=True,bytes=0,sha256=worker.sha(stderr)))
        result = dict(format=2,method=native.METHOD,receipt_path=str(rp),receipt_sha256=None,
            stdout_path=str(stdout),stdout_sha256=receipt['stdout']['sha256'],
            stderr_path=str(stderr),stderr_sha256=receipt['stderr']['sha256'],receipt=receipt)
        self.mutate(result)
        save(rp,result['receipt']); result['receipt_sha256'] = worker.sha(rp)
        return result

    def verify_native(self, result, *, executable, arguments, expected_identities,
                      timeout, max_output_bytes, direct_outputs):
        assert direct_outputs == ()
        self.checks.append(dict(arguments=arguments,timeout=timeout,
            max_output_bytes=max_output_bytes,direct_outputs=list(direct_outputs)))
        return native.verify_native(result,executable=executable,arguments=arguments,
            expected_identities=expected_identities,timeout=timeout,
            max_output_bytes=max_output_bytes,direct_outputs=direct_outputs)

def setup(name, mutate=None):
    folder = ROOT/name; folder.mkdir()
    context,exe,source = [folder/name for name in ('context.json','never-executed.fake','source.fake')]
    for path,data in ((context,b'{"synthetic":true}\r\n'),(exe,b'NEVER EXECUTE'),(source,b'synthetic source')):
        with path.open('xb') as stream: stream.write(data)
    provider, adapter = SyntheticProvider(),FileOnlyNative(mutate)
    limits = worker._limits(dict(max_worker_seconds=60,native_timeout_seconds=10))
    memory = types.SimpleNamespace(available=worker.RAM_RESERVE_BYTES)
    disk = types.SimpleNamespace(free=worker.DISK_RESERVE_BYTES)
    probe = types.SimpleNamespace(virtual_memory=lambda:memory,disk_usage=lambda path:disk,
        Process=lambda:types.SimpleNamespace(memory_info=lambda:types.SimpleNamespace(rss=1000)))
    worker._STATE = dict(prepared=provider,recipe=copy.deepcopy(provider.recipe),
        plan=copy.deepcopy(provider._plan),context_path=context,executable=exe,folder=folder,
        identities={str(path):worker.sha(path) for path in (context,exe,source)},
        source_identities={str(Path(path).resolve()):worker.sha(path)
            for path in (worker.__file__,native.__file__)},runtime_limits=limits,
        began=time.monotonic(),initialized_unix=time.time(),pid=os.getpid(),
        creation_time=psutil.Process().create_time(),psutil=probe,
        production_available=lambda:True,native=adapter,cancel_event=None)
    return folder,provider,adapter

controls = []
def control(name, function):
    began = time.monotonic()
    function()
    controls.append(dict(name=name,outcome='pass',seconds=time.monotonic()-began))

def valid():
    folder,provider,adapter = setup('valid')
    second = worker.complete(1,provider._plan['boards'][1].copy())
    first = worker.complete(0,provider._plan['boards'][0].copy())
    assert [second['result']['draw_index'],first['result']['draw_index']] == [1,0]
    for returned in (first,second):
        result = returned['result']
        assert result['format'] == 2 and result['method'] == worker.METHOD
        assert worker.sha(returned['path']) == returned['sha256']
        assert json.loads(Path(returned['path']).read_bytes()) == result
        request = json.loads(Path(result['request_artifact']).read_bytes())
        assert request == provider.request(result['board'])[0]
        assert [len(hands) for hands in request['hands']] == [1081,1081]
        assert result['request_document_sha256'] == worker._digest(request)
        assert result['invocation_identities'] == {**result['native_identities'],
            result['request_artifact']:result['request_sha256']}
        assert result['tree_sha256'] == worker.sha(result['tree_artifact'])
        assert result['record']['policy_recipe_sha256'] == result['recipe_sha256']
        assert result['plan_sha256'] == worker._digest(provider._plan)
        assert result['native_invocation']['receipt']['direct_outputs'] == []
        assert result['worker_source_identities'] == worker._STATE['source_identities']
    assert len(adapter.calls) == 2 and len(adapter.checks) == 4
    assert provider.reductions == 2
    save(folder/'scope.json',dict(synthetic=True,native_process_launched=False,
        provider='SyntheticProvider',calls=adapter.calls,actual_verifier_calls=adapter.checks,
        returned=[dict(path=r['path'],sha256=r['sha256']) for r in (second,first)]))

def refusal(name,mutate=None,pre=None,after_reduce=None,error=ValueError,expected_reductions=0):
    folder,provider,adapter = setup(name,mutate)
    if pre: pre(folder,provider,adapter)
    if after_reduce: provider.after_reduce = lambda:after_reduce(folder,provider,adapter)
    try: worker.complete(0,provider._plan['boards'][0].copy())
    except error as exc:
        assert provider.reductions == expected_reductions
        assert not (folder/'board-000'/'result.json').exists()
        save(folder/'refusal.json',dict(expected=True,type=type(exc).__name__,message=str(exc),
            reductions=provider.reductions,native_process_launched=False))
    else: raise AssertionError('Expected refusal: '+name)

def altered_receipt(field,value):
    return lambda result:result['receipt'].__setitem__(field,value)

def contract_limits():
    base = dict(max_worker_seconds=60,native_timeout_seconds=10)
    assert worker._limits(base)['max_output_bytes'] == 2_000_000_000
    assert base == dict(max_worker_seconds=60,native_timeout_seconds=10)
    for value in (256,257,64_000_000,2_000_000_000):
        assert worker._limits({**base,'max_output_bytes':value})['max_output_bytes'] == value
    for value in (0,1,255,2_000_000_001,8_000_000_000,True,256.0,'256'):
        try: worker._limits({**base,'max_output_bytes':value})
        except ValueError: pass
        else: raise AssertionError(('Incompatible prospective cap accepted',value))
    save(ROOT/'limit-contract.json',dict(default=2_000_000_000,accepted=[256,257,64_000_000,2_000_000_000],
        refused=[0,1,255,2_000_000_001,8_000_000_000,True,256.0,'256']))

def legacy_result(result):
    result.pop('format'); result.pop('method')
    result['receipt']['format'] = 1
    result['receipt']['method'] = 'native-process-bound-export-v1'

def changed_request(result):
    Path(result['receipt']['argv'][2]).write_bytes(b'{}')

def changed_stdout(result):
    Path(result['stdout_path']).write_bytes(b'{}')

def cancel_pre(folder,provider,adapter):
    worker._STATE['cancel_event'] = types.SimpleNamespace(is_set=lambda:True)

def wrong_order(folder,provider,adapter):
    worker._STATE['plan']['boards'][0].reverse()

def changed_source_after(folder,provider,adapter):
    (folder/'source.fake').write_bytes(b'changed synthetic source')

def wrong_parent(result):
    result['receipt']['process']['parent_pid'] += 1

def wrong_argv(result):
    result['receipt']['argv'] = result['receipt']['argv'][:-1]

def wrong_caller(result):
    result['receipt']['caller']['pid'] += 1
    result['receipt']['process']['parent_pid'] += 1

def wrong_direct(result):
    result['receipt']['direct_outputs'] = [dict(path=str(Path(result['stdout_path']).parent/'extra.json'),argument_index=3)]

def bad_domain(folder,provider,adapter):
    request = provider.request
    def altered(board):
        req,ids = request(board); req['hands'][1].pop(); return req,ids
    provider.request = altered

def forbidden_native(*args,**kwargs):
    raise AssertionError('Any subprocess launch is forbidden in this software control')

def main():
    ROOT.mkdir()
    began = time.monotonic(); previous = worker._STATE
    report = dict(format=1,scope='file-only synthetic wrapper/actual verifier controls; no native/poker work',
        synthetic_process_receipts=True,source_pins=SOURCE_PINS,controls=controls)
    try:
        with patch.object(native.subprocess,'Popen',side_effect=forbidden_native), \
                patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'-1'}):
            control('prospective-limit-contract',contract_limits)
            control('valid-complete1081-bounded-argv-v2-receipt-order-artifacts',valid)
            control('legacy-native-v1-schema-refused-before-reduction',lambda:refusal('legacy',legacy_result))
            control('changed-native-cap-refused-before-reduction',lambda:refusal('cap',altered_receipt('max_output_bytes',1)))
            control('changed-native-timeout-refused-before-reduction',lambda:refusal('timeout',altered_receipt('timeout_seconds',9)))
            control('missing-bounded-cap-argv-refused-before-reduction',lambda:refusal('argv',wrong_argv))
            control('direct-output-declaration-refused-before-reduction',lambda:refusal('direct',wrong_direct))
            control('changed-request-hash-refused-before-reduction',lambda:refusal('request',changed_request))
            control('changed-stdout-refused-before-reduction',lambda:refusal('stdout',changed_stdout))
            control('wrong-native-parent-refused-before-reduction',lambda:refusal('parent',wrong_parent))
            control('other-worker-caller-refused-before-reduction',lambda:refusal('caller',wrong_caller))
            control('changed-source-after-reduction-refused-before-result',lambda:refusal('sourceafter',
                after_reduce=changed_source_after,expected_reductions=1))
            control('cancellation-refused-before-native',lambda:refusal('cancel',pre=cancel_pre,error=InterruptedError))
            control('plan-order-refused-before-native',lambda:refusal('order',pre=wrong_order))
            control('incomplete-private-domain-refused-before-native',lambda:refusal('domain',pre=bad_domain))
        assert all(worker.sha(path) == identity for path,identity in SOURCE_PINS.items())
        report.update(outcome='success',seconds=time.monotonic()-began,control_count=len(controls),
            native_launches=0,source_pins_unchanged=True)
    except BaseException as exc:
        report.update(outcome='failed',seconds=time.monotonic()-began,
            failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc()))
        raise
    finally:
        worker._STATE = previous
        report['files'] = {str(p):dict(sha256=worker.sha(p),bytes=p.stat().st_size)
            for p in ROOT.rglob('*') if p.is_file()}
        save(ROOT/'result.json',report)
        print(json.dumps(dict(outcome=report['outcome'],control_count=len(controls),
            result_path=str(ROOT/'result.json'),result_sha256=worker.sha(ROOT/'result.json'))))

if __name__ == '__main__': main()
