"""V2 resource/provenance wiring controls with tiny Python children only."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from unittest.mock import patch

sys.dont_write_bytecode = True
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
STAGE = Path(__file__).resolve().parent
RESEARCH = Path(r'T:\Dev\GTOpen\tools\research')
sys.path[:0] = [str(STAGE), str(RESEARCH)]
import numpy as np
import psutil
import preflop_expected_native_execution_v2 as native
import preflop_expected_river_workers_v2 as worker
import preflop_expected_river_transport_v2 as transport
import preflop_expected_river_workers_source_check_v1 as original_controls
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir

PINS = {
    RESEARCH/'preflop_expected_river_workers_v1.py':'878f1ebb9a25f601e0604affd5af238a6dcbdc5b62a37a6442e0e3392e6c0b65',
    RESEARCH/'preflop_expected_river_transport_v1.py':'3df3746485562089a922bfb1e945c0666650308da040e2a522cb42cca6de2b93',
    STAGE/'preflop_expected_native_execution_v2.py':'1627430507472de471552ffca420b416a5ab0d6670b9ea8e5fb0e11b0da6699f',
    STAGE/'preflop_expected_river_workers_v2.py':'d34f4134c65adc8603882c4a6c2023b653dbdf27fd6f09794a2504c90f3d1fce',
    STAGE/'preflop_expected_river_transport_v2.py':'2b1c8fbc5484af9288375ee7665e0e87d9ec0486a7c93c74d670063d21610ddc',
}
DIRECT_CHILD = '''import json,os,sys
from pathlib import Path
import psutil
assert sys.argv[-1]=='--output-byte-limit=64000000'
mode=sys.argv[1];path=Path(sys.argv[-2]);path.write_bytes((mode+' direct software output\\n').encode())
p=psutil.Process();parent=p.parent()
print(json.dumps(dict(mode=mode,argv=p.cmdline(),pid=p.pid,parent_pid=parent.pid,
    creation_time=p.create_time(),parent_creation_time=parent.create_time(),cuda=os.environ.get('CUDA_VISIBLE_DEVICES'))))
'''
RIVER_CHILD = '''import json,sys
from pathlib import Path
assert sys.argv[1:]==['--output-byte-limit=64000000']
source=Path(__file__).read_text();raw=sys.stdin.read();request=json.loads(raw)
print(json.dumps(dict(format=3,mode=request['mode'],context_source=source,request_source=raw,
    queries=dict(context_source=source,batch_source=raw),targets=[])))
sys.stderr.write('tiny software export\\n')
'''


def write_new(path, raw):
    with path.open('xb') as stream: stream.write(raw)


def save_new(path, value):
    write_new(path,(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode())


def node(tree, name):
    return next(v for v in tree.body if isinstance(v,(ast.FunctionDef,ast.ClassDef)) and v.name==name)


def dumped(value): return ast.dump(value,include_attributes=False)


def source_parity():
    old = ast.parse((RESEARCH/'preflop_expected_river_workers_v1.py').read_text())
    new = ast.parse(Path(worker.__file__).read_text())
    identical = []
    for name in ('runtime','identities','CollectedVisits','guard','serialized_events','_checked_event','pool'):
        assert dumped(node(old,name))==dumped(node(new,name)),name+' changed'
        identical.append(name)
    initialize = copy.deepcopy(node(new,'initialize'))
    for value in ast.walk(initialize):
        if isinstance(value,ast.alias):
            value.name=value.name.replace('preflop_expected_native_execution_v2','preflop_expected_native_execution_v1')
    assert dumped(node(old,'initialize'))==dumped(initialize)
    identical.append('initialize-except-versioned-execution-import')
    complete = copy.deepcopy(node(new,'complete'))
    for value in ast.walk(complete):
        if isinstance(value,ast.Call) and isinstance(value.func,ast.Name):
            if value.func.id=='_invoke':
                value.keywords=[k for k in value.keywords if k.arg!='direct_outputs']
            if value.func.id=='dict':
                for k in value.keywords:
                    if k.arg=='format' and isinstance(k.value,ast.Constant) and k.value.value==2:
                        k.value.value=1
    assert dumped(node(old,'complete'))==dumped(complete)
    identical.append('complete-except-direct-declarations-and-worker-envelope-version')
    def section(function, first, final):
        a=next(i for i,v in enumerate(function.body) if isinstance(v,ast.Assign)
            and isinstance(v.targets[0],ast.Name) and v.targets[0].id==first)
        b=next(i for i,v in enumerate(function.body) if isinstance(v,ast.Assign)
            and isinstance(v.targets[0],ast.Name) and v.targets[0].id==final)
        return [dumped(v) for v in function.body[a:b]]
    assert section(node(old,'commit'),'positives','invocations')==section(node(new,'commit'),'positives','invocations')
    assert [dumped(v) for v in node(old,'commit').body[-2:]]==[dumped(v) for v in node(new,'commit').body[-2:]]
    identical.extend(['complete-positive-visit-weight-and-target-validation','ordered-reservoir-insertion-and-RNG'])
    old_transport = ast.parse((RESEARCH/'preflop_expected_river_transport_v1.py').read_text())
    new_transport = ast.parse(Path(transport.__file__).read_text())
    def math(tree):
        function=copy.deepcopy(node(tree,'generate'))
        function.body=[v for v in function.body if not isinstance(v,ast.FunctionDef)]
        return dumped(function)
    assert math(old_transport)==math(new_transport)
    assert dumped(node(old_transport,'file_sha'))==dumped(node(new_transport,'file_sha'))
    identical.append('entire-transport-generate-except-authenticated-export-helper')
    return identical


def source_ids():
    return {str(Path(p).resolve()):worker.sha(p) for p in (worker.__file__,transport.__file__,native.__file__)}


def tiny_direct_children(folder):
    root=folder/'actual-direct-wiring';root.mkdir()
    child=root/'tiny_direct_child.py';write_new(child,DIRECT_CHILD.encode())
    context=root/'context.fixture';write_new(context,b'tiny software context')
    exe=str(Path(sys.executable).resolve())
    pinned={exe:worker.sha(exe),str(context):worker.sha(context)}
    state=dict(native_identities=pinned,worker_source_identities=source_ids(),
        runtime_limits=dict(native_timeout_seconds=3))
    invocations=[];timings={};receipts=[]
    with patch.object(worker,'_STATE',state),patch.object(worker,'guard',lambda:None):
        for mode,index,extra in (('bridge',5,['unused-fixture-argument']),('trace',4,[])):
            part=root/mode;part.mkdir();output=part/'direct.bin'
            arguments=['-B',str(child),mode,*extra,str(output)]
            specs=[dict(path=str(output),argument_index=index)]
            worker._invoke(exe,arguments,'native-'+mode,part,[child,context],invocations,timings,direct_outputs=specs)
            invocation=invocations[-1];result=invocation['result']
            expected=[exe,*arguments,transport.OUTPUT_LIMIT_ARGUMENT]
            assert result['receipt']['argv']==expected
            assert result['receipt']['direct_outputs']==specs
            native.verify_native(result,executable=exe,arguments=expected[1:],
                expected_identities=invocation['expected_identities'],timeout=3,
                max_output_bytes=worker.MAX_NATIVE_OUTPUT_BYTES,direct_outputs=specs)
            independently=json.loads(Path(result['stdout_path']).read_bytes())
            assert independently['argv']==expected
            assert independently['pid']==result['receipt']['process']['pid']
            assert independently['parent_pid']==result['receipt']['caller']['pid']==os.getpid()
            assert abs(independently['creation_time']-result['receipt']['process']['creation_time'])<.002
            assert abs(independently['parent_creation_time']-result['receipt']['caller']['creation_time'])<.002
            assert independently['cuda']=='-1'
            assert output.read_bytes()==(mode+' direct software output\n').encode()
            receipts.append(dict(path=result['receipt_path'],sha256=result['receipt_sha256']))
    return receipts


def tiny_transport_children(folder):
    root=folder/'actual-transport-wiring';root.mkdir()
    child=root/'tiny_river_context.py';write_new(child,RIVER_CHILD.encode())
    source=child.read_text();exe=str(Path(sys.executable).resolve());invocations=[]
    generated=root/'conditional';generated.mkdir()
    ids=source_ids();ids.update({exe:worker.sha(exe),str(child):worker.sha(child)})
    tree=ast.parse(Path(transport.__file__).read_text())
    export=copy.deepcopy(next(v for v in node(tree,'generate').body if isinstance(v,ast.FunctionDef) and v.name=='export'))
    module=ast.Module(body=[export],type_ignores=[]);ast.fix_missing_locations(module)
    namespace=dict(transport.__dict__)
    namespace.update(folder=generated,source=source,executable=exe,context_path=child,
        expected_identities=ids,native_hash=worker.sha(exe),native_timeout_seconds=3,
        native_invocations=invocations,guard=lambda:None,write=worker.save)
    exec(compile(module,str(Path(transport.__file__).resolve()),'exec'),namespace)
    for mode in ('history','selected'):
        request=dict(format=1,mode=mode,targets=[])
        doc=namespace['export']('chunk-000-'+mode,request)
        assert doc['mode']==mode and doc['context_source']==source
        invocation=invocations[-1]
        assert invocation['arguments']==[str(child),transport.OUTPUT_LIMIT_ARGUMENT]
        assert invocation['result']['receipt']['direct_outputs']==[]
        assert invocation['result']['receipt']['max_output_bytes']==64_000_000
        assert invocation['result']['receipt']['timeout_seconds']==3
        rp=Path(invocation['stdin_path'])
        assert invocation['expected_identities'][str(rp)]==worker.sha(rp)
        native.verify_native(invocation['result'],executable=exe,arguments=invocation['arguments'],
            expected_identities=invocation['expected_identities'],stdin_path=rp,
            timeout=3,max_output_bytes=64_000_000,direct_outputs=[])
        assert worker.sha(generated/(invocation['label']+'-native.json'))==invocation['result']['stdout_sha256']
    return [dict(path=v['result']['receipt_path'],sha256=v['result']['receipt_sha256']) for v in invocations]


def synthetic_commit(folder):
    root=folder/'synthetic-commit';root.mkdir()
    with patch.object(original_controls,'worker',worker):
        result,args,source=original_controls.fixture(root)
    result.update(format=2,qualified_ingest_identity={},timings={},seconds=0.,pid=os.getpid(),rss_bytes=0)
    sources=source_ids();result['worker_source_identities']=sources
    for invocation in result['native_invocations']:
        invocation['arguments'].append(transport.OUTPUT_LIMIT_ARGUMENT)
        invocation['expected_identities'].update(sources)
    ep=root/'ordered-events.json';event_doc=json.loads(ep.read_bytes());event_doc['format']=2
    # Only this freshly created synthetic fixture is adapted to the v2 schema.
    ep.write_bytes((json.dumps(event_doc,sort_keys=True,separators=(',',':'))+'\n').encode())
    result['event_document_sha256']=worker.digest(event_doc)
    result['artifacts']={str(p.relative_to(root)):worker.sha(p) for p in root.rglob('*') if p.is_file()}
    assert set(result)==worker.RESULT_FIELDS and set(event_doc)==worker.EVENT_FIELDS
    reservoirs=[WeightedPhysicalReservoir(4,p,p,source) for p in (0,1)]
    snapshot=original_controls.reservoir_snapshot(reservoirs)
    refused=[];verifications=[]
    def verifier(value,**expected):
        verifications.append(expected)
        assert expected['timeout']==120 and expected['max_output_bytes']==64_000_000
        assert expected['arguments'][-1]==transport.OUTPUT_LIMIT_ARGUMENT
        index=5 if expected['arguments'][0]=='verify' else 4
        assert expected['direct_outputs']==[dict(path=expected['arguments'][index-1],argument_index=index)]
        assert expected['stdin_path'] is None
        return {}
    mutations=[
        ('nonfinite-event',lambda r:r['events'][1][1][3].__setitem__(0,float('nan'))),
        ('sampled-preflop-event',lambda r:r['events'].append((0,original_controls.row(0,0,1),1,2.))),
        ('event-order',lambda r:r['event_records'].reverse()),
        ('observation-count',lambda r:r['observed_counts'].__setitem__(0,3)),
        ('missing-invocation',lambda r:r['native_invocations'].pop()),
        ('changed-native-mode',lambda r:r['native_invocations'][0]['arguments'].__setitem__(0,'wrong-mode')),
        ('old-worker-format',lambda r:r.__setitem__('format',1)),
        ('old-worker-type',lambda r:r.__setitem__('worker_type','typed-expected-policy-physical-posterior64-cpu-worker-v1')),
        ('extra-result-field',lambda r:r.__setitem__('extra',1)),
        ('missing-result-field',lambda r:r.pop('timings')),
        ('missing-resource-flag',lambda r:r['native_invocations'][1]['arguments'].pop()),
        ('changed-resource-flag',lambda r:r['native_invocations'][1]['arguments'].__setitem__(-1,'--output-byte-limit=64000001')),
        ('extra-invocation-field',lambda r:r['native_invocations'][0].__setitem__('extra',1)),
        ('old-worker-source-pin',lambda r:r.__setitem__('worker_source_identities',
            {str(RESEARCH/'preflop_expected_river_workers_v1.py'):PINS[RESEARCH/'preflop_expected_river_workers_v1.py']})),
        ('extra-native-role',lambda r:r['native_roles'].__setitem__('extra',r['native_roles']['executable'])),
    ]
    with patch.object(worker,'verify_native',verifier):
        for name,mutate in mutations:
            bad=copy.deepcopy(result);mutate(bad)
            original_controls.expect_rejected(lambda:worker.commit(bad,reservoirs,**args))
            original_controls.unchanged(reservoirs,snapshot);refused.append(name)
        assert worker.commit(result,reservoirs,**args)==[1,1]
        assert [r.seen for r in reservoirs]==[1,1]
        assert all(int(r.keys[0,0])>=1<<63 for r in reservoirs)
    assert len(verifications)==2
    return dict(refused=refused,count=len(refused),all_refusals_preserve_reservoir_and_rng=True,
        valid_ordered_postflop_commit=True,native_verification_replaced_only_in_synthetic_commit=True,
        exact_native_verify_configuration=verifications)


def main(folder):
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False)
    began=time.monotonic();receipts=[]
    for path,pin in PINS.items(): assert worker.sha(path)==pin,str(path)
    source_dir=folder/'sources';source_dir.mkdir();snapshots=[]
    for path in [*PINS,Path(__file__).resolve()]:
        raw=path.read_bytes();destination=source_dir/(path.name+'.snapshot')
        write_new(destination,raw)
        snapshots.append(dict(path=str(path),snapshot=str(destination),sha256=hashlib.sha256(raw).hexdigest()))
    save_new(folder/'attempt.json',dict(format=1,purpose='Software-only prospective v2 resource/provenance controls',
        sources=snapshots,pid=os.getpid(),creation_time=psutil.Process().create_time(),
        argv=sys.argv,cuda_visible_devices=os.environ['CUDA_VISIBLE_DEVICES'],started_unix=time.time()))
    try:
        parity=source_parity()
        assert worker.MAX_NATIVE_OUTPUT_BYTES==transport.MAX_NATIVE_OUTPUT_BYTES==64_000_000
        assert worker.FAILURE_RESERVE==transport.FAILURE_RESERVE==256
        before=dict(os.environ)
        try: worker.initialize(*([None]*11))
        except RuntimeError as exc: assert 'spawned child' in str(exc)
        else: raise AssertionError('Main process environment mutation accepted')
        assert dict(os.environ)==before
        receipts.extend(tiny_direct_children(folder));receipts.extend(tiny_transport_children(folder))
        commit=synthetic_commit(folder)
        for path,pin in PINS.items(): assert worker.sha(path)==pin
        terminal=dict(format=1,passed=True,source_parity=parity,sources=snapshots,
            original_v1_sources_unchanged=True,main_process_environment_preserved=True,
            tiny_python_child_invocations=len(receipts),receipt_artifacts=receipts,
            actual_native_poker_runs=0,scientific_runs=0,gpu_used=False,cuda_visible_devices='-1',
            aggregate_cap=64_000_000,failure_reserve=256,synthetic_commit=commit,
            calculation_and_underlying_scientific_schema_unchanged=True,seconds=time.monotonic()-began)
        save_new(folder/'result.json',terminal);print(json.dumps(terminal,sort_keys=True))
    except BaseException as exc:
        save_new(folder/'failure.json',dict(format=1,passed=False,error=dict(type=type(exc).__name__,message=str(exc)),
            receipt_artifacts=receipts,sources=snapshots,seconds=time.monotonic()-began))
        raise


if __name__=='__main__': main(sys.argv[1])
