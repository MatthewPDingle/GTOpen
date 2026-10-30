import ast,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
base=h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
S=ROOT/'runs/E120-source';m=h.read(S/'manifest.json');D=ROOT/'comparisons/E120-kernel-control-root-check/report.json';d=h.read(D)
assert d['status']=='pass_scoped_full_sparse_card_raw_equivalence'and d['inventory']['comparison_pairs']==13180 and d['kernel_launches']==26360
assert h.read(ROOT/'runs/E120-direct-audit/complete.json')['all_owned_children_terminal']
owned={'crates/solver/src/gpu/kernels.cu':{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu'),'base_sha256':m['baseline_sha256'],'candidate_sha256':m['candidate_sha256']}}
H=ROOT/'runs/E120-build-plan';H.mkdir(exist_ok=False);parent=ROOT/'runs/E114-build.py'
code=parent.read_text(encoding='utf-8').replace('E114','E120').replace('e114','e120').replace("b'float acc0 = 0.f, acc1 = 0.f;' in data","b'kept_card_end[52]' in data").replace('fixed paired chance CUDA body','fixed sparse-card CUDA body')
script=ROOT/'runs/E120-build.py';assert not script.exists();ast.parse(code);script.write_bytes(code.encode())
phases=[{'id':'feature','features':'preflop-research','expected_features':['gpu','preflop-research'],'integration':False,'outputs':{'solver':'E120-feature-solver'},'target':str(ROOT/'build-e120-final-feature')},{'id':'primary','features':'gpu','expected_features':['gpu'],'integration':True,'outputs':{'solver':'E120-solver','postflop_autoresearch':'E120-postflop_autoresearch'},'target':str(ROOT/'build-e120-final-primary')}]
for phase in phases:assert not Path(phase['target']).exists()
files=[Path(__file__),parent,script,S/'manifest.json',D,ROOT/'runs/E120-direct-audit/complete.json',ROOT/'runs/E120-resource/protocol.json',ROOT/'runs/E120-resource/report.json',ROOT/'runs/D293-sparse-card-PTX/report.json',ROOT/'runs/D294-sparse-card-native/report.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json',S/'baseline.cu',S/'candidate.cu']
h.save(H/'protocol.json',{'id':'E120-final-build','at':h.now(),'status':'FROZEN_PRE_ORDINARY_INTEGRATED_CARGO_COMPILERS','owned':owned,'accepted_source_sha256':base,'candidate_owned_sha256':{'crates/solver/src/gpu/kernels.cu':m['candidate_sha256']},'tracked_owned_paths':list(owned),'new_owned_paths':[],'phases':phases,'required_free_bytes':80*1024**3,'input_sha256':{str(p):h.sha(p)for p in files},'scope':'Two fresh offline/locked ordinary feature/primary Cargo builds. One stable sparse-card CUDA form. Entire13180directpairs/26360launches exact,52sharedendpoints/+208B andregister38to40warningsretained. Restore accepted source after each compiler. Per prospective resource protocol, direct exactness+ordinary units precede initial speed screen. Full canonical raw/engine/broad/material/fresh16/holdout/currentRAMcumulative/actual-app all remain mandatory before adoption. No source/architecture/width/helper/flags/quality/sample rescue after genuine failure.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
