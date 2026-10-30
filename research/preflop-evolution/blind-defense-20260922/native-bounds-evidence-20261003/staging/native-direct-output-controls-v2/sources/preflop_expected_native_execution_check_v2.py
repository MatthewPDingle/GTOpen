"""Actual small Python-child controls; no poker/native scientific execution."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
STAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(STAGE))
import psutil
import preflop_expected_native_execution_v2 as native

CHILD = r'''import json,os,sys,time
from pathlib import Path
import psutil
mode=sys.argv[1];out=Path(sys.argv[2]);aux=Path(sys.argv[3]) if len(sys.argv)>3 else None
if mode=='quiet-large':out.write_bytes(b'x'*4096)
elif mode=='combined':
    out.write_bytes(b'd'*600);sys.stdout.buffer.write(b'o'*400);sys.stderr.buffer.write(b'e'*400)
elif mode=='immediate':out.write_bytes(b'immediate direct')
elif mode=='missing':pass
elif mode=='fail':
    out.write_bytes(b'partial-direct');sys.stderr.write('fixture nonzero\n');sys.exit(7)
elif mode=='wait':
    out.write_bytes(b'partial-before-stop');sys.stdout.write('ready\n');sys.stdout.flush()
    while True:time.sleep(.02)
else:
    if mode=='stdin':out.write_bytes(sys.stdin.buffer.read())
    elif mode=='modify-source':out.write_bytes(b'direct-before-source-refusal');aux.write_bytes(b'changed source')
    elif mode!='stdio':out.write_bytes(b'genuine direct output\n')
    me=psutil.Process();parent=psutil.Process(os.getppid())
    print(json.dumps(dict(pid=os.getpid(),creation_time=me.create_time(),parent_pid=parent.pid,
        parent_creation_time=parent.create_time(),observed_cmdline=me.cmdline(),
        executable=me.exe(),cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'))))
'''


def digest(raw): return hashlib.sha256(raw).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, sort_keys=True, separators=(',', ':')); stream.write('\n')


def main(folder):
    folder = Path(folder).resolve(); folder.mkdir(parents=True, exist_ok=False)
    started = time.monotonic(); receipts = []; refused = []; passed = []; artifacts = []
    original_paths = [STAGE/'preflop_expected_native_execution_v1.py',
        Path(r'T:\Dev\GTOpen\tools\research\preflop_expected_native_execution_v1.py')]
    original = {str(p):native.sha(p) for p in original_paths}
    sources = folder/'sources'; sources.mkdir()
    active_sources = [Path(native.__file__).resolve(), Path(__file__).resolve()]
    snapshots = {}
    for path in active_sources:
        raw = path.read_bytes(); snapshot = sources/path.name
        with snapshot.open('xb') as stream: stream.write(raw)
        assert native.sha(snapshot) == digest(raw)
        snapshots[str(path)] = dict(sha256=digest(raw), snapshot=str(snapshot))
    child = sources/'software_child_v2.py'
    with child.open('x', encoding='utf-8', newline='\n') as stream: stream.write(CHILD)
    exe = str(Path(sys.executable).resolve())
    common_ids = {exe:native.sha(exe), str(child):native.sha(child),
                  str(Path(native.__file__).resolve()):native.sha(native.__file__)}
    save(folder/'attempt.json', dict(format=2, purpose='Software children only; no scientific work',
        started_unix=time.time(), pid=os.getpid(), creation_time=psutil.Process().create_time(),
        argv=sys.argv, cuda_visible_devices=os.environ['CUDA_VISIBLE_DEVICES'], sources=snapshots,
        original_v1_sources=original, software_child_sha256=native.sha(child), executable_sha256=common_ids[exe]))

    def call(name, mode, *, budget=16_384, timeout=3, guard=lambda:None, auxiliary=None,
             stdin_path=None, direct=True, nested=False):
        root = folder/name; root.mkdir()
        parent = root/'nested' if nested else root
        if nested: parent.mkdir()
        output = parent/'direct.bin'; args = ['-B', str(child), mode, str(output)]
        ids = dict(common_ids)
        if auxiliary is not None: args.append(str(auxiliary)); ids[str(auxiliary)] = native.sha(auxiliary)
        if stdin_path is not None: ids[str(stdin_path)] = native.sha(stdin_path)
        specs = [dict(path=str(output), argument_index=4)] if direct else []
        kwargs = dict(executable=exe, arguments=args, expected_identities=ids,
            timeout=timeout, max_output_bytes=budget, direct_outputs=specs, stdin_path=stdin_path)
        try:
            launch = dict(kwargs)
            if not direct: launch.pop('direct_outputs')
            result = native.run_native(**launch, folder=root, label='call', guard=guard)
        except BaseException as exc:
            rp = root/'call-receipt.json'
            if rp.exists(): receipts.append(dict(path=str(rp), sha256=native.sha(rp)))
            return None, kwargs, root, exc
        receipts.append(dict(path=result['receipt_path'], sha256=result['receipt_sha256']))
        return result, kwargs, root, None

    def valid(name, mode='valid', **options):
        result, kwargs, root, error = call(name, mode, **options)
        assert error is None, repr(error)
        native.verify_native(result, **kwargs)
        passed.append(name); artifacts.append(result)
        return result, kwargs, root

    def failed(name, mode, expected_type, **options):
        result, kwargs, root, error = call(name, mode, **options)
        assert result is None and isinstance(error, expected_type), repr(error)
        receipt = json.loads((root/'call-receipt.json').read_bytes())
        assert receipt['outcome']=='failed' and receipt['argv']==[exe,*kwargs['arguments']]
        assert receipt['direct_outputs']==kwargs['direct_outputs']
        assert len(receipt['direct_output_artifacts'])==len(kwargs['direct_outputs'])
        for witness in [receipt['stdout'],receipt['stderr'],*receipt['direct_output_artifacts']]:
            if witness['exists']:
                assert 'error' not in witness and Path(witness['path']).stat().st_size==witness['bytes']
                assert native.sha(witness['path'])==witness['sha256']
            else: assert witness['bytes'] is None and witness['sha256'] is None
        refused.append(name); return receipt, root

    try:
        result, kwargs, root = valid('valid-direct', nested=True)
        independent = json.loads(Path(result['stdout_path']).read_bytes())
        receipt = result['receipt']
        assert independent['pid']==receipt['process']['pid']
        assert independent['parent_pid']==receipt['caller']['pid']==os.getpid()
        assert abs(independent['creation_time']-receipt['process']['creation_time'])<.002
        assert abs(independent['parent_creation_time']-receipt['caller']['creation_time'])<.002
        assert independent['observed_cmdline']==receipt['argv']==receipt['process']['observed_argv']
        assert Path(independent['executable']).resolve()==Path(exe)
        assert independent['cuda_visible_devices']=='-1'
        passed.append('independent-os-child-parent-creation-and-argv-authentication')
        valid('stdout-only-default', mode='stdio', direct=False)
        immediate, _, _ = valid('immediate-valid-exit', mode='immediate', budget=100)
        assert immediate['receipt']['stdout']['bytes']==immediate['receipt']['stderr']['bytes']==0
        stdinput = folder/'stdin-fixture.bin'
        with stdinput.open('xb') as stream: stream.write(b'exact standard input\x00\xff')
        stdin_result, _, _ = valid('registered-stdin', mode='stdin', stdin_path=str(stdinput))
        assert Path(stdin_result['receipt']['direct_output_artifacts'][0]['path']).read_bytes()==stdinput.read_bytes()
        large, _ = failed('large-direct-empty-stdio','quiet-large',ValueError,budget=1000)
        assert large['stdout']['bytes']==large['stderr']['bytes']==0 and large['direct_output_artifacts'][0]['bytes']==4096
        assert large['returncode']==0
        combined, _ = failed('combined-only-overage','combined',ValueError,budget=1000)
        sizes = [combined['stdout']['bytes'],combined['stderr']['bytes'],combined['direct_output_artifacts'][0]['bytes']]
        assert max(sizes)<1000 and sum(sizes)==1400
        missing, _ = failed('missing-direct','missing',ValueError)
        assert missing['direct_output_artifacts'][0]['exists'] is False and missing['returncode']==0
        partial, _ = failed('partial-nonzero','fail',RuntimeError)
        assert partial['direct_output_artifacts'][0]['bytes']==len(b'partial-direct') and partial['returncode']==7
        timed, _ = failed('timeout-owned-child','wait',TimeoutError,timeout=.25)
        canceled_path = folder/'cancellation-owned-child'/'direct.bin'
        def cancellation_guard():
            if canceled_path.exists(): raise InterruptedError('Injected owner cancellation')
        canceled, _ = failed('cancellation-owned-child','wait',InterruptedError,guard=cancellation_guard)
        for stopped in (timed,canceled):
            pid = stopped['process']['pid']
            if psutil.pid_exists(pid):
                assert abs(psutil.Process(pid).create_time()-stopped['process']['creation_time'])>.01
        passed.append('owned-only-terminal-timeout-and-cancellation')

        def refused_verify(name, value=result, changes=None):
            expected=dict(kwargs)
            if changes: expected.update(changes)
            try: native.verify_native(value, **expected)
            except (ValueError,KeyError,TypeError): refused.append(name)
            else: raise AssertionError('Changed verification accepted: '+name)
        refused_verify('changed-expected-byte-budget',changes={'max_output_bytes':kwargs['max_output_bytes']+1})
        refused_verify('changed-expected-timeout',changes={'timeout':kwargs['timeout']+1})
        refused_verify('omitted-expected-direct-output',changes={'direct_outputs':[]})
        changed_path=str(root/'another-direct.bin')
        refused_verify('changed-expected-direct-path',changes={'direct_outputs':[dict(path=changed_path,argument_index=4)]})
        for name, mutate in (
                ('changed-result-stdout-reference',lambda v:v.__setitem__('stdout_path',str(root/'another-stdout.bin'))),
                ('changed-result-schema',lambda v:v.__setitem__('extra',1)),
                ('changed-receipt-direct-hash',lambda v:v['receipt']['direct_output_artifacts'][0].__setitem__('sha256','0'*64)),
                ('v1-format-in-v2-result',lambda v:v.__setitem__('format',1))):
            altered=copy.deepcopy(result); mutate(altered); refused_verify(name,altered)
        tamper, tamper_kwargs, tamper_root = valid('direct-content-tamper')
        path=Path(tamper['receipt']['direct_output_artifacts'][0]['path'])
        original_raw=path.read_bytes()
        with (tamper_root/'direct-before-deliberate-tamper.bin').open('xb') as stream: stream.write(original_raw)
        # This newly generated software fixture is deliberately changed only to
        # test refusal; genuine/v1 evidence is never a mutation target.
        with path.open('ab') as stream: stream.write(b'deliberate software fixture tamper')
        try: native.verify_native(tamper,**tamper_kwargs)
        except ValueError: refused.append('changed-direct-file-content')
        else: raise AssertionError('Changed direct content accepted')

        input_path=folder/'source-binding-fixture.bin'
        with input_path.open('xb') as stream: stream.write(b'original registered source')
        changed_source,_=failed('source-change-after-launch','modify-source',ValueError,auxiliary=input_path)
        assert changed_source['direct_output_artifacts'][0]['exists']
        source_root=folder/'changed-source-before-launch'; source_root.mkdir()
        source_out=source_root/'direct.bin'; source_args=['-B',str(child),'valid',str(source_out)]
        source_ids=dict(common_ids);source_ids[str(input_path)]='0'*64
        try: native.run_native(exe,source_args,folder=source_root,label='call',expected_identities=source_ids,
            guard=lambda:None,direct_outputs=[dict(path=str(source_out),argument_index=4)])
        except ValueError: refused.append('source-change-before-launch')
        else: raise AssertionError('Changed input source accepted')
        assert not (source_root/'call-receipt.json').exists() and not source_out.exists()

        malformed = ['not-list', {}, {'path':'relative.bin','argument_index':4},
            {'path':'PLACEHOLDER','argument_index':True},{'path':'PLACEHOLDER','argument_index':0},
            {'path':'PLACEHOLDER','argument_index':999},{'path':'PLACEHOLDER','argument_index':4,'extra':1},
            {'path':'OUTSIDE','argument_index':4},{'path':'STDOUT','argument_index':4},
            {'path':'INPUT','argument_index':4},{'path':'EXISTING','argument_index':4},
            {'path':'OTHER','argument_index':4},'duplicate']
        for index,bad in enumerate(malformed):
            case=folder/f'malformed-{index:02d}'; case.mkdir(); marker=case/'direct.bin'
            args=['-B',str(child),'valid',str(marker)]; ids=dict(common_ids)
            if isinstance(bad,dict):
                spec=copy.deepcopy(bad); token=spec.get('path')
                lookup={'PLACEHOLDER':str(marker),'OUTSIDE':str(folder/'outside-owned-case.bin'),
                    'STDOUT':str(case/'call-stdout.bin'),'INPUT':str(child),
                    'EXISTING':str(case/'existing.bin'),'OTHER':str(case/'other.bin')}
                if token in lookup:spec['path']=lookup[token]
                if token in ('OUTSIDE','STDOUT','INPUT','EXISTING'):args[3]=spec['path']
                if token=='EXISTING':
                    with Path(spec['path']).open('xb') as stream:stream.write(b'existing fixture')
                specs=[spec]
            elif bad=='duplicate':specs=[dict(path=str(marker),argument_index=4)]*2
            else:specs=bad
            try:native.run_native(exe,args,folder=case,label='call',expected_identities=ids,
                guard=lambda:None,direct_outputs=specs)
            except (ValueError,KeyError,TypeError):refused.append(f'malformed-spec-{index:02d}')
            else:raise AssertionError('Malformed output spec accepted')
            assert not (case/'call-receipt.json').exists() and not marker.exists()

        for path,identity in original.items():assert native.sha(path)==identity
        for path,value in snapshots.items():assert native.sha(path)==value['sha256']
        terminal=dict(format=2,passed=True,purpose='Actual small Python-child software controls only',
            native_poker_runs=0,scientific_runs=0,gpu_used=False,cuda_visible_devices='-1',
            passed_controls=passed,refused_controls=refused,refusal_count=len(refused),
            software_child_invocations=len(receipts),receipt_artifacts=receipts,
            independent_os_attestation=independent,source_snapshots=snapshots,
            original_v1_sources_unchanged=original,seconds=time.monotonic()-started,
            acceptance_bound_only=True,transient_write_cap_certified=False)
        save(folder/'result.json',terminal)
        print(json.dumps(terminal,sort_keys=True))
    except BaseException as exc:
        save(folder/'failure.json',dict(format=2,passed=False,error=dict(type=type(exc).__name__,message=str(exc)),
            passed_controls=passed,refused_controls=refused,receipt_artifacts=receipts,
            source_snapshots=snapshots,seconds=time.monotonic()-started))
        raise


if __name__=='__main__': main(sys.argv[1])
