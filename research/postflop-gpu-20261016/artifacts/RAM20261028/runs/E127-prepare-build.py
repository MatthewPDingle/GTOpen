"""Freeze ordinary integrated E127 builds after full direct and real host controls."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
base=h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
S=ROOT/'runs/E127-host-source';manifest=h.read(S/'manifest.json');owned=manifest['owned']
D=ROOT/'runs/E127-direct';raw=h.read(D/'report.json');assert raw['status']=='pass_all2457_original_and_derived_whole_physical_cases'
assert raw['counts']['cases']==2457 and raw['kernel_launches']==7914
for label in['rustc','native','reader-v2']:
    receipt=h.read(D/'execution'/(label+'.exit.json'));assert receipt['returncode']==0 and receipt['error']is None
assert h.read(ROOT/'runs/E127-host-control/report.json')['status']=='pass_real_compiled_CPU_builder_all6_original_plans_and_types'
H=ROOT/'runs/E127-build-plan';H.mkdir(exist_ok=False)
parent=ROOT/'runs/E125-build.py';script=ROOT/'runs/E127-build.py';assert not script.exists()
code=parent.read_text(encoding='utf-8').replace('E125','E127').replace('e125','e127').replace("b'const unsigned short* __restrict__ hand_perm_p,' in data","b'up_action_star' in data").replace('fixed u16 hand-permutation source','fixed disjoint action-star source')
ast.parse(code);script.write_bytes(code.encode())
phases=[{'id':'feature','features':'preflop-research','expected_features':['gpu','preflop-research'],'integration':False,'outputs':{'solver':'E127-feature-solver'},'target':str(ROOT/'build-e127-final-feature')},{'id':'primary','features':'gpu','expected_features':['gpu'],'integration':True,'outputs':{'solver':'E127-solver','postflop_autoresearch':'E127-postflop_autoresearch'},'target':str(ROOT/'build-e127-final-primary')}]
files=[Path(__file__),parent,script,S/'manifest.json',S/'design.json',D/'protocol.json',D/'report.json',D/'reader-repair.json',ROOT/'runs/E127-read-direct-v2.py',ROOT/'runs/E127-host-control/protocol.json',ROOT/'runs/E127-host-control/report.json',ROOT/'runs/E127-native/control-report.json',ROOT/'runs/E127-resource/protocol.json',ROOT/'runs/E127-resource/report.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json']
files += [Path(value[k])for value in owned.values()for k in['base','candidate']if value[k]is not None]
h.save(H/'protocol.json',{'id':'E127-final-build','at':h.now(),'status':'FROZEN_PRE_ORDINARY_INTEGRATED_COMPILERS','owned':owned,
    'accepted_source_sha256':base,'candidate_owned_sha256':{path:value['candidate_sha256']for path,value in owned.items()},'tracked_owned_paths':manifest['tracked_owned_paths'],'new_owned_paths':manifest['new_owned_paths'],
    'phases':phases,'required_free_bytes':80*1024**3,'input_sha256':{str(path):h.sha(path)for path in files},
    'scope':'Twofreshordinaryoffline/lockedfeatureandprimaryCargo builds offixed4fileD313 action-star host+shader form. All original9kernels/sourceFPmath unchanged. Sourcehelperinverse/resource/actualnativebarrier+control/realCPUplanner6plans/types/full2457directphysicalcases7914launches passed. OriginalCUDA corpus12immutablefields/3wholemutableoutputs/allguards independently read; reader aggregate key mapping repaired additively, no native repeats. Temporarily4ownedresearchfilesonly; exactacceptedrestoreaftereachcompiler. Direct+ordinary beforeinitialspeedperprospectiveprotocol; fullrawengine/canonical/broad/capacity/material/fresh16/holdout/cumulative/actualapp beforeadoption. Newworklistmemory/CPUconstruction/driver/graph/JITcostsincludedincompletecycle. No flags/width/scope/helper/source/quality/sample rescue.'})
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'owned':list(owned)}),flush=True)
