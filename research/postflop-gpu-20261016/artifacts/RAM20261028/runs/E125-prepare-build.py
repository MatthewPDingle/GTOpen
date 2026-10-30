"""Freeze fresh ordinary feature/primary builds after full original direct corpus passed."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
base=h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
S=ROOT/'runs/E125-source';manifest=h.read(S/'manifest.json');owned=manifest['owned']
D=ROOT/'runs/E125-kernel-control';raw=h.read(D/'reader-report.json')
assert raw['cases']==1688 and raw['application_kernel_launches']==3376 and raw['all_original_inputs_and_seeds_independently_regenerated']and len(raw['negative_reader_fixtures_rejected'])==4
for label in ['rustc','native','reader']:
    receipt=h.read(D/'execution'/(label+'.exit.json'));assert receipt['returncode']==0 and receipt['error']is None
H=ROOT/'runs/E125-build-plan';H.mkdir(exist_ok=False)
parent=ROOT/'runs/E122-build.py'
code=parent.read_text(encoding='utf-8').replace('E122','E125').replace('e122','e125').replace("b'@p_lo add.rn.f32' in data","b'const unsigned short* __restrict__ hand_perm_p,' in data").replace('fixed predicated-correction CUDA body','fixed u16 hand-permutation source')
assert 'b\'@p_lo add.rn.f32\''not in code
ast.parse(code);script=ROOT/'runs/E125-build.py';assert not script.exists();script.write_bytes(code.encode())
phases=[{'id':'feature','features':'preflop-research','expected_features':['gpu','preflop-research'],'integration':False,'outputs':{'solver':'E125-feature-solver'},'target':str(ROOT/'build-e125-final-feature')},{'id':'primary','features':'gpu','expected_features':['gpu'],'integration':True,'outputs':{'solver':'E125-solver','postflop_autoresearch':'E125-postflop_autoresearch'},'target':str(ROOT/'build-e125-final-primary')}]
files=[Path(__file__),parent,script,S/'manifest.json',ROOT/'runs/D311-permutation-width-scout/report.json',D/'protocol.json',D/'reader-report.json',ROOT/'runs/E125-resource/protocol.json',ROOT/'runs/E125-resource/report.json',ROOT/'runs/E125-resource/emitted-report.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json']
files += [Path(value[k])for value in owned.values()for k in['base','candidate']]
h.save(H/'protocol.json',{'id':'E125-final-build','at':h.now(),'status':'FROZEN_PRE_ORDINARY_INTEGRATED_COMPILERS','owned':owned,
    'accepted_source_sha256':base,'candidate_owned_sha256':{path:value['candidate_sha256']for path,value in owned.items()},'tracked_owned_paths':list(owned),'new_owned_paths':[],
    'phases':phases,'required_free_bytes':80*1024**3,'input_sha256':{str(path):h.sha(path)for path in files},
    'scope':'Twofreshordinaryoffline/lockedfeatureandprimaryCargo builds offixed4fileu16handpermtableform. OriginalSpotu16 preservedthroughplan/device/kernel plusobservedstoredcapacitytypeaccounting. 1688originaldirectcases/3376launches allfullraw exact. Registers30to40warningkept; samelocal0/occupancy/maxthread. Temporarily4ownedresearchfilesonly; exactacceptedrestoreaftereachcompiler. Direct+ordinary beforeinitialspeedperprospectiveprotocol; fullCPUplan/rawengine/canonical/broad/capacity/material/fresh16/holdout/cumulative/actualapp beforeadoption. No flags/width/scope/helper/source/quality/sample rescue.'})
print(json.dumps({'protocol_sha256':h.sha(H/'protocol.json'),'owned':list(owned)}),flush=True)
