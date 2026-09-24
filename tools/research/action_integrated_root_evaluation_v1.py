"""Reuse complete saved current-policy rows for deterministic action averaging."""
import json
from pathlib import Path
import subprocess
from sampled_physical_root_evaluation_v1 import save
from action_integrated_root_targets_v1 import derive


def evaluate(context_path,batch_path,queries,policies,sampled_audit,folder,executable,guard):
    guard();folder=Path(folder)
    rows=policies['policies']
    profiles=[dict(name='baseline',policies=rows)]
    roots=[i for i,o in enumerate(queries['observations']) if o['phase']==0 and o['hi']=='1']
    if not roots:raise ValueError('Complete current-policy BB root rows required')
    for action in range(4):
        changed=list(rows)
        for i in roots:changed[i]=dict(rows[i],probabilities=[float(k==action) for k in range(4)])
        profiles.append(dict(name=f'action-{action}',policies=changed))
    transport=dict(format=1,context_source=policies['context_source'],batch_source=policies['batch_source'],profiles=profiles)
    if policies['context_source']!=Path(context_path).read_text() or policies['batch_source']!=Path(batch_path).read_text():
        raise ValueError('Original context and physical batch bytes required')
    profile_path=folder/'integrated-profiles.json';native_path=folder/'integrated-native.json'
    if profile_path.exists() or native_path.exists():raise ValueError('Do not overwrite integration evidence')
    save(profile_path,transport)
    guard()
    result=subprocess.run([str(executable),str(context_path),str(batch_path),str(profile_path),str(native_path)],
        capture_output=True,text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise RuntimeError(result.stderr[-2000:])
    guard();native=json.loads(native_path.read_bytes())
    integrated=derive(queries,policies,sampled_audit,transport,native)
    save(folder/'integrated-targets.json',integrated)
    return integrated
