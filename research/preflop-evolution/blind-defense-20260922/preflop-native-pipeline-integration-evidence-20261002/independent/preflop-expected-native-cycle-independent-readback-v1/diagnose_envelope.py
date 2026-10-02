"""Read-only diagnosis of the preserved audit refusal; no board/native rerun."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import json
from pathlib import Path
import sys
from threadpoolctl import threadpool_limits, threadpool_info

OUT=Path(__file__).resolve().parent
STAGE=OUT.parent;sys.path.insert(0,str(STAGE));sys.path.append(r'T:\Dev\GTOpen\tools\research')
import preflop_expected_training_checkpoint_v1 as cp
import sampled_visible_hybrid_checkpoint_v1 as storage
from preflop_expected_native_targets_v2 import FrozenExpectedTargets
from stack_context_inputs_v1 import Registry
from board_root_accumulator_v1 import digest

PROFILE=Path(r'S:\GTOpen-research\preflop-expected-native-cycle-profile-v1')

def read(path):return json.loads(Path(path).read_bytes())

def diffs(a,b,path='$'):
    if isinstance(a,dict) and isinstance(b,dict):
        result=[]
        for key in sorted(set(a)|set(b)):
            if key not in a or key not in b:result.append(dict(path=path+'.'+str(key),missing=True))
            else:result.extend(diffs(a[key],b[key],path+'.'+str(key)))
        return result
    if isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b):return [dict(path=path,lengths=[len(a),len(b)])]
        return [item for i,(x,y) in enumerate(zip(a,b)) for item in diffs(x,y,path+f'[{i}]')]
    if a!=b:return [dict(path=path,stored=a,expected=b,types=[type(a).__name__,type(b).__name__])]
    return []

spec=read(PROFILE/'registration.json');reg=Registry(spec['entries']);resources=spec['resources'];config=spec['config']
initial=cp.restore_checkpoint(PROFILE/'objects',read(PROFILE/'initial-complete-checkpoint.json')['checkpoint'],config,reg,resources)
metrics=read(PROFILE/'cycle-0001/metrics.json');collection=metrics['collections'][0]
target=read(collection['board_evidence']['path']);key=reg.fit_contexts[0]
source=storage.read_object(PROFILE/'objects',initial['next_model']).decode()
draws=[wrapped['result']['record'] for wrapped in collection['board_results']]
cases=[]
for threads in (1,4):
    with threadpool_limits(limits=threads):
        provider=FrozenExpectedTargets(state=initial['contexts'][key]['preflop_state'],model_source=source,registry=reg,resources=resources)
        expected=dict(plan=initial['contexts'][key]['preflop_state'].plan(),
            evidence=provider.generation_evidence(initial['contexts'][key]['preflop_state'],target['plan'],draws),recipe=provider.recipe)
        differences=diffs(target,expected)
        cases.append(dict(threads=threads,differences=differences,wire_digest_equal=digest(target)==digest(expected),
            threadpools=threadpool_info()))
result=dict(scope='Read-only exact envelope diagnosis using retained draws; no raw-tree replay or native/profile invocation.',cases=cases)
with (OUT/'envelope-diagnosis.json').open('x',encoding='utf-8') as stream:json.dump(result,stream,sort_keys=True,indent=2)
print(json.dumps(dict(cases=[dict(threads=c['threads'],differences=c['differences'],wire_digest_equal=c['wire_digest_equal']) for c in cases])))
