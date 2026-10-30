"""Prepare E018 scripts from preserved E017 controls without executing any build/GPU work."""
import json, sys
from pathlib import Path
repo=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
sys.path.insert(0,str(repo/'tools'))
import postflop_autoresearch as ar
base=ar.RESEARCH/'runs'
build=(base/'E017-build.py').read_text(encoding='utf-8').replace('E017','E018')
build=build.replace("('mod.rs','plan.rs','continuation_capacity.rs')]", "('mod.rs','plan.rs','kernels.cu','continuation_capacity.rs')]+['crates/solver/src/game.rs']")
build=build.replace("len(sys.argv)==4,'Provide reviewed mod.rs, plan.rs and continuation_capacity.rs hashes'", "len(sys.argv)==6,'Provide reviewed mod.rs, plan.rs, kernels.cu, continuation_capacity.rs and game.rs hashes'")
build=build.replace('Actor0-only down-action list candidate from accepted E015', 'Precomputed child-value address table candidate from accepted E015')
build=build.replace('From E015: filter inactive actor1 down-action CTAs in second paired sweep, with allocation and capacity accounting; CUDA math/evaluator unchanged', 'From E015: precompute validated child-value addresses for training up-action with exact table payload accounting and UI estimate; floating arithmetic and evaluator unchanged')
feature=(base/'E017-feature-prebuild.py').read_text(encoding='utf-8').replace('E017','E018')
feature=feature.replace('result=subprocess.run(command,cwd=repo,env=env,stdout=stdout,stderr=stderr)', '''proc=subprocess.Popen(command,cwd=repo,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
        while True:
            try:
                code=proc.wait(timeout=10)
                break
            except subprocess.TimeoutExpired:
                with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
                    status=json.loads(ar.STATUS.read_text(encoding='utf-8'))
                    status.update(updated_at=ar.now(),stage='Building E018 continuation controls',active_experiment='E018')
                    ar.atomic_json(ar.STATUS,status)''').replace('result.returncode==0','code==0')
primary=(base/'E017-primary.py').read_text(encoding='utf-8').replace('E017','E018').replace('V017','V018')
primary=primary.replace('B053','B056').replace('B054','B057').replace('B055','B058')
primary=primary.replace("('E018',True)","('E018R1',True)")
primary=primary.replace('mixed/uniform continuation capacity accuracy','child-value table continuation capacity accuracy')
primary=primary.replace('optional_down_list_matches_observed_metadata_for_mixed_and_uniform_plans','child_mapping_matches_observed_metadata_for_turn_and_river')
primary=primary.replace('filtered downward action work','precomputed child-value addresses')
for name,source in [('E018-build.py',build),('E018-feature-prebuild.py',feature),('E018-primary.py',primary)]:
    compile(source,name,'exec')
    with (base/name).open('x',encoding='utf-8',newline='\n') as f:f.write(source)
    print(name,ar.sha256(base/name))
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
    status=json.loads(ar.STATUS.read_text(encoding='utf-8'))
    status.update(updated_at=ar.now(),stage='E018 source freeze and memory estimate review',activity='First source review passed. Adding the exact new table payload to the user-visible VRAM estimate before freezing the five-file candidate; no E018 runtime result yet.',active_experiment='E018')
    ar.atomic_json(ar.STATUS,status)
identities=['V018-unit','V018-capacity','B056','E018R1','E018R2','B057','B058','E018R3']
assert not any((base/x).exists() for x in identities)
assert not any(x['id'] in identities for x in status['experiments'])
protocol={'at':ar.now(),'candidate':'E018','reference':'accepted E015','order':identities,
 'pairs':[{'baseline':'B056','candidate':'E018R1'},{'baseline':'B057','candidate':'E018R2'},{'baseline':'B058','candidate':'E018R3'}],
 'aggregate_gate':'At least 2 percent reduction in sum of per-fixture complete-cycle medians',
 'fixture_guard':'Reject when a fixture median is more than 3 percent slower and a strict majority (minimum two) paired repetitions are more than 3 percent slower',
 'exactness':'All non-timing complete-state/configuration fields, exploitability bits and stopping iterations match',
 'broader_qualification_if_pass':'Immutable original F32, saved-state, menu including generic >8 arities, resume, GPU and continuation controls; fresh original-baseline cumulative cohort',
 'exclusions':[],'builds_before_timing':True,'first_physical_run':'E018R1','logical_dashboard_row':'E018',
 'scripts':{n:ar.sha256(base/n) for n in ('E018-build.py','E018-feature-prebuild.py','E018-primary.py')}}
out=base/'E018-primary-plan';out.mkdir(exist_ok=False)
ar.atomic_json(out/'protocol.json',protocol)
print('E018 primary order sealed; no build or timing executed.')
