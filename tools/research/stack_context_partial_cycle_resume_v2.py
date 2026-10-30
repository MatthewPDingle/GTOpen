"""Recover the interrupted cycle using retained results and unchanged math.

Original pipeline functions are compiled with only directory creation made
idempotent. Explicit transports authenticate retained outputs; original
collect/fit ordering, random states, targets and scientific budgets stay fixed.
"""
import ast
from concurrent.futures import Future,ProcessPoolExecutor
import json
import multiprocessing as mp
from pathlib import Path
from types import SimpleNamespace
import subprocess
import stack_context_training_pipeline_v1 as pipeline
import stack_context_river_workers_v1 as workers
from stack_context_retained_state_replay_v1 import replay_events,replay_complete_context,checked_json,require
from stack_context_river_transport_resume_v1 import generate as retained_generate,retained_write
from stack_context_cycle_archive_v1 import sha

_RECOVERY=None


def function(name, *, module, namespace, resumable_directories=False):
    tree=ast.parse(Path(module.__file__).read_text(encoding='utf-8'))
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    changed=0
    if resumable_directories:
        for call in ast.walk(node):
            if isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute) and call.func.attr=='mkdir':
                found=False
                for kw in call.keywords:
                    if kw.arg=='exist_ok':kw.value=ast.Constant(True);found=True
                if not found:call.keywords.append(ast.keyword(arg='exist_ok',value=ast.Constant(True)))
                changed+=1
        require(changed==({'collect':3,'update':1}[name]),'Unexpected pipeline directory boundary')
    code=ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[]))
    scope=dict(module.__dict__);scope.update(namespace)
    exec(compile(code,module.__file__+'::retained-recovery','exec'),scope)
    return scope[name]


def writer(expected,allow_missing,*,check_collection=False):
    def write(path,value):
        path=Path(path)
        if check_collection and path.name=='collection.json' and path.exists():
            old=checked_json(path,expected)
            require({k:v for k,v in old.items() if k!='seconds'}==
                    {k:v for k,v in value.items() if k!='seconds'},'Recovered collection differs')
            return
        return retained_write(path,value,expected=expected,allow_missing=allow_missing)
    return write


class NativeTransport:
    CREATE_NO_WINDOW=subprocess.CREATE_NO_WINDOW
    def __init__(self,expected,allow_missing):self.expected=expected;self.allow_missing=allow_missing
    def run(self,command,**kwargs):
        dest=Path(command[-1]);source=Path(command[-3] if command[1]=='queries' else command[1])
        # Existing native outputs are authenticated by the interruption audit.
        # Their semantic input binding is also checked by the original ingesters.
        if dest.exists():
            require(self.expected.get(str(dest))==sha(dest),'Changed retained native output')
            require(Path(command[0]).name in ('hu_sampled_allin_history_bridge_v1.exe','hu_sampled_action_trace_v2.exe'),
                    'Unrecognized retained native command')
            return SimpleNamespace(returncode=0,stdout='' if kwargs.get('text') else b'',
                stderr='' if kwargs.get('text') else b'')
        require(self.allow_missing and str(dest) not in self.expected,'Missing retained native output')
        return subprocess.run(command,**kwargs)


def initialize(expected,allow_missing,args):
    global _RECOVERY
    workers.initialize(*args)
    _RECOVERY=dict(expected=expected,allow_missing=allow_missing)


def completed_batch(part,start,expected_inputs):
    s=workers._STATE;expected=_RECOVERY['expected'];allow_missing=_RECOVERY['allow_missing'];part=Path(part)
    existing=part/'worker-result.json'
    if existing.exists():
        record=checked_json(existing,expected)
        require(record['input_identities']==expected_inputs and record['native_identities']==s['identities'],
                'Retained worker inputs changed')
        for name,h in record['artifacts'].items():
            path=part/name
            require(path.resolve().is_relative_to(part.resolve()) and expected.get(str(path))==h and sha(path)==h,
                    'Retained worker artifact changed')
        events,counts=replay_events(part,expected=expected,generation=s['generation'],start=start,
            iteration=s['iteration'],cache=s['cache'],targets=s['targets'],policy_id=s['river_policy_id'],guard=workers.guard)
        require(counts==record['counts'],'Retained worker counts changed')
        return dict(record,events=events)
    require(allow_missing,'Missing retained worker record during read-only qualification')
    require(not any((part/name).exists() for name in ('integrated-profiles.json','integrated-native.json','integrated-targets.json')),
            'Partial root integration requires separate review')
    def generate(*args,**kwargs):
        return retained_generate(*args,**kwargs,expected=expected,allow_missing=allow_missing)
    resume=function('complete',module=workers,namespace=dict(_STATE=s,
        save=writer(expected,allow_missing),generate=generate,subprocess=NativeTransport(expected,allow_missing)))
    return resume(part,start,expected_inputs)


def pool(count,*,expected,allow_missing,**args):
    require(type(count) is int and 1<=count<=4,'Bounded recovery workers required')
    names=('context_path','cache','targets','generation','iteration','executable','trace_executable',
        'integration_executable','river_payload','river_executable','expected_native_identities')
    return ProcessPoolExecutor(max_workers=count,mp_context=mp.get_context('spawn'),
        initializer=initialize,initargs=(expected,allow_missing,tuple(args[k] for k in names)))


class RetainedBoardPool:
    def __init__(self,*,folder,expected,**kwargs):self.folder=Path(folder);self.expected=expected;self.kwargs=kwargs
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def submit(self,ignored,index,board):
        path=self.folder/f'board-{index:03d}'/'result.json';value=checked_json(path,self.expected)
        require(value['record']['board']==board and value['native_identities']==self.kwargs['expected_native_identities']
                and self.expected.get(value['tree_artifact'])==value['tree_sha256'],'Retained board identity differs')
        future=Future();future.set_result(dict(result=value,path=str(path),sha256=sha(path)));return future


def collect_partial(*args,expected,allow_missing,qualification=False,**kwargs):
    require(Path(args[0]).is_dir(),'Existing interrupted context required')
    replacement=dict(complete=completed_batch,save=writer(expected,allow_missing,check_collection=qualification),
        subprocess=NativeTransport(expected,allow_missing),
        pool=lambda count,**kw:pool(count,expected=expected,allow_missing=allow_missing,**kw),
        board_pool=lambda count,**kw:RetainedBoardPool(expected=expected,**kw))
    return function('collect',module=pipeline,namespace=replacement,resumable_directories=True)(*args,**kwargs)


def update(folder,objects,state,config,registry,resources,*,expected,**kwargs):
    """Only a reviewed partial cycle enters here; complete cycles never refit."""
    folder=Path(folder)
    require(folder.is_dir() and not (folder/'metrics.json').exists(),'Reviewed incomplete cycle required')
    # The original update function checks every registered source identity and
    # creates fits only after all contexts have been collected in original order.
    def collect(*args,**options):
        context=Path(args[0]);key=options['key']
        if (context/'collection.json').exists():
            replay_options={k:v for k,v in options.items() if k not in ('native','workers','board_workers','on_stage')}
            replay_complete_context(*args,expected=expected,**replay_options)
            options['on_stage']('retained-context-reconstructed',key)
            return checked_json(context/'collection.json',expected)
        if context.exists():return collect_partial(*args,expected=expected,allow_missing=True,**options)
        return pipeline.collect(*args,**options)
    return function('update',module=pipeline,namespace=dict(collect=collect),resumable_directories=True)(
        folder,objects,state,config,registry,resources,**kwargs)
